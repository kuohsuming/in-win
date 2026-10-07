---
date: 2026-10-07
type: added
scope: scripts
requirements: INS-07
---

# 開發機：開機自動啟動 App，資料改存系統 MySQL

- `scripts/install-autostart.sh`：建立 `~/.config/autostart/flatness.desktop`，登入後執行 `scripts/autostart.sh`；用 `remove` 參數可移除。
- `scripts/autostart.sh`：等系統 MySQL 就緒後，以真機模式啟動 App，輸出寫到 `.dev/autostart.log`。
- `scripts/run-dev.sh --system-db`：改用系統 MySQL（連線資訊 `.dev/db-system.env`），不啟動拋棄式 MySQL。拋棄式 MySQL 放在 `/tmp`，重開機會清空，不適合開機自動啟動。
- 2026-10-07：已在系統 MySQL 以 `sql/in-win.sql` 建立 `flatness` 資料庫與 App 帳號，並把開發資料庫的資料搬過去（lan_device 4、inspection 20、inspection_point 40、calibration 17 筆，皆一致）。
- 正式工站的開機自動登入與自動啟動（INS-07）仍由安裝包負責，尚未實作。
