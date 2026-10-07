"""啟動表面平整檢查系統 App：python -m flatness [選項]

啟動順序（NFR-14、DSC-06、DSC-07）：停止其他執行中的 App → 讀設定檔 → 依資料庫產生定義檔與 BOOTP 主機對應 → 啟動 dnsmasq 與探索 → 主畫面 → 自動偵測設備。
"""

from __future__ import annotations

import argparse
import ipaddress
import logging
import shlex
import signal
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from . import config as config_mod
from . import arpwatch, dnsmasq, instance, lan, sync


def parse_args(argv=None):
    p = argparse.ArgumentParser(prog="flatness", description="表面平整檢查系統")
    p.add_argument("--config", type=Path, default=Path("/etc/flatness/config.toml"), help="App 設定檔")
    p.add_argument("--db-env", type=Path, default=Path("/etc/flatness/db.env"), help="資料庫連線資訊")
    p.add_argument("--def", dest="def_file", type=Path, default=Path("/etc/flatness/dl-en1.json"),
                   help="DL-EN1 定義檔（由 App 依資料庫產生）")
    p.add_argument("--hosts", type=Path, default=Path("/var/lib/flatness/bootp/dl-en1.hosts"),
                   help="dnsmasq BOOTP 主機對應檔（由 App 依資料庫產生）")
    p.add_argument("--dnsmasq-cmd", default=shlex.join(dnsmasq.COMMAND),
                   help="啟動 dnsmasq 的命令（開發機可改用 scripts/fake-dnsmasq.py）")
    p.add_argument("--no-dnsmasq", action="store_true", help="不啟動 dnsmasq（開發用）")
    p.add_argument("--arp-cmd", default=shlex.join(arpwatch.COMMAND),
                   help="啟動 ARP 監聽的命令（DSC-19）")
    p.add_argument("--no-arp", action="store_true", help="不監聽 ARP 位址偵測封包（開發機沒有安裝監聽程式時）")
    p.add_argument("--demo", action="store_true",
                   help="示範量測來源：不連線 DL-EN1，數值隨機產生（開發機沒有 DL-EN1 時）")
    p.add_argument("--simulate", action="store_true", help="模擬模式：不啟動 dnsmasq、不探索（SIM、DSC-07-A6）")
    p.add_argument("--equip-net", type=ipaddress.IPv4Interface,
                   help="指定設備網段（預設取設備網卡目前位址，沒有時用 config.toml 的 pc_ip／net_prefix）")
    p.add_argument("--log-file", type=Path, default=Path("/var/log/flatness/flatness.log"))
    p.add_argument("--buffer", type=Path, default=Path("/var/lib/flatness/buffer"),
                   help="資料庫斷線時的本機暫存（DAT-04）")
    p.add_argument("--fullscreen", action="store_true", help="全螢幕（預設，保留此參數相容舊的啟動方式）")
    p.add_argument("--windowed", action="store_true", help="以一般視窗執行（開發用；預設全螢幕，UI-10）")
    p.add_argument("--on-top", action="store_true", help="視窗保持在最上層（Wayland 下需搭配 QT_QPA_PLATFORM=xcb）")
    return p.parse_args(argv)


def setup_logging(log_file: Path):
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        # NFR-13：日誌保存 30 天
        handlers.append(TimedRotatingFileHandler(log_file, when="midnight", backupCount=30, encoding="utf-8"))
    except OSError:
        pass  # 開發機沒有 /var/log/flatness 時只輸出到終端機
    logging.basicConfig(level=logging.INFO, handlers=handlers,
                        format="%(asctime)s %(levelname)s %(name)s %(message)s")


def make_store(db_env: Path):
    from .store import MemoryStore, MySQLStore
    if db_env.exists():
        return MySQLStore.from_env(db_env)
    logging.getLogger(__name__).error("找不到資料庫連線資訊 %s", db_env)
    store = MemoryStore()
    store.available = False
    return store


