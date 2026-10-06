"""畫面測試（offscreen）：設備設定對話框（5.10）與主畫面流程（5.1～5.5、MEA、UI-02）。"""

import os
import tempfile
import time
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from helpers import NET, ROOT, by_mac, sample_devices

try:
    from PySide6.QtWidgets import QApplication
except ImportError:  # 沒有 PySide6 的環境略過
    QApplication = None


def pump(app, sec=0.05):
    end = time.monotonic() + sec
    while time.monotonic() < end:
        app.processEvents()
        time.sleep(0.005)


@unittest.skipIf(QApplication is None, "需要 PySide6")
class UiBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        from flatness.ui import theme
        theme.load_fonts()
        cls.app.setStyleSheet(theme.qss())

    def make_backend(self, devices=None, probe_result=None):
        from flatness import config, netinfo, sync
        from flatness.backend import Backend
        from flatness.store import MemoryStore
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        cfg = config.load(ROOT / "installer" / "config.toml")
        cfg.engineer_password_sha256 = config.password_hash("1234")
        self.probes = []

        def probe(ip, ifname, own):
            self.probes.append(ip)
            return probe_result(ip) if probe_result else netinfo.ProbeResult(ip, netinfo.FREE)
        self.store = MemoryStore(sample_devices() if devices is None else devices)
        be = Backend(cfg, self.store, sync.Files(base / "dl-en1.json", base / "dl-en1.hosts"), None,
                     equip_net=NET, probe=probe)
        be.start()
        self.addCleanup(self.tmp.cleanup)
        return be


