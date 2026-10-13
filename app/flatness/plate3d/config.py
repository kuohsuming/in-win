"""板子尺寸（P3D-10）與探頭在板上的位置（P3D-05）。

板子尺寸在主畫面「板子尺寸」設定，存於本機 QSettings（與取出測試數據記住的資料夾同一處），
只影響 3D 繪圖。探頭固定在板子下方：前後依 DL-EN1 的位置「第幾排」、左右依探頭 ID 平均分佈。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

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


def probe_positions(devices: list[dict], plate: PlateConfig) -> dict[tuple[str, int], tuple[float, float]]:
    """(排 key, 探頭 ID) → (x, y) mm（P3D-05）。

    devices 為主畫面版面（定義檔格式，含維修中 "maint": True）。前後依第 n 排，R 為使用中與維修中最大的排號：
    y = 寬 × (n − 0.5) / R；排號照實際位置，中間沒有設備的排留空。左右依探頭 ID（1～N）：x = 長 × (id − 0.5) / N。
    只回傳使用中設備的探頭。
    """
    rows = [(row_no(d.get("key")), d) for d in devices]
    rows = [(n, d) for n, d in rows if n]
    if not rows:
        return {}
    r_max = max(n for n, _ in rows)
    out = {}
    for n, d in rows:
        if d.get("maint"):
            continue
        ids = sorted(p["id"] for p in d.get("probes") or [])
        count = len(ids)
        for i, pid in enumerate(ids):
            out[(d["key"], pid)] = (plate.length * (i + 0.5) / count, plate.width * (n - 0.5) / r_max)
    return out
