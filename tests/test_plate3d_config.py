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
    """POS-07、POS-13（修訂 P3D-05）：每個探頭的第幾排、第幾點，依板子版面（預設 5 × 5）。"""

    @staticmethod
    def placed(key, spots, maint=False):
        d = dev(key, len(spots), maint)
        for p, spot in zip(d["probes"], spots):
            if spot:
                p["row"], p["point"] = spot
        return d

    def test_corners(self):
        """板子 1000 × 600：第 1 排第 1 點 → 左下角 (0, 600)、最末排最末點 → 右上角 (1000, 0)（首尾落板緣）。"""
        pos = probe_positions([self.placed("row-1", [(1, 1), (5, 5)])], PlateConfig())
        self.assertEqual(pos, {("row-1", 1): (0.0, 600.0), ("row-1", 2): (1000.0, 0.0)})

    def test_device_split_across_rows(self):  # 一台的探頭可在不同排；一排可混不同台（自動以實配排/點 1~3、2~4 平均）
        pos = probe_positions([self.placed("row-1", [(1, 2), (3, 2)]), self.placed("row-2", [(1, 4)])], PlateConfig())
        self.assertEqual(pos[("row-1", 2)], (0.0, 0.0))                 # (第3排,點2)=末排左緣→右上角 x、上緣
        self.assertEqual(pos[("row-2", 1)][1], pos[("row-1", 1)][1])   # 同為第 1 排 → 同一 y（下緣）

    def test_unplaced_and_maint(self):
        devs = [self.placed("row-2", [(1, 1), None]), self.placed("row-1", [None]),
                self.placed("row-3", [None, (2, 2)], maint=True)]
        pos = probe_positions(devs, PlateConfig())
        self.assertEqual(set(pos), {("row-2", 1)})                     # 未定與維修中不畫
        self.assertEqual(config.unplaced(devs), [("row-1", 1), ("row-2", 2)])  # 依第幾台；維修中不算

    def test_plate_size(self):  # 實配排 1~2、點 1~5 → 首排在下緣、末排在上緣
        pos = probe_positions([self.placed("row-1", [(1, 1), (2, 5)])], PlateConfig(800, 400, 3))
        self.assertEqual(pos[("row-1", 1)], (0.0, 400.0))              # 第1排第1點 → 左下角
        self.assertEqual(pos[("row-1", 2)], (800.0, 0.0))             # 第2排第5點 → 右上角

    def test_auto_span_ignores_grid(self):  # POS-13（修訂）：間距依實配排/點，與傳入的 grid 無關
        from flatness.positions import Names
        pos = probe_positions([self.placed("row-1", [(1, 3), (2, 1)])], PlateConfig(900, 600, 5),
                              Names().with_grid(5, 5))                 # grid 傳 5×5 也被忽略
        self.assertEqual(pos[("row-1", 1)], (900.0, 600.0))           # (第1排,點3)=末點右緣、首排下緣 → 右下角
        self.assertEqual(pos[("row-1", 2)], (0.0, 0.0))               # (第2排,點1)=首點左緣、末排上緣 → 左上角


if __name__ == "__main__":
    unittest.main()
