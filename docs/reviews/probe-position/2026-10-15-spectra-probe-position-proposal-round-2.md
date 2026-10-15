---
target: docs/pm/probe-position/PROPOSAL.md
target_rev: 8c6e600 (rev 2)
date: 2026-10-15
reviewer: spectra-review (v2.0)
iteration: 2
verdict: ship-as-is
schema_version: enhanced-v1
contract_version: spectra-contract-v1
mode: pm-skill-generic-doc
---

> 💡 spectra-review v2.0 active(Minerva 4 能力 framework)。若想用原版簡潔版,用 `/spectra-review --lite <target>`。

🎯 Mode: PM Skill — Generic doc (target: docs/pm/probe-position/PROPOSAL.md)

# Spectra-Review Round 2 — docs/pm/probe-position/PROPOSAL.md

本輪範圍與限制:
- 對象是 rev 2(commit 8c6e600)。先逐項驗證第 1 輪 19 個 finding 的修正,再找新問題,重點放在 rev 2 新增的內容:定義檔 `position_names`、顯示名稱規則、狀態優先順序表、`inspection_point` 新欄位、生命週期表。
- 對照來源:規格書 3.13 POS-01～09、POS-G1/G2、POS-A1～A5,以及 DEF-01～DEF-10、3.7.1(含內嵌 JSON Schema)、EDT-03/05/06、DSC-06/09/12/14/15/18/20、UPL-*、UI-04/11、P3D-02～05、EXP-03、DAT-*、NFR-01;程式碼見各 finding 的 evidence。
- 第 3 節 PO 決定不重新討論。第 10 節是明文延後給 PO 的事項,只檢查「依賴它的段落有沒有標明」。
- SKILL 提到但本 repo 沒有的檔案(docs/CONTEXT.md、docs/index.md、pm-skill-proposal.md、state.md、decision-log.md)略過。
- 依呼叫者指示只寫 F1;F2(`_summary-probe-position-proposal.md`)與 decision-log audit entry 沒有更新,本輪的 tally 列見 § 4,由呼叫者決定是否補進 F2。

## § 1. Mental Lens

- **Claim → Evidence → Verdict**:rev 2 新增的每一句程式行為描述都對照原始碼,例如「`lan.replace` 複製整個 config」「`flatness_sim.inspection_point` 用 LIKE 建立」「舊版會拒絕新定義檔並沿用上一版」「`sync.apply(..., names=)`」。
- **Cross-section consistency**:對照提案 §5.1/§5.3/§5.5/§5.7/§10 彼此之間,以及提案與規格書 POS-01～09、DSC-20、UI-11。
- **Anti-Bias**:第 1 輪全部標為已修正,這一點本身就要驗證。每項都回頭看 rev 2 的實際文字與程式碼,不採信 F2 上的 ✅。
- **Understand-not-argue**:rev 2 的方向正確,修正也大多到位。以下 finding 都是可以用文字修訂補上的缺口,不需要改設計。

### 第 1 輪修正驗證

