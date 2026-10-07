---
date: 2026-10-07
type: added
scope: app, installer, sql, spec
requirements: DSC-19, DSC-01, INS-04
---

# 以 ARP 位址偵測封包探索已有 IP 的設備

- 真機驗證：DL-EN1 取得 IP 後保存於本機，重新上電不送 BOOTP，只送 3 個 ARP 位址偵測封包，只看 BOOTP／DHCP 會漏掉它。
- 安裝包新增 root 擁有、不接受參數、只監聽設備網卡的 `/usr/local/sbin/flatness-arp-watch`（`installer/files/flatness-arp-watch`，安裝時填入 `EQUIP_IF`），sudoers 加入此程式（不帶參數）。已安裝的工站需重新執行 `sudo ./installer/setup-bootp.sh`。
- App 以 sudo 執行監聽程式為子程序（與 dnsmasq 同一套管理：結束時停止、異常結束 30 秒後重新啟動），只記錄位址偵測封包（探測：傳送端 IP 0.0.0.0；宣告：傳送端 IP 等於目標 IP），一般 ARP 查詢與回應、量測 PC 自己的 ARP 不記錄。
- `lan_device` 新增 `seen_ip`（實際使用 IP），`last_request` 加入 `ARP`；`sql/in-win.sql` 對舊資料表補欄位（可重複執行）。
- 設備設定：詳細資訊顯示「實際使用 IP」，與設定的 IP 不同時以警告色標示；清單中不配發 IP 的設備顯示「不配發・使用 x.x.x.x」。
- 開發機 `scripts/run-dev.sh` 假 dnsmasq 模式加 `--no-arp`；`--real` 模式檢查監聽程式已安裝。
- 規格書新增 DSC-19（待確認），3.10 資料表與 3.0.4 步驟 3 同步。
