"""設備網路探索（DSC-01、DSC-05）：解析 dnsmasq 的 log-dhcp 輸出，記錄到資料表 lan_device。

dnsmasq（--log-facility=- 與 log-dhcp）每收到一個請求輸出一行，例：
    dnsmasq-dhcp: 3911 BOOTP(eno2) 192.168.10.11 00:01:fc:de:3a:75 front
    dnsmasq-dhcp: 3911 BOOTP(eno2) 00:01:fc:12:39:a0 no address configured
    dnsmasq-dhcp: 2716 DHCPDISCOVER(eno2) 3c:52:82:11:22:33
    dnsmasq-dhcp: 2716 client provides name: eng-laptop
    dnsmasq-dhcp: 2716 vendor class: MSFT 5.0
開頭的數字是交易編號（xid），用來把主機名稱與廠商識別對回 MAC。
格式依 dnsmasq 2.90 原始碼（rfc2131.c log_packet）；須以實機 DL-EN1 驗證（3.10 設計備註）。
"""

from __future__ import annotations

import logging
import queue
import re
import threading
from collections import OrderedDict
from datetime import datetime

from .lan import normalize_mac
from .store import SeenEvent, StoreError

log = logging.getLogger(__name__)

# 由用戶端發出的請求才計數；DHCPOFFER、DHCPACK 等是 dnsmasq 的回應
REQUEST_TYPES = {"BOOTP": "BOOTP", "DHCPDISCOVER": "DHCP", "DHCPREQUEST": "DHCP", "DHCPINFORM": "DHCP"}

_PACKET_RE = re.compile(
    r"(?:^|\s)(?:(?P<xid>\d+)\s+)?(?P<type>BOOTP|DHCP[A-Z]+)\((?P<iface>[^)]+)\)\s+"
    r"(?:(?P<ip>\d{1,3}(?:\.\d{1,3}){3})\s+)?(?P<mac>(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2})\b")
_NAME_RE = re.compile(r"(?:^|\s)(?P<xid>\d+)\s+client provides name:\s*(?P<v>\S.*?)\s*$")
_VENDOR_RE = re.compile(r"(?:^|\s)(?P<xid>\d+)\s+vendor class:\s*(?P<v>\S.*?)\s*$")


class RequestParser:
    """逐行解析 dnsmasq 輸出，回傳 SeenEvent。只記錄設備網卡上的請求（DSC-01-A1）。"""

    def __init__(self, interface: str | None = None, remember: int = 256):
        self.interface = interface
        self._xid_mac: OrderedDict[str, str] = OrderedDict()
        self._remember = remember

    def feed(self, line: str, now: datetime | None = None) -> list[SeenEvent]:
        now = now or datetime.now()
        m = _PACKET_RE.search(line)
        if m:
            kind = REQUEST_TYPES.get(m["type"])
            if self.interface and m["iface"] != self.interface:
                return []
            try:
                mac = normalize_mac(m["mac"])
            except ValueError:
                return []
            if m["xid"]:
                self._xid_mac[m["xid"]] = mac
                self._xid_mac.move_to_end(m["xid"])
                while len(self._xid_mac) > self._remember:
                    self._xid_mac.popitem(last=False)
            return [SeenEvent(mac, kind, now)] if kind else []
        for regex, attr in ((_NAME_RE, "hostname"), (_VENDOR_RE, "vendor_class")):
            m = regex.search(line)
            if m and m["xid"] in self._xid_mac:
                mac = self._xid_mac[m["xid"]]
                return [SeenEvent(mac, "DHCP", now, count=0, **{attr: m["v"][:64]})]
        return []


class Recorder:
    """把探索事件寫入資料庫的背景執行緒；不在畫面執行緒寫資料庫（DSC-01-A5）。

    資料庫無法寫入時事件留在記憶體並每 retry 秒重試，恢復後補寫，不遺失（DSC-05）。
    on_recorded(events) 在寫入成功後於本執行緒呼叫（畫面以 Qt signal 轉回畫面執行緒）。
    """

    def __init__(self, store, on_recorded=None, retry: float = 2.0, on_db_state=None):
        self.store = store
        self.on_recorded = on_recorded
        self.on_db_state = on_db_state
        self.retry = retry
        self._queue: queue.Queue = queue.Queue()
        self._pending: list[SeenEvent] = []
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, name="discovery-recorder", daemon=True)
        self.db_ok = True

    def start(self):
        self._thread.start()
        return self

    def stop(self, timeout: float = 3.0):
        self._stop.set()
        self._queue.put(None)
        self._thread.join(timeout)

    def put(self, events) -> None:
        for e in events:
            self._queue.put(e)

    def pending(self) -> list[SeenEvent]:
        """尚未寫入資料庫的事件（資料庫斷線期間畫面仍可顯示，DSC-05-G1）。"""
        with self._lock:
            return list(self._pending)

    def _run(self):
        while not self._stop.is_set():
            try:
                item = self._queue.get(timeout=self.retry if self._pending else None)
            except queue.Empty:
                item = None
            batch = [item] if item is not None else []
            while True:  # 一次取完佇列中的事件
                try:
                    more = self._queue.get_nowait()
                except queue.Empty:
                    break
                if more is not None:
                    batch.append(more)
            with self._lock:
                self._pending.extend(batch)
                todo = list(self._pending)
            if not todo:
                continue
            try:
                self.store.record(todo)
            except StoreError as exc:
                if self.db_ok:
                    log.warning("探索紀錄暫存於記憶體（%d 筆），資料庫無法寫入：%s", len(todo), exc)
                    self.db_ok = False
                    if self.on_db_state:
                        self.on_db_state(False)
                self._stop.wait(self.retry)
                continue
            if not self.db_ok:
                log.info("資料庫恢復，已補寫探索紀錄 %d 筆", len(todo))
                self.db_ok = True
                if self.on_db_state:
                    self.on_db_state(True)
            with self._lock:
                del self._pending[:len(todo)]
            if self.on_recorded:
                try:
                    self.on_recorded(todo)
                except Exception:  # 通知失敗不影響記錄
                    log.exception("探索通知失敗")
