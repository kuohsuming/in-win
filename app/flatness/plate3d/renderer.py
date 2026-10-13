"""3D 繪圖的繪製（提案第 6 節；與原型 draw3d() 相同的演算法與常數）：無狀態，以 QPainter 畫。

正交投影、畫家演算法排序多邊形；上表面白灰明暗（越高越白、光從左上方照射，光源跟著眼睛走）；
量測點範圍外（凸包外）的格子往中間灰拉近，表示推估（P3D-06）；量測點與標籤依深度避讓。
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFontMetricsF, QPainter, QPainterPath, QPen, QPolygonF

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


def render(p: QPainter, w: float, h: float, model: SurfaceModel, rot_deg: float, palette=None) -> list[Label]:
    """在 (0, 0, w, h) 畫出板子；回傳放好的標籤（測試用）。"""
    pal = palette or C
    ink, ng = QColor(pal["ink"]), QColor(pal["ng"])
    L, W = model.plate.length, model.plate.width
    tv, ex, g, nx, ny = model.thickness_vis, model.exaggeration, model.grid, model.nx, model.ny
    hmax = 0.4 * tv
    az, el = math.radians(AZIMUTH0 + rot_deg), math.radians(ELEVATION)
    v = (math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el))
    rt = (-math.sin(az), math.cos(az))
    up = (-math.sin(el) * math.cos(az), -math.sin(el) * math.sin(az), math.cos(el))
    lv = SHADE["light"]
    lw = (lv[0] * rt[0] + lv[1] * up[0] + lv[2] * v[0], lv[0] * rt[1] + lv[1] * up[1] + lv[2] * v[1],
          lv[1] * up[2] + lv[2] * v[2])
    n_lw = math.hypot(*lw)
    lw = tuple(c / n_lw for c in lw)
    diag = math.hypot(L, W)
    sc = min(w * 0.92 / diag, h * 0.84 / (diag * math.sin(el) + (tv + 2 * hmax) * math.cos(el)))
    cx, cy = w / 2, h / 2

    def pr(x, y, z):
        X, Y, Z = x - L / 2, y - W / 2, z + tv / 2
        return (cx + sc * (X * rt[0] + Y * rt[1]), cy - sc * (X * up[0] + Y * up[1] + Z * up[2]),
                X * v[0] + Y * v[1] + Z * v[2])

    gx = [L * i / (nx - 1) for i in range(nx)]
    gy = [W * j / (ny - 1) for j in range(ny)]
    Z = [[g[j][i] * ex for i in range(nx)] for j in range(ny)]
    top = [[pr(gx[i], gy[j], Z[j][i]) for i in range(nx)] for j in range(ny)]
    lo, hi, relief = SHADE["lo"], SHADE["hi"], SHADE["relief"]
    dx, dy = L / (nx - 1), W / (ny - 1)
    lim = model.lim_mm
    polys = []   # (深度, 灰階或 RGB, 頂點)
    for j in range(ny - 1):
        for i in range(nx - 1):
            q = (top[j][i], top[j][i + 1], top[j + 1][i + 1], top[j + 1][i])
            r = (g[j][i] + g[j][i + 1] + g[j + 1][i + 1] + g[j + 1][i]) / 4
            base = lo + (hi - lo) * max(0.0, min(1.0, (r / lim + 1) / 2))
            dzx = (Z[j][i + 1] + Z[j + 1][i + 1] - Z[j][i] - Z[j + 1][i]) / 2 * relief
            dzy = (Z[j + 1][i] + Z[j + 1][i + 1] - Z[j][i] - Z[j][i + 1]) / 2 * relief
            n = (-dzx * dy, -dzy * dx, dx * dy)
            lit = (n[0] * lw[0] + n[1] * lw[1] + n[2] * lw[2]) / math.hypot(*n)
            k = max(0.5, min(1.14, 1 + 1.8 * (lit - lw[2])))
            gray = min(255.0, base * k)
            ins = model.inside
            if not (ins[j][i] or ins[j][i + 1] or ins[j + 1][i + 1] or ins[j + 1][i]):
                gray = FADE_GRAY + FADE_KEEP * (gray - FADE_GRAY)
            gv = round(gray)
            polys.append(((q[0][2] + q[2][2]) / 2, QColor(gv, gv, gv), q))
    faces = [((0, -1), [(i, 0) for i in range(nx)]), ((0, 1), [(i, ny - 1) for i in range(nx)]),
             ((-1, 0), [(0, j) for j in range(ny)]), ((1, 0), [(nx - 1, j) for j in range(ny)])]
    vis = [f for f in faces if f[0][0] * v[0] + f[0][1] * v[1] > 1e-6]
    for (fnx, fny), edge in vis:
        s = 0.45 + 0.35 * min(1.0, (fnx * v[0] + fny * v[1]) / math.cos(el))
        col = QColor(*(round(min(1.0, c) * 255) for c in (0.5 * s + 0.12, 0.5 * s + 0.12, 0.5 * s + 0.14)))
        for t in range(len(edge) - 1):
            (i1, j1), (i2, j2) = edge[t], edge[t + 1]
            q = (top[j1][i1], top[j2][i2], pr(gx[i2], gy[j2], Z[j2][i2] - tv), pr(gx[i1], gy[j1], Z[j1][i1] - tv))
            polys.append(((q[0][2] + q[2][2]) / 2 - 1e-3, col, q))
    polys.sort(key=lambda t: t[0])
    p.setRenderHint(QPainter.Antialiasing)
    pen = QPen()
    pen.setWidthF(0.7)
    pen.setJoinStyle(Qt.RoundJoin)
    for _, col, q in polys:
        pen.setColor(col)
        p.setPen(pen)
        p.setBrush(col)
        p.drawPolygon(QPolygonF([QPointF(a[0], a[1]) for a in q]))
    # 輪廓：上表面四邊、可見側面下緣與兩端垂直邊
    outline = QPen(QColor(0, 0, 0, round(255 * 0.75)), 1.1)
    p.setPen(outline)
    p.setBrush(Qt.NoBrush)

    def line(edge, dz):
        path = QPainterPath()
        for k, (i, j) in enumerate(edge):
            x, y, _ = pr(gx[i], gy[j], Z[j][i] + dz)
            path.lineTo(x, y) if k else path.moveTo(x, y)
        p.drawPath(path)

    for _, edge in faces:
        line(edge, 0)
    for _, edge in vis:
        line(edge, -tv)
        for i, j in (edge[0], edge[-1]):
            a, b = top[j][i], pr(gx[i], gy[j], Z[j][i] - tv)
            p.drawLine(QPointF(a[0], a[1]), QPointF(b[0], b[1]))
    # 尺寸文字（板子尺寸設定，P3D-10）
    p.setFont(text_font(13, 500))
    p.setPen(ink)
    for (fnx, fny), edge in vis:
        i, j = edge[len(edge) // 2]
        x, y, _ = pr(gx[i] + fnx * W * 0.12, gy[j] + fny * W * 0.12, -tv)
        text = f"長 {fmt(L)} mm" if fny else f"寬 {fmt(W)} mm"
        p.drawText(QRectF(x - 80, y - 2, 160, 20), Qt.AlignCenter, text)
    # 量測點與標籤：依深度由近到遠放置（避讓），再由遠到近畫
    name_font, value_font = text_font(13, 700), num_font(13, 700)
    fm1, fm2 = QFontMetricsF(name_font), QFontMetricsF(value_font)
    labels: list[Label] = []
    for pt in model.points:
        z = model.z_mm.get(pt.key)
        x, y, d = pr(pt.x, pt.y, 0.0 if z is None else z * ex)
        t1, t2 = label_text(model, pt.key)
        labels.append(Label(pt.key, x, y, d, QRectF(), (t1, t2), pt.state in ("hi", "lo"), z is None))
    placed: list[QRectF] = []
    for lb in sorted(labels, key=lambda o: -o.depth):
        bw = max(fm1.horizontalAdvance(lb.lines[0]), fm2.horizontalAdvance(lb.lines[1])) + 10
        bh = LABEL_H
        cand = [(-bw / 2, -bh - 10), (-bw / 2, 10), (-bw - 10, -bh / 2), (10, -bh / 2),
                (-bw / 2, -2 * bh - 14), (-bw / 2, bh + 14)]
        box = None
        for ox, oy in cand:
            r = QRectF(lb.x + ox, lb.y + oy, bw, bh)
            if not any(r.adjusted(-2, -2, 2, 2).intersects(o) for o in placed):
                box = r
                break
        lb.box = box or QRectF(lb.x + cand[0][0], lb.y + cand[0][1], bw, bh)
        placed.append(lb.box)
    for lb in sorted(labels, key=lambda o: o.depth):
        b = lb.box
        p.setPen(QPen(QColor(0, 0, 0, round(255 * 0.55)), 1))
        p.drawLine(QPointF(lb.x, lb.y), QPointF(max(b.left(), min(lb.x, b.right())), max(b.top(), min(lb.y, b.bottom()))))
        if lb.missing:
            p.setPen(QPen(ng, 3, Qt.SolidLine, Qt.RoundCap))
            p.drawLine(QPointF(lb.x - 6, lb.y - 6), QPointF(lb.x + 6, lb.y + 6))
            p.drawLine(QPointF(lb.x + 6, lb.y - 6), QPointF(lb.x - 6, lb.y + 6))
        else:
            p.setPen(QPen(QColor("#111111"), 1.2))
            p.setBrush(POINT)
            p.drawEllipse(QPointF(lb.x, lb.y), 4.5, 4.5)
        red = lb.bad or lb.missing
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(200, 50, 43, round(255 * 0.94)) if red else QColor(255, 255, 255, round(255 * 0.9)))
        p.drawRoundedRect(b, 4, 4)
        p.setPen(QColor("#FFFFFF") if red else QColor("#1C2326"))
        p.setFont(name_font)
        p.drawText(QRectF(b.left(), b.top() + 1, b.width(), 17), Qt.AlignCenter, lb.lines[0])
        p.setFont(value_font)
        p.drawText(QRectF(b.left(), b.top() + 16, b.width(), 17), Qt.AlignCenter, lb.lines[1])
    # 左下角：板厚（示意）與放大倍數（P3D-07、P3D-10）
    p.setFont(text_font(13, 500))
    p.setPen(QColor(pal["ink-2"]))
    mode = "讀值（相對標準件）" if model.mode == STANDARD else "殘差（扣除傾斜）"
    p.drawText(QRectF(10, h - 26, w - 20, 20), Qt.AlignLeft | Qt.AlignVCenter,
               f"板厚 {fmt(model.plate.height)} mm（示意，不按比例）　高度放大約 ×{round(model.exaggeration):,} 倍　標籤：{mode} mm")
    return labels
