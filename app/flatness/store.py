"""資料表 lan_device 的讀寫（DSC-01、DSC-05、DSC-12、DSC-13）。

MySQLStore 為正式實作；MemoryStore 供測試與無資料庫的開發使用，行為相同。
App 帳號只有 SELECT、INSERT、UPDATE（INS-05），因此這裡沒有刪除。

每次操作各自建立連線：探索執行緒與畫面同時使用時不共用連線，資料庫重新啟動後也不需重連邏輯。
"""

from __future__ import annotations

import contextlib
import copy
import json
import threading
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .lan import UNCLASSIFIED, LanDevice


class StoreError(RuntimeError):
    """資料庫無法連線或寫入失敗。"""


@dataclass
class SeenEvent:
    """探索到的一個請求封包（DSC-01、DSC-19）；count 為 0 表示只補主機名稱或廠商識別。"""
    mac: str
    kind: str                    # "BOOTP"、"DHCP" 或 "ARP"（位址偵測封包）
    at: datetime
    hostname: str | None = None
    vendor_class: str | None = None
    count: int = 1
    ip: str | None = None        # ARP：設備實際使用的 IP（DSC-19）


def read_env(path: Path) -> dict:
    """讀取 db.env（KEY=VALUE，每行一項）。"""
    out = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


class MemoryStore:
    """記憶體內的 lan_device；available=False 模擬資料庫無法連線。"""

    def __init__(self, devices=()):
        self._rows = {d.mac: d.copy() for d in devices}
        self._lock = threading.RLock()
        self.available = True
        self.inspections: dict[str, tuple[dict, list[dict]]] = {}  # serial → (主檔, 明細)
        self.calibrations: list[dict] = []

    def _check(self):
        if not self.available:
            raise StoreError("無法連線資料庫（測試）")

    def load(self) -> list[LanDevice]:
        with self._lock:
            self._check()
            return [d.copy() for d in self._rows.values()]

    def record(self, events) -> None:
        with self._lock:
            self._check()
            for e in events:
                d = self._rows.get(e.mac)
                if d is None:
                    d = self._rows[e.mac] = LanDevice(mac=e.mac, updated_at=e.at)
                if e.count:
                    d.first_seen = d.first_seen or e.at
                    d.last_seen = max(d.last_seen or e.at, e.at)
                    d.seen_count += e.count
                    d.last_request = e.kind
                    if d.status == UNCLASSIFIED:  # DSC-13：不明設備再次出現時自動取消隱藏
                        d.hidden, d.hidden_at = False, None
                d.hostname = e.hostname or d.hostname
                d.vendor_class = e.vendor_class or d.vendor_class
                d.seen_ip = e.ip or d.seen_ip

    def write_inspection(self, head: dict, points: list[dict]) -> bool:
        with self._lock:
            self._check()
            if head["serial"] in self.inspections:
                return False
            self.inspections[head["serial"]] = (dict(head, written_at=datetime.now()), [dict(p) for p in points])
            return True

    def write_calibration(self, rec: dict) -> None:
        with self._lock:
            self._check()
            self.calibrations.append(dict(rec))

    def count_inspections(self, day) -> int:
        with self._lock:
            self._check()
            return sum(1 for h, _ in self.inspections.values() if h["measured_at"].date() == day)

    def set_hidden(self, mac: str, hidden: bool) -> None:
        with self._lock:
            self._check()
            d = self._rows[mac]
            d.hidden, d.hidden_at = hidden, (datetime.now() if hidden else None)

    @contextlib.contextmanager
    def transaction(self):
        """寫入設定；區塊內拋出例外時全部還原（DSC-03、UPL-08）。"""
        with self._lock:
            self._check()
            snapshot = {m: d.copy() for m, d in self._rows.items()}
            tx = _MemoryTx(self._rows)
            try:
                yield tx
            except BaseException:
                self._rows.clear()
                self._rows.update(snapshot)
                raise


class _MemoryTx:
    def __init__(self, rows):
        self._rows = rows

    def save(self, old_devices, new_devices) -> int:
        old = {d.mac: d for d in old_devices}
        n = 0
        for d in new_devices:
            o = old.get(d.mac)
            if o is not None and o.settings() == d.settings():
                continue
            row = self._rows.get(d.mac)
            if row is None:
                row = self._rows[d.mac] = LanDevice(mac=d.mac)
            row.status, row.ipv4, row.config = d.status, d.ipv4 or None, copy.deepcopy(d.config)
            row.sort_order, row.hidden, row.hidden_at = d.sort_order, d.hidden, d.hidden_at
            row.updated_at = datetime.now()
            n += 1
        return n

    def delete(self, macs) -> int:
        """從 lan_device 刪除（DSC-18）；之後再出現時以不明設備重新建立。"""
        n = 0
        for mac in macs:
            n += self._rows.pop(mac, None) is not None
        return n


