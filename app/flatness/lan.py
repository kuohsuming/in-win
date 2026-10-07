"""設備網路上的設備（資料表 lan_device）與 DL-EN1 設定的規則（需求規格書 3.10 DSC、3.7 DEF）。

本模組只有資料與規則，不碰資料庫、檔案或網路：
    - LanDevice：lan_device 的一筆
    - definition_from / hosts_from：資料庫內容 → 定義檔與 BOOTP 主機對應（DSC-06、DEF-03）
    - validate：設備設定畫面與啟動時的檢查（3.7.1、DSC-04、DSC-08、DSC-09、DSC-11）
    - default_ip / occupant：預設 IP 與佔用者（DSC-08）
    - set_status / replace / move：設備設定的操作（DSC-03、DSC-14、DSC-15、EDT-01）
    - diff：差異預覽（UPL-05、畫面設計規格 5.10 步驟三）
    - import_definition：匯入定義檔（DEF-07、UPL）
"""

from __future__ import annotations

import copy
import ipaddress
import re
from dataclasses import dataclass, field, replace as dc_replace
from datetime import datetime

from . import bootp

UNCLASSIFIED, LIVE, MAINT, RETIRED, OTHER = (
    "unclassified", "dl_en1_live", "dl_en1_maint", "dl_en1_retired", "not_dl_en1")
STATUSES = (UNCLASSIFIED, LIVE, MAINT, RETIRED, OTHER)
STATUS_NAME = {UNCLASSIFIED: "不明設備", LIVE: "DL-EN1 使用中", MAINT: "DL-EN1 維修中",
               RETIRED: "DL-EN1 已停用", OTHER: "其他設備"}
STATUS_SHORT = {UNCLASSIFIED: "不明", LIVE: "使用中", MAINT: "維修中", RETIRED: "已停用", OTHER: "其他"}
# 清單排序（DSC-02）：不明設備 → 使用中 → 維修中 → 其他設備 → 已停用
STATUS_RANK = {UNCLASSIFIED: 0, LIVE: 1, MAINT: 2, OTHER: 3, RETIRED: 4}
DL_STATUSES = (LIVE, MAINT)

KEYENCE_PREFIX = "00:01:FC"
DEFAULT_RANGES = {"dl_en1": (11, 99), "other": (100, 199)}
MAX_LIVE = 8
# 位置標籤（DEF-01 key）：第 1～10 排，內部存成 row-1～row-10；每排最多一台，主畫面依排號由上而下排列
ROWS = 10
ROW_KEYS = tuple(f"row-{i}" for i in range(1, ROWS + 1))

_MAC_RE = re.compile(r"^([0-9A-F]{2}:){5}[0-9A-F]{2}$")


def normalize_mac(mac: str) -> str:
    """MAC 統一大寫、冒號分隔（DSC-01-A2）。"""
    mac = mac.strip().upper().replace("-", ":")
    if not _MAC_RE.match(mac):
        raise ValueError(f"MAC 格式錯誤：{mac}")
    return mac


def default_config() -> dict:
    """第一次設為 DL-EN1 時預先帶入的設定（畫面設計規格 5.10）。"""
    return {"key": "", "name": "", "max_probes": 4,
            "probes": [{"id": i + 1, "description": d} for i, d in enumerate(("左", "左中", "右中", "右"))]}


