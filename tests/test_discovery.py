"""探索（DSC-01、DSC-05）與 dnsmasq 管理（DSC-07）。"""

import sys
import threading
import time
import unittest

from helpers import ROOT, T0

from flatness.discovery import Recorder, RequestParser
from flatness.dnsmasq import DnsmasqError, DnsmasqService
from flatness.store import MemoryStore, SeenEvent

FAKE = [sys.executable, str(ROOT / "scripts" / "fake-dnsmasq.py")]


class ParserTest(unittest.TestCase):
    def setUp(self):
        self.p = RequestParser("eno2")

    def feed(self, line):
        return self.p.feed(line, now=T0)

    def test_bootp_assigned_and_unknown(self):
        (e,) = self.feed("dnsmasq-dhcp: 3911 BOOTP(eno2) 192.168.10.11 00:01:fc:de:3a:75 front")
        self.assertEqual((e.mac, e.kind, e.count), ("00:01:FC:DE:3A:75", "BOOTP", 1))
        (e,) = self.feed("dnsmasq-dhcp[812]: 3912 BOOTP(eno2) 00:01:fc:12:39:a0 no address configured")
        self.assertEqual(e.mac, "00:01:FC:12:39:A0")

    def test_without_xid_and_syslog_prefix(self):
        (e,) = self.feed("Oct  6 14:32:40 mosa dnsmasq-dhcp[812]: BOOTP(eno2) 00:01:fc:12:39:a0 ")
        self.assertEqual(e.mac, "00:01:FC:12:39:A0")

    def test_dhcp_requests_counted_replies_ignored(self):
        self.assertEqual(len(self.feed("dnsmasq-dhcp: 77 DHCPDISCOVER(eno2) 3c:52:82:11:22:33")), 1)
        self.assertEqual(self.feed("dnsmasq-dhcp: 77 DHCPOFFER(eno2) 192.168.10.200 3c:52:82:11:22:33"), [])
        (e,) = self.feed("dnsmasq-dhcp: 78 DHCPREQUEST(eno2) 192.168.10.200 3c:52:82:11:22:33")
        self.assertEqual(e.kind, "DHCP")
        self.assertEqual(self.feed("dnsmasq-dhcp: 78 DHCPACK(eno2) 192.168.10.200 3c:52:82:11:22:33 x"), [])

    def test_hostname_and_vendor_by_xid(self):
        self.feed("dnsmasq-dhcp: 2716 DHCPDISCOVER(eno2) 3c:52:82:11:22:33")
        (n,) = self.feed("dnsmasq-dhcp: 2716 client provides name: eng-laptop")
        (v,) = self.feed("dnsmasq-dhcp: 2716 vendor class: MSFT 5.0")
        self.assertEqual((n.mac, n.hostname, n.count), ("3C:52:82:11:22:33", "eng-laptop", 0))
        self.assertEqual(v.vendor_class, "MSFT 5.0")
        self.assertEqual(self.feed("dnsmasq-dhcp: 9999 client provides name: who"), [])

    def test_other_interface_ignored(self):  # DSC-01-A1
        self.assertEqual(self.feed("dnsmasq-dhcp: 1 DHCPDISCOVER(eno1) 3c:52:82:11:22:33"), [])

    def test_noise(self):
        for line in ("dnsmasq-dhcp: DHCP, static leases only on 192.168.10.0",
                     "dnsmasq: started, version 2.90 DNS disabled", "dnsmasq-dhcp: 2716 tags: eno2", ""):
            self.assertEqual(self.feed(line), [])


class RecorderTest(unittest.TestCase):
    def wait(self, cond, timeout=3.0):
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            if cond():
                return True
            time.sleep(0.02)
        return False

    def test_records_and_notifies(self):
        store = MemoryStore()
        seen = []
        r = Recorder(store, seen.extend).start()
        r.put([SeenEvent("00:01:FC:DE:3A:75", "BOOTP", T0)] * 3)
        self.assertTrue(self.wait(lambda: len(seen) == 3))
        self.assertEqual(store.load()[0].seen_count, 3)
        r.stop()

    def test_buffers_while_db_down(self):  # DSC-05-G1
        store = MemoryStore()
        store.available = False
        r = Recorder(store, retry=0.1).start()
        r.put([SeenEvent("00:01:FC:DE:3A:78", "BOOTP", T0), SeenEvent("00:01:FC:DE:3A:79", "BOOTP", T0)])
        self.assertTrue(self.wait(lambda: not r.db_ok))
        self.assertEqual(len(r.pending()), 2)
        store.available = True
        self.assertTrue(self.wait(lambda: len(store.load()) == 2))
        self.assertEqual(r.pending(), [])
        self.assertEqual({d.last_seen for d in store.load()}, {T0})
        r.stop()


class DnsmasqTest(unittest.TestCase):
    def test_start_lines_restart_stop(self):
        lines, states = [], []
        svc = DnsmasqService(FAKE + ["--scenario", "quiet"], lines.append,
                             lambda up, why: states.append(up), settle=0.3)
        svc.start()
        end = time.monotonic() + 3
        while time.monotonic() < end and len(lines) < 2:
            time.sleep(0.05)
        self.assertIn("static leases only", lines[0])
        svc.restart()
        self.assertTrue(svc.running)
        svc.stop()
        self.assertFalse(svc.running)
        self.assertEqual(states[-1], False)

    def test_restart_failure_raises(self):
        svc = DnsmasqService(FAKE + ["--fail"], settle=1.0)
        with self.assertRaises(DnsmasqError) as ctx:
            svc.restart()
        self.assertIn("bad option", str(ctx.exception))
        svc.stop()

    def test_crash_auto_restarts(self):  # DSC-07：異常結束後自動重新啟動
        states = []
        svc = DnsmasqService(FAKE + ["--scenario", "quiet"], on_state=lambda up, why: states.append((up, why)),
                             restart_delay=0.2)
        svc.start()
        time.sleep(0.3)
        svc._proc.kill()
        end = time.monotonic() + 3
        while time.monotonic() < end and not (len(states) >= 3 and states[-1][0]):
            time.sleep(0.05)
        self.assertEqual([s[0] for s in states[:3]], [True, False, True])
        self.assertIn("異常結束", states[1][1])
        svc.stop()

    def test_no_command_is_noop(self):  # 模擬模式不啟動 dnsmasq（DSC-07-A6）
        svc = DnsmasqService(None)
        svc.start()
        svc.restart()
        self.assertFalse(svc.running)

    def test_demo_scenario_feeds_parser(self):
        parser = RequestParser("eno2")
        events = []
        lock = threading.Lock()

        def on_line(line):
            with lock:
                events.extend(parser.feed(line))
        svc = DnsmasqService(FAKE, on_line)
        svc.start()
        end = time.monotonic() + 4
        while time.monotonic() < end and not any(e.hostname for e in events):
            time.sleep(0.05)
        svc.stop()
        macs = {e.mac for e in events}
        self.assertIn("00:01:FC:12:39:A0", macs)
        self.assertIn("eng-laptop", {e.hostname for e in events})


if __name__ == "__main__":
    unittest.main()
