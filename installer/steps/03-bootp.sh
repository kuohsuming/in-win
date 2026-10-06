# 步驟 3：BOOTP 服務（INS-04、3.0.4、DEF-03、DEF-10）
# dnsmasq 只在設備網卡上運作、關閉 DNS，依 MAC 對應表配發固定 IP 給 DL-EN1，開機自動啟動。
# 由 install.sh / setup-bootp.sh 在載入 common.sh 與 site.conf 後 source。

BOOTP_DIR=/var/lib/flatness/bootp
BOOTP_HOSTS=$BOOTP_DIR/dl-en1.hosts
DNSMASQ_CONF=/etc/dnsmasq.d/flatness-dl-en1.conf
DEF_DST=/etc/flatness/dl-en1.json

step_bootp() {
  log "步驟 3：BOOTP 服務（dnsmasq）"
  local changed=0 net_addr netmask

  read -r net_addr netmask < <(python3 -c '
import ipaddress, sys
n = ipaddress.IPv4Interface(sys.argv[1]).network
print(n.network_address, n.netmask)' "$PC_IP/$NET_PREFIX") || fail "PC_IP/NET_PREFIX 格式錯誤"

  # 1. DL-EN1 定義檔：已存在則保留現場版本（3.0.8）
  local def_src="$INSTALLER_DIR/$DLEN1_DEF_FILE"
  [[ $DLEN1_DEF_FILE == /* ]] && def_src=$DLEN1_DEF_FILE
  # App 在設備設定畫面套用時，以「暫存檔 + 改名」原子覆寫定義檔並在此建立備份（UPL-06、UPL-07），
  # 故 /etc/flatness 目錄須讓 App 帳號群組可寫
  install -d -m 2775 -o root -g "$APP_USER" /etc/flatness
  if [[ ! -f $DEF_DST ]]; then
    [[ -f $def_src ]] || fail "找不到 DL-EN1 定義檔 $def_src"
    install -D -m 664 -o root -g "$APP_USER" "$def_src" "$DEF_DST"
    ok "已安裝定義檔 $DEF_DST"
  else
    ok "定義檔已存在，保留現場版本 $DEF_DST"
  fi
  PYTHONPATH="$PKG_DIR/app" python3 -m flatness.bootp check \
      --def "$DEF_DST" --equip-net "$PC_IP/$NET_PREFIX" || fail "DL-EN1 定義檔驗證失敗"

  # 2. BOOTP 主機對應檔：已存在則保留（3.0.8）；App 上傳定義檔時重新產生（DEF-03）
  install -d -m 755 -o "$APP_USER" -g "$APP_USER" "$BOOTP_DIR"
  if [[ ! -f $BOOTP_HOSTS ]]; then
    PYTHONPATH="$PKG_DIR/app" python3 -m flatness.bootp apply --no-restart \
        --def "$DEF_DST" --equip-net "$PC_IP/$NET_PREFIX" --hosts "$BOOTP_HOSTS" \
        || fail "產生 BOOTP 主機對應檔失敗"
    chown "$APP_USER:$APP_USER" "$BOOTP_HOSTS"
    changed=1
  else
    ok "BOOTP 主機對應檔已存在，保留 $BOOTP_HOSTS"
  fi

  # 3. dnsmasq 設定：先寫設定再安裝套件，避免套件安裝時以預設 DNS 模式啟動而與 systemd-resolved 衝突
  if write_if_changed "$DNSMASQ_CONF" 644 <<EOF
# 由表面平整檢查系統安裝包產生；修改請改 site.conf 後重新執行安裝包
# 只做 BOOTP/DHCP，不做 DNS（避免與 systemd-resolved 衝突）
port=0
# 只在設備網卡上運作；bind-dynamic 讓網卡較晚取得 IP（例如開機時未接網路線）也能自動開始服務
interface=$EQUIP_IF
bind-dynamic
# static：只配發給對應檔中有登錄 MAC 的設備；BOOTP 用戶端只會取得對應檔中的 IP
dhcp-range=$net_addr,static,$netmask,infinite
dhcp-hostsfile=$BOOTP_HOSTS
log-dhcp
EOF
  then
    changed=1
    ok "已寫入 $DNSMASQ_CONF"
  else
    ok "dnsmasq 設定未變更"
  fi

  # 4. 安裝 dnsmasq
  if ! dpkg -s dnsmasq >/dev/null 2>&1; then
    DEBIAN_FRONTEND=noninteractive apt-get install -y dnsmasq >>"$LOG_FILE" 2>&1 || fail "安裝 dnsmasq 失敗"
    changed=1
    ok "已安裝 dnsmasq"
  fi
  dnsmasq --test --conf-file="$DNSMASQ_CONF" >>"$LOG_FILE" 2>&1 || fail "dnsmasq 設定檢查失敗，詳見 $LOG_FILE"

  # 5. 防火牆：只在設備網卡開放 UDP 67
  if command -v ufw >/dev/null; then
    ufw allow in on "$EQUIP_IF" to any port 67 proto udp comment 'flatness BOOTP' >>"$LOG_FILE" 2>&1 \
      && ok "防火牆：$EQUIP_IF 開放 UDP 67"
  fi

  # 6. 允許 App 帳號重啟 dnsmasq（僅此一項 root 權限）
  local sudoers_tmp
  sudoers_tmp=$(mktemp)
  echo "$APP_USER ALL=(root) NOPASSWD: /usr/bin/systemctl restart dnsmasq" > "$sudoers_tmp"
  visudo -cf "$sudoers_tmp" >/dev/null || { rm -f "$sudoers_tmp"; fail "sudoers 內容錯誤"; }
  write_if_changed /etc/sudoers.d/flatness 440 < "$sudoers_tmp" && ok "已設定 /etc/sudoers.d/flatness"
  rm -f "$sudoers_tmp"

  # 7. 開機自動啟動；設定有變更才重啟
  systemctl enable dnsmasq >>"$LOG_FILE" 2>&1 || fail "無法設定 dnsmasq 開機啟動"
  if (( changed )) || ! systemctl is-active --quiet dnsmasq; then
    systemctl restart dnsmasq || fail "dnsmasq 啟動失敗：journalctl -u dnsmasq -n 30"
  fi
  systemctl is-active --quiet dnsmasq || fail "dnsmasq 未運作"
  ok "dnsmasq 運作中，已設定開機自動啟動"
}
