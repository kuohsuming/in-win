"""由 App 啟動與管理 dnsmasq（DSC-07）。

dnsmasq 為 App 的子程序，輸出（log-dhcp）交給探索（DSC-01）解析：
    sudo -n /usr/sbin/dnsmasq --keep-in-foreground --log-facility=- --conf-file=/etc/flatness/dnsmasq.conf
sudoers 只允許這一個完整命令；主設定 root 擁有、App 不可寫，App 只改寫 BOOTP 主機對應（DSC-07-A5）。

- 異常結束時自動重新啟動，期間 on_state(False, 原因) 通知畫面顯示「BOOTP 服務停止」
- restart() 供設定套用使用：以新主機對應重新啟動，回傳是否成功（失敗由呼叫端還原，UPL-08）
- command 為 None（模擬模式、開發機）時不啟動任何程式（DSC-07-A6）
- 停止：sudo 啟動的 dnsmasq 為 root 程序，App 帳號無法直接送出訊號，改以 sudoers 允許的
  STOP_COMMAND（root 擁有、不接受參數，只停止以上述固定命令列執行的 dnsmasq）停止
- 啟動前清除殘留：App 當掉或被強制終止時 dnsmasq 會繼續執行並佔用 UDP 67；App 啟動時先找出
  不屬於任何執行中 App 的同一命令列 dnsmasq 並停止，再啟動新的（DSC-07）
"""

from __future__ import annotations

import logging
import os
import signal
import subprocess
import threading
import time

log = logging.getLogger(__name__)

COMMAND = ["sudo", "-n", "/usr/sbin/dnsmasq", "--keep-in-foreground", "--log-facility=-",
           "--conf-file=/etc/flatness/dnsmasq.conf"]
STOP_COMMAND = ["sudo", "-n", "/usr/local/sbin/flatness-stop-dnsmasq"]


def _proc_table() -> dict[int, tuple[list[str], int]]:
    """pid → (命令列, 父程序 pid)，讀取 /proc；不需 root。"""
    table = {}
    for name in os.listdir("/proc"):
        if not name.isdigit():
            continue
        try:
            with open(f"/proc/{name}/cmdline", "rb") as f:
                argv = [a.decode(errors="replace") for a in f.read().split(b"\0") if a]
            with open(f"/proc/{name}/stat") as f:
                ppid = int(f.read().rsplit(")", 1)[1].split()[1])
        except (OSError, ValueError, IndexError):
            continue
        table[int(name)] = (argv, ppid)
    return table


def _is_app(argv: list[str]) -> bool:
    return any(a == "flatness" and i > 0 and argv[i - 1] == "-m" for i, a in enumerate(argv))


def _owner_app(pid: int, table) -> int | None:
    """往上找執行中的 App；找到回傳其 pid。"""
    seen = set()
    while pid in table and pid not in seen and pid > 1:
        seen.add(pid)
        argv, pid = table[pid]
        if pid in table and _is_app(table[pid][0]):
            return pid
    return None


class DnsmasqError(RuntimeError):
    pass


