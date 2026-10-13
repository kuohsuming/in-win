#!/usr/bin/env bash
# 桌面捷徑、應用程式清單與開機自動啟動共用的啟動程式（見 scripts/install-desktop.sh）：
# 真機模式、系統 MySQL；輸出寫到 .dev/autostart.log。
# App 已在執行時不再啟動第二個（App 本身會先停止舊的再啟動，NFR-14；從桌面誤點不應讓量測中的畫面重開）。
set -uo pipefail
cd "$(dirname "$0")/.."
exec >>.dev/autostart.log 2>&1
echo "=== $(date '+%F %T') 啟動（${1:-桌面}）"
if pgrep -f '^.venv/bin/python -m flatness' >/dev/null; then
  echo "App 已在執行，不重複啟動"
  command -v notify-send >/dev/null && notify-send -i "$PWD/app/flatness/ui/assets/app-icon.png" \
    "表面平整檢查系統" "App 已在執行中"
  exit 0
fi
for _ in $(seq 1 60); do  # 開機時最多等 60 秒，讓系統 MySQL 就緒
  [[ -S /var/run/mysqld/mysqld.sock ]] && break
  sleep 1
done
exec ./scripts/run-dev.sh --real --system-db
