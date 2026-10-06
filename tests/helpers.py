"""測試共用：路徑設定與範例設備。"""

import ipaddress
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "app") not in sys.path:
    sys.path.insert(0, str(ROOT / "app"))

from flatness.lan import LIVE, OTHER, RETIRED, UNCLASSIFIED, LanDevice  # noqa: E402

NET = ipaddress.IPv4Interface("192.168.10.1/24")
T0 = datetime(2026, 10, 6, 14, 0, 0)


def probes(n=4):
    names = ["左", "左中", "右中", "右", "中央", "六"]
    return [{"id": i + 1, "description": names[i]} for i in range(n)]


def dl(mac, key, name, ip, order, status=LIVE, **cfg):
    config = {"key": key, "name": name, "max_probes": cfg.pop("max_probes", 4),
              "probes": cfg.pop("probes", probes())}
    config.update(cfg)
    return LanDevice(mac=mac, status=status, ipv4=ip, config=config, sort_order=order,
                     first_seen=T0, last_seen=T0 + timedelta(minutes=order), seen_count=3,
                     last_request="BOOTP")


def sample_devices():
    """DSC-06-G1 類似：3 台使用中、1 台其他設備、1 台已停用、1 台不明設備。"""
    return [
        dl("00:01:FC:DE:3A:75", "front", "前排", "192.168.10.11", 1),
        dl("00:01:FC:DE:3A:76", "middle", "中排", "192.168.10.12", 2),
        dl("00:01:FC:DE:3A:77", "rear", "後排", "192.168.10.13", 3),
        LanDevice(mac="3C:52:82:11:22:33", status=OTHER, ipv4="192.168.10.200", hostname="eng-laptop",
                  first_seen=T0, last_seen=T0 + timedelta(minutes=30), seen_count=57, last_request="DHCP"),
        dl("00:01:FC:DE:3A:70", "old", "舊機", "192.168.10.14", 9, status=RETIRED),
        LanDevice(mac="00:01:FC:12:39:A0", status=UNCLASSIFIED, first_seen=T0,
                  last_seen=T0 + timedelta(minutes=40), seen_count=3, last_request="BOOTP"),
    ]


def by_mac(devices):
    return {d.mac: d for d in devices}
