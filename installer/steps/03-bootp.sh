# 步驟 3：BOOTP 服務（INS-04、3.0.4、DSC-07）
# 安裝 dnsmasq 並遮蔽作業系統的 dnsmasq.service：dnsmasq 由 App 啟動與管理，開機時不啟動。
# 產生 root 擁有、App 不可改的主設定；sudoers 只允許 App 帳號以固定參數執行 dnsmasq。
# BOOTP 主機對應由 App 啟動時依資料庫產生（DSC-06），安裝包不寫入內容。
# 由 install.sh / setup-bootp.sh 在載入 common.sh 與 site.conf 後 source。

BOOTP_DIR=/var/lib/flatness/bootp
BOOTP_HOSTS=$BOOTP_DIR/dl-en1.hosts
DNSMASQ_CONF=/etc/flatness/dnsmasq.conf
OLD_DNSMASQ_CONF=/etc/dnsmasq.d/flatness-dl-en1.conf   # 舊版安裝包（由系統服務啟動）留下的設定
# 與 app/flatness/dnsmasq.py 的 COMMAND 必須完全相同
DNSMASQ_CMD="/usr/sbin/dnsmasq --keep-in-foreground --log-facility=- --conf-file=$DNSMASQ_CONF"
# 與 app/flatness/dnsmasq.py 的 STOP_COMMAND 相同：停止 App 啟動的 dnsmasq（含 App 當掉後的殘留）
STOP_HELPER=/usr/local/sbin/flatness-stop-dnsmasq
# 與 app/flatness/arpwatch.py 的 COMMAND 相同：監聽設備網卡的 ARP 位址偵測封包（DSC-19）
ARP_HELPER=/usr/local/sbin/flatness-arp-watch

