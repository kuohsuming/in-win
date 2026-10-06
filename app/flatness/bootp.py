"""DL-EN1 定義檔驗證與 BOOTP 主機對應檔產生（DEF-02、DEF-03、DEF-10）。

只用 Python 標準函式庫：安裝包在建立虛擬環境之前（3.0.4 步驟 3）就要呼叫本模組。
App 執行時另以 jsonschema 做完整 Schema 驗證（DEF-02）；這裡實作的規則與 3.7.1 一致。

命令列：
    python3 -m flatness.bootp check    --def dl-en1.json --equip-net 192.168.10.1/24
    python3 -m flatness.bootp render   --def dl-en1.json --equip-net 192.168.10.1/24
    python3 -m flatness.bootp apply    --def dl-en1.json --equip-net 192.168.10.1/24 \
                                       --hosts /var/lib/flatness/bootp/dl-en1.hosts
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

DEFAULT_PORT = 64000
BACKUP_KEEP = 20
RESTART_CMD = ["sudo", "-n", "/usr/bin/systemctl", "restart", "dnsmasq"]

_KEY_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,29}$")
_MAC_RE = re.compile(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$")


class DefinitionError(ValueError):
    """定義檔不合格；errors 為所有錯誤（位置, 原因），一次列出（UPL-04）。"""

    def __init__(self, errors: list[tuple[str, str]]):
        self.errors = errors
        super().__init__("\n".join(f"{where}: {why}" for where, why in errors))


def _is_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _check_str(errors, where, value, min_len, max_len):
    if not isinstance(value, str):
        errors.append((where, "必須是字串"))
        return False
    if not min_len <= len(value) <= max_len:
        errors.append((where, f"長度須為 {min_len}～{max_len} 字"))
        return False
    return True


def validate(definition, equip_net: ipaddress.IPv4Interface) -> list[dict]:
    """依 3.7.1 驗證定義檔，回傳 DL-EN1 清單；有錯誤時拋出 DefinitionError。"""
    errors: list[tuple[str, str]] = []

    if not isinstance(definition, dict):
        raise DefinitionError([("$", "最外層必須是物件")])
    for extra in sorted(set(definition) - {"version", "dl_en1"}):
        errors.append((extra, "不允許的欄位"))
    if definition.get("version") != 1:
        errors.append(("version", "必須為 1"))

    devices = definition.get("dl_en1")
    if not isinstance(devices, list) or not 1 <= len(devices) <= 8:
        errors.append(("dl_en1", "必須是 1～8 台 DL-EN1 的陣列"))
        raise DefinitionError(errors)

    seen: dict[str, dict] = {"key": {}, "name": {}, "mac": {}, "ipv4": {}}
    device_fields = {"key", "name", "mac", "ipv4", "port", "max_probes", "probes"}

    for i, dev in enumerate(devices):
        at = f"dl_en1[{i}]"
        if not isinstance(dev, dict):
            errors.append((at, "必須是物件"))
            continue
        for extra in sorted(set(dev) - device_fields):
            errors.append((f"{at}.{extra}", "不允許的欄位"))
        for field in ("key", "name", "mac", "ipv4", "max_probes", "probes"):
            if field not in dev:
                errors.append((f"{at}.{field}", "必填"))

        key = dev.get("key")
        if "key" in dev and not (isinstance(key, str) and _KEY_RE.match(key)):
            errors.append((f"{at}.key", "限小寫英文、數字、連字號，1～30 字，不可以連字號開頭"))
        if "name" in dev:
            _check_str(errors, f"{at}.name", dev["name"], 1, 10)

        mac = dev.get("mac")
        if "mac" in dev and not (isinstance(mac, str) and _MAC_RE.match(mac)):
            errors.append((f"{at}.mac", "格式須為 XX:XX:XX:XX:XX:XX"))

        if "ipv4" in dev:
            try:
                ip = ipaddress.IPv4Address(dev["ipv4"])
            except (ipaddress.AddressValueError, TypeError, ValueError):
                errors.append((f"{at}.ipv4", "不是有效的 IPv4 位址"))
            else:
                net = equip_net.network
                if ip not in net:
                    errors.append((f"{at}.ipv4", f"不在設備網段 {net} 內"))
                elif ip in (net.network_address, net.broadcast_address):
                    errors.append((f"{at}.ipv4", "不可為網路位址或廣播位址"))
                elif ip == equip_net.ip:
                    errors.append((f"{at}.ipv4", "不可與量測 PC 相同"))

        if "port" in dev:
            port = dev["port"]
            if not (_is_int(port) and 1 <= port <= 65535):
                errors.append((f"{at}.port", "須為 1～65535 的整數"))

        max_probes = dev.get("max_probes")
        max_ok = _is_int(max_probes) and 1 <= max_probes <= 15
        if "max_probes" in dev and not max_ok:
            errors.append((f"{at}.max_probes", "須為 1～15 的整數"))

        probes = dev.get("probes")
        if "probes" in dev:
            if not isinstance(probes, list) or not 1 <= len(probes) <= 15:
                errors.append((f"{at}.probes", "必須是 1～15 個探頭的陣列"))
            else:
                if max_ok and len(probes) > max_probes:
                    errors.append((f"{at}.probes", f"探頭數 {len(probes)} 超過 max_probes {max_probes}"))
                ids: set[int] = set()
                for j, probe in enumerate(probes):
                    pat = f"{at}.probes[{j}]"
                    if not isinstance(probe, dict):
                        errors.append((pat, "必須是物件"))
                        continue
                    for extra in sorted(set(probe) - {"id", "description"}):
                        errors.append((f"{pat}.{extra}", "不允許的欄位"))
                    pid = probe.get("id")
                    if not (_is_int(pid) and 1 <= pid <= 15):
                        errors.append((f"{pat}.id", "須為 1～15 的整數"))
                    else:
                        if max_ok and pid > max_probes:
                            errors.append((f"{pat}.id", f"超過 max_probes {max_probes}"))
                        if pid in ids:
                            errors.append((f"{pat}.id", f"同一台內重複的探頭 id {pid}"))
                        ids.add(pid)
                    if "description" not in probe:
                        errors.append((f"{pat}.description", "必填"))
                    else:
                        _check_str(errors, f"{pat}.description", probe["description"], 1, 10)

        # 跨台不可重複：key、name、mac（不分大小寫）、ipv4
        for field in ("key", "name", "mac", "ipv4"):
            value = dev.get(field)
            if not isinstance(value, str):
                continue
            norm = value.upper() if field == "mac" else value
            if norm in seen[field]:
                errors.append((f"{at}.{field}", f"與 dl_en1[{seen[field][norm]}] 重複"))
            else:
                seen[field][norm] = i

    if errors:
        raise DefinitionError(errors)
    return devices


def load(path: Path, equip_net: ipaddress.IPv4Interface) -> list[dict]:
    try:
        definition = json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DefinitionError([(f"第 {exc.lineno} 行第 {exc.colno} 列", f"JSON 語法錯誤：{exc.msg}")])
    return validate(definition, equip_net)


def render_hosts(devices: list[dict]) -> str:
    """dnsmasq dhcp-hostsfile：每台一行 MAC,IPv4,key（DEF-03）。"""
    lines = ["# 由 DL-EN1 定義檔自動產生，請勿手動修改；修改請改定義檔後重新套用"]
    lines += [f"{d['mac'].lower()},{d['ipv4']},{d['key']}" for d in devices]
    return "\n".join(lines) + "\n"


def _atomic_write(path: Path, text: str) -> None:
    """先寫暫存檔再改名，斷電時檔案只會是完整的新檔或舊檔（UPL-07）。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp, 0o644)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def _backup(path: Path, keep: int = BACKUP_KEEP) -> Path | None:
    """備份舊檔（檔名含時間），只保留最近 keep 份（DEF-03）。"""
    if not path.exists():
        return None
    backup_dir = path.parent / "backup"
    backup_dir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    dest = backup_dir / f"{path.name}.{stamp}"
    shutil.copy2(path, dest)
    backups = sorted(backup_dir.glob(f"{path.name}.*"))
    for old in backups[:-keep]:
        old.unlink()
    return dest


