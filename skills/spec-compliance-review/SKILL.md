---
name: spec-compliance-review
description: Specification Compliance Reviewer (SCR) — V7 mode skill. Reviews code (*.py / *.js / *.html / *.sql / config) against 3-layer spec (requirement / functional / design) for bi-directional compliance. Triggered by `/spec-compliance-review <target>` slash command OR `V7 <target>` mode dispatcher. Composes 7-reviewer architecture (R0-R6) + SG 4-state verdict (PASS / SOFT FAIL / HARD FAIL / PENDING).
---

# SCR — Specification Compliance Reviewer

Use this skill when the user types `/spec-compliance-review` OR `V7 <target>` OR asks "spec compliance review this code".

This skill implements the design documented in [`docs/pm/v7-spec-compliance-review/spec/scr-requirement-spec.md`](docs/pm/v7-spec-compliance-review/spec/scr-requirement-spec.md) (**rev 0.3.0** — SKILL.md **v0.6** cascade:v0.3 NL UX + v0.4 § 8.13 Lifecycle doc + v0.5 OQ-6 adapter auto-dispatch wiring + **v0.6 § 8.13.4 8-step structural mirror — 8 step-by-step actionable subsections**)。

## Multi-IDE Bootstrap

| Tool | Loading Mode | User Action Required |
|---|---|---|
| **Claude Code** | Native skill load | No action — `/spec-compliance-review <target>` OR `V7 <target>` triggers this skill |
| **Antigravity** | Repo-aware auto read | Usually auto; explicit `/spec-compliance-review` mention boosts consistency |
| **Codex / VSCode** | Repo-file fallback | Paste bootstrap prompt below at session start |

**Codex bootstrap prompt:**

```text
先讀 docs/CONTEXT.md、docs/ai-principles.md §3 Mode Map(V7 entry)、
docs/pm/v7-spec-compliance-review/spec/scr-requirement-spec.md。
若我輸入 /spec-compliance-review <target> 或 V7 <target>,
讀 skills/spec-compliance-review/SKILL.md 執行 R0-R6 reviewer + SG verdict。
```

## Trigger Convention

User can invoke V7 SCR via **3 entry forms**(NL-first per rev 0.2.6 § 8.7):

### Form 1: Natural Language(default — preferred per § 8.7)

```bash
v7 review sanity check 看還剩什麼          # multi-slot NL parsed
v7 看 OTP 流程做完沒                       # feature description NL
v7 ship 前 check 這個 PR                   # git-diff target NL
v7 review TC JSON 24-field schema          # NL feature description
v7 比較這次跟上次的差距                    # trend-focused NL
```

SKILL 自動 parse **4-slot intent**(action / target / verbosity / focus_lens)per § 8.7 之 L2-L5 parsing chain;歧義時跳 popup disambiguation(per § 8.7.1)。 詳見下方 `## NL Invocation Parser` section。

### Form 2: Discovery(NEW v0.3 per § 8.8)

```bash
v7 ?
v7 help
v7 你能做什麼
v7 怎麼用
```

→ Returns plain-prose discovery card(8-10 NL examples)。 詳見下方 `## Help / Discovery` section。

### Form 3: Flag-based(advanced — backward compat)

```bash
/spec-compliance-review <target>             # direct slash command
V7 <target>                                  # V7 mode dispatcher
/spec-compliance-review --req REQ-019        # explicit REQ-ID list
/spec-compliance-review <target> --full      # verbosity flag
```

Both Form 1 + Form 3 paths 同樣 converge to R0-R6 execution + SG verdict per `scr-requirement-spec.md` § 1.2 dual-name design contract。

### Negative Scope Reject(NEW v0.3 per § 8.9)

非 SCR intent 之 `v7 ...` input 必明拒(不 silent 硬跑):

- 「v7 寫 component」/「v7 修 bug」/「v7 重構這段」 → reject + redirect
- 7 reject categories + template 詳見下方 `## Negative Scope Reject` section

### Invocation Flags(per spec § 8.5 + § 8.6 — Form 3 advanced)

**Target specification flags(per § 8.5 REQ-ID + NL Targeting):**

```bash
# Form 1: File/dir target (default — existing behavior)
/spec-compliance-review scripts/sanity_tc_*.py

# Form 2: Direct REQ-ID list
/spec-compliance-review --req REQ-019
/spec-compliance-review --req REQ-019,REQ-024,REQ-025

# Form 3: Natural language feature description
/spec-compliance-review --feature "OTP 登入流程"
v7 review 「TC JSON 24-field schema」

# Form 4: Combined
/spec-compliance-review scripts/ --req REQ-019 --feature "schema validate"
```

**Verbosity flags(per § 8.6):**

```bash
/spec-compliance-review <target>              # default = --brief (PM-friendly ~80-150 LOC output)
/spec-compliance-review <target> --brief      # 簡要 mode (explicit)
/spec-compliance-review <target> --medium     # QA test planning level
/spec-compliance-review <target> --full       # audit + dev debugging (~400-500 LOC + Appendix)
/spec-compliance-review <target> --verbose    # alias for --full
```

**Other override flags:**

```bash
/spec-compliance-review <target> --tier=heavy             # cost-staged override (per § 4.9)
/spec-compliance-review <target> --no-architectural-change # arch detection override (per § 8.4 C3)
/spec-compliance-review <target> --bypass=urgent-fix      # PO emergency bypass (per § 7)
```

**Configuration priority(per § 8.6):**
1. CLI flag — highest
2. Environment variable `SCR_VERBOSITY`
3. `state.md` `scr_default_verbosity:` field
4. Global default = `--brief`(per PM-friendly first invariant)

Unknown invocation → respond with skill help(`§Subcommand: help` below)。

## Start Here

Before handling ANY invocation, read these in order:

**Repo bootstrap(對齊 ai-principles.md §2 Bootstrap Read Order):**

1. `docs/CONTEXT.md` — repo 現況快速 context
2. `docs/ai-principles.md` — repo-wide AI 工作原則(含 §3 Mode Map V7 entry + §4.1 Three Immutable Rules)
3. `docs/index.md` — repo doc 全索引

**SCR-specific(對齊本 SKILL 邏輯):**

4. `docs/pm/v7-spec-compliance-review/spec/scr-requirement-spec.md` — authoritative source for 7 reviewer architecture / SG verdict / scope mechanism / cost-staged tier / per-stack adapter
5. `docs/pm/v7-spec-compliance-review/decision-log.md` — D-001 ~ D-060 governance trail
6. `docs/pm/active-project.txt` (if exists) — current active project for SCR cross-project context

**Conditional(per invocation context):**

7. Target's 3-layer spec(`docs/pm/<project>/spec/`)
8. `docs/pm/<project>/state.md` — `project_maturity` field for SG threshold pick
9. Memory rules referenced in target(`[[backend-change-rule]]` 等)

## Mode Detection — R0 Mode Auto-Pick

Per `scr-requirement-spec.md` § 4.1 R0 mode auto-detection,scan target project's spec layers:

```bash
# Detection algorithm:
ls docs/pm/<project>/spec/ | grep -E "(requirement|functional|design)-spec\.md$"
```

| Spec layers found | R0 mode | R1-R5 scope |
|:---:|:---|:---|
| 3-layer(req + func + design)| **R0-full** | req↔func↔design 三層 cross-check;full R1-R5 enabled |
| 2-layer(req + func OR req + design)| **R0-medium** | 已存在兩層 cross-check;R3 或 R4 may degrade |
| 1-layer(only req)| **R0-lite** | spec syntax + REQ-ID uniqueness + internal self-consistency;R3 R4 skip |

**Mode persists 整 invocation** — auto-detected mode 不可中途切換。

## Cost-Staged Tier — Invocation Scope Auto-Pick

Per `scr-requirement-spec.md` § 4.9 cost-staged tier(rev 0.2.3),scan git diff + scr_scope metadata:

```bash
# Detection inputs:
git diff --stat HEAD~1 HEAD | tail -1  # LOC count (code stack only)
git log -1 --pretty=%B | grep -E "^scr-scope:"  # scope declaration footer
```

| Tier | Trigger | Sub-tool scope |
|:---|:---|:---|
| **Light** | < 50 LOC code stack(`*.py / *.js / *.ts / *.html / *.css / *.sql`)AND 無 architectural change AND 無 memory rule touch | R0 + R1 + R6 only;skip R2-R5 detail |
| **Medium** | 50-300 LOC code OR ≥ 1 REQ scope declared | Full R0-R6 |
| **Heavy** | > 300 LOC code OR architectural change OR memory rule touch | Full R0-R6 + heavy detection tier |
| **Force-full** | `/spec-compliance-review --full` OR `project_maturity=mature` | Full R0-R6 regardless |

LOC counting rule:include `*.py / *.js / *.ts / *.html / *.css / *.sql`;exclude `*.md / *.txt / *.json (unless schema) / docs/*/`(對齊 § 4.9 N1 closure)。

### Cost + Time Preview(v0.3 NEW per spec § 8.10)

**Purpose:** Before actual run,echo 1 行 budget — let PM make informed decision between 3 分鐘 vs 30 秒。

**Preview content template(echo after popup confirm,before atomic run):**

```markdown
> 🎯 OK 我會跑:整個 sanity-check 專案 / 詳細版 / 看 remaining task
> ⏱ 預估 ~3 分鐘 / 輸出 ~600 行
> 💰 預估 ~5k tokens
> ⚠ 跑到一半可隨時 Ctrl-C 中斷,partial output 自動清理(per Escape Route)
```

**Threshold-based 2-stage confirm:** 若預估 ≥ heavy tier(> 5 min OR > 10k tokens OR > 1000 LOC output),SKILL **必再次 confirm**:

```
⚠ 此 review 規模較大(預估 8 分鐘 / 12k tokens / ~900 行)
要繼續嗎? [y] / [n] / [改成簡要版]
```

**Per-tier calibration table(對齊 § 4.9 cost-staged tier):**

| Tier | Time | Output LOC | Tokens |
|:---|:---|:---|:---|
| light(< 50 LOC code)| 10-30 sec | 50-100 LOC | 0-1k |
| medium(50-300 LOC)| 30 sec - 2 min | 100-300 LOC | 1-3k |
| heavy(> 300 LOC)| 2-5 min | 300-600 LOC | 3-8k |
| force-full(全 project)| 5-15 min | 600-1500 LOC | 8-20k |

每次 invocation 結束後 actual cost 寫入 `state.md` `v7_cost_calibration:`(rolling N=20)+ `metrics.json` `nl_intent_resolution.actual_cost`(per Persistence — § 8.12)— 對齊 § 8.10 C3 closure SSOT delineation(metrics 為 per-invocation truth;state aggregate;§ 7.3 SG-Bypass 為 independent sink)。

