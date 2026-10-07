#!/usr/bin/env bash
# 這台開發機的 App 捷徑（不需 sudo），皆執行 scripts/launch.sh、使用 app/flatness/ui/assets/app-icon.png：
#   - 桌面捷徑：點兩下啟動（已設為信任，不會跳出警告）
#   - 應用程式清單：按 Super 搜尋「表面平整」，可釘選到 Dock
#   - 開機自動啟動：登入後約 3 秒啟動
#   ./scripts/install-desktop.sh          安裝
#   ./scripts/install-desktop.sh remove   全部移除
# 前提：已設定自動登入（/etc/gdm3/custom.conf）、已執行 sudo ./installer/setup-bootp.sh、.dev/db-system.env 存在。
set -euo pipefail
cd "$(dirname "$0")/.."
DESKTOP_DIR=$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")
MENU="$HOME/.local/share/applications/flatness.desktop"
AUTO="$HOME/.config/autostart/flatness.desktop"
DESK="$DESKTOP_DIR/flatness.desktop"
if [[ ${1:-} == remove ]]; then
  rm -f "$MENU" "$AUTO" "$DESK"
  echo "已移除 $MENU、$AUTO、$DESK"
  exit 0
fi
entry() {  # $1 = launch.sh 的參數（記在日誌）
  cat <<DESKTOP
[Desktop Entry]
Type=Application
Version=1.0
Name=表面平整檢查系統
Comment=In Win 表面平整檢查（DL-EN1 真機）
Exec=$PWD/scripts/launch.sh $1
Icon=$PWD/app/flatness/ui/assets/app-icon.png
Terminal=false
Categories=Utility;
StartupWMClass=flatness
DESKTOP
}
mkdir -p "$(dirname "$MENU")" "$(dirname "$AUTO")" "$DESKTOP_DIR"
entry 選單 > "$MENU"
{ entry 開機; echo "X-GNOME-Autostart-enabled=true"; echo "X-GNOME-Autostart-Delay=3"; } > "$AUTO"
entry 桌面 > "$DESK"
chmod +x "$MENU" "$DESK"
gio set "$DESK" metadata::trusted true 2>/dev/null || true  # GNOME 桌面：允許點兩下執行
update-desktop-database "$(dirname "$MENU")" 2>/dev/null || true
echo "已安裝：$DESK、$MENU、$AUTO"
