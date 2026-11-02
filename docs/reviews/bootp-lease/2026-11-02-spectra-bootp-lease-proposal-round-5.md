---
target: docs/pm/bootp-lease/PROPOSAL.md（＋ Downloads/表面平整檢查系統_需求規格書.md DSC-21～DSC-23 與說明、G/A）
target_rev: 9619d45
date: 2026-11-02
reviewer: spectra-review (v2.0)
iteration: 5
verdict: ship-as-is
schema_version: enhanced-v1
contract_version: spectra-contract-v1
mode: pm-skill-generic-doc
---

> 💡 spectra-review v2.0 active(Minerva 4 能力 framework)。若想用原版簡潔版,用 `/spectra-review --lite <target>`。

🎯 Mode: PM Skill — Generic doc (target: docs/pm/bootp-lease/PROPOSAL.md)

# Spectra-Review Round 5 — docs/pm/bootp-lease/PROPOSAL.md（rev 5）

本輪範圍與限制:
- 變更來源:`git diff d91045e 9619d45 -- docs/pm Downloads`(提案 28 行、規格書 DSC-23 一列)。
- 對照來源:規格書 DSC-23(999)、說明與 G/A(1001-1009)、DSC-15(857)、DSC-20(985)、JDG-04(368)、UI-07(388)、POS-05(1133)、PDT-01(1166)。DSC-07/08/10/14/19、3.0.4 步驟 3、3.0.8、6.2 本輪沒有變更,沿用前幾輪的比對結果。
- 程式碼:installer/setup-bootp.sh:11(`set -euo pipefail`)、installer/steps/03-bootp.sh:14、84-91;app/flatness/lan.py:58-75;app/flatness/store.py:28-38、80-95;app/flatness/discovery.py:27、45-61;app/flatness/arpwatch.py:48-52;app/flatness/backend.py:126-135;app/flatness/ui/settings_dialog.py:171、671-691、1576-1606;app/flatness/ui/main_window.py:1300-1318、1362-1374。
- SKILL 提到但本 repo 沒有的檔案:docs/CONTEXT.md、docs/index.md(略過)。依呼叫者指示只寫 F1,不寫 F2。第 5 輪是最後一輪。

## § 1. Mental Lens

- **Claim → Evidence → Verdict**:rev 5 新增或改寫的主張逐條追證:探頭偵測提示的優先序、「最近 60 秒沒有這台的 BOOTP 請求」的資料來源、15 秒規則、「被拒期間不顯示讀值、不判定」、`rc=0; "$STOP_HELPER" || rc=$?`。
- **Cross-section consistency**:提案 3.3 ↔ 規格書 DSC-23 逐字比對,一致。這次的缺口在 DSC-23 新句與 DSC-15、JDG-04 用詞之間(C1)。
- **Anti-Bias**:「不顯示讀值」是第 4 輪 N2 的建議;「不判定」是作者自己加的。本輪把整句當新設計重審,問題出在「不判定」三個字。
- **Understand-not-argue**:第 4 輪六項都有處理,且大多照建議落實。剩下的是新句子的用詞,以及新條件沒有寫明資料來源。

## § 2. 4-Tier Findings

### 🔴 BLOCKERS — 落地前必修

(none found)

### 🟡 CONCERNS — 應修

#### C1. 「被拒期間……不顯示讀值、不判定」借用了維修中的用詞,可能被實作成「這台不計入整片判定」,整片因此可能判為合格

**📛 命名:** PROPOSAL.md:118;規格書:999「被拒期間即使主畫面連得上這個 IP,方塊仍顯示『拿不到 IP』,不顯示讀值、不判定」。

**📣 主張:**
- **規格書中「不判定」的意思是「不計入整片判定」。** DSC-15(規格書:857)寫維修中「不連線、不列入偵測、不量測、不判定,整片結果只依『使用中』的量測點判定」;POS-05(:1133)同樣寫「不連線、不量測、不判定」。照這個用法,被拒中、連得上的使用中設備會被排除,其他點都合格時整片就判為合格。
- **但同一條的其他規則要的是設備異常。** 提案 3.3「拿不到 IP 取代這台的偵測不到」並列入結果橫幅(PROPOSAL.md:129、134;規格書:999)。偵測不到在程式中是設備異常:main_window.py:1306-1310 把該台方塊設為 ERR、原因列入 `errs`,:1374 橫幅顯示「設備異常」。JDG-04(:368)規定任一點設備異常時整片為設備異常。
- **連不上時兩種讀法結果相同,連得上時不同。** 連不上時本來就是偵測不到,整片為設備異常。:118 處理的是連得上的情況(連到的可能是佔用者):main_window 會把這台當成正常;若照「不判定」排除這台,整片可能判為合格,但這台的探頭位置沒有量到,屬於漏檢。AC-11(PROPOSAL.md:207)與 DSC-23 驗收欄都只涵蓋連不上的情況。
- **會發生的情境。** 舊安裝,`.11` 被舊機 A 的租約佔用,A 仍接在網路上;B 設為 `.11`。主畫面連到 A,B 一直被拒。修完 DSC-21 後只會出現在舊安裝,但 DSC-21 ② 本來就是為舊安裝設計的,而漏檢的代價是不良品出貨。
- Impact 7/10 / Probability 0.15
- Evidence:PROPOSAL.md:118、129、134、207;規格書:368、388、857、999、1133;app/flatness/ui/main_window.py:1306-1318、1374

