"""繪圖區元件：持有模型與旋轉角，每個角度第一次畫完即存成 QPixmap（提案 6.7），之後播放直接貼圖。"""

from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QWidget

from ..ui.theme import C
from .model import SurfaceModel
from .renderer import render


class Plate3DView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model: SurfaceModel | None = None
        self.rot = 0
        self._cache: dict[tuple, QPixmap] = {}
        self.setMinimumSize(QSize(480, 320))
        self.setAttribute(Qt.WA_OpaquePaintEvent)

    def set_model(self, model: SurfaceModel):
        self.model = model
        self._cache.clear()
        self.update()

    def set_rot(self, rot: int):
        self.rot = rot % 360
        self.update()

    def resizeEvent(self, e):
        self._cache.clear()
        super().resizeEvent(e)

    def frame(self, rot: int | None = None) -> QPixmap:
        """目前大小、指定角度的畫面（有快取）。"""
        rot = self.rot if rot is None else rot % 360
        dpr = self.devicePixelRatioF()
        key = (id(self.model), self.width(), self.height(), dpr, rot)
        pm = self._cache.get(key)
        if pm is None:
            pm = QPixmap(round(self.width() * dpr), round(self.height() * dpr))
            pm.setDevicePixelRatio(dpr)
            pm.fill(QColor(C["panel-2"]))
            if self.model is not None:
                p = QPainter(pm)
                render(p, self.width(), self.height(), self.model, rot)
                p.end()
            self._cache[key] = pm
        return pm

    def paintEvent(self, _):
        p = QPainter(self)
        p.drawPixmap(0, 0, self.frame())
        p.setPen(QColor(C["line"]))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(QRectF(0.5, 0.5, self.width() - 1, self.height() - 1), 6, 6)
