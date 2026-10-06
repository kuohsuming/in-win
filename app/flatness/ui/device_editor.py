"""設備設定：在畫面上新增、刪除、修改 DL-EN1 與探頭（EDT-01～EDT-03）。

編輯內容在按「套用」前不寫入任何檔案；套用時驗證 → 差異預覽 → 確認 → 寫入定義檔並更新
dnsmasq BOOTP 主機對應（definition.apply）。
"""

from __future__ import annotations

import copy
import html
import ipaddress
import re
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QIntValidator
from PySide6.QtWidgets import (
    QAbstractItemView, QDialog, QDialogButtonBox, QFormLayout, QGroupBox, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QListWidget, QListWidgetItem, QMessageBox, QPushButton,
    QSpinBox, QSplitter, QTableWidget, QTableWidgetItem, QTextBrowser, QVBoxLayout, QWidget,
)

from .. import bootp, definition

DEFAULT_PROBES = ["左", "左中", "右中", "右"]
FIELD_NAMES = {
    "key": "識別碼", "name": "排名稱", "mac": "MAC", "ipv4": "IPv4", "port": "埠",
    "max_probes": "最多探頭數", "probes": "探頭", "id": "探頭 ID", "description": "位置名稱",
}
_WHERE_RE = re.compile(r"^dl_en1\[(\d+)\](?:\.(\w+))?(?:\[(\d+)\](?:\.(\w+))?)?$")


