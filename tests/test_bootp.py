"""flatness.bootp：定義檔驗證（DEF-02）與 BOOTP 主機對應（DEF-03）。"""

import copy
import ipaddress
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from flatness import bootp  # noqa: E402

NET = ipaddress.IPv4Interface("192.168.10.1/24")
SAMPLE = json.loads((ROOT / "installer" / "dl-en1.json").read_text(encoding="utf-8"))


def device(key, mac, ip, **extra):
    d = {"key": key, "name": key, "mac": mac, "ipv4": ip, "max_probes": 4,
         "probes": [{"id": 1, "description": "左"}]}
    d.update(extra)
    return d


def where(exc):
    return {w for w, _ in exc.errors}


class ValidateTest(unittest.TestCase):
    def test_installer_sample_is_valid(self):
        self.assertEqual(len(bootp.validate(SAMPLE, NET)), len(SAMPLE["dl_en1"]))

    def test_spec_example_is_valid(self):
        # 需求規格書 3.7.2 範例：中排只安裝 ID 1 與 ID 4
        spec = {"version": 1, "dl_en1": [
            device("row-1", "00:01:FC:12:34:56", "192.168.10.11", port=64000),
            device("row-2", "00:01:FC:12:34:57", "192.168.10.12",
                   probes=[{"id": 1, "description": "左"}, {"id": 4, "description": "右"}]),
        ]}
        self.assertEqual(len(bootp.validate(spec, NET)), 2)

    def test_reports_all_errors_with_locations(self):
        bad = {"version": 1, "dl_en1": [
            device("row-1", "00:01:FC:00:00:01", "192.168.10.11"),
            device("row-3", "00:01:fc:00:00:01", "192.168.20.5",          # 重複 MAC（不分大小寫）、網段外
                   probes=[{"id": 5, "description": "右"}]),             # id 超過 max_probes
        ]}
        with self.assertRaises(bootp.DefinitionError) as cm:
            bootp.validate(bad, NET)
        self.assertEqual(where(cm.exception),
                         {"dl_en1[1].mac", "dl_en1[1].ipv4", "dl_en1[1].probes[0].id"})

    def test_rejects_network_broadcast_and_pc_address(self):
        for ip in ("192.168.10.0", "192.168.10.255", "192.168.10.1"):
            with self.subTest(ip=ip), self.assertRaises(bootp.DefinitionError):
                bootp.validate({"version": 1, "dl_en1": [device("a", "00:01:FC:00:00:01", ip)]}, NET)

    def test_rejects_duplicate_probe_id_and_too_many_probes(self):
        d = device("a", "00:01:FC:00:00:01", "192.168.10.11", max_probes=1,
                   probes=[{"id": 1, "description": "左"}, {"id": 1, "description": "右"}])
        with self.assertRaises(bootp.DefinitionError) as cm:
            bootp.validate({"version": 1, "dl_en1": [d]}, NET)
        self.assertIn("dl_en1[0].probes", where(cm.exception))
        self.assertIn("dl_en1[0].probes[1].id", where(cm.exception))

    def test_rejects_bad_key_mac_and_unknown_field(self):
        d = device("Front", "00-01-FC-00-00-01", "192.168.10.11", color="red")
        with self.assertRaises(bootp.DefinitionError) as cm:
            bootp.validate({"version": 1, "dl_en1": [d]}, NET)
        self.assertEqual(where(cm.exception), {"dl_en1[0].key", "dl_en1[0].mac", "dl_en1[0].color"})

    def test_rejects_device_count_out_of_range(self):
        for n in (0, 9):
            devs = [device(f"d{i}", f"00:01:FC:00:00:{i:02X}", f"192.168.10.{i + 10}") for i in range(n)]
            with self.subTest(n=n), self.assertRaises(bootp.DefinitionError):
                bootp.validate({"version": 1, "dl_en1": devs}, NET)

    def test_json_syntax_error_has_line_and_column(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp, "bad.json")
            p.write_text('{\n  "version": 1,\n  "dl_en1": [,]\n}', encoding="utf-8")
            with self.assertRaises(bootp.DefinitionError) as cm:
                bootp.load(p, NET)
            self.assertIn("第 3 行", cm.exception.errors[0][0])


class HostsTest(unittest.TestCase):
    def test_render_one_line_per_device(self):
        lines = bootp.render_hosts(SAMPLE["dl_en1"]).splitlines()
        self.assertTrue(lines[0].startswith("#"))
        self.assertEqual(lines[1], "00:01:fc:de:3a:75,192.168.10.11,row-1")

    def test_backup_keeps_20(self):
        with tempfile.TemporaryDirectory() as tmp:
            hosts = Path(tmp, "dl-en1.hosts")
            for i in range(23):
                bootp.backup_file(hosts)
                bootp.atomic_write(hosts, f"{i}\n")
            self.assertEqual(hosts.read_text(), "22\n")
            self.assertEqual(len(list(Path(tmp, "backup").iterdir())), 20)


if __name__ == "__main__":
    unittest.main()
