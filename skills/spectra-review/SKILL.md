---
name: spectra-review
description: Adversarial review skill — dual-mode bridge for both OpenSpec change proposals (legacy v1) and PM Skill artifacts (v2.0). Triggered by `/spectra-review <target>` slash command or by phrases like "review this proposal", "spectra-review docs/foo.md". Produces 4-tier punch list (BLOCKERS / CONCERNS / NITS / STRENGTHS) with 7-field schema per finding (severity 三件套 + fix_economics + dependencies + decay), F1 per-round log + F2 aggregate summary per PM Skill proposal §6.4.3.C contract, Minerva 4-ability framework (批判思考 / 問題解決 / 複雜系統 / 決策思維), and explicit Confidence Tier (🟢 high / 🟡 medium / 🔴 low) per output. Composes with `/pm-bug-review` for PO override loop.
---

# Spectra Review v2.0 (project-level)

Adversarial review skill for design proposals and PM Skill artifacts. **Bridge edition** — supports both legacy OpenSpec workflow AND PM Skill artifact contracts per `docs/pm/pm-skill/spec/pm-skill-proposal.md` rev 1.12 §6.4.3.

> **Versions:**
> - **v2.0**(2026-06-17)— Bridge edition;adds PM Skill mode + Path Conventions + F1/F2 schema + 7-field finding template + Confidence Tier explicit + PM Skill `/pm validate-*` / `/pm-bug-review` integration
> - **enhanced-v1**(2026-06-17)— Minerva 4-ability framework(preserved as the analytical core)
> - **base v0**(原版)— remains accessible via `--lite` flag

## Multi-IDE Bootstrap

| Tool | Loading Mode | User Action Required |
|---|---|---|
| **Claude Code** | Native skill load(via `.claude/commands/spectra-review.md` dispatcher) | No action — `/spectra-review <target>` triggers this skill |
| **Antigravity** | Repo-aware auto read | Usually auto;explicit `/spectra-review` mention boosts consistency |
| **Codex / VSCode** | Repo-file fallback | Paste bootstrap prompt below at session start |

**Codex bootstrap prompt:**

```text
先讀 docs/CONTEXT.md、docs/pm/pm-skill/spec/pm-skill-proposal.md §6.4.3。
若我輸入 /spectra-review <target>,讀 skills/spectra-review/SKILL.md 跑對應 mode workflow。
```

## Trigger Convention

This skill activates when:
- User types `/spectra-review <target>` slash command(via `.claude/commands/spectra-review.md`)
- Or user says "review this proposal" / "spectra-review docs/foo.md" / "review §6.4 of pm-skill-proposal" plain-text patterns

Mode-specific dispatch in §Mode Detection below.

### Trigger Priority Note(對齊 Round 2 N5 fix — v1 user-level + v2 project-level 並存)

如果 Claude Code session 同時 register 兩個 spectra-review skill:
- **legacy v1**(user-level `~/.claude/skills/spectra-review/`)— OpenSpec-only
- **v2.0 bridge**(project-level,此檔)— OpenSpec + PM Skill dual-mode

**LLM 選擇優先序:**

1. **User 明示 `--mode <X>` flag** → 強制 dispatch 對應 mode(若 mode 是 PM Skill 則必走 v2.0)
2. **Target 是 PM Skill artifact pattern**(對齊 Mode Detection 表的 PM Skill rows)→ 走 v2.0
3. **Target 是 `openspec/changes/<X>/`** → 兩 SKILL 都可勝任,**優先 v2.0**(避免雙路徑 audit 散落)
4. **Target ambiguous** → ask user,推薦 v2.0(完整 7-field schema + F2 aggregate)

**Migration recommendation:** Phase E 落地後 deprecate v1 user-level 拆除單一 source of truth,對齊 §6.4.13 12-week deprecation window。

## Start Here

Read tiered by mode(對齊 Round 2 C4 fix — Lite mode 跳 conditional):

### Always Read(3 items,both modes)— repo bootstrap

1. `../../docs/CONTEXT.md` — repo 現況快速 context
2. `../../docs/ai-principles.md` — repo-wide AI 工作原則
3. `../../docs/index.md` — repo doc 全索引

### Conditional Read(enhanced mode only;Lite mode 跳)— spectra-review specific

4. `docs/pm/pm-skill/spec/pm-skill-proposal.md` §6.4.3 — spectra-review Contract(F2 schema / 7-field finding / Default vs Override)
5. `docs/pm/pm-skill/spec/pm-skill-proposal.md` §6.4.4 — Default vs Override Trust Hierarchy
6. `docs/pm/pm-skill/spec/pm-skill-proposal.md` §6.4.10 / §6.4.11 — Artifact Contracts(per-phase quality bars)
7. `references/finding-template.md`(this dir)— 7-field finding template stub
8. `references/f2-schema.md`(this dir)— F2 aggregate summary schema

