---
date: 2026-10-07
type: fixed
scope: app
requirements: UPL, EXP-02, UI-10
---

# 修正：開啟選檔視窗後 App 卡住

- 設備設定的「匯入…」「下載目前設定」，以及取出測試數據的「變更資料夾」，原本用系統（GTK）選檔視窗。App 全螢幕時這個視窗被擋在後面，看不到也關不掉，整個 App 就像卡住。2026-10-07 以 gdb 確認 App 停在 `gtk_dialog_run`。
- 改用 App 內建的選檔視窗（`widgets.pick_path`），並固定在最上層。