@dataclass
class LanDevice:
    mac: str
    status: str = UNCLASSIFIED
    first_seen: datetime | None = None
    last_seen: datetime | None = None
    seen_count: int = 0
    last_request: str | None = None
    hostname: str | None = None
    vendor_class: str | None = None
    seen_ip: str | None = None  # 設備實際使用的 IP（ARP 位址偵測封包，DSC-19）；不是配發的 IP
    ipv4: str | None = None
    config: dict | None = None  # lan_device.dl_en1_config：3.7.1 的 DL-EN1 物件去除 mac、ipv4
    sort_order: int | None = None
    hidden: bool = False
    hidden_at: datetime | None = None
    updated_at: datetime | None = None

    def copy(self) -> "LanDevice":
        return dc_replace(self, config=copy.deepcopy(self.config))

    @property
    def is_dl_en1(self) -> bool:
        return self.status in DL_STATUSES

    @property
    def assigns_ip(self) -> bool:
        """是否配發 IP（狀態表）：使用中、維修中、設有 IP 的其他設備。"""
        return bool(self.ipv4) and (self.status in DL_STATUSES or self.status == OTHER)

    @property
    def keyence(self) -> bool:
        return self.mac.upper().startswith(KEYENCE_PREFIX)

    @property
    def name(self) -> str | None:
        """清單上的名稱：DL-EN1 為排名稱（已停用者為原名稱）、其他為主機名稱。"""
        if self.status in (LIVE, MAINT, RETIRED) and self.config and self.config.get("name"):
            return self.config["name"]
        return self.hostname or None

    def label(self) -> str:
        """訊息中稱呼此設備：有名稱用名稱，否則用 MAC（5.10 檢查訊息）。"""
        return self.name or self.mac

    def settings(self) -> tuple:
        """會由設備設定寫回資料庫的欄位（比對是否有變更）。"""
        return (self.status, self.ipv4 or None, self.config, self.sort_order, self.hidden)

    def definition_entry(self) -> dict:
        """3.7.1 的 DL-EN1 物件（欄位順序與範例一致）。"""
        cfg = self.config or {}
        entry = {"key": cfg.get("key"), "name": cfg.get("name"), "mac": self.mac, "ipv4": self.ipv4}
        if cfg.get("port") is not None:
            entry["port"] = cfg["port"]
        entry["max_probes"] = cfg.get("max_probes")
        entry["probes"] = copy.deepcopy(cfg.get("probes"))
        return entry


def config_from_entry(entry: dict) -> dict:
    cfg = {"key": entry["key"], "name": entry["name"]}
    if "port" in entry:
        cfg["port"] = entry["port"]
    cfg["max_probes"] = entry["max_probes"]
    cfg["probes"] = copy.deepcopy(entry["probes"])
    return cfg


def live_devices(devices) -> list[LanDevice]:
    """「DL-EN1 使用中」依主畫面順序（排號）。"""
    return sorted((d for d in devices if d.status == LIVE), key=_row_key)


def screen_devices(devices) -> list[LanDevice]:
    """主畫面上的排：「使用中」與「維修中」，依位置標籤的排號由上而下（DSC-15、EDT-05）。"""
    return sorted((d for d in devices if d.status in DL_STATUSES), key=_row_key)


def screen_layout(devices) -> dict:
    """主畫面版面：定義檔格式，維修中的設備另加 "maint": True（只在 App 內部使用，不寫入定義檔）。"""
    out = []
    for d in screen_devices(devices):
        entry = d.definition_entry()
        if d.status == MAINT:
            entry["maint"] = True
        out.append(entry)
    return {"version": 1, "dl_en1": out}


def row_no(key) -> int | None:
    """row-3 → 3；不是位置標籤時回傳 None。"""
    return ROW_KEYS.index(key) + 1 if key in ROW_KEYS else None


def row_label(key) -> str:
    n = row_no(key)
    return f"第 {n} 排" if n else (key or "未設定")


def free_row(devices, exclude_mac: str | None = None) -> str | None:
    """最小的未使用位置（使用中、維修中佔用；已停用不佔用，DSC-09）。"""
    used = {(d.config or {}).get("key") for d in devices if d.status in DL_STATUSES and d.mac != exclude_mac}
    return next((k for k in ROW_KEYS if k not in used), None)


def _row_key(d: LanDevice):
    """主畫面順序：依位置標籤的排號（EDT-05）；與設定頁清單順序（DSC-17）無關。"""
    return (row_no((d.config or {}).get("key")) or ROWS + 1, _list_key(d))


