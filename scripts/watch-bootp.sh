#!/usr/bin/env bash
# 監看設備網卡上的 BOOTP 封包與 dnsmasq 配發紀錄，用來確認 DL-EN1 上電後是否取得 IP。
#
# 使用：sudo ./scripts/watch-bootp.sh            （網卡取自 installer/site.conf 的 EQUIP_IF）
#       sudo ./scripts/watch-bootp.sh eno2       （指定網卡）
# 結束：Ctrl+C。封包另存為 /var/log/flatness/bootp-<時間>.pcap，可用 Wireshark 開啟。
set -euo pipefail
cd "$(dirname "$0")/.."

[[ $EUID -eq 0 ]] || { echo "需要 root 才能擷取封包：sudo $0 $*" >&2; exit 1; }

IFACE=${1:-$(sed -n 's/^EQUIP_IF=\([^ #]*\).*/\1/p' installer/site.conf)}
ip link show "$IFACE" >/dev/null 2>&1 || { echo "網卡 $IFACE 不存在（ip -br link 查看）" >&2; exit 1; }

echo "=== 設備網卡 $IFACE ==="
ip -br addr show "$IFACE"
if [[ $(cat "/sys/class/net/$IFACE/carrier" 2>/dev/null) != 1 ]]; then
  echo "⚠ $IFACE 沒有連線訊號（網路線未接或 DL-EN1 未上電）；接上後封包會自動出現"
fi
echo "=== dnsmasq：$(systemctl is-active dnsmasq) ==="
[[ -f /var/lib/flatness/bootp/dl-en1.hosts ]] && grep -v '^#' /var/lib/flatness/bootp/dl-en1.hosts \
  | sed 's/^/  對應：/'
echo

mkdir -p /var/log/flatness
PCAP=/var/log/flatness/bootp-$(date +%Y%m%d-%H%M%S).pcap
echo "監看中（Ctrl+C 結束），封包另存 $PCAP"
echo "  [封包]   BOOTP Request = DL-EN1 廣播要 IP；Reply = 伺服器回覆，Your-IP 為配發的位址"
echo "  [dnsmasq] BOOTP(介面) IP MAC 名稱 = dnsmasq 已配發"
echo

trap 'kill 0 2>/dev/null' EXIT INT TERM

journalctl -u dnsmasq -f -n 0 -o cat 2>/dev/null | sed -u 's/^/[dnsmasq] /' &

# -e 顯示 MAC；-vvv 解碼 BOOTP 欄位；--print 同時顯示並寫檔
tcpdump -i "$IFACE" -n -e -l -vvv --print -w "$PCAP" 'udp port 67 or udp port 68' 2>&1 \
  | grep --line-buffered -E 'ethertype IPv4|BOOTP|Client-Ethernet-Address|Client-IP|Your-IP|Server-IP|Hostname|listening|packets' \
  | sed -u 's/^ */[封包]   /'
