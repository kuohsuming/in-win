---
date: 2026-10-07
type: added
scope: scripts
requirements: INS-07
---

# 開發機：桌面捷徑、App 圖示、開機自動啟動，資料改存系統 MySQL

- `scripts/install-desktop.sh`：建立三個捷徑，都執行 `scripts/launch.sh`，用 `remove` 參數可全部移除。
  - 桌面捷徑：點兩下啟動，已設為信任。
  - 應用程式清單：按 Super 搜尋「表面平整」，可以釘選到 Dock。
  - 開機自動啟動：`~/.config/autostart/flatness.desktop`。
- `scripts/launch.sh`：等系統 MySQL 就緒後，以真機模式啟動 App，輸出寫到 `.dev/autostart.log`。App 已在執行時不重複啟動，只顯示通知，避免誤點讓量測中的畫面重開。
- App 圖示：`app/flatness/ui/assets/app-icon.png`，由 In Win 標誌（`logo-source.png`，56×42）製成 256×256。工作列與 Dock 顯示此圖示（`setWindowIcon`、`setDesktopFileName("flatness")`）。
- `scripts/run-dev.sh --system-db`：改用系統 MySQL（連線資訊 `.dev/db-system.env`），不啟動拋棄式 MySQL。拋棄式 MySQL 放在 `/tmp`，重開機會清空，不適合開機自動啟動。
- 2026-10-07：已在系統 MySQL 以 `sql/in-win.sql` 建立 `flatness` 資料庫與 App 帳號，並把開發資料庫的資料搬過去（lan_device 4、inspection 20、inspection_point 40、calibration 17 筆，皆一致）。
- 正式工站的開機自動登入與自動啟動（INS-07）仍由安裝包負責，尚未實作。
- 螢幕與電源（2026-10-08，PO 要求「螢幕睡眠喚醒後直接登入」）：`install-desktop.sh` 設定閒置 5 分鐘關閉螢幕、喚醒不鎖定、電腦不自動睡眠（睡眠會中斷 DL-EN1 連線）；`remove` 時恢復系統預設。對應 INS-07「關閉螢幕鎖定」。
