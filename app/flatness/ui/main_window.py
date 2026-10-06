"""主畫面：頂端工具列 ＋ 依 DL-EN1 定義檔產生的量測點版面（DEF-04）。

量測流程（倒數、讀取、判定）尚未實作；目前版面只顯示每排與探頭位置，供設備設定套用後確認。
"""

from __future__ import annotations

import ipaddress
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QMainWindow, QToolBar, QVBoxLayout,
    QWidget,
)

from .. import bootp, definition
from .device_editor import DeviceEditor


class MainWindow(QMainWindow):
    def __init__(self, def_path: Path, hosts_path: Path, equip_net: ipaddress.IPv4Interface,
                 restart_cmd=bootp.RESTART_CMD):
        super().__init__()
        self.def_path, self.hosts_path = Path(def_path), Path(hosts_path)
        self.equip_net, self.restart_cmd = equip_net, restart_cmd
        self.setWindowTitle("表面平整檢查系統")

        toolbar = QToolBar("工具列", movable=False)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.addToolBar(toolbar)
        self.device_action = QAction("設備設定", self)
        self.device_action.triggered.connect(self.open_device_editor)
        toolbar.addAction(self.device_action)

        self.board = QWidget()
        self.setCentralWidget(self.board)
        self.reload_layout()

    def open_device_editor(self):
        editor = DeviceEditor(self.def_path, self.hosts_path, self.equip_net, self.restart_cmd, self)
        editor.applied.connect(lambda _: self.reload_layout())  # UPL-08：套用後重新載入畫面配置
        editor.exec()

    def reload_layout(self):
        try:
            devices = definition.load_definition(self.def_path).get("dl_en1", [])
            errors = definition.validate({"version": 1, "dl_en1": devices}, self.equip_net) if devices else []
        except bootp.DefinitionError as exc:
            devices, errors = [], exc.errors

        old = self.board.layout()
        if old is not None:
            QWidget().setLayout(old)  # 移交舊版面以便釋放
        layout = QVBoxLayout(self.board)

        if errors or not devices:
            msg = ("DL-EN1 定義檔有錯誤，請至「設備設定」修正：\n" + "\n".join(f"{w}: {r}" for w, r in errors)
                   if errors else "尚未設定 DL-EN1，請至「設備設定」新增。")
            hint = QLabel(msg, alignment=Qt.AlignCenter)
            hint.setStyleSheet("font-size:20px;color:#b91c1c")
            layout.addWidget(hint)
            return

        for d in devices:
            box = QGroupBox(f"{d['name']}　（{d['key']}  {d['ipv4']}:{d.get('port', definition.DEFAULT_PORT)}）")
            box.setStyleSheet("QGroupBox{font-size:18px;font-weight:bold}")
            row = QHBoxLayout(box)
            for p in sorted(d["probes"], key=lambda p: p["id"]):
                cell = QFrame(frameShape=QFrame.StyledPanel)
                grid = QGridLayout(cell)
                name = QLabel(p["description"], alignment=Qt.AlignCenter)
                name.setStyleSheet("font-size:22px;font-weight:bold")
                value = QLabel("—", alignment=Qt.AlignCenter)
                value.setStyleSheet("font-size:32px;color:#888")
                grid.addWidget(name, 0, 0)
                grid.addWidget(value, 1, 0)
                grid.addWidget(QLabel(f"ID {p['id']}", alignment=Qt.AlignCenter), 2, 0)
                row.addWidget(cell)
            layout.addWidget(box)
        layout.addStretch()
