"""DL-EN1 清單：驗證、差異比對與套用（DEF-02、UPL-04～UPL-09、UPL-12、EDT-01～EDT-03）。

套用流程（UPL-06～UPL-08）：
    驗證 → 備份定義檔 → 原子覆寫定義檔 → 備份並重寫 BOOTP 主機對應 → 重啟 dnsmasq
    任一步失敗：還原定義檔與 BOOTP 主機對應，拋出例外，現場維持套用前狀態。
"""

from __future__ import annotations

import ipaddress
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

from . import bootp

log = logging.getLogger(__name__)

SCHEMA_PATH = Path(__file__).with_name("dl-en1.schema.json")
DEFAULT_PORT = bootp.DEFAULT_PORT


def empty_definition() -> dict:
    return {"version": 1, "dl_en1": []}


def load_definition(path: Path) -> dict:
    """讀取定義檔；檔案不存在時回傳空清單。JSON 語法錯誤時拋出 DefinitionError。"""
    path = Path(path)
    if not path.exists():
        return empty_definition()
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise bootp.DefinitionError(
            [(f"第 {exc.lineno} 行第 {exc.colno} 列", f"JSON 語法錯誤：{exc.msg}")]
        ) from exc


def dumps(definition: dict) -> str:
    return json.dumps(definition, ensure_ascii=False, indent=2) + "\n"


def _schema_path(path) -> str:
    out = ""
    for part in path:
        out += f"[{part}]" if isinstance(part, int) else (f".{part}" if out else str(part))
    return out or "$"


def validate(definition, equip_net: ipaddress.IPv4Interface) -> list[tuple[str, str]]:
    """回傳所有錯誤 [(位置, 原因)]；空 list 表示通過。

    逐欄規則與跨欄位規則由 bootp.validate 檢查（中文訊息，一次列出全部）；
    再以正式 JSON Schema（3.7.1）把關，避免兩邊規則不一致時放行不合格的檔案。
    """
    try:
        bootp.validate(definition, equip_net)
    except bootp.DefinitionError as exc:
        return exc.errors
    try:
        import jsonschema
    except ImportError:  # 安裝包建立虛擬環境前
        return []
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.Draft202012Validator.FORMAT_CHECKER
    )
    return [(_schema_path(e.absolute_path), f"不符合 JSON Schema：{e.message}")
            for e in validator.iter_errors(definition)]


@dataclass
class Change:
    text: str
    important: bool = False  # MAC / IP 變更，預覽時醒目標示（UPL-05）


@dataclass
class Diff:
    added: list[dict] = field(default_factory=list)
    removed: list[dict] = field(default_factory=list)
    changed: list[tuple[dict, list[Change]]] = field(default_factory=list)
    reordered: bool = False
    power_cycle: list[dict] = field(default_factory=list)   # 需重新上電的 DL-EN1（UPL-09）
    removed_points: list[str] = field(default_factory=list)  # 將從畫面移除的量測點（UPL-05）

    @property
    def empty(self) -> bool:
        return not (self.added or self.removed or self.changed or self.reordered)

    def summary(self) -> str:
        parts = []
        if self.added:
            parts.append("新增 " + "、".join(d["key"] for d in self.added))
        if self.removed:
            parts.append("移除 " + "、".join(d["key"] for d in self.removed))
        if self.changed:
            parts.append("變更 " + "、".join(d["key"] for d, _ in self.changed))
        if self.reordered:
            parts.append("調整順序")
        return "；".join(parts) or "無變更"


def label(device: dict) -> str:
    return f"{device.get('name') or '（未命名）'}（{device.get('key', '')}）"


def _probes(device: dict) -> dict:
    return {p["id"]: p["description"] for p in device.get("probes", [])}


def diff(old: list[dict], new: list[dict]) -> Diff:
    """以 key 比對新舊 DL-EN1 清單；改 key 視為移除舊的、新增新的。"""
    result = Diff()
    old_by_key = {d["key"]: d for d in old}
    new_by_key = {d["key"]: d for d in new}

    for d in new:
        if d["key"] not in old_by_key:
            result.added.append(d)
            result.power_cycle.append(d)
    for d in old:
        if d["key"] not in new_by_key:
            result.removed.append(d)
            result.removed_points += [f"{d['name']} {desc}" for desc in _probes(d).values()]

    for d in new:
        before = old_by_key.get(d["key"])
        if before is None:
            continue
        changes: list[Change] = []
        for fld, name in (("name", "排名稱"), ("mac", "MAC"), ("ipv4", "IPv4")):
            a, b = before[fld], d[fld]
            same = a.upper() == b.upper() if fld == "mac" else a == b
            if not same:
                changes.append(Change(f"{name}：{a} → {b}", important=fld in ("mac", "ipv4")))
        port_a, port_b = before.get("port", DEFAULT_PORT), d.get("port", DEFAULT_PORT)
        if port_a != port_b:
            changes.append(Change(f"埠：{port_a} → {port_b}"))
        if before["max_probes"] != d["max_probes"]:
            changes.append(Change(f"最多探頭數：{before['max_probes']} → {d['max_probes']}"))

        pa, pb = _probes(before), _probes(d)
        for pid in sorted(pb.keys() - pa.keys()):
            changes.append(Change(f"新增探頭 ID {pid}「{pb[pid]}」"))
        for pid in sorted(pa.keys() - pb.keys()):
            changes.append(Change(f"移除探頭 ID {pid}「{pa[pid]}」"))
            result.removed_points.append(f"{before['name']} {pa[pid]}")
        for pid in sorted(pa.keys() & pb.keys()):
            if pa[pid] != pb[pid]:
                changes.append(Change(f"探頭 ID {pid} 名稱：{pa[pid]} → {pb[pid]}"))

        if changes:
            result.changed.append((d, changes))
        if any(c.important for c in changes):
            result.power_cycle.append(d)

    common_old = [d["key"] for d in old if d["key"] in new_by_key]
    common_new = [d["key"] for d in new if d["key"] in old_by_key]
    result.reordered = common_old != common_new
    return result


def apply(definition: dict, def_path: Path, hosts_path: Path,
          equip_net: ipaddress.IPv4Interface, restart_cmd=bootp.RESTART_CMD) -> Diff:
    """套用新的 DL-EN1 清單；成功回傳差異，失敗時還原並拋出例外（UPL-06～UPL-08、UPL-12）。"""
    def_path = Path(def_path)
    errors = validate(definition, equip_net)
    if errors:
        log.warning("套用定義檔失敗 file=%s 原因=驗證錯誤 %s", def_path, errors)
        raise bootp.DefinitionError(errors)

    old_text = def_path.read_text(encoding="utf-8") if def_path.exists() else None
    try:
        old_devices = json.loads(old_text)["dl_en1"] if old_text else []
    except (json.JSONDecodeError, KeyError, TypeError):
        old_devices = []
    changes = diff(old_devices, definition["dl_en1"])

    bootp.backup_file(def_path)
    bootp.atomic_write(def_path, dumps(definition))
    try:
        bootp.apply(definition["dl_en1"], hosts_path, restart_cmd=restart_cmd)
    except Exception as exc:
        if old_text is None:
            def_path.unlink(missing_ok=True)
        else:
            bootp.atomic_write(def_path, old_text)
        log.error("套用定義檔失敗，已還原 file=%s 差異=%s 原因=%s", def_path, changes.summary(), exc)
        raise

    log.info("套用定義檔成功 file=%s 差異=%s 需重新上電=%s", def_path, changes.summary(),
             [d["key"] for d in changes.power_cycle])
    return changes
