"""資料庫 → 定義檔與 BOOTP 主機對應（DSC-06），以及設備設定的套用（DSC-03、DSC-12、UPL-06～UPL-08）。

App 啟動與設備設定套用共用同一套產生程序：
    啟動：讀資料庫 → 檢查 → 內容不同才備份並原子覆寫（相同則不改寫）
          資料庫無法連線或檢查失敗：不改寫，沿用現有檔案並回報原因（DSC-06、DSC-11）
    套用：檢查 → 交易內寫入資料庫 → 備份並覆寫兩個檔案 → 主機對應有變更時重新啟動 dnsmasq
          任一步失敗：檔案還原、資料庫 ROLLBACK（DSC-14-A3、UPL-08）
"""

from __future__ import annotations

import ipaddress
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

from . import bootp, definition, lan
from .store import StoreError

log = logging.getLogger(__name__)


@dataclass
class Files:
    def_path: Path    # /etc/flatness/dl-en1.json
    hosts_path: Path  # /var/lib/flatness/bootp/dl-en1.hosts


class SyncError(RuntimeError):
    def __init__(self, message: str, issues: list | None = None):
        super().__init__(message)
        self.issues = issues or []


def render(devices, equip_net: ipaddress.IPv4Interface) -> tuple[dict, str, str]:
    """檢查並產生（定義檔內容, 定義檔文字, 主機對應文字）；不合格拋出 SyncError。"""
    issues = lan.validate(devices, equip_net)
    if issues:
        outside = lan.out_of_net(devices, equip_net)
        if outside:
            names = "、".join(d.label() for d in outside)
            msg = (f"設備設定有 {len(outside)} 台設備的 IP 不在設備網段 {equip_net.network}，"
                   f"沿用上次的設定：{names}")
        else:
            msg = "設備設定有錯誤，沿用上次的設定：" + "；".join(i.text() for i in issues[:5])
        raise SyncError(msg, issues)
    defn = lan.definition_from(devices)
    errors = definition.validate(defn, equip_net)  # 3.7.1 JSON Schema 把關（DEF-02）
    if errors:
        raise SyncError("定義檔驗證失敗：" + "；".join(f"{w}: {r}" for w, r in errors[:5]),
                        [lan.Issue(None, w, r) for w, r in errors])
    return defn, definition.dumps(defn), lan.render_hosts(devices)


def _read(path: Path) -> str | None:
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return None


def _write(path: Path, text: str) -> bool:
    """內容相同時不改寫（DSC-06-A4）；不同時先備份再原子覆寫（UPL-06、UPL-07）。"""
    if _read(path) == text:
        return False
    bootp.backup_file(Path(path))
    bootp.atomic_write(Path(path), text)
    return True


def _restore(path: Path, text: str | None):
    if text is None:
        Path(path).unlink(missing_ok=True)
    else:
        bootp.atomic_write(Path(path), text)


@dataclass
class StartupResult:
    definition: dict                       # 連線使用的定義檔內容（只含使用中）
    devices: list | None = None            # 資料庫內容；無法讀取時為 None
    changed: bool = False                  # 是否改寫了檔案
    problem: str | None = None             # 畫面要顯示的原因（DSC-06、DSC-11）
    db_ok: bool = True
    issues: list = field(default_factory=list)
    layout: dict | None = None             # 主畫面版面（使用中 ＋ 維修中）；資料庫無法讀取時同定義檔

    def __post_init__(self):
        if self.layout is None:
            self.layout = self.definition


def load_existing(files: Files) -> dict:
    """讀取現有定義檔；不存在或格式錯誤時回傳空清單。"""
    try:
        defn = definition.load_definition(files.def_path)
        return defn if isinstance(defn.get("dl_en1"), list) else definition.empty_definition()
    except (bootp.DefinitionError, AttributeError):
        return definition.empty_definition()


