---
target: docs/pm/bootp-lease/PROPOSAL.md（＋ Downloads/表面平整檢查系統_需求規格書.md DSC-21～DSC-23 與 G/A）
target_rev: d54a0eb
date: 2026-11-02
reviewer: spectra-review (v2.0)
iteration: 3
verdict: ship-as-is
schema_version: enhanced-v1
contract_version: spectra-contract-v1
mode: pm-skill-generic-doc
---

> 💡 spectra-review v2.0 active(Minerva 4 能力 framework)。若想用原版簡潔版,用 `/spectra-review --lite <target>`。

🎯 Mode: PM Skill — Generic doc (target: docs/pm/bootp-lease/PROPOSAL.md)

# Spectra-Review Round 3 — docs/pm/bootp-lease/PROPOSAL.md（rev 3）

本輪範圍與限制:
- 變更來源:`git diff 1430b54 d54a0eb -- docs/pm Downloads`(提案 73 行、規格書 12 行)。
- 對照來源:規格書 DSC-21～23(997-999)、說明與 G/A(1001-1009);鄰近條文 INS-04(142)、3.0.4 步驟 3(200)、3.0.7(303-316)、3.0.8(318-328)、DSC-07(849)、DSC-08(850)、DSC-10(852)、DSC-14(856)、DSC-15(857)、DSC-19(965)、DSC-20(985-993)、POS-05(1133)、PDT-01(1166)、6.2 索引(1265、1281)。
- 程式碼:installer/steps/03-bootp.sh、installer/setup-bootp.sh、installer/lib/common.sh、app/flatness/{dnsmasq,backend,discovery,arpwatch,lan,dlen1}.py、ui/main_window.py、ui/settings_dialog.py。
- 畫面文件:docs/ui/screen-design-spec.md、docs/ui/screens-device-settings.md、docs/ui/prototype/board-station.html、docs/manual/操作說明書.md(10.1 在 583 行、11.4 在 660 行)。
- 現場證據:`.dev/flatness.log`(2869 行)。以 Python 計算 plat1(`74:95:a7:15:9b:82`)850 筆 BOOTP 行的間隔。`/usr/sbin/dnsmasq` 2.90 以 Python 抽取字串。本機 dnsmasq 目前沒有執行,無法看 `/proc/<pid>/fd`。
- SKILL 提到但本 repo 沒有的檔案:docs/CONTEXT.md、docs/index.md(略過)。references/*.md 與 pm-skill-proposal.md 存在,但依呼叫者指示只寫 F1,不寫 F2 與 decision-log。

## § 1. Mental Lens

- **Claim → Evidence → Verdict**:第 2 輪 13 項逐項回到 rev 3 原文、程式碼與日誌驗證(§ 5)。rev 3 新增的四個主張逐一追證:60 秒逾時、「主畫面成功連上 = 恢復」、`original` 判斷、改名早於停止。
- **Cross-section consistency**:提案 3.3 ↔ 規格書 DSC-23 逐字比對訊息、秒數與檔名,全部一致。提案第 4 節修訂表 ↔ 規格書三條的「修訂」括號 ↔ 實際描述同一畫面的 UI 文件,缺口在最後這一層(C1)。
- **Anti-Bias**:60 秒與「主畫面成功連上」都是第 2 輪 C7 的建議。本輪把它們當成新設計審查,檢查與主畫面重新偵測、維修中設備、IP 衝突的交互作用(N1、N2)。
- **Understand-not-argue**:rev 3 把第 2 輪的問題修得很乾淨。剩下的問題落在兩處:提案外的文件同步,以及 RST 子條件縮得太窄。

## § 2. 4-Tier Findings

### 🔴 BLOCKERS — 落地前必修

(none found)

### 🟡 CONCERNS — 應修

#### C1. 文件影響清單漏列畫面設計規格與原型;screen-design-spec 仍寫「各種提示各自顯示、互不取代」

**📛 命名:** 提案 3.4(PROPOSAL.md:151-152)與第 4 節「文件」列(PROPOSAL.md:182)只列規格書、操作說明書、快速安裝指南、變更紀錄。rev 3 把 POS-05 加入修訂表(PROPOSAL.md:167),但描述同一畫面的 UI 文件沒有列入。

**📣 主張:**
- 規格書 6.2 索引把「畫面說明(畫面設計規格)」的範圍延伸到 DSC-23(規格書:1265)。也就是說,規格書自己宣告 DSC-21～23 的畫面細節由 docs/ui/screen-design-spec.md 承載。
- screen-design-spec.md 有四處與 DSC-23 直接衝突或缺漏:
  - :110 系統狀態提示列出「第 N 台 名稱 偵測不到」等類型,並寫「各種提示各自顯示、互不取代」。這正是 rev 3 為 POS-05 修訂的那句話。
  - :204 IP 不符標籤只寫「偵測不到時不加」,沒有「BOOTP 被拒期間暫停」(DSC-20 修訂)。
  - :222 方塊「設備異常」的文字清單沒有「拿不到 IP」與「拿不到 IP・維修中」。
  - :346 PDT-01 失敗提示只有「偵測不到第 N 台,清單未變更」。程式也一樣(settings_dialog.py:1603)。
- docs/ui/screens-device-settings.md:36、40 列出 `set_flag` 類型與 `ProbeTile` 方法,也要加上新類型與新方塊狀態。
- docs/ui/prototype/board-station.html:599、608、718 用同一套「偵測不到」邏輯示範主畫面,沒有「拿不到 IP」情境。
- 依 docs/ddd-doc-maintenance.md 第 1 節「文件先行,runtime 對齊」,M3 實作者會讀 screen-design-spec。照 :110 實作,會做回第 2 輪 C6 要消除的「同一台兩條提示」。
- Impact 4/10 / Probability 0.6
- Evidence:PROPOSAL.md:151-152、167、182;規格書:1265;docs/ui/screen-design-spec.md:110、204、222、346;docs/ui/screens-device-settings.md:36、40;docs/ui/prototype/board-station.html:599、608、718

**🎯 追求:** 在 3.4 與第 4 節「文件」列補上以下項目:
- screen-design-spec.md 的 :110、:204、:222、:346 四處;
- screens-device-settings.md 的 :36、:40;
- 原型 board-station.html 加一個「拿不到 IP」情境按鈕;
- M5 的「截圖」註明要重拍 screens-device-settings.md:46 那張主畫面截圖。

| Option | 動作 | 成本 |
|---|---|---|
| A | 不修 | M3 依舊畫面規格實作出重複提示,M5 才發現,返工 0.5d |
| B | 現在補清單 | 0.2h |

推薦 B。

```yaml
- tier: 🟡 CONCERN
  id: C1
  name: "文件影響清單漏列 screen-design-spec／原型;:110 仍寫互不取代"
  evidence: ["PROPOSAL.md:151-152", "PROPOSAL.md:167", "PROPOSAL.md:182", "規格書:1265", "docs/ui/screen-design-spec.md:110,204,222,346", "docs/ui/screens-device-settings.md:36,40", "docs/ui/prototype/board-station.html:599,608,718"]
  severity: {score: {value: 2.4, default: 2.4, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}
  fix_economics: {difficulty: {value: 0.2, default: 0.2, override: null}, roi: {value: 12.0, default: 12.0}, resource_estimate: {value: "1h", default: "1h", override: null}}
  cross_impact: {affected_modules: [docs/ui, main_window, settings_dialog, prototype], cascade_depth: 2, dependency_chain: "UI 規格 → M3 實作 → 頂端提示是否重複"}
  phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 3, estimated_rework_cost: low}
  decision_tree: {options: [{id: A, action: 不修, cost: "M3 依舊規格實作,0.5d 返工"}, {id: B, action: 補清單, cost: 0.2h}], recommended_option: B, counterfactual: "實作者照 screen-design-spec:110 並列兩條提示,與 POS-05 修訂衝突"}
  dependencies: {blocks: [], blocked_by: [], manual_blocks: []}
  severity_decay: {phase_when_found: 0, by_phase: {3: {value: 3.0, default: 3.0, override: null}}}
  po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}
```

#### C2. 「儲存後按住 RST 3 秒」以已儲存的設定判斷,不看設備實際的 IP:正被拒絕的設備會同時收到「洽維護人員」與「按 RST」,與 DSC-23-A1 衝突;已停用設備重新啟用時又漏掉 RST

**📛 命名:** rev 3 的 RST 子條件是「已儲存的設定中這台原本有另一個 IP」(PROPOSAL.md:141;規格書:999「原本有另一個 IP 時加…」)。另一條是「這台正被拒絕:提示拒絕原因」(PROPOSAL.md:143)。兩條提示的先後沒有規定。

**📣 主張:**
- **按 RST 的前提是設備記得一個 IP。** DL-EN1 記住 IP 後不再送 BOOTP(規格書 DSC-07:849;03-bootp.sh:94)。正在被拒的設備,表示它手上沒有 IP、一直在送 BOOTP。
- **誤報情境。** 使用中的 B 以 .11 被拒(佔用)。工程人員改用 .13,還沒儲存就按「探頭偵測」。依 rev 3:
  - `original[B]` 是「使用中、.11」,符合「原本有另一個 IP」,所以加「儲存後按住 RST 3 秒」;
  - B 正被拒絕,所以同時提示「被其他設備佔用,請洽維護人員」。
  - 這正是 DSC-23-A1「同時叫人按 RST 又叫人洽維護人員」(規格書:1009)。實際上 B 沒有 IP,儲存後下一次 BOOTP 就會拿到 .13,不需要按 RST。
- **漏報情境。** 已停用的舊機重新設為使用中並改用新 IP。它記得舊 IP,`seen_ip` 有值,但 `original` 的狀態是已停用,`assigns_ip` 為 False(lan.py:84-86),所以不加 RST 提示。從其他產線移來的 DL-EN1(不明、`seen_ip` 有值)也一樣。第 2 輪 C5 建議的條件是「`orig.ipv4` 有值,**或** `seen_ip` 不等於新 IP」,rev 3 只採用了前半。
- 有緩衝:儲存後主畫面的 DSC-20「IP 不符」會再提示按 RST,所以漏報只是多走一輪。
- Impact 4/10 / Probability 0.3
- Evidence:PROPOSAL.md:140-143;規格書:999、1009;規格書:849;app/flatness/lan.py:84-86;app/flatness/ui/settings_dialog.py:637、2007-2009

**🎯 追求:**
- RST 子條件改為「設備實際使用的 IP(`seen_ip`)有值且不等於設定的 IP,而且這台目前沒有被拒絕」;
- 兩條提示並存時,規定「正被拒絕」優先、不加 RST 句;
- AC-6 補 ③:被拒中的設備改 IP 後按「探頭偵測」→ 只提示拒絕原因,不出現 RST。

| Option | 動作 | 成本 |
|---|---|---|
| A | 不修 | 規格內部矛盾(PDT-01 修訂 vs DSC-23-A1);M3 依字面做出 A1 錯誤行為 |
| B | 改條件並定優先序 | 0.3h |

推薦 B。

```yaml
- tier: 🟡 CONCERN
  id: C2
  name: "RST 子條件依已儲存設定而非實際 IP;與 DSC-23-A1 衝突"
  evidence: ["PROPOSAL.md:140-143", "規格書:999", "規格書:1009", "app/flatness/lan.py:84-86", "app/flatness/ui/settings_dialog.py:637,2007-2009"]
  severity: {score: {value: 1.2, default: 1.2, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}
  fix_economics: {difficulty: {value: 0.3, default: 0.3, override: null}, roi: {value: 4.0, default: 4.0}, resource_estimate: {value: "1h", default: "1h", override: null}}
  cross_impact: {affected_modules: [settings_dialog, spec PDT-01/DSC-23, 操作說明書], cascade_depth: 2, dependency_chain: "提示條件 → 現場操作(RST 或洽維護)"}
  phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 3, estimated_rework_cost: low}
  decision_tree: {options: [{id: A, action: 不修, cost: "A1 錯誤行為被寫進規格"}, {id: B, action: 改為 seen_ip 並定優先序, cost: 0.3h}], recommended_option: B, counterfactual: "工程人員對沒有 IP 的設備按 RST,同時被叫去找維護人員"}
  dependencies: {blocks: [], blocked_by: [], manual_blocks: []}
  severity_decay: {phase_when_found: 0, by_phase: {}}
  po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}
```

### 🟢 NITS — 可選 polish

- **N1. 「主畫面成功連上 = 恢復」沒有確認連上的是不是這台。**
  - 主畫面依設定 IP 連線,只送讀取命令,不核對 MAC(dlen1.py:150-186)。
  - 若佔用者真的在線(DSC-22 ① 的舊機接回網路),主畫面會連上舊機並視為「恢復」。3～5 秒後下一筆被拒行又設回「被拒」,WARNING 每輪多兩筆,AC-7 不成立,方塊在「設備正常」與「拿不到 IP」之間跳動。
  - 修 DSC-21 之後,`address in use` 只會出現在舊安裝,所以機率低。
  - 建議:連線成功後 10 秒內沒有新的被拒行,才算恢復;或刪除這一條,只保留 BOOTP 配發與 ARP 兩條。
- **N2. 60 秒逾時後的描述對維修中設備不成立,日誌也會說錯。**
  - 「之後由一般的『偵測不到』接手」(PROPOSAL.md:118)與 AC-10 只適用於使用中。維修中設備不列入偵測(main_window.py:1130),逾時後應回到「維修中」。
  - 依日誌規則(PROPOSAL.md:146),逾時清除會記成「恢復」WARNING,但設備其實已拔線。建議記為「60 秒未再被拒,清除提示」。
  - AC-10 的「60 秒後」是從最後一次被拒起算,從拔線起算是 55～60 秒。建議寫明起算點。
  - 依日誌,60 秒門檻本身沒有問題,見 S2。
- **N3. 「舊的 dnsmasq 若在停止前改寫租約檔,只會寫出新檔」(PROPOSAL.md:67)與 dnsmasq 的實作不符。**
  - 沒有 `leasefile-ro` 時,dnsmasq 以 `a+` 開啟租約檔並一直開著,改寫時先 rewind 再 ftruncate。二進位中有 `a+` 與 `cannot open or create lease file %s: %s`(🟡,依原始碼記憶,本機無法看 fd)。
  - 所以改名後的寫入會進到已改名的備份檔,原路徑不會出現新檔。
  - 結論(原路徑不存在、新的 dnsmasq 不讀)不變。建議改寫為「舊的 dnsmasq 在停止前仍可能改寫已改名的備份檔,內容是它記憶體中的租約,原路徑不會再出現」。
- **N4. `|| true` 之前的安裝日誌不分情況。**
  - PROPOSAL.md:63 在停止前一律寫「重新啟動 App 的 dnsmasq 以套用新主設定」。App 沒在執行時也會寫這一行。
  - 停止程式用的是新的 `DNSMASQ_CMD`(03-bootp.sh:87)。日後命令列若有變更,`pkill` 對不到舊程序,`|| true` 會把「新設定沒有生效」也一起吞掉。
  - 建議依停止程式的結束碼記錄:0 記「已停止,App 將以新設定重新啟動」;1 記「App 未執行 dnsmasq,下次啟動時套用」;其他記警告。
- **N5. 第 6 節 M1 仍寫「安裝後檢查」(PROPOSAL.md:202)。** rev 3 已刪除 3.0.7 的 `leasefile-ro` 檢查(3.4、第 4 節都已移除),M1 這裡漏改。

```yaml
- {tier: 🟢 NIT, id: N1, name: "主畫面連上未核對身分即視為恢復", evidence: ["PROPOSAL.md:117", "app/flatness/dlen1.py:150-186"], severity: {score: {value: 0.75, default: 0.75, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}, fix_economics: {difficulty: {value: 0.2, default: 0.2, override: null}, roi: {value: 3.75, default: 3.75}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [backend, main_window], cascade_depth: 2, dependency_chain: "恢復條件 → 狀態跳動 → WARNING 數"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 2, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 加 10 秒確認或刪除該條}], recommended_option: B, counterfactual: "IP 衝突時提示跳動、AC-7 失敗"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {}}, po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}}
- {tier: 🟢 NIT, id: N2, name: "60 秒逾時對維修中描述錯、日誌記成恢復、AC-10 起算點", evidence: ["PROPOSAL.md:118", "PROPOSAL.md:146", "PROPOSAL.md:197", "app/flatness/ui/main_window.py:1130"], severity: {score: {value: 0.6, default: 0.6, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}, fix_economics: {difficulty: {value: 0.1, default: 0.1, override: null}, roi: {value: 6.0, default: 6.0}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [backend, main_window], cascade_depth: 1, dependency_chain: "文字"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 3, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 補三句}], recommended_option: B, counterfactual: "維修中設備逾時後被畫成偵測不到"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {}}, po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}}
- {tier: 🟢 NIT, id: N3, name: "改名後舊 dnsmasq 寫入去向描述錯誤", evidence: ["PROPOSAL.md:67", "/usr/sbin/dnsmasq strings (a+, cannot open or create lease file)"], severity: {score: {value: 0.3, default: 0.3, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}, fix_economics: {difficulty: {value: 0.1, default: 0.1, override: null}, roi: {value: 3.0, default: 3.0}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [proposal], cascade_depth: 1, dependency_chain: "文字"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 6, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 改寫一句}], recommended_option: B, counterfactual: "維護人員誤判備份檔未被改動"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {}}, po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}}
- {tier: 🟢 NIT, id: N4, name: "停止前日誌不分情況、|| true 吞掉未生效", evidence: ["PROPOSAL.md:61-64", "installer/steps/03-bootp.sh:87"], severity: {score: {value: 0.5, default: 0.5, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}, fix_economics: {difficulty: {value: 0.1, default: 0.1, override: null}, roi: {value: 5.0, default: 5.0}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [installer], cascade_depth: 1, dependency_chain: "安裝日誌判讀"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 1, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 依結束碼記錄}], recommended_option: B, counterfactual: "新設定未生效而安裝日誌顯示已重新啟動"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {}}, po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}}
- {tier: 🟢 NIT, id: N5, name: "M1 仍寫安裝後檢查", evidence: ["PROPOSAL.md:202"], severity: {score: {value: 0.2, default: 0.2, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}, fix_economics: {difficulty: {value: 0.05, default: 0.05, override: null}, roi: {value: 4.0, default: 4.0}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [proposal], cascade_depth: 1, dependency_chain: "文字"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 1, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 刪四字}], recommended_option: B, counterfactual: "M1 多做一項已撤回的檢查"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {}}, po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}}
```

### ✅ STRENGTHS

- **S1. 安裝包的順序在現有腳本上成立。**
  - `--test` 在 03-bootp.sh:74,停止程式在 :84-91,sudoers 在 :99-105。把停止排在 `step_bootp` 最後,三者都已完成。
  - 加上 `[[ -f ]]` 與 `|| true`,`set -euo pipefail`(setup-bootp.sh:11)下也不會中止。
  - `--test` 失敗時 `fail` 會先結束,不會執行停止,所以第 2 輪指出的重啟迴圈也避開了。
- **S2. 60 秒門檻有日誌支持。**
  - 850 筆 BOOTP 的間隔:3 秒 185 次、4 秒 243 次、5 秒 418 次,1 秒 1 次。
  - 只有兩次較長:10.8 秒(10:18:51→10:19:02)與 7.7 秒(10:41:26→10:41:34)。兩次的 xid 都重設為 1358107507,是 DL-EN1 重新啟動(RST 或斷電)。
  - 61 分鐘內沒有退避。「每 3～5 秒」屬實,60 秒約為最長間隔的 5.5 倍。
- **S3. `original` 可以支撐 PDT-01 的判斷。**
  - `self.original` 是 MAC → `LanDevice`,有 `status`、`ipv4` 與 `assigns_ip`(settings_dialog.py:637;lan.py:84-86)。
  - 儲存成功後更新並關閉對話框(settings_dialog.py:2007-2009),所以 `original` 就等於已儲存、已寫入主機對應的版本。
  - 替換(DSC-14)的新機在 `original` 中是不明或其他狀態,會正確判為「尚未儲存」。
- **S4. 提案與規格書逐字一致。** 兩種主畫面訊息、PDT-01 訊息與 RST 句、資訊列格式、60 秒、`dnsmasq.leases.flatness-old-<時間>`、「DHCP 不在範圍內」、修訂括號(DSC-07 停止來源、POS-05)都對得上。6.2 索引兩處已延伸到 DSC-23。

## § 3. Critical Hotspots

本輪沒有 hotspot:最高 effective cost 2.4,cascade 都 ≤ 2(對照 shortcut table「1-5 / ≤3 視 case,通常無 hotspot」)。

| 項目 | 早解成本 | 晚解成本 | ratio |
|---|---|---|---|
| C1 UI 文件同步(參考) | 0.2h | M3 返工約 0.5d | ~20× |

## § 4. Effective Cost Matrix

| ID | Tier | Impact | Prob | Effective cost | Fix 成本 |
|---|:---:|:---:|:---:|:---:|:---:|
| C1 | 🟡 | 4 | 0.6 | 2.4 | 0.2h |
| C2 | 🟡 | 4 | 0.3 | 1.2 | 0.3h |
| N1 | 🟢 | 5 | 0.15 | 0.75 | 0.2h |
| N2 | 🟢 | 3 | 0.2 | 0.6 | 0.1h |
| N4 | 🟢 | 5 | 0.1 | 0.5 | 0.1h |
| N3 | 🟢 | 1 | 0.3 | 0.3 | 0.1h |
| N5 | 🟢 | 1 | 0.2 | 0.2 | <0.1h |
| **合計** | | | | **≈5.95** | **≈1h** |

成本趨勢:第 1 輪 ≈27.0 → 第 2 輪 ≈18.1 → 第 3 輪 ≈5.95,比第 2 輪下降約 67%。Saving:現在修只要約 1 小時;若到 M3 才發現 C1、C2,估計返工約 0.5～1 天。

## § 5. Decision Log

**第 2 輪 finding 在 rev 3 的實際狀態(已逐項驗證):**

| R2 ID | 狀態 | 驗證 |
|---|:---:|---|
| C1 停止程式的位置與失敗處理 | ✅ fixed | PROPOSAL.md:61-64:`conf_changed`、最後一步、`|| true`、停止前先寫安裝日誌。與 03-bootp.sh:74、84-91、99-105 的順序相符(S1)。規格書 DSC-21 同步寫「最後一步」「App 未執行時忽略」。殘留:日誌不分情況(N4)。 |
| C2 ② 第二條件與改名互相抵消 | ✅ fixed | 採選項 (a):PROPOSAL.md:94 只剩「沒有 `leasefile-ro`」;`/proc` 與 dnsmasq.py 影響列已刪除;規格書:998 同步。 |
| C3 主畫面「未配發」寫「尚未儲存」 | ✅ fixed | PROPOSAL.md:111、129、132;規格書:999 訊息改為「IP 不在配發網段,或主機對應未更新」。 |
| C4 判定表套用到 DHCP 行 | ✅ fixed | PROPOSAL.md:106 限定 BOOTP;規格書:999「DHCP 不在範圍內」。 |
| C5 PDT-01 條件不精確、改 IP 漏 RST | 🔶 partial | 主條件改用 `original`,可以實作(S3),AC-6 加入 ②。RST 子條件只採「已儲存的設定原本有另一個 IP」,沒有採用 `seen_ip`,因此出現誤報與漏報,並與 DSC-23-A1 衝突(C2)。 |
| C6 與 POS-05 衝突、提示重複 | ✅ fixed(規格層)/ 殘留 | 修訂表加入 POS-05(PROPOSAL.md:167)。取代規則寫在 PROPOSAL.md:133 與規格書:999。維修中改用維修中的顏色(PROPOSAL.md:130)。新增 AC-11。殘留:screen-design-spec.md:110 同一句「互不取代」沒有列入修訂(C1)。 |
| C7 被拒狀態沒有逾時 | ✅ fixed | 60 秒、主畫面連上、ARP 在監聽端判斷(PROPOSAL.md:116-118、177);新增 AC-10;門檻有日誌支持(S2)。殘留:N1(連上未核對身分)、N2(維修中與日誌文字)。 |
| N1 安裝包觸發的重啟記為 ERROR | ✅ fixed | PROPOSAL.md:63 寫明會有 ERROR、安裝日誌先記一筆;DSC-07 加註停止來源(PROPOSAL.md:164;規格書:997 括號)。 |
| N2 改名覆蓋前次備份 | ✅ fixed | 檔名加時間 `-<YYYYMMDD-HHMMSS>`(PROPOSAL.md:66;規格書:997;AC-3)。另見 N3(本輪):寫入去向描述錯誤。 |
| N3 「DSC-22 ② 會提示尚未升級」言過其實 | ✅ fixed | PROPOSAL.md:77 改為「安裝包還沒跑之前……針對舊租約提出警告」。 |
| N4 3.0.7 檢查不可能失敗 | ✅ fixed(撤回) | 3.0.7 修訂已從 3.1、3.4、第 4 節與規格書括號中移除。殘留:M1 仍寫「安裝後檢查」(N5)。 |
| N5 ① 時間用 `last_seen` | ✅ fixed | PROPOSAL.md:89-90 改為「最後出現」並註明來源;規格書 G1(1005)格式統一為「10/07 13:51」。 |
| N6 索引表未納入 DSC-21～23 | ✅ fixed | 規格書:1265、1281 都已延伸到 DSC-23。 |

- 本輪新拍板:無,全部為 `no_decision`。
- 依據紀錄(非決定):DL-EN1 被拒時不退避,間隔 3～5 秒;重新啟動時 xid 重設、間隔 8～11 秒(S2)。

## § 6. Verdict + Next Round Focus

- **Status:** ship-as-is。沒有 BLOCKER,第 2 輪 13 項中 12 項已修、1 項部分修。
- **Recommend:** 簽核時順手修正,約 1 小時:
  - C1:文件清單補上 screen-design-spec 的 :110、:204、:222、:346,screens-device-settings 的 :36、:40,以及原型。
  - C2:RST 子條件改用 `seen_ip`,並規定「正被拒絕」的提示優先。
  - N1～N5 可在同一次修正中一起處理。
- **Next Round Focus:** 不需要第 4 輪文件審查。建議在 M3 完成後做一次 V7 spec-compliance-review,重點如下:
  1. 頂端提示與結果橫幅是否只出現一條「拿不到 IP」;
  2. 60 秒逾時後,使用中回到偵測不到、維修中回到維修中;
  3. AC-7 的 WARNING 數在 IP 衝突情境下是否成立。

(§ 7 Mental Lens Reflection:本輪沒有重大 BLOCKER,不觸發。)