**Path Reference Convention(對齊 PM Skill SKILL.md):**
- `../../docs/...` paths = **fixed file references** for Claude to READ at SKILL bootstrap(relative to SKILL.md location)
- `docs/...` paths = **runtime operational paths** at repo CWD(Claude operates from repo root)

---

## Mode Detection

The first task per invocation: detect which mode applies based on `<target>`:

| Target pattern | Mode | Cross-ref context |
|---|---|---|
| `openspec/changes/<name>/` | **OpenSpec(legacy)** | `docs/copy-inventory.md`,`action-inventory.md`,`domain-model.md`,`release/changes/` |
| `docs/2026-*-requirement.md` | **PM Skill — Requirement Spec** | proposal §6.4.10 §B contract |
| `docs/modules/<project>/_plan.md` | **PM Skill — Module Plan** | proposal §6.4.11 §B contract |
| `docs/modules/<project>/<module>/{requirement,functional,plan}.md` | **PM Skill — Module Spec** | proposal §6.4.11 §C contract |
| `docs/2026-*-pm-skill-*.md` or `skills/*/SKILL.md` | **PM Skill — Meta(self-review)** | proposal §6.4 全 contract |
| Other markdown under `docs/` | **PM Skill — Generic doc**(對齊 Round 2 C2 fix)| **無 specific contract** — 跑 7 dimensions Mental Lens 但不強制 §6.4.10 quality bar(eg. 不要求 Glossary section)|
| `docs/pm/<project>/state.md` | **PM Skill — state**(對齊 Round 2 N4 fix)| state.md schema 對齊 §6.4.10 + §6.4.11 phase signoff 機制 |
| `docs/pm/_org/contract-pack/<contract>-v<N>.md` | **PM Skill — contract-pack**(對齊 Round 2 N4 fix)| 對齊 §6.4.13 Contract Change Governance + version 規約 |
| No clear match | **Ask user** | Print mode list,let user pick |

Output mode detection at start of review log:

```
🎯 Mode: <detected mode> (target: <path>)
```

---

## Locate Target

### OpenSpec mode

If user passes a proposal name(e.g., `/spectra-review 2026-05-20-vehicle-plate-field`):
- Target = `openspec/changes/<that-name>/`

If no arg:
- List `openspec/changes/` directories(excluding `archive/`)
- If exactly one → that's the target
- If multiple → ask user
- If none → "Nothing to review in openspec/changes/"

Inside target directory: `proposal.md`(required)/ `tasks.md`(required)/ `design.md`(optional)/ `specs/<capability>/spec.md`(zero or more)

### PM Skill mode

`<target>` is a direct file path. Verify it exists with Read; abort with help text if not.

Resolve **active project context** for path resolution:
1. Read `docs/pm/active-project.txt`(if exists)
2. Or detect from target path(eg. `docs/modules/<project>/` → project is `<project>`)
3. Or ask user explicitly

---

## Cross-reference Context

### OpenSpec mode

Read these alongside the proposal:
1. `docs/copy-inventory.md` — i18n key namespace conventions
2. `docs/action-inventory.md` — action token contracts
3. `docs/domain-model.md` — aggregate / field definitions
4. Runtime files mentioned in proposal's `Impact` or `Touchpoints` — grep for hardcoded strings, missing handlers
5. `release/changes/` — find related changeset(s) for cross-validation
6. `openspec/changes/namecard-v2-core-features-baseline/specs/<capability>/spec.md` — existing requirements that might overlap

### PM Skill mode

Read these alongside the target:
1. `docs/pm/pm-skill/spec/pm-skill-proposal.md` §6.4(全 contract — authoritative source)
2. `docs/pm/pm-skill/docs/pm-skill-user-manual.md`(scenario reference if reviewing manual)
3. Per-project PM Skill state:
   - `docs/pm/<project>/state.md` — current phase / signoffs
   - `docs/pm/<project>/decision-log.md` — prior decisions(avoid re-debating closed issues)
4. Prior spectra-review logs at `docs/reviews/<project>/<date>-spectra-<target-slug>-round-*.md`(carry forward Decision Log)
5. F2 aggregate(if exists): `docs/reviews/<project>/_summary-<target-slug>.md`(对應 §6.4.3.C)
6. Memory:`memory/MEMORY.md`(index)+ project-specific memory entries

---

## Mental Lens(批判思考 — Minerva 強化點 1,preserved)

**必先讀:本 SKILL 跑 7 維度時,每維度都套用以下 4 個 mental act**。

### Mental Act 1: Claim → Evidence → Verdict

