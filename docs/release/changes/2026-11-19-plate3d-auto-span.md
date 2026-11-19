# 2026-11-19 3D 探點依實配排/點自動平均分布、首排首點移到左下角（POS-13 修訂）

3D 熱力圖的探點位置原本依「板子版面格點」（預設 5×5）計算：`x=(點−1)/(格點−1)`、`y=(排−1)/(格排−1)`。當版面未設定（預設 5×5）但實際只配了較少的排/點（例 3 排×2 點）時，點只落在板子左下 1/4、擠成一團，未填滿板面；且 `排1` 對應 `y=0`，在俯視圖（`y=0` 在上緣）落在**左上角**，與作業認知「第一排第一點在左下角」相反。

## 行為（修訂）
- **自動平均分布**：取所有「已設定位置」探頭的排號、點號之**最小～最大值**當版面範圍，首尾落板緣、其餘等分，讓設定好的探點自動鋪滿整片板（不需另外設版面格點）。
- **首排首點在左下角**：點號由左而右（首點左緣、末點右緣）；排號由下而上（首排下緣、末排上緣，配合 renderer 俯視圖 `y=0` 在上緣）。
- `grid` 參數保留以相容呼叫端，但**不再決定間距**。

## 程式
- `app/flatness/plate3d/config.py`：`probe_positions` 改為先蒐集已置位探頭的 `(排,點)`，以 `(k−kmin)/(kmax−kmin)`、`(rmax−r)/(rmax−rmin)` 計算 `x,y`（單排/單點時置中 0.5）。
- 影響範圍僅 3D 繪圖取位（`main_window.plate_snapshot`、`measure.DemoStation.read` 的示範平面、`plate3d.demo`）；主畫面版面、匯出、判定不受影響。

## 驗證
- `tests/test_plate3d_config.py`：`test_corners`、`test_device_split_across_rows`、`test_plate_size` 預期值改為新座標；`test_grid` 改為 `test_auto_span_ignores_grid`（驗證間距與傳入 grid 無關）。
- `tests/test_ui.py::test_3d_button_states_and_snapshot`：第 1 排第 1 點由 `(0,0)` 改為左下角 `(0,600)`。
- `tests/test_plate3d_render.py`、`test_measure.py`、`test_demo_station.py` 照常通過（點位 x 不變、y 上下翻轉，無重疊、數量不變）。
- 全部相關測試通過（offscreen）。
- **真機驗證：通過（2026-11-19）** —— 探點依實配排/點自動平均鋪滿板面、第一排第一點在左下角。

## 待辦（規格書，未改）
- 需求規格書 POS-13 原文述「依版面格點、首尾落板緣」，本次改為「依實配排/點自動平均、首排首點左下角」。因本機規格尚未固定，暫不改規格書；待 PO 確認後補 POS-13（並視需要調整 P3D 相關 golden/anti 與文件截圖）。
