"""3D 繪圖視窗（提案第 7 節、P3D-06～P3D-08）：嵌入主畫面中央的遮罩（UI-09），不另開系統視窗。

標題列（編號、結果）｜繪圖區＋資訊欄｜控制列（模式切換、◀ 30°、暫停／播放、30° ▶、旋轉角、關閉）。
開啟時「相對標準件」、旋轉角 0、自動播放；每 0.7 秒轉 30°。鍵盤：← → 轉動、空白鍵播放／暫停、M 切換模式、Esc 關閉。
"""

from __future__ import annotations

import html
import logging

from PySide6.QtCore import QRectF, Qt, QTimer
from PySide6.QtGui import QColor, QLinearGradient, QPainter
from PySide6.QtWidgets import (QBoxLayout, QButtonGroup, QDialog, QFrame, QHBoxLayout, QLabel, QMainWindow,
                               QPushButton, QSizePolicy, QVBoxLayout, QWidget)

from ..ui.theme import C, num_font, text_font
from ..ui.widgets import Backdrop, show_message
from .config import PlateConfig
from .model import DETRENDED, MODE_NAME, STANDARD, RefuseError, Snapshot, SurfaceModel, build_model, check
from .renderer import SHADE, STEP_DEG, STEP_MS
from .widget import Plate3DView

log = logging.getLogger(__name__)

RESULT = {"PASS": ("合格", "go-soft", "go"), "FAIL": ("不合格", "ng-soft", "ng"), "ERROR": ("設備異常", "ng-soft", "ng")}
SIDE_W = 260


def _label(text="", *, px=15, weight=400, color="ink", num=False, wrap=True) -> QLabel:
    lb = QLabel(text)
    lb.setFont(num_font(px, weight) if num else text_font(px, weight))
    lb.setStyleSheet(f"color:{C[color]}; background:transparent; border:none;")
    lb.setWordWrap(wrap)
    lb.setTextFormat(Qt.RichText)
    return lb


class Card(QFrame):
    def __init__(self, red=False):
        super().__init__()
        self.setObjectName("card3d")
        border = C["ng"] if red else C["line"]
        self.setStyleSheet(f"QFrame#card3d {{ background:{C['panel-2']}; border:{2 if red else 1}px solid {border};"
                           f" border-radius:6px; }}")
        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(12, 10, 12, 10)
        self.lay.setSpacing(4)


class Legend(QWidget):
    """明暗圖例：灰 RGB(140) 到白 RGB(228) 漸層條，刻度 −lim、0、+lim（mm）。"""

    def __init__(self):
        super().__init__()
        self.lim = 1.0
        self.setFixedHeight(34)

    def paintEvent(self, _):
        p = QPainter(self)
        bar = QRectF(0, 0, self.width(), 14)
        grad = QLinearGradient(bar.topLeft(), bar.topRight())
        grad.setColorAt(0, QColor(SHADE["lo"], SHADE["lo"], SHADE["lo"]))
        grad.setColorAt(1, QColor(SHADE["hi"], SHADE["hi"], SHADE["hi"]))
        p.fillRect(bar, grad)
        p.setPen(QColor(C["line"]))
        p.drawRect(bar.adjusted(0, 0, -1, -1))
        p.setFont(num_font(13, 500))
        p.setPen(QColor(C["ink-2"]))
        r = QRectF(0, 16, self.width(), 18)
        p.drawText(r, Qt.AlignLeft | Qt.AlignVCenter, f"{-self.lim:.3f}")
        p.drawText(r, Qt.AlignHCenter | Qt.AlignVCenter, "0")
        p.drawText(r, Qt.AlignRight | Qt.AlignVCenter, f"+{self.lim:.3f}")


