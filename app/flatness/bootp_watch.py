"""BOOTP 拒絕配發的偵測（DSC-23）：從 dnsmasq 的 log-dhcp 輸出判斷使用中／維修中 DL-EN1 的 IP 有沒有配發成功。

dnsmasq 2.90 的 BOOTP 行（實機 2026-11-02）：
    BOOTP(eno2) 192.168.10.11 74:95:a7:15:9b:82 address in use     ← IP 被其他 MAC 的租約佔用
    BOOTP(eno2) 74:95:a7:15:9b:82 no address available             ← 主機對應沒有這台／IP 不在配發網段
    BOOTP(eno2) 192.168.10.11 74:95:a7:15:9b:82                    ← 配發成功（行尾沒有拒絕字串）
DL-EN1 只用 BOOTP；DHCP 行的格式不同，不在範圍內。

狀態只在記憶體中，App 重新啟動後歸零。恢復的條件：配發成功、最近一次被拒之後 ARP 顯示它使用設定的 IP、
主畫面連上且之後 CONFIRM 秒內沒有再被拒，或最近一次被拒後 TIMEOUT 秒沒有再被拒（逾時清除）。
"""

from __future__ import annotations

import logging
import re
import threading
import time
from dataclasses import dataclass

log = logging.getLogger(__name__)

TIMEOUT = 60.0   # 被拒的設備每 3～5 秒重送；60 秒沒有新的被拒行即清除
CONFIRM = 15.0   # 主畫面連上後須持續無被拒的秒數（大於 DL-EN1 重新開機時最長的請求間隔 10.8 秒）
RECENT = 60.0    # 設定頁：最近 60 秒有 BOOTP 請求，代表設備正在要 IP（PDT-01 修訂）

USED, NONE, OTHER = "used", "none", "other"
REFUSALS = (("address in use", USED), ("no address available", NONE), ("no address configured", NONE),
            ("wrong network", OTHER), ("ignored", OTHER), ("disabled", OTHER))

_BOOTP_RE = re.compile(
    r"(?:^|\s)BOOTP\((?P<iface>[^)]+)\)\s+(?:(?P<ip>\d{1,3}(?:\.\d{1,3}){3})\s+)?"
    r"(?P<mac>(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2})\b(?P<tail>.*)$")


CONF_PATH = "/etc/flatness/dnsmasq.conf"        # 安裝包產生的主設定（App 可讀、不可寫）
LEASE_PATH = "/var/lib/misc/dnsmasq.leases"     # dnsmasq 預設的租約檔（root 擁有、644）


