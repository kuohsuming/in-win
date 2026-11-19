#!/usr/bin/env bash
# 站台安裝後／重開機後驗證：登入與畫面、網路、MySQL、App 自動啟動、dnsmasq 綁定。
# 以一般帳號在桌面終端機執行；不需 sudo。
#   ./scripts/verify-station.sh
cd "$(dirname "$0")/.."
ok(){ printf '  \033[32m✔\033[0m %s\n' "$*"; }
no(){ printf '  \033[31mX\033[0m %s\n' "$*"; }
warn(){ printf '  \033[33m•\033[0m %s\n' "$*"; }

echo "=== 站台驗證 $(date '+%F %T') ==="

echo "[1] 登入 / 畫面"
[ "$(gsettings get org.gnome.desktop.screensaver lock-enabled 2>/dev/null)" = false ] && ok "不鎖屏" || warn "鎖屏未關閉"
[ "$(gsettings get org.gnome.desktop.session idle-delay 2>/dev/null)" = "uint32 0" ] && ok "螢幕永不待機" || warn "待機黑屏未關閉"

echo "[2] 網路"
ip -br addr show br-lan 2>/dev/null | grep -q 192.168 && ok "br-lan 有設備網段 IP" || warn "br-lan 無 IP（或非 bridge 站台）"
ip -4 route show default | grep -q . && ok "有預設路由（WAN）" || warn "無預設路由"

echo "[3] 系統 MySQL"
if systemctl is-active --quiet mysql; then ok "mysql 服務執行中"; else no "mysql 未執行"; fi
if [ -f .dev/db-system.env ]; then
  P=$(sed -n 's/^DB_PASS=//p' .dev/db-system.env)
  n=$(mysql --no-defaults -uflatness_app -p"$P" --socket=/var/run/mysqld/mysqld.sock flatness \
        -N -e "SELECT COUNT(*) FROM lan_device" 2>/dev/null)
  [ -n "$n" ] && ok "flatness_app 可連線（lan_device $n 筆）" || no "flatness_app 連不上"
else
  no ".dev/db-system.env 不存在（尚未跑 setup-station-db.sh）"
fi

echo "[4] App 自動啟動（真機模式）"
pgrep -f '[-]m flatness' >/dev/null && ok "App 執行中" || no "App 未執行（journalctl --user -u flatness.service）"
if systemctl --user list-unit-files 2>/dev/null | grep -q '^flatness.service'; then
  st=$(systemctl --user is-active flatness.service 2>/dev/null)
  nr=$(systemctl --user show flatness.service -p NRestarts --value 2>/dev/null)
  [ "$st" = active ] && ok "flatness.service $st（自動重啟次數 ${nr:-0}）" || warn "flatness.service: $st"
else
  warn "未安裝 flatness.service（autostart 模式；建議跑 install-service.sh）"
fi

echo "[5] dnsmasq（由 App 啟動，綁 br-lan:67）"
pgrep -f '[d]nsmasq --keep-in-foreground' >/dev/null && ok "dnsmasq 執行中" || warn "dnsmasq 未執行（App 未起或 br-lan 尚未可用）"
ss -lun 2>/dev/null | grep -q ':67' && ok "UDP 67 已監聽" || warn "UDP 67 未監聽（br-lan 未接線時，bind-dynamic 會等接線才服務）"

echo "=== 日誌：.dev/autostart.log、.dev/flatness.log ==="
