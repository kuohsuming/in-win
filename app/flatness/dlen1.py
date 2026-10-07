"""DL-EN1 連線與讀值（DEV-01～DEV-09、DEF-05、DEF-06、5.1）。

每台 DL-EN1 一條常駐 TCP 連線（埠預設 64000），ASCII、CR LF 結尾、一問一答。量測與偵測只使用讀取命令：
    SR,00,077  連接台數              → SR,00,077,+000000002
    SR,00,000  整體狀態（0 為正常）  → SR,00,000,+000000000
    SR,00,008／009  本機錯誤（整體狀態非 0 時）
    SR,00,668～683  ID 00～15 的錯誤代碼（668 為 DL-EN1 本身，放大器 ID n 為 668 ＋ n；輸出狀態 03 時）
    FR,nn,037  放大器 ID nn 的小數位數 → FR,01,037,+000000004
    MS         全部放大器的輸出狀態與測量值 → MS,02,-000002971,02,+000000358
               （第 N 組對應放大器 ID N，DEF-05；實際值 = 整數 ÷ 10^小數位數；為放大器歸零後的判斷值 P.V.）
    SR,nn,037／038  放大器 ID nn 的判斷值 P.V.／原始值 R.V.（CAL-10：兩者相減為放大器目前的歸零基準）
寫入命令只在校準時對選取的單一放大器使用（NFR-11、CAL-02）：
    SW,nn,149／148／150  預設記憶 YES、預設資料 P.V.、執行點全部通道通用（不符合才寫入）
               預設資料選 R.V. 時歸零連 R.V. 一起改變（2026-10-07 真機），R.V. − P.V. 恆為 0，無法比對（CAL-10）
    SW,nn,067／072／077／082  通道 0～3 的預設值 0（不符合才寫入）
    SW,nn,002,+000000001  預設重置（清除歸零）；SW,nn,001,+000000001  執行預設（歸零）
    回應為 SW,nn,資料編號（不含設定值）。禁止 003 重置、005 初始化重置。
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

import time

from .bootp import DEFAULT_PORT
from .calibrate import Cancelled, SampleError
from .measure import UNCALIBRATED, ZERO_CHANGED, ZERO_LOST, DeviceStatus, ProbeReading

log = logging.getLogger(__name__)

NO_DATA = {"+100000000", "+099999999", "-099999999", "-099999998"}  # 探頭無有效數據（5.1）
BOOTING = {"031", "254"}                                             # 設備啟動中（DEV-07）
OUT_ERROR = "03"                                                     # MS 輸出狀態：00 全 OFF、01 HIGH、02 LOW、03 錯誤、04 GO（手冊 2-4）
AMP_ERROR_BASE = 668                                                 # SR,00,(668 + ID)：ID 的錯誤代碼（手冊 3-1，668 為 ID00）
SR_INVALID = {"+009999999", "-009999999", "-009999998", "+010000000"}  # SR 037／038：超範圍、欠範圍、無效、錯誤（手冊 4-1 *4）
PRESET_EXECUTE, PRESET_RESET = 1, 2                                  # GT2 資料編號 001 執行預設、002 預設重置
PRESET_SETTINGS = {149: 0, 148: 1, 150: 0}                           # 預設記憶 YES、預設資料 P.V.（R.V. 不受歸零影響）、執行點全部通道通用
PRESET_VALUES = (67, 72, 77, 82)                                     # 通道 0～3 的預設值（歸零後顯示 0）
RESPONSE_TIME = {0: 0.003, 1: 0.005, 2: 0.010, 3: 0.100, 4: 0.500, 5: 1.000}  # GT2 資料編號 132 響應時間（秒）


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
            if head[0] == "SW":
                head = head[:3]  # SW 的回應不含設定值（手冊 2-4）
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

    def __init__(self, definition: dict, standards: dict | None = None, *, tolerance: float = 0.002,
                 connect_timeout: float = 3.0, timeout: float = 3.0):
        self.definition = definition
        self.devices = list(definition.get("dl_en1", []))
        self.links = {d["key"]: Link(d["ipv4"], d.get("port") or DEFAULT_PORT, connect_timeout, timeout)
                      for d in self.devices}
        self.decimals: dict[tuple[str, int], int] = {}  # DEV-03：(key, 放大器 ID) → 小數位數
        # CAL-06：(key, 探頭 id) → 校準時放大器的歸零基準；沒有的探頭為未校準（CAL-07）
        self.offsets = {(d["key"], p["id"]): p["zero_offset"] for d in self.devices for p in d["probes"]
                        if p.get("zero_offset") is not None}
        self.tolerance = tolerance                       # CAL-10：歸零基準與紀錄的容許差
        self.not_ready: dict[tuple[str, int], str] = {}  # CAL-07、CAL-10：上次偵測時不可量測的探頭 → 原因
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
            st.uncalibrated = {pid: UNCALIBRATED for pid in ids if (key, pid) not in self.offsets}  # CAL-07
            for pid in ids:  # CAL-10：放大器的歸零與校準紀錄不符
                if pid not in st.probe_errors and pid not in st.uncalibrated:
                    why = self._check_zero(d, link, pid)
                    if why:
                        st.uncalibrated[pid] = why
            for pid in ids:
                self.not_ready.pop((key, pid), None)
                if pid in st.uncalibrated:
                    self.not_ready[(key, pid)] = st.uncalibrated[pid]
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

    def _check_zero(self, d: dict, link: Link, pid: int) -> str | None:
        """CAL-10：比對放大器目前的歸零基準（R.V. − P.V.）與校準紀錄；無法讀取時不判定。"""
        key = d["key"]
        try:
            base = self._zero_base(link, key, pid)
        except CommandError as exc:
            log.warning("%s 放大器 ID %d：無法讀取 P.V.／R.V.，不確認歸零（%s）", d["name"], pid, exc)
            return None
        if base is None:
            log.info("%s 放大器 ID %d：P.V.／R.V. 無有效數據，不確認歸零", d["name"], pid)
            return None
        stored = self.offsets[(key, pid)]
        if abs(base - stored) <= self.tolerance:
            return None
        why = ZERO_LOST if abs(base) <= self.tolerance else ZERO_CHANGED
        log.warning("%s 放大器 ID %d：%s（目前 %.4f，校準紀錄 %.4f），須重新校準", d["name"], pid, why, base, stored)
        return why

    def _zero_base(self, link: Link, key: str, pid: int) -> float | None:
        """放大器目前的歸零基準 R.V. − P.V.（mm）；任一為超範圍、無效等特殊值時回傳 None。"""
        dec = self._decimals(link, key, pid)
        pv = link.ask(f"SR,{pid:02d},037")[-1]
        rv = link.ask(f"SR,{pid:02d},038")[-1]
        if pv in SR_INVALID or rv in SR_INVALID:
            return None
        return round((int(rv) - int(pv)) / 10 ** dec, 6)

    def _decimals(self, link: Link, key: str, pid: int) -> int:
        dec = self.decimals.get((key, pid))
        if dec is None:
            dec = self.decimals[(key, pid)] = _int(link.ask(f"FR,{pid:02d},037"))
        return dec

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
                try:
                    dec = self._decimals(link, key, pid)
                except (OSError, CommandError) as exc:
                    res.append(ProbeReading(key, pid, None, raw, f"無法讀取小數位數（{exc}）"))
                    continue
                offset = self.offsets.get((key, pid))
                why = self.not_ready.get((key, pid)) or (UNCALIBRATED if offset is None else None)
                if why:  # CAL-07、CAL-10：未校準或歸零不符不判定
                    res.append(ProbeReading(key, pid, None, raw, why))
                else:    # CAL-03：放大器已歸零，直接使用判斷值；記下歸零基準（CAL-09）
                    res.append(ProbeReading(key, pid, int(raw) / 10 ** dec, raw, None, offset))
        return res

    # ------------------------------------------------------------ 校準（CAL-02）

    def resolution(self, key: str, probe_id: int) -> float:
        dec = self.decimals.get((key, probe_id))
        return 10 ** -(dec if dec is not None else 4)

    def _calib(self, key: str, probe_id: int, what: str, fn):
        """校準用的命令：通訊失敗、ER 回應皆為 SampleError。"""
        d = next(x for x in self.devices if x["key"] == key)
        try:
            return fn(self.links[key])
        except (OSError, CommandError) as exc:
            raise SampleError(f"{d['name']} 放大器 ID {probe_id} {what}失敗（{exc}）") from exc

    def _sw(self, link: Link, key: str, probe_id: int, no: int, value: int):
        cmd = f"SW,{probe_id:02d},{no:03d},{value:+010d}"
        log.info("%s 寫入放大器：%s", key, cmd)
        link.ask(cmd)

    def prepare_preset(self, key: str, probe_id: int) -> dict:
        """第 1 步：讀出放大器的歸零設定（記入日誌），不符合的才寫入；回傳原本的設定。"""
        def go(link):
            before = {no: _int(link.ask(f"SR,{probe_id:02d},{no:03d}")) for no in (*PRESET_SETTINGS, *PRESET_VALUES)}
            log.info("%s 放大器 ID %d 原本的歸零設定：%s", key, probe_id,
                     "、".join(f"{no:03d}={v}" for no, v in before.items()))
            for no, want in PRESET_SETTINGS.items():
                if before[no] != want:
                    self._sw(link, key, probe_id, no, want)
            for no in PRESET_VALUES:
                if before[no] != 0:
                    self._sw(link, key, probe_id, no, 0)
            return before
        return self._calib(key, probe_id, "歸零設定", go)

    def preset(self, key: str, probe_id: int, execute: bool) -> None:
        """execute：執行預設（歸零，放大器記住）；否則預設重置（清除歸零）。"""
        no = PRESET_EXECUTE if execute else PRESET_RESET
        self._calib(key, probe_id, "歸零" if execute else "清除歸零",
                    lambda link: self._sw(link, key, probe_id, no, 1))

    def response_time(self, key: str, probe_id: int) -> float:
        """放大器的響應時間（秒）；取樣間隔不小於此值，才不會連續讀到同一個值。"""
        v = self._calib(key, probe_id, "讀取響應時間", lambda link: _int(link.ask(f"SR,{probe_id:02d},132")))
        return RESPONSE_TIME.get(v, 0.1)

    def zero_base(self, key: str, probe_id: int) -> float:
        """放大器目前的歸零基準 R.V. − P.V.（CAL-06）。"""
        base = self._calib(key, probe_id, "讀取 P.V.／R.V.", lambda link: self._zero_base(link, key, probe_id))
        if base is None:
            raise SampleError(f"放大器 ID {probe_id} 的 P.V.／R.V. 無有效數據")
        return base

    def sample(self, key: str, probe_id: int, n: int, interval: float, cancel=None) -> list[float]:
        """讀取一個探頭的判斷值 n 次，每次間隔 interval 秒；與量測共用同一條連線。"""
        d = next(x for x in self.devices if x["key"] == key)
        link = self.links[key]
        out = []
        try:
            dec = self._decimals(link, key, probe_id)
            for i in range(n):
                if cancel is not None and cancel.is_set():
                    raise Cancelled()
                t0 = time.monotonic()
                outs = self._ms(link)
                if probe_id > len(outs):
                    raise SampleError(f"放大器 ID {probe_id} 未連接")
                status, raw = outs[probe_id - 1]
                if status == OUT_ERROR:
                    raise SampleError(f"第 {i + 1} 次：放大器錯誤")
                if raw in NO_DATA:
                    raise SampleError(f"第 {i + 1} 次：無有效數據（{raw}）")
                out.append(int(raw) / 10 ** dec)
                if i < n - 1:
                    time.sleep(max(0.0, interval - (time.monotonic() - t0)))
        except (OSError, CommandError) as exc:
            raise SampleError(f"{d['name']} 通訊失敗（{exc}）") from exc
        return out
