"""板子尺寸設定小視窗（P3D-10）：長、寬、高（mm），嵌入主畫面中央（UI-09）。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout

from ..ui.theme import C
from . import config
from .config import PlateConfig, fmt


class PlateDialog(QDialog):
    FIELDS = ("length", "width", "height")
    HINT = {"length": "左右（作業員看過去）", "width": "前到後", "height": "板厚，圖上為示意"}

    def __init__(self, plate: PlateConfig, parent=None):
        super().__init__(parent, Qt.Dialog | Qt.FramelessWindowHint)
        self.result_plate: PlateConfig | None = None
        self.setObjectName("platedlg")
        self.setStyleSheet(f"#platedlg {{ background:{C['panel']}; border:1px solid {C['line']}; border-radius:8px; }}")
        self.setFixedWidth(480)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(22, 20, 22, 20)
        lay.setSpacing(12)
        title = QLabel("板子尺寸")
        title.setObjectName("h1")
        lay.addWidget(title)
        note = QLabel("只影響 3D 繪圖，不影響判定。探頭在板子下方，位置為設備設定中每個探頭的第幾排、第幾點（5 × 5 格）。")
        note.setObjectName("note")
        note.setWordWrap(True)
        lay.addWidget(note)
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)
        self.edits: dict[str, QLineEdit] = {}
        for r, f in enumerate(self.FIELDS):
            lo, hi = config.LIMITS[f]
            lb = QLabel(config.LABEL[f])
            lb.setObjectName("label")
            e = QLineEdit(fmt(getattr(plate, f)))
            e.setProperty("num", True)
            e.setPlaceholderText(f"{fmt(lo)}～{fmt(hi)}")
            e.textChanged.connect(self._update)
            self.edits[f] = e
            unit = QLabel(f"mm（{fmt(lo)}～{fmt(hi)}，{self.HINT[f]}）")
            unit.setObjectName("note")
            grid.addWidget(lb, r, 0)
            grid.addWidget(e, r, 1)
            grid.addWidget(unit, r, 2)
        grid.setColumnStretch(1, 1)
        lay.addLayout(grid)
        self.error = QLabel()
        self.error.setWordWrap(True)
        self.error.setStyleSheet(f"color:{C['ng']}; font-size:14px; font-weight:700;")
        lay.addWidget(self.error)
        row = QHBoxLayout()
        row.addStretch()
        cancel = QPushButton("取消")
        cancel.clicked.connect(self.reject)
        self.save = QPushButton("儲存")
        self.save.setProperty("kind", "primary")
        self.save.setDefault(True)
        self.save.clicked.connect(self._save)
        row.addWidget(cancel)
        row.addWidget(self.save)
        lay.addLayout(row)
        self._update()

    def values(self) -> tuple[dict, list[str]]:
        vals, errs = {}, []
        for f, e in self.edits.items():
            v, err = config.check(f, e.text())
            e.setProperty("error", bool(err))
            e.style().unpolish(e)
            e.style().polish(e)
            if err:
                errs.append(err)
            else:
                vals[f] = v
        return vals, errs

    def _update(self):
        _, errs = self.values()
        self.error.setText("、".join(errs))
        self.error.setVisible(bool(errs))
        self.save.setEnabled(not errs)

    def _save(self):
        vals, errs = self.values()
        if errs:
            return
        self.result_plate = PlateConfig(**vals)
        self.accept()
