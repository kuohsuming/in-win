"""以 ARP 位址偵測封包探索設備（DSC-19）。

DL-EN1 取得 IP 後保存於本機，之後上電不再送 BOOTP，只送 ARP 位址偵測封包（2026-10-07 真機：3 個），
因此只看 BOOTP／DHCP 會漏掉已有 IP 的設備。監聽設備網卡需要 root：由安裝包提供 root 擁有、不接受
參數、只監聽設備網卡的 /usr/local/sbin/flatness-arp-watch（installer/files/flatness-arp-watch），
App 以 sudo 執行為子程序（與 dnsmasq 相同，DSC-07），每收到一個別人送來的 ARP 封包輸出一行：
    ARP <op> <傳送端 MAC> <傳送端 IP> <目標 IP>
只記錄位址偵測封包：
    - 探測（ARP probe，RFC 5227）：傳送端 IP 為 0.0.0.0，目標 IP 為設備要使用的 IP
    - 宣告（ARP announcement／gratuitous ARP）：傳送端 IP 等於目標 IP
一般的 ARP 查詢與回應（例如量測 PC 連線 DL-EN1 時的交換）不記錄、不計次。
"""

from __future__ import annotations

import ipaddress
import re
from datetime import datetime

from .lan import normalize_mac
from .store import SeenEvent

COMMAND = ["sudo", "-n", "/usr/local/sbin/flatness-arp-watch"]

_LINE_RE = re.compile(r"^ARP (?P<op>\d+) (?P<mac>(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}) "
                      r"(?P<sip>\d{1,3}(?:\.\d{1,3}){3}) (?P<tip>\d{1,3}(?:\.\d{1,3}){3})\s*$")
_ZERO = "0.0.0.0"


def parse(line: str) -> tuple[str, str] | None:
    """位址偵測封包回傳 (MAC, 設備的 IP)；其他 ARP 或無法解析回傳 None。"""
    m = _LINE_RE.match(line)
    if not m:
        return None
    sip, tip = m["sip"], m["tip"]
    if not (sip == _ZERO or sip == tip) or tip == _ZERO:
        return None
    try:
        mac = normalize_mac(m["mac"])
        ipaddress.IPv4Address(tip)
    except ValueError:
        return None
    if mac in ("00:00:00:00:00:00", "FF:FF:FF:FF:FF:FF"):
        return None
    return mac, tip


def feed(line: str, now: datetime | None = None) -> list[SeenEvent]:
    hit = parse(line)
    if not hit:
        return []
    return [SeenEvent(hit[0], "ARP", now or datetime.now(), ip=hit[1])]
