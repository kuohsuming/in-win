"""量測結果寫入資料庫（DAT-02～DAT-06）。

MySQL 測試需先執行 ./scripts/dev-mysql.sh start，否則略過；使用獨立的 flatness_test 資料庫。
"""

import json
import tempfile
import time
import unittest
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from flatness.config import Standard
from flatness.measure import ERR, LO, OK
from flatness.results import ResultSink, to_record
from flatness.store import MemoryStore, MySQLStore
from flatness.ui.main_window import InspectionResult, PointResult

STD = Standard(12.5, 12.45, 12.55)
T = datetime(2026, 10, 7, 14, 30, 5, 123000)


def result(serial="20261007143005123", judgment="FAIL"):
    return InspectionResult(serial, T, judgment, 1, [
        PointResult("row-1", 1, "前排", "左", "00:01:FC:DE:3A:75", LO, -0.2971, STD, "-000002971"),
        PointResult("row-1", 2, "前排", "右", "00:01:FC:DE:3A:75", OK, 12.5012, STD, "+000125012"),
        PointResult("row-1", 3, "前排", "中", "00:01:FC:DE:3A:75", ERR, None, None, "", "放大器未連接"),
    ])


def wait(cond, timeout=3.0):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if cond():
            return True
        time.sleep(0.02)
    return cond()


class RecordTest(unittest.TestCase):
    def test_to_record(self):  # DAT-02、DAT-03、DAT-06
        rec = to_record(result(), "ST01")
        self.assertEqual(rec["head"], {"serial": "20261007143005123", "station_id": "ST01",
                                       "measured_at": "2026-10-07T14:30:05.123", "judgment": "FAIL",
                                       "reread_count": 1})
        p1, p2, p3 = rec["points"]
        self.assertEqual((p1["judgment"], p1["measured_value"], p1["standard_value"], p1["lower_limit"],
                          p1["upper_limit"], p1["raw_response"], p1["device_mac"]),
                         ("LOW", -0.2971, 12.5, 12.45, 12.55, "-000002971", "00:01:FC:DE:3A:75"))
        self.assertEqual(p2["judgment"], "OK")
        self.assertEqual((p3["judgment"], p3["measured_value"], p3["standard_value"], p3["raw_response"],
                          p3["error_text"]), ("ERROR", None, None, None, "放大器未連接"))


class SinkTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name) / "buffer"
        self.store = MemoryStore()
        self.events = []

    def sink(self, retry=0.1):
        s = ResultSink(self.store, "ST01", self.dir, retry=retry)
        s.listener = self.events.append
        s.start()
        self.addCleanup(s.close, 0.5)
        return s

    def test_written_and_buffer_removed(self):  # DAT-02
        s = self.sink()
        s.write(result())
        self.assertTrue(wait(lambda: s.pending() == 0))
        head, points = self.store.inspections["20261007143005123"]
        self.assertEqual((head["judgment"], head["reread_count"], head["measured_at"], len(points)),
                         ("FAIL", 1, T, 3))
        self.assertEqual(self.events, [("written", "20261007143005123", 0)])

    def test_db_down_buffers_then_backfills(self):  # DAT-04
        self.store.available = False
        s = self.sink()
        for i in range(3):
            s.write(result(f"2026100714300512{i}"))
        self.assertTrue(wait(lambda: any(e[0] == "failed" for e in self.events)))
        self.assertEqual(s.pending(), 3)
        self.assertEqual(self.store.inspections, {})
        self.store.available = True
        self.assertTrue(wait(lambda: s.pending() == 0))
        self.assertEqual(sorted(self.store.inspections), [f"2026100714300512{i}" for i in range(3)])

    def test_no_duplicate_on_retry(self):  # 寫入後、刪除暫存前當機
        s = self.sink()
        s.write(result())
        self.assertTrue(wait(lambda: s.pending() == 0))
        (self.dir / "20261007143005123.json").write_text(json.dumps(to_record(result(), "ST01")))
        s._wake.set()
        self.assertTrue(wait(lambda: s.pending() == 0))
        self.assertEqual(len(self.store.inspections), 1)

    def test_left_in_buffer_survives_restart(self):  # DAT-05：結束時寫不進去，下次啟動補寫
        self.store.available = False
        s = ResultSink(self.store, "ST01", self.dir, retry=0.1).start()
        s.write(result())
        s.close(0.3)
        self.assertEqual(s.pending(), 1)
        self.store.available = True
        s2 = self.sink()
        self.assertTrue(wait(lambda: s2.pending() == 0))
        self.assertIn("20261007143005123", self.store.inspections)

    def test_count_includes_buffer(self):
        self.store.available = False
        s = self.sink()
        s.write(result())
        self.store.available = True
        self.assertTrue(wait(lambda: s.pending() == 0))
        self.assertEqual(s.count(T.date()), 1)


from test_store import _dev_env  # noqa: E402


@unittest.skipIf(_dev_env() is None, "開發用 MySQL 未啟動（./scripts/dev-mysql.sh start）")
class MySQLWriteTest(unittest.TestCase):
    def setUp(self):
        env, root = _dev_env()
        with root.cursor() as cur:
            cur.execute("CREATE DATABASE IF NOT EXISTS flatness_test")
            cur.execute("DROP TABLE IF EXISTS flatness_test.inspection_point")
            cur.execute("DROP TABLE IF EXISTS flatness_test.inspection")
            cur.execute("CREATE TABLE flatness_test.inspection LIKE flatness.inspection")
            cur.execute("CREATE TABLE flatness_test.inspection_point LIKE flatness.inspection_point")
            cur.execute("GRANT SELECT, INSERT, UPDATE ON flatness_test.* TO 'flatness_app'@'localhost'")
        self.root = root
        self.addCleanup(root.close)
        self.store = MySQLStore(database="flatness_test", user=env["DB_USER"], password=env["DB_PASS"],
                                unix_socket=env["DB_SOCKET"])

    def test_write_inspection(self):  # DAT-02、DAT-03、DAT-06
        rec = to_record(result(), "ST01")
        head = dict(rec["head"], measured_at=T)
        self.assertTrue(self.store.write_inspection(head, rec["points"]))
        self.assertFalse(self.store.write_inspection(head, rec["points"]))  # 不重複
        with self.root.cursor() as cur:
            cur.execute("SELECT serial, station_id, measured_at, judgment, reread_count, written_at >= measured_at"
                        " FROM flatness_test.inspection")
            self.assertEqual(cur.fetchall(), (("20261007143005123", "ST01", T, "FAIL", 1, 1),))
            cur.execute("SELECT probe_id, device_name, probe_description, measured_value, standard_value,"
                        " lower_limit, upper_limit, judgment, raw_response, error_text, device_mac"
                        " FROM flatness_test.inspection_point ORDER BY probe_id")
            rows = cur.fetchall()
        self.assertEqual(rows[0], (1, "前排", "左", Decimal("-0.297100"), Decimal("12.500000"),
                                   Decimal("12.450000"), Decimal("12.550000"), "LOW", "-000002971", None,
                                   "00:01:FC:DE:3A:75"))
        self.assertEqual(rows[2][3:], (None, None, None, None, "ERROR", None, "放大器未連接",
                                       "00:01:FC:DE:3A:75"))
        self.assertEqual(self.store.count_inspections(T.date()), 1)
        (got,) = self.store.read_inspections(T.date())                      # EXP-03
        self.assertEqual(got["head"], dict(head, measured_at=T))
        self.assertEqual(got["points"], [dict(p, zero_offset=None) for p in rec["points"]])


if __name__ == "__main__":
    unittest.main()
