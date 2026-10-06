---
title: 5-Spec Authoring Framework — AI-Agent-Friendly Project/Feature Development
version: 0.1
date: 2026-07-01
authors:
  - PO (kuohsuming — mental model + strategic direction)
  - Claude (co-author — framework synthesis + AI-agent pitfall analysis)
status: draft (baseline — refined via 2026-06-30/07-01 PM Skill kickoff discussion)
purpose: >
  Codify a 5-spec cascade framework so PM/QA/Developer can co-write specs
  that AI agents (Claude) can follow to build production-quality projects
  and features with high requirement coverage and low drift.
audience:
  - PM(👔 project intent, roadmap, business tradeoff)
  - QA(🔬 test strategy, acceptance criteria, edge case adversarial thinking)
  - Developer(💻 impl, technical constraint, feasibility)
  - Reviewer(V7 SCR + spectra-review — validates all 5 layers)
memory_rules_cited:
  - "[[human-first-docs]]"
  - "[[backend-change-rule]]"
  - "[[backend-schema-change-workflow]]"
  - "[[audit-patch-cascade-verify]]"
  - "[[incremental-rev-cascade]]"
related_specs:
  - "docs/pm/v7-spec-compliance-review/spec/scr-requirement-spec.md (V7 SCR — reviewer engine that validates specs)"
  - "docs/pm/pm-skill/spec/pm-skill-proposal.md (PM Skill — subcommand router + workflow)"
  - "docs/pm/sanity-check/spec/sanity-check-requirement-spec.md (Sanity-check — 已 validate 這 pattern 的 pilot module)"
---

# 5-Spec Authoring Framework

## 1. Motivation — Why 5 Specs Instead of 3

Traditional software engineering uses 3 specs(Requirement / Functional / Design)。 AI-agent-driven build has 2 gaps this pattern doesn't cover:

- **Coverage is "cascade" but never truly 100%** — REQ → FUNC syntactic 95% × FUNC → DESIGN 95% × DESIGN → Code 95% = 86% end-to-end。 Multiplication rule dilutes confidence。
- **Coverage ≠ Correctness** — Every layer can 100% cite parent yet mis-implement semantics(pitfall PF1)。

**Adding Test Plan Spec + Test Cases Spec closes both gaps:**

- Test Plan Spec makes REQ verifiable(FUNC review has second reference)
- Test Cases Spec is **executable** — running tests directly proves REQ is satisfied,not indirectly via 3-layer syntactic chain。

Existing pilot evidence:sanity-check module 已 impl this pattern(REQ-018/019/024 + 53 executable tc-*.json + lint.sh Stage 3+4 BLOCKING gate)— pattern 推廣至全 project 有可信度。

---

## 2. Framework Diagram

```
                    Requirement Spec (WHY + WHAT)
                          │
              ┌───────────┴───────────┐
              │                       │
              ▼                       ▼
        Test Plan Spec           Functional Spec
     (WHAT to VERIFY)            (HOW it BEHAVES)
        strategy layer            behavior layer
              │                       │
              ▼                       │
        Test Cases Spec               │
     (concrete + EXECUTABLE)          │
        instance layer                │
              │                       │
              └───────────┬───────────┘
                          │
                          ▼
                    Design Spec (HOW BUILT)
                       impl layer
                    reviewed against:
                    ✓ FUNC coverage
                    ✓ Test Cases seams
                          │
                          ▼
                        Code
                          │
                          ▼
                Execute Test Cases
                    ↓
                 100% pass = ✅ Ship
```

**Cascade + parallel verification:**

- **Cascade top-down:** REQ → {Test Plan, FUNC} → {Test Cases, DESIGN} → Code
- **Bottom-up proof:** Code → Test Cases pass → REQ satisfied(直接證明)

兩條並存 = 防漏 + 防 gold-plating + 直接驗證 triangulation。

---

## 3. The 5 Specs — Definitions

### 3.1 Requirement Spec — 「WHY + WHAT」

**Purpose:** Business intent, user problem, success criteria。 Answers「為什麼要做?做什麼?什麼算成功?」

**Primary author:** PM
**Reviewer:** Developer(feasibility)+ QA(testability)

#### Content

