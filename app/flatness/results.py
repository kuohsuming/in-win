"""量測結果寫入 MySQL（DAT-02～DAT-06）。

每片結果先以原子方式寫入本機暫存（/var/lib/flatness/buffer/<編號>.json，3.0.6），再由背景執行緒寫入
資料庫，成功後刪除暫存檔：
    - 資料庫無法寫入時照常進行下一片，暫存檔保留，每 retry 秒重試，恢復後自動補寫（DAT-04）
    - 畫面不等待資料庫（NFR-01）；App 結束時盡量寫完，來不及的留在暫存，下次啟動補寫（DAT-05）
    - 補寫時若該編號其實已寫入（例如寫入後、刪除暫存前當機），不重複寫入
listener(event) 於背景執行緒呼叫（畫面以 Qt signal 轉回畫面執行緒）：
    ("written", 編號, 待同步筆數)、("failed", 原因, 待同步筆數)
"""

from __future__ import annotations

import json
import logging
import threading
from datetime import datetime
from pathlib import Path

from . import bootp
from .measure import ERR, HI, LO, OK
from .store import StoreError

log = logging.getLogger(__name__)

POINT_JUDGMENT = {OK: "OK", HI: "HIGH", LO: "LOW", ERR: "ERROR"}


def to_record(result, station_id: str) -> dict:
    """畫面上的一片結果 → 主檔與明細（DAT-02、DAT-03 當時的標準與原始回傳、DAT-06 MAC）。"""
    points = []
    for p in result.points:
        std = p.std
        points.append({
            "device_key": p.key, "probe_id": p.probe_id,
            "device_name": p.device_name[:10], "probe_description": p.description[:10],
            "measured_value": p.value, "standard_value": std.nominal if std else None,
            "lower_limit": std.lower if std else None, "upper_limit": std.upper if std else None,
            "judgment": POINT_JUDGMENT[p.state], "raw_response": (p.raw or None) and p.raw[:64],
            "error_text": p.error[:255] if p.error else None, "device_mac": p.device_mac or None,
            "zero_offset": p.zero_offset,
        })
    return {"head": {"serial": result.serial, "station_id": station_id,
                     "measured_at": result.measured_at.isoformat(timespec="milliseconds"),
                     "judgment": result.judgment, "reread_count": result.rereads},
            "points": points}


class ResultSink:
    """寫入 MySQL 的結果輸出；介面與示範用的 MemorySink 相同（write、count、export、real）。"""

    real = True

    def __init__(self, store, station_id: str, buffer_dir: Path, retry: float = 5.0):
        self.store, self.station_id = store, station_id
        self.dir = Path(buffer_dir)
        self.retry = retry
        self.listener = None
        self.db_ok = True
        self._wake = threading.Event()
        self._stop = threading.Event()
        self._idle = threading.Event()
        self._thread = threading.Thread(target=self._run, name="result-writer", daemon=True)

    def start(self):
        self.dir.mkdir(parents=True, exist_ok=True)
        n = self.pending()
        if n:
            log.warning("本機暫存有 %d 筆尚未寫入資料庫的結果，開始補寫（DAT-04）", n)
        self._thread.start()
        return self

    # ------------------------------------------------------------ 畫面使用

    def write(self, result) -> None:
        """先寫入本機暫存（不等資料庫），再通知背景寫入。"""
        rec = to_record(result, self.station_id)
        bootp.atomic_write(self.dir / f"{result.serial}.json", json.dumps(rec, ensure_ascii=False))
        log.info("編號 %s 結果 %s 已存入本機暫存，寫入資料庫中", result.serial, result.judgment)
        self._idle.clear()
        self._wake.set()

    def pending(self) -> int:
        return len(self._files())

    def count(self, day) -> int:
        """當日筆數（取出測試數據 EXP）：資料庫 ＋ 尚未寫入的暫存。"""
        n = sum(1 for f in self._files() if f.name[:8] == day.strftime("%Y%m%d"))
        return self.store.count_inspections(day) + n

    def export(self, day, path) -> int:
        """取出測試數據（EXP-03）：資料庫 ＋ 尚未寫入的暫存；回傳筆數。資料庫無法讀取時拋出 StoreError。"""
        from . import export
        records = {r["head"]["serial"]: r for r in self.store.read_inspections(day)}
        for f in self._files():
            if f.name[:8] != day.strftime("%Y%m%d") or f.stem in records:
                continue
            try:
                rec = json.loads(f.read_text(encoding="utf-8"))
                rec["head"]["measured_at"] = datetime.fromisoformat(rec["head"]["measured_at"])
            except (OSError, ValueError, KeyError):
                continue  # 寫入中或格式錯誤（背景寫入會處理）
            records[rec["head"]["serial"]] = rec
        n = export.write_xlsx(path, list(records.values()), day)
        log.info("取出測試數據：%s 共 %d 筆 → %s", day, n, path)
        return n

    def close(self, timeout: float = 3.0) -> None:
        """App 結束：盡量寫完（DAT-05）；資料庫無法寫入時留在暫存，下次啟動補寫。"""
        self._wake.set()
        if self.db_ok:
            self._idle.wait(timeout)
        self._stop.set()
        self._wake.set()
        self._thread.join(timeout)
        n = self.pending()
        if n:
            log.warning("結束時仍有 %d 筆結果未寫入資料庫，保留於 %s，下次啟動補寫", n, self.dir)

    # ------------------------------------------------------------ 背景寫入

    def _files(self) -> list[Path]:
        try:
            return sorted(self.dir.glob("[0-9]*.json"))
        except OSError:
            return []

    def _notify(self, *event):
        if self.listener:
            try:
                self.listener(event)
            except Exception:
                log.exception("結果寫入通知失敗")

    def _run(self):
        while not self._stop.is_set():
            files = self._files()
            if not files:
                self._idle.set()
                self._wake.wait()
                self._wake.clear()
                continue
            for f in files:
                if self._stop.is_set():
                    return
                try:
                    rec = json.loads(f.read_text(encoding="utf-8"))
                    head = dict(rec["head"], measured_at=datetime.fromisoformat(rec["head"]["measured_at"]))
                except (OSError, ValueError, KeyError) as exc:
                    bad = f.with_suffix(".bad")
                    f.rename(bad)
                    log.error("本機暫存 %s 格式錯誤，已改名為 %s：%s", f.name, bad.name, exc)
                    continue
                try:
                    new = self.store.write_inspection(head, rec["points"])
                except StoreError as exc:
                    if self.db_ok:
                        log.error("寫入資料庫失敗，結果保留於本機暫存，每 %.0f 秒重試：%s", self.retry, exc)
                    self.db_ok = False
                    self._notify("failed", str(exc), self.pending())
                    self._stop.wait(self.retry)
                    break
                f.unlink(missing_ok=True)
                if not self.db_ok:
                    log.info("資料庫恢復，補寫編號 %s", head["serial"])
                self.db_ok = True
                if new:
                    log.info("編號 %s 已寫入資料庫（明細 %d 筆）", head["serial"], len(rec["points"]))
                else:
                    log.info("編號 %s 已在資料庫中，不重複寫入", head["serial"])
                self._notify("written", head["serial"], self.pending())
