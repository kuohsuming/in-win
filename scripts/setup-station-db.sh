#!/usr/bin/env bash
# 站台持久資料庫設定：安裝／啟用系統 MySQL、匯入 schema（sql/in-win.sql）、
# 設定 App 帳號 flatness_app 的密碼、寫出 .dev/db-system.env（真機模式連線資訊）。
#
# 以「執行 App 的一般帳號」執行（內部用 sudo 做 root 操作）；可重複執行，但會重設 flatness_app 密碼，
# 若 App 正在以舊密碼連線，請在重設後重新啟動 App。
#
#   ./scripts/setup-station-db.sh
set -euo pipefail
cd "$(dirname "$0")/.."

# 1. 系統 MySQL（Ubuntu 內建套件）
if ! command -v mysqld >/dev/null; then
  echo ">> 安裝 mysql-server…"
  sudo apt-get update -qq
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-server
fi
sudo systemctl enable --now mysql
for _ in $(seq 1 30); do [ -S /var/run/mysqld/mysqld.sock ] && break; sleep 1; done
[ -S /var/run/mysqld/mysqld.sock ] || { echo "MySQL socket 未就緒" >&2; exit 1; }

# 2. 匯入 schema（建 flatness／flatness_sim 與資料表、flatness_app 帳號與授權；可重複執行，亦用於升級）
echo ">> 匯入 sql/in-win.sql"
sudo mysql < sql/in-win.sql

# 3. App 帳號密碼：已設定且連得上就保留（避免打斷運行中的 App）；否則重設並寫 .dev/db-system.env（600）
SOCK=/var/run/mysqld/mysqld.sock
if [ -f .dev/db-system.env ] \
   && EXIST_PASS=$(sed -n 's/^DB_PASS=//p' .dev/db-system.env) && [ -n "$EXIST_PASS" ] \
   && mysql --no-defaults -uflatness_app -p"$EXIST_PASS" --socket="$SOCK" flatness -e "SELECT 1" >/dev/null 2>&1; then
  echo ">> flatness_app 已設定且可連線，保留現有密碼（.dev/db-system.env 不變）"
else
  PASS=$(python3 -c 'import secrets; print(secrets.token_urlsafe(18))')
  sudo mysql -e "ALTER USER 'flatness_app'@'localhost' IDENTIFIED BY '$PASS'; FLUSH PRIVILEGES;"
  mkdir -p .dev
  umask 077
  printf 'DB_SOCKET=%s\nDB_NAME=flatness\nDB_USER=flatness_app\nDB_PASS=%s\n' "$SOCK" "$PASS" > .dev/db-system.env
  chmod 600 .dev/db-system.env
  mysql --no-defaults -uflatness_app -p"$PASS" --socket="$SOCK" flatness -e "SELECT 1" >/dev/null 2>&1 \
    || { echo "flatness_app 連線測試失敗" >&2; exit 1; }
  echo ">> flatness_app 密碼已設定、.dev/db-system.env 已寫入"
fi
echo ">> 完成"
