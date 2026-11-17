# 2026-11-18 判定前先做最佳點修正（JDG-07 新增、JDG-01 修訂）

每片的 pass/fail 判定改為**相對整片最佳點**：判定前先在整片所有有效量測點中找出最靠近標準 0 的點（最佳點），把每一點減掉最佳點讀值得到修正值，再以修正值比對上下限。提案：`docs/pm/best-point-correction/PROPOSAL.md`（PO 2026-11-17 簽核）。

## 判定（JDG-07、JDG-01）
- **最佳點**：整片所有有效量測點中讀值絕對值最小者；其讀值（含正負號）為 `best`。並列（絕對值相同）時取較小、較負者，使結果可重現。
- **修正值 ＝ 讀值 − best**（最佳點修正後為 0）。設備異常、未校準、拿不到 IP、維修中、未啟用的點不參與最佳點計算；全片無有效點時整片為設備異常（JDG-04）。
- 判定沿用 JDG-01，但比的對象由讀值改為修正值：下限 ≤ 修正值 ≤ 上限為合格，大於上限偏高、小於下限偏低。整片判定（JDG-02／04）、上下限設定（JDG-06）不變。
- 效果：整片共同的墊高／墊低不再造成整片不合格；判的是相對最平那一點的平整度。

## 顯示與紀錄（方案 A）
- 主畫面方塊、3D、Excel **仍顯示原始讀值**；只有判定與「超出上限／低於下限」的差距用修正值。
- 量測紀錄 `measured_value` 維持原始讀值；本機暫存 JSON 另記該片最佳點讀值 `best_offset` 供回溯。**DB 不加欄位**（App 帳號無 DDL 權限；`best_offset` 可由各點 `measured_value` 推回）。

## 程式
- `measure.py`：新增 `best_offset(values)`（取 `|v|` 最小、並列取較小）與 `correct(value, best)`；`DemoStation.read` 的 fail 模式改為讓缺陷點相對其餘點的最佳點明確超標（與新判定一致）。
- `ui/main_window.py`：`show_result` 改為兩階段——先掃全片有效讀值求 `best`，再逐點以修正值 `judge`；不合格註記用修正值；方塊仍顯示原始讀值；`PointResult` 新增 `best_offset`。
- `results.py`：`to_record` 明細新增 `best_offset`（僅暫存 JSON；DB INSERT 不變）。

## 文件
- 規格書 JDG-07（新增並簽核）、JDG-01（修訂）、JDG-07-G1／G2／A1～A3。
- 操作說明書第 9.1 章（最佳點修正）。

## 驗證
- 單元與畫面測試通過（新增 `tests/test_measure.py` 8 項、`test_ui.test_best_point_correction_judges_relative`；修正 `DemoStation` fail 模式後 `test_demo_station`、3D 與橫幅測試照常）。
- 不需跑 SQL（沿用既有 JSON 與量測紀錄欄位）。
- 真機（mosa）：待 eno2 網路恢復後確認。
