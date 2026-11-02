# 2026-11-02 BOOTP 拒絕配發的修復與提示（DSC-21～DSC-23）

起因：mosa 新平台的 DL-EN1 先因設定尚未儲存而拿不到 IP（39 分），儲存後又被舊 DL-EN1 的永久租約佔住 192.168.10.11（22 分），畫面只顯示「偵測不到」。提案：`docs/pm/bootp-lease/PROPOSAL.md`（spectra-review 5 輪，`docs/reviews/bootp-lease/`）。

## 安裝包（DSC-21）
- `installer/steps/03-bootp.sh`：主設定加入 `leasefile-ro`，dnsmasq 不讀、不寫租約檔；加入時舊租約檔改名為 `dnsmasq.leases.flatness-old-<時間>`。
- 主設定有變更時，最後一步執行停止程式，App 約 2 秒後以新主設定自動重新啟動 dnsmasq，不必關閉 App；依結束碼記錄安裝日誌，不中斷安裝。
- **現有機器須由維護人員執行一次** `sudo ./installer/setup-bootp.sh`。

## App
- 新模組 `bootp_watch.py`：從 dnsmasq 的 BOOTP 行判斷拒絕配發（`address in use`、`no address available` 等）與恢復（配發成功、ARP、主畫面連上後 15 秒未再被拒、60 秒逾時清除）；App 的警告日誌只在狀態改變時記一筆（DSC-23）。
- 主畫面：被拒的使用中設備方塊顯示「拿不到 IP」、以設備異常計（連得上也一樣），頂端提示取代「偵測不到」；維修中顯示「拿不到 IP・維修中」，不進入異常橫幅；被拒期間暫停「IP 不符」（DSC-23，修訂 DSC-15、DSC-20、POS-05）。
- 設備設定：資訊列顯示「BOOTP：拒絕配發（原因），最近 時間」；探頭偵測失敗時說明「設定尚未儲存」（必要時加按 RST）或拒絕原因（修訂 PDT-01）。
- 設定 IP 時，曾使用此 IP 的其他設備（含已停用、不在線）與舊租約都會提示，不阻擋儲存（DSC-22，修訂 DSC-10、DSC-14）。
- `scripts/fake-dnsmasq.py`、`discovery.py` 範例改用實機 dnsmasq 2.90 的字串。

## 文件
- 規格書 DSC-21～DSC-23（PO 2026-11-02 核可）與連帶修訂、3.0.4 步驟 3、3.0.8、6.2 索引。
- 畫面設計規格、畫面與程式對照、操作說明書 10.1 與 11.4、快速安裝指南「常見狀況」、HTML 原型（「拿不到 IP」示範切換）。

## 驗證
- 單元與畫面測試 324 項通過（新增 `tests/test_bootp_watch.py`、主畫面與設定頁的拒絕配發、佔用者與舊租約提示、探頭偵測失敗說明）。
- 安裝包步驟以假的根目錄測試：舊租約檔改名、停止程式結束碼 0／1／3 各自的日誌、App 未執行時不中斷。
- 真機（mosa）：待維護人員執行 `sudo ./installer/setup-bootp.sh` 後確認 AC-3、AC-5。
