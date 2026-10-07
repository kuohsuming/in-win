"""資料庫 → 檔案（DSC-06、DSC-11）與設備設定套用／還原（DSC-03、DSC-12、DSC-14、UPL-08）。"""

import ipaddress
import json
import tempfile
import unittest
from pathlib import Path

from helpers import NET, by_mac, sample_devices

from flatness import lan, sync
from flatness.lan import RETIRED
from flatness.store import MemoryStore


class SyncTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.files = sync.Files(base / "etc" / "dl-en1.json", base / "bootp" / "dl-en1.hosts")
        self.store = MemoryStore(sample_devices())

    def tearDown(self):
        self.tmp.cleanup()

    def defn(self):
        return json.loads(self.files.def_path.read_text(encoding="utf-8"))

    def test_startup_generates_both_files(self):  # DSC-06-G1
        r = sync.startup(self.store, self.files, NET)
        self.assertTrue(r.changed and r.db_ok and r.problem is None)
        self.assertEqual([d["key"] for d in self.defn()["dl_en1"]], ["row-1", "row-2", "row-3"])
        hosts = [l for l in self.files.hosts_path.read_text().splitlines() if not l.startswith("#")]
        self.assertEqual(len(hosts), 4)

    def test_startup_unchanged_does_not_rewrite(self):  # DSC-06-A4
        sync.startup(self.store, self.files, NET)
        mtime = self.files.def_path.stat().st_mtime_ns
        r = sync.startup(self.store, self.files, NET)
        self.assertFalse(r.changed)
        self.assertEqual(self.files.def_path.stat().st_mtime_ns, mtime)
        self.assertFalse((self.files.def_path.parent / "backup").exists())

    def test_startup_db_down_keeps_files(self):  # DSC-06-A2
        sync.startup(self.store, self.files, NET)
        before = self.files.hosts_path.read_text()
        self.store.available = False
        r = sync.startup(self.store, self.files, NET)
        self.assertEqual(r.problem, "無法讀取資料庫，使用上次的設定")
        self.assertFalse(r.db_ok)
        self.assertEqual(len(r.definition["dl_en1"]), 3)
        self.assertEqual(self.files.hosts_path.read_text(), before)

    def test_startup_invalid_db_keeps_files(self):  # DSC-06-A3
        sync.startup(self.store, self.files, NET)
        before = self.files.def_path.read_text()
        devs = self.store.load()
        with self.store.transaction() as tx:
            new = [d.copy() for d in devs]
            by_mac(new)["00:01:FC:DE:3A:76"].ipv4 = "192.168.10.11"
            tx.save(devs, new)
        r = sync.startup(self.store, self.files, NET)
        self.assertIn("設備設定有錯誤", r.problem)
        self.assertEqual(self.files.def_path.read_text(), before)

    def test_startup_net_changed_lists_devices(self):  # DSC-11-G1
        net20 = ipaddress.IPv4Interface("192.168.20.1/24")
        r = sync.startup(self.store, self.files, net20)
        self.assertIn("4 台設備的 IP 不在設備網段 192.168.20.0/24", r.problem)
        self.assertIn("前排", r.problem)
        self.assertFalse(self.files.def_path.exists())

    def test_apply_writes_db_and_files_and_restarts(self):  # DSC-03-G1
        sync.startup(self.store, self.files, NET)
        old = self.store.load()
        new = [d.copy() for d in old]
        lan.set_status(new, "00:01:FC:DE:3A:76", RETIRED, NET)
        restarts = []
        r = sync.apply(self.store, self.files, NET, old, new, restart=lambda: restarts.append(1))
        self.assertEqual(restarts, [1])
        self.assertTrue(r.restarted)
        self.assertEqual(by_mac(self.store.load())["00:01:FC:DE:3A:76"].status, RETIRED)
        self.assertEqual([d["key"] for d in self.defn()["dl_en1"]], ["row-1", "row-3"])
        self.assertNotIn("3a:76", self.files.hosts_path.read_text())
        self.assertEqual(len(sync.backups(self.files)), 1)

    def test_apply_name_change_does_not_restart_dnsmasq(self):
        sync.startup(self.store, self.files, NET)
        old = self.store.load()
        new = [d.copy() for d in old]
        by_mac(new)["00:01:FC:DE:3A:76"].config["name"] = "中段"
        restarts = []
        r = sync.apply(self.store, self.files, NET, old, new, restart=lambda: restarts.append(1))
        self.assertEqual((restarts, r.restarted), ([], False))
        self.assertEqual(self.defn()["dl_en1"][1]["name"], "中段")

    def test_apply_restart_failure_restores_everything(self):  # UPL-08、DSC-14-A3
        sync.startup(self.store, self.files, NET)
        before = (self.files.def_path.read_text(), self.files.hosts_path.read_text())
        old = self.store.load()
        new = [d.copy() for d in old]
        lan.replace(new, "00:01:FC:DE:3A:75", "00:01:FC:12:39:A0")
        calls = []

        def restart():
            calls.append(self.files.hosts_path.read_text())
            if len(calls) == 1:
                raise RuntimeError("dnsmasq 啟動失敗")
        with self.assertRaises(RuntimeError):
            sync.apply(self.store, self.files, NET, old, new, restart=restart)
        self.assertEqual((self.files.def_path.read_text(), self.files.hosts_path.read_text()), before)
        self.assertEqual(calls[1], before[1])  # 以還原後的對應再啟動一次
        self.assertEqual(by_mac(self.store.load())["00:01:FC:DE:3A:75"].status, lan.LIVE)

    def test_apply_invalid_writes_nothing(self):
        sync.startup(self.store, self.files, NET)
        before = self.files.def_path.read_text()
        old = self.store.load()
        new = [d.copy() for d in old]
        by_mac(new)["00:01:FC:DE:3A:76"].config["key"] = "row-1"
        with self.assertRaises(sync.SyncError):
            sync.apply(self.store, self.files, NET, old, new)
        self.assertEqual(self.files.def_path.read_text(), before)
        self.assertEqual(by_mac(self.store.load())["00:01:FC:DE:3A:76"].config["key"], "row-2")

    def test_read_definition_file_rules(self):  # UPL-03、UPL-04
        base = Path(self.tmp.name)
        txt = base / "a.txt"
        txt.write_text("{}")
        with self.assertRaises(Exception) as ctx:
            sync.read_definition_file(txt, NET)
        self.assertIn(".json", str(ctx.exception))
        big = base / "big.json"
        big.write_text(" " * 70000)
        with self.assertRaises(Exception):
            sync.read_definition_file(big, NET)
        good = base / "good.json"
        good.write_text(json.dumps(lan.definition_from(sample_devices())), encoding="utf-8")
        self.assertEqual(len(sync.read_definition_file(good, NET)["dl_en1"]), 3)


if __name__ == "__main__":
    unittest.main()
