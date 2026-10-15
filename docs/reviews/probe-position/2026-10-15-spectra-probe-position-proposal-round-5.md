---
target: docs/pm/probe-position/PROPOSAL.md
target_rev: rev 5
date: 2026-10-15
reviewer: spectra-review (v2.0)
iteration: 5
verdict: ship-as-is
schema_version: enhanced-v1
contract_version: spectra-contract-v1
mode: pm-skill-generic-doc
---

> 💡 spectra-review v2.0 active(Minerva 4 能力 framework)。若想用原版簡潔版,用 `/spectra-review --lite <target>`。

🎯 Mode: PM Skill — Generic doc (target: docs/pm/probe-position/PROPOSAL.md)

# Spectra-Review Round 5 — docs/pm/probe-position/PROPOSAL.md

本輪範圍與限制:
- 對象是 rev 5(第 5 輪,也是最後一輪)。先逐項驗證第 4 輪 9 個 finding 的修正,再對全文做一致性檢查,重點放在 rev 5 改動的段落:§5.5 IP 不符例外、§5.1 與 §5.3 的 `names=None` 規則、§5.2 變更清單文字、§6 文件與 plate3d 列,以及規格書 POS-02、POS-07、POS-09、P3D-03 與 changeset。
- 對照來源:規格書 3.13 POS-01～09(規格書:1074-1092)、P3D-03(規格書:1044)、DSC-20(規格書:946)、3.7.1(規格書:473-474)、需求對照表(規格書:1189);changeset `docs/release/changes/2026-10-15-probe-position-requirements.md`;程式 `app/flatness/`(含 ui/、plate3d/)、`tests/`、`sql/in-win.sql`、`installer/`。
- 第 3 節 PO 決定不重新討論;第 10 節 4 點仍延後給 PO,依賴段落清楚。
- SKILL 提到但本 repo 沒有的檔案略過。依呼叫者指示只寫 F1,不更新 F2 與 decision-log。

## § 1. Mental Lens

- **Claim → Evidence → Verdict**:rev 5 新增的程式描述逐句對照原始碼。「偵測不到時方塊不加 IP 不符(同現在 `set_down`)」對照 main_window.py:425-441 與 1233-1247;「`names=None` 沿用資料庫名稱寫定義檔」對照 sync.py:131-164(`render` 在交易前呼叫);變更清單文字對照 lan.py:625-651 與 tests/;P3D-03 訊息三處對照 plate3d/model.py:92、157、165。
- **Cross-section consistency**:§4 摘要 ↔ 規格書 POS-01～09;§5.2 兩種稱呼 ↔ §5.1、§5.3、§5.6、§5.7 範例;§5.5 ↔ DSC-20、POS-05、POS-G2;§6 程式清單 ↔ 實際呼叫者(`probe_positions`、`sync.apply`、`_entry_issues`)。
- **Anti-Bias**:F2 把第 4 輪全部標為 fixed,本輪不採信,逐項回到原文確認;同時提防「最後一輪要找點東西」的偏誤,新發現一律依 calibration 判級。
- **Understand-not-argue**:文件已收斂,rev 5 的修正都落在正確位置,規格書、changeset、提案三者一致。本輪只有實作時會自然發現的細節。

### 第 4 輪修正驗證

| R4 ID | 結果 | 依據 |
| --- | --- | --- |
| C1 | 成立 | PROPOSAL.md:245 寫明偵測不到(第 2 列)或整台設備異常(第 3 列)時方塊不加 IP 不符,頂端兩種提示都顯示,與 DSC-20(規格書:946)一致。附註「同現在」對第 3 列不精確,見 N1 |
| N1 | 成立 | 小標為「IP 不符・維修中」(PROPOSAL.md:245),與 main_window.py:439 相同 |
| N2 | 成立 | §6 文件列點名操作說明書「設為 DL-EN1」一節與畫面設計規格 5.10(PROPOSAL.md:315) |
| N3 | 成立 | POS-09 驗收改為新設為 DL-EN1 的設備(探頭 1～4),新安裝只驗排頭(規格書:1082)。3D 標籤一步缺前提,見 N7 |
| N4 | 成立 | P3D-03 加註(規格書:1044);changeset `requirements` 與第 6 點列入 P3D-03;§6 plate3d 列寫「model.py 中三處」(PROPOSAL.md:311),實際就是三處 |
| N5 | 成立 | POS-02 驗收為「已由 第 1 台 前排 右 使用」(規格書:1075) |
| N6 | 成立 | §5.2 寫明既有探頭變更行也改用設備稱呼,並列入 M2、M5(PROPOSAL.md:159)。只點名 test_ui.py,漏 test_lan.py,見 N4 |
| N7 | 成立 | §5.3 寫明只有名稱區塊有變更才傳 `names`(PROPOSAL.md:207);§5.1 寫明 `None` 為沿用資料庫名稱(121)。§8 沒有加「未執行 SQL 前改名稱會儲存失敗」,但交易會還原、不遺失資料,不另列 |
| N8 | 成立 | POS-07 標籤加上重名規則(規格書:1080),與 §5.2(PROPOSAL.md:157)一致 |

