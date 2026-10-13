"""3D 繪圖（需求規格書 3.12 P3D）：以立體板子顯示這一片表面的高低，只供檢視，不改判定、不寫資料庫。

- config：板子尺寸（主畫面設定，P3D-10）與探頭位置（P3D-05）。
- model：有效點檢查、兩種顯示模式、平面擬合、插值網格（純計算，不依賴 Qt）。
- renderer／widget／dialog：繪圖與視窗（P3D-06～P3D-08）。
"""

from .config import PlateConfig, probe_positions  # noqa: F401
from .model import ProbeReading, RefuseError, Snapshot, SurfaceModel, build_model  # noqa: F401


def open_plate3d(parent, snapshot, plate):
    """主畫面「3D 繪圖」：有效點不足或同一直線時以警告訊息拒絕（P3D-02、P3D-03），否則開啟視窗。"""
    from .dialog import open_dialog
    return open_dialog(parent, snapshot, plate)
