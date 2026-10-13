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
        self.body = QBoxLayout(QBoxLayout.LeftToRight)
        self.body.setSpacing(16)
        self.view = Plate3DView()
        self.view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.body.addWidget(self.view, 1)
        self.side = QWidget()
        self.side.setObjectName("side3d")
        self.side.setFixedWidth(SIDE_W)
        self.side_lay = QVBoxLayout(self.side)
        self.side_lay.setContentsMargins(0, 0, 0, 0)
        self.side_lay.setSpacing(10)
        self.body.addWidget(self.side)
        lay.addLayout(self.body, 1)
        lay.addLayout(self._controls())
        self.timer = QTimer(self, interval=STEP_MS, timeout=self._step)
        self.set_mode(STANDARD)
        self.play(True)

    # ---------------------------------------------------------------- 版面

    def _title(self):
        row = QHBoxLayout()
        row.setSpacing(14)
        title = QLabel("3D 繪圖")
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
        self.mode_btns = QButtonGroup(self)
        for mode in (STANDARD, DETRENDED):
            b = QPushButton(MODE_NAME[mode])
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            b.setProperty("mode", mode)
            b.setStyleSheet(f"QPushButton {{ padding:8px 16px; border:2px solid {C['ink-2']}; background:{C['panel-2']};"
                            f" color:{C['ink']}; font-size:16px; border-radius:6px; }}"
                            f" QPushButton:checked {{ background:{C['ink']}; color:{C['panel']}; border-color:{C['ink']};"
                            f" font-weight:700; }}")
            self.mode_btns.addButton(b)
            row.addWidget(b)
        self.mode_btns.buttonClicked.connect(lambda b: self.set_mode(b.property("mode")))
        row.addSpacing(16)
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
        for b in self.mode_btns.buttons():
            b.setFocusPolicy(Qt.NoFocus)
        return row

    def fit(self):
        """寬為主畫面的 96%（最多 1280px），高最多 94%；寬度 ≤ 900px 時資訊欄移到繪圖區下方。"""
        host = self.parentWidget()
        if host is None:
            return
        w = min(1280, round(host.width() * 0.96))
        h = min(round(host.height() * 0.94), max(640, round(w * 0.62)))
        self.body.setDirection(QBoxLayout.TopToBottom if w <= 900 else QBoxLayout.LeftToRight)
        self.side.setFixedWidth(w - 44 if w <= 900 else SIDE_W)
        self.view.setMinimumHeight(min(round(h * 0.6), 560) if w <= 900 else 320)
        self.resize(w, h)

    # ---------------------------------------------------------------- 資訊欄

    def _fill_side(self):
        while self.side_lay.count():
            item = self.side_lay.takeAt(0)
            if item.widget():
                item.widget().hide()
                item.widget().deleteLater()
        m = self.models[self.mode]
        std = self.mode == STANDARD
        unit = "mm"
        c1 = Card()
        c1.lay.addWidget(_label("讀值差（最高 − 最低）" if std else "平面度（最小平方）", px=14, color="ink-2"))
        c1.lay.addWidget(_label(f"<span style='font-size:44px;font-weight:700'>{m.spread_mm:.3f}</span>"
                                f"<span style='font-size:18px;color:{C['ink-2']}'> {unit}</span>", px=44, num=True))
        if not std:
            c1.lay.addWidget(_label("允許值：未定（TBD-07）；只供檢視，不用於判定", px=13, color="ink-2"))
        self.side_lay.addWidget(c1)
        c2 = Card()
        for word, (key, _) in (("最高點", m.highest), ("最低點", m.lowest)):
            v = m.label_value(key)
            c2.lay.addWidget(_label(f"{word}　<b>{html.escape(m.by_key[key].name)}</b>　"
                                    f"<span style='font-family:\"Barlow Semi Condensed\"'>{v:+.3f}</span>", px=15))
        c2.lay.addWidget(_label("單位 mm；數值為讀值，以標準件為 0（探頭在下方，讀值越小表面越高）" if std else
                                "單位 mm；相對於擬合平面，表面向上為正", px=12, color="ink-2"))
        self.side_lay.addWidget(c2)
        c3 = Card()
        c3.lay.addWidget(_label("越高越白、越低越灰；光從左上方照射", px=12, color="ink-2"))
        self.legend = Legend()
        self.legend.lim = m.lim_mm
        c3.lay.addWidget(self.legend)
        self.side_lay.addWidget(c3)
        out = [p.name for p in m.points if p.state in ("hi", "lo") and p.value_mm is not None]
        miss = [p.name for p in m.points if p.value_mm is None]
        if out or miss:
            c4 = Card(red=True)
            if out:
                c4.lay.addWidget(_label(f"<b>超出允收：</b>{html.escape('、'.join(out))}", px=14, color="ng"))
            if miss:
                c4.lay.addWidget(_label(f"<b>無數據（不參與繪圖）：</b>{html.escape('、'.join(miss))}", px=14, color="ng"))
            c4.lay.addWidget(_label("探頭在下方：讀值「偏高」＝該處表面較低", px=12, color="ink-2"))
            self.side_lay.addWidget(c4)
        notes = [f"使用 {len(m.valid)}/{len(m.points)} 點。",
                 f"高度放大約 ×{round(m.exaggeration):,} 倍，厚度為示意。",
                 "點與點之間的形狀是推估；淡色區為量測點範圍外的推估，判定以實測點為準。",
                 "探頭在板子下方，已換算成由上往下看的高度。"]
        if not std:
            notes.insert(1, "已扣除整片傾斜與高低。")
        self.notes = _label("".join(f"• {html.escape(n)}<br>" for n in notes), px=13, color="ink-2")
        self.side_lay.addWidget(self.notes)
        self.side_lay.addStretch()

    # ---------------------------------------------------------------- 行為

    def set_mode(self, mode: str):
        self.mode = mode
        for b in self.mode_btns.buttons():
            b.setChecked(b.property("mode") == mode)
        self.view.set_model(self.models[mode])
        self._fill_side()
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
        elif k == Qt.Key_M:
            self.set_mode(DETRENDED if self.mode == STANDARD else STANDARD)
        else:
            super().keyPressEvent(e)

    def done(self, r):
        self.timer.stop()
        self.view.set_model(None)   # 釋放快取
        super().done(r)


def prepare(snapshot: Snapshot, plate: PlateConfig) -> dict[str, SurfaceModel]:
    """檢查並算出兩種模式；不足或同一直線時拋出 RefuseError。"""
    pts = list(snapshot.points)
    check(pts)
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
