---
target: docs/pm/bootp-lease/PROPOSAL.md
target_slug: bootp-lease-proposal
total_rounds: 5
last_round_date: 2026-11-02
last_verdict: ship-as-is
schema_version: enhanced-v1
contract_version: spectra-contract-v1
---

# Spectra-Review 彙總：bootp-lease-proposal

PO 指示：「repeat spectra-review & fix steps until no blocker no concern, max round is 5」。每輪由獨立的審查代理執行，作者依結果修正。第 5 輪剩 1 個 CONCERN，已達輪數上限，由作者直接修正於 rev 6，未再審查。

## Cumulative Findings Tally

| Round | Date | 審查版本 | BLOCKER | CONCERN | NIT | STRENGTH | Verdict |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | 2026-11-02 | rev 1（cce9959） | 2 | 6 | 4 | 4 | fix-blockers |
| 2 | 2026-11-02 | rev 2（1430b54） | 0 | 7 | 6 | 4 | ship-as-is |
| 3 | 2026-11-02 | rev 3（d54a0eb） | 0 | 2 | 5 | 4 | ship-as-is |
| 4 | 2026-11-02 | rev 4（d91045e） | 0 | 1 | 5 | 4 | ship-as-is |
| 5 | 2026-11-02 | rev 5（9619d45） | 0 | 1 | 2 | 4 | ship-as-is |
| **Total** | | | **2** | **17** | **22** | — | — |

## Issue Status Matrix

| Round | ID | Tier | Title | Status |
|:---:|:---:|:---:|:---|:---:|
| 1 | B1 | 🔴 | 重跑 setup-bootp.sh 不會重新啟動 App 的 dnsmasq | ✅ fixed（rev 2 §3.1 安裝包最後一步執行停止程式） |
| 1 | B2 | 🔴 | 事件時間線錯置；DSC-23 混淆「未儲存」與「被佔用」 | ✅ fixed（rev 2 §1 依日誌重寫、DSC-23 依原因分開） |
| 1 | C1～C6 | 🟡 | 顯示優先序、日誌筆數驗收、DSC-22 重疊、修訂清單、舊租約檔、判定規則 | ✅ fixed（rev 2；C1 殘留轉 R2-C6，C6 殘留轉 R2-C4／C7） |
| 1 | N1～N4 | 🟢 | AC-1 秒數、`--test` 範圍、DSC-22 範例、安裝後檢查位置 | ✅ fixed（rev 2） |
| 2 | C1 | 🟡 | 停止程式呼叫位置未定，新安裝會中止 | ✅ fixed（rev 3） |
| 2 | C2 | 🟡 | DSC-22 ② 第二條件與改名互相抵消 | ✅ fixed（rev 3 刪除該條件） |
| 2 | C3 | 🟡 | 主畫面「未配發」誤寫「設定尚未儲存」 | ✅ fixed（rev 3） |
| 2 | C4 | 🟡 | DHCP 行分類錯誤 | ✅ fixed（rev 3 只看 BOOTP） |
| 2 | C5 | 🟡 | 探頭偵測「尚未儲存」條件不精確 | ✅ fixed（rev 3～5） |
| 2 | C6 | 🟡 | 與 POS-05 衝突 | ✅ fixed（rev 3 列入修訂、取代規則） |
| 2 | C7 | 🟡 | 拒絕狀態沒有逾時 | ✅ fixed（rev 3 60 秒逾時） |
| 2 | N1～N6 | 🟢 | 異常結束日誌、改名覆蓋、升級說明、無效檢查、最後出現時間、索引 | ✅ fixed（rev 3） |
| 3 | C1 | 🟡 | 文件影響清單漏列畫面設計規格與原型 | ✅ fixed（rev 4～5） |
| 3 | C2 | 🟡 | RST 提示依已儲存設定判斷 | ✅ fixed（rev 4～5） |
| 3 | N1～N5 | 🟢 | 連上即恢復、維修中逾時、改名後寫入、安裝日誌、M1 殘字 | ✅ fixed（rev 4～5） |
| 4 | C1 | 🟡 | 「被拒優先」蓋掉「尚未儲存」 | ✅ fixed（rev 5 依畫面 IP 是否等於已儲存 IP 判斷） |
| 4 | N1～N5 | 🟢 | 60 秒 BOOTP 條件、15 秒、逾時清除日誌、結束碼、文件項目 | ✅ fixed（rev 5） |
| 5 | C1 | 🟡 | 「不判定」可能讓被拒設備退出整片判定 | ✅ fixed（rev 6 以設備異常計、AC-12；未再審查） |
| 5 | N1 | 🟢 | 最近 BOOTP 請求時間的資料來源 | ✅ fixed（rev 6 backend 自行記錄） |
| 5 | N2 | 🟢 | 顯示規則放在恢復條件清單中 | ✅ fixed（rev 6 移至主畫面） |

## Quality Health Score

- total_findings: 41（不含 STRENGTH）
- fixed: 41
- pending / no_decision / rejected / deferred: 0
- fix_rate: 100%
- po_overrides: 0
- convergence_signal: ✅（有效成本 27.0 → 18.1 → 5.95 → 3.05 → 1.55）

## Hotspot History

| Round | Hotspot | 等級 | 是否解 |
|:---:|:---|:---:|:---:|
| 1 | B1 安裝包不讓新設定生效 | 🔥🔥 | ✅ |
| 1 | B2 時間線與原因混淆 | 🔥 | ✅ |

## 實作後確認（各輪建議的 V7 檢查項目）

- AC-6 ①～④ 的探頭偵測提示。
- AC-7：IP 衝突且 B 重新開機時的 WARNING 筆數。
- AC-11、AC-12：同一台只出現一條「拿不到 IP」；佔用者在線時整片為設備異常。
- 逾時清除後，維修中設備回到「維修中」；DSC-20 不誤用舊的 `seen_ip`。
