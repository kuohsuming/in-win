"""量測資料模型與判定（JDG-01～JDG-05、DEF-09），以及示範用的量測來源。

畫面只依賴 Station 介面：detect() 偵測設備、read() 讀取一次；兩者皆阻斷，由畫面在背景執行緒呼叫。
DemoStation 在沒有 DL-EN1 時產生合理的數值，供畫面開發與展示（--demo）；實機為 dlen1.DlEn1Station。
"""

from __future__ import annotations

import logging
import math
import random
import time
from dataclasses import dataclass, field

log = logging.getLogger(__name__)

OK, HI, LO, ERR = "ok", "hi", "lo", "err"
UNCALIBRATED = "未校準"  # 未校準的探頭不量測（CAL-07）


@dataclass
class ProbeReading:
    key: str
    probe_id: int
    value: float | None = None        # 完整精度（JDG-03）；無有效數據為 None
    raw: str = ""                     # DL-EN1 原始回傳（DAT-03）
    error: str | None = None          # 設備異常原因，例：探頭無回應（感測頭錯誤（ErH））
    offset: float | None = None       # 校準時的歸零基準（CAL-09）；value 為放大器歸零後的值


@dataclass
class DeviceStatus:
    key: str
    reachable: bool = True            # False：DL-EN1 偵測不到（DEV-04）
    probe_errors: dict = field(default_factory=dict)  # probe_id → 原因（探頭無回應等）
    booting: bool = False             # ER,**,031／254：設備啟動中（DEV-07）
    error: str | None = None          # 整台設備異常：本機錯誤、探頭台數超出定義（DEF-06）等
    uncalibrated: dict = field(default_factory=dict)  # 未校準的探頭 id → 原因（CAL-07）


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
    """示範用量測來源：數值依允收標準隨機產生（平滑的面），大部分合格，偶爾偏高、偏低或探頭異常。"""

    def __init__(self, definition: dict, standards: dict, *, seed=None, delay: float = 0.6):
        self.definition = definition
        self.standards = standards
        self.delay = delay
        self.rng = random.Random(seed)
        self.force: str | None = None  # 測試用："pass"／"fail"／"error"
        self.zero: dict = {}           # 示範用放大器的歸零基準（校準）

    def detect(self) -> list[DeviceStatus]:
        time.sleep(self.delay * 2)
        return [DeviceStatus(d["key"]) for d in self.definition["dl_en1"]]

    # 校準（CAL-02）：示範用放大器，原始值約 12.5 mm 加上小幅雜訊，歸零後扣除歸零基準
    def prepare_preset(self, key, probe_id) -> dict:
        return {}

    def preset(self, key, probe_id, execute: bool) -> None:
        self.zero[(key, probe_id)] = round(12.5 + self.rng.gauss(0, 0.0002), 4) if execute else 0.0

    def response_time(self, key, probe_id) -> float:
        return 0.0

    def sample(self, key, probe_id, n, interval, cancel=None) -> list[float]:
        out = []
        for _ in range(n):
            if cancel is not None and cancel.is_set():
                from .calibrate import Cancelled
                raise Cancelled()
            out.append(round(12.5 + self.rng.gauss(0, 0.0002) - self.zero.get((key, probe_id), 0.0), 4))
            time.sleep(interval)
        return out

    def resolution(self, key, probe_id) -> float:
        return 0.0001

    def read(self) -> list[ProbeReading]:
        """一片的虛擬讀值：整片傾斜加上一處凹陷或凸起（平滑的面，供 3D 繪圖驗證），再加少許雜訊。

        探頭在板子下方，讀值越大表示表面越低（凹陷）。不合格時那一處超出上限或下限；
        設備異常時隨機一個探頭無回應。每片的形狀記在日誌，可對照 3D 繪圖。
        """
        from .plate3d.config import PlateConfig, probe_positions
        time.sleep(self.delay)
        mode = self.force or self.rng.choices(["pass", "fail", "error"], [70, 22, 8])[0]
        points = [(d["key"], p["id"]) for d in self.definition["dl_en1"] for p in d["probes"]]
        if not points:
            return []
        plate = PlateConfig(length=1.0, width=1.0)
        pos = probe_positions(self.definition["dl_en1"], plate)
        center = self.rng.choice(points)
        tilt = (self.rng.uniform(-0.3, 0.3), self.rng.uniform(-0.3, 0.3))  # 左→右、前→後，以允許誤差的一半為單位
        depth = self.rng.choice((1, -1)) * (self.rng.uniform(1.15, 1.5) if mode == "fail" else self.rng.uniform(0.35, 0.6))
        dead = self.rng.choice(points) if mode == "error" else None
        cx, cy = pos.get(center, (0.5, 0.5))
        out = []
        for key, pid in points:
            std = (self.standards.get(key) or {}).get(pid)
            nominal, lo, hi = (std.nominal, std.lower, std.upper) if std else (12.5, 12.45, 12.55)
            half = (hi - lo) / 2
            if (key, pid) == dead:
                out.append(ProbeReading(key, pid, None, "+100000000", "感測頭錯誤（ErH）"))
                continue
            x, y = pos.get((key, pid), (0.5, 0.5))
            bump = depth * math.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * 0.3 ** 2))
            k = tilt[0] * (2 * x - 1) + tilt[1] * (2 * y - 1) + bump + self.rng.gauss(0, 0.03)
            if (key, pid) != center or mode != "fail":
                k = max(-0.9, min(0.9, k))  # 只有那一處不合格
            v = nominal + k * half
            out.append(ProbeReading(key, pid, round(v, 4), f"{round(v * 10000):+010d}"))
        log.info("示範量測（%s）：%s-%s 一帶%s（讀值%+.0f%% 允許誤差），傾斜 左→右 %+.0f%%、前→後 %+.0f%%%s",
                 mode, *center, "凹陷" if depth > 0 else "凸起", depth * 100, tilt[0] * 200, tilt[1] * 200,
                 f"，{dead[0]}-{dead[1]} 無回應" if dead else "")
        return out