| Section | Purpose |
|:---|:---|
| **REQ-XXX list** | 每 REQ = 1 acceptance criterion,testable「user can X」句型 |
| **Problem statement** | Who suffers + from what pain + evidence(support tickets / data) |
| **Success metric** | 業務指標(不是實作指標)— eg. daily active user +10% |
| **Scope boundary** | ✅ In-scope + ⛔ Non-goals(防 scope creep) |
| **Constraints** | Regulatory / timeline / budget / memory rules that apply |
| **Priority tier** | P0 blocking / P1 desired / P2 nice-to-have |
| **Impacted stakeholders** | Who else 需要 informed |
| **Anti-example**(recommended per REQ)| 「Not this,because Y」 — 防 wrong interpretation |

#### 3-Role Perspective

- **👔 PM view:** Every REQ 應 map to a real user problem。 Vague REQ(「效能要好」)= 尚未 ready。
- **🔬 QA view:** Every REQ 必 testable。 If QA can't imagine writing a test for it,PM 需 concretize。
- **💻 Dev view:** REQ ambiguity = mid-impl blocker。 Prefer explicit constraints over「obviously」assumptions。

#### Anti-Patterns

- Vague acceptance criteria(「works well」/「user-friendly」)
- Missing non-goals(scope creep enabler)
- Silent priority(unclear if P0 or P2 → impl invests wrong effort)
- Copy-pasted REQ-IDs referencing REQs that no longer exist

#### Format

Markdown。 YAML frontmatter for metadata(revision, authors, memory_rules)。 Section: 1 REQ per subsection with clear ID anchor。

---

### 3.2 Test Plan Spec — 「WHAT to VERIFY」

**Purpose:** Testing strategy per REQ — declarative layer connecting business intent to verification approach。 Answers「這 REQ 我們會怎麼驗?」

**Primary author:** QA(+ PM secondary)
**Reviewer:** Developer

#### Content

| Section | Purpose |
|:---|:---|
| **TP-XXX list** | 每 TP = 1 test area per REQ(cite parent REQ-XXX) |
| **Verification method** | Unit test / integration / UI smoke / load / manual — 每 area 選項 |
| **Coverage areas** | Happy path / edge case / error path / concurrent / security |
| **Test data source** | Real-world corpus(anonymized)/ synthetic / adversarial fuzzing |
| **Non-verification** | 明宣不驗的 area + 為什麼(cost / risk / scope) |
| **Priority tier** | Test priority(不 一定等於 REQ priority) |
| **Environment requirements** | Local / staging / mock services |

#### 3-Role Perspective

- **👔 PM view:** Test Plan 讓 PM 看見「這 REQ 驗證嚴不嚴」 — 決定要不要投更多 QA budget。
- **🔬 QA view:** Primary artifact。 Test Plan 好壞 = QA 是否理解 REQ 意圖的體現。
- **💻 Dev view:** 讓 Dev 知道「需要提供哪些 hook / fixture / mockable interface」 for testability。

#### Anti-Patterns

- **過度細** — Test Plan 變成 concrete test case duplicate(層次錯亂)
- **只 happy path** — 缺 error / edge / adversarial coverage 宣言
- **未宣 non-verification** — silent 未驗的 area 變成 future bug source
- **忽略 test data source** — synthetic-only 過度自信,production data 沒 cover

#### Format

Markdown 敘述。 每 TP 1 subsection,max 1 頁(避免 Test Cases duplicate)。 Section 順序 = REQ 順序。

---

### 3.3 Functional Spec — 「HOW it BEHAVES」

**Purpose:** User-facing behavior — flow / interaction / state / error path。 Answers「用戶按 X,系統做什麼?錯誤時如何?」

**Primary author:** PM + QA(co-write)
**Reviewer:** Developer(interface feasibility)

#### Content

| Section | Purpose |
|:---|:---|
| **FUNC-XXX list** | 每 FUNC = 1 flow / interaction pattern(cite parent REQ-XXX) |
| **User journey** | Numbered step sequence(state machine 或 flow diagram) |
| **Edge cases** | Empty state / network fail / concurrent user / race condition |
| **Data validation** | Input format / boundaries / error message template |
| **UX pattern** | Reuse existing convention 或 justify NEW convention |
| **Integration points** | External API / other module contracts(with cite) |
| **Test scenarios**(QA-authored)| Happy path + edge + adversarial + concrete example test data |

