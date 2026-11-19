#!/usr/bin/env bash
# 站台 kiosk 設定：開機自動登入（GDM）、不鎖屏、不待機黑屏、不自動睡眠。
# 以「執行 App 的一般帳號」在圖形桌面的終端機執行（gsettings 需要桌面 session；內部用 sudo）。
# 可重複執行。移除請見各段註解。
#
#   ./scripts/setup-kiosk.sh
set -euo pipefail
USER_NAME=$(whoami)

# 1. GDM 自動登入（/etc/gdm3/custom.conf 的 [daemon] 區）
if [ -d /etc/gdm3 ]; then
  sudo python3 -I - "$USER_NAME" <<'PY'
import sys, configparser
user = sys.argv[1]; path = "/etc/gdm3/custom.conf"
cfg = configparser.ConfigParser(); cfg.optionxform = str
cfg.read(path)
if not cfg.has_section("daemon"): cfg.add_section("daemon")
cfg.set("daemon", "AutomaticLoginEnable", "true")
cfg.set("daemon", "AutomaticLogin", user)
with open(path, "w") as f: cfg.write(f)
print("  GDM 自動登入 ->", user)
PY
else
  echo "  找不到 /etc/gdm3（非 GDM 桌面？）：請改在『設定 → 使用者 → 自動登入』手動開啟"
fi

# 2. 本 session 立即生效（存進使用者 dconf，重開機保留）
gsettings set org.gnome.desktop.screensaver lock-enabled false
gsettings set org.gnome.desktop.screensaver idle-activation-enabled false
gsettings set org.gnome.desktop.lockdown disable-lock-screen true
gsettings set org.gnome.desktop.session idle-delay 0
gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-type 'nothing'
gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-battery-type 'nothing'
gsettings set org.gnome.settings-daemon.plugins.power idle-dim false

# 3. 系統層 dconf 預設（任何 session／greeter／使用者設定被重置時仍維持）
sudo install -d -m 755 /etc/dconf/profile /etc/dconf/db/local.d
printf 'user-db:user\nsystem-db:local\n' | sudo tee /etc/dconf/profile/user >/dev/null
sudo tee /etc/dconf/db/local.d/00-kiosk >/dev/null <<'EOF'
[org/gnome/desktop/screensaver]
lock-enabled=false
idle-activation-enabled=false

[org/gnome/desktop/session]
idle-delay=uint32 0

[org/gnome/desktop/lockdown]
disable-lock-screen=true

[org/gnome/settings-daemon/plugins/power]
sleep-inactive-ac-type='nothing'
sleep-inactive-battery-type='nothing'
idle-dim=false
EOF
sudo dconf update

# 4. 遮蔽 systemd 睡眠／休眠（睡眠會中斷 DL-EN1 連線）
#    恢復：sudo systemctl unmask sleep.target suspend.target hibernate.target hybrid-sleep.target
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target

# 5. 關閉自動更新（避免產線時間自動更新／自動重開機）
#    恢復：sudo systemctl enable --now unattended-upgrades
if systemctl list-unit-files 2>/dev/null | grep -q '^unattended-upgrades'; then
  sudo systemctl disable --now unattended-upgrades 2>/dev/null || true
  echo "  已停用 unattended-upgrades（自動更新）"
fi

echo ">> 完成：自動登入、不鎖屏、不黑屏、不睡眠、關自動更新（重開機後生效）"