def _list_key(d: LanDevice):
    """設備清單順序（DSC-02、DSC-17）：所有設備共用一個順序（`sort_order`），不分設備類型。

    1. 尚未排序的不明設備（新偵測到）在最上面，最近出現的在前
    2. 已排序的設備依 `sort_order`
    3. 舊資料中尚未排序的其他設備：依設備類型、最近出現；第一次調整順序時全部重新編號
    """
    ts = -d.last_seen.timestamp() if d.last_seen else float("inf")
    if d.sort_order is None and d.status == UNCLASSIFIED:
        return (0, 0, ts, d.mac)
    if d.sort_order is not None:
        return (1, d.sort_order, 0, d.mac)
    return (2, STATUS_RANK[d.status], ts, d.mac)


def list_order(devices) -> list[LanDevice]:
    return sorted(devices, key=_list_key)


def definition_from(devices) -> dict:
    """App 定義檔：只含「DL-EN1 使用中」，依畫面順序（DSC-06）。"""
    return {"version": 1, "dl_en1": [d.definition_entry() for d in live_devices(devices)]}


def hosts_from(devices) -> list[dict]:
    """BOOTP 主機對應：使用中 ＋ 維修中 ＋ 設有 IP 的其他設備（DSC-06、DEF-03）。"""
    rows = []
    # 依狀態與 IP 排序，與畫面順序無關：調整順序（DSC-17）不改變主機對應，不需重新啟動 dnsmasq
    def by_ip(d):
        try:
            return int(ipaddress.IPv4Address(d.ipv4))
        except (ipaddress.AddressValueError, ValueError, TypeError):
            return 0
    for d in sorted(devices, key=lambda d: (STATUS_RANK[d.status], by_ip(d), d.mac)):
        if d.assigns_ip:
            rows.append({"mac": d.mac, "ipv4": d.ipv4,
                         "key": (d.config or {}).get("key") if d.is_dl_en1 else None})
    return rows


def render_hosts(devices) -> str:
    """dnsmasq dhcp-hostsfile：每台一行 mac,ip[,名稱]；名稱只寫 DL-EN1 的 key。"""
    lines = ["# 由 App 依資料庫 lan_device 產生（DSC-06），請勿手動修改；請在 App「設備設定」修改"]
    for h in hosts_from(devices):
        lines.append(",".join(x for x in (h["mac"].lower(), h["ipv4"], h["key"]) if x))
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- 檢查

FIELD_NAME = {"key": "位置", "name": "排名稱", "ipv4": "IPv4", "port": "TCP 埠",
              "max_probes": "最多探頭數", "probes": "探頭", "status": "設備"}


@dataclass
class Issue:
    """檢查訊息：「✘ 設備名稱 › 欄位：訊息」（5.10）。mac 為 None 表示整體規則。"""
    mac: str | None
    field: str
    message: str
    who: str = ""

    def text(self) -> str:
        where = f"{self.who} › " if self.who else ""
        return f"{where}{FIELD_NAME.get(self.field, self.field)}：{self.message}"


def ip_problem(ip: str, equip_net: ipaddress.IPv4Interface) -> str | None:
    """IP 本身的問題（不含重複）：格式、網段、網路／廣播位址、量測 PC（3.7.1、DSC-08）。"""
    try:
        addr = ipaddress.IPv4Address(ip)
    except (ipaddress.AddressValueError, ValueError):
        return "不是有效的 IPv4 位址"
    net = equip_net.network
    if addr not in net:
        return f"IP 不在設備網段 {net}"
    if addr in (net.network_address, net.broadcast_address):
        return "不可為網路位址或廣播位址"
    if addr == equip_net.ip:
        return "不可與量測 PC 相同"
    return None