| R1 ID | 驗證結果 | 依據 |
| --- | --- | --- |
| B1 | 成立 | §5.1 兩層檢查表(PROPOSAL.md:133-140)與 lan.py:290-330 `groups`、lan.py:265-270 單台 `bootp.validate` 的分工一致;上傳時與維修中設備衝突交給 `lan.validate`,符合 `import_definition` 只把檔案中的設備設為使用中、維修中原樣保留(lan.py:514-537) |
| B2 | 成立(留有邊界情況,見 N1) | §5.3 自動帶入三個條件(PROPOSAL.md:182-188),`description` 維持必填(PROPOSAL.md:92),規格書 POS-09 同步 |
| B3 | 成立(衍生新問題 C2) | §5.3 預覽與儲存(PROPOSAL.md:199-203)涵蓋 `Preview.empty`(lan.py:557)、`is_dirty`(settings_dialog.py:587-590)、`MemoryStore` 快照(store.py:117-129);§6 已列 sync.py |
| C1 | **部分成立,重開為 C1** | 已補維修中方塊、優先順序、`set_flag("dev"/"maint")`;但漏了「整台設備異常」狀態,而且優先順序表的適用範圍與 DSC-20 衝突 |
| C2 | 成立(衍生新問題 C2) | 名稱寫入定義檔 `position_names`(PROPOSAL.md:112-120);資料庫無法連線時 `sync.startup` 讀的正是這個檔(sync.py:107-110) |
| C3 | 成立 | §5.2 顯示名稱規則與重名加註 |
| C4 | 成立(grep 驗收不足,見 N4) | §6 條文清單已含 DSC-20、UI-11、EXP-03、3.7.1、DSC-09/12、P3D-04、CAL-01/02;文件含 screens-device-settings.md;changeset 檔存在 |
| C5 | **提案已修,規格書未同步,重開為 C3** | PROPOSAL.md:225 改為以「列」計算,規格書 POS-04 仍寫「以『排』為單位不變」 |
| C6 | 成立 | §5.1 保存 `pos_row`/`pos_point`/`row_name`,§5.7 只讀紀錄,§10-1 寫出另一做法的下游影響 |
| C7 | 成立 | §5.8 生命週期表;`lan.replace` 深複製 config(lan.py:470)、`_on_field_edited` 依表格列重建 probes(settings_dialog.py:1189-1199)與表中描述一致 |
| C8 | 成立 | §5.3 選單規則(PROPOSAL.md:174-180)含先點後排、改排衝突、已滿、未儲存的編輯 |
| N1～N8 | 全部成立 | 「第幾台」、「排與點名稱區塊」、POS-07 範例、CHECK 與 ON UPDATE、§5.7 第二工作表與 MAC 標題、`_entry_issues` 比對式、M1～M4 完成前不部署、changeset 路徑 |

## § 2. 4-Tier Findings

### 🔴 BLOCKERS — 落地前必修

(none found)

第 1 輪的 3 個 BLOCKER 都已正確修正。本輪找到的問題都可以用文字修訂解決,不會造成資料遺失,也不會讓實作方向錯誤。

### 🟡 CONCERNS — 應修

#### C1. 狀態優先順序表漏了「整台設備異常」;「只顯示最前面的一個」的適用範圍不清,照字面會違反 DSC-20

**📛 命名(Identify):** §5.5 寫「一個方塊同時符合多個狀態時,依下列優先順序只顯示最前面的一個」(PROPOSAL.md:231),表格有 5 列,欄位包含「方塊、結果橫幅、頂端提示」(PROPOSAL.md:233-239)。

**📣 主張(Assert):**
- **漏了一個狀態**:`_on_detected` 有三種整台狀態,表格只列了偵測不到。
  - `not s.reachable`:偵測不到(main_window.py:1232-1238)。
  - `s.error`:「整台設備異常:連得上,但不能量測(本機錯誤、探頭台數超出定義 DEF-06)」(main_window.py:1239-1244)。這一種表格裡沒有。
  - 改成一台對多個方塊之後,整台異常同樣要標在分散在各排的方塊上(POS-05 的精神),頂端也要列出是哪一台。第 1 輪 C1 建議的順序「偵測不到 > 整台異常 > 維修中 > IP 不符 > 探頭異常」,rev 2 沒有採用整台異常這一項,也沒有說明理由。
- **與 DSC-20 衝突**:
  - DSC-20 是已簽核的條文:「偵測不到時以偵測不到的標示優先,**頂端提示仍顯示**」;適用範圍是「使用中**或維修中**」的設備(規格書:946)。
  - 表格把「頂端提示」放在同一列,又寫「只顯示最前面的一個」。照字面讀:
    - 偵測不到加 IP 不符(DSC-20-A1 指出這正是最常見的組合),IP 不符的頂端提示會被吃掉。
    - 維修中加 IP 不符,方塊上只顯示「維修中」。現行程式會顯示「IP 不符・維修中」(main_window.py:439),DSC-20 也要求維修中設備標示 IP 不符。
  - §6 對 DSC-20 只說要改「第 N 排」的文字,沒有提到這個行為改變。
- Impact 5/10 / Probability 0.6:M3 照表實作後,UI 測試會與 DSC-20 的驗收條件互相矛盾。
- Evidence: PROPOSAL.md:231-241;app/flatness/ui/main_window.py:1232-1244、425-457、1085-1105;規格書 DSC-20(946)、POS-05(1078)
- Cross-Module Impact:main_window(方塊、`set_flag`)、DSC-20 驗收、M3 UI 測試
- Phase-aware:M3 才實作,但表格是 M3 測試的依據,簽核前定案最便宜。

