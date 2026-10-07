"""探頭校準：放大器歸零（CAL-02～CAL-06、CAL-08）。"""

import threading
import unittest

from flatness import calibrate, lan
from flatness.config import Calibration


class FakeAmp:
    """模擬放大器：series 為依序取樣的原始值；歸零時以最後一次讀值為基準，之後讀值扣除基準。"""

    def __init__(self, *series, error=None, prepare_error=None, response=0.0):
        self.series = list(series)
        self.error, self.prepare_error, self.response = error, prepare_error, response
        self.zero, self.last = 0.0, None
        self.calls, self.ops = [], []

    def prepare_preset(self, key, probe_id):
        self.ops.append("prepare")
        if self.prepare_error:
            raise calibrate.SampleError(self.prepare_error)
        return {}

    def preset(self, key, probe_id, execute):
        self.ops.append("execute" if execute else "reset")
        self.zero = self.last if execute else 0.0

    def response_time(self, key, probe_id):
        return self.response

    def zero_base(self, key, probe_id):
        return self.zero

    def sample(self, key, probe_id, n, interval, cancel=None):
        self.calls.append((key, probe_id, n, interval))
        if cancel is not None and cancel.is_set():
            raise calibrate.Cancelled()
        if self.error:
            raise calibrate.SampleError(self.error)
        vals = self.series.pop(0)
        assert len(vals) == n
        self.last = vals[-1]
        return [round(v - self.zero, 6) for v in vals]

    def resolution(self, key, probe_id):
        return 0.0001


DEV = {"key": "row-1", "name": "前排", "mac": "00:01:FC:DE:3A:75",
       "probes": [{"id": 1, "description": "左"}, {"id": 2, "description": "右", "zero_offset": 12.3,
                                                    "zeroed_at": "2026-10-01T08:00:00"}]}
CS = Calibration(samples=20, interval_ms=50, verify=5, tolerance=0.002)
STEADY = [12.4987, 12.4990, 12.4984] * 6 + [12.4987, 12.4987]   # σ ≈ 0.00024


class CalibrateTest(unittest.TestCase):
    def test_pass(self):  # CAL-G1：清除 → 取樣 → 歸零 → 驗證
        amp = FakeAmp(STEADY, [12.4988, 12.4985, 12.4987, 12.4988, 12.4987])
        res = calibrate.run(amp, DEV, 2, CS)
        self.assertTrue(res.ok, res.reason)
        self.assertEqual(amp.ops, ["prepare", "reset", "execute"])
        self.assertEqual(res.new_offset, 12.4987)                # 從放大器讀回的歸零基準
        self.assertAlmostEqual(res.mean, sum(STEADY) / 20)
        self.assertEqual(res.old_offset, 12.3)
        self.assertEqual(res.verify, [0.0001, -0.0002, 0.0, 0.0001, 0.0])
        self.assertTrue(res.cleared and res.zeroed)
        self.assertEqual([c[1:] for c in amp.calls], [(2, 20, 0.05), (2, 5, 0.05)])  # 只取樣選取的探頭（CAL-A7）

    def test_interval_not_below_response_time(self):  # 放大器響應時間 100 ms
        amp = FakeAmp(STEADY, [12.4987] * 5, response=0.1)
        res = calibrate.run(amp, DEV, 1, CS)
        self.assertEqual((res.interval, [c[3] for c in amp.calls]), (0.1, [0.1, 0.1]))

    def test_unstable_samples_fail_and_stay_cleared(self):  # CAL-G2
        noisy = [12.49, 12.51] * 10
        amp = FakeAmp(noisy)
        res = calibrate.run(amp, DEV, 1, CS)
        self.assertEqual(res.result, calibrate.FAIL)
        self.assertIn("讀值不穩定", res.reason)
        self.assertIsNone(res.new_offset)
        self.assertEqual(amp.ops, ["prepare", "reset"])         # 已清除、未歸零
        self.assertTrue(res.cleared)

    def test_verify_moved_fails_and_clears_again(self):  # CAL-04、CAL-A3：未通過的歸零不留在放大器
        amp = FakeAmp(STEADY, [12.4987, 12.4987, 12.5100, 12.4987, 12.4987])
        res = calibrate.run(amp, DEV, 1, CS)
        self.assertEqual(res.result, calibrate.FAIL)
        self.assertIn("驗證", res.reason)
        self.assertEqual(amp.ops, ["prepare", "reset", "execute", "reset"])
        self.assertFalse(res.zeroed)

    def test_zero_base_must_match_mean(self):  # 讀回的歸零基準為 0（預設作用在 R.V.）→ 失敗並清除
        amp = FakeAmp(STEADY, [12.4987] * 5)
        amp.zero_base = lambda key, probe_id: 0.0
        res = calibrate.run(amp, DEV, 1, CS)
        self.assertEqual(res.result, calibrate.FAIL)
        self.assertIn("P.V.", res.reason)
        self.assertEqual(amp.ops, ["prepare", "reset", "execute", "reset"])

    def test_zero_sigma_uses_resolution(self):  # CAL-A2：σ 為 0 時 1 個解析度的晃動仍通過
        flat = [12.5] * 20
        res = calibrate.run(FakeAmp(flat, [12.5, 12.5001, 12.4999, 12.5, 12.5]), DEV, 1, CS)
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

    def test_sample_error_after_clear(self):
        amp = FakeAmp(error="第 7 次：無有效數據")
        res = calibrate.run(amp, DEV, 1, CS)
        self.assertEqual((res.result, res.reason, res.cleared), (calibrate.FAIL, "取樣失敗：第 7 次：無有效數據", True))

    def test_prepare_error_changes_nothing(self):  # 設定讀寫失敗：尚未清除歸零
        amp = FakeAmp(prepare_error="通訊失敗")
        res = calibrate.run(amp, DEV, 1, CS)
        self.assertEqual((res.result, res.cleared, amp.ops), (calibrate.FAIL, False, ["prepare"]))
        self.assertIn("放大器設定失敗", res.reason)

    def test_cancel(self):
        cancel = threading.Event()
        cancel.set()
        amp = FakeAmp(STEADY)
        res = calibrate.run(amp, DEV, 1, CS, cancel)
        self.assertEqual((res.result, res.cleared, amp.ops), (calibrate.CANCEL, False, ["prepare"]))

    def test_record(self):  # CAL-08
        res = calibrate.run(FakeAmp(STEADY, [12.4987] * 5), DEV, 2, CS)
        rec = calibrate.record(res, "ST01", True)
        self.assertEqual((rec["device_key"], rec["probe_id"], rec["samples"], rec["result"], rec["adopted"],
                          rec["old_offset"], rec["new_offset"]), ("row-1", 2, 20, "PASS", True, 12.3, 12.4987))


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
