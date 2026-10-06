#!/usr/bin/env bash
# 開發機用的拋棄式 MySQL：以目前帳號執行，不需 sudo、不碰系統的 MySQL。
# 資料放在 /tmp/flatness-dev-mysql-<帳號>/（Ubuntu 的 AppArmor 不允許 mysqld 寫入家目錄；重開機後清空）。
#   ./scripts/dev-mysql.sh start    初始化（第一次）、啟動並執行 sql/in-win.sql，寫出 .dev/db.env
#   ./scripts/dev-mysql.sh stop
#   ./scripts/dev-mysql.sh status
#   ./scripts/dev-mysql.sh sql      以 root 開啟 mysql 命令列
#   ./scripts/dev-mysql.sh reset    停止並刪除資料目錄（資料全部清除）
set -euo pipefail
cd "$(dirname "$0")/.."

D="${DEV_MYSQL_DIR:-/tmp/flatness-dev-mysql-$(whoami)}"
SOCK="$D/mysql.sock"
DEV_PASS="dev-only-password"

running() { [[ -S "$SOCK" ]] && mysqladmin --no-defaults -uroot --socket="$SOCK" ping >/dev/null 2>&1; }
client() { mysql --no-defaults -uroot --socket="$SOCK" "$@"; }

start() {
  if running; then echo "MySQL 已在執行（$SOCK）"; else
    if [[ ! -d "$D/data" ]]; then
      mkdir -p "$D" .dev
      mysqld --no-defaults --initialize-insecure --datadir="$D/data" --user="$(whoami)" >"$D/init.log" 2>&1
    fi
    mysqld --no-defaults --datadir="$D/data" --socket="$SOCK" --port=0 --skip-networking \
      --mysqlx=OFF --pid-file="$D/mysqld.pid" --log-error="$D/err.log" --user="$(whoami)" &
    for _ in $(seq 1 30); do running && break; sleep 1; done
    running || { echo "MySQL 啟動失敗，見 $D/err.log" >&2; exit 1; }
  fi
  client < sql/in-win.sql >/dev/null
  client -e "ALTER USER 'flatness_app'@'localhost' IDENTIFIED BY '$DEV_PASS'"
  mkdir -p .dev
  cat > .dev/db.env <<EOF
DB_SOCKET=$SOCK
DB_NAME=flatness
DB_USER=flatness_app
DB_PASS=$DEV_PASS
EOF
  echo "MySQL 已就緒：$SOCK（連線資訊 .dev/db.env）"
}

stop() {
  if running; then
    mysqladmin --no-defaults -uroot --socket="$SOCK" shutdown
    echo "MySQL 已停止"
  else
    echo "MySQL 未執行"
  fi
}

case "${1:-}" in
  start) start ;;
  stop) stop ;;
  status) running && echo "執行中（$SOCK）" || echo "未執行" ;;
  sql) client flatness ;;
  reset) stop; rm -rf "$D"; echo "已刪除 $D" ;;
  *) sed -n '2,8p' "$0"; exit 2 ;;
esac