對 target 內每個 claim 主動提問:
- **Claim:** target 寫了什麼聲明?
- **Evidence:** target 內哪行/哪段支撐?
- **Verdict:** 證據足夠嗎?有 counter-example 嗎?

### Mental Act 2: Cross-section consistency check

- 這聲明在 §A 跟 §B 是否一致?
- 用詞 / 數字 / 範圍是否對齊?

### Mental Act 3: Anti-Bias Self-Check(eat-own-dog-food 強化)

每跑一個 finding,自問:
- 我是不是因為熟悉 / 是我自己寫的就放過了?
- 我這判斷可能錯,反例是什麼?
- 如果我是新人看這 spec,會困惑嗎?

**Anti-Bias 額外規則(對齊 PM Skill 9 rounds 累積經驗):**
- 對 self-authored target 必須主動 deep-check
- 對 router 表 / list / 任何「填空式」結構必須 verify entries 對應到實作

### Mental Act 4: Understand-not-argue stance

- 不只說「這 issue」,要說「原作者為什麼這樣設計」
- propose Fix 時對齊 原意,不是強加自己偏好

---

## What to Check(8 維度,Mode-aware)

Run through these check categories;each category 套用上述 4 個 mental act:

### A. Naming consistency

Both modes:
- 命名規約對齊文件 governance(eg. snake_case / kebab-case 一致)
- 跨段 reference 用詞一致

OpenSpec extra: i18n key 對齊 `<namespace>.<dotted>` pattern;action token 對齊 `view:action` form。
PM Skill extra: per-phase contract version 對齊 `<X>-contract-v<N>`。

### B. Counting / arithmetic

- 數字 claim 對 evidence list 驗算
- 對齊 PM Skill §C scaling 表的 spec size 邊界正確套用

### C. Completeness

OpenSpec: grep runtime files for hardcoded strings vs proposal registry。
PM Skill: 對齊 §6.4.10 §B.4 9 必填欄位(per-REQ schema)是否完整;對齊 §6.4.11 §B-H 各 phase Mandatory Sections 是否齊全。

### D. Governance / SSOT alignment

OpenSpec: L1 / L1 Draft / L2 protected files listed in `## Impact`。
PM Skill: 對齊 §6.4.13 Contract Change Governance;contract version 變更是否走 patch/minor/major 路徑;`active_contract_version` 是否 per-project 標清楚。

### E. Acceptance criteria

Both:
- 涵蓋 happy path AND missing-key / null / edge cases
- machine-checkable(不可有「用戶體驗良好」之類)
- 對齊 PM Skill §E.4a Flaky Test Tolerance(若 acceptance 涉 intermittent test)

### F. Open Questions

- OQ 答案明示 / 標 deferred
- 對齊 §6.4.10 §F Forbidden Patterns(0 TBD/TODO at Phase 0 Exit)

### G. Backward / forward compatibility

- migration 路徑明示
- 對齊 PM Skill v1 + v2 並存期 `active_contract_version` 機制


### H. 標記雜訊 —— 給 AI 讀的文件禁用裝飾性標記（PO 2026-09-04 立）

> ⚠️ 適用對象:**讀者是 AI 的文件**(spec / design / 提案 / review log —— 未來的 session、subagent、自己)。
> 判準一句話:**標記不是資訊,句子才是。**

- **一個標記只有在「有鑑別力」時才准用** —— 即「掃這個符號就能列出該類項目」。
- `⛔` **只准接兩種東西**:①**禁令**(不得 / 不可 / 一律 / 禁)②**區辨**(X 不是 Y / 非 / 不代表 / 不等於)。
  接連接詞(而 / 且 / 但)、接粗體 `**`、接另一個 `⛔`、或單純語氣 ⇒ **判 NIT,一律刪**。
- **重複標記禁用**:`⛔⛔`、`⭐⭐⭐` —— 強調不能靠重複符號,要靠把句子寫清楚。
- **作者自檢(寫完必跑)**:把所有標記刪掉,**資訊有沒有少?** 沒少的那些就是干擾 ⇒ 刪。
- **可機檢的紅線**(純文字可判定,**⛔ 不是 needle 型**):把 `⛔` 後面的空白與 `*` 剝掉,
  若剩下的開頭**不是** `不得`／`不可`／`禁`／`一律`／`必須`／`不是`／`非`／`不代表`／`不等於`／`刻意` ⇒ **判紅**;
  另加 `⛔⛔`／`⭐⭐` 疊字命中即判紅。
  ⚠️ 早期版本寫成「`⛔ **` 命中即判紅」—— 那會把合法的 `⛔ **不得…**` 判成違規(誤報),
  而**一個會誤報的 gate 會被關掉**(`[[feedback_rule_vs_coincidence]]`:判準要用突變測,不用 needle)。

  ⚠️ **豁免**:被反引號包起來的符號是**在講這個符號**(如 `` `⛔` `` 的用法說明),不是在用它 ⇒ 不判紅。