**🎯 追求(Pursue):**
1. 表格加入「整台設備異常(`s.error`,例:探頭台數超出定義)」,放在偵測不到之後:方塊顯示「設備異常」與原因,橫幅列「第 N 台 名稱 <原因>」,頂端併入 `set_flag("dev")`。
2. 把「只顯示最前面的一個」限定為**方塊**的顯示。另外寫明:
   - 頂端提示**各自獨立累加**(IP 不符的頂端提示不受優先順序影響,DSC-20)。
   - 維修中加 IP 不符時,方塊顯示「維修中・IP 不符」(沿用現行做法)。或者明寫這是對 DSC-20 的修訂,列進 §6 的修訂方式。

**📊 Decision Tree:**

| Option | 動作 | 成本 | 備註 |
| --- | --- | --- | --- |
| A | 不修 | 0 | M3 依字面實作,DSC-20 驗收失敗,或實作者自行決定 |
| B | 現在修(補一列並限定範圍) | 0.5h | 推薦 |

**📍 推薦:** Option B
**🔮 反事實:** 不修的話,第 2 台 IP 被改錯而偵測不到時,方塊顯示「DL-EN1 偵測不到」,但頂端沒有「請按住 RST 3 秒」的提示。作業員不知道原因,正是 DSC-20-A1 描述的錯誤行為。

```yaml
- {tier: 🟡 CONCERN, id: C1, name: "狀態優先表漏整台設備異常;優先序範圍不清,與 DSC-20 頂端提示及維修中 IP 不符衝突", evidence: ["PROPOSAL.md:231-241", "app/flatness/ui/main_window.py:1239-1244", "app/flatness/ui/main_window.py:439", "規格書 DSC-20"], severity: {score: {value: 3.0, default: 3.0, override: null}, band: med, semantic: how_bad}, fix_economics: {difficulty: {value: 0.5, default: 0.5, override: null}, roi: {value: 6.0, default: 6.0}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [main_window, spec DSC-20], cascade_depth: 2, dependency_chain: "狀態表 → M3 方塊/頂端實作 → DSC-20 驗收"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 3, estimated_rework_cost: medium}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 補列並限定範圍}], recommended_option: B, counterfactual: "偵測不到加 IP 不符時頂端不提示 RST,DSC-20-A1 重現"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {3: {value: 4.0, default: 4.0, override: null}}}, po_decision: {status: no_decision}}
```

#### C2. 定義檔 `position_names` 的名稱從哪裡來沒有定義:啟動與三條立即儲存的路徑會產生不含名稱的定義檔

**📛 命名(Identify):** §5.1 寫「`sync.render` 產生定義檔時,在頂層加入選填欄位 `position_names`」(PROPOSAL.md:112);§5.3 寫「`sync.apply(..., names=)` 在既有的同一個資料庫交易內寫入名稱,再寫定義檔(含 `position_names`)」(PROPOSAL.md:203)。

**📣 主張(Assert):**
- `sync.render(devices, equip_net)` 目前只接收設備清單(sync.py:36)。呼叫它的地方有兩個:
  - `sync.startup`:每次啟動都呼叫(sync.py:112)。
  - `sync.apply`(sync.py:138)。`backend.apply` 有 4 個呼叫端,其中 3 個不經過名稱編輯:
    - 校準(CAL-05,settings_dialog.py:1129)
    - 刪除設備(DSC-18,settings_dialog.py:1322)
    - 上移／下移(DSC-17,settings_dialog.py:1358)
- 提案只寫了「改名稱時傳 `names=`」,沒有寫「每次產生定義檔都要放入目前的名稱」,也沒有寫 `startup` 要從資料庫讀名稱(`store.load()` 只回傳設備,store.py:63、209)。
- 照字面實作的結果:
  - 只要做一次校準、刪除或排序,或者重新啟動一次,定義檔就會產生不含 `position_names`(或只含預設名稱)的內容。
  - `_write` 依文字比對,內容不同就備份並覆寫(sync.py:63-69)。結果是定義檔中的名稱被洗回預設,而且每次都多一份備份。
  - 之後資料庫無法連線時(DSC-06),排頭與 3D 標籤會變回「排1」。rev 2 為了修第 1 輪 C2 才加入這個機制,這樣它就失效了。§7「資料庫無法連線時重新啟動 App,排名稱與設定時相同」的驗收也會失敗。
