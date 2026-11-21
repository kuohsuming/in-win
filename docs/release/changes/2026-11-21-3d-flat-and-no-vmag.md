# 2026-11-21 3D 繪圖定版：取消曲線/曲面實驗、移除「垂直放大 5 倍」字樣（App／PDF／網站／規格同步）

2026-11-21 PO 對 3D 繪圖的兩項決定，App／PDF／模擬網頁／Azure SWA／規格全部對齊同一畫面：

1. **取消曲線/變形曲面實驗**：先前在模擬網頁試做的「前緣剖面曲線 → 四周起伏 → 變形曲面＋前緣虛線陰影」全部取消，3D 回到**平面俯視 jet 熱力圖**（直邊、平滑上色、探點在平面上）。這些實驗只做在網頁，App `renderer.py` 全程未動，無需回滾。
2. **移除抬頭「垂直放大 5 倍」字樣**：俯視熱力圖本就沒有垂直放大，該字樣為舊立體版殘留，抬頭首列改為只顯示「寬 × 長 × 厚 mm」。

## 變更
- `app/flatness/plate3d/renderer.py`：抬頭首列移除「　垂直放大 5 倍」，註解同步。
- `docs/ui/prototype/board-station.html`＋ `Downloads/board-station.html`、`Downloads/index.html`（Azure SWA）：3D 還原平面熱力圖、抬頭移除字樣（已於前一次提交 `6cf230d`）。
- `docs/manual/操作說明書.md`：3D 抬頭說明移除「垂直放大倍率」；重產 `images/plate3d.png`（平面熱力圖、無字樣）與 `操作說明書.pdf`。
- `docs/ui/screen-design-spec.md` 5.11：抬頭移除字樣並註 2026-11-21 PO 修訂。
- `Downloads/表面平整檢查系統_需求規格書.md` P3D-06、P3D-07：移除「垂直放大 5 倍」顯示需求，P3D-07 加 2026-11-21 PO 修訂註。

## 保留（與本次無關、不動）
- `probeXY`／`config.probe_positions` 的 POS-13「沿邊緣平均排列」。
- 判定、紀錄、Excel、資料庫一律原始讀值。

## 驗證
- `tests/test_plate3d_render.py`、`test_plate3d_config.py` 全通過（14 passed）。
- 重產 `plate3d.png` 抬頭為「寬 600 × 長 1000 × 厚 5 mm」、無「垂直放大」；PDF 內文 `垂直放大` = 0。
- 模擬網頁／SWA 線上 3D 為平面熱力圖、無字樣（前一次已部署驗證）。
- 歷史 changeset `2026-11-18-best-point-correction.md` 保留原文（當時確有該字樣，為歷史紀錄）。
