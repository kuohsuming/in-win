"""畫面測試（offscreen）：設備設定對話框（5.10）與主畫面流程（5.1～5.5、MEA、UI-02）。"""

import os
import tempfile
import time
import unittest
from datetime import datetime
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from helpers import NET, ROOT, by_mac, sample_devices

try:
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication, QLabel
except ImportError:  # 沒有 PySide6 的環境略過
    QApplication = QLabel = Qt = None


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
        self.assertEqual(macs[1:4], ["00:01:FC:DE:3A:75", "00:01:FC:DE:3A:76", "00:01:FC:DE:3A:77"])
        self.assertIn("有 1 台不明設備", self.dlg.list_hint.text())
        texts = [b.text() for b in self.dlg.findChildren(type(self.dlg.btn_save))]
        self.assertFalse(any("新增設備" in t for t in texts))  # 「刪除」為 DSC-18，允許
        from PySide6.QtWidgets import QLineEdit
        self.assertFalse(any(e.objectName() == "mac" for e in self.dlg.findChildren(QLineEdit)))

    def test_classify_unknown_as_live_and_save(self):  # DSC-03-G1、EDT-01
        d = self.dlg
        d.select("00:01:FC:12:39:A0")
        d.status_box.setCurrentIndex(1)  # DL-EN1 使用中
        self.assertEqual(d.ip_edit.text(), "192.168.10.14")  # DSC-08 預設 IP
        # 位置預設最小的空位（EDT-05）：第 1～3 排已佔用；已停用的舊機（第 4 排）不佔用
        self.assertEqual(d.row_box.currentData(), "row-4")
        model = d.row_box.model()
        self.assertFalse(model.item(d.row_box.findData("row-1")).isEnabled())  # 每排一台
        self.assertIn("前排", d.row_box.itemText(d.row_box.findData("row-1")))
        self.assertTrue(model.item(d.row_box.findData("row-5")).isEnabled())
        # 有變更儲存鍵就可按（EDT-04）；排名稱未填 → 按下列出錯誤，不進入確認頁、不寫入
        self.assertTrue(d.btn_save.isEnabled())
        self.assertIn("有 1 項錯誤，儲存前須修正", d.save_hint.text())
        self.assertIn("排名稱", d.save_hint.toolTip())
        d.btn_save.click()
        self.assertEqual(d.pages.currentIndex(), 1)
        self.assertIn("設定有 1 項錯誤，請修正後再儲存", self.warnings[-1])
        self.assertEqual(by_mac(self.store.load())["00:01:FC:12:39:A0"].status, "unclassified")
        d.row_box.setCurrentIndex(d.row_box.findData("row-5"))
        self.type(d.name_edit, "加排")
        pump(self.app, 0.2)
        self.assertEqual(d.save_hint.text(), "")
        self.assertEqual(self.probes, ["192.168.10.14"])  # 新 IP 已探測
        self.save()
        self.assertEqual(len(self.saved), 1)
        result, preview = self.saved[0]
        self.assertEqual([x["key"] for x in result.definition["dl_en1"]], ["row-1", "row-2", "row-3", "row-5"])
        self.assertIn("row-5", Path(self.tmp.name, "dl-en1.hosts").read_text())
        self.assertEqual(by_mac(self.store.load())["00:01:FC:12:39:A0"].config["name"], "加排")
        self.assertIn("加排 左", preview.no_standard)  # 第 5 排沒有允收標準

    def test_probe_count_drives_list_and_saves(self):  # EDT-06
        d = self.dlg
        d.select("00:01:FC:DE:3A:76")
        d.max_spin.setValue(6)                                  # 增加：末端新增「探頭 5」「探頭 6」
        rows = [(d.probe_table.item(r, 0).text(), d.probe_table.item(r, 1).text())
                for r in range(d.probe_table.rowCount())]
        self.assertEqual(rows[-2:], [("5", "探頭 5"), ("6", "探頭 6")])
        self.assertTrue(d.btn_save.isEnabled())
        self.assertEqual(d.issues, [])
        d.max_spin.setValue(5)                                  # 減少：移除末端
        self.assertEqual(d.probe_table.rowCount(), 5)
        d.probe_table.setCurrentCell(1, 1)                      # 刪除第 2 個（左中）：後面的 ID 往前遞補
        d.btn_probe_del.click()
        self.assertEqual(d.max_spin.value(), 4)
        self.assertEqual([d.probe_table.item(r, 0).text() for r in range(4)], ["1", "2", "3", "4"])
        self.assertEqual(d.probe_table.item(1, 1).text(), "右中")
        self.assertFalse(d.probe_table.item(0, 0).flags() & Qt.ItemIsEditable)  # ID 不可手動修改
        self.save()
        cfg = by_mac(self.store.load())["00:01:FC:DE:3A:76"].config
        self.assertEqual(cfg["max_probes"], 4)
        self.assertEqual([p["description"] for p in cfg["probes"]], ["左", "右中", "右", "探頭 5"])

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
        self.assertTrue(d.btn_save.isEnabled())
        d.btn_save.click()
        self.assertEqual(d.pages.currentIndex(), 1)  # 資料表衝突：按下列出錯誤，不進入確認頁
        self.assertIn("192.168.10.200", self.warnings[-1])
        self.assertEqual(self.probes, [])  # 資料表衝突時不探測

    def test_arp_taken_only_warns(self):  # DSC-10-G2：ARP 探測結果只提示，不阻擋儲存
        from flatness import netinfo
        self.dlg.deleteLater()
        from flatness.ui.settings_dialog import SettingsDialog
        be = self.make_backend(probe_result=lambda ip: netinfo.ProbeResult(ip, netinfo.TAKEN, "3C:52:82:44:55:66")
                               if ip.endswith(".50") else netinfo.ProbeResult(ip, netinfo.FREE))
        d = SettingsDialog(be)
        d.enter_edit()
        d.select("00:01:FC:DE:3A:77")
        self.type(d.ip_edit, "192.168.10.50")
        self.assertTrue(d.btn_save.isEnabled())  # 檢查中也可儲存
        d.ip_edit.editingFinished.emit()
        pump(self.app, 0.2)
        self.assertIn("網路上已有設備使用此 IP（MAC 3C:52:82:44:55:66）", d.ip_note.text())
        self.assertTrue(d.btn_save.isEnabled())
        self.assertEqual(d.save_hint.text(), "")
        warns = [d.msg_list.item(r).text() for r in range(d.msg_list.count())]
        self.assertTrue(any(w.startswith("⚠") and "仍可儲存" in w for w in warns), warns)
        d.btn_save.click()
        confirm = " ".join(w.text() for w in d.pages.widget(2).findChildren(QLabel))
        self.assertIn("儲存後可能發生 IP 衝突", confirm)

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

    def list_macs(self, dlg):
        return [dlg.table.item(r, 3).text() for r in range(dlg.table.rowCount())]

    def test_move_saves_immediately_and_persists_after_restart(self):  # DSC-17-G1
        from flatness import lan, sync
        from flatness.backend import Backend
        from flatness.ui.main_window import MainWindow
        from flatness.ui.settings_dialog import SettingsDialog
        d = self.dlg
        hosts_before = Path(self.tmp.name, "dl-en1.hosts").read_text()
        d.select("00:01:FC:DE:3A:77")              # 後排
        d.btn_up.click()
        d.btn_up.click()                           # 後排 → 最上，每按一次即儲存
        live = ["00:01:FC:DE:3A:77", "00:01:FC:DE:3A:75", "00:01:FC:DE:3A:76"]
        self.assertEqual(self.list_macs(d)[1:4], live)
        self.assertEqual([x.mac for x in lan.list_order(self.store.load())][1:4], live)  # 已寫入資料庫
        self.assertEqual([x["key"] for x in lan.definition_from(self.store.load())["dl_en1"]],
                         ["row-1", "row-2", "row-3"])  # 主畫面依排號，不受清單順序影響（EDT-05）
        self.assertEqual(Path(self.tmp.name, "dl-en1.hosts").read_text(), hosts_before)  # 不需重啟 dnsmasq
        self.assertFalse(d.is_dirty())             # 不需按「儲存」
        d.reject()

        # 模擬 App 重新啟動：同一個資料庫、新的 Backend，檔案由資料庫重新產生
        base = Path(self.tmp.name, "restart")
        be2 = Backend(self.be.cfg, self.store, sync.Files(base / "dl-en1.json", base / "dl-en1.hosts"), None,
                      equip_net=NET, probe=lambda *a: None)
        be2.start()
        self.assertEqual([x["key"] for x in be2.definition["dl_en1"]], ["row-1", "row-2", "row-3"])
        win = MainWindow(be2, lambda defn: None)
        self.assertEqual([r.dev["name"] for r in win.rows], ["前排", "中排", "後排"])  # 主畫面依排號
        d2 = SettingsDialog(be2)
        d2.enter_edit()
        self.assertEqual(self.list_macs(d2)[1:4], live)  # 設定頁
        win.deleteLater()
        d2.deleteLater()

    def test_move_keeps_other_unsaved_edits(self):  # DSC-17：只寫入順序
        from flatness import lan
        d = self.dlg
        d.select("00:01:FC:DE:3A:76")
        self.type(d.name_edit, "中段")             # 未儲存的編輯
        d.select("00:01:FC:DE:3A:77")
        d.btn_up.click()
        saved = {x["key"]: x for x in lan.definition_from(self.store.load())["dl_en1"]}
        self.assertEqual(saved["row-2"]["name"], "中排")    # 名稱未寫入
        self.assertEqual([x.mac for x in lan.list_order(self.store.load())][1:4],
                         ["00:01:FC:DE:3A:75", "00:01:FC:DE:3A:77", "00:01:FC:DE:3A:76"])  # 順序已寫入
        self.assertTrue(d.is_dirty())
        self.assertEqual(d.work["00:01:FC:DE:3A:76"].config["name"], "中段")

    def test_move_failure_keeps_order(self):
        d = self.dlg

        def boom(*a, **k):
            raise RuntimeError("資料庫無法連線")
        self.be.apply = boom
        d.select("00:01:FC:DE:3A:77")
        d.btn_up.click()
        self.assertIn("無法儲存順序", self.warnings[-1])
        self.assertEqual(self.list_macs(d)[1:4], ["00:01:FC:DE:3A:75", "00:01:FC:DE:3A:76", "00:01:FC:DE:3A:77"])

    def test_move_maint_row(self):  # DSC-17：維修中也可調整清單順序；主畫面仍依排號（EDT-05）
        from flatness import lan
        old = self.store.load()
        new = [x.copy() for x in old]
        lan.set_status(new, "00:01:FC:DE:3A:77", lan.MAINT, NET)
        self.be.apply(old, new)
        self.dlg.load()
        self.dlg.select("00:01:FC:DE:3A:77")
        self.assertTrue(self.dlg.btn_up.isEnabled())
        self.dlg.btn_up.click()
        layout = lan.screen_layout(self.store.load())["dl_en1"]
        self.assertEqual([(x["key"], x.get("maint", False)) for x in layout],
                         [("row-1", False), ("row-2", False), ("row-3", True)])

    def test_delete_unclassified_after_confirm(self):  # DSC-18
        d = self.dlg
        asked = []
        d._confirm_delete = lambda text: asked.append(text) or False
        d.select("00:01:FC:12:39:A0")
        self.assertTrue(d.btn_delete.isEnabled())
        d.btn_delete.click()                                   # 取消：不刪除
        self.assertIn("00:01:FC:12:39:A0", by_mac(self.store.load()))
        self.assertIn("無法還原", asked[-1])
        d._confirm_delete = lambda text: True
        d.btn_delete.click()
        self.assertNotIn("00:01:FC:12:39:A0", by_mac(self.store.load()))
        self.assertNotIn("00:01:FC:12:39:A0", self.list_macs(d))
        self.assertEqual(self.saved, [])                       # 不影響主畫面
        self.assertFalse(d.is_dirty())

    def test_delete_live_updates_files_and_main_screen(self):  # DSC-18
        d = self.dlg
        texts = []
        d._confirm_delete = lambda text: texts.append(text) or True
        d.select("00:01:FC:DE:3A:76")
        self.type(d.name_edit, "中段")                         # 本台尚未儲存的修改一併捨棄
        d.select("00:01:FC:DE:3A:77")
        self.type(d.name_edit, "後段")                         # 其他設備的修改保留
        d.select("00:01:FC:DE:3A:76")
        d.btn_delete.click()
        self.assertIn("主畫面將移除", texts[-1])
        self.assertIn("192.168.10.12", texts[-1])
        self.assertNotIn("00:01:FC:DE:3A:76", by_mac(self.store.load()))
        self.assertNotIn("3a:76", Path(self.tmp.name, "dl-en1.hosts").read_text())
        (result, _preview), = self.saved
        self.assertEqual([x["key"] for x in result.layout["dl_en1"]], ["row-1", "row-3"])
        self.assertEqual(d.work["00:01:FC:DE:3A:77"].config["name"], "後段")
        self.assertTrue(d.is_dirty())

    def test_delete_last_live_allowed_with_warning(self):  # DSC-18：任何設備皆可刪除，含最後一台使用中
        from flatness import lan
        old = self.store.load()
        new = [x.copy() for x in old]
        for mac in ("00:01:FC:DE:3A:76", "00:01:FC:DE:3A:77"):
            lan.set_status(new, mac, lan.RETIRED, NET)
        self.be.apply(old, new)
        self.dlg.load()
        texts = []
        self.dlg._confirm_delete = lambda text: texts.append(text) or True
        self.dlg.select("00:01:FC:DE:3A:75")
        self.dlg.btn_delete.click()
        self.assertIn("最後一台", texts[-1])
        self.assertNotIn("00:01:FC:DE:3A:75", by_mac(self.store.load()))
        (result, _p), = self.saved
        self.assertEqual(result.definition["dl_en1"], [])      # 定義檔 0 台
        self.assertEqual(Path(self.tmp.name, "dl-en1.hosts").read_text().count("00:01:fc:de:3a:75"), 0)

    def test_move_buttons_any_device(self):  # DSC-17：到頂停用上移、到底停用下移，其餘兩鍵可用
        d = self.dlg
        shown = self.list_macs(d)
        d.select(shown[0])
        self.assertEqual((d.btn_up.isEnabled(), d.btn_down.isEnabled()), (False, True))
        d.select(shown[-1])
        self.assertEqual((d.btn_up.isEnabled(), d.btn_down.isEnabled()), (True, False))
        for mac in shown[1:-1]:                     # 不論設備類型
            d.select(mac)
            self.assertTrue(d.btn_up.isEnabled() and d.btn_down.isEnabled(), mac)
            self.assertEqual(d.move_hint.text(), "")

    def test_move_other_device_saves_order_only(self):  # DSC-17
        from flatness import lan
        d = self.dlg
        d.select("3C:52:82:11:22:33")              # 其他設備
        before = self.list_macs(d)
        d.btn_up.click()
        after = self.list_macs(d)
        i = before.index("3C:52:82:11:22:33")
        self.assertEqual(after[i - 1], "3C:52:82:11:22:33")
        stored = [x.mac for x in lan.list_order(self.store.load())]
        self.assertEqual(stored, after)             # 已寫入資料庫
        self.assertFalse(d.is_dirty())

    def test_move_unsaved_classified_device(self):  # DSC-17：類型尚未儲存也可調整順序
        from flatness import lan
        d = self.dlg
        d.select("00:01:FC:12:39:A0")
        d.status_box.setCurrentIndex(1)            # 設為使用中（尚未儲存）
        self.assertTrue(d.btn_up.isEnabled())
        d.btn_up.click()
        self.assertEqual(by_mac(self.store.load())["00:01:FC:12:39:A0"].status, "unclassified")  # 類型未寫入
        self.assertTrue(d.is_dirty())
        self.assertEqual(d.work["00:01:FC:12:39:A0"].status, "dl_en1_live")

    def test_move_disabled_when_db_down(self):
        from flatness.ui.settings_dialog import SettingsDialog
        self.store.available = False
        d = SettingsDialog(self.be)
        d.enter_edit()
        d.select(self.list_macs(d)[2])
        self.assertFalse(d.btn_up.isEnabled() or d.btn_down.isEnabled())
        self.assertIn("無法連線資料庫", d.move_hint.text())

    def test_maint_stays_on_screen_not_measured(self):  # DSC-15-G1
        d = self.dlg
        d.select("00:01:FC:DE:3A:76")
        d.status_box.setCurrentIndex(2)  # 維修中
        self.save()
        result, preview = self.saved[0]
        self.assertEqual([x["key"] for x in result.definition["dl_en1"]], ["row-1", "row-3"])
        self.assertIn("00:01:fc:de:3a:76", Path(self.tmp.name, "dl-en1.hosts").read_text())
        self.assertEqual((len(preview.paused_points), preview.removed_points), (4, []))
        self.assertEqual([(x["key"], x.get("maint", False)) for x in result.layout["dl_en1"]],
                         [("row-1", False), ("row-2", True), ("row-3", False)])  # 主畫面保留中排

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


