#!/usr/bin/env bash
# 單獨架設 BOOTP 服務的系統部分（設備網卡固定 IP、dnsmasq 主設定、sudoers）。
# dnsmasq 由 App 啟動（DSC-07），本程式執行後 dnsmasq.service 為 masked。
# 完整安裝包 install.sh 完成前先用這支；之後 install.sh 會呼叫同樣的步驟。
#
# 使用：
#   1. 編輯 installer/site.conf（EQUIP_IF、PC_IP、NET_PREFIX）
#   2. sudo ./installer/setup-bootp.sh
#   3. DL-EN1 清單：安裝 MySQL 後以 python -m flatness.initdb 匯入 installer/dl-en1.json（DEF-10），
#      之後在 App「設備設定」維護
set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"
source "$INSTALLER_DIR/steps/02-equip-net.sh"
source "$INSTALLER_DIR/steps/03-bootp.sh"

require_root
load_site_conf
step_equip_net
step_bootp

log "完成。dnsmasq 由 App 啟動；App 執行中 DL-EN1 上電即取得資料庫中設定的 IP。"
