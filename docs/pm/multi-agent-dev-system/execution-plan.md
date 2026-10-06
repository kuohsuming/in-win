# Multi-Agent 開發系統 — 執行計畫(整合 + 精修)

> **Owner:** PO(kuohsuming)+ Claude(co-author)
> **Status:** Draft(living — 每輪討論後追加)
> **Version:** 0.1(2026-07-03 baseline,捕捉本輪 V1 討論)
> **Source proposal:** 多 Agent 開發系統 Proposal v1.2(external Google Doc)
> **關聯既有:** `docs/pm/spec-authoring/requirement-spec-authoring-rules.md`、`docs/pm/5-spec-authoring-framework.md`、`skills/pm-skill/SKILL.md`

---

## 1. 這份文件是什麼

外部 proposal(v1.2)定義了「用 Claude Code 多 agent 協作開發 LINE Bot SaaS」的**設計**。本文件是它的**執行計畫** —— 捕捉 2026-07-03 V1 討論的結論、與既有 repo 資產的整合、以及待釐清清單。**living document**,逐項修補。

---

## 2. 已鎖定的策略決策(4)

| # | 決策 | 定案 |
|---|---|---|
| D-1 | **範圍** | 跨 repo 方法論,但**先在 Namecard V3 驗證** → agent/rule/command 先 project-level,驗證後 promote 到 `~/.claude/` 跨 repo |
| D-2 | **Agent Teams** | **只用 Subagent**;有自信 + PO 同意才開 Teams(Developing 階段) |
| D-3 | **PM Skill 關係** | 互補分層:**PM Skill 管流程 + 允收標準;本系統管執行面** |
| D-4 | **§6/§9 處置** | **Expand** —— 補齊 functional / design / test-plan / test-case 的 authoring rules(requirement 已建)|

---

## 3. 目標工作流(PO 願景 + 6 精修)

**PO 願景:**
```
你 + Claude → REQ draft(有缺漏、沒 log 全)
   ↓  精修 = Coverage Expansion 舉一反三 + 准入閘門 + 三元組補全 + Spec 階段 agents
多 agent 雙向精修 → close-to-perfect REQ
   ↓  「yes」= 人 PO 關鍵閘門
你 commit「yes」
   ↓
多 agent build application(Developing + Compliance）
```

**6 精修(讓「盲簽可能失控」→「人握方向盤的自動化」):**

1. **「close to perfect」用 gate 定義**,非憑感覺:= 每候選過准入閘門 + 三元組齊 + requirement-reviewer 結構稽核 + 無 orphan。有客觀停止點,不無限精修。
2. **精修是雙向**:補漏 **+** 砍 over-engineering(needs-advocate 加 ↔ resource-manager 砍,誘因對立);不是單純把缺的塞回。
3. ⭐ **「yes」= 逐項差異審核,非盲簽整份**:呈現「加了 A / 砍了 C / 改了 R,各附理由」,PO 逐項 approve/改/reject。**agent 提議,人裁決**(對齊本 session scr 13-REQ sign-off 教訓)。
4. **零 silent**:加的 → decision-log;砍的 → Out of scope + 理由;不確定 → Open Questions;假設 → Assumptions。沒有東西默默出現/消失 → 「yes」才 informed。
5. **迴路非一次過**:yes / reject-with-notes → re-refine → 再審。
6. ⚠️ **build 的 push 前必有人閘**:`push = auto-deploy Azure`(memory);agent **不得**自行 commit+push 上線。

**下游 spec 結構認知:** REQ「yes」後,agent 還要產 Functional / Design / Test Cases 才 build(5-spec)。建議 **(a)** REQ 為 PO 主閘,下游 FUNC/Design/TC 讓 agent 自走 + gate-check 把關,ship 前再一道 push 人閘。

---

## 4. 兩軌架構

### Track A — 5-Spec Authoring Rules 家族(規則層,要 expand)

住 `docs/pm/spec-authoring/`;由 `5-spec-authoring-framework.md §3.1~3.5` operationalize:

| Spec | Rulebook | 狀態 | 核心不變式(triad 對等物,待定)|
|---|---|---|---|
| Requirement | `requirement-spec-authoring-rules.md` | ✅ 已建(2026-07-02.5)| REQ ⇄ golden ⇄ anti 三元組 |
| Test Plan | `test-plan-spec-authoring-rules.md` | ❌ 補 | 每 TP cite REQ;verification method + **非驗證項宣告** + coverage(happy/edge/error/security)|
| Functional | `functional-spec-authoring-rules.md` | ❌ 補 | 每 FUNC cite REQ;user journey + **≥1 failure mode** + data validation + UX justify |
| Test Cases | `test-cases-spec-authoring-rules.md` | ❌ 補 | 每 TC cite TP+REQ;**≥1 positive + ≥1 anti-assertion**(對映 golden/anti)+ **executable** |
| Design | `design-spec-authoring-rules.md` | ❌ 補 | 每 DESIGN cite FUNC;file-impact + interface sig + DB DDL + **migration/rollback** + test seam |

### Track B — 11-Agent 執行層

- `.claude/agents/*.md` × 11(project-level,**Subagent-only**):薄檔 = 行為 + 工具 + 「去讀哪份 rules」
- `.claude/commands/*.md` × 3(`/spec-team`、`/build-team`、`/compliance-check`):封裝接力/並行/退回
- 全部指向 Track A rules + PM Skill gates,不自帶規則
- Writer/Reviewer/User 矩陣(proposal §9.3)= agent ↔ spec 對應

### 兩軌關係
```
Track B(11 agents)= 生產者 ──產出──▶ Track A(5 specs)= 被 rules 治理的產物
                                          ▲
                          PM Skill(流程+gates)在外圈驅動階段轉換
                                          ▲
                          PO 在關鍵節點(REQ yes / push)裁決
```

---

## 4A. 產物路徑 / ID / 格式慣例(Group 1 定案,2026-07-03)

### 路徑(1.1 修訂 — 專案自我包含,零碰撞)

**module 檔 nest 在專案下**(非 top-level `docs/modules/`;後者有跨專案撞名 wart,且本 repo module 不跨專案重用):

```
docs/pm/<project>/
├── spec/
│   └── <project>-requirement-spec.md   ← REQ(project SSOT,triad validator 掃)
├── modules/
│   └── <module>/
│       ├── test-plan.md                ← Test Plan(新)
│       ├── functional.md               ← Functional
│       ├── tests.md                    ← Test Cases(coverage validator 掃)
│       └── design.md                   ← Design(新)
├── decision-log.md
└── state.md
```

- **不建** proposal 的 `docs/specs/`;proposal 的「feature」→ 對映 PM skill「module」
- 跨專案共享 spec(罕見例外)才用 `docs/pm/_shared/modules/`
- **零遷移**:`docs/modules/` 目前空(0 專案到 Phase 4)→ 現在改慣例免費;coverage validator glob 改 `docs/pm/*/modules/*/`

### ID + 引用(1.2)

| Spec | ID | cite-parent 欄位 |
|---|---|---|
| Requirement | `REQ-xxx` | `source_evidence`(root)|
| Test Plan | `TP-xxx` | `covers_req: [REQ-xxx]` |
| Functional | **`FUNC-xxx`**(PO 定案:對齊 framework;既有 validator/tests.md 用 `F-` → 需同步改,見下方連帶影響)| `covers_req: [REQ-xxx]` ⭐**補上輪 spectra C2 的 module→feature 追溯洞** |
| Test Cases | `TC-<module>-<seq>` | `derived_from_acceptance`(→FUNC,PM skill E.1 例改 `FUNC-`)+ 可加 `covers_tp` |
| Design | **`DESIGN-xxx`**(⚠ 不用 `D-xxx`,撞 decision-log)| `covers_func: [FUNC-xxx]` |

> **連帶影響(FUNC-xxx 定案的 reconciliation,零遷移因無真實檔)**:coverage validator `FEATURE_ID` regex `F-` → `FUNC-`;pm-skill-proposal §E.1 `derived_from_acceptance: "F-identity-001"` 例 → `FUNC-`;selftest fixture 同步。列入 Track A/B 實作時一併改。

統一 **`covers_<parent>:` 陣列欄位** = 機器可走的雙向追溯骨幹(REQ→F→TC / REQ→TP→TC / F→DESIGN 全機檢)。

### 格式(1.3 — dual-layer,解 human-first vs 機檢張力)

每份 spec = **人類層(prose 3-role 👔/🔬/💻,可讀)+ machine-block(normative,yaml-fenced,扁平欄位 `id/status/covers_xxx/derived_from_acceptance`)**:

```
## 人類層(human-first)…prose…
## Traceability(machine-block,normative)
  ```yaml
  - id: FUNC-identity-001
    status: done
    covers_req: [REQ-005]
  ```
```

- Track A rulebook **強制 machine-block**;缺 block = **format-mismatch HARD**(對映上輪 B1 guard)
- validator 吃 machine-block(扁平欄位 → 現有 regex validator 直接解)
- **人讀 prose、機器讀 block、缺 block 大聲擋** → 可讀 + 可機檢 + 防靜默 false-pass 三合一

---

## 4B. PM Skill 邊界(Group 4 定案,2026-07-03)

### 總原則:誰 own 什麼

| 層 | Owner | 內容 |
|---|---|---|
| **RULES(法律)** | **Rulebook**(SSOT)| admission §2.5 / triad / 5-spec — 兩邊都查它 |
| **PROCESS + GATES** | **PM Skill** | 8-phase 骨架、gate-check、validate-*、signoff、state.md、phase 轉換 |
| **EXECUTION** | **Agent 系統** | 11 role agents、spawn、authoring/review 勞動 |

一句話:agent 做工 → 產物 → PM skill gate 驗 → rulebook 共同法律。command 在 gate 邊界呼叫 PM skill。

### 4.1 對齊:溶解 3-phase,PM 8-phase 為唯一骨架 + agent roster per phase

proposal 的 3-phase(role-centric)**溶解**;PM 的 8-phase(artifact/gate-centric)為 canonical。agents 插進每個 PM phase:

| PM Phase | 產物(5-spec)| Active agents | command |
|---|---|---|---|
| **0 Requirement** | REQ spec | needs-advocate → tech-architect → resource-manager → requirement-reviewer | `/spec-team` |
| **1 Structuring** | FUNC / DESIGN / Test Plan + modules | solution-architect(DESIGN)、ux-ui-designer(FUNC/UX)、qa-automation(TP)、resource-manager(FUNC co-write)、requirement-reviewer | `/spec-team`(延伸)|
| **2 Plan** | work plan | resource-manager / solution-architect | `/build-team` 起手 |
| **3-4 Code + TC** | code、Test Cases(tests.md)| backend / frontend-engineer、qa-automation(TC)| `/build-team` |
| **4-5 Compliance** | review / validate / G6 | code-reviewer ×N、qa、requirement-reviewer | `/compliance-check` |

- ⭐ **角色搬動**:solution-architect / ux-ui-designer 從 proposal 的 Developing **移到 Phase 1 spec-authoring 側**(作者在 P1、消費者 engineers 在 P3-4,比原文正確)
- ⭐ **5-spec 非同時產**:REQ(P0)→ FUNC/DESIGN/TP(P1)→ **TC 跟 code(P4)**
- ⭐ **collaboration-shape(subagent/teams)暫 moot**(D-2 subagent-only);開 Teams 時再逐 phase 決定(如 P3-4 engineers 並行才需)