#### 3-Role Perspective

- **👔 PM view:** FUNC 是 「用戶要看到的行為」 — 不 impl detail。 過細 impl 討論屬 DESIGN。
- **🔬 QA view:** FUNC 有沒有 covered edge case = 決定 Test Cases 深度。 FUNC 缺 edge = QA 補寫 or push PM 更新。
- **💻 Dev view:** FUNC 是 interface contract — 決定 method signature + error handling shape。

#### Anti-Patterns

- **Silent modality shift** — REQ 沒說 modal,FUNC 加了 modal(V7 SCR R3 catch)
- **Missing failure modes** — 只寫 happy path
- **UX pattern 未 justify NEW convention** — 增加 codebase 一致性成本
- **Integration point 未 cite** — 假設 external API 存在但沒指

#### Format

Markdown。 每 FUNC 1 subsection with numbered step list。 Cite parent REQ 用 `Parent: REQ-XXX` 明式。

---

### 3.4 Test Cases Spec — 「Concrete + EXECUTABLE Verification」⭐

**Purpose:** 具體 executable acceptance test — 直接證明 REQ 是 satisfied 的 primary evidence。 Answers「Given input X,expect output Y」

**Primary author:** QA(+ Dev secondary)
**Reviewer:** PM

#### Content

| Section | Purpose |
|:---|:---|
| **TC-XXX list** | 每 TC = 1 concrete verification instance(cite parent TP-XXX + REQ-XXX) |
| **Given** | Pre-condition + input data + system state |
| **When** | Action taken(user interaction or system event) |
| **Then** | Expected observable outcome(user-visible or side effect) |
| **Positive assertions** | 「must be true」assertions(≥ 1)|
| **Anti-assertions** | 「must NOT be true」assertions(boundary check per S6 in framework discussion)|
| **Test data** | Concrete values(not abstract 「any string」)|
| **Execution status** | pass / fail / skip / pending(auto-updated from CI runs)|

#### Format Requirements(重要)

**Test Cases 必 executable — not markdown-only:**

Preferred formats:
- **pytest with docstring**(Python project)
- **JSON declarative + runner**(如 sanity-check 53 tc-*.json pattern)
- **Given/When/Then BDD**(如 pytest-bdd)

**Anti-pattern:**
- Test Cases 只有 markdown 敘述 → QA 手動 verify → 高成本 + 易漏
- Test Cases markdown + pytest 兩份 → sync 難維護

#### 3-Role Perspective

- **👔 PM view:** Test Cases pass = 「REQ 真實達成」的最強證明。 比 3-layer syntactic cascade 直接 objective。
- **🔬 QA view:** Primary artifact。 Test Cases 質量 = QA 對 REQ 理解深度 + 對 edge case 想像力的體現。
- **💻 Dev view:** Test Cases 決定「impl 需 expose 哪些 seam」 for testability。 也提供 refactoring safety net。

#### Anti-Patterns

- **Coupled to impl detail** — assert internal method call sequence → refactoring 破 test 但不 破 behavior
- **Missing anti-assertions** — 只 assert positive path,boundary invisible
- **Pure synthetic data** — production pattern 沒 cover,false confidence
- **Test data 洩漏 PII**(對齊 `[[public-vs-private-friend-data]]`)— anonymized 要真 anonymized

#### Format

Executable code + minimal markdown。 Ideal:pytest file with docstring per TC citing parent TP + REQ IDs。 Auto-generate markdown index for review readability(不 手寫)。

---

### 3.5 Design Spec — 「HOW it's BUILT」

**Purpose:** Technical impl contract — files / interfaces / DB schema / performance budget。 Answers「哪個檔案改什麼?函式簽章?DB 動嗎?」

**Primary author:** Developer
**Reviewer:** PM(matches intent)+ QA(testable seams for Test Cases)

#### Content