## § 2. 4-Tier Findings

### 🔴 BLOCKERS — 落地前必修

(none found)

### 🟡 CONCERNS — 應修

(none found)

### 🟢 NITS — 可選 polish

```yaml
- {tier: 🟢 NIT, id: N1, name: "§5.5「同現在 set_down 的做法」對整台設備異常不精確:現行程式整台設備異常時仍顯示 IP 不符", evidence: ["PROPOSAL.md:245", "app/flatness/ui/main_window.py:437", "app/flatness/ui/main_window.py:1240-1242"], assert: "現行 s.error 時呼叫 set_down(False, \"ng\"),seen_ip 存在就顯示「IP 不符」;只有偵測不到(down=True)才隱藏。提案對第 3 列是新行為,DSC-20 只規定偵測不到優先", pursue: "改為「偵測不到同現在;整台設備異常比照辦理(新行為)」,或第 3 列維持現行顯示", severity: {score: {value: 0.3, default: 0.3}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N2, name: "_entry_issues 對 row|point 一律輸出「須同時設定」訊息,若 bootp.validate 對同一台內的重複位置也回報 probes[i].row,會被誤標;§5.1「各台之間」也沒說同一台內重複由誰擋", evidence: ["PROPOSAL.md:139", "PROPOSAL.md:142", "app/flatness/lan.py:265-288", "app/flatness/initdb.py:35"], assert: "設定頁的同台重複已由 lan.validate 標示;initdb 只經過 bootp.validate,同台重複會漏掉", pursue: "bootp.validate 寫明檢查定義檔內全部探頭(含同一台);_entry_issues 只對「須同時設定」錯誤用固定訊息,重複位置的錯誤略過(比照 ipv4,交給 lan.validate)", severity: {score: {value: 0.4, default: 0.4}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N3, name: "程式以「排名稱」稱呼 DL-EN1 name 的地方,和新的排名稱(位置排)同名,§7 grep 檢查容易誤判為位置排語意;已知清單沒列", evidence: ["PROPOSAL.md:331", "app/flatness/lan.py:93,218,628,650", "app/flatness/ui/settings_dialog.py:425,781,1300"], assert: "變更清單會同時出現「排名稱:前排 → 後排」(DL-EN1)與「排1 名稱:排1 → 前排」(位置排)", pursue: "§7 已知例子加「DL-EN1 name 的『排名稱』(lan.FIELD_NAME、diff、settings_dialog)改為『DL-EN1 名稱』」", severity: {score: {value: 0.4, default: 0.4}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N4, name: "§5.2 依賴變更清單文字的測試只點名 test_ui.py,漏 tests/test_lan.py:312「新增探頭 ID 5「中央」」", evidence: ["PROPOSAL.md:159", "tests/test_lan.py:312", "tests/test_ui.py:183"], pursue: "括號內補 test_lan.py", severity: {score: {value: 0.1, default: 0.1}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N5, name: "backend.apply 需把 names 傳給 sync.apply,§6 backend.py 列只寫載入與快取", evidence: ["PROPOSAL.md:305", "PROPOSAL.md:307", "app/flatness/backend.py:147-151"], pursue: "backend.py 列加「apply 傳入 names」", severity: {score: {value: 0.1, default: 0.1}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N6, name: "probe_positions 另有兩個呼叫者未列入 §6:示範模式的虛擬讀值與 plate3d 示範", evidence: ["PROPOSAL.md:311", "app/flatness/measure.py:106-113", "app/flatness/plate3d/demo.py:32"], assert: "改為 5×5 後未定探頭不回傳位置,示範模式凹陷位置會退化為板子中央;改函式簽名時兩處會壞", pursue: "§6 plate3d 列補 measure.py(DemoStation.read)與 plate3d/demo.py", severity: {score: {value: 0.2, default: 0.2}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N7, name: "POS-09 驗收「把探頭 2 設為第 1 排第 2 點 → 3D 標籤『排1 點2』」未寫前提:其餘使用中探頭都要設好位置且不在同一直線,否則 POS-07/P3D-03 拒絕", evidence: ["規格書:1082", "規格書:1080", "PROPOSAL.md:253"], pursue: "驗收補「(其餘使用中探頭已設定位置)」,或 3D 標籤改到 POS-G1 驗", severity: {score: {value: 0.2, default: 0.2}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N8, name: "規格書草稿同步尾巴:3.7.1 欄位表已加 row、point 但沒有頂層 position_names;需求對照表探頭位置列沒有 P3D-03", evidence: ["規格書:473-474", "規格書:1076", "規格書:1189", "PROPOSAL.md:294"], pursue: "3.7.1 補 position_names 一列(待確認);對照表補 P3D-03。也可留到簽核時依 §6 一併處理", severity: {score: {value: 0.2, default: 0.2}}, po_decision: {status: no_decision}}
```

