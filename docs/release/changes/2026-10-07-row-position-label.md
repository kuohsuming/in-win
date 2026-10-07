---
date: 2026-10-07
type: changed
scope: app, ui, spec, installer
requirements: EDT-05, DSC-17, EDT-01, DEF-01
---

# 識別碼 key 改為位置標籤（第 1～10 排）

- PO 決定：設定畫面的「識別碼 key」改為「位置」下拉選單「第 1 排」～「第 10 排」，內部存為 `row-1`～`row-10`；每排一台，佔用的排停用並標示佔用者；第一次設為 DL-EN1 時預設最小的空排。
- 主畫面順序改依排號（沒有設備的排號略過）；設定頁的上移／下移只影響清單，主畫面不再跟著調整（移除 `order_saved`／`MainWindow.reorder`）。
- 設定頁清單名稱欄顯示「第 N 排・排名稱」；差異預覽顯示「位置：第 2 排 → 第 1 排」。
- 定義檔 schema 的 `key` 限 `row-1`～`row-10`；`installer/dl-en1.json`、`installer/config.toml` 的 `front`／`middle`／`rear` 改為 `row-1`／`row-2`／`row-3`。
- 尚未部署，未提供自動轉換：既有資料庫若有舊 key，啟動時會顯示設定錯誤並沿用上次檔案，請在設定頁選擇位置後儲存。開發機資料庫已手動轉換。
- 規格書新增 EDT-05（G1、A1～A4）；DSC-17 改寫（撤回 G1、A3，新增 G2）；3.7.1 `key` 欄位、範例、情境檔範例同步。PO 曾提出同一排允許兩台，隨即撤回。
