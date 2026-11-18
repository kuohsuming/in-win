# 2026-11-18 上下限固定「自己輸入」、勾選框鎖定（JDG-06 rev3）

設備設定探頭清單的「**自己輸入上下限**」勾選框改為**預設打勾且 disabled（鎖定、不可切換）**；上限、下限一律為輸入框（−50～50 mm、最細 0.1 mm），不再保留下拉選單模式。2026-11-18 PO 要求。

## 行為
- 勾選框固定打勾、灰色不可點；只作「上下限為輸入框」的說明用。
- 每個探頭的上限、下限直接在輸入框填 −50～50 mm（超出自動夾、更細位數四捨五入）；預設上限 +0.2、下限 −0.2，須下限 ≤ 上限。判定、儲存、確認畫面與資料欄位（`probes[].upper`／`lower`）不變。

## 程式
- `ui/settings_dialog.py`：`free_limits` 預設 `True`；`chk_free_limits` 建立時 `setChecked(True)`＋`setEnabled(False)`，`_render_detail` 一律 `setEnabled(False)`。`_limit_widget` 因 `free_limits` 恆為 True 而一律產生輸入框（`_limit_spin`）；下拉（`_limit_combo`）保留但不再於 UI 出現。

## 文件／網站
- 規格書 JDG-06（Statement 改為輸入框、勾選框固定鎖定；JDG-06-A4 改述；資料範圍移除「下拉選項子集」註記）＋ 2026-11-18 簽核敘述。
- 操作說明書 9.2（上下限永遠輸入框、勾選框固定鎖定）、7.2 右欄面板說明該列。
- 網站原型 `board-station.html`：`freeLimits` 恆 true、`#freeLim` 加 `checked disabled`、移除切換 handler；同步 Azure SWA 部署檔 `Downloads/`。
- 重新產生設定頁截圖（settings-detail／edit／confirm／scan 等）與操作說明書 PDF。

## 驗證
- `test_ui`：`test_probe_limits_select`、`test_free_limit_locked_on`（原 `test_free_limit_input_mode`）、`test_lower_above_upper_blocks_save` 改以輸入框 API；新增「預設勾且 disabled」斷言。
- `manual-shots.py` 的上下限設定改用 `setValue`。
