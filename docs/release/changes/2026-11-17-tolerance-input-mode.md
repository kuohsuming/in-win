# 2026-11-17 上下限可切換輸入模式（JDG-06 rev2）

探頭清單右上新增勾選框「自己輸入上下限」（整台共用，預設不勾）：不勾為下拉選單（現況），勾選後上限、下限改為輸入框，可輸入 −50 ～ 50 mm（最細 0.1 mm）。提案 §8：`docs/pm/tolerance-limits/PROPOSAL.md`（PO 2026-11-17 簽核）。

## 程式
- `bootp.py`：`upper`／`lower` 驗證由「必須是選項值」放寬為「−50～50 mm、0.1 的倍數、下限 ≤ 上限」；新增 `LIMIT_MIN`／`LIMIT_MAX`。
- `dl-en1.schema.json`：`upper`／`lower` 由 enum 改為 number（−50～50）。
- `lan.py`：匯出 `LIMIT_MIN`／`LIMIT_MAX`。
- `ui/settings_dialog.py`：勾選框「自己輸入上下限」；上下限欄位依模式用下拉（`_limit_combo`，非選項值照原值保留）或輸入框（`_limit_spin`，QDoubleSpinBox 範圍 −50～50、步進 0.1、小數 1 位）；`_limit_value` 不分模式讀值；切換保留值、不算變更；read-only 停用勾選框。

## 文件
- 規格書 JDG-06（修訂並簽核）、JDG-06-A4、3.7.1（upper／lower 範圍）、Schema；提案 rev 2 §8。
- 操作說明書 9.2、畫面設計規格、HTML 原型（勾選框＋輸入框）、截圖（settings-edit）。

## 驗證
- 單元與畫面測試 327 項通過（新增 `test_ui.test_free_limit_input_mode`；更新 `test_bootp.test_limit_fields` 為範圍驗證）。
- 真機（mosa）：待網路恢復後確認。