class DnsmasqService:
    def __init__(self, command=COMMAND, on_line=None, on_state=None,
                 restart_delay: float = 2.0, settle: float = 1.5):
        self.command = list(command) if command else None
        self.on_line = on_line
        self.on_state = on_state
        self.restart_delay = restart_delay
        self.settle = settle  # 啟動後觀察這麼久仍在執行，才算啟動成功
        self._proc: subprocess.Popen | None = None
        self._lock = threading.RLock()
        self._wanted = False
        self._generation = 0
        self._tail: list[str] = []
        self.running = False

    # ------------------------------------------------------------ 對外

    def start(self) -> None:
        """清除殘留後啟動，並持續維持執行（異常結束時自動重新啟動）。"""
        if not self.command:
            return
        with self._lock:
            self._wanted = True
            if self._proc is None or self._proc.poll() is not None:
                try:
                    self.clear_leftovers()
                    self._spawn()
                except DnsmasqError as exc:
                    if self._proc is None:  # 清除殘留失敗：通知畫面，稍後再試
                        log.error("%s", exc)
                        self._notify(False, str(exc))
                        self._schedule_retry(self._generation)

    @property
    def _patterns(self) -> list[list[str]]:
        """要辨識的命令列：本身，以及經 sudo 時實際執行的 dnsmasq。"""
        pats = [self.command]
        if self.command[:2] == ["sudo", "-n"]:
            pats.append(self.command[2:])
        return pats

    def leftovers(self, table=None) -> list[int]:
        """與本服務命令列相同、但不是本 App 啟動的程序（App 當掉後殘留的 dnsmasq）。"""
        table = _proc_table() if table is None else table
        me = os.getpid()
        own = {self._proc.pid} if self._proc is not None else set()
        out = []
        for pid, (argv, _ppid) in table.items():
            if argv in self._patterns and pid not in own and _owner_app(pid, table) != me:
                out.append(pid)
        return out

    def clear_leftovers(self, timeout: float = 5.0) -> None:
        """停止殘留的 dnsmasq；屬於另一個執行中 App 的不停止。失敗拋出 DnsmasqError。"""
        table = _proc_table()
        pids = self.leftovers(table)
        if not pids:
            return
        for pid in pids:
            other = _owner_app(pid, table)
            if other is not None:
                raise DnsmasqError(f"另一個 App（pid {other}）正在執行 dnsmasq，請先關閉該 App")
        log.warning("發現殘留的 dnsmasq（pid %s），先停止再啟動", "、".join(map(str, pids)))
        self._signal_or_stop(pids)
        if not self._wait_gone(pids, timeout):
            left = [p for p in pids if os.path.exists(f"/proc/{p}")]
            raise DnsmasqError(f"殘留的 dnsmasq（pid {'、'.join(map(str, left))}）無法自動停止，"
                               f"BOOTP 服務無法啟動；請重新開機或執行 sudo kill {' '.join(map(str, left))}")
        log.info("已停止殘留的 dnsmasq")

    def _signal_or_stop(self, pids):
        """先直接送 SIGTERM；root 程序（sudo 啟動）沒有權限時改用 STOP_COMMAND。"""
        denied = False
        for pid in pids:
            try:
                os.kill(pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            except PermissionError:
                denied = True
        if denied:
            self._run_stop_command()

    def _run_stop_command(self):
        try:
            r = subprocess.run(STOP_COMMAND, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=10)
            log.info("執行 %s：結束碼 %s %s", " ".join(STOP_COMMAND), r.returncode, (r.stderr or "").strip())
        except (OSError, subprocess.TimeoutExpired) as exc:
            log.error("無法執行 %s：%s", " ".join(STOP_COMMAND), exc)

    @staticmethod
    def _wait_gone(pids, timeout: float) -> bool:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if not any(os.path.exists(f"/proc/{p}") for p in pids):
                return True
            time.sleep(0.05)
        return not any(os.path.exists(f"/proc/{p}") for p in pids)

    def stop(self, timeout: float = 5.0) -> None:
        """App 結束時停止 dnsmasq（DSC-07：結束 App 後 5 秒內 dnsmasq 結束）。"""
        with self._lock:
            self._wanted = False
            self._generation += 1
            self._terminate(timeout)

    def restart(self) -> None:
        """以新的主機對應重新啟動；啟動失敗拋出 DnsmasqError（附 dnsmasq 輸出）。"""
        if not self.command:
            return
        with self._lock:
            self._wanted = False
            self._generation += 1
            self._terminate(5.0)
            self._wanted = True
            proc = self._spawn()
        deadline = time.monotonic() + self.settle
        while time.monotonic() < deadline:
            if proc.poll() is not None:
                break
            time.sleep(0.05)
        if proc.poll() is not None:
            time.sleep(0.1)  # 讓讀取執行緒收完輸出
            raise DnsmasqError(f"dnsmasq 啟動失敗（結束碼 {proc.returncode}）：{' / '.join(self._tail[-3:])}")

    # ------------------------------------------------------------ 內部

    def _spawn(self) -> subprocess.Popen:
        self._generation += 1
        gen = self._generation
        self._tail = []
        try:
            proc = subprocess.Popen(self.command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True, bufsize=1,
                                    errors="replace",
                                    # 獨立程序群組：sudo 不轉送同一程序群組送來的訊號，
                                    # 與 App 同群組時 terminate() 無效，要等逾時改用 STOP_COMMAND
                                    start_new_session=True)
        except OSError as exc:
            self._notify(False, f"無法執行 dnsmasq：{exc}")
            self._schedule_retry(gen)
            raise DnsmasqError(f"無法執行 dnsmasq：{exc}") from exc
        self._proc = proc
        log.info("dnsmasq 已啟動 pid=%s", proc.pid)
        self._notify(True, "")
        threading.Thread(target=self._read, args=(proc, gen), name="dnsmasq-reader", daemon=True).start()
        return proc

    def _read(self, proc: subprocess.Popen, gen: int):
        for line in proc.stdout:
            line = line.rstrip("\n")
            self._tail = (self._tail + [line])[-20:]
            if self.on_line:
                try:
                    self.on_line(line)
                except Exception:
                    log.exception("處理 dnsmasq 輸出失敗：%s", line)
        rc = proc.wait()
        with self._lock:
            if gen != self._generation or not self._wanted:
                return  # 正常停止或已重新啟動
            reason = f"dnsmasq 異常結束（結束碼 {rc}）：{' / '.join(self._tail[-3:])}"
            log.error("%s；%.0f 秒後自動重新啟動", reason, self.restart_delay)
            self._notify(False, reason)
        self._schedule_retry(gen)

    def _schedule_retry(self, gen: int):
        def retry():
            time.sleep(self.restart_delay)
            with self._lock:
                if self._wanted and gen == self._generation:
                    try:
                        self._spawn()
                    except DnsmasqError:
                        pass
        threading.Thread(target=retry, name="dnsmasq-retry", daemon=True).start()

    def _terminate(self, timeout: float):
        proc, self._proc = self._proc, None
        if proc is None or proc.poll() is not None:
            if self.running:
                self._notify(False, "")
            return
        try:
            proc.terminate()
        except PermissionError:  # sudo 啟動的 root 程序：以 STOP_COMMAND 停止
            self._run_stop_command()
        try:
            proc.wait(timeout)
        except subprocess.TimeoutExpired:
            self._run_stop_command() if self.command[:2] == ["sudo", "-n"] else None
            try:
                proc.kill()
            except PermissionError:
                pass
            try:
                proc.wait(timeout)
            except subprocess.TimeoutExpired:
                log.error("dnsmasq（pid %s）未能在時限內停止", proc.pid)
        log.info("dnsmasq 已停止")
        self._notify(False, "")

    def _notify(self, running: bool, reason: str):
        self.running = running
        if self.on_state:
            try:
                self.on_state(running, reason)
            except Exception:
                log.exception("dnsmasq 狀態通知失敗")
