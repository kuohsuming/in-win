---
target: docs/pm/probe-position/PROPOSAL.md
target_rev: 67e1192 (rev 4)
date: 2026-10-15
reviewer: spectra-review (v2.0)
iteration: 4
verdict: ship-as-is
schema_version: enhanced-v1
contract_version: spectra-contract-v1
mode: pm-skill-generic-doc
---

> 💡 spectra-review v2.0 active(Minerva 4 能力 framework)。若想用原版簡潔版,用 `/spectra-review --lite <target>`。

🎯 Mode: PM Skill — Generic doc (target: docs/pm/probe-position/PROPOSAL.md)

# Spectra-Review Round 4 — docs/pm/probe-position/PROPOSAL.md

本輪範圍與限制:
- 對象是 rev 4(commit 67e1192)。先逐項驗證第 3 輪 9 個 finding 的修正,再找新問題,重點放在 rev 4 改動的段落:§5.2 新增「設備稱呼」與顯示名稱的分工、§5.5 IP 不符改為附加標示、§5.1 `default_config` 改為「探頭 1～4」、§8 升級順序與 `load_names` 容錯、POS-07 納入 P3D-03 訊息修訂、§5.8 降版列。
- 對照來源:規格書 3.13 POS-01～09(規格書:1074-1092)、P3D-03(規格書:1044)、DSC-20(規格書:946),以及程式碼、測試、`sql/in-win.sql`、`installer/`。
- 第 3 節 PO 決定不重新討論;第 10 節只檢查依賴段落是否清楚(本輪無問題)。
- SKILL 提到但本 repo 沒有的檔案略過。依呼叫者指示只寫 F1,不更新 F2 與 decision-log。

## § 1. Mental Lens

- **Claim → Evidence → Verdict**:rev 4 新增的程式描述逐句對照原始碼,例如「`default_config` 目前為左、左中、右中、右」(lan.py:51-54)、「App 帳號已有 SELECT、INSERT、UPDATE」(in-win.sql:207)、「`sync.startup` 讀不到資料庫時走沿用定義檔路徑」(sync.py:103-110)、「舊版讀定義檔不驗證」(definition.py:22-32)、「舊版 Schema 不允許探頭額外欄位」(bootp.py:134、dl-en1.schema.json probe `additionalProperties: false`)。
- **Cross-section consistency**:§5.2 兩種稱呼的使用處,逐一對照 §5.1、§5.3、§5.5、§5.6、§5.7 的範例;§5.5 附加標示與 DSC-20、POS-05 對照;`default_config` 改名對照 tests/、docs/、installer/。
- **Anti-Bias**:F2 把第 3 輪全部標為 fixed,本輪不採信,逐項回到 rev 4 原文與規格書確認。
- **Understand-not-argue**:rev 4 的修正都落在正確位置,文件已收斂。本輪只找到一個 rev 4 改動帶出的規格書矛盾,其餘是文字與文件同步。

### 第 3 輪修正驗證

| R3 ID | 結果 | 依據 |
| --- | --- | --- |
| C1 | 成立 | IP 不符改為附加標示,方塊內容照表顯示(PROPOSAL.md:245),優先表剩 5 列(237-243)。附加標示與「偵測不到」同時成立時沒有寫明,和 DSC-20 衝突,見本輪 C1 |
| C2 | 成立 | §5.2 新增「設備稱呼」(PROPOSAL.md:159);§5.1 衝突訊息(140)、§5.3 選單(181)、變更清單(206)都改用設備稱呼;規格書 POS-02 同步(規格書:1075)。POS-02 的驗收範例沒有跟著改,見 N5 |
| C3 | 成立 | `default_config` 改為「探頭 1～4」(PROPOSAL.md:92),§6 lan.py 列已加(303),POS-09 同步並補上預設點名稱條件(規格書:1082)。tests/ 沒有任何測試斷言預設名稱(test_lan.py:177-178 只檢查 max_probes),改名不會讓既有測試失敗。文件中寫死舊預設名稱的地方沒有點名,見 N2 |
| C4 | 成立 | §8 升級順序與 1146 容錯(PROPOSAL.md:346);§6 store.py 列(304);§9(359)。`in-win.sql` 的既有 ALTER 都用 information_schema 判斷,`CREATE USER IF NOT EXISTS`,重跑安全(in-win.sql:78-94、205) |
| N1 | 成立 | 第 4 列含「未設定允收標準」(PROPOSAL.md:242) |
| N2 | 成立 | §5.1 與 §5.3 同一個訊息(PROPOSAL.md:142、183),與 POS-01 文字一致 |
| N3 | 成立 | 原本的點改用 j(PROPOSAL.md:189) |
| N4 | 成立 | 降版列寫明啟動錯誤、所有立即儲存失敗、不只帶位置的那台(PROPOSAL.md:282),對照 sync.py:36-47 與 bootp.py:134 正確 |
| N5 | 成立 | §5.6 與 POS-07 的 P3D-03 訊息逐字相同(PROPOSAL.md:262、規格書:1080)。P3D-03 條文本身與 changeset 沒有同步,見 N4 |

