---
date: 2026-10-07
type: changed
scope: app, installer, sql
requirements: DSC-01～DSC-16, DEF-01, DEF-03, DEF-10, DAT-06, INS-04, INS-05, UPL-06～UPL-08, EDT-02, EDT-03
---

# 設備網路探索與設備分類：資料庫為主檔、dnsmasq 由 App 啟動

- `sql/in-win.sql`：新增資料表 `lan_device`（每個 MAC 一筆，5 種狀態，DL-EN1 設定存為 JSON）；`inspection_point` 新增 `device_mac`（舊表自動補欄位，可重複執行）。
- App 啟動時依資料庫產生 `dl-en1.json` 與 BOOTP 主機對應；內容相同不改寫；資料庫無法連線或資料有錯時沿用現有檔案並在畫面說明原因（`sync.py`，DSC-06、DSC-11）。
- dnsmasq 改為 App 的子程序：先產生主機對應再啟動，異常結束 2 秒後自動重新啟動，App 結束時停止（`dnsmasq.py`，DSC-07）。App 收到 SIGTERM／SIGHUP（登出、關機）時正常結束。
- 探索：解析 dnsmasq 的 log-dhcp 輸出，每個 BOOTP／DHCP 請求加 1 次並記錄主機名稱與廠商識別；資料庫斷線時暫存於記憶體，恢復後補寫（`discovery.py`，DSC-01、DSC-05）。日誌格式依 dnsmasq 2.90 原始碼，**尚待以實機 DL-EN1 驗證**。
- 設備規則（`lan.py`）：五種狀態切換、預設 IP（DL-EN1 `.11～.99`、其他設備 `.100～.199`）、重複檢查會說明佔用者、替換、維修中、匯入、差異預覽。
- IP 佔用探測：ping 後讀鄰居表取得回應者 MAC，不需 root（`netinfo.py`，DSC-10）。
- 套用設定：同一個資料庫交易內寫入資料庫、產生兩個檔案、重新啟動 dnsmasq，任一步失敗全部還原（DSC-03、DSC-12、DSC-14）。
- 安裝步驟 3 改寫：遮蔽 `dnsmasq.service`、主設定改為 root 擁有的 `/etc/flatness/dnsmasq.conf`（`/etc/flatness` 加 sticky bit，App 無法替換）、sudoers 只允許固定參數的 dnsmasq 命令；移除舊版 `/etc/dnsmasq.d/flatness-dl-en1.conf`。
- 首次匯入：`python -m flatness.initdb`，資料庫沒有任何 DL-EN1 時才以定義檔匯入（DEF-10）。
- 移除：舊的「直接改寫定義檔、以 systemctl 重啟 dnsmasq」流程（`definition.apply`、`bootp.apply`、`bootp apply` 命令）。
- 開發工具：`scripts/dev-mysql.sh`（不需 sudo 的拋棄式 MySQL）、`scripts/fake-dnsmasq.py`（輸出示範請求）、`scripts/run-dev.sh` 改為使用兩者。
- 待確認：App 異常當機時，以 root 執行的 dnsmasq 可能殘留，下次啟動會因埠 67 被佔用而失敗；需在產線 PC 實測，必要時於 sudoers 增加只能停止該 dnsmasq 的命令（屬規格變更，待 PO 決定）。