**為什麼(成本在哪)**:AI 讀文件時裝飾標記除了佔 token,還會**主動誤導** —— 「被標記」暗示「這裡有邊界」。
實測基準(2026-09-04,`bizcard-billing-phase0-schema-design-spec.md` 1,217 行):**687 個 `⛔` 中只有 21% 是禁令或區辨,32% 是純裝飾**
⇒ 該符號失去鑑別力 ⇒ 讀者學會忽略它 ⇒ **真正那 10% 的禁令跟著一起被忽略。**
⇒ 這比完全不標更糟:**沒有標記只是沒有捷徑,壞掉的標記是一條會把人帶到錯地方的捷徑。**

---

## Finding Schema(問題解決 — Minerva 強化點 2)

**每個 4-tier finding 強制三步驟結構(命名 / 主張 / 追求)+ 7 大欄位(對齊 §6.4.3.D)。**

### Required fields per finding(7 大欄位,對齊 PM Skill §6.4.3.D)

```yaml
finding:
  # 1. 識別 ─────
  tier: 🔴 BLOCKER | 🟡 CONCERN | 🟢 NIT | ✅ STRENGTH
  id: B1 / C1 / N1 / S1   # round 內流水
  name: "簡潔標題 1 行內"
  evidence:
    - "<target>:<line>"
  
  # 2. severity 三件套 ⭐ Default + Override
  severity:
    score:
      value: 5.5             # 當前生效值(PM Skill /pm-bug-review reads this)
      default: 8.0           # spectra-review 原 estimate(LOCKED 跨 round 不可變)
      override:
        by: null             # PO | SKILL | null(Round 1 spectra 寫 default 時 null)
        at: null
        reason: null
    band: med                # auto from value: <3=low / 3-6=med / >6=high
    semantic: how_bad        # how_bad(B/C/N) | how_valuable(STRENGTH)
  
  # 3. fix_economics 三件套
  fix_economics:
    difficulty:
      value: 2.0
      default: 2.0
      override: null
    roi:
      value: 2.75            # auto: severity.score.value / difficulty.value
      default: 4.0
    resource_estimate:
      value: "4h"            # 1h / 2h / 4h / 1d / 2d / 1w
      default: "2h"
      override: null
  
  # 4. cross_impact(既有 LOCKED,PO 不可 override)
  cross_impact:
    affected_modules: [...]
    cascade_depth: 1-5
    dependency_chain: "..."
  
  # 5. phase_aware
  phase_aware:
    current_phase: 0-7
    if_not_fixed_now_breaks_at: 0-7
    estimated_rework_cost: low | medium | high
  
  # 6. decision_tree(LOCKED options content)
  decision_tree:
    options:
      - { id: A, action: "不修", cost: ..., notes: "..." }
      - { id: B, action: "現在修", cost: ..., notes: "..." }
      - { id: C, action: "延後修", cost: ..., notes: "..." }
    recommended_option: B
    counterfactual: "..."
  
  # 7. dependencies + severity_decay
  dependencies:
    blocks: [B2, C3]         # SKILL 估
    blocked_by: [B1]
    manual_blocks: []        # PO 加,SKILL 不動
  
  severity_decay:
    phase_when_found: 1
    by_phase:
      2: { value: 8.0, default: 8.0, override: null }
      3: { value: 9.0, default: 9.0, override: null }
  
  # PO 拍板狀態(Round 1 一律 no_decision)
  po_decision:
    status: no_decision
    decided_at: null
    decided_by: null
    reason: null
```

### Calibration Baseline reference

對齊 PM Skill 4 個 artifact 9 rounds 累積經驗 — 詳見下方獨立 §Calibration Baseline 段(對齊 Round 2 N2 fix — 提升為 top-level 段,跨 Section 通用 scoring 標準)。

---

## Calibration Baseline(top-level 通用 scoring 標準,對齊 Round 2 N2 fix)

對齊 PM Skill 4 個 artifact / 9 rounds 累積 + §6.4.10 §B.2 Calibration Baseline。本段 baseline 應用範圍:
- Finding severity scoring(§Finding Schema)
- Hotspot 等級判定(§Critical Hotspots)
- Effective Cost matrix 解讀(§Output Format §4)
- 重大 BLOCKER 觸發 Reflection 段(§Reflection)

**Impact Level Scale(0-10):**