## Invocation Lifecycle — 8-Step Canonical Flow(v0.4 NEW per spec § 8.13)

**Purpose:** Consolidate § 8.7(NL parse + popup)+ § 8.10(cost preview + heavy-tier gate)+ § 8.11(escape route)+ § 8.12(audit log)散在 4 sub-sections 之 sequence 為 1 numbered flow chart,SKILL impl reader 不需 reconstruct。 對齊 spec § 8.13.4「SKILL.md v0.3+ implementing this lifecycle 應 mirror 8-step structure in code organization」。

### 8-Step Canonical Flow(spec § 8.13.1 mirror)

```
┌──────────────────────────────────────────────────────────────────────┐
│  V7 SCR Invocation Lifecycle(canonical 8-step)                       │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. NL parse → 4-slot intent extraction (§ 8.7)                      │
│     action / target / verbosity / focus_lens                         │
│         │                                                            │
│         ▼                                                            │
│  2. Confidence threshold check (§ 8.7 popup contract)                │
│     ┌─ All ≥ 0.9 ──────────────► skip popup, goto 3                  │
│     ├─ 1 slot 0.7-0.9 ──────────► single popup → answer → goto 3    │
│     ├─ ≥ 1 slot < 0.7 ──────────► multi popup (§ 8.7.1) → goto 3    │
│     ├─ All unparseable ─────────► reject + suggest `v7 ?` (§ 8.8)   │
│     └─ Non-SCR intent ──────────► reject + redirect (§ 8.9)         │
│         │                                                            │
│         ▼                                                            │
│  3. Echo final parsed intent (1 line — per § 8.10 banner pattern)    │
│         │                                                            │
│         ▼                                                            │
│  4. Cost + Time Preview (§ 8.10 — 5-field template)                  │
│     target / time / output LOC / tokens / Ctrl-C cancel hint         │
│         │                                                            │
│         ▼                                                            │
│  5. Heavy-tier gate check (§ 8.10 — > 5min OR > 10k OR > 1000 LOC)   │
│     ┌─ Not heavy ─────────────► goto 6                              │
│     ├─ Heavy, user [y] ──────► goto 6                              │
│     ├─ Heavy, user [n] ──────► cancel(audit `cancelled_preview`)  │
│     └─ Heavy, user [改簡要] ──► verbosity = brief, goto 6           │
│         │                                                            │
│         ▼                                                            │
│  6. Run R0-R6 review                                                 │
│     Write tmp files atomically (§ 8.11 — `<dir>/.scr-tmp-*` random) │
│     Ctrl-C during run → atomic cleanup + audit `cancelled_mid_run`  │
│         │                                                            │
│         ▼                                                            │
│  7. Write audit log (§ 8.12 — metrics.json `nl_intent_resolution`)   │
│     status ∈ {completed, cancelled_preview, cancelled_mid_run,       │
│               rejected_negative_scope}                               │
│     (Popup ⓧ silent — does NOT write per § 8.11 L1 Option A)         │
│         │                                                            │
│         ▼                                                            │
│  8. Cleanup tmp → final mv + emit output                             │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### Step Cross-Reference Matrix(spec § 8.13.2 mirror)

| Step | SKILL by-step anchor(v0.6 NEW)| SKILL by-feature section | Spec section | Key contract |
|:---:|:---|:---|:---|:---|
| 1 | `### Step 1 — NL parse → 4-slot intent extraction` | `## NL Invocation Parser` | § 8.7 | 4-slot intent model + L2-L5 parsing chain |
| 2 | `### Step 2 — Confidence threshold check + popup dispatch` | `## Popup Disambiguation Contract` | § 8.7.1 | 5 mandatory conditions(PM 語言 / 附成本 / 預設選 / ⓧ escape / echo)|
| 3 | `### Step 3 — Echo final parsed intent banner` | `### Cost + Time Preview` banner row 1 | § 8.10 banner | 1-line echo of final resolved intent |
| 4 | `### Step 4 — Cost + Time Preview emission` | `### Cost + Time Preview` template | § 8.10 | 5-field preview template |
| 5 | `### Step 5 — Heavy-tier gate 2-stage confirm` | `### Cost + Time Preview` 2-stage confirm | § 8.10 | Heavy-tier 2-stage confirm `[y]`/`[n]`/`[改簡要版]` |
| 6 | `### Step 6 — Run R0-R6 + atomic tmp write` | `### Atomic Write Pattern` + `## What to Check` | § 8.11 atomic + § 4.1-4.7 | `<output_dir>/.scr-tmp-<timestamp>-<rand-6>.{json,md}` + PID-bound cleanup |
| 7 | `### Step 7 — Write audit log entry` | `### metrics.json Schema` | § 8.12 | 4-state status enum + `format_version: scr-rev-0.2.6-nl-v1` |
| 8 | `### Step 8 — Cleanup tmp → final mv → emit output` | `### Atomic Write Pattern` final mv | § 8.11 atomic | `mv .scr-tmp-*.json final.json` 完成標誌 |

### Status Audit Path Map(spec § 8.13.3 mirror)

| Exit path | Step | metrics.json audit log status |
|:---|:---|:---|
| Happy path completion | Step 8 | `completed` |
| User cancels at heavy-tier gate | Step 5 `[n]` | `cancelled_preview` |
| User Ctrl-C mid-run | Step 6 | `cancelled_mid_run` |
| Negative scope reject | Step 2 → § 8.9 | `rejected_negative_scope` |
| Popup ⓧ escape | Step 2 → § 8.11 L1 | **silent — no log entry**(per § 8.11 L1 Option A B1 closure)|
| All unparseable + help suggested | Step 2 → § 8.8 | **silent — no log entry**(per § 8.7 popup contract row 4)|

### SKILL impl alignment note

每個 SKILL section 從 `## NL Invocation Parser` 到 `### Atomic Write Pattern` 都對應 lifecycle 一 step;reader 看到 step number 即知道對應 SKILL section + spec section(三方 anchor lock)。 Future code organization implementing dispatcher should mirror 8-step structure(eg. `dispatch_v7()` 含 numbered comments per step)— 對應 maintenance / debugging future invocations 之 structured tractability。

**v0.6 update — 8 step-by-step actionable subsections below(closes § 8.13.4 100%):** Reader 可選 by-step linear 跑(以下 8 個 `### Step N` subsections)或 by-feature cross-jump(`## NL Invocation Parser` 等 mature sections)。 Backward compat 全保留,新 step subsections append-only。

### Step 1 — NL parse → 4-slot intent extraction

**Fires:** Immediately on receiving any `v7 ...` invocation。

**What to do:**

1. Identify 4 slots from user's natural language(per `## NL Invocation Parser` 4-Slot Intent Model):
   - **action** ∈ {review, audit, check, ship-gate, trend, …}  — default `review`
   - **target** — file path / REQ-ID / NL feature / project default
   - **verbosity** ∈ {brief, medium, full, verbose} — default `brief`
   - **focus_lens** ∈ {all, remaining_task, coverage_gaps, open_findings, blockers_only, trend_only} — default `all`
2. Compute confidence per slot via L2-L5 parsing chain(per spec § 8.7 + § 5.5)。
3. Default fill missing slots from `state.md` per-user defaults(per `## state.md Memory + Decay`)。

**Output of this step:** `parsed_intent = {action, target, verbosity, focus_lens, confidence_per_slot}` → feed to Step 2。

**Reference impl detail:** `## NL Invocation Parser` 完整 algorithm + L2-L5 parsing chain。

### Step 2 — Confidence threshold check + popup dispatch

**Fires:** After Step 1 yields `parsed_intent`。

**4-branch decision tree:**

| Condition | Action |
|:---|:---|
| All 4 slots confidence ≥ 0.9 | **skip popup,goto Step 3** |
| Exactly 1 slot in 0.7-0.9 | **single popup → user answer → goto Step 3** |
| ≥ 1 slot < 0.7 | **multi-popup**(per `## Popup Disambiguation Contract` 5 mandatory conditions)→ user answer → goto Step 3 |
| All slots unparseable | **reject + suggest `v7 ?`**(per `## Help / Discovery`)→ EXIT silent |
| Detected non-SCR intent(eg.「v7 寫 component」)| **reject + redirect**(per `## Negative Scope Reject` 7 categories)→ EXIT `rejected_negative_scope` audit log |

**Popup conditions(5 mandatory per § 8.7.1):**
1. PM 語言(無 jargon)
2. 附成本(每 option 標 ~time / ~tokens)
3. 預設選(highlighted option)
4. ⓧ escape option always present(silent — no audit log)
5. Echo user's original input back

**Reference impl detail:** `## Popup Disambiguation Contract` 完整 contract + decision tree。

### Step 3 — Echo final parsed intent banner

**Fires:** After Step 2 resolves intent(skip popup OR popup-confirmed)。

**Template(1 line markdown blockquote):**

```markdown
> 🎯 OK 我會跑:<target> / <verbosity> / <focus_lens>
```

**Example:**

```markdown
> 🎯 OK 我會跑:V7 SCR project 自我 review Round 3 / 簡要版 / 全 lens
```

**Purpose:** Last-chance visual confirm before paid work begins。 Reader can hit Ctrl-C before Step 4 cost preview if banner mismatched their intent。

### Step 4 — Cost + Time Preview emission

**Fires:** Immediately after Step 3 banner。

**5-field template:**

```markdown
> 🎯 OK 我會跑:<target> / <verbosity> / <focus_lens>
> ⏱ 預估 ~<N> 分鐘 / 輸出 ~<M> 行
> 💰 預估 ~<K> tokens
> ⚠ 跑到一半可隨時 Ctrl-C 中斷,partial output 自動清理(per Escape Route)
```

**Per-tier calibration(per `### Cost + Time Preview` per-tier table):**

| Tier | Time | Output LOC | Tokens |
|:---|:---|:---|:---|
| light(< 50 LOC code)| 10-30 sec | 50-100 LOC | 0-1k |
| medium(50-300 LOC)| 30 sec - 2 min | 100-300 LOC | 1-3k |
| heavy(> 300 LOC)| 2-5 min | 300-600 LOC | 3-8k |
| force-full(全 project)| 5-15 min | 600-1500 LOC | 8-20k |

**Reference impl detail:** `### Cost + Time Preview` per-tier calibration + actual_cost SSOT delineation。

### Step 5 — Heavy-tier gate 2-stage confirm

**Fires:** Conditionally after Step 4 — only if preview ≥ heavy tier(> 5 min OR > 10k tokens OR > 1000 LOC output)。

**Confirmation prompt:**

```
⚠ 此 review 規模較大(預估 8 分鐘 / 12k tokens / ~900 行)
要繼續嗎? [y] / [n] / [改成簡要版]
```

**3-branch decision tree:**

