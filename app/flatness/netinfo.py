"""設備網卡資訊與 IP 佔用探測（DSC-08、DSC-10）。

只用一般權限：網卡位址與鄰居表以 `ip` 命令讀取；探測以 ping 觸發 ARP 解析，
再讀 `ip neigh show <IP> dev <網卡>` 取得回應者 MAC（設備即使不回應 ping 仍會回應 ARP）。
"""

from __future__ import annotations

import ipaddress
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

FREE, TAKEN, SELF, UNKNOWN = "free", "taken", "self", "unknown"

_LLADDR_RE = re.compile(r"lladdr\s+((?:[0-9a-f]{2}:){5}[0-9a-f]{2})\s+(\S+)", re.I)


def interface_address(ifname: str) -> ipaddress.IPv4Interface | None:
    """網卡目前的 IPv4 位址與遮罩；未取得位址（例如未接線）時回傳 None。"""
    try:
        out = subprocess.run(["ip", "-4", "-o", "addr", "show", "dev", ifname],
                             capture_output=True, text=True, timeout=2).stdout
    except (OSError, subprocess.TimeoutExpired):
        return None
    m = re.search(r"\binet\s+(\d+\.\d+\.\d+\.\d+/\d+)", out)
    return ipaddress.IPv4Interface(m.group(1)) if m else None


def has_carrier(ifname: str) -> bool:
    try:
        return Path(f"/sys/class/net/{ifname}/carrier").read_text().strip() == "1"
    except OSError:
        return False


def equipment_network(ifname: str, fallback: ipaddress.IPv4Interface) -> ipaddress.IPv4Interface:
    """DSC-08：以設備網卡目前的位址與遮罩為網段；網卡沒有位址時用 site.conf 的 PC_IP／NET_PREFIX。"""
    return interface_address(ifname) or fallback


@dataclass
class ProbeResult:
    ip: str
    status: str               # free／taken／self／unknown
    mac: str | None = None    # 回應者 MAC（大寫）

    def text(self, old_mac: str | None = None) -> str:
        if self.status == FREE:
            return "✔ 網路上沒有其他設備使用此 IP"
        if self.status == SELF:
            return "✔ 此設備本身正在使用此 IP"
        if self.status == UNKNOWN:
            return "無法確認網路上是否已有設備使用此 IP（設備網卡未接線）"
        if old_mac and self.mac == old_mac:
            return f"舊機 {old_mac} 仍在線上，請拔除後再為新機上電"
        return f"網路上已有設備使用此 IP（MAC {self.mac}）"


def probe(ip: str, ifname: str, own_mac: str | None = None, timeout: float = 1.0) -> ProbeResult:
    """探測 IP 是否已被網路上的其他設備使用（DSC-10）。阻斷約 1 秒，須在背景執行緒呼叫。"""
    if not has_carrier(ifname):
        return ProbeResult(ip, UNKNOWN)
    try:
        ping = subprocess.run(["ping", "-c", "1", "-W", str(max(1, int(timeout))), "-I", ifname, ip],
                              capture_output=True, timeout=timeout + 2)
        # 舊的鄰居紀錄（STALE 等）可能是已離線的設備：等它確定為 REACHABLE 或 FAILED
        for _ in range(4):
            mac, state = _neighbour(ip, ifname)
            if state not in ("DELAY", "PROBE", "STALE", "INCOMPLETE"):
                break
            if ping.returncode == 0 and mac:
                break
            time.sleep(0.4)
    except (OSError, subprocess.TimeoutExpired):
        return ProbeResult(ip, UNKNOWN)
    if mac and (state in ("REACHABLE", "PERMANENT", "NOARP") or ping.returncode == 0):
        return ProbeResult(ip, SELF if own_mac and mac == own_mac.upper() else TAKEN, mac)
    return ProbeResult(ip, FREE)


def _neighbour(ip: str, ifname: str) -> tuple[str | None, str]:
    out = subprocess.run(["ip", "neigh", "show", ip, "dev", ifname],
                         capture_output=True, text=True, timeout=2).stdout
    m = _LLADDR_RE.search(out)
    if m:
        return m.group(1).upper(), m.group(2).upper()
    words = out.split()
    return None, (words[-1].upper() if words else "NONE")
