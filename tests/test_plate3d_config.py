"""3D 繪圖設定（P3D-05、P3D-10）：板子尺寸檢查、儲存與讀回、探頭位置。"""

import unittest

from helpers import ROOT  # noqa: F401  路徑設定

from flatness.plate3d import config
from flatness.plate3d.config import PlateConfig, probe_positions


class FakeSettings:
    def __init__(self, data=None):
        self.data = dict(data or {})

    def value(self, key):
        return self.data.get(key)

    def setValue(self, key, v):
        self.data[key] = v


def dev(key, n, maint=False, name="排"):
    d = {"key": key, "name": name, "probes": [{"id": i + 1, "description": f"p{i + 1}"} for i in range(n)]}
    if maint:
        d["maint"] = True
    return d


class Plate(unittest.TestCase):
    def test_default(self):
        p = config.load(FakeSettings())
        self.assertEqual(p, PlateConfig(1000, 600, 5))
        self.assertEqual(p.text(), "板子 1000×600×5 mm")

    def test_check(self):
        self.assertEqual(config.check("length", "800"), (800.0, None))
        self.assertEqual(config.check("height", "2.5"), (2.5, None))
        for f, text in (("length", "0"), ("width", "-1"), ("length", "5000.1"), ("height", "0.05"),
                        ("height", "101"), ("width", "abc"), ("length", ""), ("length", "1.25"), ("width", "nan")):
            with self.subTest(f=f, text=text):
                v, err = config.check(f, text)
                self.assertIsNone(v)
                self.assertTrue(err)

    def test_save_load(self):
        s = FakeSettings()
        config.save(PlateConfig(800, 400, 3), s)
        p = config.load(s)
        self.assertEqual(p, PlateConfig(800, 400, 3))
        self.assertEqual(p.text(), "板子 800×400×3 mm")

    def test_invalid_stored_uses_default(self):
        p = config.load(FakeSettings({"plate/length": "abc", "plate/width": "0", "plate/height": 2}))
        self.assertEqual(p, PlateConfig(1000, 600, 2))


class Positions(unittest.TestCase):
    def test_three_rows(self):
        """P3D-05：前排左 (125, 100)、後排右 (875, 500)。"""
        pos = probe_positions([dev("row-1", 4), dev("row-2", 4), dev("row-3", 4)], PlateConfig())
        self.assertEqual(pos[("row-1", 1)], (125.0, 100.0))
        self.assertEqual(pos[("row-3", 4)], (875.0, 500.0))
        self.assertEqual(len(pos), 12)

    def test_mosa_one_row_two_probes(self):
        pos = probe_positions([dev("row-1", 2)], PlateConfig())
        self.assertEqual(pos, {("row-1", 1): (250.0, 300.0), ("row-1", 2): (750.0, 300.0)})

    def test_maint_row_keeps_gap(self):
        """第 1、3 排使用中、第 2 排維修中 → y 為 100、500，中間留空，維修中不畫。"""
        pos = probe_positions([dev("row-1", 4), dev("row-2", 4, maint=True), dev("row-3", 4)], PlateConfig())
        self.assertEqual({y for _, y in pos.values()}, {100.0, 500.0})
        self.assertNotIn(("row-2", 1), pos)

    def test_skipped_row_number(self):
        pos = probe_positions([dev("row-1", 2), dev("row-3", 2)], PlateConfig())
        self.assertEqual(pos[("row-3", 1)], (250.0, 500.0))

    def test_plate_size(self):
        pos = probe_positions([dev("row-1", 4), dev("row-2", 4)], PlateConfig(800, 400, 3))
        self.assertEqual(pos[("row-1", 1)], (100.0, 100.0))
        self.assertEqual(pos[("row-2", 4)], (700.0, 300.0))


if __name__ == "__main__":
    unittest.main()
