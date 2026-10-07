"""同一時間只執行一個 App（NFR-14）。

App 啟動時，先停止其他執行中的 App（命令列含 `-m flatness`），例如重新開機後自動啟動與手動啟動
重複、或前一個 App 卡住未結束。先送 SIGTERM 讓對方正常結束（寫入未寫入的量測結果 DAT-05、停止
自己的 dnsmasq DSC-07），時限內未結束再送 SIGKILL；被強制結束者留下的 dnsmasq 由 DSC-07 的殘留
清除處理。本程序與其上層程序（例如啟動腳本）不算。
"""

from __future__ import annotations

import logging
import os
import signal
import time

from .dnsmasq import _is_app, _proc_table

log = logging.getLogger(__name__)


def _ancestors(pid: int, table) -> set[int]:
    out = set()
    while pid in table and pid not in out and pid > 1:
        out.add(pid)
        pid = table[pid][1]
    return out


def other_apps(table=None, me: int | None = None) -> list[int]:
    """其他執行中的 App 的 pid（不含本程序及其上層程序）。"""
    table = _proc_table() if table is None else table
    mine = _ancestors(os.getpid() if me is None else me, table)
    return sorted(pid for pid, (argv, _ppid) in table.items() if _is_app(argv) and pid not in mine)


def _alive(pid: int) -> bool:
    try:
        with open(f"/proc/{pid}/stat") as f:
            return f.read().rsplit(")", 1)[1].split()[0] != "Z"  # 殭屍程序視為已結束
    except (OSError, IndexError):
        return False


def _wait_gone(pids, timeout: float) -> list[int]:
    deadline = time.monotonic() + timeout
    left = [p for p in pids if _alive(p)]
    while left and time.monotonic() < deadline:
        time.sleep(0.05)
        left = [p for p in left if _alive(p)]
    return left


def _send(pids, sig) -> list[int]:
    """送出訊號；回傳沒有權限的 pid（其他帳號執行的 App）。"""
    denied = []
    for pid in pids:
        try:
            os.kill(pid, sig)
        except ProcessLookupError:
            pass
        except PermissionError:
            denied.append(pid)
    return denied


def stop_other_apps(timeout: float = 5.0, pids=None) -> list[int]:
    """停止其他執行中的 App；回傳無法停止的 pid。"""
    pids = other_apps() if pids is None else list(pids)
    if not pids:
        return []
    log.warning("發現其他執行中的 App（pid %s），先停止再啟動", "、".join(map(str, pids)))
    denied = _send(pids, signal.SIGTERM)
    left = _wait_gone([p for p in pids if p not in denied], timeout)
    if left:
        log.warning("App（pid %s）未在 %.0f 秒內結束，強制停止", "、".join(map(str, left)), timeout)
        denied += _send(left, signal.SIGKILL)
        left = _wait_gone([p for p in left if p not in denied], timeout)
    failed = sorted(set(denied) | set(left))
    if failed:
        log.error("無法停止其他 App（pid %s）：%s", "、".join(map(str, failed)),
                  "沒有權限（由其他帳號執行）" if denied else "強制停止後仍未結束")
    else:
        log.info("已停止其他 App")
    return failed
