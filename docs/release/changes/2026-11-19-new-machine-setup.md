# 2026-11-19 新機安裝文件與腳本（空白 Ubuntu → App 可運行）

原本 repo 只有《快速安裝指南》（從「電腦已裝好 App」開始的設備／校準設定），缺少 **OS／環境層**（空白 Ubuntu 到 App 跑起來）的文件；系統 MySQL 與 kiosk 設定也沒有腳本（本站是手動做的）。本次補齊，讓下一台站台以「這份文件 + Claude」從空白 Ubuntu 一路設定完成。

## 新增
- `scripts/bootstrap-tools.sh`：**Phase 0 引導**（人手動、Claude 之前）。用 Google／Microsoft 官方 apt 來源裝 Chrome、VS Code、Claude 擴充（`anthropic.claude-code`，自帶 runtime，不需 Node/CLI），並 clone `~/in-win`。可用 `wget raw URL` 一行取得，不需先 clone。
- `docs/manual/新機安裝指南.md`：OS／環境層 runbook（含階段 0 引導）。涵蓋系統套件、clone+venv、網路（WAN／設備 LAN bridge，依 `site.conf`）、持久 MySQL、桌面/Dock/開機自動啟動、kiosk、重開機驗證；含本站實例值與疑難排解。接續《快速安裝指南》步驟 1。
- `scripts/setup-station-db.sh`：安裝/啟用系統 MySQL、匯入 `sql/in-win.sql`、設定 `flatness_app` 密碼、寫 `.dev/db-system.env`（600）；可重複執行。
- `scripts/setup-kiosk.sh`：GDM 自動登入、關鎖屏/螢幕保護、`idle-delay 0`、不自動睡眠、系統 dconf 預設、遮蔽 systemd 睡眠目標；可重複執行。

## 沿用既有
- 網路 bridge + BOOTP：`installer/setup-bootp.sh`（2026-11-19 起 `EQUIP_BRIDGE_PORTS` 支援多埠橋接）。
- 桌面捷徑/選單/自動啟動：`scripts/install-desktop.sh`（圖示為已隨 repo 帶入的 InWin logo）。

## 驗證
- 兩支新腳本 `bash -n` 通過；內含指令均為本站 2026-11-19 實作時逐步手動執行並驗證過的步驟。
- 文件流程對應本站重開機後實測結果（自動登入、br-lan、dnsmasq 綁 br-lan:67、系統 MySQL、App 自動啟動皆正常）。
- 未在既有站台重跑 `setup-station-db.sh`（會重設 DB 密碼、需重啟 App），避免干擾運行中機台。

## 審查修正（2026-11-19，交付工廠前複查；PO 決策後實作）
- **P0**：階段 1 加 **deadsnakes PPA** 後安裝 **python3.11**（PO 決定鎖定 3.11；22.04 預設無 3.11）。
- 階段 1 加入時區與 NTP 設定（`timedatectl`），確保量測時間戳正確。
- **App 崩潰自動重啟**：新增 `scripts/install-service.sh`，以 systemd 使用者服務（`Restart=always`、`WantedBy=graphical-session.target`）啟動 App，取代 install-desktop 的 autostart。**真機實測**：強殺 App 後約 3 秒自動拉起（NRestarts +1），GUI 正常、無畫面錯誤。runbook 階段 5 改用之。
- **關閉自動更新**：`setup-kiosk.sh` 加停用 `unattended-upgrades`，避免產線時間自動更新／重開機。
- `setup-station-db.sh` 改為冪等：`flatness_app` 已設定且可連線時保留現有密碼，不重設（避免打斷運行中的 App）；schema 仍可重匯入供升級。
- 新增 `scripts/verify-station.sh`（repo 版一鍵驗證，不需 sudo，含服務狀態；修正舊 `verify-boot.sh` 的 port 67 誤報）；runbook 階段 7 改用它。
- 工程人員密碼：PO 決定**維持固定 `1234`**（文件附如需更改的指令）。

## 備註
- `setup-kiosk.sh` 需在 `install-desktop.sh` 之後執行（後者會把閒置關螢幕設回 5 分鐘）。
- 需求規格書列作業系統為 Ubuntu 24.04；本站為 22.04，文件標示兩者皆適用，指令於 22.04 實測。