_COLUMNS = ("mac, status, first_seen, last_seen, seen_count, last_request, hostname, vendor_class, "
            "seen_ip, ipv4, dl_en1_config, sort_order, hidden, hidden_at, updated_at")


class MySQLStore:
    """MySQL 的 lan_device（3.10 資料表）。"""

    def __init__(self, *, database: str, user: str, password: str,
                 host: str = "localhost", port: int = 3306, unix_socket: str | None = None,
                 connect_timeout: int = 3):
        self._args = dict(database=database, user=user, password=password, host=host, port=port,
                          unix_socket=unix_socket, connect_timeout=connect_timeout,
                          read_timeout=10, write_timeout=10, charset="utf8mb4", autocommit=False)

    @classmethod
    def from_env(cls, path: Path) -> "MySQLStore":
        env = read_env(path)
        return cls(database=env.get("DB_NAME", "flatness"), user=env.get("DB_USER", "flatness_app"),
                   password=env.get("DB_PASS", ""), host=env.get("DB_HOST", "localhost"),
                   port=int(env.get("DB_PORT", "3306")), unix_socket=env.get("DB_SOCKET") or None)

    def _connect(self):
        import pymysql
        try:
            return pymysql.connect(**self._args)
        except pymysql.MySQLError as exc:
            raise StoreError(f"無法連線資料庫：{exc}") from exc

    @contextlib.contextmanager
    def _cursor(self):
        import pymysql
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                yield cur
            conn.commit()
        except pymysql.MySQLError as exc:
            conn.rollback()
            raise StoreError(f"資料庫操作失敗：{exc}") from exc
        finally:
            conn.close()

    @staticmethod
    def _row(r) -> LanDevice:
        (mac, status, first, last, count, req, host, vendor, seen_ip, ip, cfg, order, hidden, hidden_at, upd) = r
        return LanDevice(mac=mac, status=status, first_seen=first, last_seen=last, seen_count=count,
                         last_request=req, hostname=host, vendor_class=vendor, seen_ip=seen_ip, ipv4=ip,
                         config=json.loads(cfg) if cfg else None, sort_order=order,
                         hidden=bool(hidden), hidden_at=hidden_at, updated_at=upd)

    def load(self) -> list[LanDevice]:
        with self._cursor() as cur:
            cur.execute(f"SELECT {_COLUMNS} FROM lan_device")
            return [self._row(r) for r in cur.fetchall()]

    def record(self, events) -> None:
        """新增或更新探索紀錄（DSC-01）；不更動 updated_at（那是設定的修改時間）。"""
        events = list(events)
        if not events:
            return
        with self._cursor() as cur:
            for e in events:
                if e.count:
                    cur.execute(
                        "INSERT INTO lan_device (mac, first_seen, last_seen, seen_count, last_request,"
                        " hostname, vendor_class, seen_ip, updated_at)"
                        " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(3)) AS n"
                        " ON DUPLICATE KEY UPDATE"
                        "  first_seen = COALESCE(lan_device.first_seen, n.first_seen),"
                        "  last_seen = GREATEST(COALESCE(lan_device.last_seen, n.last_seen), n.last_seen),"
                        "  seen_count = lan_device.seen_count + n.seen_count,"
                        "  last_request = n.last_request,"
                        "  hostname = COALESCE(n.hostname, lan_device.hostname),"
                        "  vendor_class = COALESCE(n.vendor_class, lan_device.vendor_class),"
                        "  seen_ip = COALESCE(n.seen_ip, lan_device.seen_ip),"
                        "  hidden = IF(lan_device.status = 'unclassified', 0, lan_device.hidden),"
                        "  hidden_at = IF(lan_device.status = 'unclassified', NULL, lan_device.hidden_at)",
                        (e.mac, e.at, e.at, e.count, e.kind, e.hostname, e.vendor_class, e.ip))
                else:
                    cur.execute(
                        "INSERT INTO lan_device (mac, hostname, vendor_class, updated_at)"
                        " VALUES (%s, %s, %s, NOW(3)) AS n"
                        " ON DUPLICATE KEY UPDATE"
                        "  hostname = COALESCE(n.hostname, lan_device.hostname),"
                        "  vendor_class = COALESCE(n.vendor_class, lan_device.vendor_class)",
                        (e.mac, e.hostname, e.vendor_class))

    def write_inspection(self, head: dict, points: list[dict]) -> bool:
        """DAT-02：主檔 1 筆與明細，同一交易寫入；寫入時間為資料庫時間。

        編號已存在時回傳 False 不寫入：補寫（DAT-04）時前一次其實已寫入成功，避免重複。
        """
        import pymysql
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO inspection (serial, station_id, measured_at, written_at, judgment, reread_count)"
                    " VALUES (%s, %s, %s, NOW(3), %s, %s)",
                    (head["serial"], head["station_id"], head["measured_at"], head["judgment"], head["reread_count"]))
                cur.executemany(
                    "INSERT INTO inspection_point (serial, device_key, probe_id, device_name, probe_description,"
                    " measured_value, standard_value, lower_limit, upper_limit, judgment, raw_response,"
                    " error_text, device_mac, zero_offset)"
                    " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    [(head["serial"], p["device_key"], p["probe_id"], p["device_name"], p["probe_description"],
                      p["measured_value"], p["standard_value"], p["lower_limit"], p["upper_limit"], p["judgment"],
                      p["raw_response"], p["error_text"], p["device_mac"], p.get("zero_offset"))
                     for p in points])
            conn.commit()
            return True
        except pymysql.IntegrityError as exc:
            conn.rollback()
            if exc.args and exc.args[0] == 1062:  # 主鍵重複：已寫入
                return False
            raise StoreError(f"資料庫寫入失敗：{exc}") from exc
        except pymysql.MySQLError as exc:
            conn.rollback()
            raise StoreError(f"資料庫寫入失敗：{exc}") from exc
        finally:
            conn.close()

    def write_calibration(self, rec: dict) -> None:
        """CAL-08：校準紀錄 1 筆。"""
        cols = ("calibrated_at", "station_id", "device_key", "probe_id", "device_mac", "samples", "mean", "sigma",
                "old_offset", "new_offset", "verify_mean", "verify_max_dev", "result", "reason", "adopted")
        with self._cursor() as cur:
            cur.execute(f"INSERT INTO calibration ({', '.join(cols)}) VALUES ({', '.join(['%s'] * len(cols))})",
                        [int(rec[c]) if c == "adopted" else rec[c] for c in cols])

    def count_inspections(self, day) -> int:
        with self._cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM inspection WHERE measured_at >= %s AND measured_at < %s + INTERVAL 1 DAY",
                        (day, day))
            return cur.fetchone()[0]

    def set_hidden(self, mac: str, hidden: bool) -> None:
        with self._cursor() as cur:
            cur.execute("UPDATE lan_device SET hidden = %s, hidden_at = IF(%s, NOW(3), NULL)"
                        " WHERE mac = %s", (int(hidden), int(hidden), mac))

    @contextlib.contextmanager
    def transaction(self):
        """寫入設定；區塊內拋出例外時 ROLLBACK（DSC-03、DSC-12、UPL-08）。"""
        import pymysql
        conn = self._connect()
        try:
            tx = _MySQLTx(conn)
            yield tx
            conn.commit()
        except pymysql.MySQLError as exc:
            conn.rollback()
            raise StoreError(f"資料庫寫入失敗：{exc}") from exc
        except BaseException:
            conn.rollback()
            raise
        finally:
            conn.close()


