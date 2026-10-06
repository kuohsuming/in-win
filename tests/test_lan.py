"""設備規則（lan.py）：DSC-02～DSC-04、DSC-06、DSC-08、DSC-09、DSC-11、DSC-14、DSC-15。"""

import ipaddress
import unittest

from helpers import NET, by_mac, dl, sample_devices

from flatness import lan
from flatness.lan import LIVE, MAINT, OTHER, RETIRED, UNCLASSIFIED, LanDevice


class OutputTest(unittest.TestCase):
    def test_definition_only_live_in_screen_order(self):
        devs = sample_devices()
        by_mac(devs)["00:01:FC:DE:3A:75"].sort_order = 5  # 前排移到最後
        defn = lan.definition_from(devs)
        self.assertEqual([d["key"] for d in defn["dl_en1"]], ["middle", "rear", "front"])
        self.assertEqual(defn["dl_en1"][0]["mac"], "00:01:FC:DE:3A:76")
        self.assertNotIn("port", defn["dl_en1"][0])

    def test_hosts_live_maint_and_other_with_ip(self):
        devs = sample_devices()
        by_mac(devs)["00:01:FC:DE:3A:76"].status = MAINT
        text = lan.render_hosts(devs)
        lines = [l for l in text.splitlines() if not l.startswith("#")]
        self.assertEqual(lines, ["00:01:fc:de:3a:75,192.168.10.11,front",
                                 "00:01:fc:de:3a:77,192.168.10.13,rear",
                                 "00:01:fc:de:3a:76,192.168.10.12,middle",
                                 "3c:52:82:11:22:33,192.168.10.200"])
        self.assertNotIn("3a:70", text)  # 已停用不配發（DSC-06-A1）

    def test_other_without_ip_not_assigned(self):
        devs = sample_devices()
        by_mac(devs)["3C:52:82:11:22:33"].ipv4 = None
        self.assertNotIn("3c:52:82", lan.render_hosts(devs))

    def test_list_order(self):
        order = [d.status for d in lan.list_order(sample_devices())]
        self.assertEqual(order, [UNCLASSIFIED, LIVE, LIVE, LIVE, OTHER, RETIRED])

    def test_normalize_mac(self):
        self.assertEqual(lan.normalize_mac("00-01-fc-de-3a-75"), "00:01:FC:DE:3A:75")
        with self.assertRaises(ValueError):
            lan.normalize_mac("00:01:fc")


class ValidateTest(unittest.TestCase):
    def test_sample_passes(self):
        self.assertEqual(lan.validate(sample_devices(), NET), [])

    def issues(self, devs):
        return [(i.mac, i.field, i.message) for i in lan.validate(devs, NET)]

    def test_ip_taken_by_other_device_names_occupant(self):
        devs = sample_devices()
        by_mac(devs)["00:01:FC:DE:3A:77"].ipv4 = "192.168.10.200"
        msgs = [i.text() for i in lan.validate(devs, NET)]
        self.assertTrue(any("已由 其他設備 3C:52:82:11:22:33（eng-laptop）使用" in m for m in msgs), msgs)

    def test_retired_does_not_occupy_key_name_ip(self):  # DSC-09
        devs = sample_devices()
        new = by_mac(devs)["00:01:FC:12:39:A0"]
        new.status, new.ipv4, new.sort_order = LIVE, "192.168.10.14", 4
        new.config = {"key": "old", "name": "舊機", "max_probes": 4, "probes": [{"id": 1, "description": "左"}]}
        self.assertEqual(lan.validate(devs, NET), [])
        by_mac(devs)["00:01:FC:DE:3A:70"].status = LIVE  # 舊機改回使用中 → 衝突
        fields = {f for _, f, _ in self.issues(devs)}
        self.assertTrue({"key", "name", "ipv4"} <= fields)

    def test_maint_keeps_key_and_ip(self):  # DSC-15-A2
        devs = sample_devices()
        by_mac(devs)["00:01:FC:DE:3A:76"].status = MAINT
        other = by_mac(devs)["3C:52:82:11:22:33"]
        other.ipv4 = "192.168.10.12"
        self.assertIn(("3C:52:82:11:22:33", "ipv4"), {(m, f) for m, f, _ in self.issues(devs)})

    def test_live_count(self):
        devs = [d for d in sample_devices() if d.status != LIVE]
        self.assertIn((None, "status"), {(m, f) for m, f, _ in self.issues(devs)})

    def test_field_rules(self):
        devs = sample_devices()
        d = by_mac(devs)["00:01:FC:DE:3A:75"]
        d.config.update(key="Front", name="", port=70000, max_probes=2)
        d.config["probes"].append({"id": 3, "description": "左"})
        fields = [f for m, f, _ in self.issues(devs) if m == d.mac]
        for f in ("key", "name", "port", "probes"):
            self.assertIn(f, fields)

    def test_ip_rules(self):
        devs = sample_devices()
        for ip, word in (("192.168.11.5", "網段"), ("192.168.10.255", "廣播"), ("192.168.10.1", "量測 PC"),
                         ("abc", "IPv4")):
            by_mac(devs)["00:01:FC:DE:3A:75"].ipv4 = ip
            msgs = [msg for m, f, msg in self.issues(devs) if f == "ipv4"]
            self.assertTrue(any(word in m for m in msgs), (ip, msgs))

    def test_out_of_net(self):  # DSC-11
        net20 = ipaddress.IPv4Interface("192.168.20.1/24")
        names = [d.label() for d in lan.out_of_net(sample_devices(), net20)]
        self.assertEqual(sorted(names), sorted(["前排", "中排", "後排", "eng-laptop"]))


