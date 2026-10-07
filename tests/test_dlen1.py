"""DL-EN1 連線與讀值（DEV-02～DEV-04、DEV-07、DEV-09、DEF-05、DEF-06）。

以本機 TCP 假設備回應命令；回應格式依 2026-10-07 真機紀錄。
"""

import socket
import threading
import unittest

from flatness.dlen1 import DlEn1Station


class FakeDlEn1:
    """一問一答的假 DL-EN1：replies 為 命令 → 回應（不含 CR LF）；None 表示不回應。"""

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
                    reply = self.replies.get(cmd, f"ER,{cmd.split(',')[0]},255")
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
        replies["SR,00,669"] = "SR,00,669,+000000002"
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

    def test_offset_applied_and_uncalibrated(self):  # CAL-03、CAL-07、CAL-09
        _, st = self.station(REAL, offsets={1: -0.3, 2: None})
        (s,) = st.detect()
        self.assertEqual(s.uncalibrated, {2})
        r1, r2 = st.read()
        self.assertAlmostEqual(r1.value, 0.0029)          # −0.2971 − (−0.3)
        self.assertEqual((r1.offset, r1.raw), (-0.3, "-000002971"))
        self.assertEqual((r2.value, r2.error, r2.raw), (None, "未校準", "+000000358"))

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
