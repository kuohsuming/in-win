#!/usr/bin/env bash
# 讓這台開發機開機自動啟動 App：在目前帳號建立 ~/.config/autostart/flatness.desktop（不需 sudo）。
#   ./scripts/install-autostart.sh          安裝
#   ./scripts/install-autostart.sh remove   移除
# 前提：已設定自動登入（/etc/gdm3/custom.conf）、已執行 sudo ./installer/setup-bootp.sh、.dev/db-system.env 存在。
set -euo pipefail
cd "$(dirname "$0")/.."
F="$HOME/.config/autostart/flatness.desktop"
if [[ ${1:-} == remove ]]; then rm -f "$F"; echo "已移除 $F"; exit 0; fi
mkdir -p "$(dirname "$F")"
cat > "$F" <<DESKTOP
[Desktop Entry]
Type=Application
Name=表面平整檢查系統
Comment=開機自動啟動（scripts/autostart.sh）
Exec=$PWD/scripts/autostart.sh
X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay=3
NoDisplay=false
Terminal=false
DESKTOP
echo "已安裝 $F"