def occupant(devices, ip: str, exclude_mac: str | None = None) -> LanDevice | None:
    """資料表中（含尚未套用的編輯）使用此 IP 的設備；已停用者不佔用（DSC-08、DSC-09）。"""
    for d in devices:
        if d.mac != exclude_mac and d.assigns_ip and d.ipv4 == ip:
            return d
    return None


def occupied_text(d: LanDevice) -> str:
    """DSC-08：「已由 {狀態} {MAC}（{名稱}）使用」。"""
    name = f"（{d.name}）" if d.name else ""
    return f"已由 {STATUS_NAME[d.status]} {d.mac}{name}使用"


def _entry_issues(d: LanDevice, equip_net) -> list[tuple[str, str]]:
    """以 3.7.1 的規則檢查一台 DL-EN1（沿用 bootp.validate，與定義檔驗證完全一致）。"""
    entry = d.definition_entry()
    entry = {k: v for k, v in entry.items() if v is not None or k in ("key", "name", "max_probes", "probes")}
    try:
        bootp.validate({"version": 1, "dl_en1": [entry]}, equip_net)
    except bootp.DefinitionError as exc:
        out = []
        for where, why in exc.errors:
            fld = where.removeprefix("dl_en1[0].") if where.startswith("dl_en1[0].") else where
            m = re.match(r"probes\[(\d+)\]\.(id|description)", fld)
            if m:
                pid = (entry.get("probes") or [])[int(m.group(1))].get("id")
                what = "探頭 ID" if m.group(2) == "id" else "位置名稱"
                out.append(("probes", f"第 {int(m.group(1)) + 1} 列（ID {pid}）{what}{why}"))
            elif fld == "ipv4":
                continue  # IP 由 ip_problem 檢查，訊息較具體
            elif fld == "key":
                out.append(("key", f"請選擇第 1～{ROWS} 排其中一排"))
            else:
                out.append((fld.split(".")[0], why))
        return out
    return []


def validate(devices, equip_net: ipaddress.IPv4Interface) -> list[Issue]:
    """設備設定的全部檢查（畫面設計規格 5.10「檢查規則」）；空 list 表示可以儲存。"""
    devices = list(devices)
    issues: list[Issue] = []

    live = [d for d in devices if d.status == LIVE]
    if len(live) > MAX_LIVE:  # 0 台允許（例如刪除最後一台，DSC-18）：主畫面顯示尚未設定、無法量測
        issues.append(Issue(None, "status", f"DL-EN1 使用中最多 {MAX_LIVE} 台（目前 {len(live)} 台）"))

    groups: dict[tuple[str, str], list[LanDevice]] = {}
    for d in list_order(devices):
        who = d.label()
        if d.is_dl_en1:
            if not d.config:
                issues.append(Issue(d.mac, "key", "尚未設定", who))
            else:
                for fld, why in _entry_issues(d, equip_net):
                    issues.append(Issue(d.mac, fld, why, who))
            if not d.ipv4:
                issues.append(Issue(d.mac, "ipv4", "必填", who))
            for fld in ("key", "name"):
                value = (d.config or {}).get(fld)
                if value:
                    groups.setdefault((fld, value), []).append(d)
        if d.assigns_ip:
            problem = ip_problem(d.ipv4, equip_net)
            if problem:
                issues.append(Issue(d.mac, "ipv4", problem, who))
            else:
                groups.setdefault(("ipv4", d.ipv4), []).append(d)

    # 不可重複：衝突的每一台都標示，並說明被哪台設備使用（DSC-08-A4）
    for (fld, value), devs in groups.items():
        if len(devs) < 2:
            continue
        for d in devs:
            other = next(x for x in devs if x is not d)
            shown = value if fld == "ipv4" else row_label(value) if fld == "key" else f"「{value}」"
            issues.append(Issue(d.mac, fld, f"{shown} {occupied_text(other)}", d.label()))
    return issues


