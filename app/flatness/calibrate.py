"""探頭校準：放大器歸零（CAL-01～CAL-10）。

以標準件為基準，只對選取的探頭（放大器）：
    1. 確認放大器的歸零設定（預設記憶 YES 等），不符合才寫入
    2. 清除之前的歸零（預設重置）
    3. 讀取 N 次判斷是否穩定（間隔不小於放大器響應時間）
    4. 執行歸零（預設），放大器記住，斷電後仍保留
    5. 再讀 M 次驗證接近 0
    6. 失敗或取消時再清除一次，探頭為未校準
之後量測直接使用放大器的值；資料庫記錄歸零基準（取樣平均，即歸零前的原始值）供紀錄與追溯。
寫入命令只用於此流程（NFR-11）。經由量測用的 Station（DL-EN1 同一時間只接受 1 條連線，校準與量測共用）。

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
    old_offset: float | None                          # 原本記錄的歸零基準
    samples: list = field(default_factory=list)       # 清除歸零後的讀值（＝原始值）
    mean: float | None = None
    sigma: float | None = None
    new_offset: float | None = None                   # 歸零基準（通過時為取樣平均）
    verify: list = field(default_factory=list)        # 歸零後的讀值
    verify_mean: float | None = None
    verify_max_dev: float | None = None
    bound: float | None = None                        # 每次驗證值的上限 max(3σ, 解析度)
    result: str = FAIL
    reason: str | None = None
    cleared: bool = False                             # 已清除放大器原本的歸零（資料庫須跟著更新）
    zeroed: bool = False                              # 放大器目前為本次的歸零
    interval: float | None = None                     # 實際取樣間隔（秒）
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
    """CAL-04：驗證值（歸零後）平均在 ±容許值內，每次在 ±max(3σ, 解析度) 內。"""
    mean = statistics.fmean(values)
    max_dev = max(abs(v) for v in values)
    bound = max(3 * sigma, resolution)
    if abs(mean) > tolerance:
        return mean, max_dev, bound, f"驗證平均 {mean:+.4f} mm 超出容許值 ±{tolerance:.4f} mm"
    if max_dev > bound + 1e-12:
        return mean, max_dev, bound, f"驗證讀值偏差 {max_dev:.4f} mm 超出 ±{bound:.4f} mm（3σ 或解析度）"
    return mean, max_dev, bound, None


def run(station, dev: dict, probe_id: int, settings, cancel: threading.Event | None = None) -> CalResult:
    """校準一個探頭（阻斷數秒，須在背景執行緒呼叫）。

    station 須提供：prepare_preset(key, id)、preset(key, id, execute)、response_time(key, id)、
    sample(key, id, n, interval_s, cancel)、resolution(key, id)；
    失敗拋出 SampleError，取樣時取消拋出 Cancelled。
    """
    key = dev["key"]
    probe = next(p for p in dev["probes"] if p["id"] == probe_id)
    res = CalResult(key, probe_id, dev.get("mac"), probe.get("zero_offset"))
    try:
        station.prepare_preset(key, probe_id)
        _check_cancel(cancel)
        station.preset(key, probe_id, False)          # 第一步：清除之前的歸零
        res.cleared = True
        res.interval = max(settings.interval_ms / 1000, station.response_time(key, probe_id))
        res.samples = station.sample(key, probe_id, settings.samples, res.interval, cancel)
        res.mean, res.sigma, why = check_samples(res.samples, settings.tolerance)
        if why:
            res.reason = why
            return res
        _check_cancel(cancel)
        station.preset(key, probe_id, True)           # 歸零，放大器記住
        res.zeroed = True
        res.verify = station.sample(key, probe_id, settings.verify, res.interval, cancel)
        res.verify_mean, res.verify_max_dev, res.bound, why = check_verify(
            res.verify, res.sigma, station.resolution(key, probe_id), settings.tolerance)
        if why:
            res.reason = why
            return res
        res.new_offset = res.mean  # 歸零基準：歸零前的原始值（放大器讀不出歸零量，只供紀錄）
        res.result = PASS
    except Cancelled:
        res.result, res.reason = CANCEL, "工程人員取消"
    except SampleError as exc:
        res.reason = f"取樣失敗：{exc}" if res.cleared else f"放大器設定失敗：{exc}"
    finally:
        if res.zeroed and not res.ok:  # 失敗或取消：不留下未通過驗證的歸零
            try:
                station.preset(key, probe_id, False)
                res.zeroed = False
            except SampleError as exc:
                res.reason = f"{res.reason}；清除歸零失敗：{exc}"
    return res


def _check_cancel(cancel):
    if cancel is not None and cancel.is_set():
        raise Cancelled()


def record(res: CalResult, station_id: str, adopted: bool) -> dict:
    """CAL-08：校準紀錄；adopted 為歸零基準已寫入資料庫。"""
    return {"calibrated_at": res.at, "station_id": station_id, "device_key": res.key, "probe_id": res.probe_id,
            "device_mac": res.device_mac, "samples": len(res.samples), "mean": res.mean, "sigma": res.sigma,
            "old_offset": res.old_offset, "new_offset": res.new_offset, "verify_mean": res.verify_mean,
            "verify_max_dev": res.verify_max_dev, "result": res.result, "reason": res.reason,
            "adopted": adopted}