class _MySQLTx:
    def __init__(self, conn):
        self._conn = conn

    def save(self, old_devices, new_devices) -> int:
        """只寫入設定有變更的設備；整筆更新 dl_en1_config（DSC-12）。"""
        old = {d.mac: d for d in old_devices}
        n = 0
        with self._conn.cursor() as cur:
            for d in new_devices:
                o = old.get(d.mac)
                if o is not None and o.settings() == d.settings():
                    continue
                cfg = json.dumps(d.config, ensure_ascii=False) if d.config is not None else None
                cur.execute(
                    "INSERT INTO lan_device (mac, status, ipv4, dl_en1_config, sort_order, hidden,"
                    " hidden_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(3)) AS n"
                    " ON DUPLICATE KEY UPDATE status = n.status, ipv4 = n.ipv4,"
                    "  dl_en1_config = n.dl_en1_config, sort_order = n.sort_order, hidden = n.hidden,"
                    "  hidden_at = n.hidden_at, updated_at = n.updated_at",
                    (d.mac, d.status, d.ipv4 or None, cfg, d.sort_order, int(d.hidden), d.hidden_at))
                n += 1
        return n

    def delete(self, macs) -> int:
        """從 lan_device 刪除（DSC-18）；之後再出現時以不明設備重新建立。"""
        macs = list(macs)
        if not macs:
            return 0
        with self._conn.cursor() as cur:
            return cur.execute("DELETE FROM lan_device WHERE mac IN (" + ", ".join(["%s"] * len(macs)) + ")", macs)