## § 2. 4-Tier Findings

### 🔴 BLOCKERS — 落地前必修

(none found)

### 🟡 CONCERNS — 應修

#### C1. IP 不符附加標示沒有排除「偵測不到」,與 DSC-20「偵測不到優先」衝突

**📛 命名(Identify):** §5.5 寫「IP 不符(DSC-20)不是方塊狀態,而是附加標示:該台每個方塊加警示色外框與小標『IP 不符』,方塊內容仍依上表顯示…頂端沿用 DSC-20 的提示…與上表任何一列同時成立時仍顯示」(PROPOSAL.md:245)。

**📣 主張(Assert):**
- 規格書 DSC-20 寫「偵測不到(DEV)時以偵測不到的標示優先,頂端提示仍顯示」(規格書:946);POS-05 也寫「DSC-20 不變」(規格書:1078)。也就是方塊上只顯示偵測不到,只有頂端同時顯示 IP 不符。
- 現行程式照這個規則做:偵測不到時邊框為紅色、不顯示「IP 不符」字樣(main_window.py:426-441 的 `if self.seen_ip and not down`)。
- rev 4 的附加標示對「方塊」沒有任何例外;句末「與上表任何一列同時成立時仍顯示」在語法上屬於頂端提示,但很容易被讀成方塊也一樣。照字面實作,偵測不到的方塊會同時有紅色異常與警示色外框加「IP 不符」,兩種外框顏色互相衝突,也違反 DSC-20。
- 這不是罕見情況:`seen_ips` 保存最後一次 ARP 看到的 IP,設備斷線後仍在(main_window.py:1090-1094),所以斷線時帶著舊的 IP 不符是現行程式特地處理的分支。
- 這是第 3 輪 C1 的修正帶出來的:原本 IP 不符排在偵測不到之後,優先順序自然解決;改成附加標示後少了這一條。
- Impact 3/10 / Probability 0.4 → 1.2
- Evidence: PROPOSAL.md:245;規格書:946、1078;app/flatness/ui/main_window.py:426-441、1086-1103
- Cross-Module Impact:main_window 方塊樣式、M3 UI 測試、DSC-20 驗收
- Phase-aware:M3 實作前要定案。

**🎯 追求(Pursue):** §5.5 附加標示一段補一句:「偵測不到(第 2 列)時方塊不加 IP 不符標示,以偵測不到優先(DSC-20);頂端兩種提示都顯示。」整台設備異常(第 3 列)是否同樣處理一併寫明(建議同樣不加,與現行 `down` 一致)。

**📊 Decision Tree:**

| Option | 動作 | 成本 | 備註 |
| --- | --- | --- | --- |
| A | 不修 | 0 | M3 可能做出雙外框,與 DSC-20 驗收不符 |
| B | 現在修(補一句例外) | 0.2h | 推薦 |

**📍 推薦:** Option B
**🔮 反事實:** 第 2 台斷線且 ARP 留著舊 IP,4 個方塊同時顯示紅色「DL-EN1 偵測不到」與黃色「IP 不符」框,作業員不知道先處理哪一個;DSC-20 驗收失敗。

