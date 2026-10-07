---
date: 2026-10-07
type: added
scope: app, ui, sql, spec
requirements: DSC-18, INS-05, EDT-02
---

# 設定頁「刪除」設備

- PO 提出：設定頁可刪除設備，讓清單不再顯示（例如模擬器或假資料產生的設備）；按下後先警告並請求確認。
- PO 決定：真的刪除、任何設備皆可刪、刪除後再送出請求時以新的不明設備出現。
- 清單按鍵新增「刪除」：確認框預設「取消」；確認後立即刪除，不需「儲存」。使用中／維修中／配發 IP 的設備同時更新定義檔與 BOOTP 對應（必要時重新啟動 dnsmasq），主畫面重建前先寫入畫面上的結果。其他設備尚未儲存的修改保留。唯一一台使用中不可刪除。
- 資料層：`tx.delete(macs)`（MemoryStore／MySQLStore）；`sync.apply(..., deleted=)`、`Backend.apply(..., deleted=)` 在同一交易內刪除，失敗全部還原。
- `sql/in-win.sql`：App 帳號增加 `GRANT DELETE ON flatness.lan_device`（量測紀錄與資料表仍不可刪）。**既有安裝需重新執行 `sql/in-win.sql`**（可重複執行）。
- 規格書新增 DSC-18（G1、A1～A6），INS-05、EDT-02、資料說明同步；畫面設計規格 5.10 清單按鍵改為提供刪除。
- 同日修訂：撤銷「唯一一台使用中不可刪除」，最後一台也可刪除（確認訊息加註警告）；DL-EN1 數量改為 0～8 台（`lan.validate`、`bootp.validate`、JSON Schema `minItems: 0`），0 台時主畫面顯示「尚未設定『DL-EN1 使用中』的設備」。