def out_of_net(devices, equip_net) -> list[LanDevice]:
    """IP 不在目前設備網段的配發設備（DSC-11）。"""
    net = equip_net.network
    out = []
    for d in devices:
        if d.assigns_ip:
            try:
                if ipaddress.IPv4Address(d.ipv4) not in net:
                    out.append(d)
            except ValueError:
                out.append(d)
    return out


def usable_seen_ip(devices, d: LanDevice, equip_net: ipaddress.IPv4Interface) -> str | None:
    """設備實際使用的 IP（DSC-19）可直接沿用時回傳：在網段內、不是網路／廣播位址或量測 PC、
    未被其他設備佔用（DSC-08）。沿用它，設備不必重設即可使用。"""
    ip = d.seen_ip
    if not ip or ip_problem(ip, equip_net) or occupant(devices, ip, exclude_mac=d.mac):
        return None
    return ip


def seen_ip_problem(seen_ip: str | None, equip_net: ipaddress.IPv4Interface) -> str | None:
    """設備實際使用的 IP（DSC-19）本身的問題：不在設備網段（網段取自設備網卡，DSC-08）、
    網路／廣播位址、與量測 PC 相同。這樣的設備量測 PC 連不到，須重設後以 BOOTP 取得 IP。"""
    return ip_problem(seen_ip, equip_net) if seen_ip else None


def ip_mismatch(seen_ip: str | None, ipv4: str | None) -> bool:
    """設備實際使用的 IP 與設定（配發）的 IP 不同（DSC-19、DSC-20）。"""
    return bool(seen_ip and ipv4 and seen_ip != ipv4)


def default_ip(devices, kind: str, equip_net: ipaddress.IPv4Interface,
               ranges: dict | None = None, exclude_mac: str | None = None) -> str | None:
    """依設備類型的預設範圍取最小未佔用位址；範圍滿了改取網段內其他最小未佔用位址（DSC-08）。

    kind 為 "dl_en1" 或 "other"；回傳 None 表示網段已無可用位址。
    """
    ranges = ranges or DEFAULT_RANGES
    net = equip_net.network
    taken = {d.ipv4 for d in devices if d.assigns_ip and d.mac != exclude_mac}
    taken |= {str(net.network_address), str(net.broadcast_address), str(equip_net.ip)}
    base = int(net.network_address)
    lo, hi = ranges[kind]

    def free(n: int) -> str | None:
        ip = ipaddress.IPv4Address(base + n)
        return str(ip) if ip in net and str(ip) not in taken else None

    for n in range(lo, hi + 1):
        if ip := free(n):
            return ip
    for host in net.hosts():
        if str(host) not in taken:
            return str(host)
    return None


# ---------------------------------------------------------------- 操作（作用在編輯中的副本）

def next_sort_order(devices) -> int:
    return max((d.sort_order or 0 for d in devices), default=0) + 1


def set_status(devices, mac: str, status: str, equip_net, ranges=None,
               remembered: dict | None = None) -> LanDevice:
    """變更設備類型（DSC-03、DSC-09、DSC-15），回傳變更後的設備。

    remembered：本次編輯中曾有的 DL-EN1 設定（mac → config），切換類型後再切回時帶回。
    """
    d = next(x for x in devices if x.mac == mac)
    before = d.status
    if before == status:
        return d
    if d.config and before in (LIVE, MAINT, RETIRED) and remembered is not None:
        remembered[mac] = copy.deepcopy(d.config)
    d.status = status

    if status in DL_STATUSES:
        if not d.config:
            d.config = copy.deepcopy((remembered or {}).get(mac)) or default_config()
        if not d.config.get("key"):
            d.config["key"] = free_row(devices, exclude_mac=mac) or ""  # 預設最小的空位（EDT-05）
        # 改變設備類型時清單位置不變（DSC-17）；尚未排序者（新偵測到）排到最後一位
        if d.sort_order is None:
            d.sort_order = next_sort_order([x for x in devices if x is not d])
        d.hidden, d.hidden_at = False, None  # DSC-13：設為使用中或維修中時自動取消隱藏
        if not d.ipv4:  # 優先沿用設備實際使用的 IP（DSC-08、DSC-19），設備不必重設
            d.ipv4 = (usable_seen_ip(devices, d, equip_net)
                      or default_ip(devices, "dl_en1", equip_net, ranges, exclude_mac=mac))
    elif status == OTHER:
        d.config = None  # 其他設備只能設定 IP（DSC-04）
        if not d.ipv4:
            d.ipv4 = (usable_seen_ip(devices, d, equip_net)
                      or default_ip(devices, "other", equip_net, ranges, exclude_mac=mac))
    elif status == RETIRED:
        pass  # 保留最後的設定與 IP 供查詢，但不配發、不佔用（DSC-09）
    elif status == UNCLASSIFIED:
        d.config, d.ipv4 = None, None
    return d


