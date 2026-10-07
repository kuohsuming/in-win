---
date: 2026-10-07
type: added
scope: app, sql, config, spec, docs
requirements: CAL-01, CAL-02, CAL-03, CAL-04, CAL-05, CAL-06, CAL-07, CAL-08, CAL-09, NFR-11
---

# 探頭校準（軟體歸零）

- 設備設定的探頭表新增「校準」欄與每列「校準」鍵，一次校準一個探頭；只有已儲存、沒有未儲存變更的「DL-EN1 使用中」設備可校準。
- 流程：提示放好標準件 → 以 `MS` 讀取 20 次（間隔 50 毫秒，原始值）→ 標準差大於容許值一半判「讀值不穩定」→ 偏移量 ＝ 平均 → 再讀 5 次驗證（平均在 ±容許值內、每次在 ±max(3σ, 解析度) 內）→ 顯示結果，按「採用」立即寫入資料庫與定義檔。可取消；未通過或取消不改變設定。
- 不對放大器送任何寫入命令（NFR-11）；取樣與量測共用同一條 DL-EN1 連線（DL-EN1 同一時間只接受 1 條）。
- 量測：顯示值 ＝ 原始值 − 偏移量；未校準的探頭偵測與量測時為設備異常「未校準」，不判合格或不合格。
- 偏移量存於 `lan_device.dl_en1_config.probes[].zero_offset`／`zeroed_at`（定義檔 3.7.1 新增欄位）；刪除中間探頭使 ID 遞補、DL-EN1 替換時清除。
- 資料庫：新增 `calibration` 紀錄表（每次校準，含取消與失敗）；`inspection_point` 新增 `zero_offset`。`sql/in-win.sql` 可重複執行。
- `config.toml`：新增 `[calibration]`（samples、interval_ms、verify、tolerance = 0.002）；允收標準改為標準值 0、上下限 ±0.050（假設值，TBD-01）。**既有工站升級後所有探頭須先校準才能量測。**
- 規格書 3.11 CAL-01～CAL-09（已簽核），3.7.1、TBD-01、需求追溯同步；畫面設計規格同步。