| Level | Range | Description |
|:---:|:---:|:---|
| 🟢 低 | 0-3 | 局部影響,單一 file / function;不影響其他 module |
| 🟡 中 | 4-6 | 跨 file / 跨 section;單一 module 內部 cascade |
| 🔴 高 | 7-10 | 跨 module / 業務邏輯失效 / 系統 critical |

**Probability Scale(0.0-1.0):**

| Level | Range | Description |
|:---:|:---:|:---|
| 🟢 低 | < 0.3 | 罕見 edge case,需多重條件觸發 |
| 🟡 中 | 0.3-0.7 | 一般使用情境會遇到 |
| 🔴 高 | > 0.7 | 必發生,當前 phase 內可預見 |

**Effective Cost Interpretation(impact × probability,0-10):**

| Cost Range | Severity Implication | Action |
|:---:|:---|:---|
| < 1 | 低成本 | NIT,可選修 |
| 1-3 | 中低成本 | CONCERN,應修 |
| 3-5 | 中高成本 | CONCERN 升 BLOCKER 邊界 |
| > 5 | 高成本(系統 critical)| BLOCKER,必修 |

**Calibration 維護原則:**

- baseline 為組織通用標準(對齊 §6.4.10 §B.2 lock)
- 跨 project 沿用,新 project 不需重校準
- Phase C 試跑後 PO 可微調,需走 §6.4.13 Contract Change Governance patch level

---

## Cross-Impact Analysis(複雜系統 — Minerva 強化點 3)

每個 finding 必填 cross_impact field(對齊 §Finding Schema 第 4 段)。

### Critical Hotspots(verdict 段必加)

識別本輪 review「**牽一髮動全身**」的 fragile points:

- 🔥🔥🔥 極臨界(`cascade_depth ≥ 4`,跨層級或全系統)
- 🔥🔥 高臨界(`cascade_depth = 3`,遠端 cascade)
- 🔥 中臨界(`cascade_depth = 1-2`,直接或間接)

**Hotspot shortcut table:**

| effective_cost | cascade_depth | Hotspot 等級 |
|:---:|:---:|:---:|
| > 5 | ≥ 4 | 🔥🔥🔥 |
| > 5 | = 3 | 🔥🔥 |
| > 5 | 1-2 | 🔥 |
| 1-5 | ≥ 4 | 🔥🔥 |
| 1-5 | ≤ 3 | 視 case,通常無 hotspot |
| < 1 | any | 無 hotspot |

每個 hotspot 註記早期解 vs 晚期解成本 + ratio。

---

## Decision Tree(決策思維 — Minerva 強化點 4)

**每個 BLOCKER 強制 Decision Tree(≥ 2 options:現在修 vs 不修;推薦加「延後修」第 3 option)。**

### Verdict 段必加「Effective Cost Matrix」

整理本輪所有 findings 的 cost,輸出表格 + 總計 + saving。

### 反事實必填

每個 BLOCKER 必含 `counterfactual: "If do nothing, expected outcome: ..."`

---

## Output Format(F1 Per-Round Review Log)

### F1 File path(對齊 Round 2 C3 fix — 統一規則:enhanced mode 必寫 file)

- OpenSpec mode: `openspec/changes/<target>/spectra-review-round-N.md`(**必寫 file**,per-change local)
- PM Skill mode: `docs/reviews/<active-project>/<date>-spectra-<target-slug>-round-N.md`(**必寫 file**)

Both modes write F1 in enhanced mode. Only `--lite` mode skips file persistence(對齊 §Output Persistence)。

### F1 Frontmatter

```yaml
---
target: <full path>
target_rev: <hash or rev .N>
date: <YYYY-MM-DD>
reviewer: spectra-review (v2.0)       # SKILL impl version
iteration: <N>
verdict: ship-as-is | fix-blockers | revise-design
schema_version: enhanced-v1            # F1/F2 output format schema version
contract_version: spectra-contract-v1  # contract (alignment with §6.4.3) version
mode: openspec | pm-skill-req-spec | pm-skill-module-plan | ...
---
```

**Version naming convention(對齊 Round 2 N1 fix):**
- `reviewer`(eg. `v2.0`)= SKILL implementation version(this SKILL.md file revision)
- `schema_version`(eg. `enhanced-v1`)= F1/F2 output format schema version(independent — changes when output template changes)
- `contract_version`(eg. `spectra-contract-v1`)= alignment with PM Skill proposal §6.4.3 contract version(independent)

三層 version 各自獨立升級:SKILL impl 可在同一 schema/contract 下迭代 features(對齊 §6.4.2 I3 升級獨立 invariant)。

### F1 Body Structure(5 sections,對齊 PM Skill F1 contract)

