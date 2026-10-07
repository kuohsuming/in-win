#!/usr/bin/env python3
"""開發與測試用的假 dnsmasq：不需 root、不開任何網路埠，只依情境輸出與 dnsmasq log-dhcp 相同格式的紀錄。

App 以 --dnsmasq-cmd 改用本程式，即可在沒有 DL-EN1、沒有設備網路的開發機上看到探索結果（DSC-01）。

    fake-dnsmasq.py --hosts .dev/bootp/dl-en1.hosts                 示範情境
    fake-dnsmasq.py --scenario quiet                                 不輸出請求
    fake-dnsmasq.py --fail                                           模擬啟動失敗（設定錯誤）

示範情境：
    啟動時：主機對應中的每台設備送出 BOOTP／DHCP；另有一台不明的 KEYENCE 設備 00:01:FC:12:39:A0
    20 秒後：新的 KEYENCE 設備 00:01:FC:12:3B:11 上電
    每 30 秒：筆電 3C:52:82:11:22:33（eng-laptop）續約 DHCP
"""

import argparse
import random
import signal
import sys
import time
from pathlib import Path

IFACE = "eno2"
LAPTOP = ("3c:52:82:11:22:33", "eng-laptop", "MSFT 5.0")


def out(text):
    print(f"dnsmasq-dhcp: {text}", flush=True)


def hosts(path):
    table = {}
    if path and Path(path).exists():
        for line in Path(path).read_text().splitlines():
            if line and not line.startswith("#"):
                parts = line.split(",")
                table[parts[0].lower()] = (parts[1], parts[2] if len(parts) > 2 else "")
    return table


def bootp(mac, table):
    xid = random.randint(1000, 999999)
    if mac in table:
        ip, name = table[mac]
        out(f"{xid} BOOTP({IFACE}) {ip} {mac} {name}".rstrip())
    else:
        out(f"{xid} BOOTP({IFACE}) {mac} no address configured")


def dhcp(mac, table, name=None, vendor=None, kind="DHCPDISCOVER"):
    xid = random.randint(1000, 999999)
    ip = table.get(mac, (None,))[0]
    if ip:
        out(f"{xid} {kind}({IFACE}) {ip + ' ' if kind == 'DHCPREQUEST' else ''}{mac}")
    else:
        out(f"{xid} {kind}({IFACE}) {mac} no address available")
    if vendor:
        out(f"{xid} vendor class: {vendor}")
    if name:
        out(f"{xid} client provides name: {name}")
    if ip:
        out(f"{xid} {'DHCPACK' if kind == 'DHCPREQUEST' else 'DHCPOFFER'}({IFACE}) {ip} {mac} {name or ''}".rstrip())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--hosts")
    p.add_argument("--scenario", default="demo", choices=["demo", "quiet"])
    p.add_argument("--fail", action="store_true")
    p.add_argument("--conf-file")  # 與真 dnsmasq 參數相容，忽略
    p.add_argument("--tag")        # 測試用：區分不同的程序，忽略
    args, _ = p.parse_known_args()

    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    if args.fail:
        print("dnsmasq: bad option at line 3 of /etc/flatness/dnsmasq.conf", file=sys.stderr, flush=True)
        sys.exit(1)
    out(f"DHCP, static leases only on 192.168.10.0, lease time infinite")
    out(f"DHCP, sockets bound exclusively to interface {IFACE}")
    if args.scenario == "quiet":
        while True:
            time.sleep(3600)

    table = hosts(args.hosts)
    time.sleep(1)
    for mac in table:
        if mac.startswith("00:01:fc"):
            for _ in range(2):
                bootp(mac, table)
    bootp("00:01:fc:12:39:a0", table)
    dhcp(LAPTOP[0], table, LAPTOP[1], LAPTOP[2])
    start = time.monotonic()
    new_device_sent = False
    while True:
        time.sleep(1)
        elapsed = time.monotonic() - start
        if not new_device_sent and elapsed >= 20:
            for _ in range(3):
                bootp("00:01:fc:12:3b:11", table)
            new_device_sent = True
        if int(elapsed) % 30 == 0:
            dhcp(LAPTOP[0], table, LAPTOP[1], None, kind="DHCPREQUEST")


if __name__ == "__main__":
    main()