class SettingsDialogTest(UiBase):
    def setUp(self):
        from flatness.ui.settings_dialog import SettingsDialog
        self.be = self.make_backend()
        self.dlg = SettingsDialog(self.be)
        self.dlg._ask = lambda text: True
        self.warnings = []
        self.dlg._warn = self.warnings.append
        self.saved = []
        self.dlg.saved.connect(lambda r, p: self.saved.append((r, p)))
        self.dlg.enter_edit()

    def tearDown(self):
        self.dlg.deleteLater()

    def type(self, widget, text):
        widget.setText(text)
        widget.textEdited.emit(text)

    def save(self):
        self.assertTrue(self.dlg.btn_save.isEnabled(), [i.text() for i in self.dlg.issues])
        self.dlg.btn_save.click()
        self.assertEqual(self.dlg.pages.currentIndex(), 2)
        self.dlg.btn_commit.click()

    def test_password_required(self):  # UPL-01
        from flatness.ui.settings_dialog import SettingsDialog
        d = SettingsDialog(self.be)
        d.btn_pw_ok.click()
        self.assertTrue(d.pw_edit.property("error"))
        d.pw_edit.setText("wrong")
        d.btn_pw_ok.click()
        self.assertEqual(d.pages.currentIndex(), 0)
        self.assertIn("密碼錯誤", d.pw_msg.text())
        d.pw_edit.setText("1234")
        d.btn_pw_ok.click()
        self.assertEqual(d.pages.currentIndex(), 1)

    def test_list_order_and_no_add_or_mac_edit(self):  # DSC-02、DSC-16
        macs = [self.dlg.table.item(r, 3).text() for r in range(self.dlg.table.rowCount())]
        self.assertEqual(macs[0], "00:01:FC:12:39:A0")  # 不明設備在最前
        self.assertEqual(macs[-1], "00:01:FC:DE:3A:70")  # 已停用在最後
        self.assertIn("有 1 台不明設備", self.dlg.list_hint.text())
        texts = [b.text() for b in self.dlg.findChildren(type(self.dlg.btn_save))]
        self.assertFalse(any("新增設備" in t or t == "刪除" for t in texts))
        from PySide6.QtWidgets import QLineEdit
        self.assertFalse(any(e.objectName() == "mac" for e in self.dlg.findChildren(QLineEdit)))

    def test_classify_unknown_as_live_and_save(self):  # DSC-03-G1、EDT-01
        d = self.dlg
        d.select("00:01:FC:12:39:A0")
        d.status_box.setCurrentIndex(1)  # DL-EN1 使用中
        self.assertEqual(d.ip_edit.text(), "192.168.10.14")  # DSC-08 預設 IP
        self.assertFalse(d.btn_save.isEnabled())  # key、名稱未填
        self.type(d.key_edit, "extra")
        self.type(d.name_edit, "加排")
        pump(self.app, 0.2)
        self.assertEqual(self.probes, ["192.168.10.14"])  # 新 IP 已探測
        self.save()
        self.assertEqual(len(self.saved), 1)
        result, preview = self.saved[0]
        self.assertEqual([x["key"] for x in result.definition["dl_en1"]], ["front", "middle", "rear", "extra"])
        self.assertIn("extra", Path(self.tmp.name, "dl-en1.hosts").read_text())
        self.assertEqual(by_mac(self.store.load())["00:01:FC:12:39:A0"].config["name"], "加排")
        self.assertIn("加排 左", preview.no_standard)  # extra 沒有允收標準

    def test_nothing_written_before_save(self):  # EDT-02、DSC-12-A1
        d = self.dlg
        d.select("00:01:FC:DE:3A:76")
        self.type(d.name_edit, "中段")
        self.assertTrue(d.is_dirty())
        self.assertIn("有尚未儲存的變更", d.dirty_label.text())
        self.assertEqual(by_mac(self.store.load())["00:01:FC:DE:3A:76"].config["name"], "中排")
        d.reject()
        self.assertEqual(by_mac(self.store.load())["00:01:FC:DE:3A:76"].config["name"], "中排")

    def test_duplicate_ip_names_occupant_and_blocks_save(self):  # DSC-08-A3、A4
        d = self.dlg
        d.select("00:01:FC:DE:3A:77")
        self.type(d.ip_edit, "192.168.10.200")
        self.assertIn("已由 其他設備 3C:52:82:11:22:33（eng-laptop）使用", d.ip_note.text())
        self.assertTrue(d.ip_edit.property("error"))
        self.assertFalse(d.btn_save.isEnabled())
        self.assertEqual(self.probes, [])  # 資料表衝突時不探測

    def test_arp_taken_blocks_save(self):  # DSC-10-G1
        from flatness import netinfo
        self.dlg.deleteLater()
        from flatness.ui.settings_dialog import SettingsDialog
        be = self.make_backend(probe_result=lambda ip: netinfo.ProbeResult(ip, netinfo.TAKEN, "3C:52:82:44:55:66")
                               if ip.endswith(".50") else netinfo.ProbeResult(ip, netinfo.FREE))
        d = SettingsDialog(be)
        d.enter_edit()
        d.select("00:01:FC:DE:3A:77")
        self.type(d.ip_edit, "192.168.10.50")
        d.ip_edit.editingFinished.emit()
        pump(self.app, 0.2)
        self.assertIn("網路上已有設備使用此 IP（MAC 3C:52:82:44:55:66）", d.ip_note.text())
        self.assertFalse(d.btn_save.isEnabled())
        self.type(d.ip_edit, "192.168.10.60")
        d.ip_edit.editingFinished.emit()
        pump(self.app, 0.2)
        self.assertTrue(d.btn_save.isEnabled())

    def test_unchanged_ip_not_probed(self):  # DSC-10-A1
        d = self.dlg
        d.select("00:01:FC:DE:3A:75")
        self.type(d.name_edit, "前段")
        d.ip_edit.editingFinished.emit()
        pump(self.app, 0.1)
        self.assertEqual(self.probes, [])
        self.assertEqual(d.ip_note.text(), "使用中的 IP，未變更")

    def test_hide_writes_immediately_and_blocked_for_live(self):  # DSC-13
        d = self.dlg
        d.select("00:01:FC:DE:3A:75")
        self.assertFalse(d.btn_hide.isEnabled())
        d.select("3C:52:82:11:22:33")
        d.btn_hide.click()
        self.assertTrue(by_mac(self.store.load())["3C:52:82:11:22:33"].hidden)
        self.assertFalse(d.is_dirty())
        macs = [d.table.item(r, 3).text() for r in range(d.table.rowCount())]
        self.assertNotIn("3C:52:82:11:22:33", macs)
        self.assertEqual(d.chk_hidden.text(), "顯示已隱藏（1）")

    def test_replace(self):  # DSC-14-G1
        d = self.dlg
        d.select("00:01:FC:DE:3A:75")
        d.btn_replace.click()
        self.assertEqual(d.replace_box.currentData(), "00:01:FC:12:39:A0")
        d.btn_replace_ok.click()
        pump(self.app, 0.2)
        self.assertEqual(d.selected, "00:01:FC:12:39:A0")
        self.save()
        result, preview = self.saved[0]
        self.assertEqual(result.definition["dl_en1"][0]["mac"], "00:01:FC:12:39:A0")
        self.assertEqual(preview.items[0].tag, "替換")
        self.assertEqual(by_mac(self.store.load())["00:01:FC:DE:3A:75"].status, "dl_en1_retired")

    def test_replace_old_device_still_online_only_warns(self):  # DSC-14-A4
        from flatness import netinfo
        from flatness.ui.settings_dialog import SettingsDialog
        be = self.make_backend(probe_result=lambda ip: netinfo.ProbeResult(ip, netinfo.TAKEN, "00:01:FC:DE:3A:75"))
        d = SettingsDialog(be)
        d.enter_edit()
        d.select("00:01:FC:DE:3A:75")
        d.btn_replace.click()
        d.btn_replace_ok.click()
        pump(self.app, 0.2)
        self.assertIn("舊機 00:01:FC:DE:3A:75 仍在線上", d.ip_note.text())
        self.assertTrue(d.btn_save.isEnabled())

    def test_maint_removes_from_screen(self):  # DSC-15-G1
        d = self.dlg
        d.select("00:01:FC:DE:3A:76")
        d.status_box.setCurrentIndex(2)  # 維修中
        self.save()
        result, preview = self.saved[0]
        self.assertEqual([x["key"] for x in result.definition["dl_en1"]], ["front", "rear"])
        self.assertIn("00:01:fc:de:3a:76", Path(self.tmp.name, "dl-en1.hosts").read_text())
        self.assertEqual(len(preview.removed_points), 4)

    def test_apply_failure_keeps_dialog_and_restores(self):  # UPL-08
        d = self.dlg

        def boom(*a, **k):
            raise RuntimeError("dnsmasq 啟動失敗")
        self.be.apply = boom
        d.select("00:01:FC:DE:3A:76")
        self.type(d.name_edit, "中段")
        self.save()
        self.assertEqual(self.saved, [])
        self.assertIn("套用失敗", self.warnings[-1])
        self.assertEqual(d.pages.currentIndex(), 2)

    def test_import(self):  # DEF-07、UPL
        import json
        from flatness import lan
        path = Path(self.tmp.name, "new.json")
        defn = lan.definition_from(sample_devices())
        defn["dl_en1"][1]["name"] = "中段"
        path.write_text(json.dumps(defn, ensure_ascii=False), encoding="utf-8")
        self.dlg.import_file(path)
        self.assertEqual(self.dlg.pages.currentIndex(), 2)
        texts = [t for i in self.dlg.preview.items for t, _ in i.lines]
        self.assertIn("排名稱：中排 → 中段", texts)

    def test_import_errors_listed(self):  # UPL-04
        path = Path(self.tmp.name, "bad.json")
        path.write_text('{"version": 1, "dl_en1": [{"key": "A"}]}', encoding="utf-8")
        self.dlg.import_file(path)
        self.assertEqual(self.dlg.pages.currentIndex(), 1)
        self.assertIn("dl_en1[0].key", self.warnings[-1])

    def test_auto_refresh_adds_new_device(self):  # DSC-02
        from datetime import datetime
        from flatness.store import SeenEvent
        self.store.record([SeenEvent("00:01:FC:12:3B:11", "BOOTP", datetime.now())])
        self.dlg._refresh()
        macs = [self.dlg.table.item(r, 3).text() for r in range(self.dlg.table.rowCount())]
        self.assertIn("00:01:FC:12:3B:11", macs)
        self.assertIn("偵測到 1 台新設備", self.dlg.toast.history[-1])

    def test_db_down_read_only(self):  # DSC-05
        from flatness.ui.settings_dialog import SettingsDialog
        self.store.available = False
        d = SettingsDialog(self.be)
        d.enter_edit()
        self.assertTrue(d.read_only)
        self.assertTrue(d.db_banner.isVisibleTo(d))
        self.assertGreater(d.table.rowCount(), 0)  # 上次讀到的資料
        self.assertFalse(d.btn_save.isEnabled())


