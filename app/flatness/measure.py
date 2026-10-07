"""量測資料模型與判定（JDG-01～JDG-05、DEF-09），以及示範用的量測來源。

畫面只依賴 Station 介面：detect() 偵測設備、read() 讀取一次；兩者皆阻斷，由畫面在背景執行緒呼叫。
DemoStation 在沒有 DL-EN1 時產生合理的數值，供畫面開發與展示（--demo）；實機為 dlen1.DlEn1Station。
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field

OK, HI, LO, ERR = "ok", "hi", "lo", "err"


@dataclass
class ProbeReading:
    key: str
    probe_id: int
    value: float | None = None        # 完整精度（JDG-03）；無有效數據為 None
    raw: str = ""                     # DL-EN1 原始回傳（DAT-03）
    error: str | None = None          # 設備異常原因，例：探頭無回應（感測頭錯誤（ErH））
    offset: float | None = None       # 使用的校準偏移量（CAL-03、CAL-09）；value 已扣除


@dataclass
class DeviceStatus:
    key: str
    reachable: bool = True            # False：DL-EN1 偵測不到（DEV-04）
    probe_errors: dict = field(default_factory=dict)  # probe_id → 原因（探頭無回應等）
    booting: bool = False             # ER,**,031／254：設備啟動中（DEV-07）
    error: str | None = None          # 整台設備異常：本機錯誤、探頭台數超出定義（DEF-06）等
    uncalibrated: set = field(default_factory=set)    # 未校準的探頭 id（CAL-07）


def judge(value: float | None, std) -> str:
    """JDG-01：下限 ≤ 測量值 ≤ 上限為合格，大於上限偏高，小於下限偏低；無標準或無數據為設備異常。"""
    if std is None or value is None:
        return ERR
    if value > std.upper:
        return HI
    if value < std.lower:
        return LO
    return OK


def overall(states) -> str:
    """JDG-02、JDG-04：任一點異常 → 設備異常；任一點偏高或偏低 → 不合格；全部合格 → 合格。"""
    states = list(states)
    if not states or ERR in states:
        return "error"
    if HI in states or LO in states:
        return "fail"
    return "pass"


class DemoStation:
    """示範用量測來源：數值依允收標準隨機產生，大部分合格，偶爾偏高、偏低或探頭異常。"""

    def __init__(self, definition: dict, standards: dict, *, seed=None, delay: float = 0.6):
        self.definition = definition
        self.standards = standards
        self.delay = delay
        self.rng = random.Random(seed)
        self.force: str | None = None  # 測試用："pass"／"fail"／"error"

    def detect(self) -> list[DeviceStatus]:
        time.sleep(self.delay * 2)
        return [DeviceStatus(d["key"]) for d in self.definition["dl_en1"]]

    def sample(self, key, probe_id, n, interval, cancel=None) -> list[float]:
        """校準取樣（CAL-02）：示範用原始值約 12.5 mm 加上小幅雜訊。"""
        out = []
        for _ in range(n):
            if cancel is not None and cancel.is_set():
                from .calibrate import Cancelled
                raise Cancelled()
            out.append(round(12.5 + self.rng.gauss(0, 0.0002), 4))
            time.sleep(interval)
        return out

    def resolution(self, key, probe_id) -> float:
        return 0.0001

    def read(self) -> list[ProbeReading]:
        time.sleep(self.delay)
        mode = self.force or self.rng.choices(["pass", "fail", "error"], [70, 22, 8])[0]
        out = []
        points = [(d["key"], p["id"]) for d in self.definition["dl_en1"] for p in d["probes"]]
        bad = set(self.rng.sample(points, k=min(2, len(points)))) if mode != "pass" else set()
        for key, pid in points:
            std = (self.standards.get(key) or {}).get(pid)
            nominal, lo, hi = (std.nominal, std.lower, std.upper) if std else (12.5, 12.45, 12.55)
            half = (hi - lo) / 2
            if (key, pid) in bad and mode == "error":
                out.append(ProbeReading(key, pid, None, "+100000000", "感測頭錯誤（ErH）"))
                continue
            if (key, pid) in bad:
                v = (hi if self.rng.random() < 0.5 else lo) + self.rng.choice((1, -1)) * half * self.rng.uniform(0.15, 0.6)
                v = max(v, hi + 0.001) if v > nominal else min(v, lo - 0.001)
            else:
                v = nominal + self.rng.uniform(-0.7, 0.7) * half
            out.append(ProbeReading(key, pid, round(v, 4), f"{round(v * 10000):+010d}"))
        return out
