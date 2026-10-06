# 安裝包共用函式；由 install.sh / setup-*.sh 以 source 載入。

PKG_DIR="${PKG_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
INSTALLER_DIR="$PKG_DIR/installer"
LOG_FILE="${LOG_FILE:-/var/log/flatness-install.log}"

log()  { printf '[%s] %s\n' "$(date '+%F %T')" "$*" | tee -a "$LOG_FILE"; }
ok()   { log "  ✔ $*"; }
fail() { log "  ✘ $*"; exit 1; }

require_root() {
  [[ $EUID -eq 0 ]] || { echo "請以 sudo 執行：sudo $0" >&2; exit 1; }
}

# 讀取 site.conf，檢查本步驟需要的欄位（3.0.1）
load_site_conf() {
  local conf="$INSTALLER_DIR/site.conf"
  [[ -f $conf ]] || fail "找不到 $conf"
  # shellcheck disable=SC1090
  source "$conf"
  APP_USER="${APP_USER:-${SUDO_USER:-}}"
  [[ -n $APP_USER ]] || fail "site.conf APP_USER 為空，且無法由 sudo 取得執行帳號"
  id "$APP_USER" >/dev/null 2>&1 || fail "帳號 $APP_USER 不存在"
  [[ -n ${EQUIP_IF:-} ]] || fail "site.conf 缺少 EQUIP_IF"
  [[ -n ${PC_IP:-} && -n ${NET_PREFIX:-} ]] || fail "site.conf 缺少 PC_IP 或 NET_PREFIX"
  [[ -n ${DLEN1_DEF_FILE:-} ]] || fail "site.conf 缺少 DLEN1_DEF_FILE"
  ip link show "$EQUIP_IF" >/dev/null 2>&1 || fail "設備網卡 $EQUIP_IF 不存在（ip -br link 查看網卡名稱）"
}

# 內容不同才寫入；有寫入回傳 0，內容相同回傳 1（3.0.8：內容相同時不重啟服務）
write_if_changed() {
  local path=$1 mode=$2 content
  content=$(cat)
  if [[ -f $path ]] && [[ "$(cat "$path")" == "$content" ]]; then
    return 1
  fi
  install -D -m "$mode" /dev/null "$path"
  printf '%s\n' "$content" > "$path"
  return 0
}