class DefaultIpTest(unittest.TestCase):
    def test_smallest_free_in_range(self):  # DSC-08-G1
        devs = sample_devices()
        self.assertEqual(lan.default_ip(devs, "dl_en1", NET), "192.168.10.14")  # .14 已停用 → 不佔用
        self.assertEqual(lan.default_ip(devs, "other", NET), "192.168.10.100")

    def test_two_new_devices_get_different_ips(self):  # DSC-08-A5
        devs = sample_devices()
        a = by_mac(devs)["00:01:FC:12:39:A0"]
        lan.set_status(devs, a.mac, LIVE, NET)
        devs.append(LanDevice(mac="00:01:FC:12:39:A1"))
        b = lan.set_status(devs, "00:01:FC:12:39:A1", LIVE, NET)
        self.assertNotEqual(a.ipv4, b.ipv4)

    def test_range_full_falls_back(self):
        devs = [LanDevice(mac=f"00:01:FC:00:00:{i:02X}", status=OTHER, ipv4=f"192.168.10.{i}")
                for i in range(100, 200)]
        self.assertEqual(lan.default_ip(devs, "other", NET), "192.168.10.2")

    def test_small_net(self):
        net = ipaddress.IPv4Interface("10.0.0.1/29")  # 主機位址只有 .1～.6
        self.assertEqual(lan.default_ip([], "dl_en1", net), "10.0.0.2")


class OperationTest(unittest.TestCase):
    def test_classify_unknown_as_live(self):  # DSC-03-G1
        devs = sample_devices()
        d = lan.set_status(devs, "00:01:FC:12:39:A0", LIVE, NET)
        self.assertEqual(d.config["max_probes"], 4)
        self.assertEqual(len(d.config["probes"]), 4)
        self.assertEqual(d.ipv4, "192.168.10.14")
        self.assertEqual(d.sort_order, 10)

    def test_retire_keeps_config_and_restore(self):  # DSC-12-A5、DSC-09
        devs = sample_devices()
        lan.set_status(devs, "00:01:FC:DE:3A:76", RETIRED, NET)
        d = by_mac(devs)["00:01:FC:DE:3A:76"]
        self.assertEqual(d.config["key"], "middle")
        self.assertNotIn("middle", lan.render_hosts(devs))
        lan.set_status(devs, d.mac, LIVE, NET)
        self.assertEqual((d.config["key"], d.ipv4, d.sort_order), ("middle", "192.168.10.12", 2))

    def test_maint_and_back_keeps_position(self):  # DSC-15-G1
        devs = sample_devices()
        lan.set_status(devs, "00:01:FC:DE:3A:76", MAINT, NET)
        self.assertEqual([d["key"] for d in lan.definition_from(devs)["dl_en1"]], ["front", "rear"])
        lan.set_status(devs, "00:01:FC:DE:3A:76", LIVE, NET)
        self.assertEqual([d["key"] for d in lan.definition_from(devs)["dl_en1"]], ["front", "middle", "rear"])

    def test_switch_to_other_and_back_remembers_config(self):
        devs = sample_devices()
        memo = {}
        lan.set_status(devs, "00:01:FC:DE:3A:76", OTHER, NET, remembered=memo)
        self.assertIsNone(by_mac(devs)["00:01:FC:DE:3A:76"].config)
        lan.set_status(devs, "00:01:FC:DE:3A:76", LIVE, NET, remembered=memo)
        self.assertEqual(by_mac(devs)["00:01:FC:DE:3A:76"].config["key"], "middle")

    def test_set_live_unhides(self):
        devs = sample_devices()
        d = by_mac(devs)["00:01:FC:12:39:A0"]
        d.hidden = True
        lan.set_status(devs, d.mac, LIVE, NET)
        self.assertFalse(d.hidden)

    def test_replace(self):  # DSC-14-G1
        devs = sample_devices()
        old = by_mac(devs)["00:01:FC:DE:3A:75"]
        cands = lan.replace_candidates(devs, old.mac)
        self.assertEqual(cands[0].mac, "00:01:FC:12:39:A0")  # KEYENCE、最近出現
        new = lan.replace(devs, old.mac, "00:01:FC:12:39:A0")
        self.assertEqual((new.status, new.ipv4, new.sort_order, new.config), (LIVE, "192.168.10.11", 1, old.config))
        self.assertEqual(old.status, RETIRED)
        self.assertEqual(lan.validate(devs, NET), [])
        self.assertEqual(lan.definition_from(devs)["dl_en1"][0]["mac"], "00:01:FC:12:39:A0")
        with self.assertRaises(ValueError):
            lan.replace(devs, new.mac, by_mac(devs)["00:01:FC:DE:3A:76"].mac)  # 新機不可為使用中

    def test_move(self):
        devs = sample_devices()
        self.assertTrue(lan.move(devs, "00:01:FC:DE:3A:76", -1))
        self.assertEqual([d["key"] for d in lan.definition_from(devs)["dl_en1"]], ["middle", "front", "rear"])
        self.assertFalse(lan.move(devs, "00:01:FC:DE:3A:76", -1))

    def test_import(self):  # DEF-07
        devs = sample_devices()
        defn = {"version": 1, "dl_en1": [
            {"key": "front", "name": "前排", "mac": "00:01:fc:de:3a:75", "ipv4": "192.168.10.11",
             "max_probes": 4, "probes": [{"id": 1, "description": "左"}]},
            {"key": "new", "name": "新排", "mac": "00:01:FC:99:99:99", "ipv4": "192.168.10.20",
             "max_probes": 2, "probes": [{"id": 1, "description": "左"}]}]}
        out = by_mac(lan.import_definition(devs, defn))
        self.assertEqual(out["00:01:FC:DE:3A:76"].status, RETIRED)
        self.assertEqual(out["00:01:FC:99:99:99"].status, LIVE)
        self.assertIsNone(out["00:01:FC:99:99:99"].first_seen)
        self.assertEqual(lan.definition_from(out.values())["dl_en1"][0]["probes"], [{"id": 1, "description": "左"}])
        self.assertEqual(by_mac(devs)["00:01:FC:DE:3A:76"].status, LIVE)  # 原清單不變


