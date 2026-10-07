#!/usr/bin/env bash
# 開機登入後自動啟動 App（由 ~/.config/autostart/flatness.desktop 呼叫，見 scripts/install-autostart.sh）：
# 真機模式、系統 MySQL；等設備網卡與 MySQL 就緒後才啟動，輸出寫到 .dev/autostart.log。
set -uo pipefail
cd "$(dirname "$0")/.."
exec >>.dev/autostart.log 2>&1
echo "=== $(date '+%F %T') 開機自動啟動"
for _ in $(seq 1 60); do  # 最多等 60 秒
  [[ -S /var/run/mysqld/mysqld.sock ]] && break
  sleep 1
done
exec ./scripts/run-dev.sh --real --system-db "$@"