| User input | Action |
|:---|:---|
| `[y]` | **goto Step 6** |
| `[n]` | **cancel** → audit log `cancelled_preview` → EXIT |
| `[改成簡要版]` | `verbosity = brief` → recompute Step 4 preview → goto Step 6 |

**Reference impl detail:** `### Cost + Time Preview` 2-stage confirm pattern。

### Step 6 — Run R0-R6 + atomic tmp write

**Fires:** After Step 5 confirms continuation OR if preview ≤ heavy(skip Step 5)。

**Workflow:**

1. **Create atomic tmp file** per `### Atomic Write Pattern`:
   - `<output_dir>/.scr-tmp-<timestamp>-<rand-6>.{json,md}`
   - PID-bound cleanup registered(SIGTERM / Ctrl-C handler)
2. **Run R0 → R1 → R2 → R3 → R4 → R5 → R6** sequentially per `## What to Check` 7 reviewer architecture:
   - R0 fail → abort all subsequent reviewers + emit「fix spec layers first」
   - R5 memory rule violation = 0 hard gate(per § 6.3)
   - **v0.5 wired:** R1/R2/R3/R4 use `## Adapter Auto-Dispatch During Review` for L3 AST precision(cost-tier-gated)
3. **Ctrl-C handler:** During run,if user Ctrl-C → atomic cleanup tmp + audit log `cancelled_mid_run`。

**Reference impl detail:** `## What to Check — 7 Reviewer Architecture` + `### Atomic Write Pattern` + `## Adapter Auto-Dispatch During Review`。

### Step 7 — Write audit log entry

**Fires:** After Step 6 completes(success OR caught cancellation)。

**4-state status enum(write to `metrics.json.nl_intent_resolution`):**

| Status | When written |
|:---:|:---|
| `completed` | Step 8 happy-path completion |
| `cancelled_preview` | Step 5 user `[n]` |
| `cancelled_mid_run` | Step 6 Ctrl-C caught |
| `rejected_negative_scope` | Step 2 negative scope reject path |

**Silent — no audit log entry(per § 8.11 L1 Option A + § 8.7 popup contract row 4):**
- Popup ⓧ escape(Step 2)
- All unparseable + help suggested(Step 2 → § 8.8)

**Schema pin:** `format_version: scr-rev-0.2.6-nl-v1`(per `### metrics.json Schema`)。

**Reference impl detail:** `### metrics.json Schema` 完整 audit log schema。

### Step 8 — Cleanup tmp → final mv → emit output

**Fires:** After Step 7 audit log written(happy path only — cancelled paths exit at Step 5/6)。

**Workflow:**

1. **Atomic rename** per `### Atomic Write Pattern`:
   - `mv <output_dir>/.scr-tmp-<timestamp>-<rand-6>.json <output_dir>/<final>.json`
   - `mv <output_dir>/.scr-tmp-<timestamp>-<rand-6>.md <output_dir>/<final>.md`
2. **Unregister PID-bound cleanup handler** — no longer needed,tmp 已 promoted to final。
3. **Emit output to user** — print review markdown to terminal stdout OR open final file path if `verbosity=full`。
4. **Update `state.md`** — `v7_cost_calibration:` rolling N=20 actual_cost append(per `### Cost + Time Preview` SSOT delineation)。

**Reference impl detail:** `### Atomic Write Pattern` final mv idiom + `### state.md Companion Schema` rolling cost calibration。

### Lifecycle complete

After Step 8 emits output,V7 SCR invocation ends。 Reader can chain follow-up `v7 ...` invocations or escape to other V-modes per `docs/ai-principles.md` §3 Mode Map。

## Locate Target

### Code-side target(traditional file/dir/range)

User can specify target via:
- File path:`scripts/sanity_tc_pre_flight_check.py`
- Directory:`scripts/`(SCR scan all code-stack files)
- Commit range:`HEAD~3..HEAD`(diff-based scope)
- PR target:`origin/main..HEAD`(branch comparison)
- Default(no arg):current working directory + active project `docs/pm/<active>/spec/` SSOT

If multiple projects detected via `docs/pm/active-project.txt`,scope to active project default。

### REQ-ID + Natural Language target(rev 0.2.4 NEW per spec § 8.5)

**Form 2: Direct REQ-ID list** — auto fills `scr_scope`(equivalent to explicit declaration per § 8.4):

```bash
/spec-compliance-review --req REQ-019         # single
/spec-compliance-review --req REQ-019,REQ-024 # comma-separated multi-REQ
```

SCR scans全 codebase for files implementing declared REQs — output is **REQ-centric not file-centric**(對 PM 「我想看某 REQ 對齊狀況」 pattern)。

**Form 3: Natural language feature description** — NL → REQ-ID auto-mapping(對齊 § 8.7 NL Invocation Parser Target slot — single-slot REQ scope per SSOT delineation):

```bash
/spec-compliance-review --feature "OTP 登入流程"
v7 review TC JSON 24-field schema           # no 「」 quote per N2 convention
```

**NL → REQ-ID auto-mapping algorithm(per § 8.5):**

```
Step 1: L2 regex keyword match against REQ titles in spec
        → Extract candidate REQ-IDs

Step 2 (if L4 LLM available): semantic similarity ranking
        → Rerank by embedding cosine similarity

Step 3 (if L4 LLM available): top-3 candidates LLM Q&A confirm
        → 「Does this REQ implement <NL description>?」 yes/no per candidate

Step 4: Return matches with confidence ≥ 0.7
```

**Match scenarios:**

| Result | Behavior |
|:---|:---|
| 1 exact match(confidence ≥ 0.9)| Direct review of that REQ |
| Multiple matches(0.7-0.9)| Show候 list + ask user confirm |
| Ambiguous(no match ≥ 0.7)| Show top-5 candidates + ask user clarify |
| No match | Fall to file/dir target OR error 「請明示 REQ-ID 或精確 feature 描述」 |

**Form 4: Combined** — `--req` + `--feature` intersect(`--feature` refines `--req` scope)

### Target resolution priority

1. `--req REQ-XXX`(explicit)→ highest
2. `--feature "NL"`(auto-detect single-slot)→ medium
3. **NL Invocation Parser**(multi-slot full-invocation per § 8.7)→ medium-high(per parsed confidence)
4. File/dir target → lowest
5. Combined → intersection

## NL Invocation Parser(v0.3 NEW per spec § 8.7)

**Purpose:** Parse full-invocation natural language input(Form 1 of Trigger Convention)into 4 actionable slots — no flag memorization required。

### 4-Slot Intent Model

| Slot | 含義 | 範例 lexicon | Default |
|:---|:---|:---|:---|
| **Action** | 動作意圖 | 「review」/「看」/「check」/「audit」/「對齊檢查」 | review |
| **Target** | 對象 | file path / dir / project name / REQ-ID / NL feature description / `git diff HEAD~N` | (active project context)|
| **Verbosity** | 詳細度 | 「簡要」=brief / 「詳細版」=medium / 「全部資訊」=full | brief |
| **Focus Lens** ⭐ | 視角過濾(NEW)| 「還剩什麼」=remaining_task / 「比較進度」=trend_only / 「看哪些是 blocker」=blockers_only | all |

### Parsing Chain L2-L5(per spec § 8.7 + § 5.5 detection tier)

1. **L2 keyword match** — 對 4 slot 各自 lexicon dict scan
2. **L3 NL→REQ embedding** — for Target slot 之 feature description(reuse § 8.5 既有 algorithm — SSOT for single-slot REQ matching)
3. **L4 LLM Q&A confirm** — for ambiguous slots(confidence 0.7-0.9)
4. **L5 popup disambiguation** — fallback when confidence < threshold per `## Popup Disambiguation Contract`

**SSOT delineation(per spec § 8.7 Relationship to § 8.5):**
- **Single-slot NL → REQ matching** → goes through § 8.5(`--feature "..."` path,Locate Target above)
- **Multi-slot full-invocation NL parsing** → goes through this § 8.7 parser

### Confidence Threshold Matrix

| All slots confidence | Behavior |
|:---:|:---|
| ≥ 0.9 | Echo parsed intent inline(1 行)+ § 8.10 Cost Preview + run(no popup)|
| Any 1 slot 0.7-0.9 | Single-question popup + echo + run |
| ≥ 1 slot < 0.7 | **Multi-question popup**(per Popup Contract)+ wait for user pick |
| All unparseable | Reject + suggest `v7 ?`(per `## Help / Discovery`)|
| Non-SCR intent | Reject + redirect(per `## Negative Scope Reject`)|

### Example: parsing `v7 review sanity check 看還剩什麼`

```
Slot       | Value                     | Confidence
-----------|---------------------------|----------
action     | review                    | 0.95 (L2 keyword)
target     | sanity-check project      | 0.85 (L3 fuzzy — could be project OR file pattern)
verbosity  | brief (default)           | 1.00 (no NL signal — fallback default)
focus_lens | remaining_task            | 0.80 (L2 keyword 「還剩什麼」 → remaining_task)
```

→ target confidence 0.85 just below threshold 0.9 → single-question popup for target slot disambiguation。

## Popup Disambiguation Contract(v0.3 NEW per spec § 8.7.1)

**Purpose:** When NL parsing has ambiguity,ask user via popup using PM-friendly question format。

### 5 Mandatory Conditions per Popup Question

1. **用 PM 看得懂的話** — 避免「REQ-scoped fallback 3a」/「coverage AC-weighted」 等術語
2. **附「會幹什麼 / 多久」** — 讓 PM 判斷成本(對齊 § 8.10 Cost Preview)
3. **預設選最常見的** — pre-highlight default with ⭐
4. **必含 escape option** ⓧ「我打錯了,讓我重打」(per `## Escape Route`)
5. **跑前 echo final 解讀** — 1 行明示 SKILL 即將跑什麼

### Popup Implementation in Claude Code

Use `AskUserQuestion` tool(or equivalent in IDE)— max 4 questions per popup;若 ≥ 5 slot 需 disambiguate,先問 highest-confidence-gap 3-4 個,others 套 default 或下一輪 popup。

### Example Popup Template

```
🤔 您的指令我解讀有幾處不確定,請選擇:

Q1.「sanity check」指的是?
   ⓐ 整個 sanity-check 專案(12 個 script,3851 LOC)→ ~3 分鐘
   ⓑ 只看 pre-flight check 那個檔 → ~30 秒
   ⓒ 只看「測試 case 撰寫紀律」相關需求(REQ-019/024/025)→ ~1 分鐘
   ⓧ 我打錯了,讓我重打

Q2.「看還剩什麼」指?
   ⓐ「規格還沒做完」的部分(coverage gap)→ PM 視角
   ⓑ「之前 review 已 flag 但還沒修」的(deferred findings)→ 開發 backlog 視角
   ⓒ 兩個都看 ⭐ 預設
   ⓧ 我打錯了
```

