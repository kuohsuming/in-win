# 2026-11-17 允許誤差改為上限、下限分開（JDG-06 修訂）

設備設定探頭清單的「允許誤差」單一對稱值，改為「上限」「下限」兩個下拉選單。提案：`docs/pm/tolerance-limits/PROPOSAL.md`（PO 2026-11-17 簽核）。

## 判定（JDG-06）
- 每個探頭有上限、下限（mm）。判定沿用 JDG-01：下限 ≤ 讀值 ≤ 上限為合格，大於上限偏高、小於下限偏低。
- 選項各為 0、±0.1、±0.2、±0.5、±1、±2、±5、±10、±20、±50 mm。**上限預設 +0.2、下限預設 −0.2**（舊預設為對稱 ±0.5）。須下限 ≤ 上限（可同側）。
- 向下相容：舊設定的 `probes[].tolerance: t` 視為上限 +t、下限 −t；沒有任何誤差欄位的探頭以新預設 ±0.2 判定。

## 程式
- `bootp.py`：新增 `LIMIT_OPTIONS`；驗證 `upper`／`lower` 在選項內、下限 ≤ 上限、不與 `tolerance` 併用。
- `lan.py`：`probe_limits()` 取代 `probe_tolerance()`（含舊 tolerance 與新預設）；`standards()`、diff 改用上下限；`limit_text()`。
- `dl-en1.schema.json`：新增 `upper`／`lower`（保留 `tolerance` 供舊檔匯入）。
- `ui/settings_dialog.py`：「允許誤差」一欄拆成「上限」「下限」兩欄；下限 > 上限時檢查訊息擋下儲存；確認畫面分別列出。
- `ui/main_window.py`：3D 高度放大改以上下限的較大絕對值為基準（P3D-07）。

## 文件
- 規格書 JDG-06（修訂並簽核）、JDG-06-A3、JDG-06-G1、3.7.1（`upper`／`lower`／`tolerance`）、Schema。
- 操作說明書第 9 章、畫面設計規格、HTML 原型（上限／下限兩個選單）、截圖（settings-edit、settings-confirm）。

## 驗證
- 單元與畫面測試 326 項通過（新增 `test_bootp.test_limit_fields`、`test_ui.test_probe_limits_select`、`test_ui.test_lower_above_upper_blocks_save`；更新預設 ±0.2 的相關斷言）。
- 不需跑 SQL（沿用既有 JSON 與量測紀錄欄位）。
- 真機（mosa）：待網路恢復後確認。
