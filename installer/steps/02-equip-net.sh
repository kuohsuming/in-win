# 步驟 2：設備網卡固定 IP，不使用 DHCP（INS-04、3.0.4）
# 由 install.sh / setup-bootp.sh 在載入 common.sh 與 site.conf 後 source。

step_equip_net() {
  log "步驟 2：設備網卡 $EQUIP_IF 固定 IP $PC_IP/$NET_PREFIX"

  # 防呆：不可把公司網路（預設路由所在網卡）設成設備網卡
  local default_if
  default_if=$(ip -4 route show default | awk '{print $5; exit}')
  [[ $default_if != "$EQUIP_IF" ]] || fail "$EQUIP_IF 是預設路由所在的公司網卡，不可作為設備網卡；請檢查 site.conf EQUIP_IF"

  if write_if_changed /etc/netplan/60-flatness-equipment.yaml 600 <<EOF
# 由表面平整檢查系統安裝包產生；修改請改 site.conf 後重新執行安裝包
network:
  version: 2
  renderer: NetworkManager
  ethernets:
    $EQUIP_IF:
      dhcp4: false
      dhcp6: false
      link-local: []
      addresses: [$PC_IP/$NET_PREFIX]
EOF
  then
    netplan generate || fail "netplan 設定錯誤"
    netplan apply || fail "netplan apply 失敗"
    ok "已寫入 /etc/netplan/60-flatness-equipment.yaml 並套用"
  else
    ok "設備網卡設定未變更"
  fi
}