## state.md Memory + Decay(v0.3 NEW per spec § 8.7.2)

**Purpose:** Remember per-user NL phrasing → resolved intent;避免 PM 對同樣 phrase 重複 popup。

### state.md Schema Addition

```yaml
# In docs/pm/<project>/state.md
v7_user_intent_history:
  - phrase: "sanity check"
    resolved_to: "sanity-check project (full scope)"
    confidence_after_3_uses: 0.95
    last_used: 2026-06-30
  - phrase: "看還剩什麼"
    resolved_to: "focus=remaining_task"
    confidence_after_2_uses: 0.85
    last_used: 2026-06-30
```

### Decay Rule

- 每次 user 接受同樣解讀 → confidence + 0.05,**reset `last_used = now`**
- 每月未用 → confidence - 0.1(per formula below)
- 達 confidence ≥ 0.9 → silent default(skip popup)
- 達 confidence < 0.5 → entry 從 state.md 移除

### Decay Formula (per spec § 8.7.2 N5 closure)

```
Reference clock: last_used (not first_seen)
decay_count = floor((now - last_used) / 30 days)
total: confidence -= decay_count × 0.1
```

「now」 採 system local time;跨 timezone project 採 UTC(state.md `v7_decay_clock_timezone:` field 可 override)。

## Cross-Reference Context

Read alongside the target:

1. Target's 3-layer spec(`docs/pm/<project>/spec/<*>-requirement-spec.md` + functional + design)— SCR ruler
2. `docs/pm/<project>/decision-log.md` — `D-scr-bypass-*` entries for retroactive backfill verification(per § 7.4)
3. `docs/pm/_org/org-decision-log.md` — org-level bypass cross-check
4. `docs/pm/<project>/state.md` `project_maturity` field — SG threshold pick(MVP / GA / mature)
5. Memory rules(grep `[[memory-name]]` from target file + spec)— § 2 invariant enforcement
6. Prior SCR run sidecar:`docs/reviews/*.scr-<target>.metrics.json` — trendline calc(per § 9.4.3 C4 closure)
7. **PM Skill context(if exists):**
   - `docs/pm/<project>/decision-log.md` — avoid re-litigating closed decisions
   - prior `docs/reviews/<date>-scr-<target>.md` — Round N+1 verify carryforward

## Mental Lens(批判思考 — 4 mental act,SCR-adapted)

對齊 spectra-review enhanced-v1 4 mental act,SCR contextualize for code-vs-spec compliance:

### Mental Act 1: Claim → Evidence → Verdict

對 spec 內每個 REQ-XXX / FUNC-XXX / DESIGN-XXX claim 主動提問:
- **Claim:** spec 寫了什麼 acceptance criterion?(eg. "REQ-005 Export PDF — output ≤ 5MB")
- **Evidence:** code 哪 file:line 真實 implement 此 AC?是 string match / docstring tag / runtime behavior?
- **Verdict:** 證據是否 binary 0/0.5/1?是否 multi-anchor 疊加(per § 5.4)?

### Mental Act 2: Cross-section consistency check

- Spec layer cross-check:REQ-XXX 之 functional flow 是否在 FUNC-YYY 對應?DESIGN-ZZZ component signature 是否一致?
- Code-side cross-check:同 function 多 REQ-tag,是否 multi-anchor 疊加 work?

### Mental Act 3: Anti-Bias Self-Check

每 finding 自問:
- 我是不是因為 code 寫得 「看起來 reasonable」 就放過了 spec drift?
- 反例:spec 沒寫的 code 我是否誤判 unspec'd?(free-pass anchor per § 5.4)
- 我是否 over-trust 「PASS lint = PASS review」 反 pattern?

### Mental Act 4: Understand-not-argue stance

- 不只說 「這 code drift」,要 propose 「scope declaration OR spec amendment」 二選一 fix
- 對 author 之 narrow scope decision 對齊 trust commitment invariant(per § 8.4)

## What to Check — 7 Reviewer Architecture

Per `scr-requirement-spec.md` § 4 execute R0-R6 sequentially per mode:

### R0 Spec Cross-Layer Consistency(mandatory pre-gate)

**Purpose:** SCR 自身先 verify spec 自身正確,才有 review code 的 ruler。

**Per-mode focus(per § 4.1):**

| Mode | Layer-mapping check | Semantic conflict check | Spec freshness | Heading levels |
|:---|:---|:---|:---|:---|
| R0-full | req↔func↔design 全 3 層 ID mapping | 3 層 cross-check semantic conflict | rev 落後對齊 issue date | ✅ H1/H2/H3 only |
| R0-medium | req↔func OR req↔design 2 層 | 2 層 cross-check | 同 above | ✅ H1/H2/H3 only |
| R0-lite | ID 唯一性(REQ-XXX 不重複) | AC sub-step internal self-consistency | rev metadata freshness | ✅ H1/H2/H3 only |

**Fail behavior:** R0 fail → SCR 全 abort + return「fix spec layers first」+ 標 spec drift bug。後續 R1-R6 不跑。

### R1 Traceability(fan-out host)

**Purpose:** 建立 spec ↔ code bi-directional map。

**Detection method per Tier 2.1(§ 5.5):**

- **Default tier L3:** AST + naming(Python `ast` / per-stack adapter § 4.10)— **v0.5 wired** via `## Adapter Auto-Dispatch During Review`(adapter.extract_req_tags + extract_entry_points)
- **Light tier L2:** Regex + word boundary grep(fallback when adapter unavailable)
- **Heavy tier L4:** LLM Q&A confirm for ambiguous cases

**Output schema(per § 4.2):**

```yaml
traceability:
  spec_to_code:
    REQ-005: [src/api/export.py:42, templates/export-pdf.html:18]
    REQ-099: []   # missing impl
  code_to_spec:
    src/api/export.py:42: [REQ-005, FUNC-012, DESIGN-007]
    src/api/payment.py:88: []   # unspec'd
```

### R2 Requirement Coverage

**Purpose:** 量化 req spec → code 對齊度,scope-aware(per § 8.4)。

**Coverage methodology(per § 5):**

- Base unit:acceptance criteria(non REQ 數)
- 3-tier partial impl scoring:0(無 code reference)/ 0.5(partial sub-step)/ 1(complete impl + test)
- Scoped coverage(SG gate base):`Σ in-scope AC score / Σ in-scope AC total`
- Full-spec coverage(parallel reference,not SG gate)
- **v0.5 wired** — code-side entry-point count via `adapter.extract_entry_points()`(per `## Adapter Auto-Dispatch During Review`),L2 regex fallback when adapter unavailable

### R3 Functional Compliance

**Purpose:** Verify code flow 對齊 functional spec step ordering。

**Detection focus:**

- AST-parse code,追 call chain per FUNC-XXX flow step list — **v0.5 wired** via `adapter.parse_source() + extract_entry_points()`(per `## Adapter Auto-Dispatch During Review`)
- 抓 missing step / extra step / out-of-order step
- L4 LLM Q&A for semantic flow understanding

### R4 Design Compliance

**Purpose:** Verify code structure 對齊 design spec component / signature。

**Detection focus:**

- Per-stack adapter `signature_compare()`(per § 4.10):code_sig vs spec_sig — **v0.5 wired** as primary detection per `## Adapter Auto-Dispatch During Review`
- Drift type:missing_param / extra_param / type_mismatch / return_type_drift(+ stack-specific:missing_column SQL / extra_id HTML / cross_ref_broken Markdown ⭐)

### R5 Architecture Compliance

**Purpose:** Layer pattern + 17 memory rule invariant enforcement。

**§ 7.2 Memory rule invariant 17 條 enforcement check:**

| # | Memory rule | SCR check |
|:---:|:---|:---|
| 1 | `[[backend-change-rule]]` | Verify *.py change has propose-first artifact + PO authorize trail |
| 2 | `[[backend-schema-change-workflow]]` | Verify SSOTs plural(laundry + sanity)cascade compliance |
| 3 | `[[audit-patch-cascade-verify]]` 5-dim | Verify (a) cross-file (b) intra-file (c) commit-time (d) Round N+1 (e) external state — all 5/5 |
| 4 | `[[public-vs-private-friend-data]]` | PII boundary not crossed in new friend data fields |
| 5 | `[[friend-fetch-cost]]` | Anti-pattern bulk fetch(`last_days`)not present |
| 6 | `[[delete-dialog-no-undo-hint]]` | 刪除 dialog 文案禁含「隱藏 / 可還原 / 軟刪」 |
| 7 | `[[dep-management]]` | requirements.txt unauthorized add not present;Azure Linux 3.0 compat |
| 8 | `[[v3-default-ui-mainline]]` | V2 UI new feature not present(frozen) |
| 9 | `[[profile-bizcard-invariant]]` | profile 必伴 main_bizcard,首張 = 預設 |
| 10 | `[[sender-discard-silent]]` | discard 行為 silent — no label/banner/hint to receiver |
| 11 | `[[receiver-edit-invariant]]` | RBT update path 無 sender side guard |
| 12 | `[[sanity-check-bug-fix-direct-main-rule]]` | direct-to-main bug fix:same session + `fix:` prefix + non-architectural |
| 13 | `[[profile-json-ssot]]` | V3 identity invariant 讀 profile JSON 不讀 BCT cards array |
| 14 | `[[human-first-docs]]` | New spec / proposal 含 PM/QA/Developer 3-role perspective |
| 15 | `[[backend-lint-workflow]]` | ruff F821/F baseline 不增 |
| 16 | `[[v3-backend-contract-source-rule]]` | V3 cmd/response 形狀 嚴格依 V2 UI 實作 |
| 17 | `[[v1-ui-retired]]` | V1 LIFF page 新功能 dev not present |

**Always-zero gate per § 6.3:** Memory rule violation = 0 容忍 regardless of maturity tier。

### R6 Coding Standard

**Purpose:** Lint baseline + UX pattern + naming convention。

**Reuse existing tooling:**

- `[[backend-lint-workflow]]` — `bash lint.sh`(ruff F821/F)
- mypy attr typo catch
- UX pattern check(`[[delete-dialog-no-undo-hint]]` 文案)

**Cost:** lowest tier — direct invoke existing lint chain;no SCR-specific LLM call。

## Finding Schema — 4-Tier + SG Verdict

每 finding 包含(對齊 spectra enhanced-v1 schema):

