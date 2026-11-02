"""DSC-23：BOOTP 拒絕配發的判定與狀態（實機 2026-11-02 的 dnsmasq 2.90 輸出）。"""

import unittest

from flatness import bootp_watch as bw

MAC = "74:95:A7:15:9B:82"
USED_LINE = "dnsmasq-dhcp[3523]: 1358107507 BOOTP(eno2) 192.168.10.11 74:95:a7:15:9b:82 address in use"
NONE_LINE = "dnsmasq-dhcp[2563]: 1358108570 BOOTP(eno2) 74:95:a7:15:9b:82 no address available"
OK_LINE = "dnsmasq-dhcp[6643]: 1358107518 BOOTP(eno2) 192.168.10.11 74:95:a7:15:9b:82 "


class Clock:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t


class ParseTest(unittest.TestCase):
    def test_lines(self):
        self.assertEqual(bw.parse(USED_LINE), bw.Outcome(MAC, "192.168.10.11", bw.USED, "address in use"))
        self.assertEqual(bw.parse(NONE_LINE), bw.Outcome(MAC, None, bw.NONE, "no address available"))
        self.assertEqual(bw.parse(OK_LINE), bw.Outcome(MAC, "192.168.10.11", None))
        self.assertEqual(bw.parse("BOOTP(eno2) 00:01:fc:12:39:a0 no address configured").refused, bw.NONE)
        self.assertEqual(bw.parse("BOOTP(eno2) 00:01:fc:12:39:a0 ignored").refused, bw.OTHER)

    def test_not_bootp(self):
        for line in ("dnsmasq-dhcp: 2716 DHCPDISCOVER(eno2) 3c:52:82:11:22:33",
                     "dnsmasq-dhcp[6643]: 1358107518 next server: 192.168.10.1",
                     "dnsmasq-dhcp[6643]: 1358107518 sent size:  4 option:  1 netmask  255.255.255.0"):
            self.assertIsNone(bw.parse(line))

    def test_interface(self):
        self.assertIsNone(bw.parse(USED_LINE, "eno1"))
        self.assertIsNotNone(bw.parse(USED_LINE, "eno2"))


class WatchTest(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.w = bw.BootpWatch(self.clock)
        self.w.watch({MAC: bw.Watched("第 1 台 plat1", "192.168.10.11")})

    def test_refused_once_logged(self):
        with self.assertLogs("flatness.bootp_watch", "WARNING") as cm:
            self.assertTrue(self.w.feed(USED_LINE))
            for _ in range(100):  # AC-7：持續被拒只記一筆
                self.clock.t += 4
                self.assertFalse(self.w.feed(USED_LINE))
            self.clock.t += 4
            self.assertTrue(self.w.feed(OK_LINE))
        self.assertEqual(len(cm.output), 2)
        self.assertIn("拒絕配發", cm.output[0])
        self.assertIn("恢復", cm.output[1])
        self.assertIsNone(self.w.refusal(MAC))

    def test_message(self):
        self.w.feed(USED_LINE)
        self.assertEqual(self.w.message(MAC), "192.168.10.11 被其他設備佔用（BOOTP 拒絕配發），請洽維護人員")
        self.w.feed(NONE_LINE)  # 原因改變
        self.assertEqual(self.w.refusal(MAC).kind, bw.NONE)
        self.assertIn("BOOTP 沒有配發 192.168.10.11（IP 不在配發網段", self.w.message(MAC))

    def test_unwatched_ignored(self):
        self.assertFalse(self.w.feed("BOOTP(eno2) 192.168.10.12 00:01:fc:de:3a:75 address in use"))
        self.assertIsNone(self.w.refusal("00:01:FC:DE:3A:75"))
        self.assertTrue(self.w.requesting("00:01:fc:de:3a:75"))  # 設定頁的 RST 提示用：不限追蹤中的設備

    def test_timeout(self):
        self.w.feed(USED_LINE)
        self.clock.t += bw.TIMEOUT - 1
        self.assertFalse(self.w.tick())
        self.clock.t += 1
        with self.assertLogs("flatness.bootp_watch", "WARNING") as cm:
            self.assertTrue(self.w.tick())
        self.assertIn("逾時清除", cm.output[0])
        self.assertIsNone(self.w.refusal(MAC))

    def test_arp_recovery(self):
        self.w.feed(USED_LINE)
        self.assertFalse(self.w.arp(MAC, "192.168.10.21"))  # 舊 IP 不算
        self.assertTrue(self.w.arp(MAC, "192.168.10.11"))
        self.assertIsNone(self.w.refusal(MAC))

    def test_connected_needs_confirm(self):
        self.w.feed(USED_LINE)
        self.w.connected(MAC)
        self.clock.t += 11  # DL-EN1 重新開機：10.8 秒後再送，又被拒
        self.w.feed(USED_LINE)
        self.clock.t += bw.CONFIRM
        self.assertFalse(self.w.tick())
        self.assertIsNotNone(self.w.refusal(MAC))
        self.w.connected(MAC)
        self.clock.t += bw.CONFIRM
        self.assertTrue(self.w.tick())
        self.assertIsNone(self.w.refusal(MAC))

    def test_requesting(self):
        self.assertFalse(self.w.requesting(MAC))
        self.w.feed(USED_LINE)
        self.assertTrue(self.w.requesting(MAC))
        self.clock.t += bw.RECENT
        self.assertFalse(self.w.requesting(MAC))

    def test_unwatch_clears(self):
        self.w.feed(USED_LINE)
        self.w.watch({})
        self.assertIsNone(self.w.refusal(MAC))


if __name__ == "__main__":
    unittest.main()
