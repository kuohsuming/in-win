"""示範量測來源的虛擬讀值（--demo）：平滑的面，供 3D 繪圖驗證。"""

import json
import unittest
from pathlib import Path

from helpers import ROOT  # noqa: F401  路徑設定

from flatness import lan, measure

DEF = json.loads((Path(__file__).resolve().parents[1] / "installer" / "dl-en1.json").read_text(encoding="utf-8"))


class DemoStationTest(unittest.TestCase):
    def station(self, force, seed):
        s = measure.DemoStation(DEF, lan.standards(DEF), seed=seed, delay=0)
        s.force = force
        return s, lan.standards(DEF)

    def states(self, force, seed):
        s, std = self.station(force, seed)
        return [measure.judge(r.value, std[r.key][r.probe_id]) for r in s.read()]

    def test_pass_all_within_limits(self):
        for seed in range(30):
            self.assertEqual(set(self.states("pass", seed)), {measure.OK})

    def test_fail_exactly_one_point_out(self):
        for seed in range(30):
            st = self.states("fail", seed)
            self.assertEqual(sum(x in (measure.HI, measure.LO) for x in st), 1, st)
            self.assertNotIn(measure.ERR, st)

    def test_error_one_probe_without_data(self):
        for seed in range(30):
            self.assertEqual(self.states("error", seed).count(measure.ERR), 1)

    def test_smooth_surface_neighbours_close(self):
        # 同一排相鄰探頭的差距遠小於允許誤差（不是每點獨立亂數）
        s, std = self.station("pass", 3)
        by = {(r.key, r.probe_id): r.value for r in s.read()}
        for d in DEF["dl_en1"]:
            ids = sorted(p["id"] for p in d["probes"])
            half = (std[d["key"]][ids[0]].upper - std[d["key"]][ids[0]].lower) / 2
            for a, b in zip(ids, ids[1:]):
                self.assertLess(abs(by[(d["key"], a)] - by[(d["key"], b)]), 1.2 * half)


if __name__ == "__main__":
    unittest.main()