- Impact 5/10 / Probability 0.6
- Evidence: PROPOSAL.md:112-120、203、320;app/flatness/sync.py:36、63-69、107-121、131-164;app/flatness/ui/settings_dialog.py:1129、1322、1358;app/flatness/store.py:63、209
- Cross-Module Impact:sync(render/startup/apply)、store(讀名稱)、backend(名稱快取)、所有 apply 呼叫端
- Phase-aware:M1 定 `sync`/`store` 介面時就要決定。

**🎯 追求(Pursue):** 在 §5.1 寫明:
1. `render(devices, names, equip_net)` 一律輸出目前的 `position_names`(全部預設時也輸出,或一律省略預設值,擇一,讓文字比對穩定)。
2. `startup` 在同一次讀取中由 `store.load()`(或新增的 `store.load_names()`)取得名稱。
3. `apply(..., names=None)` 的 `None` 表示「名稱不變,寫檔時沿用 backend 快取或資料庫中的目前名稱」,不是「不輸出名稱」。
4. M1 測試加一條:先改名稱並儲存,再校準一個探頭,定義檔仍含自訂名稱。

```yaml
- {tier: 🟡 CONCERN, id: C2, name: "render 的名稱來源未定義,校準/刪除/排序/啟動會洗掉定義檔中的名稱", evidence: ["PROPOSAL.md:112", "PROPOSAL.md:203", "app/flatness/sync.py:36", "app/flatness/sync.py:112", "app/flatness/ui/settings_dialog.py:1129", "app/flatness/ui/settings_dialog.py:1322", "app/flatness/ui/settings_dialog.py:1358"], severity: {score: {value: 3.0, default: 3.0, override: null}, band: med, semantic: how_bad}, fix_economics: {difficulty: {value: 0.5, default: 0.5, override: null}, roi: {value: 6.0, default: 6.0}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [sync, store, backend, settings_dialog], cascade_depth: 3, dependency_chain: "apply/startup → render → dl-en1.json → DSC-06 離線名稱"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 1, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 寫明 render 一律帶目前名稱}], recommended_option: B, counterfactual: "校準一次後定義檔名稱回預設;MySQL 停機重開時排頭顯示排1"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {1: {value: 3.5, default: 3.5, override: null}}}, po_decision: {status: no_decision}}
```

#### C3. 規格書 POS-04 與提案 §5.4 對 UI-11 縮放單位的說法互相矛盾(第 1 輪 C5 只修了提案)

- **Assert:**
  - 規格書 POS-04 結尾:「UI-11 的縮放規則以『排』為單位**不變**」(規格書:1077)。
  - 提案 §5.4:「以『列』為單位計算,每個位置排算一列,『未設定位置』區每 5 個探頭算一列」(PROPOSAL.md:225)。
  - 提案 §0 規定「兩者不一致時以規格書為準」(PROPOSAL.md:11)。所以實作者照規則會採用規格書,把整個「未設定位置」區當成一排計算,第 1 輪 C5 的問題(升級後 mosa 全部未定時高度被低估,main_window.py:943-969)又回來了。
  - 呼叫者也要求提案與規格書的 POS 文字必須一致。
- **Pursue:** POS-04 改為「UI-11 的縮放以『列』計算:每個位置排算一列,『未設定位置』區每 5 個探頭算一列;『至少 4 排不需捲動』改為『至少 4 列』」,並把 UI-11 列入簽核時要修訂的條文(§6 已列)。
- Evidence: 規格書:1077;PROPOSAL.md:11、225;app/flatness/ui/main_window.py:943-969
- Impact 4 / Prob 0.7 → 2.8

```yaml
- {tier: 🟡 CONCERN, id: C3, name: "POS-04「UI-11 以排為單位不變」與提案「以列計算」矛盾", evidence: ["規格書:1077", "PROPOSAL.md:11", "PROPOSAL.md:225"], severity: {score: {value: 2.8, default: 2.8, override: null}, band: low, semantic: how_bad}, fix_economics: {difficulty: {value: 0.3, default: 0.3, override: null}, roi: {value: 9.3, default: 9.3}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [spec POS-04, UI-11, main_window._fit], cascade_depth: 2, dependency_chain: "規格書優先 → _fit 實作"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 3, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 同步 POS-04}], recommended_option: B, counterfactual: "依規格書實作,升級當天未設定位置區被當成一排,出現捲軸或方塊過小"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {3: {value: 3.0, default: 3.0, override: null}}}, po_decision: {status: no_decision}}
```

