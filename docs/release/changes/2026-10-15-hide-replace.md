# 設備設定：暫時隱藏「替換…」區塊

- 日期：2026-10-15
- 依 PO 指示，設備設定頁的「替換…」按鈕與說明「DL-EN1 故障換新機時使用」暫時不顯示。
- 功能本身（DSC-14）保留未刪；要恢復時將 `app/flatness/ui/settings_dialog.py` 的 `SHOW_REPLACE` 改回 `True`。
