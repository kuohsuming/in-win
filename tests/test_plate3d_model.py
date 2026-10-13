"""3D 繪圖計算（P3D-02～P3D-07）：測試資料、拒絕條件、兩種模式、凸包、比例。"""

import json
import unittest

from helpers import ROOT  # noqa: F401  路徑設定

from flatness.plate3d.config import PlateConfig
from flatness.plate3d.model import DETRENDED, STANDARD, ProbeReading, RefuseError, build_model, check

VECTORS = json.loads((ROOT / "tests" / "data" / "plate3d_vectors.json").read_text(encoding="utf-8"))
NAMES = ["左", "左中", "右中", "右"]
ROWS = ["前排", "中排", "後排"]


def readings(values, tol=0.2, cols=4, plate=PlateConfig()):
    """values 依前排左→後排右排列；None 為無數據。"""
    out = []
    rows = len(values) // cols
    for k, v in enumerate(values):
        r, c = divmod(k, cols)
        out.append(ProbeReading(f"{r + 1}-{c + 1}", f"{ROWS[r]} {NAMES[c]}",
                                plate.length * (c + 0.5) / cols, plate.width * (r + 0.5) / rows,
                                v, tol, "err" if v is None else "ok"))
    return out


def from_case(case):
    pts = [ProbeReading(f"p{i}", f"點{i}", p["x"], p["y"], p["reading_mm"], 0.2,
                        "err" if p["reading_mm"] is None else "ok") for i, p in enumerate(case["points"])]
    pl = case["plate"]
    return pts, PlateConfig(pl["length"], pl["width"], pl["thickness"]), pl["probe_side"]


class Vectors(unittest.TestCase):
    """提案 11 節：扣除傾斜模式的殘差與平面度（µm，誤差 < 0.01 µm）。"""

    def test_cases(self):
        tol = VECTORS["tolerance_um"]
        for case in VECTORS["cases"]:
            with self.subTest(case["name"]):
                pts, plate, side = from_case(case)
                m = build_model(pts, plate, DETRENDED, probe_side=side)
                exp = case["expected"]
                self.assertAlmostEqual(m.spread_mm * 1000, exp["flatness_um"], delta=tol)
                got = [m.z_mm.get(p.key) for p in pts]
                for g, e in zip(got, exp["residual_um"]):
                    if e is None:
                        self.assertIsNone(g)
                    else:
                        self.assertAlmostEqual(g * 1000, e, delta=tol)

    def test_named_flatness(self):
        flat = {c["name"]: c["expected"]["flatness_um"] for c in VECTORS["cases"]}
        self.assertAlmostEqual(flat["fail_below"], 66.433, places=3)
        self.assertAlmostEqual(flat["missing_one"], 66.591, places=3)
        self.assertEqual(flat["pure_tilt"], 0)


class Refuse(unittest.TestCase):
    def test_too_few_configured(self):
        """P3D-02、P3D-G2：1 台 2 個探頭。"""
        pts = [ProbeReading("1-1", "前排 左", 250, 300, 0.01, 0.2, "ok"),
               ProbeReading("1-2", "前排 右", 750, 300, -0.02, 0.2, "ok")]
        with self.assertRaises(RefuseError) as cm:
            check(pts)
        self.assertIn("本次只有 2 個有效量測點，至少需要 3 個", str(cm.exception))
        self.assertIn("目前設定只有 2 個探頭", str(cm.exception))

    def test_zero_and_one(self):
        for vals in ([None, None, None], [0.1, None, None]):
            with self.subTest(vals), self.assertRaises(RefuseError):
                check(readings(vals, cols=3))

    def test_missing_points_listed(self):
        """設定 3 個、1 個無數據 → 拒絕並列出該點。"""
        pts = readings([0.1, None, None], cols=3)
        with self.assertRaises(RefuseError) as cm:
            check(pts)
        msg = str(cm.exception)
        self.assertIn("只有 1 個有效量測點", msg)
        self.assertIn("設定 3 個探頭；無數據：前排 左中、前排 右中", msg)

    def test_collinear(self):
        """P3D-03、P3D-G3：1 排 4 點。"""
        with self.assertRaises(RefuseError) as cm:
            check(readings([0.1, 0.0, -0.1, 0.05]))
        self.assertIn("同一直線上", str(cm.exception))

    def test_two_rows_two_probes_ok(self):
        check(readings([0.1, 0.0, -0.1, 0.05], cols=2))

    def test_three_points_ok(self):
        pts = [ProbeReading("a", "a", 100, 100, 0.1, 0.2, "ok"), ProbeReading("b", "b", 900, 100, 0.0, 0.2, "ok"),
               ProbeReading("c", "c", 500, 500, -0.1, 0.2, "ok")]
        m = build_model(pts, PlateConfig())
        self.assertEqual(len(m.z_mm), 3)


