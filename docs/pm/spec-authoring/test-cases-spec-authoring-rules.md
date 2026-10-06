# Test Cases Spec Authoring Rules

> **Owner:** PM(spec authoring governance)
> **Status:** Draft
> **Spec-Version:** 2026-07-05.3
> **Last Updated:** 2026-07-05
> **Role:** L3 Primary — test cases spec 的 **create / update / delete** 唯一 authoring 規則書(Track A 家族第 4 份)
> **Authors:** PO(kuohsuming)+ Claude(co-author)

---

## 1. Purpose

定義 Claude(及任何 AI 工具)在 **建立、更新、刪除 test case(TC)spec** 時**必須嚴格遵守**的規則。可逐條打勾。

- 論述 / framework → `docs/pm/5-spec-authoring-framework.md`
- 姊妹 rulebook:`requirement-spec-authoring-rules.md`(REQ §3.4 claim-ID)· `test-plan-spec-authoring-rules.md`(TP + vkp-ID)· `design-spec-authoring-rules.md`(DESIGN)
- **本檔專注**:TC 是 **executable** 的具體斷言(1 Given/When/Then);對 code 跑出綠 = G6。
- **基底 = sanity 24-field schema**(REQ-004 semantic + REQ-019 format,已真機驗證)—— **不重造**,只 ADD `covers_tp` + ALIGN intent。

> **本檔是 test cases authoring 的唯一 Primary。**(One Topic, One Primary)

> **⭐ TC 恆存在(2026-07-05,D-035;5 份 spec 不可省略)**:無論 feature 多簡單,**TC 都要寫**——無 tier 省略。tier 只控**深度**(framework §6)。**最小地板(floor)= ≥1 positive(對映 golden)+ ≥1 anti-assertion(對映 anti)+ `covers_tp` 單值 + executable 形式**;簡單 feature 寫到此即合格,但不省。

---

## 2. Scope

### ✅ In-scope
- TC spec 的 create / update / delete 規則
- TC schema(sanity 24-field 一般化 + `covers_tp`)+ intent↔TP 一致性 + G6 分層 + PII 規則

### ⛔ Non-goals
- 驗證策略 / validation_key_point(= TP,`test-plan-spec-authoring-rules.md`)
- runner / dispatcher 實作(= sanity 既有基礎建設 + Track B)
- validator 硬 gate 實作:Track B(rulebook-first)

---

## 3. 核心模型 — TC = 1 executable G/W/T,cite 單一 TP

### 3.1 sizing + 追溯不變式

| # | 不變式 | 說明 |
|---|---|---|
| **INV-TC1 One-GWT** | 1 TC = **1 Given/When/Then**(1 具體情境)| 混多情境 → 拆 |
| **INV-TC2 Cite-parent single** | **`covers_tp` 單值**,cite 恰 1 父 TP → 透傳父 TP 的 claim(`covers_req` claim-ID)+ REQ(TC→TP→REQ **1:1:1**)| 0 或 >1 → validator fail |
| **INV-TC3 Intent↔TP** | intent **必與父 TP `covers_req` 的 claim 類型一致**(claim-ID `G`→`positive` / `A`→`negative`\|`boundary`\|`injection` + `expected_count: 0`);**機制 layer-specific(見 §4 note):UI=`test_data.intent` 欄 / backend=test polarity** | validator 檢一致(claim 類型讀自 claim-ID 前綴,無獨立 `TP.claim` 欄)|
| **INV-TC4 Observable-only** | assertion **只斷言可觀察**(UI / DB / API 狀態),**禁內部 method call** | refactor-safe |
| **INV-TC5 No-PII** | 測試資料無真 PII;**機制 layer-specific(見 §4 note):UI=`test_data.label` regex + `TEST_FAKE_` + `cleanup_after` / backend=fixture scrub**;+ `qa_notes` scrub | 對齊 `[[public-vs-private-friend-data]]` |

- **assertion 極性跟隨 TP**(INV-TC3):**不**每 TC 硬塞 anti-assertion;anti 覆蓋靠**基數保證**(每 anti_example → boundary TP → anti TC,TP rulebook §3.5)。
- **covers_tp 是追溯骨幹**:sanity 舊 TC 無 parent 引用(= 走偏本質),`covers_tp` 是唯一結構性 ADD。

### 3.2 claim / vkp 透傳

- TC 透過 `covers_tp` → TP → `covers_req`(claim-ID §3.4)→ 回溯到 REQ 的 golden/anti。
- TC 斷言的標的 = 父 TP 的 `validation_key_point`(vkp-ID `TP-<id>.vkp-<n>`,TP rulebook §4.2);TC 讓 vkp 可執行驗證。