class ScreenFitTest(UiBase):
    """UI-11：主畫面依螢幕自動縮放，至少 4 排不需捲動即可看到全部探頭。"""

    def window(self, n, probes=4, size=(1920, 1080)):
        from helpers import dl
        from flatness.ui.main_window import MainWindow
        devs = [dl(f"00:01:FC:DE:3A:{0x70 + i:02X}", f"row-{i + 1}", f"第{i + 1}排", f"192.168.10.{11 + i}", i + 1,
                   max_probes=probes, probes=[{"id": j + 1, "description": f"點{j + 1}"} for j in range(probes)])
                for i in range(n)]
        be = self.make_backend(devices=devs)
        win = MainWindow(be, lambda defn: None)
        self.addCleanup(win.deleteLater)
        win.resize(*size)
        win.show()
        pump(self.app, 0.1)
        return win

    def bottom_of(self, win, row):
        vp = win.rows_area.viewport()
        return row.mapTo(vp, row.rect().bottomLeft()).y()

    def test_four_rows_fit_1080p(self):
        win = self.window(4)
        self.assertLess(win.scale_k, 1.0)                                # 已縮小
        self.assertEqual(win.rows_area.verticalScrollBar().maximum(), 0)  # 不需捲動
        self.assertLessEqual(self.bottom_of(win, win.rows[3]), win.rows_area.viewport().height())

    def test_eight_rows_show_at_least_four(self):
        win = self.window(8, probes=6)
        self.assertLessEqual(self.bottom_of(win, win.rows[3]), win.rows_area.viewport().height())

    def test_few_rows_stay_full_size_and_scale_with_window(self):
        win = self.window(2)
        win4 = self.window(4)
        k_big = win4.scale_k
        self.assertGreater(win.scale_k, k_big)                            # 排少時方塊較大
        win4.resize(1600, 900)
        pump(self.app, 0.1)
        self.assertLess(win4.scale_k, k_big)                              # 畫面變小，方塊跟著縮小

    def test_tile_height_same_for_every_result(self):  # 結果改變時排不跳動
        from flatness.measure import ERR, HI, OK
        win = self.window(4)
        t = next(iter(win.rows[0].tiles.values()))
        heights = set()
        for args in ((OK, 12.5), (HI, 12.6, "超出上限 0.050"), (ERR, None, "探頭無回應", "探頭無回應", True)):
            t.set_result(*args)
            pump(self.app, 0.02)
            heights.add(t.sizeHint().height())
        t.set_blank()
        heights.add(t.sizeHint().height())
        self.assertEqual(len(heights), 1, heights)


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
        self.assertEqual([r.dev["key"] for r in self.win.rows], ["row-1", "row-2", "row-3"])
        self.assertEqual(sum(len(r.tiles) for r in self.win.rows), 12)

    def test_ip_mismatch_highlights_row_and_asks_for_reset(self):  # DSC-20
        from flatness.store import SeenEvent
        w, row = self.win, self.win.rows[0]
        mac, want = row.dev["mac"], row.dev["ipv4"]
        w._on_seen([SeenEvent(mac.upper(), "ARP", datetime.now(), ip=want)])     # 相同：不提示
        self.assertIsNone(w.flags["ip"])
        self.assertIsNone(row.seen_ip)
        w._on_seen([SeenEvent(mac.upper(), "ARP", datetime.now(), ip="192.168.10.99")])
        self.assertEqual(row.seen_ip, "192.168.10.99")
        self.assertIn("IP 不符", row.unit_text.text())
        self.assertIn("RST 鍵 3 秒", w.flags["ip"])
        self.assertIn("192.168.10.99", w.flags["ip"])
        self.assertIsNone(w.rows[1].seen_ip)                                       # 其他排不受影響
        w._on_seen([SeenEvent(mac.upper(), "ARP", datetime.now(), ip="10.0.0.5")])  # 不同網段
        self.assertIn("10.0.0.5（IP 不在設備網段 192.168.10.0/24）", w.flags["ip"])
        w._on_seen([SeenEvent(mac.upper(), "ARP", datetime.now(), ip=want)])     # 重設後取得設定的 IP
        self.assertIsNone(w.flags["ip"])
        self.assertNotIn("IP 不符", row.unit_text.text())

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
        st.detect = lambda: [measure.DeviceStatus("row-1"), measure.DeviceStatus("row-2", reachable=False),
                             measure.DeviceStatus("row-3")]
        w.detect()
        self.wait_state("error")
        self.assertIn("中排 DL-EN1 偵測不到", w.banner.say.text())
        self.assertIn("偵測不到", w.rows[1].unit_text.text())

    def test_missing_standard_is_device_error(self):  # DEF-09
        self.be.cfg.standards.pop("row-3")
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
        self.assertEqual([(r.dev["key"], r.maint) for r in w.rows],
                         [("row-1", False), ("row-2", True), ("row-3", False)])
        self.assertEqual([r.dev["key"] for r in w.live_rows], ["row-1", "row-3"])
        self.assertEqual([d["key"] for d in self.stations[-1].definition["dl_en1"]], ["row-1", "row-3"])
        self.wait_state("idle")
        self.assertEqual(w.detect_count, 2)

    def test_maint_row_not_measured(self):  # DSC-15
        from flatness import lan
        old = self.store.load()
        new = [x.copy() for x in old]
        lan.set_status(new, "00:01:FC:DE:3A:76", lan.MAINT, NET)
        result = self.be.apply(old, new)
        w = self.win
        w.rebuild(result.layout)
        self.assertEqual(w.rows[1].unit_text.text(), "DL-EN1 #2\n維修中")
        self.assertEqual(w.rows[1].tiles, {})
        w.detect()
        self.wait_state("idle")
        self.assertIn("2 台 DL-EN1、8 個探頭正常", w.sum_text.text())
        self.stations[-1].force = "pass"
        w.next_piece()
        self.wait_state("pass")
        self.assertEqual({p.key for p in w.result.points}, {"row-1", "row-3"})
        self.assertIn("8 個量測點都在標準範圍內", w.banner.say.text())

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

    def _centered(self, dlg):
        host = dlg.parentWidget()
        self.assertIs(host, self.win.backdrop)
        g = dlg.geometry()
        self.assertLessEqual(abs(g.center().x() - host.width() / 2), 1)
        self.assertLessEqual(abs(g.center().y() - host.height() / 2), 1)
        self.assertTrue(host.rect().contains(g))

    def test_settings_dialog_centered(self):  # UI-09、UI-10
        from PySide6.QtCore import QTimer
        from flatness.ui.settings_dialog import SettingsDialog
        w = self.win
        w.show()
        dlg = SettingsDialog(self.be, w)
        checks = []

        def check():
            self._centered(dlg)                 # 步驟一（密碼）
            checks.append(dlg.size().width())
            dlg.enter_edit()                    # 步驟二：對話框變大後仍置中
            pump(self.app, 0.05)
            self._centered(dlg)
            self.assertEqual(dlg.size(), w.backdrop.size())  # UI-10：編輯步驟佔滿主畫面
            checks.append(dlg.size().width())
            w.resize(1400, 900)                 # 主畫面改變大小後仍佔滿、置中
            pump(self.app, 0.05)
            self._centered(dlg)
            self.assertEqual(dlg.size(), w.backdrop.size())
            checks.append(dlg.size().width())
            dlg.done(0)
        QTimer.singleShot(0, check)
        w._modal(dlg)
        self.assertEqual(len(checks), 3)
        self.assertLess(checks[0], checks[1])
        self.assertFalse(w.backdrop.isVisible())

    def test_message_box_centered(self):  # UI-09：設定頁的確認、警告訊息框
        from PySide6.QtCore import QTimer
        from flatness.ui.settings_dialog import SettingsDialog
        from flatness.ui.widgets import MessageDialog
        w = self.win
        w.show()
        dlg = SettingsDialog(self.be, w)
        answers = []

        def in_settings():
            dlg.enter_edit()
            dlg.select("00:01:FC:DE:3A:76")
            dlg.name_edit.setText("中段")
            dlg.name_edit.textEdited.emit("中段")

            def in_message():
                box = next(x for x in w.findChildren(MessageDialog) if x.isVisible())
                host = box.parentWidget()
                g = box.geometry()
                answers.append(abs(g.center().x() - host.width() / 2) <= 1 and
                               abs(g.center().y() - host.height() / 2) <= 1)
                self.assertIn("有尚未儲存的變更", box.findChildren(type(dlg.info))[1].text())
                box.buttons[1].click()                 # 確定 → 放棄變更並關閉
            QTimer.singleShot(0, in_message)
            dlg.reject()
        QTimer.singleShot(0, in_settings)
        w._modal(dlg)
        self.assertEqual(answers, [True])
        self.assertFalse(dlg.isVisible())

    def test_export_dialog_centered(self):  # UI-09
        from PySide6.QtCore import QTimer
        from flatness.ui.main_window import ExportDialog
        w = self.win
        w.show()
        dlg = ExportDialog(w.sink, w)
        ok = []

        def check():
            self._centered(dlg)
            ok.append(True)
            dlg.done(0)
        QTimer.singleShot(0, check)
        w._modal(dlg)
        self.assertEqual(ok, [True])

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