class DeviceEditor(QDialog):
    """DL-EN1 清單維護畫面。applied 訊號在套用成功後送出新的定義。"""

    applied = Signal(dict)

    def __init__(self, def_path: Path, hosts_path: Path, equip_net: ipaddress.IPv4Interface,
                 restart_cmd=bootp.RESTART_CMD, parent=None):
        super().__init__(parent)
        self.def_path = Path(def_path)
        self.hosts_path = Path(hosts_path)
        self.equip_net = equip_net
        self.restart_cmd = restart_cmd
        self._loading = False

        self.setWindowTitle("設備設定 — DL-EN1 清單")
        self.resize(1100, 680)
        self._build()

        try:
            self.saved = definition.load_definition(self.def_path)
        except bootp.DefinitionError as exc:
            self._warn("定義檔無法讀取，將從空白清單開始。\n\n" + str(exc))
            self.saved = definition.empty_definition()
        self.devices: list[dict] = copy.deepcopy(self.saved.get("dl_en1", []))
        self._refresh_device_table(select=0)

    # ------------------------------------------------------------------ 畫面
    def _build(self):
        # 左：DL-EN1 清單
        self.device_table = QTableWidget(0, 5)
        self.device_table.setHorizontalHeaderLabels(["排名稱", "識別碼", "MAC", "IPv4", "探頭"])
        self.device_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.device_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.device_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.device_table.verticalHeader().setVisible(False)
        self.device_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.device_table.horizontalHeader().setStretchLastSection(True)
        self.device_table.currentCellChanged.connect(lambda row, *_: self._show_device(row))

        self.btn_add = QPushButton("新增 DL-EN1")
        self.btn_delete = QPushButton("刪除")
        self.btn_up = QPushButton("上移")
        self.btn_down = QPushButton("下移")
        self.btn_add.clicked.connect(self._add_device)
        self.btn_delete.clicked.connect(self._delete_device)
        self.btn_up.clicked.connect(lambda: self._move_device(-1))
        self.btn_down.clicked.connect(lambda: self._move_device(1))
        row_buttons = QHBoxLayout()
        for b in (self.btn_add, self.btn_delete, self.btn_up, self.btn_down):
            row_buttons.addWidget(b)
        row_buttons.addStretch()

        left = QGroupBox("DL-EN1 清單（畫面由上而下依此順序排列）")
        lv = QVBoxLayout(left)
        lv.addWidget(self.device_table)
        lv.addLayout(row_buttons)

        # 右：選取的 DL-EN1 內容
        self.key_edit = QLineEdit(placeholderText="小寫英文、數字、連字號，例：front")
        self.name_edit = QLineEdit(placeholderText="畫面顯示的排名稱，例：前排")
        self.mac_edit = QLineEdit(placeholderText="DL-EN1 本體上的 MAC，例：00:01:FC:DE:3A:75")
        self.ip_edit = QLineEdit(placeholderText=f"設備網段 {self.equip_net.network} 內")
        self.port_edit = QLineEdit(placeholderText=f"{definition.DEFAULT_PORT}（未填寫時）")
        self.port_edit.setValidator(QIntValidator(1, 65535, self))
        self.max_spin = QSpinBox(minimum=1, maximum=15)
        for w in (self.key_edit, self.name_edit, self.mac_edit, self.ip_edit, self.port_edit):
            w.textEdited.connect(self._on_field_changed)
        self.max_spin.valueChanged.connect(self._on_field_changed)

        form = QFormLayout()
        form.addRow("識別碼 key", self.key_edit)
        form.addRow("排名稱 name", self.name_edit)
        form.addRow("MAC", self.mac_edit)
        form.addRow("IPv4", self.ip_edit)
        form.addRow("TCP 埠 port", self.port_edit)
        form.addRow("最多探頭數", self.max_spin)

        self.probe_table = QTableWidget(0, 2)
        self.probe_table.setHorizontalHeaderLabels(["探頭 ID", "位置名稱"])
        self.probe_table.horizontalHeaderItem(0).setToolTip("等於放大器 ID，依實體串接順序由 1 起算")
        self.probe_table.setColumnWidth(0, 110)
        self.probe_table.verticalHeader().setVisible(False)
        self.probe_table.horizontalHeader().setStretchLastSection(True)
        self.probe_table.itemChanged.connect(self._on_probe_changed)
        self.btn_add_probe = QPushButton("新增探頭")
        self.btn_delete_probe = QPushButton("刪除探頭")
        self.btn_add_probe.clicked.connect(self._add_probe)
        self.btn_delete_probe.clicked.connect(self._delete_probe)
        probe_buttons = QHBoxLayout()
        probe_buttons.addWidget(self.btn_add_probe)
        probe_buttons.addWidget(self.btn_delete_probe)
        probe_buttons.addStretch()

        self.detail = QGroupBox("DL-EN1 內容")
        rv = QVBoxLayout(self.detail)
        rv.addLayout(form)
        rv.addWidget(QLabel("已安裝的探頭（畫面由左至右依 ID 排列）"))
        rv.addWidget(self.probe_table)
        rv.addLayout(probe_buttons)

        splitter = QSplitter()
        splitter.addWidget(left)
        splitter.addWidget(self.detail)
        splitter.setSizes([560, 540])

        # 下：錯誤清單與按鍵
        self.error_list = QListWidget()
        self.error_list.setMaximumHeight(130)
        self.error_list.setVisible(False)
        self.error_list.itemClicked.connect(self._jump_to_error)

        self.btn_check = QPushButton("檢查")
        self.btn_apply = QPushButton("套用…")
        self.btn_apply.setDefault(True)
        self.btn_close = QPushButton("關閉")
        self.btn_check.clicked.connect(self._check)
        self.btn_apply.clicked.connect(self._apply)
        self.btn_close.clicked.connect(self.reject)
        bottom = QHBoxLayout()
        self.status = QLabel()
        bottom.addWidget(self.status, 1)
        for b in (self.btn_check, self.btn_apply, self.btn_close):
            bottom.addWidget(b)

        layout = QVBoxLayout(self)
        layout.addWidget(splitter, 1)
        layout.addWidget(self.error_list)
        layout.addLayout(bottom)

    # ------------------------------------------------------------------ 清單
    def _current(self) -> dict | None:
        row = self.device_table.currentRow()
        return self.devices[row] if 0 <= row < len(self.devices) else None

    def _device_cells(self, d: dict) -> list[str]:
        ids = ", ".join(str(p.get("id", "")) for p in d.get("probes", []))
        return [d.get("name", ""), d.get("key", ""), d.get("mac", ""), d.get("ipv4", ""),
                f"{len(d.get('probes', []))}/{d.get('max_probes', '')}  ({ids})"]

    def _refresh_device_table(self, select: int | None = None):
        self.device_table.blockSignals(True)
        self.device_table.setRowCount(len(self.devices))
        for r, d in enumerate(self.devices):
            for c, text in enumerate(self._device_cells(d)):
                self.device_table.setItem(r, c, QTableWidgetItem(text))
        self.device_table.blockSignals(False)
        if select is not None and self.devices:
            select = max(0, min(select, len(self.devices) - 1))
            self.device_table.setCurrentCell(select, 0)
        self._show_device(self.device_table.currentRow() if self.devices else -1)
        self._update_status()

    def _refresh_current_row(self):
        row = self.device_table.currentRow()
        if row < 0:
            return
        for c, text in enumerate(self._device_cells(self.devices[row])):
            self.device_table.item(row, c).setText(text)
        self._update_status()

    def _update_status(self):
        dirty = self.is_dirty()
        self.status.setText("● 有尚未套用的變更" if dirty else "與目前使用中的定義檔相同")
        self.status.setStyleSheet("color:#b45309;font-weight:bold" if dirty else "color:#555")
        has = self._current() is not None
        self.btn_delete.setEnabled(has)
        row = self.device_table.currentRow()
        self.btn_up.setEnabled(has and row > 0)
        self.btn_down.setEnabled(has and row < len(self.devices) - 1)
        self.btn_add.setEnabled(len(self.devices) < 8)

    def _next_ip(self) -> str:
        used = {d.get("ipv4") for d in self.devices}
        for host in self.equip_net.network.hosts():
            if int(host) & 0xFF >= 11 and host != self.equip_net.ip and str(host) not in used:
                return str(host)
        return ""

    def _add_device(self):
        used = {d.get("key") for d in self.devices}
        n = len(self.devices) + 1
        while f"dl-en1-{n}" in used:
            n += 1
        self.devices.append({
            "key": f"dl-en1-{n}", "name": "", "mac": "", "ipv4": self._next_ip(),
            "max_probes": 4,
            "probes": [{"id": i + 1, "description": d} for i, d in enumerate(DEFAULT_PROBES)],
        })
        self._refresh_device_table(select=len(self.devices) - 1)
        self.name_edit.setFocus()

    def _delete_device(self):
        d = self._current()
        if d is None:
            return
        if not self._ask(f"確定刪除 {definition.label(d)}？\n（按「套用」前不會寫入檔案）"):
            return
        row = self.device_table.currentRow()
        del self.devices[row]
        self._refresh_device_table(select=row)

    def _move_device(self, step: int):
        row = self.device_table.currentRow()
        dst = row + step
        if not (0 <= row < len(self.devices) and 0 <= dst < len(self.devices)):
            return
        self.devices[row], self.devices[dst] = self.devices[dst], self.devices[row]
        self._refresh_device_table(select=dst)

    # ------------------------------------------------------------------ 內容
    def _show_device(self, row: int):
        d = self.devices[row] if 0 <= row < len(self.devices) else None
        self.detail.setEnabled(d is not None)
        self._loading = True
        self.key_edit.setText(d.get("key", "") if d else "")
        self.name_edit.setText(d.get("name", "") if d else "")
        self.mac_edit.setText(d.get("mac", "") if d else "")
        self.ip_edit.setText(d.get("ipv4", "") if d else "")
        self.port_edit.setText(str(d["port"]) if d and "port" in d else "")
        self.max_spin.setValue(d.get("max_probes", 4) if d else 4)
        self.probe_table.blockSignals(True)
        probes = d.get("probes", []) if d else []
        self.probe_table.setRowCount(len(probes))
        for r, p in enumerate(probes):
            self.probe_table.setItem(r, 0, QTableWidgetItem(str(p.get("id", ""))))
            self.probe_table.setItem(r, 1, QTableWidgetItem(p.get("description", "")))
        self.probe_table.blockSignals(False)
        self._loading = False
        self._update_status()

    def _on_field_changed(self, *_):
        d = self._current()
        if d is None or self._loading:
            return
        d["key"] = self.key_edit.text().strip()
        d["name"] = self.name_edit.text().strip()
        d["mac"] = self.mac_edit.text().strip().upper()
        d["ipv4"] = self.ip_edit.text().strip()
        port = self.port_edit.text().strip()
        if port:
            d["port"] = int(port)
        else:
            d.pop("port", None)
        d["max_probes"] = self.max_spin.value()
        self._normalize_order(d)
        self._refresh_current_row()

    @staticmethod
    def _normalize_order(d: dict):
        """寫出的 JSON 欄位順序與規格範例一致。"""
        order = ["key", "name", "mac", "ipv4", "port", "max_probes", "probes"]
        items = {k: d[k] for k in order if k in d}
        d.clear()
        d.update(items)

    def _on_probe_changed(self, *_):
        d = self._current()
        if d is None or self._loading:
            return
        probes = []
        for r in range(self.probe_table.rowCount()):
            id_text = (self.probe_table.item(r, 0).text() if self.probe_table.item(r, 0) else "").strip()
            desc = (self.probe_table.item(r, 1).text() if self.probe_table.item(r, 1) else "").strip()
            probes.append({"id": int(id_text) if id_text.isdigit() else id_text, "description": desc})
        d["probes"] = probes
        self._refresh_current_row()

    def _add_probe(self):
        d = self._current()
        if d is None:
            return
        used = {p.get("id") for p in d["probes"]}
        free = [i for i in range(1, d["max_probes"] + 1) if i not in used]
        if not free:
            self._warn(f"已達最多探頭數 {d['max_probes']}；請先調高「最多探頭數」。")
            return
        d["probes"].append({"id": free[0], "description": ""})
        d["probes"].sort(key=lambda p: p["id"] if isinstance(p.get("id"), int) else 99)
        self._show_device(self.device_table.currentRow())
        self._refresh_current_row()

    def _delete_probe(self):
        d = self._current()
        r = self.probe_table.currentRow()
        if d is None or not 0 <= r < len(d["probes"]):
            return
        del d["probes"][r]
        self._show_device(self.device_table.currentRow())
        self._refresh_current_row()

    # ------------------------------------------------------------------ 檢查與套用
    def current_definition(self) -> dict:
        return {"version": 1, "dl_en1": copy.deepcopy(self.devices)}

    def is_dirty(self) -> bool:
        return self.devices != self.saved.get("dl_en1", [])

    def _describe_where(self, where: str) -> tuple[str, int | None]:
        m = _WHERE_RE.match(where)
        if not m:
            return where, None
        i = int(m.group(1))
        dev = self.devices[i] if i < len(self.devices) else {}
        who = dev.get("name") or dev.get("key") or f"第 {i + 1} 台"
        parts = [who]
        if m.group(2):
            parts.append(FIELD_NAMES.get(m.group(2), m.group(2)))
        if m.group(3) is not None:
            parts.append(f"第 {int(m.group(3)) + 1} 個探頭")
            if m.group(4):
                parts.append(FIELD_NAMES.get(m.group(4), m.group(4)))
        return " › ".join(parts), i

    def _show_errors(self, errors) -> None:
        self.error_list.clear()
        self.error_list.setVisible(bool(errors))
        for where, why in errors:
            text, idx = self._describe_where(where)
            item = QListWidgetItem(f"✘ {text}：{why}")
            item.setForeground(QColor("#b91c1c"))
            item.setData(Qt.UserRole, idx)
            self.error_list.addItem(item)

    def _jump_to_error(self, item: QListWidgetItem):
        idx = item.data(Qt.UserRole)
        if idx is not None and idx < len(self.devices):
            self.device_table.setCurrentCell(idx, 0)

    def _check(self) -> bool:
        errors = definition.validate(self.current_definition(), self.equip_net)
        self._show_errors(errors)
        if not errors:
            self.status.setText("✔ 檢查通過")
            self.status.setStyleSheet("color:#15803d;font-weight:bold")
        return not errors

    def _apply(self):
        if not self._check():
            self._warn("有錯誤，未套用。請依下方清單修正。")
            return
        new = self.current_definition()
        changes = definition.diff(self.saved.get("dl_en1", []), new["dl_en1"])
        if changes.empty:
            self._info("沒有變更。")
            return
        if not self._confirm(changes):
            return
        try:
            definition.apply(new, self.def_path, self.hosts_path, self.equip_net, self.restart_cmd)
        except Exception as exc:  # 已在 definition.apply 內還原
            self._warn(f"套用失敗，已還原為套用前的設定。\n\n原因：{exc}")
            return
        self.saved = new
        self._update_status()
        self.applied.emit(new)
        msg = "已套用：定義檔與 BOOTP 主機對應已更新，dnsmasq 已重新啟動。"
        if changes.power_cycle:
            msg += "\n\n請將下列 DL-EN1 重新上電，以取得新的 IP：\n" + "\n".join(
                f"  • {definition.label(d)}  {d['mac']} → {d['ipv4']}" for d in changes.power_cycle)
        self._info(msg)

    # ------------------------------------------------------------------ 對話框（測試時可替換）
    def _confirm(self, changes: definition.Diff) -> bool:
        return PreviewDialog(changes, self).exec() == QDialog.Accepted

    def _ask(self, text: str) -> bool:
        return QMessageBox.question(self, "設備設定", text) == QMessageBox.Yes

    def _info(self, text: str):
        QMessageBox.information(self, "設備設定", text)

    def _warn(self, text: str):
        QMessageBox.warning(self, "設備設定", text)

    def reject(self):
        if self.is_dirty() and not self._ask("有尚未套用的變更，確定放棄並關閉？"):
            return
        super().reject()


