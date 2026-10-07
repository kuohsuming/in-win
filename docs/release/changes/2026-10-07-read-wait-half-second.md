---
date: 2026-10-07
type: changed
scope: app, config, spec, docs
requirements: MEA-03, MEA-07
---

# 按「下一片」「重讀」後 0.5 秒開始讀取

- 量測前的等待從 5 秒改成 0.5 秒（`config.toml` 的 `countdown_seconds = 0.5`，可為小數）。
- 等待不到 1 秒時不顯示倒數數字，橫幅直接顯示「讀取中／請勿移動表面」；設為 1 秒以上時仍逐秒倒數。等待與讀取期間按鍵照舊停用。
- **既有工站**：`/etc/flatness/config.toml` 若仍寫 `countdown_seconds = 5`，須改為 0.5 才會生效。
- 規格書 MEA-03、MEA-07、TBD-02 修訂，新增 MEA-G1、MEA-A1（已簽核）；畫面設計規格同步。
