"""探頭校準：軟體歸零（CAL-02～CAL-06、CAL-08）。"""

import threading
import unittest

from flatness import calibrate, lan
from flatness.config import Calibration


class FakeStation:
    """回傳預設讀值序列的取樣來源。"""

    def __init__(self, *series, error=None):
        self.series = list(series)
        self.error = error
        self.calls = []

    def sample(self, key, probe_id, n, interval, cancel=None):
        self.calls.append((key, probe_id, n, interval))
        if cancel is not None and cancel.is_set():
            raise calibrate.Cancelled()
        if self.error:
            raise calibrate.SampleError(self.error)
        vals = self.series.pop(0)
        assert len(vals) == n
        return vals

    def resolution(self, key, probe_id):
        return 0.0001


DEV = {"key": "row-1", "name": "前排", "mac": "00:01:FC:DE:3A:75",
       "probes": [{"id": 1, "description": "左"}, {"id": 2, "description": "右", "zero_offset": 12.3,
                                                    "zeroed_at": "2026-10-01T08:00:00"}]}
CS = Calibration(samples=20, interval_ms=50, verify=5, tolerance=0.002)
STEADY = [12.4987, 12.4990, 12.4984] * 6 + [12.4987, 12.4987]   # σ ≈ 0.00024


class CalibrateTest(unittest.TestCase):
    def test_pass(self):  # CAL-G1
        st = FakeStation(STEADY, [12.4988, 12.4985, 12.4987, 12.4988, 12.4987])
        res = calibrate.run(st, DEV, 2, CS)
        self.assertTrue(res.ok, res.reason)
        self.assertAlmostEqual(res.new_offset, sum(STEADY) / 20)
        self.assertEqual(res.old_offset, 12.3)
        self.assertEqual(len(res.verify), 5)
        self.assertLess(abs(res.verify_mean), CS.tolerance)
        self.assertEqual([c[1:] for c in st.calls], [(2, 20, 0.05), (2, 5, 0.05)])  # 只取樣選取的探頭（CAL-A7）

    def test_unstable_samples_fail(self):  # CAL-G2
        noisy = [12.49, 12.51] * 10
        res = calibrate.run(FakeStation(noisy), DEV, 1, CS)
        self.assertEqual(res.result, calibrate.FAIL)
        self.assertIn("讀值不穩定", res.reason)
        self.assertIsNone(res.new_offset)

    def test_verify_moved_fails(self):  # CAL-04：驗證時標準件被移動
        res = calibrate.run(FakeStation(STEADY, [12.4987, 12.4987, 12.5100, 12.4987, 12.4987]), DEV, 1, CS)
        self.assertEqual(res.result, calibrate.FAIL)
        self.assertIn("驗證", res.reason)

    def test_zero_sigma_uses_resolution(self):  # CAL-A2：σ 為 0 時 1 個解析度的晃動仍通過
        flat = [12.5] * 20
        res = calibrate.run(FakeStation(flat, [12.5, 12.5001, 12.4999, 12.5, 12.5]), DEV, 1, CS)
        self.assertTrue(res.ok, res.reason)
        self.assertEqual(res.sigma, 0.0)
        self.assertEqual(res.bound, 0.0001)

    def test_old_one_sigma_rule_would_fail_normal_probe(self):  # 說明：舊規則 5 次皆在 1σ 內過嚴
        import random
        rng = random.Random(1)
        fails = 0
        for _ in range(500):
            vals = [rng.gauss(0, 1) for _ in range(5)]
            fails += any(abs(v) > 1 for v in vals)
        self.assertGreater(fails / 500, 0.75)

    def test_sample_error_and_cancel(self):
        res = calibrate.run(FakeStation(error="第 7 次：無有效數據"), DEV, 1, CS)
        self.assertEqual((res.result, res.reason), (calibrate.FAIL, "取樣失敗：第 7 次：無有效數據"))
        cancel = threading.Event()
        cancel.set()
        res = calibrate.run(FakeStation(STEADY), DEV, 1, CS, cancel)
        self.assertEqual(res.result, calibrate.CANCEL)

    def test_record(self):  # CAL-08
        res = calibrate.run(FakeStation(STEADY, [12.4987] * 5), DEV, 2, CS)
        rec = calibrate.record(res, "ST01", True)
        self.assertEqual((rec["device_key"], rec["probe_id"], rec["samples"], rec["result"], rec["adopted"],
                          rec["old_offset"]), ("row-1", 2, 20, "PASS", True, 12.3))


class ClearZeroTest(unittest.TestCase):  # CAL-06
    def test_replace_clears_offsets(self):
        from helpers import by_mac, sample_devices
        devs = sample_devices()
        front = by_mac(devs)["00:01:FC:DE:3A:75"]
        for p in front.config["probes"]:
            p.update(zero_offset=1.0, zeroed_at="2026-10-07T15:00:00")
        new = lan.replace(devs, front.mac, "00:01:FC:12:39:A0")
        self.assertTrue(all("zero_offset" not in p for p in new.config["probes"]))
        self.assertTrue(all("zero_offset" in p for p in front.config["probes"]))  # 舊機保留


if __name__ == "__main__":
    unittest.main()
