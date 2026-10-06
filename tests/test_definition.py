"""flatness.definition：差異比對與套用／還原（UPL-05～UPL-08、EDT-03）。"""

import copy
import ipaddress
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

from flatness import bootp, definition  # noqa: E402

NET = ipaddress.IPv4Interface("192.168.10.1/24")


def three_rows():
    def dev(key, name, last):
        return {"key": key, "name": name, "mac": f"00:01:FC:12:34:{last:02X}",
                "ipv4": f"192.168.10.{last - 0x56 + 11}", "max_probes": 4,
                "probes": [{"id": i + 1, "description": d} for i, d in enumerate(["左", "左中", "右中", "右"])]}
    return {"version": 1, "dl_en1": [dev("front", "前排", 0x56), dev("middle", "中排", 0x57),
                                     dev("rear", "後排", 0x58)]}


class DiffTest(unittest.TestCase):
    def setUp(self):
        self.old = three_rows()["dl_en1"]
        self.new = copy.deepcopy(self.old)

    def test_no_change(self):
        self.assertTrue(definition.diff(self.old, self.new).empty)

    def test_mac_and_ip_change_is_important_and_needs_power_cycle(self):
        self.new[1]["mac"] = "00:01:FC:DE:3A:75"
        self.new[1]["ipv4"] = "192.168.10.20"
        d = definition.diff(self.old, self.new)
        (dev, changes), = d.changed
        self.assertEqual(dev["key"], "middle")
        self.assertTrue(all(c.important for c in changes))
        self.assertEqual([x["key"] for x in d.power_cycle], ["middle"])

    def test_mac_case_only_is_not_a_change(self):
        self.new[0]["mac"] = self.new[0]["mac"].lower()
        self.assertTrue(definition.diff(self.old, self.new).empty)

    def test_add_remove_and_removed_points(self):
        removed = self.new.pop(2)
        self.new[0]["probes"] = self.new[0]["probes"][:2]
        self.new.append({"key": "extra", "name": "加排", "mac": "00:01:FC:00:00:09",
                         "ipv4": "192.168.10.30", "max_probes": 1,
                         "probes": [{"id": 1, "description": "中"}]})
        d = definition.diff(self.old, self.new)
        self.assertEqual([x["key"] for x in d.added], ["extra"])
        self.assertEqual([x["key"] for x in d.removed], [removed["key"]])
        self.assertIn("前排 右中", d.removed_points)
        self.assertIn("後排 左", d.removed_points)
        self.assertEqual([x["key"] for x in d.power_cycle], ["extra"])

    def test_reorder_and_port_default(self):
        self.new.reverse()
        self.new[0]["port"] = 64000  # 明確填寫預設值不算變更
        d = definition.diff(self.old, self.new)
        self.assertTrue(d.reordered)
        self.assertEqual(d.changed, [])


class ApplyTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.def_path = Path(self.tmp.name, "etc", "dl-en1.json")
        self.hosts = Path(self.tmp.name, "bootp", "dl-en1.hosts")
        self.def_path.parent.mkdir()
        self.original = three_rows()
        self.def_path.write_text(definition.dumps(self.original), encoding="utf-8")
        bootp.apply(self.original["dl_en1"], self.hosts, restart_cmd=None)

    def tearDown(self):
        self.tmp.cleanup()

    def test_apply_writes_definition_and_hosts(self):
        new = copy.deepcopy(self.original)
        new["dl_en1"][0]["ipv4"] = "192.168.10.21"
        d = definition.apply(new, self.def_path, self.hosts, NET, restart_cmd=None)
        self.assertEqual(json.loads(self.def_path.read_text(encoding="utf-8")), new)
        self.assertIn("00:01:fc:12:34:56,192.168.10.21,front", self.hosts.read_text())
        self.assertEqual([x["key"] for x in d.power_cycle], ["front"])
        self.assertEqual(len(list(self.def_path.parent.joinpath("backup").iterdir())), 1)

    def test_restart_failure_restores_both_files(self):
        before_def = self.def_path.read_text(encoding="utf-8")
        before_hosts = self.hosts.read_text()
        new = copy.deepcopy(self.original)
        new["dl_en1"][0]["ipv4"] = "192.168.10.21"
        with self.assertRaises(RuntimeError):
            definition.apply(new, self.def_path, self.hosts, NET, restart_cmd=["false"])
        self.assertEqual(self.def_path.read_text(encoding="utf-8"), before_def)
        self.assertEqual(self.hosts.read_text(), before_hosts)

    def test_invalid_definition_writes_nothing(self):
        before = self.def_path.read_text(encoding="utf-8")
        new = copy.deepcopy(self.original)
        new["dl_en1"][1]["mac"] = new["dl_en1"][0]["mac"]
        with self.assertRaises(bootp.DefinitionError):
            definition.apply(new, self.def_path, self.hosts, NET, restart_cmd=None)
        self.assertEqual(self.def_path.read_text(encoding="utf-8"), before)

    def test_schema_matches_spec_example(self):
        # 正式 JSON Schema 與 bootp 規則對規格範例的判斷一致
        self.assertEqual(definition.validate(self.original, NET), [])


if __name__ == "__main__":
    unittest.main()
