#!/usr/bin/env bash
# 單獨架設 BOOTP 服務（設備網卡固定 IP + dnsmasq，開機自動啟動）。
# 完整安裝包 install.sh 完成前先用這支；之後 install.sh 會呼叫同樣的步驟。
#
# 使用：
#   1. 編輯 installer/site.conf（EQUIP_IF、PC_IP、NET_PREFIX）
#   2. 編輯 installer/dl-en1.json（每台 DL-EN1 的 MAC 與 IP）
#   3. sudo ./installer/setup-bootp.sh
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"
source "$INSTALLER_DIR/steps/02-equip-net.sh"
source "$INSTALLER_DIR/steps/03-bootp.sh"

require_root
load_site_conf
step_equip_net
step_bootp

log "完成。BOOTP 主機對應："
grep -v '^#' "$BOOTP_HOSTS" | tee -a "$LOG_FILE"
log "DL-EN1 重新上電後即取得上列 IP；查看配發紀錄：journalctl -u dnsmasq -f"