class Plate3DDialog(QDialog):
    def __init__(self, snapshot: Snapshot, models: dict[str, SurfaceModel], parent=None):
        super().__init__(parent, Qt.Dialog | Qt.FramelessWindowHint)
        self.snapshot, self.models, self.mode = snapshot, models, STANDARD
        self.setObjectName("plate3d")
        self.setStyleSheet(f"#plate3d {{ background:{C['panel']}; border:1px solid {C['line']}; border-radius:8px; }}"
                           f" #plate3d QLabel, #side3d {{ background:transparent; }}")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(22, 16, 22, 16)
        lay.setSpacing(12)
        lay.addLayout(self._title())
        self.view = Plate3DView()
        self.view.rot = 20          # 預設傾斜，讓橫向板子填滿直式畫面、探點散開
        self.view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        lay.addWidget(self.view, 1)
        lay.addLayout(self._controls())
        self.timer = QTimer(self, interval=STEP_MS, timeout=self._step)
        self.set_mode(STANDARD)
        self.play(False)

    # ---------------------------------------------------------------- 版面

    def _title(self):
        row = QHBoxLayout()
        row.setSpacing(14)
        title = QLabel("變形曲面示意圖")
        title.setFont(text_font(20, 700))
        row.addWidget(title)
        serial = _label(self.snapshot.serial, px=20, color="ink-2", num=True, wrap=False)
        row.addWidget(serial)
        word, bg, fg = RESULT.get(self.snapshot.judgment, RESULT["ERROR"])
        tag = QLabel(word)
        tag.setFont(text_font(15, 900))
        tag.setStyleSheet(f"background:{C[bg]}; color:{C[fg]}; border-radius:4px; padding:3px 10px;")
        row.addWidget(tag)
        row.addStretch()
        x = QPushButton("✕")
        x.setFlat(True)
        x.setCursor(Qt.PointingHandCursor)
        x.setStyleSheet(f"QPushButton {{ border:none; background:transparent; font-size:22px; color:{C['ink-2']};"
                        f" padding:4px 10px; }}")
        x.clicked.connect(self.reject)
        row.addWidget(x)
        return row

    def _controls(self):
        row = QHBoxLayout()
        row.setSpacing(10)
        self.btn_left = QPushButton(f"◀ {STEP_DEG}°")
        self.btn_play = QPushButton()
        self.btn_right = QPushButton(f"{STEP_DEG}° ▶")
        self.btn_left.clicked.connect(lambda: self.turn(-STEP_DEG))
        self.btn_right.clicked.connect(lambda: self.turn(STEP_DEG))
        self.btn_play.clicked.connect(lambda: self.play(not self.timer.isActive()))
        for b in (self.btn_left, self.btn_play, self.btn_right):
            b.setCursor(Qt.PointingHandCursor)
            b.setMinimumWidth(96)
            b.setFocusPolicy(Qt.NoFocus)
            row.addWidget(b)
        self.angle = _label("", px=18, num=True, wrap=False)
        row.addWidget(self.angle)
        row.addStretch()
        close = QPushButton("關閉")
        close.setProperty("kind", "primary")
        close.setFixedWidth(132)
        close.setCursor(Qt.PointingHandCursor)
        close.clicked.connect(self.reject)
        row.addWidget(close)
        return row

    def fit(self):
        """直式圖：寬為主畫面的 62%（最多 820px），高最多 94%。"""
        host = self.parentWidget()
        if host is None:
            return
        w = min(820, round(host.width() * 0.62))
        h = min(round(host.height() * 0.94), round(w * 1.2))
        self.resize(w, h)

    # ---------------------------------------------------------------- 行為

    def set_mode(self, mode: str):
        self.mode = mode
        self.view.set_model(self.models[mode])
        self._show_angle()

    def play(self, on: bool):
        if on:
            self.timer.start()
        else:
            self.timer.stop()
        self.btn_play.setText("❚❚ 暫停" if on else "▶ 播放")

    def turn(self, deg: int):
        self.play(False)
        self.view.set_rot(self.view.rot + deg)
        self._show_angle()

    def _step(self):
        self.view.set_rot(self.view.rot + STEP_DEG)
        self._show_angle()

    def _show_angle(self):
        self.angle.setText(f"旋轉 {self.view.rot}°")

    def keyPressEvent(self, e):
        k = e.key()
        if k == Qt.Key_Left:
            self.turn(-STEP_DEG)
        elif k == Qt.Key_Right:
            self.turn(STEP_DEG)
        elif k == Qt.Key_Space:
            self.play(not self.timer.isActive())
        else:
            super().keyPressEvent(e)

    def done(self, r):
        self.timer.stop()
        self.view.set_model(None)   # 釋放快取
        super().done(r)


def prepare(snapshot: Snapshot, plate: PlateConfig) -> dict[str, SurfaceModel]:
    """檢查並算出兩種模式；不足或同一直線時拋出 RefuseError。"""
    pts = list(snapshot.points)
    check(pts, snapshot.unplaced)
    return {STANDARD: build_model(pts, plate, STANDARD), DETRENDED: build_model(pts, plate, DETRENDED)}


def open_dialog(origin: QWidget, snapshot: Snapshot, plate: PlateConfig):
    """P3D-02、P3D-03：不足或同一直線 → 警告訊息框拒絕；否則嵌入主畫面中央開啟（P3D-08）。"""
    try:
        models = prepare(snapshot, plate)
    except RefuseError as exc:
        log.info("3D 繪圖拒絕：%s", str(exc).replace("\n", " "))
        show_message(origin, str(exc), title="3D 繪圖", buttons=("關閉",), kind="warn")
        return None
    win = origin.window()
    host = win.centralWidget() if isinstance(win, QMainWindow) else win
    backdrop = Backdrop(host)
    dlg = Plate3DDialog(snapshot, models)
    backdrop.host(dlg)
    try:
        return dlg.exec()
    finally:
        backdrop.release()
        backdrop.deleteLater()
