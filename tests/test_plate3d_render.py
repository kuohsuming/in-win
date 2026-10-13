"""3D 繪圖畫面（P3D-06～P3D-08）：離屏繪製、標籤不重疊、快取、視窗操作與拒絕訊息。"""

import os
import time
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from helpers import ROOT  # noqa: F401  路徑設定

try:
    from PySide6.QtCore import QTimer
    from PySide6.QtGui import QImage, QPainter
    from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QWidget
except ImportError:
    QApplication = None


@unittest.skipIf(QApplication is None, "需要 PySide6")
class Render(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        from flatness.ui import theme
        theme.load_fonts()
        cls.app.setStyleSheet(theme.qss())

    def snapshot(self, name="sample"):
        from flatness.plate3d import demo
        from flatness.plate3d.config import PlateConfig
        return demo.case_snapshot(name, PlateConfig())

    def models(self, name="sample"):
        from flatness.plate3d.config import PlateConfig
        from flatness.plate3d.dialog import prepare
        return prepare(self.snapshot(name), PlateConfig())

    def test_all_angles_both_modes(self):
        """12 個角度、兩種模式皆可畫；標籤框兩兩不重疊（6 個候選位置有空位時）。"""
        from flatness.plate3d.renderer import render
        for mode, m in self.models().items():
            for rot in range(0, 360, 30):
                with self.subTest(mode=mode, rot=rot):
                    img = QImage(1100, 560, QImage.Format_ARGB32)
                    img.fill(0xFFECEEEC)
                    p = QPainter(img)
                    labels = render(p, 1100, 560, m, rot)
                    p.end()
                    self.assertEqual(len(labels), 12)
                    boxes = [lb.box for lb in labels]
                    overlaps = sum(a.intersects(b) for i, a in enumerate(boxes) for b in boxes[i + 1:])
                    self.assertEqual(overlaps, 0)

    def test_label_text(self):
        """標籤：排名稱 位置名稱 + 讀值（相對標準件，與主畫面相同）；無數據寫「無數據」。"""
        from flatness.plate3d.model import STANDARD
        from flatness.plate3d.renderer import label_text
        ms = self.models("missing")
        m = ms[STANDARD]
        self.assertEqual(label_text(m, "2-4"), ("中排 右", "+0.217"))
        self.assertEqual(label_text(m, "2-2"), ("中排 左中", "無數據"))

    def test_render_speed(self):
        """P3D-09：單張繪製（1100×560）應遠小於 0.3 秒。"""
        from flatness.plate3d.renderer import render
        m = self.models()["standard"]
        img = QImage(1100, 560, QImage.Format_ARGB32)
        t = time.perf_counter()
        p = QPainter(img)
        render(p, 1100, 560, m, 30)
        p.end()
        self.assertLess(time.perf_counter() - t, 0.3)

    def _open(self, snap, action):
        from flatness.plate3d import dialog
        from flatness.plate3d.config import PlateConfig
        win = QMainWindow()
        central = QWidget()
        win.setCentralWidget(central)
        win.resize(1920, 1080)
        win.show()
        out = {}

        def run():
            try:
                out.update(action(central))
            finally:
                for w in central.findChildren(QWidget):
                    if hasattr(w, "reject"):
                        w.reject()
        QTimer.singleShot(200, run)
        out["ret"] = dialog.open_dialog(central, snap, PlateConfig())
        win.close()
        return out

    def test_dialog_controls_and_cache(self):
        """P3D-08：置中、自動播放、暫停、轉動、切換模式；第二圈使用快取。"""
        from flatness.plate3d.dialog import Plate3DDialog
        from flatness.plate3d.model import DETRENDED

        def act(central):
            d = central.findChildren(Plate3DDialog)[0]
            host = d.parentWidget()
            res = {"center": (d.geometry().center() - host.rect().center()).manhattanLength(),
                   "playing": d.timer.isActive()}
            d.turn(30)
            res["after_turn"] = (d.view.rot, d.timer.isActive(), d.angle.text())
            d.set_mode(DETRENDED)
            res["mode_label"] = d.side_lay.itemAt(0).widget().findChildren(type(d.angle))[0].text()
            d.view.frame(0)
            n = len(d.view._cache)
            d.view.frame(0)
            res["cache"] = (n, len(d.view._cache))
            return res
        out = self._open(self.snapshot(), act)
        self.assertLessEqual(out["center"], 2)
        self.assertTrue(out["playing"])
        self.assertEqual(out["after_turn"], (30, False, "旋轉 30°"))
        self.assertIn("平面度", out["mode_label"])
        self.assertEqual(out["cache"][0], out["cache"][1])

    def test_refuse_shows_warning(self):
        """P3D-02：1 台 2 探頭 → 警告訊息，不開 3D 視窗。"""
        from flatness.plate3d.dialog import Plate3DDialog
        from flatness.ui.widgets import MessageDialog

        def act(central):
            msg = central.findChildren(MessageDialog)[0]
            return {"msg": msg.findChildren(QLabel)[1].text(), "dlg": len(central.findChildren(Plate3DDialog))}
        out = self._open(self.snapshot("mosa"), act)
        self.assertIsNone(out["ret"])
        self.assertIn("只有 2 個有效量測點", out["msg"])
        self.assertEqual(out["dlg"], 0)


if __name__ == "__main__":
    unittest.main()