```yaml
- {tier: 🟡 CONCERN, id: C1, name: "IP 不符附加標示未排除偵測不到,與 DSC-20「偵測不到優先」衝突", evidence: ["PROPOSAL.md:245", "規格書:946", "規格書:1078", "app/flatness/ui/main_window.py:426-441"], severity: {score: {value: 1.2, default: 1.2, override: null}, band: low, semantic: how_bad}, fix_economics: {difficulty: {value: 0.1, default: 0.1, override: null}, roi: {value: 12.0, default: 12.0}, resource_estimate: {value: "0.2h", default: "0.2h", override: null}}, cross_impact: {affected_modules: [main_window, M3 測試, DSC-20], cascade_depth: 2, dependency_chain: "附加標示規則 → 方塊樣式 → DSC-20 驗收"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 3, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 補偵測不到例外}], recommended_option: B, counterfactual: "偵測不到方塊出現雙外框,違反 DSC-20"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {3: {value: 1.5, default: 1.5, override: null}}}, po_decision: {status: no_decision}}
```

### 🟢 NITS — 可選 polish

```yaml
- {tier: 🟢 NIT, id: N1, name: "「維修中・IP 不符(同現在)」順序與現行相反,現行為「IP 不符・維修中」", evidence: ["PROPOSAL.md:245", "app/flatness/ui/main_window.py:439"], pursue: "改為「IP 不符・維修中」,或拿掉「同現在」", severity: {score: {value: 0.2, default: 0.2}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N2, name: "default_config 改名後,文件中寫死「左、左中、右中、右」為預設的地方沒有點名", evidence: ["PROPOSAL.md:92", "PROPOSAL.md:315", "docs/manual/操作說明書.md:374", "docs/ui/screen-design-spec.md:319"], pursue: "§6 文件列或 M5 補「操作說明書 7.4 步驟 3、畫面設計規格 5.10 的預設探頭名稱改為探頭 1～4」", severity: {score: {value: 0.3, default: 0.3}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N3, name: "POS-09 驗收「新安裝 → 3D 標籤『排1 點2』」:以 installer/dl-en1.json 新安裝時探頭為左…右,不觸發自動帶入,照驗收步驟做不出「排1 點2」", evidence: ["規格書:1082", "installer/dl-en1.json", "PROPOSAL.md:92"], pursue: "驗收改為「新增的 DL-EN1(探頭 1～4)選第 1 排第 2 點 → 3D 標籤『排1 點2』」,新安裝只驗排頭「排1」", severity: {score: {value: 0.3, default: 0.3}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N4, name: "P3D-03 條文未加註被 POS-07 修訂,其驗收「1 台 4 個探頭 → 拒絕;2 台各 2 個 → 可開啟」在 5×5 下已不成立;changeset 的 requirements 未列 P3D-03;§6 plate3d 列未提訊息(model.py 三處)", evidence: ["規格書:1044", "規格書:1080", "docs/release/changes/2026-10-15-probe-position-requirements.md", "PROPOSAL.md:311", "app/flatness/plate3d/model.py:92,157,165"], pursue: "P3D-03 比照 P3D-05 加「(2026-10-15 POS-07 提議修訂訊息與驗收,待確認)」;changeset 補 P3D-03;§6 plate3d 列加「P3D-03 訊息」", severity: {score: {value: 0.4, default: 0.4}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N5, name: "POS-02 驗收「已由前排 右使用」不是條文自己規定的設備稱呼格式", evidence: ["規格書:1075", "PROPOSAL.md:159"], pursue: "驗收改為「已由 第 1 台 前排 右 使用」", severity: {score: {value: 0.2, default: 0.2}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N6, name: "§5.2 說變更清單用設備稱呼,但現行清單以設備為標題、探頭行為「探頭 ID n「名稱」…」;未寫既有的名稱、允許誤差行是否也改格式(test_ui.py:183、操作說明書:544 依賴現行文字)", evidence: ["PROPOSAL.md:159", "PROPOSAL.md:206", "app/flatness/lan.py:638-647", "tests/test_ui.py:183"], pursue: "寫明只有新增的位置行用設備稱呼,既有探頭行格式不變(或寫明一起改並列入 M2 測試)", severity: {score: {value: 0.3, default: 0.3}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N7, name: "未寫設定頁儲存時 names 何時為 None;若每次儲存都傳名稱,未執行 SQL 時設定頁任何儲存都因資料表不存在而失敗(1146 容錯只涵蓋讀取)", evidence: ["PROPOSAL.md:111", "PROPOSAL.md:207", "PROPOSAL.md:346"], pursue: "§5.3 寫明「名稱有變更時才傳 names,否則為 None」,§8 註明未執行 SQL 前改名稱會儲存失敗", severity: {score: {value: 0.3, default: 0.3}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N8, name: "POS-07 標籤寫「排名稱 位置名稱」,提案用顯示名稱(含重名時加「(第 N 台 探頭 id)」),規格書沒有重名規則", evidence: ["規格書:1080", "PROPOSAL.md:157", "PROPOSAL.md:252"], pursue: "POS-07 標籤改為「顯示名稱(排名稱 位置名稱;重名時加第 N 台與探頭 ID)」", severity: {score: {value: 0.2, default: 0.2}}, po_decision: {status: no_decision}}
```