### 4.2 command = phase-cluster 便利包裝,呼叫 /pm 委派 gate

- `/spec-team` = Phase 0-1(REQ + FUNC + DESIGN + TP)
- `/build-team` = Phase 2-4(plan + code + TC)
- `/compliance-check` = Phase 4-5(review + validate + G6)
- 每個 command:**spawn 該 phase agents + 在 gate 邊界呼叫 /pm**(validate-* / gate-check / signoff / advance-phase);**不平行、不重造 gate**;不教條綁剛好 3 段
- 深度整合(`/pm advance-phase` 自動 spawn 該 phase roster)= **defer**,驗證期手動

### 4.3 admission / sign-off 執行者

- **admission(5-test)**:RULE = rulebook §2.5(SSOT);EXECUTOR **依入口** —— agent 系統 → **resource-manager agent**;`/pm` 直接 → P3c subcommand。同規則兩執行者(defense-in-depth)
- **sign-off(§5.5)**:兩級 —— **agent 級 advisory**(resource-manager / qa-automation / engineer role-review)+ **人 PO 級 authoritative**(REQ 逐項差異審核 OD-D)。**人 PO 簽 = 權威閘**(接 Group 6.1)

### 邊界圖
```
PO ─(REQ 逐項審核 / push 人閘)──────────────┐ 權威裁決
                                             ▼
/spec-team /build-team /compliance-check ─── agent 編排(spawn 11 roles)
   │  在 gate 邊界呼叫 ▼
PM Skill ── process 骨架 + gate-check + validate-* + signoff + state
   │  查 ▼
Rulebook ── admission §2.5 / triad / 5-spec(SSOT)
```

---

## 4C. 人的控制點(Group 6 定案,2026-07-03)

### 設計原則:少而準的人閘 + 隨時可搶方向盤 + 全程可稽核

**人閘越少越準,PO 控制感越強**(不被淹沒 + 該管的管到)。控制 = 「**必簽 2 點**」+ 「**能查全部**」+ 「**能搶任何點**」。

### 6.1 agent 簽還人簽

| 產物 | 誰簽 |
|---|---|
| **REQ spec** | 🔴 **人 PO**(逐項差異審核,OD-D)|
| FUNC / DESIGN / TP / TC | 🟢 agent(role-review)+ gate-check backstop |
| code / compliance / G6 | 🟢 agent + validator/gate |
| **ship / push to main** | 🔴 **人 PO**(auto-deploy Azure 防線)|

下游 = agent 簽,**兩例外拉人**:(a) `risk_class ∈ {safety,data,compliance,金流}` → 下游也要人 review;(b) ship/push 一律人。

### 6.2 人介入節點清單

| 節點 | 人? | 型 |
|---|---|---|
| admission(每候選 5-test)| 🟢 agent(resource-manager)跑;**不逐條即時批**,outcomes 折進 REQ 閘一起看;PO override anytime | folded |
| **REQ sign-off** | 🔴 **HARD**(逐項差異審核)| 意圖閘 |
| tier confirm | 🟡 light(agent auto-detect + 人一鍵確認/覆寫,§9.5)| 輕閘 |
| FUNC/DESIGN/TP/TC | 🟢 agent + gate;🟡 人 IF high-stakes | 條件 |
| code / impl-review / compliance | 🟢 agent + validator | 自走 |
| **ship / push** | 🔴 **HARD**(auto-deploy 防線)| 部署閘 |
| reject / delete / override | 🔴 人(delete = PO-confirm,rulebook)| on-demand |

**淨結果:2 硬閘(REQ、ship)+ 1 輕閘(tier)+ 條件閘(high-stakes)+ 其餘自走。**

### REQ 閘呈現 = 人話 prose delta(非格式化欄位)⭐

接 §4A dual-layer:REQ 閘給 PO 看的是**人類層 prose**(白話「是什麼/為何加/影響/不涵蓋什麼」),**非** yaml 欄位:
```
本輪 REQ 變更(3 項),逐項裁決:
① [新增] 用戶可匯出單筆好友筆記
   為何:你提到私訊前想快速回顧一則 · 影響:P1 · 不涵蓋:批量、私人 comments
   [✔ 收 / ✎ 改 / ✘ 退]
② [砍] 退款手續費計算 — 超出「全額退款」範圍(YAGNI)→ Out of Scope  [✔ 砍 / ↩ 救回]
③ [改] 退款時效 7→14 天 — 金流對帳週期需 14 天  [✔ 收 / ✎ 改 / ✘ 退]
(想看正式 spec 欄位?→ drill-down REQ-042)
```
**預設人話,drill-down 才看 yaml** → PO 的「yes」是理解後的 yes。

### Standing Interrupt 機制(搶方向盤,任何點可用)

**4 動作**:`pause`(停+改方向)/ `kill`(砍某 agent)/ `override`(改某決定)/ `inspect`(只讀不停)。**不限閘口,agent 自走時隨時可用。**

**機制(怎麼實現的)**:orchestrator(跑 command 的主 session)可被 PO **隨時中斷**;所有 agent 產出 = **檔案**(原則六)PO 隨時讀;中斷後給新指令 → orchestrator 重新導向。

**情境例**:
- `/build-team` 中,backend-engineer 用**未授權金流 API** 在寫 → PO `kill` → 澄清 → re-spawn(防燒 token + 錯 code)
- Spec 中 resource-manager 判退你想要的候選 → PO `override: admit`(記 log)→ 收進去(免等 REQ 閘才救、下游已分岔)

> ⚠️ 誠實限制:**並行**階段(compliance 多 reviewer)中斷較亂,但每 subagent 獨立、輸出獨立檔,kill 一個不壞其他;**接力**階段(Spec)最乾淨 —— 也是驗證期 subagent-only 的好處。

---

## 4D. Test Plan rulebook 定案(Group 2 — TP,2026-07-03)

> Track A 4 份 rulebook 的第一份細化。其餘(FUNC/TC/DESIGN)待後續。

### 貫穿原則:每層宣告「正面 + 負空間」

REQ 三元組(golden 正 + anti 邊界)的模式一路貫穿 5 層:每份 spec 同時宣告**正面內容 + 明確負空間**(防 silent-gap)。**sizing atom + 超過就拆** 也全層一致:

| Spec | sizing atom | 正面 | 負空間 |
|---|---|---|---|
| Requirement | 1 golden_scenario | golden_scenario | anti_examples |
| **Test Plan** | **1 claim(golden 或 1 anti)** | positive TP | boundary TP + non-verification 宣告 |
| Functional | 1 user journey | happy journey | ≥1 failure mode |
| Test Cases | 1 Given/When/Then | positive assertion | anti-assertion |
| Design | 1 component 變更 | file-impact+signature | migration/rollback |

### TP sizing:1 TP = 1 claim

- **1 TP = 1 個可測 claim = golden_scenario **或** 一個 anti_example**(二選一,不 bundle)
- **痛點(pain point)不算 sizing 單位**(它是 why,不直接測);可測的是 golden(正)+ anti(邊界)
- **area 是標籤非 atom**(從 claim 推:golden→happy;anti 講空狀態→edge;anti 講 PII→security)
- 每 REQ 的 TP 數 = **1(golden)+ N(anti_examples)** —— REQ 三元組直接決定 TP 集合
- 拆分規則:一個 TP 混了 >1 claim → 拆

### 雙向基數(PO 修正)

- **⬇️ 向下(覆蓋 fan-out)**:`REQ ─1:m─▶ TP ─1:n─▶ TC` ⟹ **REQ:TP:TC = 1:m:n**
- **⬆️ 向上(trace,每手恰 1 parent)**:`TC ▶ TP ▶ REQ` ⟹ **TC:TP:REQ = 1:1:1(唯一 parent 鏈)**
- **cite-parent 單值**:`TP.covers_req` = 恰 1 REQ + claim;`TC.covers_tp` = 恰 1 TP(0 或 >1 → validator fail)
- ⚠️ **別假設全 5 層 up 都 1:1:1**:FUNC 可能 cover 多 REQ(m:n up),談 FUNC 時再定

### REQ→TP→TC 全鏈對映
```
golden_scenario ──▶ positive TP ──▶ positive-assertion TC
anti_example #k ──▶ boundary TP ──▶ anti-assertion TC
```

### TP schema(dual-layer)

**machine-block**:
```yaml
- id: TP-012
  covers_req: REQ-005       # 單值
  claim: golden             # golden | anti#k → 合成 claim ID = REQ-005.golden ⭐
  # ↑ covers_req + claim = 統一 claim ID「REQ-005.golden」= 三角互驗共同單位
  #   (REQ 擁有 / TP verifies 此 claim / FUNC realizes|handles 此 claim,三者共享,見 §4G)
  area: happy               # enum: happy|edge|error|concurrent|security|performance
  validation_key_point: "匯出產生 PNG,含該則文字+時間,檔 < 500KB"  # ⭐ 必 observable + trace REQ acceptance
  verification_method: integration   # unit|integration|ui|load|manual
  test_data_source: real-corpus(anonymized)
  environment: real-device-ios/android   # ⭐ 本 repo:LINE WebView 關鍵
  priority: P1
```
**人類層(description)**:白話「這 TP 驗什麼」(base on golden/anti)。

**anti 例**:`claim: anti#2` / `area: security` / `validation_key_point: "匯出 payload 不含任何 card_comments 欄位"` / `priority: P0`

### 關鍵規則
- **`validation_key_point` = TP↔TC 契約**:必 **observable/measurable**(❌「運作正常」)+ **trace 回 REQ acceptance / golden 的 Then**(不自己發明)。這防不可測 TC(spectra R2 教訓)
- **TP = 策略非具體**:只放 validation_key_point,**不放 test steps**(那是 TC 的事)—— 守住不變 TC 複本
- **area 集合 = risk-weighted**:`risk_class ∈ {safety,data,compliance,金流}` → **error + security TP 強制**;normal → happy(+edge);不適用 area → 宣告 non-verification

### Gate + Dashboard(先做 TP 這層,option a)
- **Gate**:每 REQ ≥1 TP(HARD;0 = 未驗需求)
- **Dashboard**:REQ × TP count + **area 覆蓋矩陣**(count 是虛榮指標,area 完整性才是真信號)
```
REQ-005 匯出單筆筆記 | TP:3 | areas: happy✓ edge✓ security✓ error✗⚠
REQ-006 批量匯出     | TP:0 ❌
```
- 人話呈現(非 yaml);全鏈 dashboard(REQ→TP→TC→FUNC→DESIGN)等 5 份 spec 齊再做

---

## 4E. Work-item — sanity REQ→TP→TC 全鏈重做(pilot,2026-07-03)

> sanity-check 現況「走偏」:REQ→TC 直產(TP 折疊進 tc-*.json 的 `validate.prompts` + `system_state_assertions`),缺顯式 TP 層 → 人不知道測啥、Claude 易漂移。修正為 **REQ→TP→TC 三層鏈**,全 follow spec rules。