---

## 4. TC Schema(sanity 24-field 一般化 + `covers_tp`,self-contained)

> **具體欄名 project-specific(守 pilot guard ③)**:下表用**一般化名**(rulebook 用語);concrete runner 欄名各專案自訂。**sanity 映射**:`test_data`←`fake_data` · `state_assertions`←`system_state_assertions` · `target`←`target_spa_path/strategy/url`。**pilot 保 sanity 具體名以免弄壞 runner**,一般化名僅供 rulebook 表述。「24-field」= sanity 原欄數,此處列主要欄非逐一。
>
> ⭐ **TC executable 形式 layer-specific(pilot 01 F2)**:下表 schema = **UI / sanity 層**(fake_data variants + validate.prompts 人工 Q&A + target 導航,真機跑)。**非 UI(backend / module)TC** = 該層原生 executable(eg. **pytest** 斷言;無 fake_data/validate.prompts;`target` = 被測函式 / API;斷言用 assert 而非人工 Q&A)。UI 24-field 為 UI 層具體化,非唯一形式。
> **不變式分兩類(pilot 01 F2 spectra R1)**:
> - **(i) 機制通用(跨層同)**:`covers_tp` 單值(INV-TC2)· observable-only 斷言(INV-TC4)· G6 分層。
> - **(ii) 原則通用、機制 layer-specific**:`intent↔TP`(INV-TC3)—— **UI** 用 `test_data.intent` 欄 / **backend** 用 test polarity(positive/negative test);`no-PII`(INV-TC5)—— **UI** 用 `label` regex + `TEST_FAKE_` / **backend** 用 fixture scrub。

**🔑 Identity + Traceability**

| 欄位 | 必 | 說明 |
|---|---|---|
| `id` | ✅ | `TC-<module>-<seq>` |
| **`covers_tp`** | ✅ **⭐NEW** | **單值**,cite 父 TP → 透傳 claim + REQ(§3.1 INV-TC2)|
| `legacy_id` | ○ | migration 舊 ID 保留 |

**📝 Content(人類層,3-role)**

| 欄位 | 必 | 說明 |
|---|---|---|
| `title` | ✅ | 1 行 |
| `description` | ✅ | 完整敘述 |
| `qa_notes` | ○ | QA 敘述;**PII scrub** |
| `category` | ✅ | 專案 domain enum |
| `priority` | ✅ | P0 / P1 / P2 |
| `operation_type` | ✅ | CRUD enum |
| `tags` | ○ | smoke / regression … |

**▶️ Executable — steps**

| 欄位 | 必 | 說明 |
|---|---|---|
| `preconditions` | ○ | `{type, description}` |
| `test_steps` | ○ | `{step_num, action, qa_focus}` |
| `target`(navigation)| ○ | 怎麼到達測試面(sanity `target_spa_path/strategy/url` 一般化,專案特定)|

**✅ Executable — assertions(承重)**

| 欄位 | 必 | 說明 |
|---|---|---|
| `validate.prompts` | ✅ | 人 Q&A `[{q, yesPass}]` |
| `state_assertions` | ○(強烈建議)| 機器 DSL(`db_row` / `ui_state` / `api`,**可觀察非內部**);`expected_count: 0` = anti-assertion |

**🧪 Test data**

| 欄位 | 必 | 說明 |
|---|---|---|
| `test_data` | ○ | `{field: [{value, label, intent, scenario, expected}]}` |
| — `intent` enum | | `{positive \| negative \| boundary \| injection}` ⭐ **必與父 TP 的 claim 類型一致**(見 INV-TC3)|
| — PII 規則 | | `label` regex `^[a-z]+-[a-z0-9-]+$` + `TEST_FAKE_` + `cleanup_after`(INV-TC5)|

**🔧 Meta**:`execution`(pass/fail/skip,CI 回填)/ `skip` / `dependencies`

---

## 5. 疊在元素上的規則(rulebook 靈魂)

1. `covers_tp` **單值**(0 或 >1 → validator fail)。
2. `intent` ↔ 父 TP `covers_req` 的 claim 類型 **一致**(claim-ID `G`→positive / `A`→negative\|boundary\|injection + `expected_count: 0`)。
3. assertion **只斷言可觀察**(UI / DB / API),禁內部 method call(refactor-safe)。
4. **no PII**(label regex + qa_notes scrub + `TEST_FAKE_` + cleanup)。
5. **executable + G6 分層**:P0 REQ 的 TC = **100% hard gate**;P1 / P2 = **≥95%**(避免 LINE API flaky 卡非關鍵 ship)。
6. assertion 極性**跟隨 TP**(不每 TC 硬塞 anti;anti 覆蓋靠基數,§3.1)。

