# 步驟 2：設備網卡固定 IP，不使用 DHCP（INS-04、3.0.4）
# EQUIP_IF 可為單一實體網卡；或在 site.conf 設 EQUIP_BRIDGE_PORTS 時，EQUIP_IF 為由這些實體
# 埠橋接而成的 bridge（多個 LAN 埠同屬設備網，DL-EN1 插任一埠皆可）。
# 由 install.sh / setup-bootp.sh 在載入 common.sh 與 site.conf 後 source。

step_equip_net() {
  local default_if changed=0
  default_if=$(ip -4 route show default | awk '{print $5; exit}')

  if [[ -n ${EQUIP_BRIDGE_PORTS:-} ]]; then
    log "步驟 2：設備網卡 $EQUIP_IF（橋接 $EQUIP_BRIDGE_PORTS）固定 IP $PC_IP/$NET_PREFIX"

    # 防呆：被橋接的實體埠都不可是公司網路（預設路由所在網卡）
    local p eth_block="" if_list=""
    for p in $EQUIP_BRIDGE_PORTS; do
      [[ $p != "$default_if" ]] || fail "$p 是預設路由所在的公司網卡，不可加入設備橋接；請檢查 site.conf EQUIP_BRIDGE_PORTS"
      ip link show "$p" >/dev/null 2>&1 || fail "橋接埠 $p 不存在（ip -br link 查看網卡名稱）"
      eth_block+="    $p:"$'\n'"      dhcp4: false"$'\n'"      dhcp6: false"$'\n'"      link-local: []"$'\n'
      if_list+="${if_list:+, }$p"
    done

    if write_if_changed /etc/netplan/60-flatness-equipment.yaml 600 <<EOF
# 由表面平整檢查系統安裝包產生；修改請改 site.conf 後重新執行安裝包
network:
  version: 2
  renderer: NetworkManager
  ethernets:
$eth_block  bridges:
    $EQUIP_IF:
      interfaces: [$if_list]
      dhcp4: false
      dhcp6: false
      link-local: []
      addresses: [$PC_IP/$NET_PREFIX]
      parameters:
        stp: false
        forward-delay: 0
EOF
    then changed=1; fi
  else
    log "步驟 2：設備網卡 $EQUIP_IF 固定 IP $PC_IP/$NET_PREFIX"

    # 防呆：不可把公司網路（預設路由所在網卡）設成設備網卡
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
    then changed=1; fi
  fi

  if (( changed )); then
    netplan generate || fail "netplan 設定錯誤"
    netplan apply || fail "netplan apply 失敗"
    ok "已寫入 /etc/netplan/60-flatness-equipment.yaml 並套用"
  else
    ok "設備網卡設定未變更"
  fi
}
