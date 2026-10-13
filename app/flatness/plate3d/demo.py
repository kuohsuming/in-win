"""展示程式：不連 DL-EN1，直接開 3D 繪圖視窗（提案 M2、M3）。

python -m flatness.plate3d.demo [情境] [--shot 檔案.png] [--rot 角度] [--mode detrended] [--size 寬x高]
情境：sample（3 排 × 4 點、不合格，預設）、missing（1 點無數據）、good（好板）、mosa（1 台 2 探頭 → 拒絕）、
      row（1 排 4 點 → 拒絕），或 tests/data/plate3d_vectors.json 的 case 名稱（讀值扣 12.5 mm 當作歸零後的值）。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

from ..ui import theme
from .config import PlateConfig, probe_positions
from .model import ProbeReading, Snapshot

ROOT = Path(__file__).resolve().parents[3]
NAMES = ["左", "左中", "右中", "右"]
ROWS = ["前排", "中排", "後排"]
SAMPLE = [0.003, -0.002, 0.012, -0.009, -0.004, 0.009, 0.150, 0.217, -0.300, -0.005, 0.009, 0.004]


def grid_snapshot(values, rows, cols, tol=0.2, plate=PlateConfig(), judgment="FAIL") -> Snapshot:
    devs = [{"key": f"row-{r + 1}", "name": ROWS[r] if r < 3 else f"第{r + 1}排",
             "probes": [{"id": c + 1, "description": NAMES[c] if cols == 4 else f"探頭{c + 1}"} for c in range(cols)]}
            for r in range(rows)]
    pos = probe_positions(devs, plate)
    pts = []
    for k, v in enumerate(values):
        r, c = divmod(k, cols)
        d = devs[r]
        x, y = pos[(d["key"], c + 1)]
        state = "err" if v is None else "hi" if v > tol else "lo" if v < -tol else "ok"
        pts.append(ProbeReading(f"{r + 1}-{c + 1}", f"{d['name']} {d['probes'][c]['description']}", x, y, v, tol, state))
    return Snapshot("20261013093015123", judgment, tuple(pts))


def case_snapshot(name: str, plate: PlateConfig) -> Snapshot:
    if name == "sample":
        return grid_snapshot(SAMPLE, 3, 4, plate=plate)
    if name == "missing":
        v = list(SAMPLE)
        v[5] = None
        return grid_snapshot(v, 3, 4, plate=plate, judgment="ERROR")
    if name == "good":
        return grid_snapshot([0.01, -0.004, 0.006, 0.0, -0.008, 0.003, 0.009, -0.002, 0.004, -0.006, 0.0, 0.007],
                             3, 4, plate=plate, judgment="PASS")
    if name == "mosa":
        return grid_snapshot([0.012, -0.008], 1, 2, plate=plate, judgment="PASS")
    if name == "row":
        return grid_snapshot([0.01, -0.02, 0.03, 0.0], 1, 4, plate=plate, judgment="PASS")
    data = json.loads((ROOT / "tests" / "data" / "plate3d_vectors.json").read_text(encoding="utf-8"))
    case = next(c for c in data["cases"] if c["name"] == name)
    pts = []
    for i, p in enumerate(case["points"]):
        r, c = divmod(i, 4)
        v = None if p["reading_mm"] is None else round(p["reading_mm"] - 12.5, 4)
        state = "err" if v is None else "hi" if v > 0.03 else "lo" if v < -0.03 else "ok"
        pts.append(ProbeReading(f"{r + 1}-{c + 1}", f"{ROWS[r]} {NAMES[c]}", p["x"], p["y"], v, 0.03, state))
    return Snapshot("20261013093015123", "FAIL", tuple(pts))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m flatness.plate3d.demo")
    ap.add_argument("case", nargs="?", default="sample")
    ap.add_argument("--shot", help="存成圖片後結束（離屏）")
    ap.add_argument("--rot", type=int, default=0)
    ap.add_argument("--mode", default="standard", choices=["standard", "detrended"])
    ap.add_argument("--size", default="1920x1080")
    a = ap.parse_args(argv)
    app = QApplication.instance() or QApplication(sys.argv[:1])
    theme.load_fonts()
    app.setStyleSheet(theme.qss())
    w, h = (int(x) for x in a.size.split("x"))
    win = QMainWindow()
    central = QWidget()
    central.setObjectName("page")  # 只對主畫面底色生效，不影響對話框內的元件
    win.setCentralWidget(central)
    win.resize(w, h)
    win.show()
    plate = PlateConfig()
    snap = case_snapshot(a.case, plate)
    from . import dialog

    if a.shot:
        def shoot():
            dlg = next((c for c in central.findChildren(dialog.Plate3DDialog)), None)
            if dlg is not None:
                dlg.play(False)
                dlg.set_mode(a.mode)
                dlg.view.set_rot(a.rot)
                dlg._show_angle()
            app.processEvents()
            win.grab().save(a.shot)
            for top in app.topLevelWidgets():
                top.close()
            for c in central.findChildren(QWidget):
                if hasattr(c, "reject"):
                    c.reject()
        QTimer.singleShot(400, shoot)
    dialog.open_dialog(central, snap, plate)
    return 0


if __name__ == "__main__":
    sys.exit(main())
