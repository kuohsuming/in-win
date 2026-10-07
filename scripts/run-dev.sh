#!/usr/bin/env bash
# 開發機執行 App：不需 root、不需 DL-EN1。
#   - 資料庫：拋棄式 MySQL（scripts/dev-mysql.sh），第一次以 installer/dl-en1.json 匯入（DEF-10）
#   - dnsmasq：改用 scripts/fake-dnsmasq.py，輸出示範的 BOOTP／DHCP 請求（探索 DSC-01）
#   - 設定檔：.dev/config.toml（由 installer/config.toml 產生；工程人員密碼 1234）
#   - 量測：示範量測來源（DL-EN1 連線尚未實作）
#
#   ./scripts/run-dev.sh                 全螢幕（與產線相同，UI-10）
#   ./scripts/run-dev.sh --windowed      一般視窗
#   ./scripts/run-dev.sh --no-dnsmasq    不啟動假 dnsmasq（不會探索到設備）
#   ./scripts/run-dev.sh --real          真機：以 sudo 執行真的 dnsmasq，BOOTP 對應寫到 /var/lib/flatness/bootp/
#                                        （需先執行一次 sudo ./installer/setup-bootp.sh）
set -euo pipefail
cd "$(dirname "$0")/.."

REAL=no
ARGS=()
for a in "$@"; do
  if [[ $a == --real ]]; then REAL=yes; else ARGS+=("$a"); fi
done

mkdir -p .dev/bootp
./scripts/dev-mysql.sh start >/dev/null
if [[ ! -f .dev/config.toml ]]; then
  hash=$(python3 -c 'import hashlib;print(hashlib.sha256(b"1234").hexdigest())')
  sed "s/^engineer_password_sha256 = \"\"/engineer_password_sha256 = \"$hash\"/" installer/config.toml > .dev/config.toml
fi

NET=$(sed -n 's/^pc_ip = "\(.*\)".*/\1/p' .dev/config.toml)/$(sed -n 's/^net_prefix = \([0-9]*\).*/\1/p' .dev/config.toml)
PYTHONPATH=app .venv/bin/python -m flatness.initdb --db-env .dev/db.env --def installer/dl-en1.json --equip-net "$NET"

if [[ $REAL == yes ]]; then
  # 真機：dnsmasq 主設定 /etc/flatness/dnsmasq.conf 固定讀 /var/lib/flatness/bootp/dl-en1.hosts
  HOSTS=/var/lib/flatness/bootp/dl-en1.hosts
  CMD="/usr/sbin/dnsmasq --keep-in-foreground --log-facility=- --conf-file=/etc/flatness/dnsmasq.conf"
  if [[ ! -f /etc/flatness/dnsmasq.conf || ! -w $HOSTS ]] || ! sudo -n -l $CMD >/dev/null 2>&1; then
    echo "真機模式尚未設定：請先執行  sudo ./installer/setup-bootp.sh" >&2
    exit 1
  fi
  PYTHONPATH=app exec .venv/bin/python -m flatness \
    --config .dev/config.toml --db-env .dev/db.env \
    --def .dev/dl-en1.json --hosts "$HOSTS" \
    --log-file .dev/flatness.log "${ARGS[@]}"
fi

PYTHONPATH=app exec .venv/bin/python -m flatness \
  --config .dev/config.toml --db-env .dev/db.env \
  --def .dev/dl-en1.json --hosts .dev/bootp/dl-en1.hosts \
  --dnsmasq-cmd "$PWD/.venv/bin/python $PWD/scripts/fake-dnsmasq.py --hosts $PWD/.dev/bootp/dl-en1.hosts" \
  --log-file .dev/flatness.log "${ARGS[@]}"
