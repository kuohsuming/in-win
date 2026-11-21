"""3D 繪圖的繪製（提案第 6 節；與原型 draw3d() 相同的演算法與常數）：無狀態，以 QPainter 畫。

正交投影、畫家演算法排序多邊形；上表面白灰明暗（越高越白、光從左上方照射，光源跟著眼睛走）；
量測點範圍外（凸包外）的格子往中間灰拉近，表示推估（P3D-06）；量測點與標籤依深度避讓。
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (QColor, QFontMetricsF, QImage, QPainter, QPainterPath, QPen, QPolygonF,
                           QTransform)

from ..ui.theme import C, num_font, text_font
from .config import fmt
from .model import STANDARD, SurfaceModel

ELEVATION = 15.0          # 仰角（度）
AZIMUTH0 = -45.0          # rot = 0 時從左前方 45° 看
STEP_DEG = 30             # 每次轉 30°
STEP_MS = 700             # 每 0.7 秒（P3D-08）
SHADE = {"lo": 140, "hi": 228, "relief": 6, "light": (-0.55, 0.75, 0.6)}
FADE_GRAY, FADE_KEEP = 184, 0.4   # 推估區：灰階往 184 拉近 60%
POINT = QColor("#FF7A00")
LABEL_H = 34


@dataclass
class Label:
    key: str
    x: float
    y: float
    depth: float
    box: QRectF
    lines: tuple[str, str]
    bad: bool
    missing: bool


def label_text(model: SurfaceModel, key: str) -> tuple[str, str]:
    """標籤兩行：探頭名稱「排名稱 位置名稱」；讀值（相對標準件）或殘差（扣除傾斜），小數 3 位、帶正負號。"""
    v = model.label_value(key)
    return model.by_key[key].name, "無數據" if v is None else f"{v:+.3f}"


def _jet(t: float) -> QColor:
    """jet 配色：0→藍、0.5→綠、1→紅。"""
    t = max(0.0, min(1.0, t))
    r = max(0.0, min(1.0, 1.5 - abs(4 * t - 3)))
    g = max(0.0, min(1.0, 1.5 - abs(4 * t - 2)))
    b = max(0.0, min(1.0, 1.5 - abs(4 * t - 1)))
    return QColor(round(r * 255), round(g * 255), round(b * 255))


def render(p: QPainter, w: float, h: float, model: SurfaceModel, rot_deg: float, palette=None) -> list[Label]:
    """變形曲面示意圖（俯視 jet 熱力圖）：相對高度（最低=0）上色，探點標連號、標最高/最低，
    下方列各點相對高度與判定、底部 jet 色條。回傳探點編號標籤（測試用）。"""
    pal = palette or C
    ink, ink2 = QColor(pal["ink"]), QColor(pal["ink-2"])
    L, W = model.plate.length, model.plate.width
    g, nx, ny = model.grid, model.nx, model.ny
    zvals = model.z_mm
    zmin = min(zvals.values()) if zvals else 0.0
    zmax = max(zvals.values()) if zvals else 0.0
    spread = (zmax - zmin) or 1e-9

    def rel(z):
        return z - zmin

    numof = {pt.key: i + 1 for i, pt in enumerate(model.points)}
    p.setRenderHint(QPainter.Antialiasing)
    p.setRenderHint(QPainter.TextAntialiasing)

    # ---- 版面：抬頭（上）／熱力圖（中）／清單＋色條（下）
    head_h = 3 * 20 + 14
    n = len(model.points)
    rows = max(1, (n + 2) // 3)
    legend_h = 24 + rows * 20
    bar_h = 42
    area = QRectF(8, head_h, w - 16, h - head_h - legend_h - bar_h - 12)

    # ---- 抬頭（尺寸、最低、最高）
    hi_k, hi_z = model.highest
    lo_k, lo_z = model.lowest
    p.setPen(ink)
    p.setFont(text_font(14))
    head = [
        f"寬 {fmt(W)} × 長 {fmt(L)} × 厚 {fmt(model.plate.height)} mm",
        f"最低：{model.by_key[lo_k].name} = {rel(lo_z):.4f} mm",
        f"最高：{model.by_key[hi_k].name} = {rel(hi_z):.4f} mm",
    ]
    for i, line in enumerate(head):
        p.drawText(QRectF(24, 8 + i * 20, w - 48, 20), Qt.AlignLeft | Qt.AlignVCenter, line)

    # ---- 板子投影（俯視，依 rot_deg 平面旋轉）
    ang = math.radians(rot_deg)
    ca, sa = math.cos(ang), math.sin(ang)

    def rotp(x, y):
        X, Y = x - L / 2, y - W / 2
        return (X * ca - Y * sa, X * sa + Y * ca)

    corners = [rotp(0, 0), rotp(L, 0), rotp(L, W), rotp(0, W)]
    xs = [c[0] for c in corners]
    ys = [c[1] for c in corners]
    bw, bh = (max(xs) - min(xs)) or 1.0, (max(ys) - min(ys)) or 1.0
    sc = min(area.width() / bw, area.height() / bh) * 0.98   # 幾乎填滿，不留四周旁白
    ccx, ccy = area.center().x(), area.center().y()

    def scr(x, y):
        rx, ry = rotp(x, y)
        return QPointF(ccx + sc * rx, ccy + sc * ry)

    gx = [L * i / (nx - 1) for i in range(nx)]
    gy = [W * j / (ny - 1) for j in range(ny)]
    # 把網格各點上色成一張小圖，再用雙線性平滑放大貼到板面，顏色連續漸層（不馬賽克）
    hm = QImage(nx, ny, QImage.Format_ARGB32)
    for j in range(ny):
        for i in range(nx):
            col = _jet(rel(g[j][i]) / spread)
            if not model.inside[j][i]:                 # 推估範圍外：淡化
                col = QColor((col.red() + 235) // 2, (col.green() + 235) // 2, (col.blue() + 235) // 2)
            hm.setPixelColor(i, j, col)
    quad = QPolygonF([scr(0, 0), scr(L, 0), scr(L, W), scr(0, W)])
    src = QPolygonF([QPointF(0.5, 0.5), QPointF(nx - 0.5, 0.5),
                     QPointF(nx - 0.5, ny - 0.5), QPointF(0.5, ny - 0.5)])   # 以像素中心對齊網格點
    t = QTransform()
    if QTransform.quadToQuad(src, quad, t):
        clip = QPainterPath()
        clip.addPolygon(quad)
        clip.closeSubpath()
        p.save()
        p.setClipPath(clip)
        p.setRenderHint(QPainter.SmoothPixmapTransform, True)
        p.setTransform(t, True)
        p.drawImage(0, 0, hm)
        p.restore()
    p.setPen(QPen(QColor(0, 0, 0, 120), 1.2))
    p.setBrush(Qt.NoBrush)
    p.drawPolygon(quad)

    # ---- 尺寸文字（長、寬）
    p.setPen(ink)
    p.setFont(text_font(13))
    mb = scr(L / 2, W)
    p.drawText(QRectF(mb.x() - 70, mb.y() + 4, 140, 18), Qt.AlignCenter, f"寬 {fmt(W)} mm")
    mr = scr(L, W / 2)
    p.drawText(QRectF(mr.x() + 6, mr.y() - 9, 120, 18), Qt.AlignLeft | Qt.AlignVCenter, f"長 {fmt(L)} mm")

    # ---- 探點（連號）＋最高／最低標記；回傳標籤
    labels: list[Label] = []
    for pt in model.points:
        sp = scr(pt.x, pt.y)
        num = str(numof[pt.key])
        box = QRectF(sp.x() - 11, sp.y() - 21, 22, 15)
        z = model.z_mm.get(pt.key)
        if pt.value_mm is None:
            p.setPen(QPen(QColor(pal["ng"]), 3, Qt.SolidLine, Qt.RoundCap))
            p.drawLine(QPointF(sp.x() - 5, sp.y() - 5), QPointF(sp.x() + 5, sp.y() + 5))
            p.drawLine(QPointF(sp.x() + 5, sp.y() - 5), QPointF(sp.x() - 5, sp.y() + 5))
        else:
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(25, 25, 25))
            p.drawEllipse(sp, 3.5, 3.5)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(255, 255, 255, 215))        # 白底讓編號在任何底色上都清楚
        p.drawRoundedRect(box, 3, 3)
        p.setPen(ink)
        p.setFont(text_font(12, 700))
        p.drawText(box, Qt.AlignCenter, num)
        if pt.key == hi_k:
            p.setPen(QPen(QColor("white"), 2))
            p.setBrush(Qt.NoBrush)
            p.drawEllipse(sp, 7, 7)
            p.setPen(QColor(pal["ng"]))
            p.setFont(text_font(12, 700))
            p.drawText(QRectF(sp.x() - 28, sp.y() + 6, 56, 16), Qt.AlignCenter, "最高")
        if pt.key == lo_k:
            p.setPen(QColor(pal["focus"]))
            p.setFont(text_font(12, 700))
            p.drawText(QRectF(sp.x() - 28, sp.y() + 6, 56, 16), Qt.AlignCenter, "最低")
        labels.append(Label(pt.key, sp.x(), sp.y(), 0.0, box,
                            (num, ""), pt.state in ("hi", "lo"), pt.value_mm is None))

    # ---- 點位相對高度清單（偏高紅／偏低藍／合格）
    word = {"hi": "偏高", "lo": "偏低", "ok": "合格", "err": "無數據"}
    list_top = h - legend_h - bar_h - 8
    p.setPen(ink)
    p.setFont(text_font(14, 700))
    p.drawText(QRectF(24, list_top, 300, 20), Qt.AlignLeft | Qt.AlignVCenter, "點位相對高度 (mm)")
    p.setFont(text_font(13))
    col_w = (w - 48) / 3
    for pt in model.points:
        idx = numof[pt.key] - 1
        c, r = idx // rows, idx % rows
        if pt.value_mm is None:
            txt, col = f"{numof[pt.key]}：無數據", ink2
        else:
            rv = rel(model.z_mm[pt.key])
            txt = f"{numof[pt.key]}：{rv:.4f} {word.get(pt.state, '')}"
            col = {"hi": QColor(pal["ng"]), "lo": QColor(pal["focus"])}.get(pt.state, ink)
        p.setPen(col)
        p.drawText(QRectF(24 + c * col_w, list_top + 24 + r * 20, col_w - 8, 18),
                   Qt.AlignLeft | Qt.AlignVCenter, txt)

    # ---- 色條（相對高度）
    bar = QRectF(60, h - 30, w - 220, 16)
    steps = max(1, int(bar.width()))
    for i in range(steps):
        p.setPen(_jet(i / steps))
        x = bar.left() + i
        p.drawLine(QPointF(x, bar.top()), QPointF(x, bar.bottom()))
    p.setPen(QPen(QColor(0, 0, 0, 120), 1))
    p.setBrush(Qt.NoBrush)
    p.drawRect(bar)
    p.setPen(ink2)
    p.setFont(num_font(11))
    for i in range(6):
        t = i / 5
        x = bar.left() + t * bar.width()
        p.drawText(QRectF(x - 32, bar.bottom() + 2, 64, 14), Qt.AlignCenter, f"{t * spread:.4f}")
    p.setPen(ink)
    p.setFont(text_font(13))
    p.drawText(QRectF(bar.right() + 8, bar.top() - 3, 150, 22), Qt.AlignLeft | Qt.AlignVCenter, "相對高度 (mm)")
    return labels
