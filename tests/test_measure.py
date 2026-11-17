"""JDG-07：最佳點修正的判定公式（measure.best_offset／correct 與修正後判定）。"""

import unittest

from helpers import ROOT  # noqa: F401  路徑設定

from flatness import measure
from flatness.config import Standard


class BestOffsetTest(unittest.TestCase):
    def test_closest_to_zero(self):
        self.assertEqual(measure.best_offset([2.0, -3.0, 2.5]), 2.0)      # |2| 最小
        self.assertEqual(measure.best_offset([5.0, 5.3, 5.1]), 5.0)       # 整片墊高

    def test_tie_takes_smaller(self):  # 並列取較小（較負）者，結果可重現
        self.assertEqual(measure.best_offset([2.0, -2.0]), -2.0)
        self.assertEqual(measure.best_offset([-2.0, 2.0]), -2.0)

    def test_ignores_none_and_empty(self):
        self.assertEqual(measure.best_offset([None, 1.0, None]), 1.0)
        self.assertIsNone(measure.best_offset([]))
        self.assertIsNone(measure.best_offset([None, None]))

    def test_correct_subtracts_best(self):
        self.assertAlmostEqual(measure.correct(2.5, 2.0), 0.5)
        self.assertAlmostEqual(measure.correct(-3.0, 2.0), -5.0)
        self.assertIsNone(measure.correct(None, 2.0))
        self.assertAlmostEqual(measure.correct(2.5, None), 2.5)           # 無最佳點不修正


class CorrectedJudgeTest(unittest.TestCase):
    std = Standard(0.0, -0.2, 0.2)

    def judged(self, values):
        best = measure.best_offset(values)
        states = [measure.judge(measure.correct(v, best), self.std) for v in values]
        return best, states, measure.overall(states)

    def test_defect_relative_to_best_fails(self):  # +2.0、−3.0、+2.5 → 最佳 +2.0
        best, states, verdict = self.judged([2.0, -3.0, 2.5])
        self.assertEqual(best, 2.0)
        self.assertEqual(states, [measure.OK, measure.LO, measure.HI])
        self.assertEqual(verdict, "fail")

    def test_common_offset_passes(self):  # 整片同墊高，只有超標的點偏高（舊版會整片偏高）
        best, states, verdict = self.judged([5.0, 5.05, 5.1, 5.35])
        self.assertEqual(best, 5.0)
        self.assertEqual(states, [measure.OK, measure.OK, measure.OK, measure.HI])
        self.assertEqual(verdict, "fail")

    def test_flat_plate_all_pass(self):  # 整片相對最佳點都在 ±0.2 內
        _best, states, verdict = self.judged([5.0, 5.08, 4.96, 5.05])
        self.assertEqual(states, [measure.OK] * 4)
        self.assertEqual(verdict, "pass")

    def test_single_point_zeroed(self):  # 只有一個有效點 → 修正為 0 → 合格
        _best, states, verdict = self.judged([7.3])
        self.assertEqual(states, [measure.OK])
        self.assertEqual(verdict, "pass")


if __name__ == "__main__":
    unittest.main()