```yaml
finding:
  tier: 🔴 BLOCKER | 🟡 CONCERN | 🟢 NIT | ✅ STRENGTH
  id: V-001  # 流水 ID per round
  
  # 📛 命名(Identify)
  name: "簡潔標題"  # eg. "REQ-019 frontmatter 8 required fields under-checked"
  
  # 📣 主張(Assert)
  assertion:
    why_this_is_issue: "..."
    impact_level: 0-10
    probability: 0.0-1.0
    evidence:
      - "scr-spec § 4.2 line N"
      - "code file:line"
    
    cross_impact:
      affected_modules: [...]
      cascade_depth: 1-5
    
    phase_aware:
      current_phase: "Phase 4.5"
      if_not_fixed_now_breaks_at: "Phase 5 release note"
      estimated_rework_cost: low | medium | high
  
  # 🎯 追求(Pursue)
  pursuit: "具體 actionable fix (propose-first per [[backend-change-rule]] if *.py)"
  
  # 📊 Decision Tree(BLOCKER only)
  decision_tree:
    options:
      - { id: A, action: "do nothing", cost: <impact × probability>, notes: "..." }
      - { id: B, action: "fix now", cost: ..., notes: "..." }
      - { id: C, action: "defer rev N+1", cost: ..., notes: "..." }
    recommended_option: B
    counterfactual: "If do nothing, expected outcome: ..."
```

## SG Verdict — 4-State + PENDING Handling

Per `scr-requirement-spec.md` § 9.2 rev 0.2.2(C5 closure):

```markdown
## § 7. SG Gate Decision

**Project maturity:** <MVP | GA | mature>  ← from state.md `project_maturity`
**Spec scope declaration state:** <declared | auto-detected | undeclared force_full | undeclared PENDING>
**SG threshold applied:** ← per § 6.1 matrix column

| Dimension | Required | Actual | Status |
|:---|:---:|:---:|:---:|
| R0 Spec Cross-Layer Conflict | 0 | <X> | ✅ / 🔴 |
| R2 Req Coverage(scoped) | ≥<%> | <%> | ✅ / ⚠ / 🔴 |
| R3 Func Compliance | ≥<%> | <%> | ✅ / ⚠ / 🔴 |
| R4 Design Compliance | ≥<%> | <%> | ✅ / ⚠ / 🔴 |
| R5 Arch Violation | ≤<N> | <N> | ✅ / 🔴 |
| R5 Memory Rule Violation | 0 | <X> | ✅ / 🔴 |
| Unspec'd entry-point | ≤<N> | <N> | ✅ / ⚠ |
| Missing required code | 0 | <X> | ✅ / 🔴 |
| R6 Lint baseline 增 | ≤0 | <delta> | ✅ / 🔴 |

**SG Verdict:** ✅ PASS / ⚠ SOFT FAIL / 🔴 HARD FAIL / ⏸ PENDING(missing scr_scope declaration)
**Allowed Phase transition:** Phase 4.5 → Phase 5 ✅ / 🔴 blocked / ⏸ blocked-pending
**Bypass:** none / urgent-fix (reason: ...) / pending-scope (refer § 8.4)
```

**PENDING fallback per § 8.4:**

If `scr_scope` not declared(neither PR description YAML nor commit `scr-scope:` footer found):
1. 3a per-stack adapter `extract_req_tags()`(high confidence)
2. 3b raw `REQ-\d+(-[A-Z]+)?` regex grep(low confidence)
3. 3c union with warning「auto-detected scope from <3a/3b/both>」
4. 3d if union empty → **⏸ PENDING verdict**
   - SG verdict = PENDING(3rd informational state)
   - Phase 5 release note 前 commit author 必須補 declare(retroactive PR comment OR amend)
   - Refuse to declare → force_full + audit log entry

## Output Format — 3-Role(rev 0.2.4 NEW per spec § 9.5)

**Default output structure(per verbosity § 8.6 modulated):**

```
1. 🎯 TL;DR(1-3 sentence ship verdict — PM 最先看到)
2. 👔 PM Lens(per § 9.6 — full in default 簡要 mode)
   - 風險摘要 plain prose
   - 📋 規格 ↔ 實作對照表(coverage gap explicit per § 5.6)
   - 📈 趨勢比較(per § 9.6.2)
   - 🗓 Time-to-Ship Estimate(per § 9.6.3)
   - 🔁 Open vs Closed Findings(per § 9.6.4)
   - 🎯 Effort vs Value Matrix(per § 9.6.5)
3. 🔬 QA Lens(per § 9.7 — summary in 簡要,full in medium/full)
   - 測試對齊狀況
   - 測試 gap 明細(per missing/partial sub-AC)
   - 推薦測試重點
   - 品質信心度
4. 💻 Developer Lens(per § 9.8 — summary in 簡要,full in medium/full)
   - 具體 actionable fixes(file:line + command + 接受標準)
   - (full mode only)架構補完方向
5. Appendix(--full mode only)
   - § 1 Mental Lens 4 acts
   - § 2 R0-R6 per-reviewer findings
   - § 3 Top 10 findings + Effective Cost Matrix
   - § 4 Critical Hotspots
   - § 5 SG Gate Decision matrix(9 dimensions)
   - § 6 Verdict + Next Round Focus
```

**Plain language standards(per spec § 9.5 — anti-jargon rules):**

| Anti-pattern(old) | 新標準 |
|:---|:---|
| 「R0-R6 7-reviewer」 | 「7 個檢查維度」 |
| 「fallback (3b) low confidence」 | 「Scope 是自動推斷,信心度中等」 |
| 「memory rule invariant」 | 「治理規則」 |
| 「PASS WITH WARNINGS」 | 「✅ 可以 ship,有 N 個小提醒」 |
| 「coverage 78% AC-weighted」 | 「規格涵蓋率 78%(超過 MVP 標準 70%)」 |
| 「§ 1 Mental Lens」 | (omit in PM-facing OR rename「審查思路」 in appendix)|

**Visual indicators:** ✅ pass / ⚠ warning / 🔴 blocker / ⏸ pending / 🟢 low risk / 🟡 medium risk

### Focus Lens Output Filter(v0.3 NEW per spec § 8.7.3)

**Purpose:** Focus Lens slot(parsed by NL Invocation Parser)dynamically filters which sections of 3-Role output get shown vs collapsed。

**6-Mode Output Filter Matrix:**

| Focus Lens | Output 行為 |
|:---|:---|
| `all`(default)| 全 3-role lens 顯示(per default structure)|
| `remaining_task` | PM Lens 只列 partial + missing(complete 摺起來,1 行 summary)+ § 9.6.4 open findings 全顯 + § 9.6.3 Time-to-Ship 強調 |
| `coverage_gaps` | 只顯 § 5.6 coverage gap table + § 9.6.1 規格↔實作對照 |
| `open_findings` | 只顯 § 9.6.4 open vs closed + 4-tier findings(BLOCKER/CONCERN 段)|
| `blockers_only` | 只顯 4-tier BLOCKER + SG Gate verdict |
| `trend_only` | 只顯 § 9.6.2 趨勢 table + § 9.4.3 trendline |

**「摺起來不等於隱藏」:** complete 段一律以 1 行 summary 顯示(eg.「✅ 完整實作 6 個 REQ 已收摺,展開請加 `--full`」),讓 PM 知道有東西被收掉。

**Interaction with verbosity(per § 8.7.3 + § 8.6 — 2-dim filter resolution per C2 closure):**

1. **Focus Lens 先過濾** — 決定「哪些 section 顯示 / 摺起來」
2. **Verbosity 再裁切** — 在 顯 的 section 內決定「每段內容多詳細」
3. **衝突解** — eg. `focus_lens=trend_only` × `verbosity=full` → 只顯 trend section(per Focus Lens),但該 section 內展開 full detail(計算公式 + 範例)
4. **`focus_lens=all`** 等同沒 filter → 純套用 verbosity matrix
5. **`verbosity=brief` × `focus_lens=blockers_only`** narrow combination → 顯 1 section + brief summary(< 30 行,適合 super-quick ship-blocker scan)

### PM Lens 👔 Content(per § 9.6)

#### 📋 規格 ↔ 實作對照表(§ 9.6.1 Coverage Gap Explicit)

Per coverage gap detail from § 5.6,output 必含 4 sub-sections:

```markdown
#### ✅ 完整實作(<N> 個需求)
| 需求 ID | 內容 | 涵蓋深度 | 品質 |
|:---:|:---|:---|:---:|
| REQ-XXX | <title> | <N> 個檔案 — <distribution note> | 🟢 <%> |

#### 🟡 部分實作 — 需 PM 注意(<N> 個需求)
| 需求 ID | 內容 | ✅ 已做 | ❌ 缺什麼 | Ship 影響 |
|:---:|:---|:---|:---|:---:|
| REQ-XXX | <title> | <completed sub-AC list> | <missing sub-AC list> | 🟡/🟢 |

#### 🔴 完全未做(<N> 個需求)
| 需求 ID | 內容 | 全 sub-AC 缺 | Ship 影響 |

#### ⚪ 不在這次 scope(<N> 個需求 — 不算缺漏)
REQ-XXX, REQ-YYY, ... 屬於 <other layer scope>,SCR 自動排除。
```

#### 📈 趨勢比較(§ 9.6.2)

Grep prior `*.metrics.json` sidecars,compute Δ:

```markdown
| Metric | 上次 | 這次 | Δ | PM 解讀 |
|:---|:---:|:---:|:---:|:---|
| 涵蓋率(scoped) | X% | Y% | +/-Δ | <PM-friendly 1-line> |
```

#### 🗓 Time-to-Ship(§ 9.6.3)

```markdown
| Ship path | 內容 | 預估工時 | 累計 |
|:---|:---|:---:|:---:|
| ⚡ MVP 立即可 ship | <必補 list> | X min | X min |
| 🎯 GA-ready | + <推薦 polish list> | Y hr | X+Y |
| 🌟 Production-perfect | + <nice-to-have> | Z hr | X+Y+Z |
```

#### 🔁 Open vs Closed Findings(§ 9.6.4)

Grep prior SCR review markdowns,match by file:line + description fuzzy:

```markdown
| 來源 | 開出時間 | 狀態 | 備註 |
|:---|:---:|:---|:---|
| <prior-run> V-N | YYYY-MM-DD | ✅ closed / 🟡 deferred / 🔴 still open | <commit hash> |
```

🔥 Highlight: **「<finding> 連續 N 次 SCR flag → 不能再 defer」** when applicable。

#### 🎯 Effort vs Value Matrix(§ 9.6.5)

```
Value
  High │  <Q2: 低 effort, 高 value>  <Q1: 高 effort, 高 value> ← 🌟 do next
       │
   Low │  <Q3: 低 effort, 低 value>  <Q4: 高 effort, 低 value> ← 🟢 quick win / 🟡 defer
       │
       └──────────────────────────────
       Low                          High
                  Effort
```

**Top 3 高 ROI:** ranked by value/effort ratio。

### QA Lens 🔬 Content(per § 9.7)

#### 測試對齊狀況 / 測試 gap 明細

Per missing/partial sub-AC,output checklist:

```markdown
**REQ-Y sub-X — N 個 sub-test 缺:**
- [ ] Test: <specific test case description>
- [ ] Test: ...
```