| Section | Purpose |
|:---|:---|
| **DESIGN-XXX list** | 每 DESIGN = 1 component/module change(cite parent FUNC-XXX) |
| **File impact map** | 具體 path list — 修哪些 / 新增哪些 / 刪哪些 |
| **Interface signatures** | Function 簽章 + return type + error paths(不 pseudocode) |
| **DB schema changes** | ALTER TABLE ... ADD COLUMN 具體 SQL(對齊 `[[backend-schema-change-workflow]]`) |
| **Data flow** | Input → transform → output,含 error handling |
| **Performance budget** | Q95 latency / memory ceiling / DB query count |
| **Migration + rollback** | 若 schema/config change 必有 rollback path |
| **Security** | Input sanitization / auth / PII boundary |
| **Test seam design** | Hooks / fixtures / mockable interface 供 Test Cases 使用 |

#### 3-Role Perspective

- **👔 PM view:** Design 讀不懂沒關係,但「file impact + effort estimate」 must be clear。 決定 project timeline。
- **🔬 QA view:** DESIGN 是否 expose enough test seam = Test Cases writeability。 缺 seam = QA push Dev 補設計。
- **💻 Dev view:** Primary artifact。 DESIGN 好壞決定 impl velocity + refactoring risk。

#### Anti-Patterns

- **Gold-plating** — DESIGN 加 FUNC 沒要的 component(V7 SCR R2 catch)
- **Missing migration/rollback** — schema change without safety net
- **Vague interface signatures** — 「string」 without 「what format?」
- **Missing test seam** — Design 沒設 hook,Test Cases 寫不出 → QA blocker
- **Ungrounded mount-point / file-impact** — 選「掛哪個 cmd / 改哪個檔」前**沒查主入口的實際 payload 與非交易性 side-effect**,憑想像設計 → 掛載點錯、實作期被迫 revert。**強制**:File impact map / Interface signatures 敲定前,先列**該功能主入口實際送什麼 payload(有沒有照片/檔案/大物件)+ 有無 blob/外呼/檔案等 transaction 回滾不了的 side-effect**;掛載點須落在「已持有所需資料 + side-effect 可控」的那一層。(G1-A 教訓:atomic 建首卡原設計掛 `create_bizcard_profile`,但新增身份唯一入口走 view-ocr 帶照片 → 該 cmd 無 blob 能力會掉照片 → 被迫重掛 `upload_personal_bizcard`;見 `lessons-ledger.md` 69be285)

#### Format

Markdown。 每 DESIGN 1 subsection with file impact table。 Cite parent FUNC 用 `Parent: FUNC-XXX` 明式。 Signature 用 Python type hints 或 SQL DDL(具體 syntax,不 pseudocode)。

---

## 4. Cross-Doc Relations & Traceability

### 4.1 Bi-directional Cascade

```
REQ-005 ──┬─► TP-005A ──► TC-101 (positive)
          │              ──► TC-102 (edge)
          │              ──► TC-103 (adversarial)
          │
          ├─► FUNC-012 ──► DESIGN-007 ──► src/foo.py:42
          │                             ──► src/foo.py:88
          │
          └─► FUNC-013 ──► DESIGN-008 ──► templates/bar.html:15
```

### 4.2 Bi-directional Invariants(V7 SCR R0-R6 enforce)

| Direction | Rule | Violation type |
|:---|:---|:---|
| REQ ↔ TP | 每 REQ 有 ≥ 1 Test Plan; 每 TP cite ≥ 1 REQ | Gap / Gold-plating |
| REQ ↔ FUNC | 每 REQ 有 ≥ 1 FUNC child; 每 FUNC cite ≥ 1 REQ | Vacuous spec / Extra behavior |
| TP ↔ TC | 每 TP 有 ≥ 1 concrete TC; 每 TC cite ≥ 1 TP | Untestable strategy / Ad-hoc test |
| FUNC + TC ↔ DESIGN | 每 FUNC 有 ≥ 1 DESIGN; DESIGN 支持 TC seams | Impl missing / Testability broken |
| DESIGN ↔ Code | 每 DESIGN 有 ≥ 1 code entry; 每 code entry cite ≥ 1 DESIGN | Unimpl'd design / Unspec'd code |

**Bidirectional check catches:**
- **Top-down gap** — spec 有,code 缺(未實作)
- **Bottom-up gold-plating** — code 有,spec 缺(實作 spec 沒要)

---

