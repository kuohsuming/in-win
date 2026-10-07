"""探頭校準：軟體歸零（CAL-01～CAL-08）。

以標準件為基準：讀取該探頭 N 次（間隔固定）取平均為偏移量，之後顯示值 ＝ 原始值 − 偏移量；再讀 M 次
驗證扣除後接近 0。不送任何寫入命令到放大器（NFR-11）。取樣經由量測用的 Station（DL-EN1 同一時間只
接受 1 條連線，校準與量測共用同一條）。

驗證條件（CAL-04）：M 次平均在 0 ± 容許值內，且每次在 0 ± max(3σ, 解析度) 內。
原本提出的「M 次皆在 1σ 內」正常探頭約 85% 會失敗（0.68^5 ≈ 0.15），σ 為 0 時任何晃動也會失敗。
"""

from __future__ import annotations

import statistics
import threading
from dataclasses import dataclass, field
from datetime import datetime

PASS, FAIL, CANCEL = "PASS", "FAIL", "CANCEL"


class SampleError(Exception):
    """取樣失敗：無有效數據、放大器錯誤、連線失敗。"""


class Cancelled(Exception):
    pass


@dataclass
class CalResult:
    key: str
    probe_id: int
    device_mac: str | None
    old_offset: float | None
    samples: list = field(default_factory=list)       # 原始值
    mean: float | None = None
    sigma: float | None = None
    new_offset: float | None = None
    verify: list = field(default_factory=list)        # 扣除新偏移量後的值
    verify_mean: float | None = None
    verify_max_dev: float | None = None
    bound: float | None = None                        # 每次驗證值的上限 max(3σ, 解析度)
    result: str = FAIL
    reason: str | None = None
    at: datetime = field(default_factory=datetime.now)

    @property
    def ok(self) -> bool:
        return self.result == PASS


def check_samples(samples, tolerance: float) -> tuple[float, float, str | None]:
    """CAL-02：平均、樣本標準差；σ 大於容許值的一半為讀值不穩定。"""
    mean = statistics.fmean(samples)
    sigma = statistics.stdev(samples) if len(samples) > 1 else 0.0
    if sigma > tolerance / 2:
        return mean, sigma, (f"讀值不穩定（標準差 {sigma:.4f} mm，上限 {tolerance / 2:.4f} mm），"
                             "請確認標準件已放好、治具未晃動")
    return mean, sigma, None


def check_verify(values, sigma: float, resolution: float, tolerance: float) -> tuple[float, float, float, str | None]:
    """CAL-04：驗證值（已扣偏移量）平均在 ±容許值內，每次在 ±max(3σ, 解析度) 內。"""
    mean = statistics.fmean(values)
    max_dev = max(abs(v) for v in values)
    bound = max(3 * sigma, resolution)
    if abs(mean) > tolerance:
        return mean, max_dev, bound, f"驗證平均 {mean:+.4f} mm 超出容許值 ±{tolerance:.4f} mm"
    if max_dev > bound + 1e-12:
        return mean, max_dev, bound, f"驗證讀值偏差 {max_dev:.4f} mm 超出 ±{bound:.4f} mm（3σ 或解析度）"
    return mean, max_dev, bound, None


def run(station, dev: dict, probe_id: int, settings, cancel: threading.Event | None = None) -> CalResult:
    """校準一個探頭（阻斷約 (samples + verify) × interval 秒，須在背景執行緒呼叫）。

    station 須提供 sample(key, probe_id, n, interval_s, cancel) → 原始值 list[float]（失敗拋出 SampleError、
    取消拋出 Cancelled）與 resolution(key, probe_id) → 解析度。
    """
    probe = next(p for p in dev["probes"] if p["id"] == probe_id)
    res = CalResult(dev["key"], probe_id, dev.get("mac"), probe.get("zero_offset"))
    interval = settings.interval_ms / 1000
    try:
        res.samples = station.sample(dev["key"], probe_id, settings.samples, interval, cancel)
        res.mean, res.sigma, why = check_samples(res.samples, settings.tolerance)
        if why:
            res.reason = why
            return res
        res.new_offset = res.mean
        raw = station.sample(dev["key"], probe_id, settings.verify, interval, cancel)
        res.verify = [v - res.new_offset for v in raw]
        res.verify_mean, res.verify_max_dev, res.bound, why = check_verify(
            res.verify, res.sigma, station.resolution(dev["key"], probe_id), settings.tolerance)
        if why:
            res.reason = why
            return res
        res.result = PASS
    except Cancelled:
        res.result, res.reason = CANCEL, "工程人員取消"
    except SampleError as exc:
        res.reason = f"取樣失敗：{exc}"
    return res


def record(res: CalResult, station_id: str, adopted: bool) -> dict:
    """CAL-08：校準紀錄。"""
    return {"calibrated_at": res.at, "station_id": station_id, "device_key": res.key, "probe_id": res.probe_id,
            "device_mac": res.device_mac, "samples": len(res.samples), "mean": res.mean, "sigma": res.sigma,
            "old_offset": res.old_offset, "new_offset": res.new_offset, "verify_mean": res.verify_mean,
            "verify_max_dev": res.verify_max_dev, "result": res.result, "reason": res.reason,
            "adopted": adopted}