#### 推薦測試重點 + 品質信心度

```markdown
**Top 3 推薦:**
1. <area> — <rationale>

**QA 品質信心:**
| Level | Now | After 補完 |
|:---|:---:|:---:|
| Unit test coverage | X% | Y% |
```

### Developer Lens 💻 Content(per § 9.8)

#### 具體 actionable fixes

```markdown
### 🟡 Fix N(<tier>,<effort>)
- 檔案:<file>:<line>
- 問題:<1-line>
- 命令:<exact command>
- 接受標準:<verification>
- 影響:<behavior impact>
```

## Persistence

Per `scr-requirement-spec.md` § 9.3 + N3 closure + rev 0.2.4 § 5.6 coverage_gaps + **rev 0.2.6 § 8.11 escape route + § 8.12 NL audit trail**:

**Markdown report:** `docs/reviews/<date>-scr-<target-slug>.md`(human-friendly,3-Role format default 簡要)

**Sidecar JSON:** `docs/reviews/<date>-scr-<target-slug>.metrics.json`(structured;trendline grep target per § 9.4.3 C4 closure)

### Atomic Write Pattern(v0.3 NEW per spec § 8.11)

Per **rev 0.2.6 § 8.11 N6 closure** — mid-run cleanup 必 atomic:

1. Write tmp filename:`<output_dir>/.scr-tmp-<timestamp>-<rand-6>.{json,md}`(timestamp + 6-char random 後綴)
2. 完成才 `mv .scr-tmp-*.json final.json` + `mv .scr-tmp-*.md final.md`
3. Ctrl-C signal handler 觸發 → 刪當前 SKILL invocation 之 tmp files(by PID match,**不刪他人 in-flight 的**)
4. Atomic guarantee — 看到 `final.json` 即代表完整 review

**Tmp location override:** read-only filesystem 可 override via state.md `v7_tmp_dir:` field。

### Escape Route — 3 Levels(v0.3 NEW per spec § 8.11)

| Level | Trigger | Behavior |
|:---|:---|:---|
| **L1 Popup ⓧ** | User picks ⓧ「我打錯了」 in popup | 0 partial run / 0 metrics.json / **0 audit log**(silent — per B1 Option A)/ suggest correction from state.md fuzzy match |
| **L2 Cost preview [n]** | User picks `[n]` at cost preview gate | Status `cancelled_preview` in audit log / 0 partial run |
| **L3 Mid-run Ctrl-C** | User aborts mid-run | Status `cancelled_mid_run` / atomic tmp cleanup / 短訊息「已取消,0 檔案異動」 |

對齊 `[[delete-dialog-no-undo-hint]]`:Escape 後真 0 file change,**不顯示**「已隱藏 / 可還原」 措辭(silent escape per PO 「打錯了」 原意)。

### metrics.json Schema(v0.3 — rev 0.2.6 cascade)

```yaml
# metrics.json schema (rev 0.2.6 + nl_intent_resolution)
---
spec_pins:
  requirement: { rev: X.Y.Z, hash: sha256:... }
  functional:  { rev: X.Y,   hash: sha256:... }
  design:      { rev: X.Y,   hash: sha256:... }
code_pin:      { branch: main, head: <commit>, diff_against: <baseline> }
nl_intent_resolution:                        # v0.3 NEW per § 8.12
  format_version: "scr-rev-0.2.6-nl-v1"      # schema versioning per N9 closure
  raw_phrase: "<user-typed NL>"
  parsed_slots:
    action:     { value: review, confidence: 0.95 }
    target:     { value: <resolved>, confidence: 0.85 }
    verbosity:  { value: brief, confidence: 1.0, source: default }
    focus_lens: { value: <resolved>, confidence: 0.80 }
  popup_questions_asked: <int>
  user_choices: { Q1: A, Q3: C, ... }
  resolution_final:
    target: <final resolved>
    verbosity: brief | medium | full
    focus_lens: <final resolved>
  resolution_confidence_final: 0.95
  user_overrode_default: <bool>
  memory_default_applied: <bool>
  memory_default_updated: <bool>
  status: completed | cancelled_preview | cancelled_mid_run | rejected_negative_scope   # 4 states per B1 closure
  actual_cost:
    duration_seconds: <int>
    output_loc: <int>
    tokens_estimate: <int>
invocation:                                  # rev 0.2.4 base
  forms_used: [file, req, feature, combined, nl]   # v0.3 加 'nl'
  verbosity: brief | medium | full
  focus_lens: all | remaining_task | coverage_gaps | open_findings | blockers_only | trend_only   # v0.3 NEW
  scope_source: declared | auto_detect | nl_mapping | force_full
metrics:
  R0_verdict: pass | fail
  R2_coverage_scoped_percent: <0-100>
  R2_coverage_full_percent: <0-100>
  R3_compliance_percent: <0-100>
  R4_compliance_percent: <0-100>
  R5_arch_violations: <count>
  R5_memory_rule_violations: <count>
  R6_lint_baseline_delta: <int>
coverage_gaps:                               # rev 0.2.4 § 5.6
  - req_id: REQ-XXX
    title: "<title>"
    status: complete | partial | missing
    score: 0.0-1.0
    completed_sub_ac: [...]
    missing_sub_ac: [...]
    impl_files: [...]
    ship_impact: low | medium | high
    pm_note: "<plain language interpretation>"
trend_baseline:                              # rev 0.2.4 § 9.6.2
  prior_run: <date>
  prior_metrics_path: docs/reviews/<...>.metrics.json
  deltas: { coverage_scoped_delta: +/-Δ, ... }
findings_history:                            # rev 0.2.4 § 9.6.4
  open_count: <int>
  closed_count: <int>
  deferred_recurring: [<finding-id list — 連續多次 flag>]
sg_verdict: PASS | SOFT_FAIL | HARD_FAIL | PENDING | PASS_WITH_WARNINGS
---
```

> **Note(B1 Option A 對齊 per § 8.11 + § 8.12):** Popup ⓧ escape(L1)**完全不寫 metrics.json**(silent escape);若需 phrase history 進 parser self-improvement,改用 state.md `v7_rejected_phrases:` debug list(per Negative Scope Reject section)。

### state.md Companion Schema(v0.3 NEW)

下列 fields 全 opt-in,default OFF;writes 由 SKILL invocation 自動 maintain:

```yaml
# In docs/pm/<project>/state.md
v7_user_intent_history: [...]      # per NL Memory + Decay section (§ 8.7.2)
v7_cost_calibration:               # per Cost Preview rolling N=20 (§ 8.10 C3)
  light: { recent_runs: [...], moving_avg_seconds: <float> }
  medium: {...}
  heavy: {...}
v7_rejected_phrases: [...]         # per Negative Scope Reject (§ 8.9)
v7_help_examples: [<NL>...]        # per Help / Discovery override (§ 8.8)
v7_decay_clock_timezone: UTC|local|<IANA>  # per § 8.7.2 N5
v7_tmp_dir: <path>                 # per § 8.11 N6 (read-only fs override)
v7_audit_opt_out: false            # per § 8.12 privacy
v7_popup_escape_log_to_debug: false # per § 8.11 B1 (opt-in escape phrase log)
```

**Decision log append:**

對齊 PM Skill `docs/pm/<project>/decision-log.md` design:若 PO 在 inline 對話中 close BLOCKER/CONCERN,SKILL 自動 append:

```markdown
- D-scr-<id>: <decision> | reason | impacted: [...] | source: <review file>
```

## Compliance Coverage Matrix — Dual View

Per § 9.4.4:

```markdown
## § 8. Compliance Coverage Matrix

### Scoped(SG gate base — REQ-XXX declared via § 8.4)
| Direction | Total | Found | Gap | Coverage |
|:---|:---:|:---:|:---:|:---:|
| Spec → Code | <N> AC | <X> impl + <Y> partial | <Z> missing | <%> |
| Code → Spec | <N> entry-point | <X> tagged | <Y> unspec'd | <%> |

### Full-spec(reference only — 不參與 SG gate)
| Direction | Total | Found | Gap | Coverage |
|:---|:---:|:---:|:---:|:---:|
| Spec → Code | <N> AC | <X> impl + <Y> partial | <Z> missing | <%> |
| Code → Spec | <N> entry-point | <X> tagged | <Y> unspec'd | <%> |
```

## Per-Stack Adapter Dispatch

Per § 4.10,detect target file extension + invoke matching adapter:

| Extension | Adapter | Reference | Status |
|:---|:---|:---|:---:|
| `*.py` | Python `ast` module(stdlib) | `scripts/scr_python_ast_adapter.py` | ✅ **Track 1 landed**(rev 0.2.6 / 2026-06-30)|
| `*.js` / `*.ts` | esprima(pure Python BSD-2 1 MB)| `scripts/scr_js_adapter.py` | ✅ **Track 4 landed**(rev 0.3.0 / 2026-06-30,esprima==4.0.1 dev-only)|
| `*.html` | beautifulsoup4 + html.parser stdlib backend(MIT 350 KB)| `scripts/scr_html_adapter.py` | ✅ **Track 5 landed**(rev 0.3.0 / 2026-06-30,beautifulsoup4==4.13.4 dev-only)|
| `*.sql` | sqlparse(pure Python BSD-3 120 KB) | `scripts/scr_sql_adapter.py` | ✅ **Track 6 landed**(rev 0.3.0 / 2026-06-30,sqlparse==0.5.3 dev-only)|
| `*.yaml` / `*.json` / `.md` frontmatter | stdlib json + sanity_tc_md_parser (manual YAML) | `scripts/scr_yaml_json_adapter.py` | ✅ **Track 7 landed**(rev 0.3.0 / 2026-06-30,0 pip)|
| `*.md`(body)| stdlib regex(headings + cross-refs + frontmatter)| `scripts/scr_markdown_adapter.py` | ✅ **Track 8 (F-cross-1) landed**(rev 0.3.0 / 2026-06-30,0 pip)— closes 6/6 adapter family ⭐⭐ |

### Python Adapter Track 1 details(2026-06-30 landed)

**Module:** `scripts/scr_python_ast_adapter.PythonAstAdapter`(~290 LOC,stdlib `ast` only,0 pip)

**4 API methods per ScrStackAdapter Protocol:**
- `parse_source(file_path) -> ast.Module`
- `extract_entry_points(tree, file_path) -> list[EntryPoint]`(5 kinds:flask_route / liff_handler / cli_subcommand / public_method / invariant_guard)
- `extract_req_tags(tree, file_path, source_text) -> list[ReqTag]`(2 sources:docstring + comment per OQ-3;attribute defer)
- `signature_compare(code_sig, spec_sig) -> list[Drift]`(4 kinds + Optional/Union normalize per OQ-4)

**Phase B opt-in usage:** `sanity_tc_schema_validator.py --audit-scripts --ast-mode`(Phase A regex still default per OQ-2 preserve backward compat)

