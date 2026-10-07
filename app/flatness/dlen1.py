"""DL-EN1 連線與讀值（DEV-01～DEV-09、DEF-05、DEF-06、5.1）。

每台 DL-EN1 一條常駐 TCP 連線（埠預設 64000），ASCII、CR LF 結尾、一問一答。只使用讀取命令
（NFR-11：不送 SW 等寫入命令）：
    SR,00,077  連接台數              → SR,00,077,+000000002
    SR,00,000  整體狀態（0 為正常）  → SR,00,000,+000000000
    SR,00,008／009  本機錯誤（整體狀態非 0 時）
    SR,00,668～683  放大器 ID 1～16 的錯誤代碼（輸出狀態 03 時）
    FR,nn,037  放大器 ID nn 的小數位數 → FR,01,037,+000000004
    MS         全部放大器的輸出狀態與測量值 → MS,02,-000002971,02,+000000358
               （第 N 組對應放大器 ID N，DEF-05；實際值 = 整數 ÷ 10^小數位數）
錯誤回應 ER,命令,ddd；031／254 表示設備啟動中（DEV-07）。
2026-10-07 以真機（2 台放大器、4 位小數）確認以上回應格式。

Station 介面與 measure.DemoStation 相同：detect()、read() 皆阻斷，由畫面在背景執行緒呼叫，
各台 DL-EN1 平行處理（NFR-02）。
"""

from __future__ import annotations

import logging
import socket
import threading
from concurrent.futures import ThreadPoolExecutor

from .bootp import DEFAULT_PORT
from .measure import DeviceStatus, ProbeReading

log = logging.getLogger(__name__)

NO_DATA = {"+100000000", "+099999999", "-099999999", "-099999998"}  # 探頭無有效數據（5.1）
BOOTING = {"031", "254"}                                             # 設備啟動中（DEV-07）
OUT_ERROR = "03"                                                     # MS 輸出狀態：放大器錯誤
AMP_ERROR_BASE = 667                                                 # SR,00,(667 + ID)：放大器 ID 的錯誤代碼


class CommandError(Exception):
    """DL-EN1 回應 ER,命令,代碼。"""

    def __init__(self, cmd: str, code: str):
        super().__init__(f"{cmd} 回應錯誤 {code}")
        self.code = code

    @property
    def booting(self) -> bool:
        return self.code in BOOTING


class Link:
    """一台 DL-EN1 的常駐連線（DEV-09）：失敗時關閉，下一次命令自動重連。"""

    def __init__(self, ip: str, port: int = DEFAULT_PORT, connect_timeout: float = 3.0, timeout: float = 3.0):
        self.ip, self.port = ip, port
        self.connect_timeout, self.timeout = connect_timeout, timeout
        self._sock: socket.socket | None = None
        self._buf = b""
        self._lock = threading.Lock()

    def close(self):
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass
        self._sock, self._buf = None, b""

    def _connect(self):
        # DEV-04：3 秒內未建立連線即為偵測不到（由 create_connection 拋出 OSError）
        self._sock = socket.create_connection((self.ip, self.port), timeout=self.connect_timeout)
        self._sock.settimeout(self.timeout)
        self._buf = b""
        log.info("已連線 DL-EN1 %s:%s", self.ip, self.port)

    def ask(self, cmd: str) -> list[str]:
        """送出命令並回傳回應欄位（不含命令本身）；連線失敗拋出 OSError，ER 回應拋出 CommandError。"""
        with self._lock:
            while True:
                stale = self._sock is not None  # 沿用既有連線：可能已被對方關閉，失敗時重連一次
                try:
                    if self._sock is None:
                        self._connect()
                    self._sock.sendall(cmd.encode("ascii") + b"\r\n")
                    line = self._readline()
                    break
                except OSError:
                    self.close()
                    if not stale:  # 新建的連線也失敗：偵測不到（DEV-04）
                        raise
            fields = line.split(",")
            if fields[0] == "ER":
                raise CommandError(cmd, fields[2] if len(fields) > 2 else "?")
            head = cmd.split(",")
            if fields[:len(head)] != head:
                self.close()  # 回應錯位：重新連線以免之後的回應都對不上
                raise OSError(f"{cmd} 的回應不符：{line}")
            return fields[len(head):]

    def _readline(self) -> str:
        while b"\r\n" not in self._buf:
            chunk = self._sock.recv(4096)
            if not chunk:
                raise ConnectionError("DL-EN1 關閉連線")
            self._buf += chunk
        line, self._buf = self._buf.split(b"\r\n", 1)
        return line.decode("ascii", errors="replace")


def _int(fields: list[str]) -> int:
    return int(fields[-1])


