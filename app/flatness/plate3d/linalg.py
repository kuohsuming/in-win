"""3D 繪圖用的小型數值計算（純 Python，不新增套件，INS-06）：線性方程、凸包。

量測點最多約 90 個，矩陣最大約 93×93，純 Python 足夠快。
"""

from __future__ import annotations

import math


def solve(a: list[list[float]], b: list[float], eps: float = 1e-12) -> list[float] | None:
    """部分選主元高斯消去解 a·x = b；奇異（主元相對太小）時回傳 None。"""
    n = len(b)
    m = [list(map(float, row)) + [float(b[i])] for i, row in enumerate(a)]
    scale = max((abs(v) for row in a for v in row), default=0.0) or 1.0
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(m[r][c]))
        if abs(m[p][c]) < eps * scale:
            return None
        m[c], m[p] = m[p], m[c]
        piv = m[c][c]
        for r in range(c + 1, n):
            f = m[r][c] / piv
            if f:
                row_r, row_c = m[r], m[c]
                for k in range(c, n + 1):
                    row_r[k] -= f * row_c[k]
    x = [0.0] * n
    for r in range(n - 1, -1, -1):
        s = m[r][n] - sum(m[r][k] * x[k] for k in range(r + 1, n))
        x[r] = s / m[r][r]
    return x


def spread_minor(points: list[tuple[float, float]]) -> float:
    """點分佈在最窄方向的寬度指標：共變異矩陣較小特徵值的平方根（mm）。同一直線時為 0。"""
    n = len(points)
    mx = sum(p[0] for p in points) / n
    my = sum(p[1] for p in points) / n
    sxx = sum((p[0] - mx) ** 2 for p in points) / n
    syy = sum((p[1] - my) ** 2 for p in points) / n
    sxy = sum((p[0] - mx) * (p[1] - my) for p in points) / n
    tr, det = sxx + syy, sxx * syy - sxy * sxy
    disc = math.sqrt(max(0.0, tr * tr / 4 - det))
    return math.sqrt(max(0.0, tr / 2 - disc))


def convex_hull(points: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """單調鏈法凸包，逆時針。"""
    pts = sorted(set(points))
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def in_hull(hull: list[tuple[float, float]], p: tuple[float, float], tol: float = 1e-6) -> bool:
    """點是否在凸包內（含邊上）。"""
    if len(hull) < 3:
        return False
    for i in range(len(hull)):
        a, b = hull[i], hull[(i + 1) % len(hull)]
        if (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) < -tol:
            return False
    return True