def lease_holder(ip: str, mac: str, conf_path: str | None = None, lease_path: str | None = None) -> str | None:
    """DSC-22 ②：舊安裝（主設定沒有 leasefile-ro）時，租約檔中此 IP 登記給其他 MAC 則回傳該 MAC（大寫）。
    主設定已有 leasefile-ro、檔案不存在或讀不到時回傳 None。只讀，不寫入。"""
    conf_path, lease_path = conf_path or CONF_PATH, lease_path or LEASE_PATH
    try:
        with open(conf_path, encoding="utf-8") as f:
            if any(line.strip() == "leasefile-ro" for line in f):
                return None
        with open(lease_path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError:
        return None
    for line in lines:
        parts = line.split()  # 到期時間 MAC IP 主機名稱 用戶端識別
        if len(parts) >= 3 and parts[2] == ip and parts[1].upper() != (mac or "").upper():
            return parts[1].upper()
    return None


def lease_text(ip: str, holder: str) -> str:
    return (f"{ip} 仍被舊租約登記給 {holder}，BOOTP 會拒絕配發；"
            "請維護人員執行 sudo ./installer/setup-bootp.sh")


@dataclass(frozen=True)
class Outcome:
    mac: str                 # 大寫、冒號分隔
    ip: str | None           # 行中的 IP（被佔用、配發成功時有）
    refused: str | None      # USED／NONE／OTHER；None 為配發成功
    text: str = ""           # 拒絕的原字串


def parse(line: str, interface: str | None = None) -> Outcome | None:
    """解析一行 dnsmasq 輸出；不是 BOOTP 行，或沒有 IP 也沒有拒絕字串時回傳 None。"""
    m = _BOOTP_RE.search(line)
    if not m or (interface and m["iface"] != interface):
        return None
    mac = m["mac"].replace("-", ":").upper()
    tail = m["tail"].strip()
    for text, kind in REFUSALS:
        if tail.startswith(text):
            return Outcome(mac, m["ip"], kind, text)
    return Outcome(mac, m["ip"], None) if m["ip"] else None  # 有 IP、沒有拒絕字串：配發成功


@dataclass
class Refusal:
    kind: str                # USED／NONE／OTHER
    text: str                # 拒絕的原字串
    ip: str | None           # 被佔用的 IP（USED 時取自日誌）或設定的 IP
    first: float             # time.time()
    last: float
    connected_at: float | None = None   # 被拒期間主畫面連上的時間（待確認是否恢復）


@dataclass
class Watched:
    label: str               # 「第 N 台 名稱」
    ipv4: str | None         # 設定的 IP
    maint: bool = False


class BootpWatch:
    """每個使用中／維修中 DL-EN1 的 BOOTP 狀態；可由多個執行緒呼叫（dnsmasq、ARP 讀取執行緒與畫面）。"""

    def __init__(self, clock=time.time, interface: str | None = None):
        self.clock = clock
        self.interface = interface
        self._lock = threading.Lock()
        self._watched: dict[str, Watched] = {}
        self._refused: dict[str, Refusal] = {}
        self._last_bootp: dict[str, float] = {}

    # ------------------------------------------------------------ 設定

    def watch(self, devices: dict[str, Watched]) -> None:
        """設定要追蹤的設備（MAC → Watched）；不再追蹤的設備清除狀態，不記日誌。"""
        with self._lock:
            self._watched = {mac.upper(): w for mac, w in devices.items()}
            for mac in list(self._refused):
                if mac not in self._watched:
                    del self._refused[mac]

    # ------------------------------------------------------------ 事件

    def feed(self, line: str) -> bool:
        """dnsmasq 的一行輸出；狀態有變更時回傳 True。"""
        o = parse(line, self.interface)
        if o is None:
            return False
        now = self.clock()
        with self._lock:
            self._last_bootp[o.mac] = now
            w = self._watched.get(o.mac)
            if w is None:
                return False
            old = self._refused.get(o.mac)
            if o.refused is None:
                return self._clear(o.mac, "恢復", f"已配發 {o.ip}")
            ip = o.ip or w.ipv4
            if old is not None and old.kind == o.refused:
                old.last, old.ip, old.connected_at = now, ip, None
                return False
            self._refused[o.mac] = Refusal(o.refused, o.text, ip, now if old is None else old.first, now)
            log.warning("BOOTP 被拒：%s（%s）%s", w.label, o.mac, self._describe(o.refused, o.text, ip))
            return True

    def arp(self, mac: str, ip: str) -> bool:
        """ARP 位址偵測：最近一次被拒之後，設備使用設定的 IP 即視為恢復。"""
        mac = mac.upper()
        with self._lock:
            w, r = self._watched.get(mac), self._refused.get(mac)
            if w is None or r is None or ip != w.ipv4:
                return False
            return self._clear(mac, "恢復", f"ARP 顯示使用 {ip}")

    def connected(self, mac: str) -> None:
        """主畫面連上這台：之後 CONFIRM 秒內沒有再被拒才算恢復（連線不核對 MAC，可能連到佔用者）。"""
        mac = mac.upper()
        with self._lock:
            r = self._refused.get(mac)
            if r is not None and r.connected_at is None:
                r.connected_at = self.clock()

    def tick(self) -> bool:
        """定期呼叫：連上後確認期滿即恢復；最近一次被拒後逾時即清除。有變更時回傳 True。"""
        now = self.clock()
        changed = False
        with self._lock:
            for mac, r in list(self._refused.items()):
                if r.connected_at is not None and now - r.connected_at >= CONFIRM and r.last <= r.connected_at:
                    changed |= self._clear(mac, "恢復", "主畫面已連上，且未再被拒")
                elif now - r.last >= TIMEOUT:
                    changed |= self._clear(mac, "逾時清除", f"{int(TIMEOUT)} 秒沒有再被拒")
        return changed

    # ------------------------------------------------------------ 查詢

    def refusal(self, mac: str) -> Refusal | None:
        with self._lock:
            r = self._refused.get((mac or "").upper())
            return None if r is None else Refusal(**vars(r))

    def requesting(self, mac: str, within: float = RECENT) -> bool:
        """最近 within 秒內收到這台的 BOOTP 請求（設備手上沒有 IP、正在要 IP）。"""
        with self._lock:
            t = self._last_bootp.get((mac or "").upper())
        return t is not None and self.clock() - t < within

    def message(self, mac: str) -> str | None:
        """主畫面頂端提示的原因部分，例「192.168.10.11 被其他設備佔用（BOOTP 拒絕配發），請洽維護人員」。"""
        r = self.refusal(mac)
        return None if r is None else self._describe(r.kind, r.text, r.ip)

    @staticmethod
    def _describe(kind: str, text: str, ip: str | None) -> str:
        if kind == USED:
            return f"{ip} 被其他設備佔用（BOOTP 拒絕配發），請洽維護人員"
        if kind == NONE:
            return f"BOOTP 沒有配發 {ip or ''}（IP 不在配發網段，或主機對應未更新），請洽維護人員".replace("配發 （", "配發（")
        return f"BOOTP 拒絕配發（{text}），請洽維護人員"

    def _clear(self, mac: str, what: str, why: str) -> bool:
        if self._refused.pop(mac, None) is None:
            return False
        w = self._watched.get(mac)
        log.warning("BOOTP %s：%s（%s）%s", what, w.label if w else mac, mac, why)
        return True
