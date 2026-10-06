"""SVG 圖示（畫面設計規格第 6 節）：以 currentColor 上色，繪製前替換為狀態色。"""

from __future__ import annotations

from PySide6.QtCore import QByteArray, QRectF, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

SVG = {
    "pass": '<svg viewBox="0 0 32 32"><circle cx="16" cy="16" r="15" fill="currentColor"/><path d="M9 16.5l4.5 4.5L23 11.5" fill="none" stroke="#fff" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "fail": '<svg viewBox="0 0 32 32"><circle cx="16" cy="16" r="15" fill="currentColor"/><path d="M10.5 10.5l11 11M21.5 10.5l-11 11" stroke="#fff" stroke-width="3.6" stroke-linecap="round"/></svg>',
    "hi": '<svg viewBox="0 0 32 32"><path d="M16 2L31 29H1z" fill="currentColor"/><path d="M16 23V12M11 16.5l5-5 5 5" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "lo": '<svg viewBox="0 0 32 32"><path d="M16 30L1 3h30z" fill="currentColor"/><path d="M16 9v11M11 15.5l5 5 5-5" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "err": '<svg viewBox="0 0 32 32"><rect x="2" y="2" width="28" height="28" rx="5" fill="currentColor"/><path d="M16 8v10" stroke="#fff" stroke-width="3.6" stroke-linecap="round"/><circle cx="16" cy="24" r="2.3" fill="#fff"/></svg>',
    "detect": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="3"/><path d="M5.6 5.6a9 9 0 0 0 0 12.8M18.4 5.6a9 9 0 0 1 0 12.8M8.5 8.5a5 5 0 0 0 0 7M15.5 8.5a5 5 0 0 1 0 7"/></svg>',
    "edit": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/></svg>',
    "excel": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6M9 13l6 6M15 13l-6 6"/></svg>',
}


def renderer(name: str, color: str) -> QSvgRenderer:
    return QSvgRenderer(QByteArray(SVG[name].replace("currentColor", color).encode()))


def pixmap(name: str, color: str, size: int, dpr: float = 2.0) -> QPixmap:
    pm = QPixmap(int(size * dpr), int(size * dpr))
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    renderer(name, color).render(p, QRectF(0, 0, size * dpr, size * dpr))
    p.end()
    pm.setDevicePixelRatio(dpr)
    return pm


def icon(name: str, color: str, size: int = 22) -> QIcon:
    return QIcon(pixmap(name, color, size))