class DlEn1Station:
    """以 DL-EN1 實機量測（DEV、MEA）。definition 只含使用中的 DL-EN1。"""

    def __init__(self, definition: dict, standards: dict | None = None, *,
                 connect_timeout: float = 3.0, timeout: float = 3.0):
        self.definition = definition
        self.devices = list(definition.get("dl_en1", []))
        self.links = {d["key"]: Link(d["ipv4"], d.get("port") or DEFAULT_PORT, connect_timeout, timeout)
                      for d in self.devices}
        self.decimals: dict[tuple[str, int], int] = {}  # DEV-03：(key, 放大器 ID) → 小數位數
        self._pool = ThreadPoolExecutor(max_workers=max(1, len(self.devices)), thread_name_prefix="dlen1")

    def close(self):
        for link in self.links.values():
            link.close()
        self._pool.shutdown(wait=False)

    # ------------------------------------------------------------ 偵測

    def detect(self) -> list[DeviceStatus]:
        return list(self._pool.map(self._detect_one, self.devices))

    def _detect_one(self, d: dict) -> DeviceStatus:
        key, link = d["key"], self.links[d["key"]]
        st = DeviceStatus(key)
        ids = sorted(p["id"] for p in d["probes"])
        try:
            count = _int(link.ask("SR,00,077"))
            state = _int(link.ask("SR,00,000"))
            if state:
                where, code = _int(link.ask("SR,00,008")), _int(link.ask("SR,00,009"))
                st.error = f"DL-EN1 本機錯誤（錯誤代碼 {code}，位置 {where}）"
                log.warning("%s：整體狀態 %s，008=%s，009=%s", d["name"], state, where, code)
            if count > d.get("max_probes", len(ids)):
                st.error = f"探頭台數超出定義（連接 {count} 台，設定 {d.get('max_probes', len(ids))} 台）"  # DEF-06
            for pid in ids:
                if pid > count:  # DEF-06：連接台數少於已安裝探頭的 ID
                    st.probe_errors[pid] = f"放大器未連接（DL-EN1 只連接 {count} 台）"
                    continue
                self.decimals[(key, pid)] = _int(link.ask(f"FR,{pid:02d},037"))
            outs = self._ms(link)
            for pid in ids:
                if pid <= len(outs) and outs[pid - 1][0] == OUT_ERROR and pid not in st.probe_errors:
                    code = _int(link.ask(f"SR,00,{AMP_ERROR_BASE + pid}"))
                    st.probe_errors[pid] = f"放大器錯誤（錯誤代碼 {code}）"
            log.info("偵測 %s（%s）：連接 %d 台，整體狀態 %d，小數位數 %s", d["name"], link.ip, count, state,
                     {pid: self.decimals.get((key, pid)) for pid in ids})
        except CommandError as exc:
            if exc.booting:
                st.booting = True
            else:
                st.error = f"DL-EN1 回應錯誤（{exc}）"
            log.warning("偵測 %s：%s", d["name"], exc)
        except OSError as exc:
            st.reachable = False
            log.warning("偵測 %s（%s）：偵測不到（%s）", d["name"], link.ip, exc)
        return st

    @staticmethod
    def _ms(link: Link) -> list[tuple[str, str]]:
        f = link.ask("MS")
        return [(f[i], f[i + 1]) for i in range(0, len(f) - 1, 2)]

    # ------------------------------------------------------------ 讀值

    def read(self) -> list[ProbeReading]:
        out = []
        for part in self._pool.map(self._read_one, self.devices):
            out.extend(part)
        return out

    def _read_one(self, d: dict) -> list[ProbeReading]:
        key, link = d["key"], self.links[d["key"]]
        ids = sorted(p["id"] for p in d["probes"])
        try:
            outs = self._ms(link)
        except (OSError, CommandError) as exc:
            log.warning("讀值 %s：%s", d["name"], exc)
            why = "DL-EN1 偵測不到" if isinstance(exc, OSError) else f"DL-EN1 回應錯誤（{exc}）"
            return [ProbeReading(key, pid, None, "", why) for pid in ids]
        res = []
        for pid in ids:  # DEF-05：只處理已安裝的探頭
            if pid > len(outs):
                res.append(ProbeReading(key, pid, None, "", "探頭無回應（放大器未連接）"))
                continue
            status, raw = outs[pid - 1]
            if status == OUT_ERROR:
                res.append(ProbeReading(key, pid, None, raw, "放大器錯誤"))
            elif raw in NO_DATA:
                res.append(ProbeReading(key, pid, None, raw, "無有效數據"))
            else:
                dec = self.decimals.get((key, pid))
                if dec is None:
                    try:
                        dec = self.decimals[(key, pid)] = _int(link.ask(f"FR,{pid:02d},037"))
                    except (OSError, CommandError) as exc:
                        res.append(ProbeReading(key, pid, None, raw, f"無法讀取小數位數（{exc}）"))
                        continue
                res.append(ProbeReading(key, pid, int(raw) / 10 ** dec, raw))
        return res
