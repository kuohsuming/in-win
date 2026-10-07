"""lan_device 讀寫（DSC-01、DSC-05、DSC-12、DSC-13）。

同一組測試跑在 MemoryStore 與 MySQLStore；MySQL 測試需先執行 ./scripts/dev-mysql.sh start，
否則略過。MySQL 測試使用獨立的 flatness_test 資料庫，不動開發用的 flatness。
"""

import unittest
from datetime import timedelta

from helpers import ROOT, T0, by_mac, sample_devices

from flatness import lan
from flatness.lan import LIVE, RETIRED, UNCLASSIFIED
from flatness.store import MemoryStore, MySQLStore, SeenEvent, StoreError, read_env

MAC = "00:01:FC:DE:3A:99"


class StoreContract:
    def make_store(self, devices=()):
        raise NotImplementedError

    def test_new_mac_creates_unclassified_row(self):  # DSC-01-G1
        s = self.make_store()
        s.record([SeenEvent(MAC, "BOOTP", T0), SeenEvent(MAC, "BOOTP", T0 + timedelta(seconds=1))])
        (d,) = s.load()
        self.assertEqual((d.mac, d.status, d.seen_count, d.last_request), (MAC, UNCLASSIFIED, 2, "BOOTP"))
        self.assertEqual((d.first_seen, d.last_seen), (T0, T0 + timedelta(seconds=1)))

    def test_existing_row_counts_and_keeps_settings(self):
        s = self.make_store(sample_devices())
        front = "00:01:FC:DE:3A:75"
        s.record([SeenEvent(front, "BOOTP", T0 + timedelta(hours=1))])
        d = by_mac(s.load())[front]
        self.assertEqual((d.status, d.seen_count, d.config["key"]), (LIVE, 4, "row-1"))
        self.assertEqual(d.last_seen, T0 + timedelta(hours=1))
        self.assertEqual(len(s.load()), 6)  # 每個 MAC 只有一筆（DSC-01-A2）

    def test_hostname_info_event(self):
        s = self.make_store()
        s.record([SeenEvent(MAC, "DHCP", T0), SeenEvent(MAC, "DHCP", T0, hostname="eng-laptop",
                                                        vendor_class="MSFT 5.0", count=0)])
        (d,) = s.load()
        self.assertEqual((d.seen_count, d.hostname, d.vendor_class), (1, "eng-laptop", "MSFT 5.0"))

    def test_hidden_unclassified_reappears(self):  # DSC-13
        s = self.make_store(sample_devices())
        s.set_hidden("00:01:FC:12:39:A0", True)
        s.set_hidden("3C:52:82:11:22:33", True)
        d = by_mac(s.load())
        self.assertTrue(d["00:01:FC:12:39:A0"].hidden and d["00:01:FC:12:39:A0"].hidden_at)
        s.record([SeenEvent("00:01:FC:12:39:A0", "BOOTP", T0), SeenEvent("3C:52:82:11:22:33", "DHCP", T0)])
        d = by_mac(s.load())
        self.assertFalse(d["00:01:FC:12:39:A0"].hidden)
        self.assertTrue(d["3C:52:82:11:22:33"].hidden)  # 其他狀態維持隱藏

    def test_save_writes_only_changed_rows_and_json(self):  # DSC-12
        s = self.make_store(sample_devices())
        old = s.load()
        new = [d.copy() for d in old]
        m = by_mac(new)["00:01:FC:DE:3A:76"]
        m.config["name"] = "中段"
        m.config["probes"].append({"id": 5, "description": "中央"})
        m.config["max_probes"] = 5
        lan.move(new, m.mac, -1)
        m.config["key"], by_mac(new)["00:01:FC:DE:3A:75"].config["key"] = "row-1", "row-2"
        with s.transaction() as tx:
            n = tx.save(old, new)
        self.assertEqual(n, 6)  # 第一次調整順序時全部設備重新編號（DSC-17）
        back = by_mac(s.load())["00:01:FC:DE:3A:76"]
        self.assertEqual(back.config, m.config)
        self.assertEqual([d["name"] for d in lan.definition_from(s.load())["dl_en1"]], ["中段", "前排", "後排"])

    def test_transaction_rolls_back(self):
        s = self.make_store(sample_devices())
        old = s.load()
        new = [d.copy() for d in old]
        lan.set_status(new, "00:01:FC:DE:3A:76", RETIRED, None)
        with self.assertRaises(RuntimeError):
            with s.transaction() as tx:
                tx.save(old, new)
                raise RuntimeError("dnsmasq 重新啟動失敗")
        self.assertEqual(by_mac(s.load())["00:01:FC:DE:3A:76"].status, LIVE)

    def test_save_inserts_imported_device(self):
        s = self.make_store(sample_devices())
        old = s.load()
        new = [d.copy() for d in old] + [lan.LanDevice(mac=MAC, status=LIVE, ipv4="192.168.10.40",
                                                       config={"key": "x", "name": "x", "max_probes": 1,
                                                               "probes": [{"id": 1, "description": "左"}]},
                                                       sort_order=7)]
        with s.transaction() as tx:
            tx.save(old, new)
        d = by_mac(s.load())[MAC]
        self.assertEqual((d.status, d.first_seen, d.seen_count), (LIVE, None, 0))


