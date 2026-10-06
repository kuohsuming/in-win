"""設備設定畫面（EDT-01～EDT-03）：以 offscreen 方式操作畫面。"""

import ipaddress
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

try:
    from PySide6.QtWidgets import QApplication
except ImportError:  # 沒有 PySide6 的環境略過
    QApplication = None

NET = ipaddress.IPv4Interface("192.168.10.1/24")


@unittest.skipIf(QApplication is None, "需要 PySide6")
class DeviceEditorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        from flatness import bootp, definition
        from flatness.ui.device_editor import DeviceEditor

        self.tmp = tempfile.TemporaryDirectory()
        self.def_path = Path(self.tmp.name, "dl-en1.json")
        self.hosts = Path(self.tmp.name, "bootp", "dl-en1.hosts")
        sample = json.loads((ROOT / "installer" / "dl-en1.json").read_text(encoding="utf-8"))
        self.def_path.write_text(definition.dumps(sample), encoding="utf-8")
        bootp.apply(sample["dl_en1"], self.hosts, restart_cmd=None)

        self.editor = DeviceEditor(self.def_path, self.hosts, NET, restart_cmd=None)
        self.messages = []
        self.confirmed = []
        self.editor._info = self.messages.append
        self.editor._warn = self.messages.append
        self.editor._ask = lambda text: True
        self.editor._confirm = lambda diff: self.confirmed.append(diff) or True

    def tearDown(self):
        self.editor.deleteLater()
        self.tmp.cleanup()

    def fill(self, **fields):
        e = self.editor
        widgets = {"key": e.key_edit, "name": e.name_edit, "mac": e.mac_edit, "ipv4": e.ip_edit,
                   "port": e.port_edit}
        for name, value in fields.items():
            widgets[name].setText(value)
            widgets[name].textEdited.emit(value)

    def test_loads_existing_list(self):
        self.assertEqual(self.editor.device_table.rowCount(), 1)
        self.assertEqual(self.editor.mac_edit.text(), "00:01:FC:DE:3A:75")
        self.assertFalse(self.editor.is_dirty())

    def test_add_device_and_apply_updates_files(self):
        self.editor.btn_add.click()
        self.fill(key="middle", name="中排", mac="00:01:fc:de:3a:76")
        self.assertTrue(self.editor.is_dirty())
        self.assertEqual(self.editor.ip_edit.text(), "192.168.10.12")  # 自動帶入下一個可用 IP
        self.editor.btn_apply.click()

        self.assertEqual(len(self.confirmed), 1)
        self.assertEqual([d["key"] for d in self.confirmed[0].added], ["middle"])
        saved = json.loads(self.def_path.read_text(encoding="utf-8"))
        self.assertEqual([d["key"] for d in saved["dl_en1"]], ["front", "middle"])
        self.assertEqual(saved["dl_en1"][1]["mac"], "00:01:FC:DE:3A:76")  # 統一大寫
        self.assertIn("00:01:fc:de:3a:76,192.168.10.12,middle", self.hosts.read_text())
        self.assertFalse(self.editor.is_dirty())
        self.assertIn("重新上電", self.messages[-1])

    def test_errors_block_apply_and_list_location(self):
        before = self.def_path.read_text(encoding="utf-8")
        self.editor.btn_add.click()
        self.fill(key="Bad Key", name="", mac="00:01:FC:DE:3A:75")  # 格式錯、名稱空白、MAC 重複
        self.editor.btn_apply.click()

        self.assertEqual(self.confirmed, [])
        self.assertEqual(self.def_path.read_text(encoding="utf-8"), before)
        errors = [self.editor.error_list.item(i).text() for i in range(self.editor.error_list.count())]
        self.assertTrue(any("識別碼" in t for t in errors), errors)
        self.assertTrue(any("排名稱" in t for t in errors), errors)
        self.assertTrue(any("MAC" in t and "重複" in t for t in errors), errors)

    def test_delete_last_device_is_rejected_by_validation(self):
        self.editor.btn_delete.click()
        self.assertEqual(self.editor.device_table.rowCount(), 0)
        self.editor.btn_apply.click()
        self.assertEqual(self.confirmed, [])  # 至少要有 1 台（3.7.1）

    def test_edit_probe_name_and_cancel_keeps_file(self):
        before = self.def_path.read_text(encoding="utf-8")
        self.editor.probe_table.item(1, 1).setText("中左")
        self.assertTrue(self.editor.is_dirty())
        self.editor.reject()  # _ask 回答「是」：放棄變更
        self.assertEqual(self.def_path.read_text(encoding="utf-8"), before)

    def test_restart_failure_is_reported_and_rolled_back(self):
        before = self.def_path.read_text(encoding="utf-8")
        self.editor.restart_cmd = ["false"]
        self.fill(name="前段")
        self.editor.btn_apply.click()
        self.assertIn("已還原", self.messages[-1])
        self.assertEqual(self.def_path.read_text(encoding="utf-8"), before)
        self.assertTrue(self.editor.is_dirty())


if __name__ == "__main__":
    unittest.main()