## 5. Ship-Gate — 8-Gate Composition

| # | Gate | Rule | Threshold | Verify by |
|:---:|:---|:---|:---:|:---|
| **G1** | REQ → TP syntactic coverage | 每 REQ AC 有 Test Plan area | ≥ 95% | V7 SCR R2 |
| **G2** | TP → TC coverage | 每 test area 有 concrete TC | ≥ 95% | V7 SCR R2 |
| **G3** | REQ → FUNC coverage | 每 REQ 有 FUNC child | ≥ 95% | V7 SCR R2 |
| **G4** | FUNC + TC → DESIGN dual verify | DESIGN 支持 FUNC + Test seams | ≥ 95% | V7 SCR R2 + R4 |
| **G5** | DESIGN → Code coverage | 每 DESIGN 有 code entry | ≥ 95% | V7 SCR R2 |
| **G6** | **Test Cases execute against Code** ⭐ | 100% acceptance test green | **100% HARD GATE** | CI pipeline |
| **G7** | Semantic L4 LLM Q&A | 每 REQ「is it truly implemented?」= yes | All yes | V7 SCR heavy tier |
| **G8** | Independent reviewer sign-off | authors ≠ reviewers across 5 specs | All signed | Frontmatter check |

**5-spec cascade math:** 0.95⁵ = 77% syntactic dilution — 所以 **G6 executable 100% hard gate 是 compensating gate**,補償 syntactic cascade dilution。

**任一 gate fail = ship blocked。**

---

## 6. Feature-Size Tiered Rules — tier 控深度,不控 spec 存在

> **PO 2026-07-05 親令:制度一致 > 例外處理。** 廢除舊「Small 省 FUNC」carve-out(它生出 spine 降級 / H6 / validator `--tier` 特例等跨檔例外機器,反增維護負擔)。

**5 份 spec(REQ / FUNC / DESIGN / TP / TC)永遠存在,無論 feature 多簡單。** tier 是「寫多細」的旋鈕(深度 / 嚴謹度 dial),不是「寫不寫」的開關。每份 spec 有**最小可用地板(floor)**;簡單 feature 寫到 floor 即合格(不 gold-plate),但**不省略任一份**。

| tier | 深度(隨 tier 縮放;5 份恆在) |
|:---|:---|
| **Small**(~50–300 LOC / 1 REQ 清楚) | 各寫到 floor:核心 + ~1 鄰近候選;FUNC 1 journey + 1 FM;TP 每 claim 1 vkp;TC ≥1 pos + ≥1 anti;solo sign-off |
| **Medium**(300–1000) | floor 之上:~3 鄰近候選;多 journey / FM;happy+edge+error;多 component;3-role sign-off |
| **Large / high-stakes**(>1000 / `risk≠normal`) | 窮舉:sibling 全掃;全 journey + 邊界 FM;+security+concurrent+perf;跨模組 interface;強 gate 不省;phased 分 rev(`[[incremental-rev-cascade]]`) |

**最小可用地板(floor)** — 每份 spec 的存在下限(低於 = 未寫;寫到即合格,防「一律寫」退化成空儀式):

| spec | floor(最小骨架) |
|---|---|
| **REQ** | 三元組:1 golden `G1` + ≥1 anti `A1` |
| **FUNC** | ≥1 `user_journey`(≥1 step 有 `realizes` golden)+ ≥1 `failure_mode`(`handles` anti);`covers_req` list |
| **DESIGN** | ≥1 component + `covers_func`(cite FUNC)+ `file_impact` ≥1 + `test_seam`;UI 加 markup 契約(INV-D1~5) |
| **TP** | 每 claim ≥1 `validation_key_point`(帶 vkp-ID);`covers_req` 單值 claim-ID;≥1 area |
| **TC** | ≥1 positive(對映 golden)+ ≥1 anti-assertion(對映 anti);`covers_tp` 單值;executable |

**零例外**:trivial feature(config / 常數 / copy)仍寫 5 份,但 FUNC / TP 可能只 1–2 行(停在 floor)。**不留「可省」carve-out** —— 例外正是要消滅的維護負擔。

**PM Skill 落地:** `/pm project-kickoff <name> --size small|medium|large` → skill 生 **5-spec skeleton(全份,深度依 tier)**,非「決定要哪幾份」。