class PreviewDialog(QDialog):
    """套用前的差異預覽（UPL-05）：MAC / IP 變更醒目標示，並列出影響。"""

    def __init__(self, changes: definition.Diff, parent=None):
        super().__init__(parent)
        self.setWindowTitle("確認套用 — 差異預覽")
        self.resize(640, 520)
        view = QTextBrowser()
        view.setHtml(self.render(changes))
        buttons = QDialogButtonBox()
        buttons.addButton("套用", QDialogButtonBox.AcceptRole)
        buttons.addButton("取消", QDialogButtonBox.RejectRole)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout = QVBoxLayout(self)
        layout.addWidget(view)
        layout.addWidget(buttons)

    @staticmethod
    def render(c: definition.Diff) -> str:
        e = html.escape
        out = []
        if c.added:
            out.append("<h3 style='color:#15803d'>新增</h3><ul>")
            out += [f"<li>{e(definition.label(d))}　{e(d['mac'])} → {e(d['ipv4'])}，"
                    f"探頭 {len(d['probes'])} 個</li>" for d in c.added]
            out.append("</ul>")
        if c.removed:
            out.append("<h3 style='color:#b91c1c'>移除</h3><ul>")
            out += [f"<li>{e(definition.label(d))}　{e(d['mac'])}</li>" for d in c.removed]
            out.append("</ul>")
        if c.changed:
            out.append("<h3 style='color:#b45309'>變更</h3>")
            for d, items in c.changed:
                out.append(f"<p><b>{e(definition.label(d))}</b></p><ul>")
                for ch in items:
                    text = e(ch.text)
                    out.append(f"<li><span style='color:#b91c1c;font-weight:bold'>⚠ {text}</span></li>"
                               if ch.important else f"<li>{text}</li>")
                out.append("</ul>")
        if c.reordered:
            out.append("<p>畫面排列順序已調整。</p>")

        out.append("<h3>影響</h3><ul>")
        if c.power_cycle:
            out.append("<li><b>需重新上電的 DL-EN1：</b>" + "、".join(
                e(definition.label(d)) for d in c.power_cycle) + "</li>")
        if c.removed_points:
            out.append("<li><b>將從畫面移除的量測點：</b>" + "、".join(map(e, c.removed_points)) + "</li>")
        if not (c.power_cycle or c.removed_points):
            out.append("<li>無需重新上電，無量測點被移除。</li>")
        out.append("<li>套用後會更新 BOOTP 主機對應並重新啟動 dnsmasq。</li></ul>")
        return "".join(out)