def startup(store, files: Files, equip_net: ipaddress.IPv4Interface) -> StartupResult:
    """App 啟動時依資料庫產生兩個檔案（DSC-06）；之後由呼叫端啟動 dnsmasq（DSC-07）。"""
    try:
        devices = store.load()
    except StoreError as exc:
        log.error("啟動：無法讀取資料庫，沿用現有定義檔與 BOOTP 主機對應：%s", exc)
        return StartupResult(load_existing(files), None, False,
                             "無法讀取資料庫，使用上次的設定", db_ok=False)
    try:
        defn, def_text, hosts_text = render(devices, equip_net)
    except SyncError as exc:
        log.error("啟動：%s", exc)
        defn = load_existing(files)
        return StartupResult(defn, devices, False, str(exc), issues=exc.issues)
    changed = _write(files.def_path, def_text)
    changed = _write(files.hosts_path, hosts_text) or changed
    log.info("啟動：依資料庫產生定義檔與 BOOTP 主機對應（%s）DL-EN1 %d 台",
             "已更新" if changed else "內容相同，未改寫", len(defn["dl_en1"]))
    return StartupResult(defn, devices, changed, layout=lan.screen_layout(devices))


@dataclass
class ApplyResult:
    definition: dict
    restarted: bool
    layout: dict | None = None             # 主畫面版面（使用中 ＋ 維修中）


def apply(store, files: Files, equip_net: ipaddress.IPv4Interface, old_devices, new_devices,
          restart=None, summary: str = "") -> ApplyResult:
    """套用設備設定；失敗時資料庫與檔案皆還原並拋出例外（UPL-08、UPL-12）。

    restart：以新主機對應重新啟動 dnsmasq 的函式，失敗時拋出例外；None 表示不重新啟動（開發用）。
    """
    defn, def_text, hosts_text = render(new_devices, equip_net)
    before = {files.def_path: _read(files.def_path), files.hosts_path: _read(files.hosts_path)}
    hosts_changed = before[files.hosts_path] != hosts_text
    try:
        with store.transaction() as tx:
            n = tx.save(old_devices, new_devices)
            try:
                _write(files.def_path, def_text)
                _write(files.hosts_path, hosts_text)
                if hosts_changed and restart:
                    restart()
            except BaseException:
                for path, text in before.items():
                    _restore(path, text)
                if hosts_changed and restart:
                    try:
                        restart()  # 以還原後的主機對應再啟動，DL-EN1 仍可取得原 IP
                    except Exception as exc:
                        log.error("還原後重新啟動 dnsmasq 仍失敗：%s", exc)
                raise
    except Exception as exc:
        log.error("套用設備設定失敗，資料庫與檔案已還原：%s；變更=%s", exc, summary)
        raise
    log.info("套用設備設定成功：資料庫 %d 筆；變更=%s；dnsmasq %s", n, summary,
             "已重新啟動" if hosts_changed and restart else "未重新啟動")
    return ApplyResult(defn, hosts_changed and restart is not None, lan.screen_layout(new_devices))


def backups(files: Files, keep: int = bootp.BACKUP_KEEP) -> list[Path]:
    """定義檔備份，新的在前（UPL-10）。"""
    d = Path(files.def_path).parent / "backup"
    return sorted(d.glob(f"{Path(files.def_path).name}.*"), reverse=True)[:keep]


def read_definition_file(path: Path, equip_net, max_bytes: int = 64 * 1024) -> dict:
    """讀取並驗證要匯入的定義檔（UPL-03、UPL-04）；不合格拋出 bootp.DefinitionError。"""
    path = Path(path)
    if path.suffix.lower() != ".json" and "backup" not in path.parts:
        raise bootp.DefinitionError([(path.name, "只接受副檔名 .json 的檔案")])
    if path.stat().st_size > max_bytes:
        raise bootp.DefinitionError([(path.name, "檔案超過 64 KB")])
    try:
        text = path.read_bytes().decode("utf-8")
    except UnicodeDecodeError:
        raise bootp.DefinitionError([(path.name, "檔案不是 UTF-8 編碼")])
    try:
        defn = json.loads(text)
    except json.JSONDecodeError as exc:
        raise bootp.DefinitionError([(f"第 {exc.lineno} 行第 {exc.colno} 列", f"JSON 語法錯誤：{exc.msg}")])
    errors = definition.validate(defn, equip_net)
    if errors:
        raise bootp.DefinitionError(errors)
    return defn