def apply(devices: list[dict], hosts_path: Path, restart_cmd=RESTART_CMD) -> None:
    """備份 → 覆寫對應檔 → 重啟 dnsmasq；重啟失敗時還原舊檔並再次重啟（DEF-03）。"""
    hosts_path = Path(hosts_path)
    backup = _backup(hosts_path)
    _atomic_write(hosts_path, render_hosts(devices))
    if not restart_cmd:
        return
    result = subprocess.run(restart_cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return
    if backup is not None:
        shutil.copy2(backup, hosts_path)
    else:
        hosts_path.unlink(missing_ok=True)
    subprocess.run(restart_cmd, capture_output=True, text=True)
    raise RuntimeError(f"dnsmasq 重啟失敗，已還原 BOOTP 主機對應：{result.stderr.strip()}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="flatness.bootp", description=__doc__.splitlines()[0])
    parser.add_argument("action", choices=["check", "render", "apply"])
    parser.add_argument("--def", dest="def_file", required=True, type=Path, help="DL-EN1 定義檔")
    parser.add_argument("--equip-net", required=True, type=ipaddress.IPv4Interface,
                        help="量測 PC 設備網卡 IP/遮罩長度，例：192.168.10.1/24")
    parser.add_argument("--hosts", type=Path, help="apply：BOOTP 主機對應檔路徑")
    parser.add_argument("--no-restart", action="store_true", help="apply：只寫檔，不重啟 dnsmasq")
    args = parser.parse_args(argv)

    try:
        devices = load(args.def_file, args.equip_net)
    except DefinitionError as exc:
        print("DL-EN1 定義檔驗證失敗：", file=sys.stderr)
        for where, why in exc.errors:
            print(f"  {where}: {why}", file=sys.stderr)
        return 2

    if args.action == "check":
        print(f"OK：{len(devices)} 台 DL-EN1")
    elif args.action == "render":
        sys.stdout.write(render_hosts(devices))
    else:
        if args.hosts is None:
            parser.error("apply 需要 --hosts")
        try:
            apply(devices, args.hosts, restart_cmd=None if args.no_restart else RESTART_CMD)
        except RuntimeError as exc:
            print(exc, file=sys.stderr)
            return 1
        print(f"已寫入 {args.hosts}（{len(devices)} 台 DL-EN1）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
