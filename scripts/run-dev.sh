#!/usr/bin/env bash
# 開發機執行 App：定義檔與 BOOTP 主機對應放在 .dev/，套用時不重啟 dnsmasq。
#   ./scripts/run-dev.sh            一般視窗
#   ./scripts/run-dev.sh --fullscreen
set -euo pipefail
cd "$(dirname "$0")/.."

mkdir -p .dev
[[ -f .dev/dl-en1.json ]] || cp installer/dl-en1.json .dev/dl-en1.json

PYTHONPATH=app exec .venv/bin/python -m flatness \
  --def .dev/dl-en1.json --hosts .dev/bootp/dl-en1.hosts \
  --log-file .dev/flatness.log --no-restart "$@"