### ✅ STRENGTHS

- 「顯示名稱」與「設備稱呼」分工清楚:給作業員看的地方用位置,設定頁用「哪一台的哪一個探頭」,§5.1、§5.3 的範例都改對,第 3 輪的自我指涉問題完整消除。
- `default_config` 改為「探頭 1～4」同時解決自動帶入與「不依順序推定位置」兩件事,並明確排除 `installer/dl-en1.json`;既有測試不受影響。
- §8 升級順序把「缺表(1146)」與「資料庫無法連線」分開處理,理由寫明(避免維修中設備消失、設定頁唯讀),且 `inspection_point` 寫入失敗走既有暫存補寫,不會遺失資料。
- 降版列以實際程式行為描述影響範圍(不只帶位置的那台),並給出可操作的降版前步驟。

## § 3. Critical Hotspots

本輪沒有達到 hotspot 門檻的 finding(C1 effective cost 1.2、cascade_depth 2)。

## § 4. Effective Cost Matrix

| ID | Impact | Prob | Effective cost | 修正成本 |
| --- | :---: | :---: | :---: | :---: |
| C1 | 3 | 0.4 | 1.2 | 0.2h |
| N1–N8 | — | — | 合計約 2.2 | 合計約 1h(含規格書 POS-02、POS-07、POS-09、P3D-03 文字) |
| **總計** | | | **約 3.4**(45 → 15.9 → 9.3 → 3.4) | **約 1.2h,全部是文字修訂** |

本輪 tally(供 F2 append):Round 4|2026-10-15|BLOCKER 0|CONCERN 1|NIT 8|STRENGTH 4|ship-as-is。

## § 5. Decision Log

- 本輪沒有新的 PO 決定,所有 finding 的 `po_decision` 都是 `no_decision`。
- 沿用的前提:第 3 節 11 項 PO 決定;第 10 節 4 點仍延後給 PO,依賴段落清楚。
- 第 3 輪 9 項全部成立,沒有重開。C1 是 R3-C1 修正帶出的新問題;N2～N5 是 rev 4 規格書與文件同步的尾巴。

## § 6. Verdict + Next Round Focus

- **Status:** ship-as-is(BLOCKER 0、CONCERN 1、NIT 8、STRENGTH 4)
- **Recommend:**
  - 送 PO 簽核前修 C1(一句話)。N3、N4、N5、N8 牽涉規格書條文的驗收或文字,建議簽核前一併修,避免簽核後再改。
  - N1、N2、N6、N7 可在 M1～M2 開工前順手處理。
- **Convergence:** effective cost 45 → 15.9 → 9.3 → 3.4,連續兩輪沒有 BLOCKER,本輪只有一個 CONCERN 且是單句修訂。不需要第 5 輪全面審查;修完後只需確認 §5.5 那一句與規格書四處驗收文字。
- **Next Round Focus(若有):** 無全面審查需求。

(本輪沒有 BLOCKER,不附 § 7 Reflection。)