#### C4. 依賴 §10 的段落沒有全部標明「依 §10」,PO 改選其他做法時會留下過時的內容

- **Assert:**
  - §0 承諾「PO 改選其他做法時,第 5 節標註『依 §10』的段落要跟著改」(PROPOSAL.md:13)。但 rev 2 只有 §5.1(PROPOSAL.md:144)與 §5.3(PROPOSAL.md:190)有這個標註。
  - 以下段落也依賴 §10,卻沒有標註:
    - **§10-1(保存位置)**:
      - §5.7 第一、二點:「依 §5.1 保存的 `pos_row`…排列」(PROPOSAL.md:260-261)
      - §6 `sql/in-win.sql`、`store.py`、`results.py` 三列的 `inspection_point` 部分(PROPOSAL.md:294、298、301)
      - §8 M1 的「`inspection_point` 新欄位」與 M4 的「量測紀錄寫入位置」(PROPOSAL.md:331、334)
    - **§10-3(Excel 標題)**:
      - §5.7 第三點「欄位標題與『不合格點』用顯示名稱」(PROPOSAL.md:262)
      - §5.2「使用處」中的「Excel 欄位標題」(PROPOSAL.md:155)
    - **§10-4(HTML 原型)**:§6 文件清單與 M5(PROPOSAL.md:308、335)
  - 如果 PO 對 §10-1 選「不保存」,依 §0 的規則只會改 §5.1 那一段,§6、§8、§5.7 會留下錯誤的工作項目。§10-1 本身描述的替代做法(`write_xlsx` 傳入目前設定)還要改 `ResultSink.export`(results.py:91-104)與 `MemorySink.export`(main_window.py:86-95),這兩處也沒有對應標註。
- **Pursue:** 在上述每一處加註「(依 §10 第 n 點)」;或把 §0 的規則改為「§10 每一點列出受影響的段落」,在 §10 各點後面加「影響:§5.7、§6 sql/store/results、§8 M1/M4」。
- Evidence: PROPOSAL.md:13、144、155、190、260-262、294-301、308、331-335、352-359
- Impact 3 / Prob 0.5 → 1.5

```yaml
- {tier: 🟡 CONCERN, id: C4, name: "依賴 §10 的段落未全部標「依 §10」", evidence: ["PROPOSAL.md:13", "PROPOSAL.md:260-262", "PROPOSAL.md:294-301", "PROPOSAL.md:331-334"], severity: {score: {value: 1.5, default: 1.5, override: null}, band: low, semantic: how_bad}, fix_economics: {difficulty: {value: 0.3, default: 0.3, override: null}, roi: {value: 5.0, default: 5.0}, resource_estimate: {value: "1h", default: "1h", override: null}}, cross_impact: {affected_modules: [proposal §5.7, §6, §8], cascade_depth: 2, dependency_chain: "PO 對 §10 的決定 → 實作範圍"}, phase_aware: {current_phase: 0, if_not_fixed_now_breaks_at: 0, estimated_rework_cost: low}, decision_tree: {options: [{id: A, action: 不修}, {id: B, action: 補標註或在 §10 列影響}], recommended_option: B, counterfactual: "PO 選不保存位置後,M1 仍 ALTER inspection_point"}, dependencies: {blocks: [], blocked_by: [], manual_blocks: []}, severity_decay: {phase_when_found: 0, by_phase: {1: {value: 2.0, default: 2.0, override: null}}}, po_decision: {status: no_decision}}
```

### 🟢 NITS — 可選 polish