**Fallback chain:** Adapter unavailable → 降級 L1 regex/string match + emit warning「stack <X> adapter unavailable,降級 L1 detection」 不 fail。

### Markdown F-cross-1 Adapter Track 8 details(2026-06-30 landed — closes 6/6)

**Module:** `scripts/scr_markdown_adapter.MarkdownAdapter`(~280 LOC,stdlib `re` only,0 pip)

**4 API methods per ScrStackAdapter Protocol:**
- `parse_source(file_path) -> MarkdownTree`(in-memory segment list — heading + code_block + cross_ref + frontmatter)
- `extract_entry_points(tree, file_path) -> list[EntryPoint]`(4 kinds:md_heading / md_code_block / md_cross_ref / md_frontmatter_key)
- `extract_req_tags(tree, file_path) -> list[ReqTag]`(3 sources:markdown_body / markdown_code_block / markdown_frontmatter)
- `signature_compare(code_sig, spec_sig) -> list[Drift]`(3 kinds:missing_heading / extra_heading / **cross_ref_broken** ⭐ F-cross-1 marquee)

**F-cross-1 detection:** `signature_compare` 之 `cross_ref_broken` drift kind 對 markdown 內 `[text](path#anchor)` link 進行 on-disk file existence check — external `http://` / `https://` / `mailto:` URLs 自動 skip。

**Integration tested:** Real V7 SCR spec parses successfully(`docs/pm/v7-spec-compliance-review/spec/scr-requirement-spec.md` 自我 application — SCR adapter can parse SCR spec)。

**Fallback chain:** Adapter exception → 降級 L1 regex pattern `\bREQ-\d+\b` global match(現 sanity_tc_schema_validator 用法)+ emit warning。

## Adapter Auto-Dispatch During Review(v0.5 NEW — closes OQ-6 per Track 1 propose-first)

**Purpose:** Wire 6/6 landed adapter family into R1/R2/R3/R4 reviewer workflow so V7 SCR auto-uses adapters instead of falling back to L2 regex when reviewing code targets。 Closes OQ-6 carry-forward from Track 1 propose-first(2026-06-30 PO authorize 「Y 全 4 OQ + Y go impl」)。

### When dispatch fires(cost-tier-gated per OQ-1)

| Cost-Staged Tier(per § 4.9) | Adapter dispatch behavior |
|:---|:---|
| **Light** (< 50 LOC code change) | MAY skip adapter — L1 regex 已夠 precision;Claude 自判 |
| **Medium** (50-300 LOC OR ≥ 1 REQ scope declared) | **Recommended** — use adapter for R1/R2/R3/R4 |
| **Heavy** (> 300 LOC OR architectural change OR memory rule touch) | **MUST** use adapter — L3 AST mandatory for precision |
| **Force-full** (`--full` OR `project_maturity=mature`) | **MUST** use adapter regardless |

### Which reviewers use adapters(per OQ-3)

| Reviewer | Adapter used | API methods called |
|:---:|:---|:---|
| R0 spec cross-layer | ❌ N/A | spec/string-level — adapter Protocol 不適用 |
| **R1 Traceability** | ✅ YES | `adapter.extract_req_tags(tree)` 取代 grep `REQ-XXX` |
| **R2 Req Coverage** | ✅ YES | `adapter.extract_entry_points(tree)` 計 code-side count |
| **R3 Functional Compliance** | ✅ YES | `adapter.extract_entry_points()` 比對 spec func step list |
| **R4 Design Compliance** | ✅ YES | `adapter.signature_compare(code_sig, spec_sig)` 抓 drift |
| R5 Architecture / memory | ❌ N/A | string-pattern + memory rule check — adapter 不適用 |
| R6 Coding Standard | ❌ N/A | reuse `bash lint.sh` — adapter 不適用 |

### Dispatch trigger logic(per-target-file workflow)

For each target file in scope of R1/R2/R3/R4 review:

```
1. Detect file extension → ext
2. Look up adapter in "## Per-Stack Adapter Dispatch" table by ext
3. If matching adapter ✅ landed:
     try:
       from scripts.scr_<X>_adapter import <X>Adapter
       adapter = <X>Adapter()
       tree = adapter.parse_source(file_path)
       eps  = adapter.extract_entry_points(tree, file_path=file_path)
       tags = adapter.extract_req_tags(tree, file_path=file_path)
       # Feed eps + tags into R1/R2/R3 result aggregation
     except (ImportError, Exception) as err:
       emit_warning(f"stack {ext} adapter unavailable: {err}, 降級 L2 regex")
       audit_log['detection_tier_actual'] = 'L2_fallback'
       run_l2_regex_fallback(file_path)
4. If adapter ⏸ not landed OR ext unknown:
     audit_log['detection_tier_actual'] = 'L2_default'
     run_l2_regex_fallback(file_path)
```

### Adapter dispatch reference table(canonical extensions)

| Extension | Import statement | Track |
|:---|:---|:---:|
| `*.py` | `from scripts.scr_python_ast_adapter import PythonAstAdapter` | Track 1 |
| `*.yaml` / `*.json` | `from scripts.scr_yaml_json_adapter import YamlJsonAdapter` | Track 7 |
| `*.sql` | `from scripts.scr_sql_adapter import SqlAdapter` | Track 6 |
| `*.js` / `*.ts` | `from scripts.scr_js_adapter import JsAdapter` | Track 4 |
| `*.html` | `from scripts.scr_html_adapter import HtmlAdapter` | Track 5 |
| `*.md` | `from scripts.scr_markdown_adapter import MarkdownAdapter` | Track 8 |

### Fallback semantics(per OQ-2 — graceful + audit)

When adapter import / parse / extract raises exception:

1. **Catch silently** — adapter exception does NOT abort R1/R2/R3/R4 review
2. **Emit user-visible warning** — `"stack <X> adapter unavailable, 降級 L2 regex detection"` 一行印出 SCR review output 開頭
3. **Audit log records actual tier** — `metrics.json.detection_tier_actual = "L2_fallback"`(separate from `detection_tier_declared` which captures user intent)
4. **Continue review** — fall back to L2 regex per existing `\bREQ-\d+\b` + heuristic name match
5. **Trendline visibility** — fallback rate visible in `metrics.json.adapter_fallback_count` per project,trigger condition for future OQ-6 polish round

### Example adapter call(Python target — R3 Functional Compliance)

```python
# Inside R3 functional compliance flow:
try:
    from scripts.scr_python_ast_adapter import PythonAstAdapter
    adapter = PythonAstAdapter()
    tree = adapter.parse_source('scripts/sanity_tc_pre_flight_check.py')
    entry_points = adapter.extract_entry_points(
        tree, file_path='scripts/sanity_tc_pre_flight_check.py',
    )
    # entry_points = [
    #   {name:'main', kind:'cli_subcommand', location:{...}},
    #   {name:'_load_tcs', kind:'public_method', location:{...}},
    #   ...
    # ]
    # Compare against spec FUNC-XXX step list
    drifts = compare_func_step_order(entry_points, spec_func_steps)
except (ImportError, Exception) as err:
    emit_warning(f"Python adapter unavailable: {err}, 降級 L2 regex")
    # Fall back to existing L2 regex pattern matching
```

### Status

⏸ → ✅ **CLOSED 2026-06-30** via SKILL v0.5 cascade per PO Option A 「Y 全 4 OQ + Y go impl」 directive(closes 4/4 Round 1 meta self-review carry-forward = 100% closure rate)。 6/6 adapter family 從「shop window 陳列」升級為「主流程 active dispatch」,V7 SCR review 默認走 L3 AST(per cost-tier-gated trigger),L2 regex 降為 fallback。

## Cross-SKILL Integration

SCR is one of Phase 4.5 multi-tool stack per orchestrator rev 0.1.3 § 6:

```
Phase 4.5 Impl-Review(cost-staged per SCR § 4.9):
  4.5a spectra-review enhanced-v1  → spec internal quality / drift
  4.5b SCR(本 SKILL,V7 mode)       → code ↔ spec compliance
  4.5c lint reuse [[backend-lint-workflow]]
  4.5d pytest unit + light integration
  4.5e smoke test single happy-path runtime sanity

Phase 4.5 → Phase 5 gating(per orchestrator § 6):
  ALL 5 pass → Phase 5 ✅
  4.5b SCR PENDING → ⏸ blocked-pending(declare-or-decline)
  4.5b SCR HARD FAIL → 🔴 return to Phase 4 code revision
```

SCR 不 replace spectra — 兩者並列(spectra reviews spec text quality,SCR reviews code-vs-spec compliance)。

## Help / Discovery —「v7 ?」(v0.3 NEW per spec § 8.8)

**Purpose:** Plain-prose discovery card — new PM 第一次來,不需讀 docs 即可 self-discover SKILL 能幹什麼。

### Trigger Forms

```bash
v7 ?
v7 help
v7 你能做什麼
v7 怎麼用
/spec-compliance-review --help     # Form 3 advanced equivalent
```

### Discovery Card Output(plain-prose,no flag list per § 8.8 anti-pattern)

```markdown
👋 V7 SCR 是「規格對齊檢查」工具 — 確認 code 真的有按 spec 做。

你可以這樣問(不需記 flag,自然語言即可):

📋 看現況
- 「v7 review sanity check 看還剩什麼」
- 「v7 看 namecard v3 哪些 REQ 沒做完」

🚦 ship 前 check
- 「v7 ship 前 check 一下這個 PR」
- 「v7 看這次 commit 有沒有破規」

📈 比較進度
- 「v7 比較這次跟上次的差距」
- 「v7 看上週到現在改了什麼」

🎯 聚焦特定 feature
- 「v7 OTP 流程做完了嗎」
- 「v7 review REQ-019 schema validation」

📊 想看詳細
- 「v7 review sanity check 全部資訊」(switch to full mode)
- 「v7 看哪些是 blocker」(只看 blockers_only)

💡 不確定要看什麼? 直接打「v7 看一下」 — 會問你想看什麼。
```

### Anti-Pattern Rules

- ❌ 列 `--brief / --full / --req` 等 flag(對 PM 是噪音)
- ❌ 秀 SG Gate / R0-R6 等技術術語(藏在 Appendix)
- ❌ 列完整 capability matrix(只列高頻 4-5 群 use case,各 1-2 NL example,total 8-10 phrasings — N3 alignment)

### Discovery Card Source Priority

1. Per-project `state.md` `v7_help_examples:` field(if defined)
2. High-frequency phrases from `metrics.json` `nl_intent_resolution.raw_phrase` aggregate(if 90+ day history)
3. Fallback: hardcoded 8-10 examples above

## Negative Scope Reject(v0.3 NEW per spec § 8.9)

