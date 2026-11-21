# 2026-11-21 首頁顯示調整：取消最佳點標記、大字改相對高度、刻度校正值放大（JDG-07 顯示修訂）

2026-11-21 PO 三項首頁顯示要求，**只動畫面顯示，不改判定、紀錄、3D、Excel 與資料庫**：

1. **取消「最佳點」標記**：方塊不再標藍色「最佳點」標籤。
2. **首頁大字測量值改為整片相對高度**：`測量值 = max(本次所有有效讀值) − 該點讀值`，與 3D 繪圖的相對高度**同定義**（讀值最大的那片顯示 0、其餘為正）。
3. **刻度校正值字體放大**：三角上方的校正值由 12px 放大為 16px，刻度條由 48px 加高為 56px、版面下移避免裁切。

## 不變（重要）
- **判定**仍用 JDG-07 最佳點修正（修正值＝讀值 − 最佳點讀值，比對上下限）；刻度三角仍以修正值定位。
- **量測紀錄、3D、Excel、資料庫**的探測值一律為**原始探頭讀值**（`measured_value`）。相對高度、修正值都只在畫面顯示層計算，不回寫紀錄。

## 程式
- `ui/main_window.py`：移除 `ProbeTile` 的 `best_tag`／`is_best`／`set_best` 與 `show_result` 的標記；`show_result` 計 `hi = max(有效讀值)`，大字傳 `hi − r.value`（`scale_value` 仍為修正值、`PointResult.value` 仍為原始讀值）。`ScaleBar` 校正值字體 `val_px=max(12, round(16·k))`、刻度條 48→56px 並重排各列。

## 文件／網站／測試
- 規格書 JDG-07（顯示方式、JDG-07-G1／A3、2026-11-21 簽核敘述）；操作說明書 9.1；畫面設計規格 5.6。
- 網站原型 `board-station.html`（移除 besttag、大字改 max−讀值、刻度 cv 放大）＋同步 Azure SWA 部署檔 `Downloads/`。
- `test_ui.test_best_point_correction_judges_relative`：移除 is_best 斷言，改驗「大字＝max−讀值、紀錄＝原始讀值」。
- 重產主畫面截圖與操作說明書 PDF。