```markdown
> 💡 spectra-review v2.0 active(Minerva 4 能力 framework)。若想用原版簡潔版,用 `/spectra-review --lite <target>`。

# Spectra-Review Round N — <target>

## § 1. Mental Lens
(4 mental acts 本輪採用)

## § 2. 4-Tier Findings

### 🔴 BLOCKERS — 落地前必修

#### B1. <name>

**📛 命名(Identify):** ...

**📣 主張(Assert):**
- Why BLOCKER: ...
- Impact: X/10 / Probability: 0.X
- Evidence: <file:line>
- Cross-Module Impact: ...
- Phase-aware: ...

**🎯 追求(Pursue):** ...

**📊 Decision Tree:** (table A/B/C 成本)
**📍 推薦:** Option <X>
**🔮 反事實:** ...

### 🟡 CONCERNS — 應修
(same format,可簡 Decision Tree 為 2 options)

### 🟢 NITS — 可選 polish
(精簡格式:name / 1-line assert / 1-line pursuit)

### ✅ STRENGTHS
- <bullet 設計亮點>

## § 3. Critical Hotspots
(等級 + 早晚解 ratio)

## § 4. Effective Cost Matrix
(全 finding cost 表 + 總 + saving)

## § 5. Decision Log
(本輪新拍板 + carry forward)

## § 6. Verdict + Next Round Focus
(Status + Recommend + Next Round Focus)

## § 7. Mental Lens Reflection(只在 重大 BLOCKER ≥ 2 個時)
```

---

## F2 Aggregate Summary(嚴格對齊 §6.4.3.C contract)

### F2 File Path

- OpenSpec mode: 不強制(legacy 只用 F1)
- PM Skill mode: `docs/reviews/<active-project>/_summary-<target-slug>.md`(必存)

### F2 Mandatory Sections(4 段)

**Frontmatter:**

```yaml
---
target: <target path>
target_slug: <slug>
total_rounds: <N>
last_round_date: <YYYY-MM-DD>
last_verdict: ship-as-is | fix-blockers | revise-design
schema_version: enhanced-v1
contract_version: spectra-contract-v1
---
```

**Section 1: Cumulative Findings Tally**(每 round 一 row,append-only)

```markdown
## Cumulative Findings Tally

| Round | Date | BLOCKER | CONCERN | NIT | STRENGTH | Verdict |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | 2026-06-17 | X | X | X | X | <verdict> |
| **Total** | | **X** | **X** | **X** | — | — |
```

**Section 2: Issue Status Matrix**(每 finding 一 row — PM Skill `/pm-bug-review` 主要 metric 來源)

```markdown
## Issue Status Matrix

| Round | ID | Tier | Title | severity_score | fix_roi | Status | PO 決策 |
|:---:|:---:|:---:|:---|:---:|:---:|:---:|:---|
| 1 | B1 | 🔴 | ... | 8.0 | 4.0 | ⏸ no_decision | — |
```

**Status enum:** `✅ fixed` / `⏳ pending`(已 accept 未實作)/ `⏸ no_decision`(PO 未表態)/ `❌ rejected` / `🔁 deferred` / `✅ valued`(STRENGTH 專用)

**Section 3: Quality Health Score**

```markdown
## Quality Health Score

- total_findings: <N>
- fixed: <N>
- pending: <N>
- no_decision: <N>          ⭐ PM Skill /pm gate-check 重點
- rejected: <N>
- deferred: <N>
- valued: <N>(STRENGTH)
- fix_rate: <%>             = fixed / (total - strengths)
- close_rate: <%>           = (fixed + rejected + deferred + valued) / total
- avg_severity_open: <X.X>
- po_overrides: <N>         ⭐ 透明度 metric
- convergence_signal: ✅ | ⚠ | ❌
```

**Section 4: Hotspot History**(累積)

```markdown
## Hotspot History

| Round | Hotspot | 等級 | 是否解 |
|:---:|:---|:---:|:---:|
| 1 | ... | 🔥🔥🔥 | ⏸ pending |
```

### F2 Invariants(對齊 §6.4.3.E)

- **INV-1**: 每 round 結束,append 1 row 到 F2 Cumulative tally;**不可改前輪 row**
- **INV-2**: F2 Issue Status Matrix 每個 finding 必有 row;「未表態」必顯式列 `status='no_decision'`
- **INV-3**: 所有 finding 必填 7 大欄位 + Default 子欄位
- **INV-4**: 同一 round 重跑,僅更新該 round row,**不 append duplicate**
- **INV-5**: `value` = PM Skill 用的當前值;`default` = spectra-review 原值(**LOCKED 跨 round 不可變**);`override` = audit trail
- **INV-6**: 任何 override 必含非空 `reason`(空 reject);override 後自動 recalc `roi.value`

---

## Confidence Tier(對齊 PM Skill user manual rev 1.6 prefix block)