**🎯 追求:** 把「不判定」改為明確的判定規則,並補驗收:
- 提案 :118 與規格書 999 改為「……方塊仍顯示『拿不到 IP』,不顯示讀值;這台各點以設備異常計(同偵測不到,JDG-04),整片為設備異常」。維修中的「拿不到 IP・維修中」仍依 DSC-15 不計入,不受影響。
- 這句移出「以下也視為恢復」清單(見 N2)。
- AC-11 加一項:「被拒中的使用中設備,主畫面連得上該 IP(佔用者在線):方塊顯示『拿不到 IP』、無讀值,結果橫幅為設備異常,不出現合格」。規格書 DSC-23 驗收欄同步。

| Option | 動作 | 成本 |
|---|---|---|
| A | 不修 | 實作者可能比照維修中排除這台,佔用者在線時出現漏檢的合格 |
| B | 改為「以設備異常計(JDG-04)」,AC-11 加連得上的情況 | 0.1h |

推薦 B。反事實:不修的話,M3 實作者照 DSC-15 的用法寫成排除,V7 也只會驗連不上的 AC-11,漏檢要到現場才會發現。

```yaml
- tier: 🟡 CONCERN
  id: C1
  name: "被拒期間『不判定』可被讀成不計入整片判定,佔用者在線時整片可能誤判合格"
  evidence: ["PROPOSAL.md:118", "PROPOSAL.md:129", "PROPOSAL.md:134", "PROPOSAL.md:207", "規格書:368", "規格書:857", "規格書:999", "規格書:1133", "app/flatness/ui/main_window.py:1306-1318", "app/flatness/ui/main_window.py:1374"]
  severity: {score: {value: 1.05, default: 1.05, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}
  fix_economics: {difficulty: {value: 0.1, default: 0.1, override: null}, roi: {value: 10.5, default: 10.5}, resource_estimate: {value: "1h", default: "1h", override: null}}
  cross_impact: {affected_modules: [main_window, spec DSC-23/JDG-04, AC-11], cascade_depth: 2, dependency_chain: "DSC-23 方塊規則 → 整片判定(JDG-04) → 量測紀錄 judgment"}
  phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 3, estimated_rework_cost: low}
  decision_tree: {options: [{id: A, action: 不修, cost: "可能漏檢誤判合格"}, {id: B, action: "改為以設備異常計並補 AC-11", cost: 0.1h}], recommended_option: B, counterfactual: "M3 比照維修中排除這台,佔用者在線時整片合格但有位置未量"}
  dependencies: {blocks: [], blocked_by: [], manual_blocks: []}
  severity_decay: {phase_when_found: 0, by_phase: {3: {value: 1.5, default: 1.5, override: null}}}
  po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}
```

### 🟢 NITS — 可選 polish

- **N1. 「最近 60 秒沒有這台的 BOOTP 請求」沒有寫資料從哪裡來;現有欄位只能近似。**
  - 3.3「狀態」(PROPOSAL.md:122)只保存被拒的時間,而且只追蹤使用中、維修中(:106)。這條 RST 規則用在「尚未儲存」分支,設備多半是不明或已停用,沒有對應的狀態。
  - `lan_device` 沒有「最近一次 BOOTP 請求時間」。`last_seen` 與 `last_request`(lan.py:63、65)記的是最近一次任何事件:ARP 事件也是 `count=1`(arpwatch.py:52、store.py:37),會把 `last_request` 改成 `"ARP"`、`last_seen` 改成 ARP 的時間(store.py:86-90、backend.py:130-131)。
  - 可行的近似是「`last_request == "BOOTP"` 且 `last_seen` 在 60 秒內」。正在要 IP 的設備沒有 IP,不會送 ARP,所以一般情況下結果正確;設定頁也會在探索事件寫入後更新這兩個欄位(settings_dialog.py:171、689-690)。
  - 建議在 :143 註明採用這個近似,或在 backend 為每個 MAC 另記最近一次 BOOTP 請求時間,並列入第 4 節 backend.py 的變更。否則實作者需要自己決定是否新增狀態。
  - 另外,AC-6 ②(:202)與規格書驗收欄「改了 IP 未儲存時 → 另加按 RST 的提示」沒有寫前提「已有實際使用 IP(`seen_ip`)」。設備開機後最長 3 分鐘才會有 ARP 位址偵測封包(DSC-20 驗收),太早按會看不到 RST 提示。建議驗收寫明前提。
