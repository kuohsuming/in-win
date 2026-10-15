"""探頭位置（需求規格書 3.13 POS）：排與點、排名稱與點名稱、顯示名稱。

只用 Python 標準函式庫：bootp（安裝包在建立虛擬環境之前就會呼叫）也使用本模組。
    - 每個探頭在設定中可有 row、point（1～5，兩者同時存在或同時省略；省略即未定，POS-01、POS-08）
    - 排名稱、點名稱全機共用一組，預設 排1～排5、點1～點5（POS-03、POS-09）
    - 板子版面：幾排、每排幾點（各 1～5，預設 5 × 5，POS-10）；探頭位置不可超出版面（POS-11）
    - 顯示名稱（給作業員）與設備稱呼（給設定頁）見 PROPOSAL §5.2
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace

SIZE = 5                     # 排與點各 1～5（POS-01）
NAME_MAX = 10
UNSET = "未定"
DEFAULT_ROWS = tuple(f"排{i}" for i in range(1, SIZE + 1))
DEFAULT_POINTS = tuple(f"點{i}" for i in range(1, SIZE + 1))
KIND_LABEL = {"rows": "排名稱", "points": "點名稱"}

_DEFAULT_PROBE = re.compile(r"^探頭 ?\d+$")   # 新增探頭的預設位置名稱「探頭 N」（POS-09）


def _is_int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


@dataclass(frozen=True)
class Names:
    """排名稱與點名稱（各 5 個），以及板子版面（幾排、每排幾點，POS-10）。

    名稱一律存 5 個：版面外的名稱不顯示但保留，版面改大時恢復（POS-10）。
    """
    rows: tuple[str, ...] = DEFAULT_ROWS
    points: tuple[str, ...] = DEFAULT_POINTS
    grid_rows: int = SIZE
    grid_points: int = SIZE

    @classmethod
    def default(cls) -> "Names":
        return cls()

    @classmethod
    def from_json(cls, obj, grid=None) -> "Names":
        """定義檔的 position_names 與 position_grid；沒有或不合格時為預設名稱、5 × 5。"""
        out = cls()
        if isinstance(obj, dict) and not check_names_json(obj):
            out = cls(tuple(obj["rows"]), tuple(obj["points"]))
        if isinstance(grid, dict) and not check_grid_json(grid):
            out = out.with_grid(grid["rows"], grid["points"])
        return out

    @classmethod
    def from_definition(cls, definition) -> "Names":
        d = definition if isinstance(definition, dict) else {}
        return cls.from_json(d.get("position_names"), d.get("position_grid"))

    def to_json(self) -> dict:
        return {"rows": list(self.rows), "points": list(self.points)}

    def grid_json(self) -> dict:
        return {"rows": self.grid_rows, "points": self.grid_points}

    def with_grid(self, rows: int, points: int) -> "Names":
        return replace(self, grid_rows=rows, grid_points=points)

    def with_names(self, rows=None, points=None) -> "Names":
        return replace(self, rows=tuple(rows) if rows is not None else self.rows,
                       points=tuple(points) if points is not None else self.points)

    def in_grid(self, position) -> bool:
        """位置（排, 點）在版面內（POS-11）。"""
        return 1 <= position[0] <= self.grid_rows and 1 <= position[1] <= self.grid_points

    def grid_text(self) -> str:
        return f"{self.grid_rows} 排 × {self.grid_points} 點"

    def row(self, n: int) -> str:
        return self.rows[n - 1]

    def point(self, n: int) -> str:
        return self.points[n - 1]

    @property
    def is_default(self) -> bool:
        return self.rows == DEFAULT_ROWS and self.points == DEFAULT_POINTS


def name_errors(kind: str, values) -> list[tuple[int, str]]:
    """排名稱或點名稱的錯誤 [(第幾個 0 起算, 原因)]：1～10 字、不可空白、同類不可重複（POS-03）。"""
    out, seen = [], {}
    for i, v in enumerate(values):
        if not isinstance(v, str) or not v.strip():
            out.append((i, "不可空白"))
            continue
        if len(v) > NAME_MAX:
            out.append((i, f"最多 {NAME_MAX} 字"))
            continue
        if v in seen:
            out.append((i, f"與第 {seen[v] + 1} 個重複"))
        else:
            seen[v] = i
    return out


def check_names_json(obj) -> list[tuple[str, str]]:
    """定義檔 position_names 的錯誤 [(位置, 原因)]。"""
    if not isinstance(obj, dict):
        return [("position_names", "必須是物件")]
    errors = [(f"position_names.{k}", "不允許的欄位") for k in sorted(set(obj) - {"rows", "points"})]
    for kind in ("rows", "points"):
        values = obj.get(kind)
        if not isinstance(values, list) or len(values) != SIZE:
            errors.append((f"position_names.{kind}", f"必須是 {SIZE} 個名稱的陣列"))
            continue
        errors += [(f"position_names.{kind}[{i}]", why) for i, why in name_errors(kind, values)]
    return errors


def check_grid_json(obj) -> list[tuple[str, str]]:
    """定義檔 position_grid 的錯誤 [(位置, 原因)]：rows、points 各為 1～5 的整數（POS-10）。"""
    if not isinstance(obj, dict):
        return [("position_grid", "必須是物件")]
    errors = [(f"position_grid.{k}", "不允許的欄位") for k in sorted(set(obj) - {"rows", "points"})]
    for kind in ("rows", "points"):
        v = obj.get(kind)
        if not (_is_int(v) and 1 <= v <= SIZE):
            errors.append((f"position_grid.{kind}", f"須為 1～{SIZE} 的整數"))
    return errors


def outside_grid(probe: dict, names: "Names") -> str | None:
    """探頭位置超出版面時的說明（POS-11），例「第 4 排超出版面 3 排」；在版面內或未定時為 None。"""
    where = pos(probe)
    if not where:
        return None
    if where[0] > names.grid_rows:
        return f"第 {where[0]} 排超出版面 {names.grid_rows} 排"
    if where[1] > names.grid_points:
        return f"第 {where[1]} 點超出版面每排 {names.grid_points} 點"
    return None


def probe_errors(probe: dict) -> list[tuple[str, str]]:
    """探頭 row、point 的錯誤 [(欄位, 原因)]：範圍 1～5、同時存在或同時省略（POS-01、POS-08）。"""
    out = []
    has_r, has_p = "row" in probe, "point" in probe
    if has_r != has_p:
        out.append(("point" if has_r else "row", "排與點須同時設定或同時省略"))
    for f in ("row", "point"):
        if f in probe and not (_is_int(probe[f]) and 1 <= probe[f] <= SIZE):
            out.append((f, f"須為 1～{SIZE} 的整數"))
    return out


def pos(probe: dict) -> tuple[int, int] | None:
    """探頭的（排, 點）；未定（或不完整、不合格）時為 None。"""
    r, p = probe.get("row"), probe.get("point")
    if _is_int(r) and _is_int(p) and 1 <= r <= SIZE and 1 <= p <= SIZE:
        return r, p
    return None


def set_pos(probe: dict, row: int | None, point: int | None) -> None:
    """設定探頭位置；None 表示未定（該欄位不寫入設定）。"""
    for f, v in (("row", row), ("point", point)):
        if v is None:
            probe.pop(f, None)
        else:
            probe[f] = v


def auto_description(desc: str, old_point: int | None, new_point: int | None,
                     names: Names, old_names: Names | None = None) -> str:
    """POS-09：選定第幾點時自動帶入點名稱。

    位置名稱為新增探頭的預設名稱「探頭 N」、等於原本所選點 j 目前（或修改前）的名稱或預設名稱「點j」、
    或被清空時，改為新點的名稱；工程人員自己取的名稱不改。點改回未定時名稱不變。
    """
    if new_point is None:
        return desc
    text = (desc or "").strip()
    auto = not text or bool(_DEFAULT_PROBE.match(text))
    if not auto and old_point is not None:
        known = {names.point(old_point), DEFAULT_POINTS[old_point - 1]}
        if old_names is not None:
            known.add(old_names.point(old_point))
        auto = text in known
    return names.point(new_point) if auto else desc


def device_no(key) -> int | None:
    """DL-EN1 的位置標籤 row-N → N（畫面上稱「第 N 台」，POS-06）。"""
    m = re.match(r"^row-(\d+)$", key or "")
    return int(m.group(1)) if m else None


def device_label(key, device_name) -> str:
    """「第 N 台 DL-EN1 名稱」。"""
    n = device_no(key)
    head = f"第 {n} 台" if n else (key or "—")
    return f"{head} {device_name}".strip() if device_name else head


def device_call(key, device_name, description) -> str:
    """設備稱呼（設定頁）：第 N 台 DL-EN1 名稱 位置名稱，例「第 2 台 中排 點2」。"""
    return f"{device_label(key, device_name)} {description}".strip()


def display_name(names: Names, position, key, device_name, description) -> str:
    """顯示名稱（給作業員，PROPOSAL §5.2）：已設定位置「排名稱 位置名稱」，未定「第 N 台 名稱 位置名稱」。"""
    if position:
        return f"{names.row(position[0])} {description}"
    return device_call(key, device_name, description)


def disambiguate(items: list[tuple[str, str, int]]) -> list[str]:
    """[(名稱, key, 探頭 id)] → 名稱；同一份清單中名稱重複者加「（第 N 台 探頭 id）」。"""
    count: dict[str, int] = {}
    for name, _, _ in items:
        count[name] = count.get(name, 0) + 1
    out = []
    for name, key, pid in items:
        if count[name] > 1:
            n = device_no(key)
            name = f"{name}（{'第 ' + str(n) + ' 台' if n else key} 探頭 {pid}）"
        out.append(name)
    return out