class MainWindowTest(UiBase):
    def setUp(self):
        from flatness import measure
        from flatness.ui.main_window import MainWindow
        self.be = self.make_backend()
        self.stations = []

        def factory(defn):
            s = measure.DemoStation(defn, self.be.cfg.standards, seed=1, delay=0)
            self.stations.append(s)
            return s
        self.win = MainWindow(self.be, factory, countdown=1, redetect=10)
        self.win.resize(1920, 1080)

    def tearDown(self):
        self.win._retry_timer.stop()
        self.win.deleteLater()

    def wait_state(self, *states, timeout=3.0):
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            pump(self.app, 0.02)
            if self.win.banner.state in states and not self.win.busy:
                return
        self.fail(f"橫幅狀態 {self.win.banner.state}，預期 {states}")

    def test_layout_from_definition(self):  # DEF-04
        self.assertEqual([r.dev["key"] for r in self.win.rows], ["front", "middle", "rear"])
        self.assertEqual(sum(len(r.tiles) for r in self.win.rows), 12)

    def test_detect_then_measure_pass_and_next_writes(self):  # DEV-01、MEA-01～MEA-06
        w = self.win
        w.detect()
        self.assertTrue(w.busy)
        self.assertFalse(w.btn_settings.isEnabled())  # 偵測中停用
        self.wait_state("idle")
        self.assertIn("第 1 次偵測", w.banner.say.text())
        self.assertFalse(w.banner.btn_reread.isEnabled())
        self.stations[-1].force = "pass"
        w.next_piece()
        self.assertEqual(len(w.serial), 17)  # DAT-01
        self.assertEqual(w.banner.state, "countdown")
        self.wait_state("pass")
        first = w.serial
        w.reread()
        self.assertEqual(w.serial, first)  # MEA-05 編號不變
        self.wait_state("pass")
        self.assertIn("重讀 1 次", w.reread_label.text())
        self.assertEqual(w.sink.rows, [])  # MEA-06 重讀不寫入
        self.stations[-1].force = "fail"
        w.next_piece()
        self.assertEqual(len(w.sink.rows), 1)
        self.assertEqual((w.sink.rows[0].serial, w.sink.rows[0].rereads, w.sink.rows[0].judgment),
                         (first, 1, "PASS"))
        self.wait_state("fail")
        faded = [t for r in w.rows for t in r.tiles.values() if t.state == "ok"]
        self.assertTrue(faded and all(t._fx.opacity() == 0.55 for t in faded))  # 淡化規則

    def test_first_next_writes_nothing(self):  # MEA-02
        self.win.detect()
        self.wait_state("idle")
        self.win.next_piece()
        self.assertEqual(self.win.sink.rows, [])

    def test_device_error_and_auto_retry_text(self):  # JDG-04、DEV-05、DEV-06
        w = self.win
        w.detect()
        self.wait_state("idle")
        self.stations[-1].force = "error"
        w.next_piece()
        self.wait_state("error")
        self.assertIn("探頭無回應", w.banner.say.text())
        self.assertIn("10</b> 秒後自動重新偵測", w.banner.say.text())
        self.assertFalse(w.banner.btn_next.isEnabled())
        self.assertEqual(w.result.judgment, "ERROR")

    def test_unreachable_device_marks_row(self):  # DEV-04、UI-07
        from flatness import measure
        w = self.win
        st = self.stations[-1]
        st.detect = lambda: [measure.DeviceStatus("front"), measure.DeviceStatus("middle", reachable=False),
                             measure.DeviceStatus("rear")]
        w.detect()
        self.wait_state("error")
        self.assertIn("中排 DL-EN1 偵測不到", w.banner.say.text())
        self.assertIn("偵測不到", w.rows[1].unit_text.text())

    def test_missing_standard_is_device_error(self):  # DEF-09
        self.be.cfg.standards.pop("rear")
        self.win.rebuild(self.be.definition)
        self.win.detect()
        self.wait_state("error")
        self.assertIn("後排 有 4 個探頭未設定允收標準", self.win.banner.say.text())

    def test_settings_saved_rebuilds_and_detects(self):  # 5.10 儲存後
        from flatness import lan, sync
        w = self.win
        w.detect()
        self.wait_state("idle")
        old = self.store.load()
        new = [d.copy() for d in old]
        lan.set_status(new, "00:01:FC:DE:3A:76", lan.MAINT, NET)
        result = self.be.apply(old, new)
        w._on_settings_saved(result, lan.diff(old, new))
        self.assertEqual([r.dev["key"] for r in w.rows], ["front", "rear"])
        self.wait_state("idle")
        self.assertEqual(w.detect_count, 2)

    def test_flags(self):  # 5.1 系統狀態提示
        w = self.win
        w._on_bootp(False, "dnsmasq 異常結束")
        w.set_flag("db", "無法讀取資料庫，使用上次的設定")
        pump(self.app)
        texts = [w.flag_box.itemAt(i).widget().text() for i in range(w.flag_box.count())]
        self.assertTrue(any("BOOTP 服務停止" in t for t in texts))
        self.assertTrue(any("無法讀取資料庫" in t for t in texts))
        w._on_bootp(True, "")
        pump(self.app)
        texts = [w.flag_box.itemAt(i).widget().text() for i in range(w.flag_box.count())]
        self.assertFalse(any("BOOTP" in t for t in texts))

    def test_close_writes_pending(self):  # DAT-05
        w = self.win
        w.detect()
        self.wait_state("idle")
        w.next_piece()
        self.wait_state("pass", "fail", "error")
        w.close()
        self.assertEqual(len(w.sink.rows), 1)


if __name__ == "__main__":
    unittest.main()
