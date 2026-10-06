"""首次匯入 DL-EN1 定義檔到資料庫（DEF-10）：資料庫沒有任何 DL-EN1 時才匯入，已有資料則不變。

    python -m flatness.initdb --db-env /etc/flatness/db.env --def dl-en1.json --equip-net 192.168.10.1/24
"""

from __future__ import annotations

import argparse
import ipaddress
import sys
from pathlib import Path

from . import bootp, lan, sync
from .store import MySQLStore, StoreError


def import_if_empty(store, definition: dict) -> int:
    """回傳匯入的台數；資料庫已有任何 DL-EN1（使用中、維修中、已停用）時回傳 0。"""
    devices = store.load()
    if any(d.status in (lan.LIVE, lan.MAINT, lan.RETIRED) for d in devices):
        return 0
    new = lan.import_definition(devices, definition)
    with store.transaction() as tx:
        tx.save(devices, new)
    return len(definition["dl_en1"])


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="flatness.initdb", description=__doc__.splitlines()[0])
    p.add_argument("--db-env", type=Path, required=True)
    p.add_argument("--def", dest="def_file", type=Path, required=True)
    p.add_argument("--equip-net", type=ipaddress.IPv4Interface, required=True)
    args = p.parse_args(argv)
    try:
        definition = sync.read_definition_file(args.def_file, args.equip_net)
        n = import_if_empty(MySQLStore.from_env(args.db_env), definition)
    except bootp.DefinitionError as exc:
        print("DL-EN1 定義檔驗證失敗：", file=sys.stderr)
        for where, why in exc.errors:
            print(f"  {where}: {why}", file=sys.stderr)
        return 2
    except StoreError as exc:
        print(exc, file=sys.stderr)
        return 1
    print(f"已匯入 {n} 台 DL-EN1" if n else "資料庫已有 DL-EN1，不匯入（DEF-10）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
