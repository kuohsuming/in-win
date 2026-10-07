---
date: 2026-10-07
type: added
scope: app, installer, spec
requirements: DAT-02, DAT-03, DAT-04, DAT-05, DAT-06
---

# 量測結果寫入 MySQL

- 按「下一片」（或關閉程式、開啟設備設定前）時，畫面上的結果寫入 `inspection`（編號、工站、量測時間、寫入時間、PASS／FAIL／ERROR、重讀次數）與 `inspection_point`（每個已安裝探頭 1 筆：當時的排名稱與位置名稱、測量值、標準值與上下限、OK／HIGH／LOW／ERROR、DL-EN1 原始回傳、異常原因、DL-EN1 MAC）。
- 先寫入本機暫存 `/var/lib/flatness/buffer/<編號>.json`，再由背景執行緒寫入資料庫，成功後刪除；畫面不等待資料庫。
- 資料庫無法寫入時照常量測，頂端顯示「資料庫無法寫入，待同步 N 筆」，每 5 秒重試，恢復後自動補寫；App 結束時最多等 3 秒，其餘留在暫存，下次啟動補寫；補寫時不重複寫入同一編號。
- 寫入成功時提示「編號 … 已寫入資料庫」。示範模式（`--demo`）不寫入資料庫。
- 安裝包建立 `/var/lib/flatness/buffer`（App 帳號）；開發機 `scripts/run-dev.sh` 使用 `.dev/buffer`。
- 新增測試：欄位對應、寫入後刪除暫存、資料庫中斷時暫存與補寫、不重複寫入、結束時未寫完於下次啟動補寫、實際 MySQL 寫入與讀回。
