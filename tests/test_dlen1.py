"""DL-EN1 連線與讀值（DEV-02～DEV-04、DEV-07、DEV-09、DEF-05、DEF-06）。

以本機 TCP 假設備回應命令；回應格式依 2026-10-07 真機紀錄。
"""

import socket
import threading
import unittest

from flatness.dlen1 import DlEn1Station


class FakeDlEn1:
    """一問一答的假 DL-EN1：replies 為 命令 → 回應（不含 CR LF）的 dict，或以命令回傳回應的函式。"""

    def __init__(self, replies: dict):
        self.replies = replies
        self.received: list[str] = []
        self.srv = socket.socket()
        self.srv.bind(("127.0.0.1", 0))
        self.srv.listen()
        self.port = self.srv.getsockname()[1]
        self.conns = 0
        threading.Thread(target=self._serve, daemon=True).start()

    def _serve(self):
        while True:
            try:
                c, _ = self.srv.accept()
            except OSError:
                return
            self.conns += 1
            threading.Thread(target=self._handle, args=(c,), daemon=True).start()

    def _handle(self, c):
        buf = b""
        with c:
            while True:
                try:
                    data = c.recv(1024)
                except OSError:
                    return
                if not data:
                    return
                buf += data
                while b"\r\n" in buf:
                    line, buf = buf.split(b"\r\n", 1)
                    cmd = line.decode()
                    self.received.append(cmd)
                    reply = (self.replies(cmd) if callable(self.replies) else
                             self.replies.get(cmd, f"ER,{cmd.split(',')[0]},255"))
                    if reply == "CLOSE":
                        return
                    c.sendall(reply.encode() + b"\r\n")

    def close(self):
        self.srv.close()


REAL = {  # 真機回應（2 台放大器、4 位小數）
    "SR,00,077": "SR,00,077,+000000002",
    "SR,00,000": "SR,00,000,+000000000",
    "FR,01,037": "FR,01,037,+000000004",
    "FR,02,037": "FR,02,037,+000000004",
    "MS": "MS,02,-000002971,02,+000000358",
}


class Gt2:
    """假 DL-EN1 加上放大器 ID 2 的歸零狀態：原始值 +0.0358，P.V. ＝ 原始值 − 歸零基準；
    預設資料選擇（148）為 0（R.V.）時 R.V. 也一起歸零（真機行為），為 1（P.V.）時 R.V. 不變。"""

    RV = 358

    def __init__(self, zero=0, settings=None):
        self.zero = zero
        self.mem = {148: 1, 149: 0, 150: 0, 67: 0, 72: 0, 77: 0, 82: 0, 132: 3, **(settings or {})}

    def __call__(self, cmd):
        f = cmd.split(",")
        if f[0] == "SW" and f[1] == "02":
            no, v = int(f[2]), int(f[3])
            if no == 1:
                self.zero = self.RV
            elif no == 2:
                self.zero = 0
            elif no in self.mem:
                self.mem[no] = v
            else:
                return f"ER,SW,255"
            return ",".join(f[:3])
        if f[0] == "SR" and f[1] == "02":
            no = int(f[2])
            rv = self.RV - self.zero if self.mem[148] == 0 else self.RV
            v = {37: self.RV - self.zero, 38: rv}.get(no, self.mem.get(no))
            return f"SR,02,{f[2]},{v:+010d}" if v is not None else "ER,SR,255"
        if f[0] == "SR" and f[1] == "01" and f[2] in ("037", "038"):
            return f"SR,01,{f[2]},-000002971"
        if cmd == "MS":
            return f"MS,02,-000002971,02,{self.RV - self.zero:+010d}"
        return REAL.get(cmd, f"ER,{f[0]},255")


def sw(dev):
    return [c for c in dev.received if c.startswith("SW")]