### 為何要 TP 層(anti-drift + 可理解)
- REQ 直接爆 M×N 個 TC = 無政府 pile;**TP = 「該驗什麼」(少、可審)與「怎麼測」(多、生成)之間的意圖錨**
- **對 Claude(機械防漂移)**:TC 從 TP 生 + 必 cite TP(covers_tp)+ 每 TP≥1 TC / 每 REQ claim≥1 TP → validator 抓 orphan/gap;validation_key_point observable → 無 vague TC
- **對人(可理解)**:先審 TP 計畫(3 個)而非 TC pile(40 個);TP dashboard 可視 + standing interrupt 可搶方向盤;不加 mandatory 硬閘(high-stakes 才條件審)

### 流程(top-down 全鏈重做,PO 選)
```
修訂 REQ(小,triad 已 backfill)→ gate-check
  → 寫 TP(每 claim 1 個,validation_key_point observable + trace REQ acceptance)→ validate
  → 重生 TC(參考既有 53 + follow TC rules:cite TP、positive/anti-assertion、executable)→ validate + lint.sh
  → 全綠 → swap
```

### 4 安全 guard(sanity 成熟 + CI-gating,不能弄壞)
1. **重生參考既有 53 TC**(真實測試知識 corpus)—— 不從零盲生,防丟失邊界案例 / 倒退
2. **worktree/branch 做,新鏈綠了才換**:`bash lint.sh` Stage 3/4 + 新 REQ↔TP、TP↔TC validator 全綠才 swap
3. **保 tc-*.json executable 豐富度**:TC rules 映射到既有 schema(positive→`system_state_assertions`、anti→反向斷言、`validate.prompts`、`test_steps`)—— 不發明新格式弄壞 runner
4. **分階段每步 validate**;REQ 改動應小,大 delta 在 TP(新)+ TC(reconform)

### 雙贏定位
修正 sanity + 成為 5-spec **reference implementation** + 當場暴露 rule 漏洞 + 補「無真實 functional.md/tests.md 可測」洞。**當獨立 work-item/mini-project**,動工時可 spin 自己的 spec doc(用 sanity 自己的嚴謹度對待)。

---

## 4F. Test Cases rulebook 定案(Group 2 — TC,2026-07-03)

> **結論:TC 幾乎不用新造** —— sanity 的 24-field TC schema(REQ-004 semantic invariant + REQ-019 format SSOT)已在真機驗證且極豐富,直接當 project-agnostic TC schema 基底。只 ADD 一個 + ALIGN 一條。

### TC 完整元素清單(從 sanity 24-field 一般化 + `covers_tp`,self-contained)

**🔑 Identity + Traceability**
| 欄位 | 必 | 說明 |
|---|---|---|
| `id` | ✅ | `TC-<module>-<seq>` |
| **`covers_tp`** | ✅ **⭐NEW** | **單值**,cite 父 TP → 透傳 TP.claim + REQ(TC→TP→REQ 1:1:1;0 或 >1 → validator fail)|
| `legacy_id` | ○ | migration 舊 ID 保留 |

**📝 Content(人類層,3-role)**
| 欄位 | 必 | 說明 |
|---|---|---|
| `title` | ✅ | 1 行 |
| `description` | ✅ | 完整敘述 |
| `qa_notes` | ○ | QA 敘述;**PII scrub** |
| `category` | ✅ | 專案 domain enum(各專案自訂)|
| `priority` | ✅ | P0/P1/P2 |
| `operation_type` | ✅ | CRUD enum |
| `tags` | ○ | smoke/regression… |

**▶️ Executable — steps**
| 欄位 | 必 | 說明 |
|---|---|---|
| `preconditions` | ○ | `{type, description}` |
| `test_steps` | ○ | `{step_num, action, qa_focus}` |
| `target`(navigation)| ○ | 一般化 sanity `target_spa_path/strategy/url` — 怎麼到達測試面(專案特定)|

**✅ Executable — assertions(承重)**
| 欄位 | 必 | 說明 |
|---|---|---|
| `validate.prompts` | ✅ | 人 Q&A `[{q, yesPass}]` |
| `state_assertions` | ○(強烈建議)| 一般化 sanity `system_state_assertions` — 機器 DSL(db_row/ui_state/api,**可觀察非內部**);`expected_count: 0` = anti-assertion |

**🧪 Test data**
| 欄位 | 必 | 說明 |
|---|---|---|
| `test_data` | ○ | 一般化 `fake_data`:`{field: [{value, label, intent, scenario, expected}]}` |
| — `intent` enum | | `{positive|negative|boundary|injection}` ⭐ **必與父 TP.claim 一致** |
| — PII 規則 | | `label` regex `^[a-z]+-[a-z0-9-]+$` + `TEST_FAKE_` + `cleanup_after` |

**🔧 Meta**:`execution`(pass/fail/skip,CI 回填)/ `skip` / `dependencies`

### 疊在元素上的規則(rulebook 靈魂)
1. `covers_tp` **單值**(0 或 >1 → validator fail)
2. `intent` ↔ 父 TP.claim **一致**(golden→positive / anti→negative/boundary/injection + `expected_count: 0`)
3. assertions **只斷言可觀察**(UI/DB/API),禁內部 method call(refactor-safe)
4. **no PII**(label regex + qa_notes scrub + `TEST_FAKE_` + cleanup)
5. **executable + G6 分層**(P0 100% hard / P1-P2 ≥95%)
6. assertion 極性**跟隨 TP**(不每 TC 硬塞 anti;anti 覆蓋靠基數,§4D)

### 清理
`related_feature`(鬆散)→ 被 `covers_tp` 取代;`subject` 已 deprecated

### Executable + G6
- 執行器 = sanity 既有 dispatcher(validate.prompts + system_state_assertions 真機跑)
- **G6 分層(§9.4)**:P0 REQ 的 TC = **100% hard gate**;P1/P2 = ≥95%(避免 LINE API flaky 卡非關鍵 ship)

### 一句話
**TC schema = sanity 24-field(SSOT)+ `covers_tp`(唯一 ADD)+ intent↔TP 一致性檢查。** 證明 sanity 是好的 reference impl —— 缺的只有 traceability,正是 sanity work-item(§4E)要補的。

---

## 4G. Functional rulebook 定案(Group 2 — FUNC,2026-07-03)

### 三角互驗:共同單位 = claim(統一 ID `REQ-<id>.<golden|anti#k>`)

REQ / FUNC / TP **任兩個驗第三個**,前提 = 三者共享 claim。**統一 claim ID:`REQ-005.golden` / `REQ-005.anti#2`**:
- **REQ** 擁有 claim(golden + N anti)
- **TP** verifies 1 claim(1 TP = 1 claim)
- **FUNC** `realizes`(golden)/ `handles`(anti)

| 用哪兩個 | 驗第三個 | 機械檢查(對照 claim 覆蓋)|
|---|---|---|
| REQ + FUNC | **TP** | FUNC realizes/handles 的每 claim → 必有 TP;否則 TP 漏 |
| REQ + TP | **FUNC** | 每有 TP 的 claim → FUNC 必 realizes/handles;否則 FUNC 漏 |
| FUNC + TP | **REQ** | FUNC/TP 的 claim → 必都是 REQ 宣告的;否則 REQ 漏 / gold-plating |

### FUNC = 1 user journey;covers_req = list(m:n)

**兩子結構,兩基數**:
- **測試側 REQ→TP→TC**:下 1:m:n / **上 1:1:1(唯一鏈)**
- **行為/建構側 REQ→FUNC→DESIGN→Code**:**m:n mesh**(流程/元件天生共用)
- 兩者在 **TC↔FUNC 交叉連**(TC `derived_from_acceptance`→FUNC)

### 正面 + 負空間 + 靈魂 guard
- 正面:journey(realizes golden);負空間:**≥1 failure_mode**(handles anti)
- **禁 silent modality shift**:每個行為必 trace 到 claim;realizes 不到任何 claim 的 outcome = 憑空多做
- 新 UX pattern 必 justify

### ⭐ 結構化 per-step + 追溯線下沉到程式碼註解

FUNC **不是散文**(散文只有 Claude 讀得順)。每步/每 failure_mode = **帶 claim 引用的可觀察行為單位**,讓追溯一路流到 code:

```yaml
user_journey:
  - step: 3
    action: 點「匯出」→ 系統產生單則 PNG → 彈出分享 sheet
    observable: PNG 生成 + 分享 sheet 顯示
    realizes: REQ-005.golden          # claim 引用跟著這一步
failure_modes:
  - id: FM-1
    handles: REQ-005.anti#2
    trigger: 筆記含私人 card_comments
    response: 匯出 payload 過濾 card_comments
    user_message: (silent)
```

**追溯鏈一路到程式碼註解**:
```
REQ-005.golden → FUNC-export-note.step-3 → DESIGN.exportNoteToPng()(@implements)→ code 註解
```
```python
def export_note_to_png(note_id):
    """
    @implements FUNC-export-note.step-3 (realizes REQ-005.golden): 產生單則 PNG
    @enforces   FUNC-export-note.FM-1  (REQ-005.anti#2): 過濾 card_comments,防外洩
    """
```
- **好處**:程式碼可讀(function 自帶「實現哪個需求」)+ 人可 debug/review + 防危險 refactor(看到 @enforces 就知牽動需求)+ validator 檢 `@implements` 指向存在的 FUNC step
- **延伸 repo 既有 `@governed-by`(檔案層,ddd-doc-maintenance §3.6)→ function 層**(`@implements FUNC-xxx.step-N`)

### FUNC schema(dual-layer)
| 欄位 | 必 | 說明 |
|---|---|---|
| `id` | ✅ | FUNC-xxx |
| `covers_req` | ✅ | **list ≥1**(m:n)|
| `user_journey` | ✅ | **結構化 steps**:每步 `{step, action, observable, realizes: <claim>}` |
| `failure_modes` | ✅ | ≥1;每個 `{id, handles: <claim>, trigger, response, user_message}` |
| `data_validation` | ○ | input format / boundaries / error template |
| `ux_pattern` | ○ | reuse 或 justify NEW |
| `integration_points` | ○ | external API / 他 module 契約(必 cite)|
+ 人類層 prose(3-role)+ machine-block。**不含 test scenarios**(TP/TC 的事)。

---

## 4H. Design rulebook 定案(Group 2 — DESIGN,收尾 Track A,2026-07-03)

### DESIGN 的雙重上游約束(PO:滿足 FUNC + TP)

- **對 FUNC = 實作**:DESIGN 直接實作行為(每 `FUNC.step / failure_mode` → DESIGN component,`@implements FUNC-xxx.step-N`)
- **對 TP = 可驗(非實作)**:TP 是驗證策略,DESIGN **不 implement TP**,而是 **expose `test_seam`** 讓 TC 能斷言 TP 的 `validation_key_point`
- **一句話**:DESIGN 實作 FUNC 的行為 + expose seam 讓 TP 的允收標準可被驗證 + 宣告自己的 build contract

### DESIGN = 行為(FUNC)× 驗證(TP)在同一 claim 上的收斂點
```
REQ-005.golden (claim)
  ├─ FUNC-export-note.step-3   realizes  (行為)
  ├─ TP-012                    verifies  (驗證 validation_key_point)
  └─ DESIGN.exportNoteToPng()  @implements step-3 + test_seam 讓 TP-012 驗得到
```
**每個 claim,DESIGN 都要同時有「怎麼做(implements)」+「怎麼驗(test_seam)」。**

### ⭐ 完整性不變式(PO 補充:cover all FUNC + TP items,雙向)