class MemoryStoreTest(StoreContract, unittest.TestCase):
    def make_store(self, devices=()):
        return MemoryStore(devices)

    def test_unavailable(self):
        s = MemoryStore()
        s.available = False
        with self.assertRaises(StoreError):
            s.load()


def _dev_env():
    path = ROOT / ".dev" / "db.env"
    if not path.exists():
        return None
    env = read_env(path)
    try:
        import pymysql
        conn = pymysql.connect(user="root", unix_socket=env["DB_SOCKET"], autocommit=True, connect_timeout=1)
    except Exception:
        return None
    return env, conn


@unittest.skipIf(_dev_env() is None, "開發用 MySQL 未啟動（./scripts/dev-mysql.sh start）")
class MySQLStoreTest(StoreContract, unittest.TestCase):
    def make_store(self, devices=()):
        env, root = _dev_env()
        with root.cursor() as cur:
            cur.execute("CREATE DATABASE IF NOT EXISTS flatness_test")
            cur.execute("DROP TABLE IF EXISTS flatness_test.lan_device")
            cur.execute("CREATE TABLE flatness_test.lan_device LIKE flatness.lan_device")
            cur.execute("GRANT SELECT, INSERT, UPDATE ON flatness_test.* TO 'flatness_app'@'localhost'")
        root.close()
        store = MySQLStore(database="flatness_test", user=env["DB_USER"], password=env["DB_PASS"],
                           unix_socket=env["DB_SOCKET"])
        if devices:
            with store.transaction() as tx:
                tx.save([], list(devices))
            store.record([SeenEvent(d.mac, d.last_request, d.first_seen, d.hostname)
                          for d in devices if d.first_seen])
            # 讓 seen_count、last_seen 與範例相同
            env, root = _dev_env()
            with root.cursor() as cur:
                for d in devices:
                    if d.first_seen:
                        cur.execute("UPDATE flatness_test.lan_device SET seen_count=%s, last_seen=%s,"
                                    " first_seen=%s WHERE mac=%s",
                                    (d.seen_count, d.last_seen, d.first_seen, d.mac))
            root.close()
        return store

    def test_unreachable(self):
        s = MySQLStore(database="x", user="x", password="x", unix_socket="/nonexistent.sock", connect_timeout=1)
        with self.assertRaises(StoreError):
            s.load()

    def test_app_account_cannot_delete(self):
        import pymysql
        env, _ = _dev_env()
        conn = pymysql.connect(user=env["DB_USER"], password=env["DB_PASS"], unix_socket=env["DB_SOCKET"],
                               database="flatness")
        with self.assertRaises(pymysql.MySQLError):
            with conn.cursor() as cur:
                cur.execute("DELETE FROM lan_device")
        conn.close()


if __name__ == "__main__":
    unittest.main()
