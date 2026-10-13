"""3D 繪圖的計算（P3D-02～P3D-07）：純 Python，不依賴 Qt。

- 有效點（有讀值的點）少於 3 個，或全部在同一直線上 → RefuseError（訊息即警告文字）。
- 探頭在板子下方：讀值越大表示表面越低，高度 h = −讀值（mm）。
- 兩種模式：「相對標準件」z = h（讀值已對標準件歸零，CAL-03）；「扣除傾斜」z = h − 最小平方平面。
- 點與點之間以薄板樣條推估（只用來畫形狀，不得用於判定）；記下每個網格點是否在有效點凸包內。
- 高度放大以允許誤差為基準（P3D-07）：lim ≥ 有效點中最大的允許誤差。
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .config import PlateConfig
from .linalg import convex_hull, in_hull, solve, spread_minor

STANDARD, DETRENDED = "standard", "detrended"
MODE_NAME = {STANDARD: "相對標準件", DETRENDED: "扣除傾斜"}
MIN_POINTS = 3
LINE_MM = 1.0          # 有效點在最窄方向的分佈小於 1 mm 視為同一直線（P3D-03）
GRID_LONG = 41         # 長邊網格點數
GRID_SHORT_MIN = 9


class RefuseError(Exception):
    """有效點不足或同一直線：不畫圖，訊息直接顯示在警告訊息框。"""


@dataclass(frozen=True)
class ProbeReading:
    key: str                  # 內部識別「排號-探頭 ID」，例「2-3」（不顯示）
    name: str                 # 顯示名稱：排名稱 + 位置名稱，例「中排 右中」
    x: float                  # mm
    y: float                  # mm
    value_mm: float | None    # 主畫面的讀值；None = 無數據
    tolerance_mm: float       # 允許誤差（JDG-06）
    state: str                # ok／hi／lo／err（主畫面的單點判定）


@dataclass
class SurfaceModel:
    points: list[ProbeReading]
    mode: str
    plate: PlateConfig
    z_mm: dict[str, float]                 # key → 顯示高度（表面向上為正）；無數據的點不在內
    grid: list[list[float]]                # [ny][nx]，mm
    inside: list[list[bool]]               # [ny][nx]，是否在有效點凸包內
    nx: int
    ny: int
    highest: tuple[str, float]             # (key, z)
    lowest: tuple[str, float]
    spread_mm: float                       # 最高 − 最低（standard：讀值差；detrended：平面度）
    lim_mm: float
    thickness_vis: float                   # 示意板厚 Tv
    exaggeration: float                    # 高度倍率 ex（每 mm 對應的顯示單位）
    plane: tuple[float, float, float] | None = None   # detrended：h = a + b·X + c·Y（X、Y 為公尺）
    by_key: dict[str, ProbeReading] = field(default_factory=dict)

    @property
    def valid(self) -> list[ProbeReading]:
        return [p for p in self.points if p.value_mm is not None]

    def label_value(self, key: str) -> float | None:
        """標籤第二行的數值：相對標準件為讀值（與主畫面相同），扣除傾斜為殘差（表面向上為正）。"""
        p = self.by_key[key]
        if p.value_mm is None:
            return None
        return p.value_mm if self.mode == STANDARD else self.z_mm[key]


def check(points: list[ProbeReading]) -> None:
    """P3D-02、P3D-03：有效點不足或同一直線時拋出 RefuseError。"""
    valid = [p for p in points if p.value_mm is not None]
    if len(valid) < MIN_POINTS:
        first = f"無法繪製 3D：本次只有 {len(valid)} 個有效量測點，至少需要 {MIN_POINTS} 個。"
        if len(points) < MIN_POINTS:
            second = f"（目前設定只有 {len(points)} 個探頭）"
        else:
            missing = [p.name for p in points if p.value_mm is None]
            second = f"（設定 {len(points)} 個探頭；無數據：{'、'.join(missing)}）"
        raise RefuseError(f"{first}\n{second}")
    if spread_minor([(p.x, p.y) for p in valid]) < LINE_MM:
        raise RefuseError("無法繪製 3D：所有有效量測點在同一直線上（例如只有 1 排），至少需要 2 排探頭。")


def fit_plane(pts: list[tuple[float, float, float]]) -> tuple[float, float, float] | None:
    """最小平方 h = a + b·X + c·Y（X、Y 為公尺，避免數值過大）。"""
    s = [[0.0] * 3 for _ in range(3)]
    t = [0.0] * 3
    for x, y, h in pts:
        r = (1.0, x / 1000, y / 1000)
        for i in range(3):
            t[i] += r[i] * h
            for j in range(3):
                s[i][j] += r[i] * r[j]
    sol = solve(s, t)
    return tuple(sol) if sol else None


def _u(r: float) -> float:
    return 0.0 if r < 1e-12 else r * r * math.log(r)


def tps(pts: list[tuple[float, float, float]]):
    """薄板樣條（與原型 tps()、scipy thin_plate_spline 同一種）：解 (n+3)×(n+3)，回傳 f(x, y)。"""
    n = len(pts)
    size = n + 3
    a = [[0.0] * size for _ in range(size)]
    b = [0.0] * size
    for i, (xi, yi, zi) in enumerate(pts):
        for j, (xj, yj, _) in enumerate(pts):
            a[i][j] = _u(math.hypot(xi - xj, yi - yj))
        a[i][n] = a[n][i] = 1.0
        a[i][n + 1] = a[n + 1][i] = xi
        a[i][n + 2] = a[n + 2][i] = yi
        b[i] = zi
    w = solve(a, b)
    if w is None:
        return None

    def f(x, y):
        z = w[n] + w[n + 1] * x + w[n + 2] * y
        for i, (xi, yi, _) in enumerate(pts):
            z += w[i] * _u(math.hypot(x - xi, y - yi))
        return z
    return f


def grid_size(plate: PlateConfig) -> tuple[int, int]:
    """長邊 41 點，短邊依比例，至少 9 點。"""
    L, W = plate.length, plate.width
    if L >= W:
        return GRID_LONG, max(GRID_SHORT_MIN, round((GRID_LONG - 1) * W / L) + 1)
    return max(GRID_SHORT_MIN, round((GRID_LONG - 1) * L / W) + 1), GRID_LONG


def build_model(points: list[ProbeReading], plate: PlateConfig, mode: str = STANDARD,
                probe_side: str = "below") -> SurfaceModel:
    """P3D-05～P3D-07。probe_side 固定為 below（PO 確認）；above 只供測試資料使用。"""
    check(points)
    sign = -1.0 if probe_side == "below" else 1.0
    valid = [p for p in points if p.value_mm is not None]
    h = {p.key: sign * p.value_mm for p in valid}
    plane = None
    if mode == DETRENDED:
        plane = fit_plane([(p.x, p.y, h[p.key]) for p in valid])
        if plane is None:
            raise RefuseError("無法繪製 3D：所有有效量測點在同一直線上（例如只有 1 排），至少需要 2 排探頭。")
        a, b, c = plane
        z = {p.key: h[p.key] - (a + b * p.x / 1000 + c * p.y / 1000) for p in valid}
    else:
        z = h
    unit = max(plate.length, plate.width)       # 兩軸同比例；薄板樣條對縮放不變
    f = tps([(p.x / unit, p.y / unit, z[p.key]) for p in valid])
    if f is None:
        raise RefuseError("無法繪製 3D：所有有效量測點在同一直線上（例如只有 1 排），至少需要 2 排探頭。")
    nx, ny = grid_size(plate)
    hull = convex_hull([(p.x, p.y) for p in valid])
    tol = 1e-9 * unit * unit
    grid, inside = [], []
    for j in range(ny):
        y = plate.width * j / (ny - 1)
        grid.append([f(plate.length * i / (nx - 1) / unit, y / unit) for i in range(nx)])
        inside.append([in_hull(hull, (plate.length * i / (nx - 1), y), tol) for i in range(nx)])
    hi_key = max(z, key=z.get)
    lo_key = min(z, key=z.get)
    lim = max(max(p.tolerance_mm for p in valid),
              max(abs(v) for row in grid for v in row),
              max(abs(v) for v in z.values()))
    tv = 0.05 * unit
    return SurfaceModel(points=list(points), mode=mode, plate=plate, z_mm=z, grid=grid, inside=inside,
                        nx=nx, ny=ny, highest=(hi_key, z[hi_key]), lowest=(lo_key, z[lo_key]),
                        spread_mm=z[hi_key] - z[lo_key], lim_mm=lim, thickness_vis=tv,
                        exaggeration=0.4 * tv / lim, plane=plane, by_key={p.key: p for p in points})