| 對象 | top-down(cover 全)| bottom-up(禁 gold-plating)|
|---|---|---|
| **FUNC ↔ DESIGN** | 每 `FUNC.step/FM` → 必有 ≥1 DESIGN `implements`(無未實作行為)| 每 `implements` → 指向存在 FUNC step(無憑空多做)|
| **TP ↔ DESIGN**(via `test_seam`)| 每 `TP.validation_key_point` → 必有 `test_seam.for_claim`(無不可驗允收)| 每 `test_seam` → 指向存在 TP claim |

→ 兩邊在 DESIGN 這層 close;**進 code 前就保證:所有行為被設計 + 所有允收可驗**。gap 在**設計時**抓(對映 framework G4,但提前到設計階段)。

### DESIGN schema(dual-layer)
| 欄位 | 必 | 說明 |
|---|---|---|
| `id` | ✅ | DESIGN-xxx(不用 D- 避撞 decision-log)|
| `covers_func` | ✅ | **list ≥1**(m:n;元件常跨 FUNC 共用)|
| `implements` | ✅ | `[FUNC-xxx.step-N, FUNC-xxx.FM-k]` → 程式碼註解 `@implements`(claim-transitive)|
| `file_impact` | ✅ | 建 / 改 / 刪哪些檔 |
| `interface_signatures` | ✅ | 真型別(非 pseudocode)|
| `db_schema` | ○(涉 schema 則必)| ALTER TABLE DDL |
| `migration_rollback` | ○(schema/config 變則**必**)| migration + rollback path |
| **`test_seam`** | ✅ | ⭐ `[{for_claim, exposes}]` —— 讓 TP validation_key_point 可驗;設計時檢每 TP claim 有 seam |
| `performance_budget` / `security` | ○ | Q95 latency / mem;input sanitize / auth / PII |
+ 人類層 prose(3-role)+ machine-block

### 連帶:coverage validator 家族湊齊
```
REQ↔TP · REQ↔FUNC · TP↔TC · FUNC↔DESIGN(implements)· TP↔DESIGN(test_seam)· DESIGN↔Code(@implements 註解)
```
—— 整條 cascade 的雙向覆蓋(gap + orphan)全機檢。

### 最終版(PO 那句話)
> **DESIGN 必須 cover 全部 FUNC items(implements,不多做)+ 全部 TP items(test_seam,不多做);每個 claim 在 DESIGN 這層同時有「怎麼做」與「怎麼驗」;gap 在進 code 前就被抓。**

---

## Track A 規則層 — 5 份全定案 ✅

| Spec | 定案 | 核心 |
|---|---|---|
| Requirement | rulebook 已建(spec-authoring/)| REQ ⇄ golden ⇄ anti 三元組 |
| Test Plan | §4D | 1 TP=1 claim;validation_key_point;雙向 1:m:n / 1:1:1 |
| Test Cases | §4F | 沿用 sanity 24-field + covers_tp;G6 executable |
| Functional | §4G | covers_req list(m:n);結構化 step realizes/handles;@implements 下沉程式碼 |
| Design | §4H | 實作 FUNC + expose test_seam 驗 TP;完整性不變式(cover all,雙向)|

**貫穿全 5 層**:共同單位 = claim ID(`REQ-<id>.<golden|anti#k>`);每層宣告「正面 + 負空間」;三角互驗(REQ/FUNC/TP)+ cascade 雙向覆蓋 + 追溯下沉程式碼註解。

---

## 4J. Track B 執行機制定案(Agent schema + 只審不改 + 退回迴路,2026-07-03)

### Agent 檔 schema(標準 Claude Code 格式)
```markdown
---
name: <全域唯一>
description: <何時 spawn 這角色>
tools: <per-role 權限;省略=繼承全部>
model: <per-role,控成本>
---
<system prompt:角色行為 + 「去讀哪份 rules」+ 輸出契約(寫哪路徑/格式/下一手)>
```

### 11-agent tool matrix + 只審不改

| Agent | 型 | tools | 只審不改 |
|---|---|---|---|
| tech-architect | advisory | Read/Grep/Glob | ✅ **tool 硬強制** |
| requirement-reviewer | reviewer | Read/Grep/Glob | ✅ **tool 硬強制** |
| code-reviewer | reviewer | Read/Grep/Glob | ✅ **tool 硬強制** |
| needs-advocate | author | +Write | 作者本該可寫 |
| resource-manager | author | +Write | 作者 |
| solution-architect | author | +Write | 作者 |
| ux-ui-designer | author | +Write | 作者 |
| backend-engineer | author | +Edit/Write/Bash | 作者 |
| frontend-engineer | author | +Edit/Write/Bash | 作者 |
| qa | runner | Read/Grep/Glob **+Bash** | ⚠️ Bash 可繞 |
| qa-automation | test author | +Edit | ⚠️ 無法 path-scope「只改測試」|

