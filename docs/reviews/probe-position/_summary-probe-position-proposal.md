---
target: docs/pm/probe-position/PROPOSAL.md
target_slug: probe-position-proposal
total_rounds: 2
last_round_date: 2026-10-15
last_verdict: ship-as-is
schema_version: enhanced-v1
contract_version: spectra-contract-v1
---

# Spectra-Review 彙總：probe-position-proposal

## Cumulative Findings Tally

| Round | Date | BLOCKER | CONCERN | NIT | STRENGTH | Verdict |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | 2026-10-15 | 3 | 8 | 8 | 6 | fix-blockers |
| 2 | 2026-10-15 | 0 | 4 | 9 | 6 | ship-as-is |
| **Total** | | **3** | **12** | **17** | — | — |

## Issue Status Matrix

| Round | ID | Tier | Title | severity_score | fix_roi | Status | PO 決策 |
|:---:|:---:|:---:|:---|:---:|:---:|:---:|:---|
| 1 | B1 | 🔴 | 位置不可重複的檢查放錯層 | 5.6 | 5.6 | ✅ fixed（rev 2 §5.1 兩層檢查） | PO 指示全部修正 |
| 1 | B2 | 🔴 | description 必填與自動帶入條件矛盾 | 5.4 | 5.4 | ✅ fixed（rev 2 §5.3；POS-09 同步） | PO 指示全部修正 |
| 1 | B3 | 🔴 | 只改名稱無法儲存、交易位置錯 | 5.4 | 3.6 | ✅ fixed（rev 2 §5.3 預覽與儲存、§6 sync.py） | PO 指示全部修正 |
| 1 | C1 | 🟡 | 狀態對應缺維修中方塊、優先序、頂端元件 | 3.6 | 2.4 | ✅ fixed（rev 2 §5.5；第 2 輪部分重開為 R2-C1，rev 3 修正） | PO 指示全部修正 |
| 1 | C2 | 🟡 | 名稱離線時重開遺失 | 2.0 | 2.0 | ✅ fixed（rev 2 §5.1 定義檔 position_names） | PO 指示全部修正 |
| 1 | C3 | 🟡 | 探頭層級稱呼未定義 | 3.5 | 3.5 | ✅ fixed（rev 2 §5.2 顯示名稱） | PO 指示全部修正 |
| 1 | C4 | 🟡 | 受影響條文與影響範圍不完整 | 4.0 | 2.7 | ✅ fixed（rev 2 §6） | PO 指示全部修正 |
| 1 | C5 | 🟡 | 未設定位置區列數計算矛盾 | 2.4 | 4.8 | ✅ fixed（rev 2 §5.4；規格書 POS-04 於 rev 3 同步，R2-C3） | PO 指示全部修正 |
| 1 | C6 | 🟡 | Excel 資料來源與缺漏點未定義 | 3.0 | 3.0 | ✅ fixed（rev 2 §5.1、§5.7、§10-1） | PO 指示全部修正 |
| 1 | C7 | 🟡 | 生命週期邊界情況未定義 | 3.0 | 3.0 | ✅ fixed（rev 2 §5.8） | PO 指示全部修正 |
| 1 | C8 | 🟡 | 排選單與選取順序規則缺漏 | 2.4 | 4.8 | ✅ fixed（rev 2 §5.3 選單規則） | PO 指示全部修正 |
| 1 | N1 | 🟢 | 「編號」同名 | 0.8 | — | ✅ fixed（改「第幾台」） | — |
| 1 | N2 | 🟢 | 「位置名稱」一詞兩用 | 0.6 | — | ✅ fixed（「排與點名稱區塊」） | — |
| 1 | N3 | 🟢 | 3D 拒絕訊息範例不一致 | 0.5 | — | ✅ fixed（POS-07 範例同步） | — |
| 1 | N4 | 🟢 | seq 無 CHECK、updated_at 無 ON UPDATE | 0.6 | — | ✅ fixed | — |
| 1 | N5 | 🟢 | Excel 欄名與 MAC 標題 | 0.6 | — | ✅ fixed（§5.7） | — |
| 1 | N6 | 🟢 | _entry_issues 比對式 | 0.5 | — | ✅ fixed（§5.1） | — |
| 1 | N7 | 🟢 | M3～M4 部署落差 | 0.7 | — | ✅ fixed（§8） | — |
| 1 | N8 | 🟢 | 未提 changeset | 0.4 | — | ✅ fixed（文件頭） | — |
| 2 | C1 | 🟡 | 狀態優先表缺整台設備異常、與 DSC-20 衝突 | — | — | ✅ fixed（rev 3 §5.5；POS-05 同步） | PO 指示全部修正 |
| 2 | C2 | 🟡 | render 取名稱來源未定義，立即儲存路徑會丟名稱 | — | — | ✅ fixed（rev 3 §5.1、§6、§7） | PO 指示全部修正 |
| 2 | C3 | 🟡 | 規格書 POS-04 與提案的 UI-11 計算不一致 | — | — | ✅ fixed（POS-04 改為以列計算） | PO 指示全部修正 |
| 2 | C4 | 🟡 | 依賴 §10 的段落未全部標示 | — | — | ✅ fixed（§0、§10 各項列出依賴段落） | PO 指示全部修正 |
| 2 | N1～N9 | 🟢 | 自動帶入邊界、Excel 當日位置、降版描述、grep 範圍、訊息格式、檔案對照、未設定區維修中、離線維修中、內嵌 Schema | — | — | ✅ fixed（rev 3） | — |

## Quality Health Score

- total_findings: 44
- fixed: 32
- pending: 0
- no_decision: 0
- rejected: 0
- deferred: 0
- valued: 12（STRENGTH）
- fix_rate: 100%
- close_rate: 100%
- avg_severity_open: 0
- po_overrides: 0
- convergence_signal: ⚠（第 2 輪 0 BLOCKER、4 CONCERN，待第 3 輪確認）

## Hotspot History

| Round | Hotspot | 等級 | 是否解 |
|:---:|:---|:---:|:---:|
| 1 | B1 位置不可重複檢查層級（POS-02 失守） | 🔥🔥 | ✅ rev 2 |
| 1 | C4 影響範圍（簽核範圍少於實際改動） | 🔥🔥 | ✅ rev 2 |
