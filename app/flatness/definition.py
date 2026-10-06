"""DL-EN1 定義檔：讀取、輸出與驗證（3.7.1、DEF-02、UPL-04）。

定義檔由 App 依資料庫產生（DSC-06），差異預覽與套用見 lan.py、sync.py。
"""

from __future__ import annotations

import ipaddress
import json
from pathlib import Path

from . import bootp

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