class DiffTest(unittest.TestCase):
    def test_no_change(self):
        devs = sample_devices()
        self.assertTrue(lan.diff(devs, [d.copy() for d in devs]).empty)

    def test_replace_preview(self):
        old = sample_devices()
        new = [d.copy() for d in old]
        lan.replace(new, "00:01:FC:DE:3A:75", "00:01:FC:12:39:A0")
        p = lan.diff(old, new)
        self.assertEqual([i.tag for i in p.items], ["替換"])
        self.assertIn("MAC 00:01:FC:DE:3A:75 → 00:01:FC:12:39:A0", p.items[0].lines[0][0])
        self.assertEqual(p.replaced, [("front", "00:01:FC:DE:3A:75", "00:01:FC:12:39:A0")])
        self.assertEqual(len(p.power_cycle), 1)
        self.assertEqual(p.removed_points, [])

    def test_retire_lists_removed_points(self):
        old = sample_devices()
        new = [d.copy() for d in old]
        lan.set_status(new, "00:01:FC:DE:3A:76", RETIRED, NET)
        p = lan.diff(old, new)
        self.assertEqual(p.removed_points, ["中排 左", "中排 左中", "中排 右中", "中排 右"])
        self.assertTrue(p.items[0].lines[0][1])  # 狀態變更醒目

    def test_changes_and_standards(self):
        old = sample_devices()
        new = [d.copy() for d in old]
        d = by_mac(new)["00:01:FC:DE:3A:76"]
        d.config["name"] = "中段"
        d.config["max_probes"] = 5
        d.config["probes"].append({"id": 5, "description": "中央"})
        d.ipv4 = "192.168.10.30"
        lan.move(new, d.mac, -1)
        std = {k: {i: object() for i in range(1, 5)} for k in ("front", "middle", "rear")}
        p = lan.diff(old, new, std)
        texts = [t for i in p.items for t, _ in i.lines]
        self.assertIn("排名稱：中排 → 中段", texts)
        self.assertIn("新增探頭 ID 5「中央」", texts)
        self.assertIn("IP：192.168.10.12 → 192.168.10.30", texts)
        self.assertIn("順序", [i.tag for i in p.items])
        self.assertEqual(p.no_standard, ["中段 中央"])
        self.assertEqual(len(p.power_cycle), 1)


if __name__ == "__main__":
    unittest.main()