```yaml
- {tier: 🟢 NIT, id: N1, name: "自動帶入條件的邊界:刪除中間探頭後「探頭 4」變成 ID 3,條件 1 不成立;條件 2 只比對編輯中的點名稱,點改過名(本次或之前已儲存)後,帶入的舊名稱「點2」在探頭移到第 3 點時不會更新", evidence: ["PROPOSAL.md:182-188", "app/flatness/ui/settings_dialog.py:1246-1258"], pursue: "條件 1 改為符合「探頭 \\d+」;條件 2 加上「或等於預設名稱 點{原點號}」,避免第 3 點的探頭叫「點2」", severity: {score: {value: 0.9, default: 0.9}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N2, name: "Excel 欄位排序的依據沒有寫到同一個探頭當日改過位置的情況(只寫了名稱取最後一筆)", evidence: ["PROPOSAL.md:261-262", "app/flatness/export.py:32-36"], pursue: "寫明排序位置也取當日最後一筆紀錄,與名稱一致", severity: {score: {value: 0.6, default: 0.6}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N3, name: "降版描述與程式不符:舊版在資料庫可用時,因 lan_device 帶有 row/point 而驗證失敗(bootp.py:134),改走 load_existing;load_existing 不驗證就直接使用新的定義檔(sync.py:94-100、113-116),不是「拒絕並沿用上一版」;「刪除名稱」在介面上做不到,也不需要(舊版不讀 plate_position_name)", evidence: ["PROPOSAL.md:276", "app/flatness/sync.py:94-116", "app/flatness/bootp.py:63", "app/flatness/bootp.py:134"], pursue: "改為「降版前把所有探頭位置設為未定並儲存;名稱與資料表可保留」,並描述舊版實際的行為", severity: {score: {value: 0.7, default: 0.7}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N4, name: "§7 的 grep 只抓得到 lan.py:154;漏掉 bootp.py:89「第 1～10 排」、lan.py:283「第 1～{ROWS} 排其中一排」、settings_dialog.py:40「保留該排」、settings_dialog.py:1299「這一排」、export.py:83「排」", evidence: ["PROPOSAL.md:323"], pursue: "改為 grep -rn '排' app/flatness --include=*.py 後逐筆分類,或至少加入「第[^\"]*排\\|該排\\|這一排\\|整排\\|每排」", severity: {score: {value: 0.8, default: 0.8}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N5, name: "同一個錯誤有兩種訊息格式:§5.1「第 N 列(ID n)位置須…」與 §5.3「探頭 n:位置須…」;佔用訊息「…(第 2 台 中排)探頭 1 使用」也不屬於 §5.2 宣稱套用到「檢查訊息」的顯示名稱規則", evidence: ["PROPOSAL.md:138", "PROPOSAL.md:140", "PROPOSAL.md:155", "PROPOSAL.md:177-179"], pursue: "統一為一種格式;§5.2 寫明佔用者用「第 N 台 名稱 位置名稱」(與 POS-02 範例「第 2 台 中排 左」一致)", severity: {score: {value: 0.6, default: 0.6}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N6, name: "§6 檔案對應有幾處不精確:MemorySink 在 main_window.py:72-95,不在 results.py;PointResult(main_window.py:47-58)要加位置與排名稱才能讓 to_record 取得;下載目前設定 _download(settings_dialog.py:1496,UPL-11)與 import_file 套用名稱沒有列出;initdb(DEF-10)匯入時是否帶入 position_names 沒有說明", evidence: ["PROPOSAL.md:301-303", "app/flatness/ui/main_window.py:47-95", "app/flatness/ui/settings_dialog.py:1460-1506", "app/flatness/initdb.py:17-22"], pursue: "§6 補列這幾處", severity: {score: {value: 0.6, default: 0.6}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N7, name: "§5.4「未設定位置區:位置未定的探頭(含維修中設備的探頭)…照常量測與判定」照字面會讓維修中探頭也量測,與 §5.5 第 1 列矛盾", evidence: ["PROPOSAL.md:223", "PROPOSAL.md:235"], pursue: "改為「使用中設備的探頭照常量測與判定;維修中設備的探頭依 §5.5 顯示維修中」", severity: {score: {value: 0.5, default: 0.5}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N8, name: "資料庫無法連線時,版面取自只含使用中設備的定義檔(sync.py:87-91、109-110),維修中設備的方塊會消失,原本佔用的位置變成空框;§5.8 只寫「設備與名稱都沿用定義檔」", evidence: ["PROPOSAL.md:275", "app/flatness/sync.py:87-110"], pursue: "§5.8 註明這是 DSC-15 既有的限制,不在本次範圍", severity: {score: {value: 0.4, default: 0.4}}, po_decision: {status: no_decision}}
- {tier: 🟢 NIT, id: N9, name: "規格書 3.7.1 內嵌 Schema 原本就缺 zero_offset、zeroed_at、tolerance(程式的 dl-en1.schema.json:43-47 有);只加 row/point/position_names,同步後仍然不一致", evidence: ["PROPOSAL.md:122", "規格書 3.7.1 內嵌 Schema probe 段", "app/flatness/dl-en1.schema.json:43-47"], pursue: "§5.1 寫明「以 app/flatness/dl-en1.schema.json 全文取代規格書內嵌 Schema」", severity: {score: {value: 0.5, default: 0.5}}, po_decision: {status: no_decision}}
```

