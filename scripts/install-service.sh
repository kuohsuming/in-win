#!/usr/bin/env bash
# 以 systemd 使用者服務自動啟動 App，崩潰自動重啟（Restart=always）——適合無人顧產線。
# 取代 install-desktop.sh 建立的開機自動啟動（.config/autostart/flatness.desktop）；
# 桌面捷徑與應用程式選單仍由 install-desktop.sh 提供。
#
#   ./scripts/install-service.sh            安裝並啟用（隨圖形登入自動啟動）
#   ./scripts/install-service.sh remove     移除服務（之後可再用 install-desktop.sh 的 autostart）
set -euo pipefail
cd "$(dirname "$0")/.."
REPO=$PWD
UNIT="$HOME/.config/systemd/user/flatness.service"

if [[ ${1:-} == remove ]]; then
  systemctl --user disable --now flatness.service 2>/dev/null || true
  rm -f "$UNIT"
  systemctl --user daemon-reload
  echo "已移除 flatness.service（如需 autostart 改跑 ./scripts/install-desktop.sh）"
  exit 0
fi

mkdir -p "$(dirname "$UNIT")"
cat > "$UNIT" <<EOF
[Unit]
Description=表面平整檢查系統（DL-EN1 真機）
After=graphical-session.target
PartOf=graphical-session.target

[Service]
Type=simple
WorkingDirectory=$REPO
# 真機模式、系統 MySQL；App 結束（含崩潰）後由 Restart 自動拉起。
# MySQL 尚未就緒時 run-dev 會失敗，RestartSec 後自動重試，直到可連線。
ExecStart=$REPO/scripts/run-dev.sh --real --system-db
Restart=always
RestartSec=3

[Install]
WantedBy=graphical-session.target
EOF

# 改由本服務啟動，移除 GNOME autostart，避免重複啟動
rm -f "$HOME/.config/autostart/flatness.desktop"

systemctl --user daemon-reload
systemctl --user enable flatness.service
systemctl --user restart flatness.service
echo "已安裝並啟用 flatness.service（Restart=always）。"
echo "  狀態：systemctl --user status flatness.service"
echo "  日誌：journalctl --user -u flatness.service -f"
