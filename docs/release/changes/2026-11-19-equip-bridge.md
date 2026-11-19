# 2026-11-19 設備網卡支援多實體埠橋接（installer）

安裝包的設備網卡設定（步驟 2，INS-04）原本只支援單一實體網卡：`step_equip_net` 把 `EQUIP_IF` 當成 ethernet、寫一份固定 IP 的 `60-flatness-equipment.yaml`。當站台要用多個實體 LAN 埠（DL-EN1 插任一埠皆可）時，必須先手動把那些埠橋接成一個 bridge 當 `EQUIP_IF`——但再次執行安裝包時 `step_equip_net` 會把該 bridge 當普通 ethernet 覆寫，破壞橋接。

本次讓安裝包認得橋接，從 `site.conf` 宣告式重建正確 netplan（維持 INS-02「只改 site.conf」）。

## 設定（site.conf）
- 新增 `EQUIP_BRIDGE_PORTS`：空白分隔的實體網卡清單；設定後 `EQUIP_IF` 為由這些埠橋接而成的 bridge 名稱（如 `br-lan`）。**留空＝維持原本單一網卡行為，既有單埠站台不受影響。**
- 本站設定：`EQUIP_IF=br-lan`、`EQUIP_BRIDGE_PORTS="enp2s0 enp3s0"`（port1+port2 為設備 LAN；WAN 走 port3/enp4s0）。

## 程式
- `installer/steps/02-equip-net.sh`：`EQUIP_BRIDGE_PORTS` 非空時產生 **bridge 版** netplan——每個實體埠為 `dhcp4/6:false` 的 ethernet，`bridges.<EQUIP_IF>` 橋接這些埠並設 `addresses:[PC_IP/NET_PREFIX]`、`stp:false`、`forward-delay:0`；留空時維持原 ethernet 版。防呆擴充：被橋接的每個實體埠都不可是預設路由（公司網路）網卡，且須存在。
- `installer/lib/common.sh`：`load_site_conf` 在橋接模式下改檢查各實體埠存在（bridge 本身可能尚未建立，由 step_equip_net 產生），非橋接模式仍檢查 `EQUIP_IF`。
- `03-bootp.sh`（dnsmasq `interface=`、ufw、`flatness-arp-watch`）沿用 `EQUIP_IF`，橋接時自然綁在 bridge 上，不需修改。

## 驗證
- `bash -n` 語法檢查通過；乾跑產生的 YAML 格式正確。
- 真機（本開發/站台機，Ubuntu 22.04）實跑 `load_site_conf`＋`step_equip_net`：重建並套用 bridge netplan 成功，`br-lan` 仍為 `192.168.10.1/24`、橋接 `enp2s0`/`enp3s0`，WAN（`enp4s0`）不受影響、對外連線正常；重跑具冪等性（內容相同不重套用）。
- 另已跑 `step_bootp`：`/etc/flatness/dnsmasq.conf` 綁 `interface=br-lan`，實測 dnsmasq 綁 `br-lan:67` 成功。

## 待辦（規格書 gap，未自動修改）
- 需求規格書 `Downloads/表面平整檢查系統_需求規格書.md` 仍將 `EQUIP_IF` 描述為單一「設備網卡」（INS-02 欄位清單、§安裝步驟、`site.conf` 欄位表 enp3s0 範例）。多埠橋接能力尚未入規格；是否新增/修訂（INS-02 欄位、INS-04）待 PO 決定。