- **N2. :118 放在「以下也視為恢復」清單中,但它不是恢復條件。**
  - PROPOSAL.md:115-119 是恢復條件的清單,:118 卻是被拒期間的顯示規則,讀者可能誤以為「連得上」也算恢復,與 :117 的 15 秒規則混淆。
  - 建議移到「主畫面」段(:133-136 附近),與 C1 的修改一起處理。規格書 999 的位置(接在提示消失條件之後,以分號分隔)可以不動。

```yaml
- {tier: 🟢 NIT, id: N1, name: "最近 60 秒 BOOTP 請求的資料來源未寫明;AC-6 ② 缺 seen_ip 前提", evidence: ["PROPOSAL.md:106", "PROPOSAL.md:122", "PROPOSAL.md:143", "PROPOSAL.md:202", "規格書:999", "app/flatness/lan.py:63-65", "app/flatness/arpwatch.py:52", "app/flatness/store.py:37", "app/flatness/store.py:86-90", "app/flatness/backend.py:130-131", "app/flatness/ui/settings_dialog.py:171", "app/flatness/ui/settings_dialog.py:689-690"], severity: {score: {value: 0.3, default: 0.3, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}, fix_economics: {difficulty: {value: 0.05, default: 0.05, override: null}, roi: {value: 6.0, default: 6.0}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [backend, settings_dialog], cascade_depth: 1, dependency_chain: "RST 提示條件"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 2, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: "註明 last_request==BOOTP 且 last_seen 60 秒內,或 backend 新增欄位;AC-6 ② 加前提"}], recommended_option: B, counterfactual: "M2/M3 實作者各自決定資料來源,V7 對不上規格"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {}}, po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}}
- {tier: 🟢 NIT, id: N2, name: "被拒期間顯示規則放在恢復條件清單中", evidence: ["PROPOSAL.md:115-119"], severity: {score: {value: 0.2, default: 0.2, override: {by: null, at: null, reason: null}}, band: low, semantic: how_bad}, fix_economics: {difficulty: {value: 0.05, default: 0.05, override: null}, roi: {value: 4.0, default: 4.0}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [docs], cascade_depth: 1, dependency_chain: "文字結構"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 3, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 移到主畫面段}], recommended_option: B, counterfactual: "讀者把連得上當成恢復條件"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {}}, po_decision: {status: no_decision, decided_at: null, decided_by: null, reason: null}}
```

### ✅ STRENGTHS

- **S1. 探頭偵測提示的優先序正確,而且寫出了理由。** :141-145 先比對「已儲存的設定是否為會配發 IP 的狀態＋畫面上這個 IP」,再看是否被拒,並說明「探頭偵測連的是畫面上的 IP」。這與 settings_dialog.py:1578-1589(用 `self.work` 中編輯後的 `d.ipv4` 呼叫 `station.scan`)相符。AC-6 ③、④ 兩種情況都涵蓋,規格書 999 與驗收欄逐字同步。
- **S2. `rc=0; "$STOP_HELPER" || rc=$?` 在 `set -euo pipefail` 下正確。** setup-bootp.sh:11 開啟 `set -e`;位於 `||` 左側的命令失敗不會觸發中止,`rc=$?` 取得的是停止程式的結束碼。停止程式以 `exec` 執行 pkill(03-bootp.sh:87),結束碼不會被 shell 改寫。`rc=0` 先初始化,`set -u` 下也不會出錯。
- **S3. 15 秒的理由可以驗證。** :117 引用重新開機時最長的請求間隔 10.8 秒,AC-7 也加上 B 重新開機的情況,第 4 輪 N2 提到的 WARNING 多出兩筆的問題已排除。
- **S4. 日誌與文件清單補齊。** :148 與規格書 999 都列入「逾時清除」;:160 列出 screens-device-settings 的 `set_flag`、`ProbeTile`、Signal 清單與主畫面截圖,與第 4 輪查到的四處相符。

## § 3. Critical Hotspots

