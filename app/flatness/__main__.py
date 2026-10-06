"""啟動表面平整檢查系統 App：python -m flatness [選項]"""

from __future__ import annotations

import argparse
import ipaddress
import logging
import sys
from pathlib import Path

from . import bootp


def parse_args(argv=None):
    p = argparse.ArgumentParser(prog="flatness", description="表面平整檢查系統")
    p.add_argument("--def", dest="def_file", type=Path, default=Path("/etc/flatness/dl-en1.json"),
                   help="DL-EN1 定義檔（預設 /etc/flatness/dl-en1.json）")
    p.add_argument("--hosts", type=Path, default=Path("/var/lib/flatness/bootp/dl-en1.hosts"),
                   help="dnsmasq BOOTP 主機對應檔")
    p.add_argument("--equip-net", type=ipaddress.IPv4Interface,
                   default=ipaddress.IPv4Interface("192.168.10.1/24"),
                   help="量測 PC 設備網卡 IP/遮罩長度（site.conf PC_IP/NET_PREFIX）")
    p.add_argument("--no-restart", action="store_true", help="開發用：套用時不重啟 dnsmasq")
    p.add_argument("--log-file", type=Path, default=Path("/var/log/flatness/flatness.log"))
    p.add_argument("--fullscreen", action="store_true", help="產線全螢幕")
    p.add_argument("--on-top", action="store_true", help="視窗保持在最上層（Wayland 下需搭配 QT_QPA_PLATFORM=xcb）")
    return p.parse_args(argv)


def setup_logging(log_file: Path):
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    try:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    except OSError:
        pass  # 開發機沒有 /var/log/flatness 時只輸出到終端機
    logging.basicConfig(level=logging.INFO, handlers=handlers,
                        format="%(asctime)s %(levelname)s %(name)s %(message)s")


def main(argv=None) -> int:
    args = parse_args(argv)
    setup_logging(args.log_file)

    from PySide6.QtGui import QFont, QFontDatabase
    from PySide6.QtWidgets import QApplication

    from .ui.main_window import MainWindow

    app = QApplication(sys.argv[:1])
    for family in ("Noto Sans CJK TC", "Noto Sans TC", "Noto Sans CJK JP"):
        if family in QFontDatabase.families():
            app.setFont(QFont(family, 12))
            break

    win = MainWindow(args.def_file, args.hosts, args.equip_net,
                     restart_cmd=None if args.no_restart else bootp.RESTART_CMD)
    if args.on_top:
        from PySide6.QtCore import Qt
        win.setWindowFlag(Qt.WindowStaysOnTopHint, True)
    if args.fullscreen:
        win.showFullScreen()
    else:
        win.resize(1280, 800)
        win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