def replace(devices, old_mac: str, new_mac: str) -> LanDevice:
    """替換（DSC-14）：新機取得舊機全部設定並設為使用中；舊機改為已停用並保留原設定。"""
    old = next(x for x in devices if x.mac == old_mac)
    new = next(x for x in devices if x.mac == new_mac)
    if old.status != LIVE:
        raise ValueError("只能替換「DL-EN1 使用中」的設備")
    if new is old or new.status == LIVE:
        raise ValueError("新機不可為使用中，也不可與舊機相同")
    new_pos = new.sort_order
    new.status, new.config, new.ipv4, new.sort_order = LIVE, copy.deepcopy(old.config), old.ipv4, old.sort_order
    new.hidden, new.hidden_at = False, None
    old.status = RETIRED
    # 舊機移到新機原本的位置，順序不重複
    old.sort_order = new_pos if new_pos is not None else next_sort_order(devices)
    return new


def replace_candidates(devices, old_mac: str) -> list[LanDevice]:
    """替換的新機候選：不明、其他、已停用；KEYENCE 優先、最近出現的在前（DSC-14）。"""
    cands = [d for d in devices if d.mac != old_mac and d.status in (UNCLASSIFIED, OTHER, RETIRED)]
    return sorted(cands, key=lambda d: (not d.keyence, -(d.last_seen.timestamp() if d.last_seen else 0)))


def renumber(devices, order=None) -> None:
    """依目前清單順序（或指定的 MAC 順序）重新編號 1～N。"""
    by = {d.mac: d for d in devices}
    macs = order if order is not None else [d.mac for d in list_order(devices)]
    macs = [m for m in macs if m in by] + [d.mac for d in list_order(devices) if d.mac not in set(macs)]
    for i, m in enumerate(macs):
        by[m].sort_order = i + 1


def move(devices, mac: str, step: int, visible=None) -> bool:
    """上移／下移（DSC-17）：任何設備皆可，與清單上相鄰的設備交換位置；回傳是否有移動。

    visible：畫面上看得到的 MAC（隱藏的設備不顯示時略過）；None 表示全部。
    第一次調整時若有尚未排序或重複的順序，先依目前清單順序全部重新編號。
    """
    devices = list(devices)
    order = list_order(devices)
    nums = [d.sort_order for d in order]
    if None in nums or len(set(nums)) != len(nums):
        renumber(devices, [d.mac for d in order])
    shown = [d for d in order if visible is None or d.mac in visible]
    idx = next((i for i, d in enumerate(shown) if d.mac == mac), None)
    if idx is None or not 0 <= idx + step < len(shown):
        return False
    a, b = shown[idx], shown[idx + step]
    a.sort_order, b.sort_order = b.sort_order, a.sort_order
    return True