step_bootp() {
  log "步驟 3：BOOTP 服務（dnsmasq，由 App 啟動）"
  local net_addr netmask

  read -r net_addr netmask < <(python3 -c '
import ipaddress, sys
n = ipaddress.IPv4Interface(sys.argv[1]).network
print(n.network_address, n.netmask)' "$PC_IP/$NET_PREFIX") || fail "PC_IP/NET_PREFIX 格式錯誤"

  # 1. 目錄：/etc/flatness 讓 App 帳號群組可寫（App 原子覆寫 dl-en1.json 並在此備份，3.0.6），
  #    加上 sticky bit，App 只能改自己擁有的檔案，不能刪除或替換 root 擁有的 dnsmasq.conf（DSC-07-A5）
  install -d -m 3775 -o root -g "$APP_USER" /etc/flatness
  install -d -m 755 -o "$APP_USER" -g "$APP_USER" "$BOOTP_DIR"
  # 資料庫斷線時的量測結果本機暫存（DAT-04、3.0.6）
  install -d -m 750 -o "$APP_USER" -g "$APP_USER" /var/lib/flatness/buffer
  if [[ ! -f $BOOTP_HOSTS ]]; then
    echo "# 由 App 依資料庫 lan_device 產生（DSC-06）" | install -m 644 -o "$APP_USER" -g "$APP_USER" /dev/stdin "$BOOTP_HOSTS"
  fi

  # 2. 主設定（root 擁有、App 不可寫）
  if write_if_changed "$DNSMASQ_CONF" 644 <<EOF
# 由表面平整檢查系統安裝包產生；修改請改 site.conf 後重新執行安裝包
# dnsmasq 由 App 以 sudo 執行（DSC-07），此檔不可由 App 修改
# 只做 BOOTP/DHCP，不做 DNS（避免與 systemd-resolved 衝突）
port=0
# 只在設備網卡上運作；bind-dynamic 讓網卡較晚取得 IP（例如開機時未接網路線）也能自動開始服務
interface=$EQUIP_IF
bind-dynamic
# static：只配發給主機對應中有登錄 MAC 的設備
dhcp-range=$net_addr,static,$netmask,infinite
dhcp-hostsfile=$BOOTP_HOSTS
# 記錄每一筆請求（含未登錄的 MAC、主機名稱、廠商識別），App 以此探索設備（DSC-01）
log-dhcp
# 由 App 管理程序，不寫 PID 檔
pid-file=
EOF
  then
    ok "已寫入 $DNSMASQ_CONF"
  else
    ok "dnsmasq 主設定未變更"
  fi

  # 3. 安裝 dnsmasq；遮蔽作業系統的服務（INS-04）
  if ! dpkg -s dnsmasq >/dev/null 2>&1; then
    # 先遮蔽再安裝，避免套件安裝時以預設 DNS 模式啟動而與 systemd-resolved 衝突
    systemctl mask dnsmasq >>"$LOG_FILE" 2>&1 || true
    DEBIAN_FRONTEND=noninteractive apt-get install -y dnsmasq >>"$LOG_FILE" 2>&1 || fail "安裝 dnsmasq 失敗"
    ok "已安裝 dnsmasq"
  fi
  systemctl disable --now dnsmasq >>"$LOG_FILE" 2>&1 || true
  systemctl mask dnsmasq >>"$LOG_FILE" 2>&1 || fail "無法遮蔽 dnsmasq.service"
  ok "dnsmasq.service 已停用並遮蔽（由 App 啟動）"
  if [[ -f $OLD_DNSMASQ_CONF ]]; then
    rm -f "$OLD_DNSMASQ_CONF"
    ok "已移除舊版設定 $OLD_DNSMASQ_CONF"
  fi
  dnsmasq --test --conf-file="$DNSMASQ_CONF" >>"$LOG_FILE" 2>&1 || fail "dnsmasq 主設定檢查失敗，詳見 $LOG_FILE"

  # 4. 防火牆：只在設備網卡開放 UDP 67
  if command -v ufw >/dev/null; then
    ufw allow in on "$EQUIP_IF" to any port 67 proto udp comment 'flatness BOOTP' >>"$LOG_FILE" 2>&1 \
      && ok "防火牆：$EQUIP_IF 開放 UDP 67"
  fi

  # 5. 停止程式：root 擁有、App 不可改；不接受參數，只停止以固定命令列執行的 dnsmasq（DSC-07）
  #    sudo 啟動的 dnsmasq 為 root 程序，App 帳號無法直接送訊號停止
  if write_if_changed "$STOP_HELPER" 755 <<EOF
#!/bin/sh
# 由表面平整檢查系統安裝包產生：停止 App 啟動的 dnsmasq（DSC-07）；不接受參數
exec /usr/bin/pkill -TERM -x -f '$DNSMASQ_CMD'
EOF
  then
    ok "已寫入 $STOP_HELPER"
  fi

  # 6. ARP 監聽程式：root 擁有、App 不可改；不接受參數，只監聽設備網卡（DSC-19）
  #    DL-EN1 取得 IP 後上電不再送 BOOTP，只送 ARP 位址偵測封包；監聽網卡需要 root
  if sed "s/@EQUIP_IF@/$EQUIP_IF/g" "$INSTALLER_DIR/files/flatness-arp-watch" | write_if_changed "$ARP_HELPER" 755; then
    ok "已寫入 $ARP_HELPER（監聽 $EQUIP_IF）"
  fi

  # 7. sudoers：只允許 App 帳號以固定參數執行 dnsmasq，以及不帶參數執行停止程式與 ARP 監聽程式（DSC-07-A5）
  local sudoers_tmp
  sudoers_tmp=$(mktemp)
  echo "$APP_USER ALL=(root) NOPASSWD: $DNSMASQ_CMD, $STOP_HELPER \"\", $ARP_HELPER \"\"" > "$sudoers_tmp"
  visudo -cf "$sudoers_tmp" >/dev/null || { rm -f "$sudoers_tmp"; fail "sudoers 內容錯誤"; }
  write_if_changed /etc/sudoers.d/flatness 440 < "$sudoers_tmp" && ok "已設定 /etc/sudoers.d/flatness"
  rm -f "$sudoers_tmp"
}