class Modes(unittest.TestCase):
    VALUES = [0.003, -0.002, 0.012, -0.009, -0.004, 0.009, 0.217, -0.010, -0.300, -0.005, 0.009, 0.004]

    def test_standard_matches_readings(self):
        """P3D-06：相對標準件的標籤數值即讀值；高度為 −讀值（探頭在下方）。"""
        pts = readings(self.VALUES)
        m = build_model(pts, PlateConfig())
        for p in pts:
            self.assertEqual(m.label_value(p.key), p.value_mm)
            self.assertAlmostEqual(m.z_mm[p.key], -p.value_mm)
        self.assertAlmostEqual(m.spread_mm, 0.217 + 0.300)
        self.assertEqual(m.lowest[0], "2-3")   # 讀值 +0.217 → 表面最低（P3D-05）
        self.assertEqual(m.highest[0], "3-1")

    def test_missing_point_excluded(self):
        """P3D-04：無數據的點不參與。"""
        vals = list(self.VALUES)
        vals[5] = None
        m = build_model(readings(vals), PlateConfig())
        self.assertEqual(len(m.z_mm), 11)
        self.assertNotIn("2-2", m.z_mm)
        self.assertIsNone(m.label_value("2-2"))

    def test_pure_tilt_detrended_zero(self):
        vals = [0.001 * c + 0.002 * r for r in range(3) for c in range(4)]
        m = build_model(readings(vals), PlateConfig(), DETRENDED)
        for v in m.z_mm.values():
            self.assertAlmostEqual(v, 0.0, places=9)
        self.assertAlmostEqual(m.spread_mm, 0.0, places=9)

    def test_grid_passes_through_points(self):
        """插值網格經過量測點；凸包外的格子標為推估。"""
        plate = PlateConfig(1000, 600, 5)
        m = build_model(readings(self.VALUES), plate)   # 網格間距 25 mm，量測點 (125, 100)… 剛好在網格上
        self.assertEqual((m.nx, m.ny), (41, 25))
        for p in m.valid:
            i, j = round(p.x / 25), round(p.y / 25)
            self.assertAlmostEqual(m.grid[j][i], m.z_mm[p.key], places=9)
        self.assertFalse(m.inside[0][0])          # 左前角在量測點範圍外
        self.assertTrue(m.inside[12][20])         # 板子中央
        self.assertTrue(m.inside[4][5])           # (125, 100) 量測點本身（邊上）

    def test_scale_uses_tolerance(self):
        """P3D-07：讀值都在 ±0.01、允許誤差 0.2 → lim = 0.2，好板近乎平坦。"""
        m = build_model(readings([0.01, -0.01, 0.005, 0.0, -0.005, 0.01, 0.0, 0.002, -0.01, 0.0, 0.01, -0.002]),
                        PlateConfig())
        self.assertAlmostEqual(m.lim_mm, 0.2, places=3)
        self.assertAlmostEqual(m.thickness_vis, 50.0)
        self.assertAlmostEqual(m.exaggeration, 0.4 * 50 / 0.2)
        big = build_model(readings(self.VALUES), PlateConfig())
        self.assertGreaterEqual(big.lim_mm, 0.300)

    def test_wide_plate_grid(self):
        m = build_model(readings(self.VALUES, plate=PlateConfig(300, 900, 5), cols=4), PlateConfig(300, 900, 5))
        self.assertEqual(m.ny, 41)
        self.assertEqual(m.nx, max(9, round(40 * 300 / 900) + 1))


if __name__ == "__main__":
    unittest.main()