def import_definition(devices, definition: dict) -> list[LanDevice]:
    """匯入定義檔（DEF-07、UPL）：檔案中的 DL-EN1 設為使用中，原本使用中但不在檔案內者設為已停用。

    回傳新的設備清單（副本）；檔案中尚未出現過的 MAC 新增一筆（first_seen 為 NULL）。
    """
    out = {d.mac: d.copy() for d in devices}
    in_file = set()
    for i, entry in enumerate(definition["dl_en1"]):
        mac = normalize_mac(entry["mac"])
        in_file.add(mac)
        d = out.setdefault(mac, LanDevice(mac=mac))
        d.status, d.config, d.ipv4, d.sort_order = LIVE, config_from_entry(entry), entry["ipv4"], i + 1
        d.hidden, d.hidden_at = False, None
    for d in out.values():
        if d.status == LIVE and d.mac not in in_file:
            d.status = RETIRED
    # 檔案中的 DL-EN1 依檔案順序排在最前，其餘設備維持原本的相對順序
    file_order = [normalize_mac(e["mac"]) for e in definition["dl_en1"]]
    rest = [d.mac for d in list_order(devices) if d.mac not in in_file]
    renumber(list(out.values()), file_order + rest)
    return list(out.values())


# ---------------------------------------------------------------- 差異預覽

@dataclass
class ChangeItem:
    tag: str                      # 替換／變更／順序／新增
    title: str
    lines: list[tuple[str, bool]] = field(default_factory=list)  # (文字, 醒目)


@dataclass
class Preview:
    items: list[ChangeItem] = field(default_factory=list)
    power_cycle: list[str] = field(default_factory=list)       # 需重新上電才會取得新 IP
    no_standard: list[str] = field(default_factory=list)       # 尚未設定允收標準的探頭
    removed_points: list[str] = field(default_factory=list)    # 將從主畫面移除的量測點
    paused_points: list[str] = field(default_factory=list)     # 改為維修中、暫停量測的量測點（DSC-15）
    replaced: list[tuple[str, str, str]] = field(default_factory=list)  # (key, 舊 MAC, 新 MAC)

    @property
    def empty(self) -> bool:
        return not self.items

    def summary(self) -> str:
        return "；".join(f"{i.tag} {i.title}" for i in self.items) or "無變更"


def _title(d: LanDevice) -> str:
    cfg = d.config or {}
    if d.is_dl_en1 or (d.status == RETIRED and cfg):
        return f"{cfg.get('name') or '（未命名）'}（{cfg.get('key') or '—'}）"
    return f"{d.hostname or STATUS_NAME[d.status]} {d.mac}"


def _probes(cfg) -> dict:
    return {p["id"]: p["description"] for p in (cfg or {}).get("probes") or []}


