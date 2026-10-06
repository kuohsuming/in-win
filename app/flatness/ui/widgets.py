"""共用小元件：提示訊息（5.9）、背景遮罩、指示點（5.7）。"""

from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QEvent, QPropertyAnimation, QRect, Qt, QTimer
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QGraphicsOpacityEffect, QLabel, QWidget

from .theme import C


class Toast(QLabel):
    """畫面底部置中、距底 24px；淡入 0.2 秒，顯示 3.2 秒後淡出（5.9、第 7 節）。"""

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName("toast")
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignCenter)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self._fx = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._fx)
        self._anim = QPropertyAnimation(self._fx, b"opacity", self)
        self._timer = QTimer(self, singleShot=True, timeout=self._fade_out)
        self.hide()
        self.history: list[str] = []

    def show_text(self, text: str, ms: int = 3200):
        self.history.append(text)
        self.setText(text)
        parent = self.parentWidget()
        self.setMaximumWidth(int(parent.width() * 0.8))
        self.adjustSize()
        self.move((parent.width() - self.width()) // 2, parent.height() - self.height() - 24)
        self.raise_()
        self.show()
        self._anim.stop()
        self._anim.setDuration(200)
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.start()
        self._timer.start(ms)

    def _fade_out(self):
        self._anim.stop()
        self._anim.setDuration(300)
        self._anim.setStartValue(1.0)
        self._anim.setEndValue(0.0)
        self._anim.setEasingCurve(QEasingCurve.InQuad)
        self._anim.finished.connect(self.hide, Qt.SingleShotConnection)
        self._anim.start()


class Backdrop(QWidget):
    """對話框背景遮罩：黑色 45%（5.8、5.10），並把對話框置於主畫面中央（UI-09）。

    對話框嵌入遮罩內，不另開視窗：Wayland 不允許程式指定視窗位置，嵌入後在任何桌面環境都能精確置中；
    對話框改變大小（例如設備設定切換步驟）或主畫面改變大小時重新置中。遮罩擋住主畫面的點擊。
    """

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self._dialog: QWidget | None = None
        self.hide()

    def paintEvent(self, _):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor(0, 0, 0, int(255 * 0.45)))

    def cover(self):
        self.setGeometry(QRect(0, 0, self.parentWidget().width(), self.parentWidget().height()))
        self.raise_()
        self.show()
        self.center()

    def host(self, dialog: QWidget):
        """嵌入對話框並置中；對話框可提供 fit() 依可用空間調整大小。"""
        self._dialog = dialog
        dialog.setParent(self, Qt.Widget)
        dialog.installEventFilter(self)
        self.cover()
        if hasattr(dialog, "fit"):
            dialog.fit()
        else:
            dialog.adjustSize()
        self.center()

    def release(self):
        if self._dialog is not None:
            self._dialog.removeEventFilter(self)
            self._dialog = None
        self.hide()

    def center(self):
        d = self._dialog
        if d is not None:
            w, h = min(d.width(), self.width()), min(d.height(), self.height())
            if (w, h) != (d.width(), d.height()):
                d.resize(w, h)
            d.move((self.width() - w) // 2, (self.height() - h) // 2)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if self._dialog is not None and hasattr(self._dialog, "fit"):
            self._dialog.fit()
        self.center()

    def eventFilter(self, obj, event):
        if obj is self._dialog and event.type() == QEvent.Resize:
            self.center()
        return False


class Dot(QWidget):
    """12px 圓點：go 正常、ng 異常、stale 未知、閃爍為偵測中（5.7）。"""

    def __init__(self, color: str = "stale", size: int = 12, parent=None):
        super().__init__(parent)
        self._color = color
        self._on = True
        self.setFixedSize(size, size)
        self._blink = QTimer(self, interval=500, timeout=self._toggle)

    def set_color(self, color: str, blink: bool = False):
        self._color = color
        self._on = True
        self._blink.start() if blink else self._blink.stop()
        self.update()

    def _toggle(self):
        self._on = not self._on
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        c = QColor(C[self._color])
        c.setAlphaF(1.0 if self._on else 0.2)
        p.setBrush(c)
        p.setPen(Qt.NoPen)
        p.drawEllipse(self.rect())