### 只審不改 enforcement(大半硬,兩個軟補)
- **純 reviewer(3 個)= tool 完全強制**(無 Edit 無 Bash → 物理改不了)
- **qa / qa-automation**(需 Bash/Edit)→ **軟補**:①prompt 紀律(system prompt 硬性「禁碰 src/js/*.py 產品碼」)②**post-step `git diff --name-only`**:agent 跑完,orchestrator 檢有無碰不該碰的檔 → flag + 退回;③(可選)PreToolUse hook 攔 Edit 檢 path(hook 能否知發起 agent 待驗)

### 退回迴路(findings 檔 + orchestrator re-spawn,跨 context)
subagent 不共享 context → 靠**檔案 + orchestrator 中轉**(原則六):
```
1. author subagent   → 寫 artifact 檔
2. reviewer subagent → 讀 artifact → 寫 findings 檔
3. orchestrator      → 讀 findings
      ├─ 有 → re-spawn author(全新 instance)帶 {artifact, findings} → 修 → 寫回
      │        → re-spawn reviewer 複查 → 回 3
      └─ 0 → 過,進下一階段
```
- author 每輪**全新 instance,從檔案重建 context**(非記憶)—— 即本 session spectra→fix 迴路 pattern
- **findings 檔 schema**:每筆 `{id, severity, location, issue, suggested_fix}`
- **max-rounds = 3**:觸頂不收斂 → **escalate 人**(防無限迴圈)
- **收斂追蹤**:findings ID → author 回報哪些修 → orchestrator 對照
- **人的位置**:退回迴路 **agent 自走**(不佔人閘,Group 6);只 max-rounds 觸頂拉人;standing interrupt 隨時可 inspect findings 檔

---

## 4K. Command 編排 + 交接 + 狀態 + non-blocking 分層(Group 3.3 + 5 定案,2026-07-03)

### Non-blocking 分層(PO 澄清)⭐
```
使用者前門(便利層,新)   /spec-team · /build-team · /compliance-check
        │ 呼叫(委派)
後端機房(退到後面)       /pm · /pm sanity-* · validators · gate-check
        ▲
使用者「仍可直接呼叫後端」← 不阻擋
```
- 前門 = 高階編排(spawn agents + gate 邊界呼叫 /pm);一般使用走這
- `/pm`、`/pm sanity-*` 退到後面當機房,但**人隨時可直接跑**(不藏不禁)
- **加法便利,不是圍牆**:debug / power-user / 遷移期 都可直接動後端(對齊 D-3 + Group 6 隨時搶方向盤)

### Command 編排(`/spec-team` 模板,其餘同構)
```
/spec-team <feature>:
1. 取 project context(/pm 現行專案 or new-requirement)+ 寫進度 state.md
2. Phase 0(REQ):
   a. spawn needs-advocate → 寫「候選池」檔
   b. spawn tech-architect → 讀候選池 → 寫「技術評估」檔
   c. spawn resource-manager → 讀兩者 → 准入閘門 → 寫 REQ spec(含 claim ID)
   d. spawn requirement-reviewer → 讀 REQ → 寫 findings 檔
   e. 退回迴路(§4J):findings → re-spawn resource-manager 帶 findings → 修 → 複查(max 3)
   f. 呼叫 /pm validate-req-spec + gate-check phase-0(§4B 委派)
   g. 逐項差異審核(人閘)→ PO yes → /pm signoff phase-0
3. Phase 1:同構(solution-architect / ux-ui-designer / qa-automation…)
```
= 逐階段 spawn(§4B roster)+ 檔案交接 + 退回迴路(§4J)+ gate 邊界呼叫 /pm(§4B)。

### 檔案交接 header(延伸既有 `@governed-by`,不新造)
```
<!--
@produced-by: needs-advocate
@covers: REQ-005 (feature: 匯出筆記)
@next: resource-manager
@governed-by: docs/pm/spec-authoring/requirement-spec-authoring-rules.md
-->
```
下一手 agent 一讀就知「誰產的 / 對應啥 / 我該接 / 依哪份 rules」。

### 狀態/進度(重用 `state.md`,擴 agent 層,不新造)
```yaml
current_phase: 0
agents: {needs-advocate: done, tech-architect: done, resource-manager: in-progress}
retback_rounds: 1
findings_open: 2
```
- standing interrupt 的 `inspect` 讀這個;re-spawn author 從 state + artifact 檔重建 context(§4J 不靠記憶)

---

## 4L. 命名統一 / 切分 / 驗證 / 預算(Group 7/8 定案,2026-07-03)

### Group 7 — 命名統一表
| 類 | 命名 |
|---|---|
| spec ID | `REQ-xxx / TP-xxx / FUNC-xxx / TC-<module>-<seq> / DESIGN-xxx`(不用 D-)|
| claim ID | `REQ-005-G1 / A1 / P1`(穩定、單調、不重用、不 reindex)|
| cite 欄位 | `covers_req / covers_tp / covers_func / for_claim` |
| FUNC 掛 claim | `realizes`(golden)/ `handles`(anti)|
| 追溯註解 | `@governed-by / @produced-by / @covers / @next / @implements / @enforces` |
| 路徑 | `docs/pm/<project>/{spec, modules/<module>}` |

**2 修正**:
1. **TC 兩上游 link 命名對齊**:canonical = `covers_tp`(→TP 策略)+ **`covers_func`**(→FUNC 行為);sanity 既有 `derived_from_acceptance` 當 alias,sanity 重做時對齊
2. proposal 的 `docs/requirement-rules.md` = 我們的 **`spec-authoring/` 5 份家族**;統一入口到後者,不建前者

### Group 8.1 — universal vs repo-specific 切分
| | 內容 | 放哪 |
|---|---|---|
| **Universal**(可 promote `~/.claude/`)| 5-spec rules、11 agent **行為**、3 commands、validators、claim-ID/三角機制 | 通用核心 |
| **Repo-specific**(留 project)| Namecard 領域(LINE WebView / BCT / profile-bizcard invariant / memory)、category enum、target 導航、各專案 specs | 專案 context |

**原則:agent 不 hardcode Namecard 領域**,領域從 **CLAUDE.md + memory + 專案 spec** 注入 → agent 天生 generic。**day 1 就寫 generic**,promote 時搬核心、留 context。

### Group 8.2 — 驗證(兩階段)
1. **sanity REQ→TP→TC 重做(§4E)** = 驗 **Track A 規則**於真實 spec(不動 agent/code)
2. **一個小而完整真 feature** = 驗 **Track B 全 pipeline**;準則:小 + 完整 + 真 + 低風險。**feature 到那步 PO 選**(roadmap 候選:Phase 3.4 outreach log 讀 / account-switch / friend-card-update)

### Group 8.3 — token 預算 guardrail
1. subagent-only(D-2,已避 Teams 數倍)
2. **per-agent model tiering**(§4J):reviewer/runner 便宜(haiku/sonnet)、judgment(resource-manager/solution-architect)opus
3. max-rounds=3(退回,已定)
4. **log spend + 超標 alert**(對齊 `[[user-working-style]]` cost-conscious)
5. **measure-first**:先 1 feature 量真實成本再 scale

---

## 4M. Build 順序(planning 完 → 動工,measure-first)

1. **Track A 真檔** ✅ **全 done(5/5)**:`requirement`(+§3.4 claim-ID D-028)· `design`(§3+§4,9 輪 spectra)· `test-plan`(§4D,含 vkp-ID)· `test-cases`(§4F)· `functional`(§4G,D-031)—— 5-spec rulebook 家族齊
2. **sanity pilot(§4E)**:REQ→TP→TC 重做 = 驗規則於真實資料
3. **reconciliation**:FUNC-xxx validator regex + coverage glob(`docs/modules/*`→`docs/pm/*/modules/*`)+ TC covers_func
4. **Track B**:11 agent 檔 + 3 commands + **⚠️ coverage validators A.1-A.4 已 landed**(spine / REQ↔TP↔TC / FUNC↔DESIGN↔TP↔DESIGN↔Code file_impact / staleness;lint Stage 6-9;守 proposal §9 H1-H6)—— 剩 **`@implements` 註解 code-scan validator**(=A.5,stdlib,propose-first)+ **builder build-mode(disambiguation-up + TP-driven,§4O)+ debug-mode + delta 收集器 + carve-out pre-gate(§4N)+ spine-gap flag(§4O)**

**先 1+2**(規則落地 + 真實驗證),穩了再 3+4。全程 propose-first 對 `.py`(backend-change-rule)+ 逐 rev(incremental-rev-cascade)。

---

## 4N. Runtime Debug Flow（builder debug-mode + 上溯 + delta 事後審,2026-07-04）

> **問題**:agent 怎麼(a)照 DESIGN/TP **往下 build**,同時(b)出 bug 時**往上溯** FUNC/REQ 找 root cause、在對的層修。**答案**:同一條追溯脊椎(claim-ID + `covers_` + `@implements` + `test_seam`)兩個方向用 —— build 往下、debug 往上。
> **本節詳 debug 方向(執行後);build 方向(建構期照 DESIGN 建 + 不清上溯 + TP-driven)見 §4O。**

### 定案模型(PO)

**單一 builder agent 切 debug-mode**:沿 `@implements` 上溯定缺陷層 → 在**缺陷起源層**修 → 往下 cascade 到綠。**spec 層改動(DESIGN/FUNC/REQ)彙整 delta,事後逐項人審(OD-D)**;純 code fix 靠 G6/validator 綠,不進 delta。
(決策②覆蓋①:**不 route 出去**,同一 agent 各層自修,只是 spec 改動落事後 delta;context 連續、最快。)

### 流程
```
bug / 失敗TC → builder 切 debug-mode
  → 讀失敗行 @implements → 上溯 FUNC.step / claim
  → 四層診斷定「缺陷起源層」→ 該層修 + 往下 cascade(code/TC 重綠)
  → spec 層改動 → 進 delta → 事後逐項人審(OD-D)
```

### 四層診斷(在**缺陷起源層**修,再往下 cascade)

**原則**:自底向上掃,**停在第一個「未忠實實現上游」的 artifact = 起源層**;修該層、**不在其下游貼膏藥**(REQ 錯就別 hack code;code 錯就別動 REQ)。**起源可高可低** —— impl bug 起源就是 code(修最低層),需求 bug 起源才是 REQ。

| 診斷(自底向上,停在第一個斷裂處)| 起源層 | 修哪 | 成本 |
|---|---|---|---|
| code ≠ DESIGN | 實作 | code | 低(最常見)|
| code=DESIGN 但 DESIGN ≠ FUNC / 缺 `test_seam` | 設計 | DESIGN → cascade | 中 |
| DESIGN=FUNC 但 FUNC ≠ REQ claim | 行為 spec | FUNC → cascade | 高 |
| 全對但 REQ claim 錯/模糊 | 需求 | REQ(觸發三元組治理閘)| 最高 |

- **negative space 幫判**:bug 命中**已宣告** `failure_mode`/anti → 「有處理但壞了」(impl);**沒宣告** → 新負空間缺口 → 往上補 anti + 很可能到 FUNC/REQ。
- 上游修完 → framework §4.3 `cascade-check` flag 下游未更新。

### 人閘 = 全自走 + 事後 delta 逐項審,**但 3 條硬 carve-out 為 pre-gate**(不進事後)

| Carve-out(自走前先停)| 為何 | 出處 |
|---|---|---|
| 改 `*.py` / backend → **propose-first + PO 授權** | 後端錯優先前端 workaround;動 Azure 運轉更嚴 | `[[backend-change-rule]]` `[[dep-management]]` |
| **任一 spec 層破壞性 delete(REQ / DESIGN)** → **PO-confirm before**(一律必做;預設 Deprecate 優先)| 刪需求 / 設計 = 慎思,不可事後補審 | requirement rulebook + DESIGN §4.4 |
| **high-stakes claim**(`risk_class` = safety/data/compliance)→ 較強 pre-gate;**沿 claim 傳播**:touch 到 high-stakes claim 的**任一層**改動(REQ / DESIGN / code)皆 pre-gate | 安全·資料·法遵不容事後 | 准入閘 §2.5 T3 + §5.5 floor |

其餘(frontend code / DESIGN / FUNC / **normal 非破壞性 REQ create-update**)→ agent 自走 → 落 delta。REQ 類進 delta **仍帶三元組**(golden/anti)+ Verdict Annotation(治理線不變,sign-off 收事後 delta);**§2.5 admission 折進 REQ 閘即時跑(Group 6 §4C),准入 outcomes 在同一 delta 一起審**(debug-mode 加 REQ 不繞准入)。

### delta 呈現
所有 spec 層改動彙整 → **OD-D 逐項差異審核**(人話 prose:什麼/為何/影響/不涵蓋;drill-down 才看 machine-block);非 spec 的 code fix **不進 delta**,但須 **G6(TC 綠)+ INV-D8(code↔DESIGN 一致)雙綠**(防改綠卻與 DESIGN 分歧的 green-but-divergent drift)。

### 要素(Track B 實作)+ 依賴
- builder **debug-mode**(讀脊椎 + 上溯 + 四層診斷 prompt/tool)· **delta 收集器**(彙整 → OD-D 呈現)· **carve-out pre-gate 攔截**(3 條)
- 依賴:`@implements` + coverage validator(Track B)· TP/FUNC 真檔(Track A 剩)才有節點可爬

### 與既有退回迴路(§4J)的關係
§4J 退回 = **review findings**(spec 未過 gate,**設計時**);§4N = **runtime bug**(code 跑出錯,**執行後**)。兩者皆 agent 自走 + max-rounds/carve-out backstop,但**觸發源 + 上溯方向不同**——§4N 特有「沿 @implements 爬回意圖層」。

---

## 4O. Build Flow（builder 照 DESIGN 建 + 不清上溯 + TP-driven,2026-07-04)

> **§4N 的姊妹半**:§4N 是**執行後 bug 往上溯**;§4O 是**建構期 spec→code 往下走**,但遇不清一樣**上溯意圖**,且全程**朝 Test Plan 允收標準收斂**。同一脊椎,兩個時機。

### A. Disambiguation-up（DESIGN 不清 / 不足 → 上溯 FUNC → REQ 解意圖,**不猜**)

- builder 主線讀 **DESIGN**(怎麼做:file_impact / interface / implements)。
- 遇 DESIGN **不清 / 矛盾 / 不足以決策** → **禁 guess**,逐跳上溯(`covers_func` → FUNC 的 `covers_req`):
  - **FUNC**(`user_journey.step` 的 `observable` + 為何)→ 這步該看到什麼
  - **REQ claim**(`golden_scenario` = 對的樣子 / `anti_examples` = 不可以的樣子)→ 意圖的兩個錨
- 用上游意圖消歧 → 回 DESIGN 層落實。**若上游也不清 = spec gap** → route 回 spec-author / 落 §4N delta(build 期發現的意圖缺口,同層級路由)。
- ⭐ **golden 給「對」、anti 給「界」**——消歧就靠這兩錨,不靠 agent 想像。

### B. TP-driven build（建 code 時心裡有 Test Plan,確保 meet 允收)

- builder 的 context bundle **必含該 component 所 implements 的所有 claim 對應的 TP 集合**(每 TP 的 `validation_key_point` = 允收標準)。
- **建之前**:先讀各 `TP.validation_key_point`(什麼叫「做完 / 對」)+ `test_seam`(要暴露什麼 hook 讓 TC 斷言得到)。
- **建之中**:朝 `validation_key_point` 建,**不是朝「看起來能動」建**。
- **建之後**:從 TP 導出 / 跑 TC → **G6(每 claim 的 TC 全綠)+ coverage validator(DESIGN↔Code〔INV-D8,`@implements`〕、FUNC↔DESIGN)全綠,才算 build done**;缺 seam → **補 seam(= `test_seam` 是 DESIGN 欄位 → DESIGN 改動,走 disambiguation/delta 路由),不改 TP 遷就**。
- = **acceptance-driven**:TP 是「對」的定義,code 向它收斂(非反向)。

### 合起來 — build 期脊椎雙向用

```
主向下（建）:  REQ ─► FUNC ─► DESIGN ─► code        （讀 DESIGN 建）
遇不清上溯:    code ◄─ DESIGN ◄─ FUNC ◄─ REQ         （讀 golden/anti 消歧）
驗收錨:        TP.validation_key_point + test_seam ─► TC ─► G6 全綠
```
- **gate**:coverage validator(DESIGN↔Code〔INV-D8,`@implements`〕、FUNC↔DESIGN)+ **G6**;過了才 build done。

### 與 §4N(debug)的關係

| | 觸發時機 | 主方向 | 上溯用途 |
|---|---|---|---|
| **§4O build** | 建構期(spec→code)| 往下建 | DESIGN 不清 → 上溯 golden/anti **消歧** |
| **§4N debug** | 執行後(code 出錯)| 往上溯 | 定**缺陷起源層**修 |

同脊椎、同上溯機制(`covers_` / `@implements`),差在**時機 + 目的**(消歧 vs 定根因)。carve-out(§4N 3 條)build 期同樣適用(消歧若導致 REQ/DESIGN 改、或 touch `*.py` → 同 pre-gate)。
**邊界**:build 期 **G6 紅 = 未 done**,續 build-mode 迭代收斂;§4N debug 專治 **build done 後**才出的 runtime bug(非 build 期未收斂)。

### Spine-gap fallback（build + debug 共用;收 §4N R3 N1)

上溯**假設脊椎完整**(節點有 `covers_`、失敗行有 `@implements`)。建置期脊椎未鋪滿時:
- 撞到**無 `@implements` 的 code 行** → 預設**當 impl 層**處理 + **flag annotation 缺口待 backfill**(把脊椎洞本身變可見待辦)。
- DESIGN 無 `covers_func` / FUNC 無 claim → 同視為 spec gap,route 回 spec-author。
- 即:脊椎不完整不 block,但**每個缺口都被標記**,漸進補齊(對齊 measure-first)。

---

## 4P. Automated Sanity Validation + Triage（agent 自動驗品質 + 出 bug 上溯,2026-07-04)

> **問題**:怎麼讓 agent **自動跑 sanity(TC)驗 app 品質**,出 bug / root cause 不清時 **上溯 TP/DESIGN/FUNC/REQ** 定根因 + 對的 solution。**答案**:detection(sanity 跑)= 前端 · triage(§4N)= 後端 · **`covers_tp`(sanity rev 1.34 加)= 橋**。

### 硬約束(誠實):REQ-001 真機強制
sanity TC 的 UI 視覺確認(`validate.prompts` Q&A)= 真人 QA 真機 LIFF。故「agent 全自動」不能 100% —— 但「驗品質」拆層,agent 自動化其中 **2.5 層**:

| 層 | 驗什麼 | agent 自動? |
|---|---|---|
| 靜態/覆蓋 | schema(REQ-011)· covers_tp/covers_req 覆蓋 · intent↔TP · REQ→TP→TC 鏈 · lint | ✅ 全自動 |
| 後端狀態 | `state_assertions`(db_row/api 可觀察)| ✅ agent 打 API 驗,不需真機 |
| UI 結構 | `sig.json` describe() 快照(DESIGN §3B)| ✅ 半自動,無真機 |
| UI 視覺/互動 | LIFF WebView 渲染/tap/視覺 | ❌ REQ-001 真人 QA(或 headless extension,見下)|

### ① Automated validation harness
agent orchestrate coverage/schema validators + 後端 `state_assertion` runner(API-level)+ `describe()` 快照 diff。⭐ **`covers_tp` 是關鍵**:讓 agent 把「某 check 掛了」綁回 **TP→REQ**(否則只知「TC 紅了」,不知「哪個需求沒滿足」)。

**⚠ detection 兩出口(不可混)**:
- **(a) coverage/schema gap**(REQ 無 TP · covers_tp 缺 · intent↔TP 不一致 · schema drift)= **authoring 缺口** → 補 TP/TC/FUNC(走各 rulebook + §2.5 准入閘),**非** §4N triage
- **(b) behavior assertion fail**(後端 state_assertion / 真機 TC 斷言掛)= **真 bug** → 走 ② §4N triage

### ② behavior bug → agent triage（§4N;僅 (b) 型)
```
失敗 TC ─covers_tp→ TP ─covers_req→ REQ-<id>-G1 → golden(對)+ anti(界)=意圖
失敗行 code @implements FUNC-x.step-N (realizes REQ-<id>-G1) → FUNC → DESIGN
→ 四層診斷定缺陷起源層 → 在該層修 → cascade
```
真人 QA 報 UI bug 也走同一條(TC→covers_tp 爬上去)。不清 → 上溯讀 golden/anti 消歧(§4O)。carve-out 照舊(§4N 3 條)。

### ③ REQ-001 真機這層 = **headless/emulator 例外(PO 定案方向)**
對**可程式驅動的 UI flow** 定 REQ-001 例外,讓 agent headless/emulator 跑(提高自動化)。⚠️ = **governed REQ-001 update**(動 requirement 三元組 → requirement-authoring gate)+ 可能漏真機-only bug(WebView 渲染,呼應 `[[android-webview-render-bug]]`)→ 例外**只涵蓋可程式驅動子集**,真機-only(視覺/裝置特異)仍真人。**deferred**(build 順序 FUNC 先)。

### 要素(依賴)+ build 順序(PO 定案)
1. ✅ **FUNC rulebook(§4G)先**(已建)—— 上溯有 FUNC 節點可爬
2. **propose-first *.py**:REQ-011 `covers_tp` check + coverage validators(REQ→TP→TC / FUNC↔DESIGN …)+ 後端 `state_assertion` runner + **engine `describe()`(DESIGN §3B/§4O;UI 結構層依賴,Track B 未建)**
3. **agent sanity-runner + triage command**:auto 跑靜態/後端/結構層 → 收真人真機結果 → **兩出口(見 ①):coverage/authoring gap 補 spec(准入閘)/ behavior assertion fail 走 §4N triage**
4. **REQ-001 headless extension**(governed,defer)

---

## 4Q. Automated Frontend Validation（純前端自動驗證 — 首個 spec-first feature / adoption driver,2026-07-05)

> **PO 定案(2026-07-05)**:要「自動化**前端**驗證」= **純驗前端 UI(結構 + 視覺),不驗後端**;**以 spec-first 建**(先寫 5 specs 再開發),當**第一個新格式 feature** —— 正好驅動 adoption(讓 A validators + describe() 有的放矢)。

### 純前端 = 驗什麼（不碰後端斷言)
- **UI 結構**:engine `describe()`(config → component 樹 JSON,Node 跑、無瀏覽器)→ `sig.json` diff,抓 markup / component 漂移。便宜、agent 自動。
- **UI 視覺 / 互動**:headless / emulator 自動驅動(REQ-001 governed ext)/ 真機人工(最終)。抓渲染 / 互動 bug。
- **不含**:backend DB/API `state_assertion`(= 後端驗證,另一件事,B.1,獨立 defer)。前端測試如需資料 → **mock / stub backend**,**斷言仍在前端**。

### 為什麼是對的下一步（解 adoption gap)
- A(coverage validators)已就位但**空等新格式**;describe() 也空等(§4P/B 提案的 adoption gap)。
- **把「自動化前端驗證」當第一個 spec-first feature** → 它的 5 specs 用新格式(claim-ID / covers_ / vkp / @implements)→ **validators 從 WARN 轉真守**;它的 DESIGN/code 產出 `describe()` → **describe() 有的放矢**。
- = 一石多鳥:交付一個真功能 + 驗整條 5-spec cascade + 工具鏈活起來。

### 做法（spec-first;PO 定「適合時間點」)
1. 寫「自動化前端驗證」的 **5 specs**(REQ→TP→FUNC→DESIGN→TC,新格式,過 A validators + spectra)
2. 開發:含 engine `describe()` 純路徑(= 此 feature 的 DESIGN/code;動 V3 engine 走 `[[v3-default-ui-mainline]]` rollback + propose-first)
3. `describe()` sig.json gate 上線 +(可選)headless ext 視覺層 → 前端品質 agent 自動驗

### 與 B 提案的關係
- **B.2 describe()** → **併入本 feature**(是它的機制,不獨立建)
- **B.1 state_assertion**(後端)→ **非本目標**,獨立 defer
- **REQ-001 headless ext** → 本 feature 視覺層選項(governed,後續)

### 時機
**defer 到 PO 定的適合時間點**;現只記入 plan。先決條件已備:規則層 sealed + A validators 就位 → 隨時可 spec-first 起手。

---

## 4R. 小決策收斂（§8 backlog concerns,2026-07-05)

V1 過 §8 backlog 找出 3 個真 concern,收斂:

### ① Cross-spec staleness（backlog 2.5)— ✅ 建了 A.4
`scripts/coverage_staleness.py`:downstream frontmatter `upstream_pins: {REQ-x: <hash>}`(cover 的 REQ block content-hash);**REQ 改 → hash 變 → mismatch = stale**(下游須複審);無 pin = unpinned WARN。lint **Stage 9**。**補 framework §4.3 + backlog 2.5 的洞**(A.1-A.3 檢結構、A.4 檢新舊)。opt-in(afv TP/FUNC 已 pin 示範)。

### ② Checker 分工表（backlog 4.5)— 防工具增殖混淆
| 層 | 工具 | 性質 | 何時 |
|---|---|---|---|
| **機械結構** | triad + coverage A.1–A.4 validators | 確定性 pass/fail | 每 commit(lint Stage 5–9)|
| **語意判斷** | spectra-review / V7 SCR | agent 判斷 → findings | 動工前 / gate |
| **編排裁決** | pm gate-check / validate-* | 綜合上兩者 → phase gate | phase 邊界 |
**原則**:validators 給「機械事實」· review agents 給「語意判斷」· pm gate 做「綜合裁決」。**Track B compliance agent = 叫 review(語意),不重造 validators 的機械檢**(各司其職、不重疊)。

**⭐ 寫任何新 validator/checker(Track B 含)前必守 6 條硬約束** → `proposals/coverage-validators-proposal.md §9`:**H1 identity 必帶 project(禁全域 bare-id map,§3.4.1)**· H2 selftest 必含 cross-project 隔離 case · H3 落地後反證(green ≠ 正確)· H4 scope=真 canonical id def · H5 stdlib-only + WARN→BLOCKING · H6 cite-parent 需 parent 存在。由 2026-07-05 spectra sweep(A.4 B1 假綠 + A.1-A.3 同型 collision)換來。

### ③ Tier = 深度 dial(**5 份恆在**,不控存在;backlog 1.4 / 2026-07-05 PO 反轉 C1)
> **廢除舊「Small 省 FUNC」carve-out**(PO 親令制度一致 > 例外)。canonical 定義在 **framework §6**(tier=深度 + 每 spec floor)。

| tier | 深度(5 份恆在,寫多細) |
|---|---|
| **Small**(~50–300 LOC / 1 REQ 清楚)| 各寫到 **floor**:FUNC 1 journey+1 FM · TP 每 claim 1 vkp · DESIGN 1 component · TC ≥1 pos+≥1 anti;solo sign-off |
| **Medium** | floor 之上:多 journey/FM · happy+edge+error · 多 component · 3-role sign-off |
| **Large / high-stakes** | 窮舉 + 強 gate 不省 + phased 分 rev |

- **無 spine 降級 / 無 `--tier` validator 特例**(已刪):FUNC/TP 恆在 → DESIGN `covers_func`→FUNC、TC `covers_tp`→TP、`test_seam`→vkp 一律 resolve;A.1-A.4 **0 改**、不欠 `--tier` 放行。
- **防 gold-plate 靠 floor 不靠省略**:簡單 feature 每份寫到 floor(FUNC 可能 1-2 行)即停,不生冗贅但也不缺件(cost-conscious `[[user-working-style]]`)。high-stakes 不得停 floor。

### 其餘 backlog 判讀
- **7.2 舊/新慣例**:部分已解(sanity covers_tp rev 1.34);canonical = 新格式,舊 grandfather。邊做邊遷。
- **8.1 universal vs repo-specific**:僅「promote 到別 repo」時處理(agent generic + 領域從 CLAUDE.md/memory 注入,§4L);Namecard 本身不阻。
- **7.1 §6 對映 / 2.1 深度 / 3.4 spawn 模板 / OD-A/B/C/E**:已解或 Track B 動工時自然定。

---

## 5. 打包形式:bundle of primitives(不是單一 skill)

| 概念 | 原語 | 位置 |
|---|---|---|
| 5-spec 規則 | **docs** | `docs/pm/spec-authoring/*.md` |
| 11 角色執行者 | **Subagent** | `.claude/agents/*.md` |
| 3 階段編排(入口)| **Slash command** | `.claude/commands/*.md` |
| 流程 + gates | **PM Skill**(既有)| `skills/pm-skill/` |
| 審查能力 | **Skill**(既有)| spectra-review / V7 SCR |
| 全域規則 + 開關 | CLAUDE.md + settings.json | — |

**編排硬度**:驗證期用**薄 command spawn subagent**(Claude-driven);流程穩 + 要確定性 → 升 **Workflow**。前門 = 3 command(+ PM skill 管流程),**無** umbrella skill。

---

## 6. 與既有資產的重用/擴充對映

| Proposal 章節 | 既有落點 | 處置 |
|---|---|---|
| §6.2 需求入場規則(5-test)| rulebook §2.5 Admission Gate(**5 test 一模一樣**)| ✅ 重用 |
| §6.1 需求格式規則 | §B.4 11 欄位(priority MoSCoW vs P0/P1/P2 待調)| ✅ 重用 |
| §6.3 corner case 登記處 | admission gate 路由(Open Q / Out of Scope)| ✅ 重用 |
| §6.4 兩層守門 | admission gate + `/pm validate-req-spec` | ✅ 重用 |
| §9 5-Spec Framework | `5-spec-authoring-framework.md` | ✅ 重用 + Track A expand |
| §9.2 bidirectional cascade | triad validator + `/pm validate-coverage` | ✅ 重用 |
| §9.6 anti-example / living spec / decision-log / spec_dirty | triad anti_examples + decision-log | ✅ 大半重用 |
| §4/§5/§7/§8 11 agents + 3 commands | — | ❌ Track B 新建 |

---

## 7. 執行順序(phased,對齊「先驗證」)

1. **Phase 1 — Track A 骨架**:4 份 rulebook 核心不變式 + checklist(從 framework §3.2~3.5 導出,最小可用)
2. **Phase 2 — Track B**:11 agents(Subagent-only)+ 3 commands,指向 Track A + PM Skill
3. **Phase 3 — 驗證**:挑 1 個真實 Namecard V3 feature 跑 `/spec-team → /build-team(subagent)→ /compliance-check`,end-to-end 驗證,學到再迭代
4. **Phase 4(deferred)**:Agent Teams + promote user-level 跨 repo

---

## 8. 執行釐清 Backlog(逐項修補;🔴 動工前必決 / 🟡 邊做邊定 / 🟢 之後)

### Group 1 — 產物與路徑 ✅ 定案(見 §4A)
- **1.1 ✅** 路徑 = `docs/pm/<project>/{spec/, modules/<module>/}`(nested,零碰撞;不建 `docs/specs/`;feature→module)
- **1.2 ✅** ID = REQ / TP / **FUNC**(PO 定案)/ TC-`<module>`-`<seq>` / DESIGN(不用 D-)+ 統一 `covers_<parent>`(補 C2 洞)
- **1.3 ✅** dual-layer:prose + normative machine-block;缺 block = format-mismatch HARD(B1 guard)
- **1.4 ✅** tier→spec 對映表(§4R③,防 gold-plating);一檔/多檔 = 已用 `modules/<module>/` 分檔慣例(§4A)。

### Group 2 — Track A 4 份 rulebook(TP ✅ 定案 §4D;FUNC/TC/DESIGN 待)
- **2.1 🟡** 深度:骨架先(貫穿原則 + sizing atom 表已定 §4D)
- **2.2 ✅ 全定案** 核心不變式:**TP**(§4D)· **TC**(§4F)· **FUNC**(§4G)· **DESIGN**(§4H:實作 FUNC + expose test_seam 驗 TP;完整性不變式 cover-all 雙向;convergence on claim)—— **Track A 5 份 rules 討論全齊**(見 §4H 尾表)
- **2.2a ✅ 三角互驗**:REQ+FUNC→TP / REQ+TP→FUNC / FUNC+TP→REQ,共同單位 = claim ID `REQ-<id>.<golden|anti#k>`(REQ 擁有 / TP verifies / FUNC realizes|handles 三者共享)
- **2.3 ✅** TC executable 格式 = (a) yaml/JSON declarative in `tests.md`(對齊 sanity + coverage validator);真打 API 才 pytest(標 tc_format)
- **2.4 🟢** 各 spec validator 何時做(TP↔REQ coverage gate 已規劃)。
- **2.5 ✅** cross-spec staleness 機械 enforce = **A.4 `coverage_staleness.py`**(upstream-pin content-hash;§4R①;lint Stage 9)。

### Group 3 — Track B agents + commands
- **3.1 ✅** agent 檔 schema(標準格式 name/description/tools/model)+ tool matrix(§4J)
- **3.2 ✅** 「只審不改」:純 reviewer tool 硬強制;qa/qa-automation 需 Bash/Edit → prompt + post-step git-diff 偵測(§4J)
- **3.3 ✅** command 編排(逐階段 spawn + 檔案交接 + 退回 + 呼叫 /pm,§4K);non-blocking 分層(前門 command / 後端 /pm 直接可用)
- **3.4 🟡** instance 分工 spawn prompt 模板。
- **3.5 🟢** 每 agent model 選擇 + 成本。

### Group 4 — PM Skill 邊界 ✅ 定案(見 §4B)
- **4.1 ✅** 溶解 3-phase,PM 8-phase 為唯一骨架 + agent roster per phase 表(solution-architect/ux-designer 移 Phase 1)
- **4.2 ✅** command = phase-cluster 便利包裝(spec-team P0-1 / build-team P2-4 / compliance P4-5),**呼叫** /pm 委派 gate,不平行
- **4.3 ✅** admission 規則在 rulebook、執行者依入口(agent→resource-manager / 直接→/pm);sign-off agent advisory + 人 PO 權威
- **4.4 ✅** agent↔phase roster 表已含(§4B)= agent↔PM 對映
- **4.5 ✅** compliance agents vs validators/PM gate = **checker 分工表(§4R②)**:機械結構=validators / 語意=review agents / 綜合=pm gate;compliance agent 叫 review 不重造 validator。

### Group 5 — 編排機制
- **5.1 ✅** 交接 header = 延伸 @governed-by(@produced-by/@covers/@next,§4K)
- **5.2 ✅** 退回 = findings 檔 + orchestrator re-spawn(§4J)
- **5.3 ✅** 狀態 = 重用 state.md 擴 agent 層(§4K)
- **5.4 🟢** 失敗/retry 策略。

### Group 6 — 人的控制點 ✅ 定案(見 §4C)
- **6.1 ✅** REQ + ship = 人;下游 = agent + gate(high-stakes 例外拉人)
- **6.2 ✅** 2 硬閘(REQ、ship)+ 1 輕閘(tier)+ 條件閘(high-stakes)+ on-demand;admission 折進 REQ 閘
- **6.3 ✅** REQ 閘呈現 = 人話 prose delta(非 yaml)+ standing interrupt(pause/kill/override/inspect,任何點)= 觸發到人的機制

### Group 7 — 既有資產調和 ✅(§4L)
- **7.1 🔴** §6/§9 對映確認(§6 表)。
- **7.2 🟡** tests.md / functional.md / sanity tc-*.json 與 5-spec 關係(接 1.1)。
- **7.3 🟢** proposal `docs/requirement-rules.md` 概念 = 既有 `spec-authoring/` 家族;命名/入口統一。

### Group 8 — 跨 repo + 成本 + 驗證 ✅(§4L)
- **8.1 🟡** repo-specific vs universal 切分(promote 前分離)。
- **8.2 🟡** Phase 3 驗證 feature 選誰(小而完整)。
- **8.3 🟢** 一次 run 的 token 預算 + guardrail。
- **8.4 🟢** 何時用 Workflow 取代手動 orchestration。

---

## 9. Open Decisions(V4 動工前/中裁決)

- **OD-A** 執行順序:Track A 先 / Track B 先(建議 A 骨架先)。
- **OD-B** 4 rulebook 首輪深度:骨架 / full(建議骨架)。
- **OD-C** Phase 3 驗證 feature 選誰。
- **OD-D** ✅ **定案(2026-07-03 PO)= 逐項差異審核**(agent 提議「加 A / 砍 C / 改 R + 理由」,PO 逐項 approve/改/reject;非盲簽整份)。對映精修 #3。
- **OD-E** 三組 🔴 先鑽哪組(建議 Group 1 產物路徑 + Group 4 PM 邊界 + Group 6 人控)。

---

## 10. Revision History

| Rev | Date | Change |
|---|---|---|
| 0.1 | 2026-07-03 | Baseline — 捕捉 V1 討論:4 決策 + 目標工作流 6 精修 + 兩軌架構 + bundle 打包 + 重用對映 + 30 項 backlog |
| 0.2 | 2026-07-03 | OD-D 定案 = 逐項差異審核(PO 確認精修 #3)|
| 0.3 | 2026-07-03 | Group 1 定案(§4A):路徑 nest `docs/pm/<project>/modules/`(PO 抓碰撞 wart)/ ID 含 FUNC-xxx(PO 定案)+ 統一 covers_<parent> 補 C2 洞 / dual-layer machine-block(B1)|
| 0.4 | 2026-07-03 | Group 4 定案(§4B):溶解 3-phase → PM 8-phase 唯一骨架 + agent roster per phase(solution-architect/ux-designer 移 P1)/ command = phase-cluster 呼叫 /pm 委派 gate / admission 執行者依入口 + sign-off 兩級(agent advisory + 人 PO 權威)|
| 0.5 | 2026-07-03 | Group 6 定案(§4C):人閘 = 2 硬(REQ、ship)+ 1 輕(tier)+ 條件(high-stakes)+ on-demand;admission 折進 REQ 閘;REQ 閘呈現人話 prose delta(非 yaml);⭐ standing interrupt 機制(pause/kill/override/inspect,任何點可搶方向盤)|
| 1.18 | 2026-07-05 | **廢除「Small 省 FUNC」carve-out → tier=深度 dial(PO 反轉 C1)**:5 份 spec 恆在,tier 只控深度 + 每 spec floor(canonical=framework §6)。刪 §4R③ spine 降級規則 + A.2/A.3 `--tier` validator TODO(未爆彈拆除;FUNC/TP 恆在→cite-parent 恆 resolve,A.1-A.4 0 改)。零例外(trivial 亦寫 5 份、停 floor)。cascade:framework §6 / §4R③ / proposal §9 H6 / decision-log D-035 / outreach-log-read 補 FUNC(pilot 轉 conformant)。理由:carve-out 生跨檔例外機器,制度一致 > 例外 |
| 1.17 | 2026-07-05 | **spectra sweep 收斂 + validator 6 條硬約束**:A.4 B1 假綠(跨 project REQ-id 碰撞)+ A.1-A.3 同型 collision 全修(per-project scoping,commits a651b10/d6af923);升格 requirement rulebook **§3.4.1 Project-qualified identity**(D-034,混合方案:spec 內 bare / 跨邊界 qualified);proposal **§9 H1-H6 共同硬約束**(H1 禁全域 bare-id map / H2 cross-project selftest / H3 落地反證 / H4-H6)寫入,§4R② checker 表 cross-ref → **Track B 前置硬規則** |
| 1.16 | 2026-07-05 | **§4R 小決策收斂**(V1 過 §8 backlog):① backlog 2.5 cross-spec staleness → 建 **A.4 `coverage_staleness.py`**(upstream-pin content-hash,lint Stage 9;補 framework §4.3 洞;afv TP/FUNC 已 pin 示範)② backlog 4.5 → **checker 分工表**(機械 validators / 語意 review agents / 綜合 pm gate)③ backlog 1.4 → **tier→spec 對映表**(Small 省 FUNC / high-stakes 不省;防 agent gold-plating)。7.2/8.1/7.1 判讀=部分已解或跨repo/瑣碎 |
| 1.15 | 2026-07-05 | **§4Q Automated Frontend Validation 定案**(PO):純驗**前端** UI(結構 via engine `describe()` sig.json / 視覺 via headless ext / 真機人工),**不驗後端**(state_assertion=B.1 另 defer);**以 spec-first 建**(先寫 5 specs,新格式)= **第一個新格式 feature** → 驅動 adoption(A validators 轉真守 + describe() 有的放矢);B.2 describe() 併入本 feature、B.1 獨立 defer;defer 到 PO 定適合時間點。並記:coverage validator A 家族(A.1/A.2/A.3)已上(lint Stage 6/7/8 WARN)|
| 1.14 | 2026-07-04 | **§4P spectra R2 fix**(grep-verify):C1 兩出口漏傳 —— 要素 item 3 仍「失敗走 §4N triage」沒帶兩出口(R1 修 ①/② header 漏 item 3)→ 對齊「coverage gap 補 spec / behavior fail §4N」;grep 確認 §4P 兩出口 ①/②/item3 全一致清零 |
| 1.13 | 2026-07-04 | **§4P + FUNC spectra R1 fixes**(accept;0 BLOCKER / 1 CONCERN / 3 NIT):C1 §4P **detection 兩出口分清**(coverage/authoring gap → 補 spec+准入閘 / behavior assertion fail → §4N triage;② header 標「僅 (b) 型」)—— 防 agent 對 coverage gap 誤跑四層診斷;N1 §4P 要素補 engine `describe()` 依賴(UI 結構層,Track B);N2/N3 FUNC(claim-level gate 註 / INV-F1×F2 消歧,見 FUNC rev 2026-07-04.1)|
| 1.12 | 2026-07-04 | **§4P Automated Sanity Validation + Triage 定案**(PO):agent 自動驗品質 detection + §4N triage,`covers_tp`(sanity rev 1.34)= 橋;3-layer 自動化(靜態/後端/UI 結構 sig.json)+ UI 視覺真人(REQ-001);**REQ-001 headless/emulator 例外 = PO 定案方向**(governed REQ-001 update,只涵蓋可程式驅動子集,defer);build 順序 = **FUNC rulebook 先(已建 D-031)**→ *.py validators → sanity-runner/triage command → REQ-001 extension。§4M item1 全 Track A 真檔 5/5 done |
| 1.11 | 2026-07-04 | **Track A FUNC rulebook(§4G)= 5/5 收尾**(D-031):`functional-spec-authoring-rules.md` — 三角互驗(REQ/FUNC/TP 任兩驗第三,共同單位 claim §3.4)+ 兩子結構基數(測試側 1:1:1 / 行為側 m:n mesh,TC↔FUNC 交叉連)+ INV-F1~F5 + 結構化 user_journey/failure_modes(realizes/handles claim)+ `@implements`/`@enforces` 下沉(§4N/§4O 上溯節點)+ REQ→FUNC G3 gate;claim-ID 用 §3.4 |
| 1.10 | 2026-07-04 | **§4O spectra R2 seal**(accept;0 BLOCKER / 0 CONCERN / 1 cosmetic):grep 確證兩處「build done」門檻一致(G6 + coverage validator);N1 統一 DESIGN↔Code validator 標籤為〔INV-D8,`@implements`〕。**§4O Build Flow 定稿** —— build+debug 完整運作模型齊 |
| 1.9 | 2026-07-04 | **§4O spectra R1 fixes**(accept;0 BLOCKER / 2 CONCERN / 3 NIT):C1 「build done」B 段統一為 **G6 + coverage validator(DESIGN↔Code/INV-D8、FUNC↔DESIGN)全綠**(消 B 段只 G6 vs 合起來段的兩套,對齊 §4N)/ C2 TP-driven context 改「該 component **所 implements 的所有 claim 對應 TP 集合**」(非單一 claim,因 covers_func m:n)/ N1 上溯精確「`covers_func` → FUNC `covers_req` 逐跳」/ N2 補 seam 註明 = DESIGN 改動走 delta / N3 界定 build 期 G6 紅=續 build-mode、§4N=build done 後 runtime bug |
| 1.8 | 2026-07-04 | **§4O Build Flow 定案**(PO,§4N 姊妹半):**A. Disambiguation-up** — DESIGN 不清/不足 → 禁 guess,沿 `covers_func` 上溯 FUNC observable + REQ `golden`(對的樣子)/`anti`(界)消歧;上游也不清=spec gap route 回;**B. TP-driven build** — context 必含 claim 的 TP,建前讀 `validation_key_point`(允收)+ `test_seam`、建中朝 vkp、建後 **G6 全綠才 done**(缺 seam 補 seam 不改 TP);acceptance-driven code 向 TP 收斂;**Spine-gap fallback**(收 §4N R3 N1):無 `@implements`→當 impl 層+flag backfill,漸進補齊不 block;carve-out(§4N 3 條)build 期同適用。§4N intro 指向 §4O、§4M item4 加 build-mode |
| 1.7 | 2026-07-04 | **§4N spectra R2 fixes**(accept;0 BLOCKER / 1 CONCERN / 1 NIT):C1 定案模型 summary(line 719)仍「最高缺陷層」(R1 改 3 處漏 summary)→ 對齊「缺陷起源層」;N1 high-stakes carve-out **沿 claim 傳播**(touch high-stakes claim 的任一層 REQ/DESIGN/code 皆 pre-gate,杜非 REQ 層邊角)。§4N summary↔內文全自洽 → **定稿** |
| 1.6 | 2026-07-04 | **§4N spectra R1 fixes**(accept;0 BLOCKER / 2 CONCERN / 2 NIT):C1 核心原則「最高缺陷層」→「**缺陷起源層**」+ 自底向上診斷演算法(停在第一個未忠實實現上游者、不在下游貼膏藥;**起源可高可低**,impl bug=code / 需求 bug=REQ)/ C2 carve-out「REQ delete」擴為「**任一 spec 層破壞性 delete(REQ/DESIGN)**」對齊 DESIGN §4.4 / N1 REQ 進 delta 註「§2.5 admission 折進 REQ 閘即時跑,outcomes 一起審」(不繞准入)/ N2 code fix 須 **G6 + INV-D8 雙綠**(防 green-but-divergent) |
| 1.5 | 2026-07-04 | **§4N Runtime Debug Flow 定案**(PO):builder **debug-mode** 單 agent 沿 `@implements` 上溯 → **最高缺陷層修** → cascade;**四層診斷**(impl/design/behavior/requirement,起源最高層修)+ negative-space 判「已宣告 vs 新缺口」;人閘 = **全自走 + spec 改動 delta 事後逐項人審(OD-D)**、純 code fix 靠 G6 綠;**3 硬 carve-out pre-gate**(`*.py` propose-first / REQ delete PO-confirm / high-stakes 較強 gate);與 §4J review 退回迴路區隔(**設計時 vs 執行後**,上溯方向不同)。§4M item1 design rulebook 標 ✅ done |
| 1.4 | 2026-07-03 | §4L Group 7/8 定案(命名統一表 + 2 修正〔TC covers_func / requirement-rules 併入 spec-authoring〕;universal vs repo-specific 切分〔agent generic + 領域從 CLAUDE.md/memory 注入〕;兩階段驗證〔sanity 規則 → 1 小 feature〕;token guardrail〔model tiering + max-rounds + log/alert + measure-first〕)+ §4M Build 順序(1 Track A 真檔 → 2 sanity pilot → 3 reconciliation → 4 Track B)。**backlog 全清,plan 定稿** |
| 1.3 | 2026-07-03 | §4K command 編排(/spec-team 模板:逐階段 spawn + 檔案交接 + 退回 + gate 呼叫 /pm)+ **non-blocking 分層**(前門 command 便利層 / 後端 /pm·sanity 退後但人可直接跑,不阻擋)+ 交接 header 延伸 @governed-by(@produced-by/@covers/@next)+ 狀態重用 state.md 擴 agent 層;Group 3.3 + 5 收掉 |
| 1.2 | 2026-07-03 | §4J Track B 執行機制:agent 檔 schema(標準格式)+ 11-agent tool matrix;只審不改(純 reviewer tool 硬強制 / qa·qa-automation prompt+post-step git-diff 軟補);退回迴路(findings 檔 + orchestrator re-spawn author,全新 instance 從檔案重建;findings schema + max-rounds=3 escalate + 收斂追蹤;agent 自走不佔人閘)|
| 1.1 | 2026-07-03 | Design rulebook 定案(§4H)—— 收尾 Track A 5 份 rules。DESIGN 對 FUNC=實作(@implements)、對 TP=可驗(test_seam,非實作);convergence on claim;⭐ 完整性不變式(cover all FUNC+TP items,雙向禁 gold-plating,gap 設計時抓);test_seam 必填;coverage validator 家族湊齊(FUNC↔DESIGN + TP↔DESIGN + DESIGN↔Code)。Track A 全定案 |
| 1.0 | 2026-07-03 | Functional rulebook 定案(§4G)+ 三角互驗(PO 洞察:任兩 spec 驗第三)—— 共同單位 = claim ID `REQ-<id>.<golden|anti#k>`(REQ 擁有/TP verifies/FUNC realizes|handles);FUNC covers_req list(m:n)+ 兩子結構(測試側1:1:1/行為側m:n);⭐ 結構化 per-step realizes/handles + 追溯下沉程式碼註解 `@implements`(延伸 @governed-by 到 function 層,程式碼可讀+人可 debug/review);§4D TP claim 統一為 REQ-005.golden 合成 ID |
| 0.9 | 2026-07-03 | §4F 展開:TC 完整元素清單一般化搬入(self-contained,不再只指向 sanity)—— Identity/Content/Steps/Assertions/TestData/Meta 分組 + covers_tp(NEW 必填單值)+ 6 條規則 |
| 0.8 | 2026-07-03 | Test Cases rulebook 定案(§4F):TC schema = 沿用 sanity 24-field(REQ-004/019 已在真機驗證,executable+intent 極性+PII scrub 全 reuse);唯一結構性 ADD = `covers_tp`(單值,補 sanity 缺的 parent 引用 = 走偏本質);ALIGN intent↔父 TP claim(validator 檢);assertion 極性跟隨 TP 非每 TC 硬塞;G6 分層 P0 100%/P1-P2 ≥95%;清理 related_feature/subject |
| 0.7 | 2026-07-03 | Work-item §4E:sanity REQ→TP→TC 全鏈重做(pilot)—— PO 選 top-down 全鏈重做(修訂 REQ→重寫 TP→重生 TC)+ 4 安全 guard(參考既有/worktree 綠了才換/保 tc executable 格式/分階段 validate);anti-drift 用可視+interrupt |
| 0.6 | 2026-07-03 | Test Plan rulebook 定案(§4D):貫穿「正面+負空間」+ sizing atom 表;1 TP=1 claim(golden/anti,痛點非 atom、area 是 tag);雙向基數 REQ→TP→TC 1:m:n / TC→TP→REQ 1:1:1(cite-parent 單值,PO 修正);TP schema(covers_req+claim+area+validation_key_point+method+data_source+environment+priority);validation_key_point=observable+trace REQ acceptance 契約;risk-weighted area;TP↔REQ gate + area 覆蓋 dashboard;TC 格式 = yaml declarative |
