"""啟動表面平整檢查系統 App：python -m flatness [選項]

啟動順序（DSC-06、DSC-07）：讀設定檔 → 依資料庫產生定義檔與 BOOTP 主機對應 → 啟動 dnsmasq 與探索 → 主畫面 → 自動偵測設備。
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
from . import dnsmasq, sync


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
    p.add_argument("--simulate", action="store_true", help="模擬模式：不啟動 dnsmasq、不探索（SIM、DSC-07-A6）")
    p.add_argument("--equip-net", type=ipaddress.IPv4Interface,
                   help="指定設備網段（預設取設備網卡目前位址，沒有時用 config.toml 的 pc_ip／net_prefix）")
    p.add_argument("--log-file", type=Path, default=Path("/var/log/flatness/flatness.log"))
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
    cfg = config_mod.load(args.config)

    from PySide6.QtWidgets import QApplication

    from .backend import Backend
    from .measure import DemoStation
    from .ui import theme
    from .ui.main_window import MainWindow

    app = QApplication(sys.argv[:1])
    app.setApplicationName("flatness")
    family = theme.load_fonts()
    app.setFont(theme.text_font(15))
    app.setStyleSheet(theme.qss())
    log.info("文字字型：%s", family)

    cmd = None if args.no_dnsmasq else shlex.split(args.dnsmasq_cmd)
    backend = Backend(cfg, make_store(args.db_env), sync.Files(args.def_file, args.hosts), cmd,
                      simulate=args.simulate, equip_net=args.equip_net)
    result = backend.start()
    if result.problem:
        log.warning("啟動：%s", result.problem)

    # DL-EN1 連線（DEV、MEA）尚未實作：目前以示範量測來源驅動畫面
    log.warning("量測來源：示範模式（DL-EN1 連線尚未實作，數值為隨機產生）")
    win = MainWindow(backend, lambda definition: DemoStation(definition, cfg.standards))
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
    for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(sig, lambda *_: win.close())
    pulse = QTimer(interval=300)
    pulse.timeout.connect(lambda: None)
    pulse.start()
    code = app.exec()
    backend.shutdown()  # DSC-07：App 結束時停止 dnsmasq
    return code


if __name__ == "__main__":
    sys.exit(main())
