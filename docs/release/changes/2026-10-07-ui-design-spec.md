---
date: 2026-10-07
type: added
scope: docs, spec
requirements: UI-01, UI-02, 5.3, EDT-01, DSC-02～DSC-16
---

# 納入畫面設計規格與 HTML 原型，並與需求規格書 3.10 對齊

- 新增 `docs/ui/screen-design-spec.md`（作業員畫面設計規格）與 `docs/ui/prototype/board-station.html`（可操作的 HTML 原型），附 5 張原型截圖。
- 「編輯 BOOTP 設備」改名「設備設定」，依已簽核的 3.10 改寫：五種狀態（不明設備／DL-EN1 使用中／DL-EN1 維修中／DL-EN1 已停用／其他設備）、資料庫為主檔（移除定義檔 `enabled`、`other_devices`）、所有設備皆記錄、刪除改為隱藏、替換、依範圍的預設 IP 與 ARP 佔用檢查、清單自動更新、匯入／還原／下載、儲存前先寫入未寫入的量測結果。
- 主畫面工具列新增系統狀態提示：BOOTP 服務停止、無法讀取資料庫、模擬模式。`warn` 色票改為使用中。
- 需求規格書：1.4 參考文件加入畫面設計規格與原型；UI-01、UI-02、5.3 改指向畫面設計規格；新增 DSC-15（DL-EN1 維修中，保留 IP）、DSC-16（MAC 只能經偵測或匯入取得）；EDT-01、DSC-14 移除手動輸入 MAC；「未分類」改稱「不明設備」、「非 DL-EN1」改稱「其他設備」（代碼不變），`status` 增加 `dl_en1_maint`。
