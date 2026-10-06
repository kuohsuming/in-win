---
date: 2026-10-07
type: changed
scope: app, ui
requirements: UI-01～UI-08, DEV-01～DEV-08, MEA-01～MEA-06, JDG-01～JDG-05, DEF-04, DEF-09, UPL-01～UPL-12, EDT-01～EDT-03, DSC-02～DSC-16, EXP-01
---

# 主畫面與設備設定依畫面設計規格重寫

- 主畫面（`ui/main_window.py`）：依設計規格 5.1～5.9 實作頂端工具列（含 BOOTP 服務停止、無法讀取資料庫、模擬模式提示）、編號列、8 種狀態的結果橫幅、排與探頭方塊、刻度條、淡化規則；倒數、讀取、偵測在背景執行，畫面不凍結；設備異常每 10 秒自動重新偵測。
- 設備設定（`ui/settings_dialog.py`，取代舊的 `device_editor.py`）：密碼 → 偵測到的設備清單 ＋ 設備內容兩欄式編輯 → 確認儲存。五種設備類型、清單自動更新、隱藏、上移／下移、替換、IP 預設值與 ARP 探測、即時檢查、匯入／從備份還原／下載目前設定、差異預覽與影響。
- 取出測試數據對話框（5.8）。
- 共用：色票與 QSS（`ui/theme.py`）、SVG 圖示（`ui/icons.py`）、提示訊息、遮罩、指示點（`ui/widgets.py`）；隨附數字字型 Barlow Semi Condensed（SIL OFL）。
- 設定檔範本 `installer/config.toml`：允收標準（假設值，TBD-01）、倒數秒數、預設 IP 範圍、工程人員密碼的 SHA-256。開發機密碼為 `1234`。
- 量測來源目前為示範（`measure.DemoStation`，隨機數值），結果只存在記憶體並提示「示範模式：未寫入資料庫」；DL-EN1 連線、資料庫寫入與 Excel 匯出為下一步。
- 與設計規格不同之處（見 `docs/ui/screens-device-settings.md` §6）：儲存失敗時留在確認頁；量測後設備異常排除時可重讀或下一片；資料庫斷線時設備設定唯讀；只有排與探頭區捲動。
- 文件：`docs/ui/screens-device-settings.md` 改為描述新畫面，以新截圖取代舊版截圖。