def diff(old_devices, new_devices, standards: dict | None = None) -> Preview:
    """以 MAC 對應新舊資料，列出要確認的變更與影響（5.10 步驟三、UPL-05）。

    standards：{key: {probe_id: ...}}，用來列出尚未設定允收標準的探頭（DEF-09）。
    """
    old = {d.mac: d for d in old_devices}
    new = {d.mac: d for d in new_devices}
    p = Preview()
    handled: set[str] = set()

    # 替換：新機成為使用中且接手某台舊機的 key，舊機改為已停用
    for n in new.values():
        o_self = old.get(n.mac)
        if n.status != LIVE or (o_self and o_self.status == LIVE):
            continue
        key = (n.config or {}).get("key")
        for o in old.values():
            if (o.status == LIVE and o.mac != n.mac and (o.config or {}).get("key") == key
                    and new.get(o.mac) and new[o.mac].status == RETIRED):
                item = ChangeItem("替換", _title(n), [
                    (f"MAC {o.mac} → {n.mac}", True),
                    ("IP、埠、探頭、順序沿用" if n.config == o.config and n.ipv4 == o.ipv4
                     else "設定已修改，見下方", False),
                    (f"舊機改為「{STATUS_NAME[RETIRED]}」並保留原設定", True),
                ])
                p.items.append(item)
                p.power_cycle.append(f"{_title(n)} 新機 {n.mac}（{n.ipv4}）")
                p.replaced.append((key, o.mac, n.mac))
                handled |= {n.mac, o.mac}
                break

    for mac, n in new.items():
        o = old.get(mac)
        if o is None:
            o = LanDevice(mac=mac)
        lines: list[tuple[str, bool]] = []
        if mac not in handled and o.status != n.status:
            lines.append((f"設備：{STATUS_NAME[o.status]} → {STATUS_NAME[n.status]}", True))
        ip_old = o.ipv4 if o.assigns_ip else None
        ip_new = n.ipv4 if n.assigns_ip else None
        if mac not in handled and ip_old != ip_new:
            lines.append((f"IP：{ip_old or '不配發'} → {ip_new or '不配發'}", True))
        if ip_new and ip_new != ip_old and mac not in handled:
            p.power_cycle.append(f"{_title(n)}（{ip_new}）")
        if n.is_dl_en1 and o.is_dl_en1 and mac not in handled:
            co, cn = o.config or {}, n.config or {}
            for fld, nm in (("key", "位置"), ("name", "排名稱"), ("port", "埠"), ("max_probes", "最多探頭數")):
                a, b = co.get(fld), cn.get(fld)
                if fld == "key":
                    a, b = row_label(a), row_label(b)
                if fld == "port":
                    a, b = a or bootp.DEFAULT_PORT, b or bootp.DEFAULT_PORT
                if a != b:
                    lines.append((f"{nm}：{a} → {b}", False))
            pa, pb = _probes(co), _probes(cn)
            for pid in sorted(pb.keys() - pa.keys()):
                lines.append((f"新增探頭 ID {pid}「{pb[pid]}」", False))
            for pid in sorted(pa.keys() - pb.keys()):
                lines.append((f"移除探頭 ID {pid}「{pa[pid]}」", False))
            for pid in sorted(pa.keys() & pb.keys()):
                if pa[pid] != pb[pid]:
                    lines.append((f"探頭 ID {pid} 名稱：{pa[pid]} → {pb[pid]}", False))
        elif n.is_dl_en1 and not o.is_dl_en1 and mac not in handled:
            cn = n.config or {}
            lines.append((f"識別碼 {cn.get('key')}、排名稱 {cn.get('name')}、"
                          f"{len(cn.get('probes') or [])} 個探頭", False))
        if lines:
            tag = "新增" if o.status == UNCLASSIFIED and n.is_dl_en1 else "變更"
            p.items.append(ChangeItem(tag, _title(n), lines))

    old_order = [d.mac for d in screen_devices(old.values()) if new.get(d.mac) and new[d.mac].is_dl_en1]
    new_order = [d.mac for d in screen_devices(new.values()) if old.get(d.mac) and old[d.mac].is_dl_en1]
    if old_order != new_order:
        p.items.append(ChangeItem("順序", "主畫面排列順序", [
            (" → ".join(_title(new[m]) for m in new_order), False)]))

    # 影響：將從主畫面移除的量測點、尚未設定允收標準的探頭（以 key ＋ 探頭 id 識別量測點，DEF-08）
    def points(devs):
        out = {}
        for d in live_devices(devs):
            cfg = d.config or {}
            for pid, desc in _probes(cfg).items():
                out[(cfg.get("key"), pid)] = f"{cfg.get('name')} {desc}"
        return out
    po, pn = points(old.values()), points(new.values())
    maint_keys = {(d.config or {}).get("key") for d in new.values() if d.status == MAINT}
    p.paused_points = [po[k] for k in po if k not in pn and k[0] in maint_keys]
    p.removed_points = [po[k] for k in po if k not in pn and k[0] not in maint_keys]
    if standards is not None:
        p.no_standard = [pn[k] for k in pn if not (standards.get(k[0]) or {}).get(k[1])]
    return p
