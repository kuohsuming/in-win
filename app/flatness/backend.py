"""App 的服務層：設定檔、資料庫、定義檔、dnsmasq 與探索，供畫面使用（3.10 DSC、DSC-06、DSC-07）。

啟動順序（DSC-07-G1）：依資料庫產生定義檔與 BOOTP 主機對應 → 啟動 dnsmasq → 探索開始記錄。
畫面只透過本類別存取資料；背景執行緒的事件以 Qt signal 轉回畫面執行緒。
"""

from __future__ import annotations

import ipaddress
import logging
import threading

from PySide6.QtCore import QObject, Signal

from . import lan, netinfo, sync
from .config import Config
from .discovery import Recorder, RequestParser
from .dnsmasq import DnsmasqService
from .store import StoreError

log = logging.getLogger(__name__)
dnsmasq_log = logging.getLogger("dnsmasq")


class Backend(QObject):
    devices_seen = Signal(list)        # 探索事件已寫入資料庫（list[SeenEvent]）
    bootp_state = Signal(bool, str)    # dnsmasq 執行中？、原因（DSC-07「BOOTP 服務停止」）
    db_state = Signal(bool)            # 探索寫入資料庫是否正常（DSC-05）

    def __init__(self, cfg: Config, store, files: sync.Files, dnsmasq_cmd=None, *,
                 simulate: bool = False, equip_net: ipaddress.IPv4Interface | None = None,
                 probe=None):
        super().__init__()
        self.cfg, self.store, self.files = cfg, store, files
        self.simulate = simulate
        self._equip_net = equip_net
        self._probe = probe or netinfo.probe
        self.startup_result: sync.StartupResult | None = None
        self.definition: dict = {"version": 1, "dl_en1": []}   # 連線用（只含使用中）
        self.layout: dict = self.definition                    # 主畫面版面（使用中 ＋ 維修中）
        self.bootp_ok = True
        self.bootp_reason = ""
        self._db_ok = True
        self._parser = RequestParser(cfg.equip_if)
        self._recorder = Recorder(store, self._recorded, on_db_state=self.mark_db)
        cmd = None if simulate else dnsmasq_cmd  # 模擬模式不啟動 dnsmasq（DSC-07-A6）
        self.dnsmasq = DnsmasqService(cmd, self._on_line, self._on_dnsmasq_state)
        self._cache: list[lan.LanDevice] = []

    # ------------------------------------------------------------ 生命週期

    def start(self) -> sync.StartupResult:
        r = sync.startup(self.store, self.files, self.equip_net())
        self.startup_result, self.definition, self.layout = r, r.definition, r.layout
        self._db_ok = r.db_ok
        if r.devices is not None:
            self._cache = r.devices
        if not self.simulate:
            self._recorder.start()
        self.dnsmasq.start()
        return r

    def shutdown(self):
        self.dnsmasq.stop()
        if not self.simulate:
            self._recorder.stop()

    # ------------------------------------------------------------ 探索

    def _on_line(self, line: str):
        dnsmasq_log.info("%s", line)
        events = self._parser.feed(line)
        if events:
            self._recorder.put(events)

    def _recorded(self, events):
        self.devices_seen.emit(events)

    def _on_dnsmasq_state(self, running: bool, reason: str):
        self.bootp_ok = running or not reason
        self.bootp_reason = reason
        self.bootp_state.emit(running, reason)

    # ------------------------------------------------------------ 設備

    def equip_net(self) -> ipaddress.IPv4Interface:
        """DSC-08：設備網卡目前位址；沒有位址時用 site.conf 的 PC_IP／NET_PREFIX。"""
        if self._equip_net is not None:
            return self._equip_net
        return netinfo.equipment_network(self.cfg.equip_if, self.cfg.fallback_net)

    def load_devices(self) -> list[lan.LanDevice]:
        """讀取 lan_device；無法連線時拋出 StoreError。"""
        devices = self.store.load()
        self._cache = devices
        return devices

    def cached_devices(self) -> list[lan.LanDevice]:
        """資料庫無法連線時：上次讀到的資料 ＋ 尚未寫入的探索事件（DSC-05-G1）。"""
        out = {d.mac: d.copy() for d in self._cache}
        for e in self._recorder.pending():
            d = out.setdefault(e.mac, lan.LanDevice(mac=e.mac, first_seen=e.at))
            if e.count:
                d.last_seen, d.last_request = e.at, e.kind
                d.seen_count += e.count
            d.hostname = e.hostname or d.hostname
        return list(out.values())

    def set_hidden(self, mac: str, hidden: bool):
        self.store.set_hidden(mac, hidden)

    def apply(self, old, new, summary: str = "", deleted=()) -> sync.ApplyResult:
        restart = self.dnsmasq.restart if self.dnsmasq.command else None
        result = sync.apply(self.store, self.files, self.equip_net(), old, new, restart, summary, deleted)
        self.definition, self.layout = result.definition, result.layout
        return result

    def probe(self, ip: str, own_mac: str | None = None) -> netinfo.ProbeResult:
        """IP 佔用探測（阻斷約 1 秒；由畫面在背景執行緒呼叫，DSC-10-A3）。"""
        return self._probe(ip, self.cfg.equip_if, own_mac)

    def probe_async(self, ip: str, own_mac: str | None, callback):
        threading.Thread(target=lambda: callback(self.probe(ip, own_mac)), daemon=True,
                         name="ip-probe").start()

    # ------------------------------------------------------------ 其他

    def check_password(self, password: str) -> bool:
        return self.cfg.check_password(password)

    def standards(self) -> dict:
        return self.cfg.standards

    def backups(self):
        return sync.backups(self.files)

    def read_definition(self, path):
        return sync.read_definition_file(path, self.equip_net())

    @property
    def db_ok(self) -> bool:
        return self._db_ok

    def mark_db(self, ok: bool):
        if ok != self._db_ok:
            self._db_ok = ok
            self.db_state.emit(ok)


__all__ = ["Backend", "StoreError"]