**Purpose:** Reject non-SCR intent + redirect to correct tool;防 silent hallucination 誤觸發。

### 7 Reject Categories

| Category | 範例 phrase | Reject + Redirect |
|:---|:---|:---|
| Code generation | 「v7 幫我寫 component / function」 | 「V7 只做 spec 對齊 review,寫程式請改用一般 Claude Code prompt」 |
| Bug fix | 「v7 修這個 bug」 | 「V7 不修 code,只 report 違規。 修 bug 請直接描述問題 + 檔案 path」 |
| Code refactor | 「v7 重構這段」 | 「V7 不修 code。 重構請走 Phase 4 orchestrator refactor 流程」 |
| Spec writing | 「v7 幫我寫 spec」 | 「V7 review spec compliance,不寫 spec。 寫 spec 請用 PM Skill `propose` workflow」 |
| Test execution | 「v7 跑測試」 | 「V7 不執行測試,只看 code-spec 對齊。 跑測試請用 `pytest` 或 PM Skill `sanity-tc-runner`」 |
| Deploy / git ops | 「v7 deploy」/「v7 commit」 | 「V7 不操作 git / deploy。 ship 前 check 請改問「v7 ship 前 check 這個 PR」」 |
| Pure chitchat | 「v7 你好」/「v7 怎樣?」 | 「我是 V7 SCR(規格對齊 reviewer)。 試試 `v7 ?` 看可以怎麼用」 |

### Reject Response Template

```markdown
🚫 您要的不是 V7 SCR 的職責。

我理解您想做:**<paraphrase user intent>**

但 V7 SCR 只做「規格 vs code 對齊 review」 — 不會:
- 寫 / 改 code
- 跑測試
- 做 git / deploy 操作

**建議改用:**
- <對應正確的工具/流程,per table above>

若您原意是想「review <某 spec area>」,可以試問:
- 「v7 review <relevant area>」
```

### Implementation Notes

- **L4 LLM intent classifier 必含 negative training set**(non-SCR phrasings)
- 不確定時(confidence ambiguous SCR vs non-SCR)走 popup,**不要默默硬跑**
- Reject **不寫** metrics.json(B1 Option A 對齊 — 對齊 silent escape 語意)
- Reject phrase 進 `state.md` `v7_rejected_phrases:` debug list(opt-in per state.md `v7_audit_opt_out`)— 供 future negative training set 累積

## Subcommand: help

If invocation 無 specific target OR user typed `/spec-compliance-review help`:

```markdown
SCR — Specification Compliance Reviewer (V7 mode, rev 0.2.6 NL-first format)

📋 Recommended invocation: Natural Language (per § 8.7)
  v7 review sanity check 看還剩什麼              # multi-slot NL
  v7 看 OTP 流程做完沒                           # feature description
  v7 ship 前 check 這個 PR                       # PR scope
  v7 比較這次跟上次                              # trend mode
  v7 ?  OR  v7 help                              # discovery card (per § 8.8)

⚙ Form 3 — Flag-based (advanced backward compat,per § 8.5/8.6):

Target forms:
  /spec-compliance-review <target>           File/dir/range target
  /spec-compliance-review --req REQ-XXX      Direct REQ-ID (single or comma-separated)
  /spec-compliance-review --feature "<NL>"   Natural language → REQ-ID auto-map (single-slot)
  /spec-compliance-review --req REQ-XXX --feature "..."   Combined intersection

Verbosity:
  --brief    (default) PM-friendly ~80-150 LOC, 3-role, no Appendix
  --medium   QA test planning, +full QA sub-AC detail
  --full     Audit + dev debugging, +Appendix (R0-R6 / SG matrix / Mental Lens)
  --verbose  alias for --full

Other flags:
  --tier=heavy             Override cost-staged tier
  --no-architectural-change Override arch detection
  --bypass=<reason>        Emergency PO override

🎯 Outputs (per § 9.5 / § 5.6 / § 8.12):
  - docs/reviews/<date>-scr-<target-slug>.md
    (human-friendly markdown: TL;DR + 👔 PM Lens + 🔬 QA Lens + 💻 Dev Lens + Appendix*)
  - docs/reviews/<date>-scr-<target-slug>.metrics.json
    (structured: spec_pins + nl_intent_resolution + invocation + metrics +
     coverage_gaps + trend_baseline + findings_history + sg_verdict)
  * Appendix only in --full mode

📊 Verdict (per § 9.2):
  ✅ PASS / ⚠ SOFT FAIL / 🔴 HARD FAIL / ⏸ PENDING (missing scr_scope)

🚫 Negative scope rejected (per § 8.9):
  「v7 寫 / 修 / 重構 / 跑測試 / deploy / commit」 etc. → see § Negative Scope Reject

Spec reference:
  docs/pm/v7-spec-compliance-review/spec/scr-requirement-spec.md (rev 0.2.6)
```

## Tone

Critical but constructive. Bias toward finding issues. If genuinely 「(none found)」 in a tier, write so explicitly。

**Understand-not-argue stance:** 不只 reject,要 propose 替代方案 + 對齊 PO 原意 + 對齊 trust commitment invariant per § 8.4。

## Out of Scope

- Do NOT auto-apply fix — only report(對齊 `[[backend-change-rule]]` propose-first)
- Do NOT edit target files unless user explicitly asks afterwards
- Do NOT run `git` destructive commands
- Do NOT call orchestrator other Phase 4.5 sub-tools(4.5a/c/d/e)— orchestrator host responsibility,not SCR
- Do NOT modify spec itself(reviews against spec,not for spec)
- Do NOT bypass 17 memory rule invariants(§ 6.3 always-zero gate)
- **Do NOT accept 7 negative-scope intent categories**(per § 8.9 — code-gen / bug-fix / refactor / spec-write / test-exec / deploy-git / chitchat)→ explicit reject + redirect per `## Negative Scope Reject` section
- **Do NOT silent hallucinate run** when NL parsing 不確定 — 走 popup disambiguation per § 8.7 multi-question popup,不默默硬跑

## Cross-Project Portability

Per Stage 5b PoC evidence(commit 9c5570c,2026-06-29):

- ✅ orchestrator proposal vs spec — R0-lite mode + PENDING verdict path verified
- ✅ pm-skill SKILL.md vs spec — multi-stack adapter readiness + GA maturity threshold verified
- Cross-project SCR works without modification — target argument 對齊 active project context

## Compliance Contract — Specification Gate

對齊 user-facing covenant per `scr-requirement-spec.md` § 7:

> 「Code 過 lint」 ≠ 「Code 過 review」。
> SG(Specification Gate)= Code ↔ Spec compliance ship-readiness verdict。
> 落地後每 PR 必過 SG → Phase 5 release note 才允許。

---

## Version

- **0.3**(2026-06-30 — implementing SCR rev 0.2.6)— NL UX cascade per PO 「no one be able to remember the detail commands ... support nature language input」 + 「popup and ask user」 directives:
  - Trigger Convention 重組為 **NL-first 3 forms**(NL / Discovery / Flag-based)
  - § 8.7 NEW **NL Invocation Parser** — 4-slot intent model(action / target / verbosity / focus_lens NEW)+ L2-L5 parsing chain + confidence threshold matrix
  - § 8.7.1 NEW **Popup Disambiguation Contract** — 5 PM-friendly conditions + AskUserQuestion tool 整合 + example template
  - § 8.7.2 NEW **state.md Memory + Decay** — `v7_user_intent_history:` schema + `floor((now - last_used) / 30 days) × 0.1` formula + timezone override
  - § 8.7.3 NEW **Focus Lens Output Filter** — 6 mode matrix + 2-dim interaction with verbosity per § 8.6
  - § 8.10 NEW **Cost + Time Preview** — 5-field template + heavy-tier 2-stage confirm + per-tier calibration + actual cost feedback to state.md `v7_cost_calibration:`
  - § 8.11 NEW **Atomic Write Pattern + Escape Route** — `<output_dir>/.scr-tmp-<ts>-<rand-6>` random suffix + PID-bound cleanup + 3-level escape(popup ⓧ silent / cost preview [n] / Ctrl-C)
  - § 8.12 NEW **NL Intent Resolution Audit Trail** — metrics.json `nl_intent_resolution` sub-section + `format_version: "scr-rev-0.2.6-nl-v1"` + 4-state status enum(`completed` / `cancelled_preview` / `cancelled_mid_run` / `rejected_negative_scope`)
  - NEW **Help / Discovery `v7 ?`** section — plain-prose card 8-10 NL examples + anti-pattern rules(無 flag list)
  - NEW **Negative Scope Reject** section — 7 categories table + reject template + ambiguous → popup
  - state.md companion schema 8 new opt-in fields(全 default OFF per D-007 maturity-aware)
  - Subcommand help 重寫 — NL-first 範例 + Form 3 flag list as advanced backward compat
  - Out of Scope 加 7 negative-scope categories + 「不 silent hallucinate run」 explicit invariant
- **0.2**(2026-06-30 — implementing SCR rev 0.2.4)— Real-try output redesign per PO 4 directives(3-role + coverage gap + REQ-NL targeting + verbosity)
- **0.1**(2026-06-30 Track 2 初版落地)— Initial SKILL.md draft per SCR rev 0.2.3 spec;7 reviewer architecture + SG 4-state verdict + cost-staged tier + per-stack adapter dispatch + memory rule enforcement 全 codified。

## Related References

- Spec: `docs/pm/v7-spec-compliance-review/spec/scr-requirement-spec.md`(rev 0.2.6)
- Decision log: `docs/pm/v7-spec-compliance-review/decision-log.md`(D-001 ~ D-067)
- README: `docs/pm/v7-spec-compliance-review/README.md`
- Proposals: `docs/pm/v7-spec-compliance-review/proposals/`
  - `track-2-skill-md-v0-3-nl-ux-cascade.md` — v0.3 cascade propose-first artifact
- Gap Audit + Task Plan: `docs/pm/v7-spec-compliance-review/V7_SCR_GAP_AUDIT_AND_TASK_PLAN.md`
- Reviews:
  - `docs/reviews/2026-06-29-scr-poc-*` + `2026-06-29-spectra-scr-*`(early SCR proposal lifecycle)
  - `docs/reviews/2026-06-30-scr-sanity-tc-scripts-coverage.md`(first PROD V7 invocation,v0.1 format)
  - `docs/reviews/2026-06-30-scr-sanity-tc-scripts-coverage-PROOF-v0.2.4.md`(3-role PROOF example,v0.2.4 format)
  - `docs/reviews/2026-06-30-spectra-scr-proposal-rev-0.2.5.md`(Round 1 review on rev 0.2.5 — verdict ⚠ fix-blockers)
  - `docs/reviews/2026-06-30-spectra-scr-proposal-rev-0.2.6.md`(Round 2 review on rev 0.2.6 — verdict ✅ ship-as-is)