def main(argv=None) -> int:
    args = parse_args(argv)
    setup_logging(args.log_file)
    log = logging.getLogger("flatness")
    instance.stop_other_apps()  # NFR-14：同一時間只執行一個 App，先停止之前遺留的 App
    cfg = config_mod.load(args.config)

    from PySide6.QtWidgets import QApplication

    from .backend import Backend
    from .dlen1 import DlEn1Station
    from .measure import DemoStation
    from .results import ResultSink
    from .ui import theme
    from .ui.main_window import MainWindow

    app = QApplication(sys.argv[:1])
    app.setApplicationName("flatness")
    family = theme.load_fonts()
    app.setFont(theme.text_font(15))
    app.setStyleSheet(theme.qss())
    log.info("文字字型：%s", family)

    cmd = None if args.no_dnsmasq else shlex.split(args.dnsmasq_cmd)
    store = make_store(args.db_env)
    arp_cmd = None if args.no_arp else shlex.split(args.arp_cmd)
    backend = Backend(cfg, store, sync.Files(args.def_file, args.hosts), cmd,
                      simulate=args.simulate, equip_net=args.equip_net, arp_cmd=arp_cmd)
    result = backend.start()
    if result.problem:
        log.warning("啟動：%s", result.problem)

    if args.demo:
        log.warning("量測來源：示範模式（不連線 DL-EN1，數值為隨機產生；結果不寫入資料庫）")
        factory = lambda definition: DemoStation(definition, lan.standards(definition))  # noqa: E731
        sink = None
    else:
        log.info("量測來源：DL-EN1 實機；結果寫入資料庫（本機暫存 %s）", args.buffer)
        factory = lambda definition: DlEn1Station(definition)  # noqa: E731
        sink = ResultSink(store, cfg.station_id, args.buffer).start()
    win = MainWindow(backend, factory, sink)
    if args.on_top:
        from PySide6.QtCore import Qt
        win.setWindowFlag(Qt.WindowStaysOnTopHint, True)
    if not args.windowed:  # UI-10：預設全螢幕
        win.showFullScreen()
    else:
        win.resize(1600, 1000)
        win.show()
    win.detect()  # DEV-01：開機後自動偵測

    # 登出、關機（SIGTERM、SIGHUP）或 Ctrl+C 時正常結束：寫入未寫入的結果（DAT-05）並停止 dnsmasq（DSC-07）。
    # Qt 事件迴圈執行中 Python 無法處理訊號，以計時器定期讓出控制權。
    from PySide6.QtCore import QTimer
    def on_signal(signum, _frame):
        log.info("收到 %s，結束 App", signal.Signals(signum).name)
        win.close()   # DAT-05：closeEvent 寫入未寫入的結果
        app.quit()    # 不依賴「最後一個視窗關閉」：仍有其他視窗（設定頁等）時也要結束（NFR-14）

    for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(sig, on_signal)

    def on_snapshot(_signum, _frame):
        """維護用：kill -USR1 <pid> 將目前畫面存到日誌目錄（Wayland 下外部程式無法擷取 App 畫面）。"""
        from datetime import datetime
        path = args.log_file.parent / f"screen-{datetime.now():%Y%m%d-%H%M%S}.png"
        ok = win.grab().save(str(path))
        log.info("畫面擷取%s：%s（%dx%d）", "完成" if ok else "失敗", path, win.width(), win.height())

    signal.signal(signal.SIGUSR1, on_snapshot)
    pulse = QTimer(interval=300)
    pulse.timeout.connect(lambda: None)
    pulse.start()
    code = app.exec()
    backend.shutdown()  # DSC-07：App 結束時停止 dnsmasq
    if sink is not None:
        sink.close()    # DAT-05：結束前盡量寫完，未寫入的留在本機暫存
    return code


if __name__ == "__main__":
    sys.exit(main())
