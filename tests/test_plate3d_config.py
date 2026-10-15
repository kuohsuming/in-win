"""3D 繪圖設定（P3D-10、POS-07）：板子尺寸檢查、儲存與讀回、探頭位置。"""

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
    """POS-07（修訂 P3D-05）：每個探頭的第幾排、第幾點，固定 5 × 5 格。"""

    @staticmethod
    def placed(key, spots, maint=False):
        d = dev(key, len(spots), maint)
        for p, spot in zip(d["probes"], spots):
            if spot:
                p["row"], p["point"] = spot
        return d

    def test_corners(self):
        """板子 1000 × 600：第 1 排第 1 點 → (100, 60)、第 5 排第 5 點 → (900, 540)。"""
        pos = probe_positions([self.placed("row-1", [(1, 1), (5, 5)])], PlateConfig())
        self.assertEqual(pos, {("row-1", 1): (100.0, 60.0), ("row-1", 2): (900.0, 540.0)})

    def test_device_split_across_rows(self):  # 一台的探頭可在不同排；一排可混不同台
        pos = probe_positions([self.placed("row-1", [(1, 2), (3, 2)]), self.placed("row-2", [(1, 4)])], PlateConfig())
        self.assertEqual(pos[("row-1", 2)], (300.0, 300.0))
        self.assertEqual(pos[("row-2", 1)][1], pos[("row-1", 1)][1])

    def test_unplaced_and_maint(self):
        devs = [self.placed("row-2", [(1, 1), None]), self.placed("row-1", [None]),
                self.placed("row-3", [None, (2, 2)], maint=True)]
        pos = probe_positions(devs, PlateConfig())
        self.assertEqual(set(pos), {("row-2", 1)})                     # 未定與維修中不畫
        self.assertEqual(config.unplaced(devs), [("row-1", 1), ("row-2", 2)])  # 依第幾台；維修中不算

    def test_plate_size(self):
        pos = probe_positions([self.placed("row-1", [(1, 1), (2, 5)])], PlateConfig(800, 400, 3))
        self.assertEqual(pos[("row-1", 1)], (80.0, 40.0))
        self.assertEqual(pos[("row-1", 2)], (720.0, 120.0))


if __name__ == "__main__":
    unittest.main()
