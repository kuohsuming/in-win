---
date: 2026-10-07
type: changed
scope: app, ui, spec, scripts
requirements: UI-10
---

# 預設全螢幕；設備設定佔滿主畫面

- PO 決定：App 預設全螢幕（`--fullscreen` 保留相容，新增 `--windowed` 供開發用）；`scripts/run-dev.sh` 也預設全螢幕。
- 設備設定的編輯與確認儲存步驟佔滿主畫面，主畫面改變大小時跟著調整；密碼步驟仍為置中的小視窗（建議值）。
- 規格書新增 UI-10（G1、A1、A2）；畫面設計規格 5.10 容器尺寸同步。