---

## 7. Roles & Responsibility Matrix

| Spec | Primary Author | Reviewer(必不同 person)| Rationale |
|:---:|:---|:---|:---|
| REQ | 👔 PM | 💻 Dev + 🔬 QA | Business intent — PM 是 SSOT |
| **Test Plan** | 🔬 QA(+ PM secondary)| 💻 Dev | Independent from REQ author(防 PF4 circular) |
| FUNC | 👔 PM + 🔬 QA | 💻 Dev | User-facing behavior 需 PM/QA co-visibility |
| **Test Cases** | 🔬 QA(+ Dev secondary)| 👔 PM | Executable — QA primary,Dev help seam design |
| DESIGN | 💻 Dev | 👔 PM + 🔬 QA | Impl contract — Dev SSOT,PM/QA verify intent alignment |
| Code | 💻 Dev | (V7 SCR + PR review) | Standard practice |

**Rule:** No single person 貫穿 3+ layer authorship(防 misreading systemic 透透)。

---

## 8. Anti-Example per REQ Pattern

每 REQ / TC 加「positive + anti-example」對比:

```markdown
REQ-005: Profile 必伴 main_bizcard

Positive:
  - 新增 profile → 自動建 1 張 main_bizcard 用身份名稱

Anti-example(什麼不算 satisfying REQ-005):
  - ❌ Profile 可獨立存在,bizcard optional
  - ❌ 首張 bizcard 用 profile.email 當 name
  - ❌ 只在 UI 顯示 default bizcard,DB 沒真的 insert
```

**效果:**
- AI agent 讀 anti-example 直接排除 wrong interpretation
- QA 寫 Test Cases 直接 map anti-example → anti-assertion

---

## 9. Living Spec & Change Propagation

**5-spec 允許 impl 期修訂(discovered constraint 落回 spec)**, 但必 discipline:

- **Any spec edit** → append `docs/<project>/decision-log.md` `D-XXX` row(reason + PO confirm)
- **Upstream edit**(REQ change)→ 觸發 `/pm cascade-check` — 自動 flag downstream(TP/FUNC/TC/DESIGN)未更新
- **`spec_dirty: true` frontmatter** — 標「上流改過,本層 needs review」
- **Ship-gate 需 `spec_dirty: false` across all 5 specs** — 防 stale spec pass gate

---

## 10. Anti-Pattern Catalog(spec smell — ship-blocking OR blocker)

| Smell | 症狀 | 出現在 spec | 解方 |
|:---|:---|:---:|:---|
| **Vague AC** | 「效能要好」「UX 要順」 | REQ | 改 metric:「Q95 < 2s」「3-tap 內達成」 |
| **Missing failure modes** | 只寫 happy path | FUNC / TP | 每 FUNC 列 ≥ 2 失敗情境 |
| **Undeclared assumptions** | 「假設 DB 有 X column」 | DESIGN | Pre-condition 明列 + 驗證 command |
| **Cross-spec disagreement** | REQ async / DESIGN sync | ALL | Round 1 spectra-review 抓 |
| **Copy-paste rot** | 引用 REQ-105(已 renamed) | ALL | V7 SCR R0 catch |
| **Gold-plating** | DESIGN 多做 REQ 沒要 | DESIGN / FUNC | Bidirectional R2 抓 unspec'd |
| **Under-specified errors** | 「handle errors」 | FUNC | 每 error 有:trigger + response + user-facing message |
| **Silent modality shift** | REQ 沒說 modal,FUNC 加了 | FUNC | V7 SCR R3 catch |
| **Test coupled to impl** | assert internal method calls | TC | 只 assert user-observable outcome |
| **Test all synthetic** | 100% synthetic data | TC | 50%+ real-world corpus mandatory |
| **Missing anti-assertion** | 只 positive assert | TC | 每 TC ≥ 1 anti-assertion |
| **Missing test seam** | Design 沒 hook | DESIGN | QA reviewer push Dev 補 |

---

## 11. AI-Agent Failure Modes(對照 8-Pillar Framework)

**5-spec framework 屬 8-pillar framework 的 pillar 2(rules)+ pillar 3(acceptance criteria)。 其他 pillar 需另 mechanism 支持:**