def definition(port, probes=(1, 2), max_probes=None, ip="127.0.0.1", offsets=None):
    """offsets：探頭 id → 校準偏移量；預設全部以 0 校準，None 值表示未校準。"""
    offsets = {i: 0.0 for i in probes} if offsets is None else offsets

    def probe(i):
        p = {"id": i, "description": f"P{i}"}
        if offsets.get(i) is not None:
            p.update(zero_offset=offsets[i], zeroed_at="2026-10-07T15:00:00")
        return p
    return {"version": 1, "dl_en1": [{
        "key": "row-1", "name": "前排", "ipv4": ip, "port": port,
        "max_probes": max_probes or len(probes),
        "probes": [probe(i) for i in probes]}]}


class DlEn1StationTest(unittest.TestCase):
    def station(self, replies, **kw):
        dev = FakeDlEn1(replies)
        self.addCleanup(dev.close)
        st = DlEn1Station(definition(dev.port, **kw), timeout=1.0)
        self.addCleanup(st.close)
        return dev, st

    def test_detect_and_read_real_format(self):  # DEV-02、DEV-03、DEF-05
        dev, st = self.station(REAL)
        (s,) = st.detect()
        self.assertTrue(s.reachable)
        self.assertEqual((s.probe_errors, s.error, s.booting), ({}, None, False))
        self.assertEqual(st.decimals, {("row-1", 1): 4, ("row-1", 2): 4})
        r = st.read()
        self.assertEqual([(x.probe_id, x.value, x.raw, x.error) for x in r],
                         [(1, -0.2971, "-000002971", None), (2, 0.0358, "+000000358", None)])
        self.assertEqual(dev.conns, 1)  # DEV-09：常駐 1 條連線
        self.assertNotIn("SW", " ".join(dev.received))  # NFR-11：不送寫入命令

    def test_only_defined_probes(self):  # DEF-05：實際 2 台、只定義 ID 2
        _, st = self.station(REAL, probes=(2,), max_probes=2)
        st.detect()
        self.assertEqual([(x.probe_id, x.value) for x in st.read()], [(2, 0.0358)])

    def test_missing_amplifier(self):  # DEF-06：連接 2 台、定義到 ID 3
        _, st = self.station(REAL, probes=(1, 2, 3))
        (s,) = st.detect()
        self.assertIn("放大器未連接", s.probe_errors[3])
        self.assertEqual(st.read()[2].error, "探頭無回應（放大器未連接）")

    def test_more_amplifiers_than_defined(self):  # DEF-06
        _, st = self.station(REAL, probes=(1,), max_probes=1)
        (s,) = st.detect()
        self.assertEqual(s.error, "探頭台數超出定義（連接 2 台，設定 1 台）")

    def test_no_data_and_amp_error(self):  # 5.1 特殊值、輸出狀態 03
        replies = dict(REAL, MS="MS,02,+099999999,03,+000000000")
        replies["SR,00,670"] = "SR,00,670,+000000002"  # 放大器 ID 2 → 668 ＋ 2
        _, st = self.station(replies)
        (s,) = st.detect()
        self.assertEqual(s.probe_errors, {2: "放大器錯誤（錯誤代碼 2）"})
        r = st.read()
        self.assertEqual([(x.value, x.error) for x in r], [(None, "無有效數據"), (None, "放大器錯誤")])

    def test_booting(self):  # DEV-07
        _, st = self.station({"SR,00,077": "ER,SR,031"})
        (s,) = st.detect()
        self.assertTrue(s.booting)

    def test_unit_error(self):  # DEV-02：整體狀態非 0 時讀 008、009
        replies = dict(REAL)
        replies.update({"SR,00,000": "SR,00,000,+000000001", "SR,00,008": "SR,00,008,+000000000",
                        "SR,00,009": "SR,00,009,+000000051"})
        _, st = self.station(replies)
        (s,) = st.detect()
        self.assertIn("錯誤代碼 51", s.error)

    def test_amplifier_value_and_uncalibrated(self):  # CAL-03、CAL-07、CAL-09
        _, st = self.station(REAL, offsets={1: -0.3, 2: None})
        (s,) = st.detect()                                # 讀不到 P.V.／R.V.（ER）：不判定歸零
        self.assertEqual(s.uncalibrated, {2: "未校準"})
        r1, r2 = st.read()
        self.assertEqual(r1.value, -0.2971)               # 放大器已歸零：直接使用，不扣偏移量
        self.assertEqual((r1.offset, r1.raw), (-0.3, "-000002971"))
        self.assertEqual((r2.value, r2.error, r2.raw), (None, "未校準", "+000000358"))

    def test_zero_matches_record(self):  # CAL-10：歸零基準與紀錄相符
        dev, st = self.station(Gt2(zero=358), offsets={1: 0.0, 2: 0.0358})
        (s,) = st.detect()
        self.assertEqual(s.uncalibrated, {})
        r1, r2 = st.read()
        self.assertEqual((r2.value, r2.offset), (0.0, 0.0358))
        self.assertEqual(sw(dev), [])                     # 偵測與量測不寫入（NFR-11）

    def test_zero_lost_or_changed(self):  # CAL-10、CAL-A9
        amp = Gt2(zero=0)                                 # 放大器被重設：歸零遺失
        _, st = self.station(amp, offsets={1: 0.0, 2: 0.0358})
        (s,) = st.detect()
        self.assertEqual(s.uncalibrated, {2: "歸零遺失"})
        self.assertEqual((st.read()[1].value, st.read()[1].error), (None, "歸零遺失"))
        amp.zero = 100                                    # 面板上重新歸零
        (s,) = st.detect()
        self.assertEqual(s.uncalibrated, {2: "歸零已變更"})
        amp.zero = 358 + 10                               # 差 0.001，在容許值 0.002 內
        (s,) = st.detect()
        self.assertEqual(s.uncalibrated, {})
        self.assertIsNone(st.read()[1].error)

    def test_zero_check_skipped_on_invalid_value(self):  # SR 特殊值：不判定
        amp = Gt2(zero=0)
        replies = lambda cmd: "SR,02,038,-009999998" if cmd == "SR,02,038" else amp(cmd)  # noqa: E731
        _, st = self.station(replies, offsets={1: 0.0, 2: 0.0358})
        (s,) = st.detect()
        self.assertEqual(s.uncalibrated, {})

    def test_preset_commands(self):  # CAL-02、NFR-11：只寫選取的放大器、只寫必要的資料編號
        amp = Gt2(settings={149: 1, 72: 50})
        dev, st = self.station(amp)
        st.detect()
        before = st.prepare_preset("row-1", 2)
        self.assertEqual((before[149], before[72], before[148]), (1, 50, 1))
        self.assertEqual(sw(dev), ["SW,02,149,+000000000", "SW,02,072,+000000000"])
        self.assertEqual(st.prepare_preset("row-1", 2)[149], 0)  # 已符合：不再寫入
        self.assertEqual(len(sw(dev)), 2)
        st.preset("row-1", 2, True)
        self.assertEqual((st.zero_base("row-1", 2), st.sample("row-1", 2, 2, 0.0)), (0.0358, [0.0, 0.0]))
        st.preset("row-1", 2, False)
        self.assertEqual((st.zero_base("row-1", 2), st.sample("row-1", 2, 1, 0.0)), (0.0, [0.0358]))
        self.assertEqual(sw(dev)[2:], ["SW,02,001,+000000001", "SW,02,002,+000000001"])
        self.assertEqual(st.response_time("row-1", 2), 0.1)

    def test_calibrate_end_to_end(self):  # CAL-G1：清除 → 取樣 → 歸零 → 驗證，從不送 003／005
        from flatness import calibrate
        from flatness.config import Calibration
        amp = Gt2(zero=100, settings={148: 0, 150: 1})  # 148 原為 R.V.：改為 P.V.
        dev, st = self.station(amp, offsets={1: 0.0, 2: 0.01})
        st.detect()
        d = definition(0, offsets={1: 0.0, 2: 0.01})["dl_en1"][0]
        res = calibrate.run(st, d, 2, Calibration(samples=3, interval_ms=0, verify=2, tolerance=0.002))
        self.assertTrue(res.ok, res.reason)
        self.assertEqual((res.samples, res.verify, res.new_offset, res.interval), ([0.0358] * 3, [0.0, 0.0], 0.0358, 0.1))
        self.assertEqual(sw(dev), ["SW,02,148,+000000001", "SW,02,150,+000000000", "SW,02,002,+000000001",
                                   "SW,02,001,+000000001"])
        self.assertTrue(all(c.split(",")[1] == "02" for c in sw(dev)))

    def test_calibrate_fails_when_rv_is_zeroed(self):  # 2026-10-07 真機：148 為 R.V. 時讀回的基準為 0
        from flatness import calibrate
        from flatness.config import Calibration
        amp = Gt2(settings={148: 0})
        replies = lambda cmd: "SW,02,148" if cmd.startswith("SW,02,148") else amp(cmd)  # noqa: E731 寫入無效
        dev, st = self.station(replies)
        st.detect()
        d = definition(0)["dl_en1"][0]
        res = calibrate.run(st, d, 2, Calibration(samples=3, interval_ms=0, verify=2, tolerance=0.002))
        self.assertEqual(res.result, calibrate.FAIL)
        self.assertIn("歸零基準", res.reason)
        self.assertEqual((sw(dev)[-1], amp.zero), ("SW,02,002,+000000001", 0))  # 未通過的歸零已清除

    def test_preset_error(self):  # 寫入被拒（例：按鍵鎖定）→ SampleError
        from flatness.calibrate import SampleError
        amp = Gt2()
        replies = lambda cmd: "ER,SW,012" if cmd.startswith("SW") else amp(cmd)  # noqa: E731
        _, st = self.station(replies)
        with self.assertRaises(SampleError):
            st.preset("row-1", 2, False)

    def test_sample_raw_values(self):  # CAL-02：原始值、不扣偏移量、間隔
        import time
        dev, st = self.station(REAL, offsets={1: 5.0, 2: 5.0})
        st.detect()
        t0 = time.monotonic()
        self.assertEqual(st.sample("row-1", 2, 4, 0.05), [0.0358] * 4)
        self.assertGreaterEqual(time.monotonic() - t0, 0.14)  # 3 個間隔
        self.assertEqual(st.resolution("row-1", 2), 0.0001)
        self.assertNotIn("SW", " ".join(dev.received))        # NFR-11

    def test_sample_errors(self):  # CAL-02：無有效數據即失敗
        from flatness.calibrate import SampleError
        _, st = self.station(dict(REAL, MS="MS,02,+099999999,02,+000000358"))
        with self.assertRaises(SampleError):
            st.sample("row-1", 1, 3, 0.0)

    def test_unreachable(self):  # DEV-04
        srv = socket.socket()
        srv.bind(("127.0.0.1", 0))
        port = srv.getsockname()[1]
        srv.close()  # 沒有人在聽：立刻拒絕連線
        st = DlEn1Station(definition(port), connect_timeout=0.5)
        self.addCleanup(st.close)
        (s,) = st.detect()
        self.assertFalse(s.reachable)
        self.assertTrue(all(x.error == "DL-EN1 偵測不到" for x in st.read()))

    def test_reconnects_after_device_closes(self):  # DEV-09：斷線自動重連
        replies = dict(REAL)
        dev, st = self.station(replies)
        st.detect()
        replies["MS"] = "CLOSE"            # 對方關閉連線
        self.assertEqual(st.read()[0].error, "DL-EN1 偵測不到")
        replies["MS"] = REAL["MS"]
        self.assertEqual(st.read()[0].value, -0.2971)  # 下一次自動重連
        self.assertEqual(dev.conns, 3)  # 原連線、斷線後立即重試一次、下一次讀值


if __name__ == "__main__":
    unittest.main()
