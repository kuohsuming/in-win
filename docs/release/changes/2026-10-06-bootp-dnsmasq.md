---
date: 2026-10-06
type: added
scope: installer, bootp
requirements: INS-04, DEF-02, DEF-03, DEF-10, UPL-07, 3.0.4 步驟 2～3
---

# BOOTP 服務（dnsmasq）安裝步驟與 MAC↔IP 對應檔產生

- `installer/setup-bootp.sh`：設定設備網卡固定 IP、安裝並設定 dnsmasq（只在設備網卡、關閉 DNS、只配發對應檔內的 MAC），開機自動啟動。
- `app/flatness/bootp.py`：驗證 DL-EN1 定義檔（3.7.1 規則，一次列出所有錯誤），產生 dnsmasq 主機對應檔（每台一行 MAC,IP,key）；套用時先備份（保留 20 份）、原子寫入，dnsmasq 重啟失敗自動還原。
- `installer/site.conf`、`installer/dl-en1.json`：現場參數與定義檔；目前只登錄 1 台 DL-EN1（00:01:FC:DE:3A:75 → 192.168.10.11）。
- 重複執行時保留現場的定義檔與對應檔，設定內容相同時不重啟 dnsmasq（3.0.8）。