### ✅ STRENGTHS

- §5.5 把方塊優先序與頂端提示明確分開,IP 不符的例外寫在附加標示那一段,三種組合(單獨、與維修中、與設備異常)都有定義。
- `names=None` 的語意寫在兩處(§5.1 為資料流、§5.3 為呼叫端),並說明為什麼立即儲存路徑不會丟名稱,實作者不需要猜。
- 規格書、changeset、提案三者在 POS-02、POS-07、POS-09、P3D-03 上逐字一致,第 4 輪的同步尾巴全部收齊。
- 程式描述經得起逐行對照:SQL 權限、`LIKE` 建表、`definition_entry` 深拷貝探頭(位置欄位會自然帶到定義檔與主畫面版面)、匯入先經 `read_definition_file` 驗證,都與提案所述相符。

## § 3. Critical Hotspots

本輪沒有達到 hotspot 門檻的 finding。最高為 N2、N3(各 0.4),都是實作時跑測試或做 §7 grep 檢查就會碰到的細節。

## § 4. Effective Cost Matrix

| ID | Effective cost | 修正成本 |
| --- | :---: | :---: |
| N1–N8 | 合計約 1.9 | 合計約 0.7h,全部是文字補充 |
| **總計** | **約 1.9**(45 → 15.9 → 9.3 → 3.4 → 1.9) | **約 0.7h** |

本輪 tally(供 F2 append):Round 5|2026-10-15|BLOCKER 0|CONCERN 0|NIT 8|STRENGTH 4|ship-as-is。

## § 5. Decision Log

- 本輪沒有新的 PO 決定,所有 finding 的 `po_decision` 都是 `no_decision`。
- 沿用的前提:第 3 節 11 項 PO 決定;第 10 節 4 點延後給 PO,依賴段落清楚。
- 第 4 輪 9 項全部成立,沒有重開。N1、N7 是第 4 輪修正的附帶細節;其餘是全文一致性檢查新找到的實作細節。

## § 6. Verdict + Next Round Focus

- **Status:** ship-as-is(BLOCKER 0、CONCERN 0、NIT 8、STRENGTH 4)
- **Recommend:**
  - 可以送 PO 簽核。N7、N8 牽涉規格書文字,方便的話簽核前順手修;N1 若 PO 希望整台設備異常時仍顯示 IP 不符(現行行為),簽核時說一聲即可。
  - N2～N6 是實作細節,M1(N2、N5)、M2(N3、N4)、M4(N6)開工時處理即可。
- **Convergence:** effective cost 45 → 15.9 → 9.3 → 3.4 → 1.9;連續三輪沒有 BLOCKER,本輪沒有 CONCERN。文件已收斂,不需要再審。
- **Next Round Focus:** 無。下一次審查對象應是 M1 的程式變更。

(本輪沒有 BLOCKER,不附 § 7 Reflection。)