本輪沒有 hotspot:最高 effective cost 1.05,cascade 都 ≤ 2(shortcut table「1-5 / ≤3 視 case,通常無 hotspot」)。

| 項目 | 早解成本 | 晚解成本 | ratio |
|---|---|---|---|
| C1 被拒期間的判定規則(參考) | 0.1h | 現場漏檢後追溯量測紀錄、改程式與說明書,約 1d | ~80× |

## § 4. Effective Cost Matrix

| ID | Tier | Impact | Prob | Effective cost | Fix 成本 |
|---|:---:|:---:|:---:|:---:|:---:|
| C1 | 🟡 | 7 | 0.15 | 1.05 | 0.1h |
| N1 | 🟢 | 2 | 0.15 | 0.3 | <0.1h |
| N2 | 🟢 | 1 | 0.2 | 0.2 | <0.1h |
| **合計** | | | | **≈1.55** | **≈0.25h** |

成本趨勢:第 1 輪 ≈27.0 → 第 2 輪 ≈18.1 → 第 3 輪 ≈5.95 → 第 4 輪 ≈3.05 → 第 5 輪 ≈1.55,比第 4 輪下降約 49%。現在修約 0.25 小時。

## § 5. Decision Log

**第 4 輪 finding 在 rev 5 的實際狀態(已逐項驗證):**

| R4 ID | 狀態 | 驗證 |
|---|:---:|---|
| C1 正被拒絕時蓋掉尚未儲存 | ✅ fixed | :141-145 改為先比對畫面上的 IP 與已儲存設定,尚未儲存優先;AC-6 ③ 改為「提示設定尚未儲存,不提示被佔用,也不提示 RST」,另加 ④(:202);規格書 999 本文與驗收欄同步。與 settings_dialog.py:1578-1589 相符,不再違反 DSC-23-A1。 |
| N1 RST 條件的「目前沒有被拒」無效 | ✅ fixed | :143 與規格書 999 改為「最近 60 秒沒有收到這台的 BOOTP 請求」,不論是否被拒、不論狀態。殘留:資料來源沒有寫明(本輪 N1)。 |
| N2 10 秒太短、連上但被拒的畫面未定義 | ✅ fixed | :117 與規格書 999 改為 15 秒並寫明理由;:118 定義被拒期間的方塊。殘留:「不判定」用詞有歧義(本輪 C1),且位置放在恢復清單中(本輪 N2)。 |
| N3 逾時清除未列入日誌段與規格書 | ✅ fixed | :148、:119 與規格書 999 都列入「逾時清除」。規格書驗收欄的拔線項沒有寫日誌,但本文已規定,提案 AC-10 也有,不另列。 |
| N4 `|| true` 拿不到結束碼;結束碼 1 訊息過度斷言 | ✅ fixed | :61 改為 `rc=0; "$STOP_HELPER" || rc=$?`,:64 說明 `set -e` 不會中止(S2 已驗證);結束碼 1 改為「沒有找到 App 的 dnsmasq(App 可能沒在執行)」。 |
| N5 screens-device-settings 列錯項目 | ✅ fixed | :160 改列 `set_flag`、`ProbeTile`、Signal 清單與 `app-main-error-flags.png`,設定頁的部分改寫在畫面設計規格。 |

- 本輪新拍板:無,全部為 `no_decision`。
- 依據紀錄(非決定):ARP 事件也會更新 `last_seen`、`last_request`(arpwatch.py:52、store.py:86-90);偵測不到在主畫面算設備異常(main_window.py:1306-1310、1374);DSC-15 的「不判定」是「不計入整片判定」(規格書:857)。

## § 6. Verdict + Next Round Focus

- **Status:** ship-as-is。沒有 BLOCKER。第 4 輪 6 項全部修好;有 1 項新的 CONCERN,來自 rev 5 新增的句子。
- **Recommend:** 簽核前修 C1,約 0.1 小時:「不判定」改為「以設備異常計(JDG-04),整片為設備異常」,AC-11 加上主畫面連得上的情況。N1、N2 可在同一次修正中處理,不需要再審。
- **Next Round Focus:** 本輪是最後一輪,不再做文件審查。M2/M3 完成後跑 V7 spec-compliance-review,重點如下:
  1. AC-11 連得上(佔用者在線)時,整片為設備異常、不出現合格;
  2. AC-6 ①～④ 的提示文字與 RST 條件的資料來源;
  3. AC-7 在 B 重新開機時的 WARNING 筆數;
  4. 逾時清除後 DSC-20 是否用過期的 `seen_ip` 又叫人按 RST。

(§ 7 Mental Lens Reflection:本輪沒有 BLOCKER,不觸發。)
