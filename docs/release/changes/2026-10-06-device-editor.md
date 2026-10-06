---
date: 2026-10-06
type: added
scope: app, spec, installer
requirements: EDT-01～EDT-03（新增）, DEF-02, DEF-04, UPL-04～UPL-09, UPL-12
---

# App 第一版：設備設定（DL-EN1 清單維護）

- 新增 PySide6 App（`python -m flatness`）：主畫面依定義檔顯示每排與探頭位置；工具列「設備設定」可新增、刪除、修改、排序 DL-EN1 與探頭。
- 套用：驗證（逐欄＋跨欄位，並以正式 JSON Schema 把關，一次列出所有錯誤並標示排名稱與欄位）→ 差異預覽（MAC／IP 變更紅字、需重新上電清單、將移除的量測點）→ 確認 → 備份並原子覆寫 `dl-en1.json` → 重寫 dnsmasq BOOTP 主機對應並重啟 dnsmasq；任一步失敗即還原兩個檔案。
- 需求規格書新增 3.8.3「在畫面上編輯 DL-EN1 清單」EDT-01～EDT-03。
- 安裝包：`/etc/flatness` 目錄改為 App 帳號群組可寫（原子覆寫與備份所需）。
- 新增 `requirements.txt`（3.0.5 鎖定版本）、`requirements-dev.txt`、`scripts/run-dev.sh`。

尚未實作：工程人員密碼（UPL-01）、量測中停用（UPL-02）、套用後自動偵測設備（UPL-08 最後一步，待 DEV 完成）。