Every output containing analytical claim MUST classify:

| Tier | Confidence | Behavior on failure / uncertainty |
|:---:|:---:|---|
| 🟢 high | ≥ 90% | Abort + specific error |
| 🟡 medium | 60-90% | List evidence + ask PO;不強推結論 |
| 🔴 low | < 60% | Refuse to conclude;list raw data only |

**Default classification per spectra-review section:**

| Section | Tier |
|---|---|
| Finding evidence file:line citation | 🟢 high(file read deterministic) |
| Naming consistency check | 🟢 high(grep / pattern match) |
| Counting / arithmetic | 🟢 high(deterministic) |
| Severity score estimate | 🟡 medium(LLM judgment + Calibration Baseline) |
| Cross-impact analysis | 🟡 medium(cascade depth requires LLM understanding) |
| Phase-aware prediction | 🟡 medium(forecasting) |
| Anti-Bias self-judgment | 🟡 medium(introspection) |
| Inferring design intent | 🔴 low(speculation;always cite evidence) |

---

## Path Conventions(對齊 Round 5 PM Skill architectural fix)

### PM Skill mode 強制 per-project subfolder

```
docs/reviews/<active-project>/
├── _summary-<target-slug>.md             # F2 aggregate(append-only rows)
├── <date>-spectra-<target-slug>-round-1.md
├── <date>-spectra-<target-slug>-round-2.md
└── ...
```

### Target slug 生成規則

- For `docs/pm/pm-skill/spec/pm-skill-proposal.md` §6.4 → `pm-skill-proposal-section-6-4`
- For `docs/modules/<project>/_plan.md` → `<project>-module-plan`
- For full file: derive from filename minus date prefix + extension

---

## PM Skill Integration

### Invoked by `/pm validate-*`

PM Skill SKILL.md §validate-* workflows delegate to spectra-review by:

1. Resolving the artifact target(eg. requirement spec path)
2. Determining the contract version to validate against(§6.4.10 §B / §6.4.11 §B-H per phase)
3. Calling spectra-review with that target + cross-ref expectations

Spectra-review's job is to:
- Run 7 dimensions × Mental Lens
- Output F1 + F2 with 7-field findings
- Hand back verdict for PM Skill to decide pass/fail at gate-check

### Composes with `/pm-bug-review`

After spectra-review produces F2 with `status: no_decision` findings:
- PM Skill `/pm-bug-review <target-slug>` reads F2
- Walks PO through each finding offering Default vs Override 選項
- Writes override 三件套(by/at/reason)to finding's severity/fix_economics
- Updates F2 Quality Health Score (`po_overrides++`)
- Appends to `docs/pm/<project>/decision-log.md`

### Audit trail(對齊 Round 2 C1 fix — bridge mode 完整覆蓋)

Per-mode audit destination(每個 mode 寫不同 decision-log,確保 audit 必存 INV-6):

| Mode | Audit destination |
|---|---|
| PM Skill modes(req-spec / module-plan / module-spec / etc.)| `docs/pm/<active-project>/decision-log.md` |
| **OpenSpec mode(legacy)** | `docs/pm/_org/org-decision-log.md` with `mode: openspec` field |
| PM Skill — Meta(self-review / proposal)| `docs/pm/_org/org-decision-log.md` |
| PM Skill — Contract Pack | `docs/pm/_org/org-decision-log.md` |

Entry format(對齊 Round 2 N3 fix — 具體範例):

```
D-spectra-<round>.<finding_id>: <target_slug> tier=<T> severity_default=<X> mode=<M> | by: SKILL at: <ISO8601>
```

具體範例:

```
D-spectra-1.B1: pm-skill-proposal-section-6-4 tier=BLOCKER severity_default=8.0 mode=pm-skill-meta | by: SKILL at: 2026-06-17T15:30:00+08:00
D-spectra-1.C1: 2026-05-20-vehicle-plate-field tier=CONCERN severity_default=4.5 mode=openspec | by: SKILL at: 2026-06-17T16:15:00+08:00
```

---

## Reflection Section(訓練 PO 思考習慣 — preserved)

**只在重大 BLOCKER ≥ 2 個 / 輪時加 Reflection 段**。

### 「重大 BLOCKER」明確定義

對齊 Calibration Baseline,重大 BLOCKER 定義為**同時滿足**:
- `impact_level ≥ 7`
- `probability ≥ 0.5`
- 等同 `effective_cost ≥ 3.5`

### 觸發邏輯

本輪 review 結束時計算:
- **重大 BLOCKER 數** = 4-Tier Findings 中,符合 `tier='🔴 BLOCKER' AND impact_level ≥ 7 AND probability ≥ 0.5` 的數量
- **若 ≥ 2** → 觸發 Reflection 段(附在 § 6 Verdict 之後)