### 清理
`related_feature`(鬆散)→ 被 `covers_tp` 取代;`subject` 已 deprecated。

---

## 6. Executable + G6 Gate

- **執行器** = sanity 既有 dispatcher(`validate.prompts` + `state_assertions` 真機跑)。
- **G6 分層(framework §9.4)**:P0 REQ 的 TC = **100% hard gate**;P1/P2 = ≥95%。
- **格式不動**:一般化須**保 sanity `tc-*.json` executable 格式**(不弄壞 runner);新增 `covers_tp` 為 additive。
- **validator 機檢**(covers_tp 單值 / intent↔TP / PII / observable-only)= Track B。

---

## 7. CRUD + Write-time Sign-off（對齊 REQ §5.5)

- **角色**:🔬 QA = primary author(+ 💻 Dev seam secondary);👔 PM = reviewer(對齊意圖)。
- **write-time sign-off**:async per-TC,**有人決定就走**(non-blocking)。
- **CRUD**:
  - **create** — 過 INV-TC1~5 + intent↔TP 一致才寫入。
  - **update** — 改 `covers_tp` 觸發 TP↔TC 重驗;改 assertion 須維持 observable-only。
  - **delete** — 破壞性 → **PO-confirm**;預設 Deprecate;TC-ID 永不重用。

---

## 8. Decision Log

裁決見 `docs/pm/spec-authoring/decision-log.md`。TC rulebook 源自 execution-plan §4F 定案(sanity 24-field SSOT + `covers_tp` 唯一 ADD + intent↔TP)。

## 9. Revision

| Rev | Date | Change |
|---|---|---|
| 2026-07-05.2 | 2026-07-05 | pilot 01 F2 **spectra R2 fix**(grep-verify):C1 normative row 未跟 §4 note —— INV-TC3 + INV-TC5 row 加「機制 layer-specific(見 §4 note):UI=欄/regex / backend=polarity/fixture-scrub」;checklist ↔ note 全 layer-aware 一致 |
| 2026-07-05.1 | 2026-07-05 | pilot 01 F2 **spectra R1 fix**:carve-out note 的「通用不變式跨層皆守」分兩類 —— (i) 機制通用(covers_tp/observable/G6)/ (ii) 原則通用、機制 layer-specific(intent↔TP:UI 欄 vs backend polarity;no-PII:label regex vs fixture scrub)。消 overclaim,免 backend author 找不存在的欄 |
| 2026-07-05.0 | 2026-07-05 | **pilot 01 F2 fix**(backend-schema-auto-sync measure-first):§4 加 **TC executable 形式 layer-specific carve-out** —— UI/sanity 24-field(fake_data+validate.prompts 真機)vs 非 UI/backend pytest(assert,無 fake_data);通用不變式(covers_tp/intent↔TP/observable-only/no-PII/G6)跨層皆守。根因:schema 衍生自 sanity 帶 UI 假設 |
| 2026-07-04.2 | 2026-07-04 | spectra R2 fix(grep-verify):C1 消 R1 漏掉的 2 個 `TP.claim` dangler(INV-TC2 line 45 + intent enum row line 104 → 「父 TP 的 claim / claim 類型」);grep 確認 `TP.claim` 清零(僅存 INV-TC3 的「無獨立 `TP.claim` 欄」正確否定)。TC↔TP claim 引用全自洽 |
| 2026-07-04.1 | 2026-07-04 | spectra R1 fixes(accept,C2–C3 + N2):C2 INV-TC3 + §5 rule 2 改「`intent` ↔ 父 TP `covers_req` claim 類型(claim-ID `G`/`A`)」消 `TP.claim` dangling / C3 **一般化欄名 ↔ sanity 具體名映射表**(`test_data`←`fake_data` 等,守 pilot guard ③ runner 不壞)+ 24-field 註 |
| 2026-07-04.0 | 2026-07-04 | 新建 Track A TC rulebook(§4F → 檔):基底 = sanity 24-field(不重造);唯一結構 ADD = **`covers_tp` 單值**(TC→TP→REQ 1:1:1);INV-TC1~5(One-GWT / cite-single / intent↔TP / observable-only / no-PII);assertion 極性跟隨 TP(不硬塞 anti,靠基數);G6 分層 P0 100%/P1-2 ≥95%;保 sanity executable 格式;claim/vkp 透傳;validator = Track B |
