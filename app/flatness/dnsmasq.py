"""由 App 啟動與管理 dnsmasq（DSC-07）。

dnsmasq 為 App 的子程序，輸出（log-dhcp）交給探索（DSC-01）解析：
    sudo -n /usr/sbin/dnsmasq --keep-in-foreground --log-facility=- --conf-file=/etc/flatness/dnsmasq.conf
sudoers 只允許這一個完整命令；主設定 root 擁有、App 不可寫，App 只改寫 BOOTP 主機對應（DSC-07-A5）。

- 異常結束時自動重新啟動，期間 on_state(False, 原因) 通知畫面顯示「BOOTP 服務停止」
- restart() 供設定套用使用：以新主機對應重新啟動，回傳是否成功（失敗由呼叫端還原，UPL-08）
- command 為 None（模擬模式、開發機）時不啟動任何程式（DSC-07-A6）
"""

from __future__ import annotations

import logging
import subprocess
import threading
import time

log = logging.getLogger(__name__)

COMMAND = ["sudo", "-n", "/usr/sbin/dnsmasq", "--keep-in-foreground", "--log-facility=-",
           "--conf-file=/etc/flatness/dnsmasq.conf"]


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
        """啟動並持續維持執行（異常結束時自動重新啟動）。"""
        if not self.command:
            return
        with self._lock:
            self._wanted = True
            if self._proc is None or self._proc.poll() is not None:
                try:
                    self._spawn()
                except DnsmasqError:
                    pass  # 已通知畫面並排定重試

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
                                    errors="replace")
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
        proc.terminate()  # sudo 會把 SIGTERM 轉給 dnsmasq
        try:
            proc.wait(timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        log.info("dnsmasq 已停止")
        self._notify(False, "")

    def _notify(self, running: bool, reason: str):
        self.running = running
        if self.on_state:
            try:
                self.on_state(running, reason)
            except Exception:
                log.exception("dnsmasq 狀態通知失敗")
