---
date: 2026-10-06
type: added
scope: database
requirements: INS-05, DAT-02, DAT-03, DAT-04, DEF-08, DEF-09, SIM-15, 5.2
---

# 新增資料庫建立腳本 `sql/in-win.sql`

- 建立 `flatness`（正式）與 `flatness_sim`（模擬模式，SIM-15）資料庫，utf8mb4。
- 建立 `inspection`（主檔）與 `inspection_point`（明細）資料表；明細以 `device_key` + `probe_id` 識別量測點，並保存當時的名稱、標準值與 DL-EN1 原始回傳字串。
- 建立 App 帳號 `flatness_app@localhost`，只有 SELECT、INSERT、UPDATE 權限，密碼由 MySQL 隨機產生。
- 可重複執行：已存在的資料庫、帳號、資料表皆略過，不變更資料。

已知缺口：欄位依需求規格書推導，待「功能規格：資料寫入規則與資料表設計」納入後逐欄核對。