| Pillar | Mechanism(non-spec) | 目的 |
|:---|:---|:---|
| 1. Role | PM Skill 分工 + V0-V7 mode map | 設定 agent lens |
| 4. Context Anchor | Memory rules(17 條)+ decision-log + state.md | 防 context loss |
| 5. Escape Route | `[[backend-change-rule]]` propose-first + `TBD:` marker | 防 silent assumption |
| 6. Feedback Loop | V7 SCR + spectra-review + Test Cases execution | 防 hallucination + wrong metric |
| 7. Judgment | Priority tier + cost tier + confidence tier | 防 rule 平權 卡住 |
| 8. Recovery | `[[backend-lint-workflow]]` + cascade-verify + regression tests | 防 failure 無 playbook |

**Rule:** 5-spec framework 是 necessary,不 sufficient。 需 8-pillar 全 pillar 都 in place 才是「AI agent 建 production-quality feature」的完整 setup。

---

## 12. Templates

TBD:next iteration 加。 initial pass 建議直接參考 sanity-check module 現有 spec 為 template:

- REQ template:`docs/pm/sanity-check/spec/sanity-check-requirement-spec.md`(REQ-018/019/024 pattern)
- Test Cases template:`docs/pm/sanity-check/test-cases/generated/tc-*.json`(53 examples)
- DESIGN template:`docs/pm/sanity-check/spec/modules/tc-lifecycle-workflow/sanity-check-tc-lifecycle-workflow-design-spec.md`
- FUNC template:same module functional-spec.md

Test Plan template pending — 首個 pilot feature 建 canonical example。

---

## 13. Open Questions

| # | OQ | Options |
|:---:|:---|:---|
| **OQ-1** | Test Cases format | (a) pytest with docstring(對齊 sanity-check pattern)(b) JSON / YAML declarative (c) BDD Given/When/Then |
| **OQ-2** | Test Plan Spec format | (a) markdown 敘述 (b) YAML declarative (c) 混合 |
| **OQ-3** | G6 executable 100% hard gate carve-out? | (a) 無 carve-out (b) `test_ship_blocking:false` frontmatter opt-out (c) 只 P0 REQ 硬 gate |
| **OQ-4** | Feature-size tier 誰決定? | (a) PM 手動宣 (b) PM Skill auto-detect + propose (c) 混合 |
| **OQ-5** | Living spec edit propose-first 要嗎? | (a) 全部 propose-first (b) 只 REQ 層 (c) 全部 direct + D-XXX log |
| **OQ-6** | Anti-example 必附還 optional? | (a) 每 REQ 必附 (b) recommended only (c) 只 novel pattern 必附 |

---

## 14. Adoption Roadmap

### Short-term(next few sessions)

1. Framework doc landing(this file — v0.1)
2. Pilot on 1 upcoming feature — measure real cost + quality delta
3. Refine templates based on pilot findings

### Mid-term(next month)

4. PM Skill `/pm project-kickoff --size <tier>` 自動生 spec skeleton
5. V7 SCR update:R2 add TP/TC coverage dimension
6. `/pm spec-quality-check <path>` 跑 8-dim rubric

### Long-term(next quarter)

7. 累積 AI agent failure mode taxonomy(from real project findings)
8. Framework 成熟後 abstract 為 「AI agent-friendly project template」

---

## 15. Revision History

| Rev | Date | Author | Change |
|:---:|:---|:---|:---|
| 0.1 | 2026-07-01 | PO + Claude | Baseline draft — 2026-06-30/07-01 PM Skill kickoff discussion consolidated |

---

## 16. See Also

- V7 SCR spec — `docs/pm/v7-spec-compliance-review/spec/scr-requirement-spec.md`(reviewer engine)
- PM Skill spec — `docs/pm/pm-skill/spec/pm-skill-proposal.md`(subcommand router)
- Sanity-check module — `docs/pm/sanity-check/spec/`(validated pilot pattern)
- Spectra-review skill — `~/.claude/skills/spectra-review/SKILL.md`(spec quality review)
- Memory index — `~/.claude/projects/-home-hsuming-AzureLineBOT-main/memory/MEMORY.md`(17 memory rules)
