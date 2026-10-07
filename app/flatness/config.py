"""App 設定檔 /etc/flatness/config.toml（3.0.6、NFR-12）。

允收標準、倒數秒數、重新偵測間隔、設備網卡與預設 IP 範圍；DL-EN1 的 IP 不在此（以資料庫為準）。

範例：
    station_id = "ST01"
    equip_if = "eno2"
    pc_ip = "192.168.10.1"
    net_prefix = 24
    countdown_seconds = 0.5          # 按「下一片」「重讀」後到讀取的秒數；小於 1 秒不顯示倒數數字
    redetect_seconds = 10
    engineer_password_sha256 = "…"   # 工程人員密碼（UPL-01）的 SHA-256；留空則無法進入設備設定

    [ip_range]                        # 預設 IP 範圍（DSC-08），主機位址
    dl_en1 = [11, 99]
    other = [100, 199]

    [calibration]                     # 探頭校準（CAL-02、CAL-04）
    samples = 20                      # 取樣次數
    interval_ms = 50                  # 每次間隔
    verify = 5                        # 驗證次數
    tolerance = 0.002                 # 驗證容許值（mm）；取樣標準差上限為其一半

    [standards.row-1]                 # 允收標準（JDG-05、DEF-09）：DL-EN1 key → 探頭 id；校準後以 0 為基準（CAL-03）
    1 = { nominal = 0.000, lower = -0.050, upper = 0.050 }
"""

from __future__ import annotations

import hashlib
import hmac
import ipaddress
from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10（開發機）；產線為 3.12
    import tomli as tomllib


@dataclass
class Standard:
    nominal: float
    lower: float
    upper: float


@dataclass
class Calibration:
    samples: int = 20
    interval_ms: int = 50
    verify: int = 5
    tolerance: float = 0.002


@dataclass
class Config:
    station_id: str = "ST01"
    equip_if: str = "eno2"
    pc_ip: str = "192.168.10.1"
    net_prefix: int = 24
    countdown_seconds: float = 0.5
    redetect_seconds: int = 10
    engineer_password_sha256: str = ""
    ip_range: dict = field(default_factory=lambda: {"dl_en1": (11, 99), "other": (100, 199)})
    standards: dict = field(default_factory=dict)  # {key: {probe_id: Standard}}
    calibration: Calibration = field(default_factory=Calibration)

    @property
    def fallback_net(self) -> ipaddress.IPv4Interface:
        return ipaddress.IPv4Interface(f"{self.pc_ip}/{self.net_prefix}")

    def standard(self, key: str, probe_id: int) -> Standard | None:
        return (self.standards.get(key) or {}).get(probe_id)

    def check_password(self, password: str) -> bool:
        if not self.engineer_password_sha256 or not password:
            return False
        digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
        return hmac.compare_digest(digest, self.engineer_password_sha256.lower())


def load(path: Path | None) -> Config:
    cfg = Config()
    if path is None or not Path(path).exists():
        return cfg
    data = tomllib.loads(Path(path).read_text(encoding="utf-8"))
    for name in ("station_id", "equip_if", "pc_ip", "engineer_password_sha256"):
        if name in data:
            setattr(cfg, name, str(data[name]))
    for name in ("net_prefix", "redetect_seconds"):
        if name in data:
            setattr(cfg, name, int(data[name]))
    if "countdown_seconds" in data:
        cfg.countdown_seconds = float(data["countdown_seconds"])
    for kind, value in (data.get("ip_range") or {}).items():
        lo, hi = value
        cfg.ip_range[kind] = (int(lo), int(hi))
    cal = data.get("calibration") or {}
    for name in ("samples", "interval_ms", "verify"):
        if name in cal:
            setattr(cfg.calibration, name, int(cal[name]))
    if "tolerance" in cal:
        cfg.calibration.tolerance = float(cal["tolerance"])
    for key, probes in (data.get("standards") or {}).items():
        cfg.standards[key] = {int(pid): Standard(float(v["nominal"]), float(v["lower"]), float(v["upper"]))
                              for pid, v in probes.items()}
    return cfg


def password_hash(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()