### Reflection 格式

```markdown
## Mental Lens Reflection(給 PO 的思考訓練)

- **批判思考應用:** ...
- **複雜系統應用:** ...
- **決策思維應用:** ...
```

---

## Lite Mode(原版 backward-compat,preserved)

若 user invoke `/spectra-review --lite <target>`:
- **跳過** Mental Lens / Cross-Impact / Decision Tree / Reflection / F2
- 維持原版 4-tier 簡潔輸出(對齊 既有 100 行版本)

Lite Mode 適用:
- 快速 sanity check
- 小 proposal(< 200 行)
- PO 已熟悉設計,只要快速看 issue list

Lite Mode 輸出:

```markdown
**🔴 BLOCKERS** — must fix before apply
1. <issue> — <file:line> — **Fix**: <recommendation>

**🟡 CONCERNS** — should fix
<same>

**🟢 NITS** — optional polish
<same>

**✅ STRENGTHS** — what's solid
- <bullet>

**Recommend:** ship-as-is / fix-blockers / revise
```

---

## Output Persistence

### v2.0 enhanced mode 必寫 file

- **F1 per-round log**(必)— `docs/reviews/<project>/<date>-spectra-<slug>-round-N.md`
- **F2 aggregate summary**(必)— `docs/reviews/<project>/_summary-<slug>.md`(round 1 新建,後續 round append rows)
- **Audit entry** to `docs/pm/<project>/decision-log.md`(必)

### Lite mode

- Inline output only(維持 backward-compat)
- 若 user 想 archive 可手動 redirect

---

## Cross-SKILL Integration Map

| 觸發 | SKILL | 我的 role |
|---|---|---|
| `/pm validate-req-spec <path>` | PM Skill SKILL → spectra-review | review target |
| `/pm validate-module-plan <path>` | PM Skill | review target with `module-plan` mode |
| `/pm-bug-review <slug>` | PM Skill | reads my F2 for adjudication |
| 直接 `/spectra-review <target>` | user → me | full standalone review |
| OpenSpec V3 / V4 / V8 modes | namecard-v2 guardian | composes spectra-review for design review |

---

## Tone

Critical but constructive. Do not rubber-stamp. Bias toward finding issues. If genuinely nothing to flag in a tier, write "(none found)".

**Understand-not-argue stance:** 不只 reject,要 propose 替代方案 + 對齊原意。

**Anti-Bias enforcement:** Self-authored content treats Anti-Bias as MANDATORY deep-check, not optional.

---

## Out of Scope

- Do NOT auto-apply fixes. Only report. User decides next step via PM Skill `/pm-bug-review`.
- Do NOT edit the target files unless user explicitly asks afterwards.
- Do NOT run `git` commands beyond `log` reads.
- Do NOT call external APIs.
- Do NOT bypass `/pm gate-check` — spectra-review verdict is input,not authoritative pass/fail.

---

## Version

- **v2.0**(2026-06-17)— Bridge edition:project-level + slash command + PM Skill mode + F1/F2 explicit + 7-field finding default + Confidence Tier + PM integration
- **v2.0.1**(2026-06-17)— self-review Round 1 fix(0 BLOCKER + 4 CONCERN + 5 NIT 全 close):C1 PM Skill Integration 加 per-mode audit destination table + 具體範例;C2 Mode Detection Generic doc baseline 改「無 specific contract」;C3 F1 file path 統一「enhanced mode 必寫」(OpenSpec 寫 `openspec/changes/<X>/`);C4 Start Here 分 Always Read(3)vs Conditional Read(5,enhanced only);N1 version naming convention 註記三層獨立(reviewer / schema_version / contract_version);N2 Calibration Baseline 提到 top-level 獨立段(跨 section 通用 scoring);N3 audit entry 加 2 個具體範例;N4 Mode Detection 加 pm-skill-state + pm-skill-contract-pack entries;N5 加 Trigger Priority Note(v1+v2 並存 LLM 選擇優先序 + Phase E migration recommendation)
- **enhanced-v1**(2026-06-17)— Minerva 4-ability framework(analytical core,preserved)
- **base v0**(原版)— remains via `--lite`

## See Also

- `docs/pm/pm-skill/spec/pm-skill-proposal.md` rev 1.12 §6.4.3 — spectra-review contract authoritative source
- `docs/pm/pm-skill/docs/pm-skill-user-manual.md` rev 1.8 — review usage scenarios(2 / 8 / etc.)
- `../pm-skill/SKILL.md` v1.0.1 — PM Skill workflow that delegates to me
- `references/finding-template.md` — 7-field finding stub(this dir)
- `references/f2-schema.md` — F2 schema reference(this dir)
