"""板子尺寸（P3D-10）與探頭在板上的位置（P3D-05）。

板子尺寸在主畫面「板子尺寸」設定，存於本機 QSettings（與取出測試數據記住的資料夾同一處），
只影響 3D 繪圖。探頭固定在板子下方，位置為設備設定中每個探頭的第幾排、第幾點，依設備設定的板子版面（POS-07、POS-13）。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from .. import positions
from ..lan import row_no

log = logging.getLogger(__name__)

LIMITS = {"length": (1.0, 5000.0), "width": (1.0, 5000.0), "height": (0.1, 100.0)}
DEFAULT = {"length": 1000.0, "width": 600.0, "height": 5.0}
LABEL = {"length": "長", "width": "寬", "height": "高"}
SETTINGS_KEY = "plate/{}"


@dataclass(frozen=True)
class PlateConfig:
    length: float = DEFAULT["length"]   # mm，x：作業員看過去的左右
    width: float = DEFAULT["width"]     # mm，y：前到後
    height: float = DEFAULT["height"]   # mm，實際板厚；圖上厚度為示意

    def text(self) -> str:
        """工具列按鍵文字，例「板子 1000×600×5 mm」。"""
        return f"板子 {fmt(self.length)}×{fmt(self.width)}×{fmt(self.height)} mm"


def fmt(v: float) -> str:
    return f"{v:.1f}".rstrip("0").rstrip(".")


def check(field: str, text) -> tuple[float | None, str | None]:
    """檢查單一欄位：回傳 (數值, 錯誤訊息)。可輸入至小數 1 位（P3D-10）。"""
    lo, hi = LIMITS[field]
    try:
        v = float(str(text).strip())
    except ValueError:
        return None, f"{LABEL[field]}須為數字"
    if v != v or v in (float("inf"), float("-inf")):
        return None, f"{LABEL[field]}須為數字"
    if round(v, 1) != v:
        return None, f"{LABEL[field]}最多小數 1 位"
    if not lo <= v <= hi:
        return None, f"{LABEL[field]}須為 {fmt(lo)}～{fmt(hi)} mm"
    return v, None


def _settings():
    from PySide6.QtCore import QSettings
    return QSettings("flatness", "flatness")


def load(settings=None) -> PlateConfig:
    """讀取板子尺寸；未設定或不合法時用預設（不合法者記入日誌）。"""
    s = settings or _settings()
    values = {}
    for f, d in DEFAULT.items():
        raw = s.value(SETTINGS_KEY.format(f))
        if raw is None:
            values[f] = d
            continue
        v, err = check(f, raw)
        if err:
            log.warning("板子尺寸設定不合法（%s=%r：%s），使用預設 %s", f, raw, err, fmt(d))
            v = d
        values[f] = v
    return PlateConfig(**values)


def save(plate: PlateConfig, settings=None) -> None:
    s = settings or _settings()
    for f in DEFAULT:
        s.setValue(SETTINGS_KEY.format(f), getattr(plate, f))
    if hasattr(s, "sync"):
        s.sync()
    log.info("板子尺寸設定為 %s", plate.text())


def probe_positions(devices: list[dict], plate: PlateConfig,
                    grid: positions.Names | None = None) -> dict[tuple[str, int], tuple[float, float]]:
    """(DL-EN1 key, 探頭 ID) → (x, y) mm（POS-07、POS-13，修訂 2026-11-19）。

    devices 為主畫面版面（定義檔格式，含維修中 "maint": True）。探頭依「實際配置到的排／點」自動平均分布在整片板上：
    取所有已設定位置探頭的排號、點號的最小～最大值當版面範圍，首尾落板緣、其餘等分；**第一排第一點在板子左下角**。
    （renderer 俯視圖 y=0 在上緣，故排由下而上：首排 → 下緣、末排 → 上緣。）grid 參數保留相容但不再決定間距。
    只回傳使用中設備、已設定位置的探頭；位置未定的見 unplaced。
    """
    placed = [(d["key"], p["id"], where[0], where[1])
              for d in devices if not d.get("maint")
              for p in (d.get("probes") or []) if (where := positions.pos(p))]
    if not placed:
        return {}
    rmin, rmax = min(t[2] for t in placed), max(t[2] for t in placed)
    kmin, kmax = min(t[3] for t in placed), max(t[3] for t in placed)
    out = {}
    for key, pid, r, k in placed:
        fx = (k - kmin) / (kmax - kmin) if kmax > kmin else 0.5   # 點：首點左緣、末點右緣
        fy = (rmax - r) / (rmax - rmin) if rmax > rmin else 0.5   # 排：首排下緣、末排上緣（y=0 在上）
        out[(key, pid)] = (plate.length * fx, plate.width * fy)
    return out


def unplaced(devices: list[dict]) -> list[tuple[str, int]]:
    """使用中設備位置未定的探頭 (key, 探頭 ID)，依第幾台、探頭 ID（POS-07：有任一個就拒絕 3D）。"""
    out = []
    for d in sorted(devices, key=lambda d: (row_no(d.get("key")) or 99, d.get("key") or "")):
        if d.get("maint"):
            continue
        out += [(d["key"], p["id"]) for p in sorted(d.get("probes") or [], key=lambda p: p["id"]) if not positions.pos(p)]
    return out