### ✅ STRENGTHS

- 兩層檢查的分工與程式完全對應:`bootp.validate` 處理單台與檔案內(只含使用中),`lan.validate` 的 `groups` 處理使用中加維修中,訊息沿用 `occupied_text`。上傳時與維修中設備的衝突也放在正確的一層(lan.py:290-330、514-537)。
- 生命週期表中各列的程式依據都正確:替換時深複製 config(lan.py:470);刪除探頭時依表格列重建 probes(settings_dialog.py:1189-1199);已停用改回使用中時,由驗證標示衝突,符合 DSC-09 的「重新檢查是否重複」。
- `inspection_point` 擴充寫到了最容易漏的地方:`flatness_sim.inspection_point` 是用 LIKE 建立的,要另外 ALTER(in-win.sql:168-169、188-194);舊暫存檔沒有新欄位時視為 NULL(對應 `write_inspection` 讀取暫存檔的方式)。
- 顯示名稱規則同時處理了「同一台兩個點2」與「工程人員把位置名稱改成相同」兩種重名情況,而且明確排除主畫面方塊。這兩點都符合 POS-05 的 PO 決定。
- 定義檔帶 `position_names` 沿用了 DSC-06 既有的離線機制,沒有另外建立快取檔,維持單一來源。
- 部署限制(M1～M4 全部完成才上產線)明確避免了半套狀態。

## § 3. Critical Hotspots

| Finding | effective_cost | cascade_depth | 等級 | 早解 vs 晚解 |
| --- | :---: | :---: | :---: | --- |
| C2 名稱來源 | 3.0 | 3 | 無(1-5 且 ≤3) | 現在改一段文字約 1h;M1 之後才發現,要改 sync/store 介面與測試,約 0.5d |
| C1 狀態表與 DSC-20 | 3.0 | 2 | 無 | 現在約 1h;M3 UI 測試與 DSC-20 驗收衝突時才發現,約 0.5d |

本輪沒有達到 hotspot 門檻的 finding。第 1 輪的兩個 hotspot(B1、C4)確認已解。

## § 4. Effective Cost Matrix

| ID | Impact | Prob | Effective cost | 修正成本 |
| --- | :---: | :---: | :---: | :---: |
| C1 | 5 | 0.6 | 3.0 | 1h |
| C2 | 5 | 0.6 | 3.0 | 1h |
| C3 | 4 | 0.7 | 2.8 | 1h(含規格書) |
| C4 | 3 | 0.5 | 1.5 | 1h |
| N1–N9 | — | — | 合計約 5.6 | 合計約 1.5h |
| **總計** | | | **約 15.9**(第 1 輪約 45) | **約 5.5h(全部是文字修訂)** |

本輪 tally(供 F2 append):Round 2|2026-10-15|BLOCKER 0|CONCERN 4|NIT 9|STRENGTH 6|ship-as-is。

## § 5. Decision Log

- 本輪沒有新的 PO 決定。所有 finding 的 `po_decision` 都是 `no_decision`。
- 沿用的前提:第 3 節的 11 項 PO 決定;第 10 節 4 點維持延後給 PO,本輪只指出依賴它們的段落沒有完整標註(C4)。
- 第 1 輪的處理結果:R1-C1 部分重開為 C1(整台設備異常、DSC-20 範圍);R1-C5 因規格書沒有同步,重開為 C3。其餘 17 項確認成立。

## § 6. Verdict + Next Round Focus

- **Status:** ship-as-is(BLOCKER 0、CONCERN 4、NIT 9、STRENGTH 6)
- **Recommend:**
  - 送 PO 簽核前先修 C1、C2、C3。三項都是一兩段文字修訂,其中 C3 要同時改規格書 POS-04。
  - C4 可以與 §10 的 PO 決定一起處理:PO 拍板後,直接刪除或保留標註的段落即可。
  - NIT 可以在 M1 開工前順手處理。
- **Next Round Focus(若有第 3 輪):**
  - §5.5 修訂後的狀態表是否涵蓋 `_on_detected` 的全部分支,並與 DSC-20 一致。
  - `render`、`startup`、`apply` 的名稱資料流是否在每條儲存路徑上都寫明。
  - PO 對 §10 的決定與 §5～§8 是否一致。

(本輪沒有 BLOCKER,不附 § 7 Reflection。)
