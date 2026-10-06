---
name: pm-skill
description: AI Project Assistant orchestrating 8-stage SDLC. Triggered by `/pm <subcommand>` slash command (dispatched via .claude/commands/pm.md) or by plain-text patterns like "pm <subcommand>" / "pm help" / "pm init" in user message. Examples: "pm help", "pm init my-project", "pm daily". Full command list in Subcommand Router below. Composes spectra-review + V0-V8 sub-skills.
---

# PM Skill — AI Project Assistant

Use this skill when the user types any `/pm <subcommand>` or `/pm-bug-review`.

This skill orchestrates the full 8-stage SDLC (Phase 0 Kick-off → Phase 7 Post-launch) per the design documented in [`docs/pm/pm-skill/spec/pm-skill-proposal.md`](docs/pm/pm-skill/spec/pm-skill-proposal.md) (**rev 1.16** §6.4 Skill Composition Contract + Artifact Contracts + v1.2 Multi-Dev Workflow Commands + §6.4.14 Team Composition + §6.4.15 SKILL Workflow Lifecycle + §6.4.16 SDLC v2 + §6.4.17 Mid-Phase REQ Change Governance) and the usage scenarios in [`docs/pm/pm-skill/docs/pm-skill-user-manual.md`](docs/pm/pm-skill/docs/pm-skill-user-manual.md) (rev 1.8, 18 scenarios + appendices).

## Multi-IDE Bootstrap

| Tool | Loading Mode | User Action Required |
|---|---|---|
| **Claude Code** | Native skill load | No action — `/pm <subcommand>` triggers this skill |
| **Antigravity** | Repo-aware auto read | Usually auto; explicit `/pm` mention boosts consistency |
| **Codex / VSCode** | Repo-file fallback | Paste bootstrap prompt below at session start |

**Codex bootstrap prompt:**

```text
先讀 docs/CONTEXT.md、docs/pm/pm-skill/spec/pm-skill-proposal.md §6.4。
若我輸入 /pm <subcommand> 或 /pm-bug-review,讀 skills/pm-skill/SKILL.md 執行對應 workflow。
```

## Trigger Convention

This skill activates when user input matches `/pm <subcommand>` or `/pm-bug-review`. Subcommand routing in §Subcommand Router below.

Unknown subcommand → respond with command list (see §Subcommand: help).

## Start Here

Before handling ANY subcommand, read these in order:

**Repo bootstrap(對齊 Round 2 C3 fix — 確保 repo invariant 已 inject):**

1. `../../docs/CONTEXT.md` — repo 現況快速 context
2. `../../docs/ai-principles.md` — repo-wide AI 工作原則
3. `../../docs/index.md` — repo doc 全索引(L1/L2/L3 boundaries)

**PM Skill specific(對齊本 SKILL 邏輯):**

4. `docs/pm/pm-skill/spec/pm-skill-proposal.md` §6.4 (contracts) — authoritative source for path conventions, schema invariants, governance
5. `docs/pm/pm-skill/docs/pm-skill-user-manual.md` — scenario reference for expected behavior per subcommand
6. `docs/pm/active-project.txt` (if exists, runtime path) — current active project context for this terminal session
7. For lifecycle subcommands (archive/delete/restore), also `references/lifecycle-policy.md`

**Path Reference Convention(對齊 Round 2 C1 fix):**
- `../../docs/...` paths = **fixed file references** for Claude to READ at SKILL bootstrap(relative to SKILL.md location)
- `docs/...` paths = **runtime operational paths** at repo CWD(Claude operates from repo root,not SKILL.md location)
- 兩者語意不同,本 SKILL 全文遵循此 convention

For subcommand-specific deeper read, see per-subcommand sections below.

## Path Conventions (Round 5 architectural lock)

All file operations MUST follow per-project subfolder + `_org` shared structure:

```
docs/
├── pm/
│   ├── _org/                            # org-level shared
│   │   ├── active-project.txt           # current active project name (1 line)
│   │   ├── org-roster.md                # cross-project team roster
│   │   ├── org-decision-log.md          # cross-project audit
│   │   ├── org-retrospectives/
│   │   └── contract-pack/
│   ├── _archive/                        # archived projects
│   │   └── <project>/                   # 7-day grace period before _cold
│   └── <project>/                       # per-project (one per `/pm init`)
│       ├── state.md                     # current_phase / signoffs / project_type
│       ├── team-roster.md
│       ├── phase-gates.md
│       ├── output-schemas.md
│       ├── decision-log.md
│       └── reports/
│           ├── <date>-daily.md
│           ├── <date>-weekly.md
│           └── <date>-phase-N-*.md
├── reviews/
│   └── <project>/                       # per-project
│       ├── _summary-<target>.md
│       └── <date>-spectra-<target>-round-N.md
└── modules/
    └── <project>/                       # per-project
        ├── _plan.md
        └── <module>/
            ├── requirement.md
            ├── functional.md
            ├── plan.md
            ├── tests.md
            └── test-results.md
```

**Rule:** never write to a flat path like `docs/pm/state.md`. Always resolve via active project from `active-project.txt`.

## Active Project Context Detection

Resolution order (first hit wins):

1. Explicit `--project <X>` flag in the subcommand
2. `docs/pm/active-project.txt` content (set by `/pm use` or last `/pm init`)
3. If `docs/pm/<project>/` has exactly 1 subdirectory → assume that one
4. Otherwise → ask user to specify `/pm use "<project>"` first

If `docs/pm/active-project.txt` does not exist and step 3 fails, abort with:

```
❌ No active project. Run:
   /pm init "<project>"          # create new project
   /pm use "<project>"           # switch to existing
   /pm list                      # see all projects
```

## Spec Target Resolution Policy(v1.7,2026-06-20 PO lock — Round 7 meta-level migration complete)

> **Rule:** Project artifacts(spec / module-spec / review log)co-locate under `docs/pm/<project>/` per-project namespace。Meta-level concepts(如 PM Skill 本身、spectra-review framework)亦 own namespace(`docs/pm/<meta-project>/`),no special `_org/specs/` carve-out。
> **Trigger:** any write to spec-class artifact(requirement / design / module-spec / review log)
> **Source of truth:** active-project.txt + NL intent parse + 3-tier confirm matrix
> **Naming rule(Round 6):** internal operational files canonical / external shareable docs self-id with `<project>-` prefix

### Internal vs External naming tier(Round 6 PO lock)

| Tier | Files | Naming pattern | 理由 |
|:---:|:---|:---|:---|
| 🔵 **External shareable** | requirement spec / functional spec / design spec / module spec / user manual / user guide / review log / proposal | `<project>-<doc-type>.md`(self-id)| 共享 / share URL / IDE tab 看 filename 即知屬哪 project + 哪類 doc |
| 🟢 **Internal operational** | state.md / team-roster.md / decision-log.md / active-project.txt / _archived-at.txt / _org/* / templates | canonical(`state.md` etc)| 1-per-project,只在 folder context 才有意義,prefix = redundant noise |

### Resolution priority

1. **Explicit NL path**(eg.「save to docs/foo/bar.md」)→ trust verbatim,**no popup**
2. **Explicit NL project name**(eg.「幫 db-auto-syncup 寫 spec」)+ target ≠ active → use explicit + ⚠ override banner +`(Y/n)` confirm
3. **Meta-keyword detected**(「PM Skill / framework / contract / spectra-review framework」)→ each meta concept has own project namespace(eg. `docs/pm/pm-skill/spec/proposal.md`)+ confirm
4. **Active project exists** → `docs/pm/<active>/spec/...` + low-friction `(Y/n)` confirm
5. **Active is empty** → **sub-prompt** 問 PO 哪 project(列出 `/pm list` 結果),or `/pm init <new>`(不 refuse,對齊 PO 2026-06-20 lock)

### 3-tier confirm matrix

| File class | Default path | Confirm? | 理由 |
|:---|:---|:---:|:---|
| **Spec(Phase 0 requirement / Phase 1+ module spec)** | `docs/pm/<active>/spec/...` | ✅ **YES**(`Y/n`)| 結構性 deliverable,wrong project = audit trail 髒 |
| **State.md / team-roster.md** | `docs/pm/<active>/...` | 🟡 **only on init/restructure** | 後續 mutation 已有各 command 自身 confirm phrase |
| **Spectra review log** | `docs/pm/<active>/reviews/...` | ❌ **silent** | 高頻 + Claude 自動產出 + PO 已 review verdict 階段 confirm 過 |
| **Decision-log append** | `docs/decision-log.md`(repo-wide cross-project)| ❌ **silent** | Append-only,low risk |
| **Implementation file**(Phase 4+ backend/frontend)| repo source path | ❌ **N/A** | 普通 code,不走本 policy |

### Directory layout(canonical,Round 6 update)

```
docs/
├── pm/
│   ├── active-project.txt                                    🟢 internal
│   ├── _org/org-decision-log.md                              🟢 internal
│   ├── _archive/<old-project>/                               🟢 internal(full snapshot)
│   └── <project>/                                            ⭐ project SSOT,/pm archive sweep 全帶走
│       ├── state.md                                          🟢 internal(canonical)
│       ├── team-roster.md                                    🟢 internal(canonical)
│       ├── spec/
│       │   ├── <project>-requirement-spec.md                 🔵 external(self-id Phase 0 deliverable)
│       │   ├── <project>-design-spec.md                      🔵 external(if Phase 1+ design 分檔)
│       │   └── modules/<module>/
│       │       └── <project>-<module>-spec.md                🔵 external(Phase 1+ split)
│       └── reviews/
│           └── <date>-<project>-round-N-spec-review.md       🔵 external(date 在前,自然按時間排序)
└── decision-log.md                                            🟢 internal(repo-wide cross-project)
```

### Migration history

| Round | Date | Before | After |
|:---:|:---:|:---|:---|
| 5 | 2026-06-20 | `docs/2026-06-19-backend-schema-auto-sync-requirement-spec.md` | `docs/pm/backend-schema-auto-sync/spec/requirement.md` |
| 5 | 2026-06-20 | `docs/2026-06-18-phase-3-cicd-wrap-migration-spec.md` | `docs/pm/phase-3-cicd-wrap/spec/migration.md` |
| **6** | **2026-06-20** | `docs/pm/backend-schema-auto-sync/spec/requirement.md` | `docs/pm/backend-schema-auto-sync/spec/backend-schema-auto-sync-requirement-spec.md` |
| **6** | **2026-06-20** | `docs/pm/phase-3-cicd-wrap/spec/migration.md` | `docs/pm/phase-3-cicd-wrap/spec/phase-3-cicd-wrap-migration-spec.md` |
| **7** | **2026-06-20** | `docs/archives/htmljscss2claude_v2ui_20260512.tar.gz:htmljscss2claude_20260512/docs/2026-06-17-pm-skill-proposal.md` | `docs/pm/pm-skill/spec/pm-skill-proposal.md` |
| **7** | **2026-06-20** | `docs/archives/htmljscss2claude_v2ui_20260512.tar.gz:htmljscss2claude_20260512/docs/2026-06-17-pm-skill-user-manual.md` | `docs/pm/pm-skill/docs/pm-skill-user-manual.md` |
| **7** | **2026-06-20** | `docs/archives/htmljscss2claude_v2ui_20260512.tar.gz:htmljscss2claude_20260512/docs/2026-06-17-pm-skill-proposal-highlights.md` | `docs/pm/pm-skill/docs/pm-skill-proposal-highlights.md` |
| **7** | **2026-06-20** | `docs/archives/htmljscss2claude_v2ui_20260512.tar.gz:htmljscss2claude_20260512/docs/2026-06-17-spectra-review-requirement-proposal.md` | `docs/pm/spectra-review/spec/spectra-review-requirement-proposal.md` |

### Phase D complete(Round 7,2026-06-20)— meta-level migration

4 meta-level docs migrated to `docs/pm/<meta-project>/` namespace per PO 2026-06-20 lock:

| Meta-project | External spec | Internal docs |
|:---|:---|:---|
| `pm-skill` | `spec/pm-skill-proposal.md` | `docs/pm-skill-user-manual.md` + `docs/pm-skill-proposal-highlights.md` + `state.md` |
| `spectra-review` | `spec/spectra-review-requirement-proposal.md` | `state.md` |

**Cross-ref update scope:** 16 files batch-sed'd to absolute-from-root path syntax(無更多 `../../docs/` relative path reliance,convention uniform)。

| File class | Files updated |
|:---|:---|
| Repo-root configs | `QUICKSTART.md`, `docs/decision-log.md`, `.claude/commands/README.md`, `.claude/commands/spectra-review.md`, `CLAUDE.md` |
| Skills | `skills/pm-skill/SKILL.md`, `skills/spectra-review/SKILL.md`, `skills/spectra-review/references/f2-schema.md` |
| Review log archives | 8 files under `docs/reviews/`(migrated 2026-07-01 from subfolder — Session 1 Phase 3)|
| Self-refs(intra-spec relative links)| 2 files manually patched(`../spec/` and `../../pm-skill/spec/`)|

---

## SDLC v2 Contract Reference(canonical:proposal §6.4.16 + §6.4.17,rev 1.16)

> **Canonical source:** [`docs/pm/pm-skill/spec/pm-skill-proposal.md`](../../../../docs/pm/pm-skill/spec/pm-skill-proposal.md) **§6.4.16 SDLC v2 Contract** + **§6.4.17 Mid-Phase REQ Change Governance**(rev 1.16,promoted 2026-06-20)
> **Status:** Canonical contract(no longer "override")— supersedes §6.4.10 §B / §6.4.11 §B / §6.4.11 §C v1 versions
> **Authority:** §6.4.10 §L Contract Override Mechanism + revision 1.13 promotion 為 canonical
> **Below:** quick SKILL implementation reference;authoritative detail in proposal §6.4.16

### Phase 0 — Requirement Gathering(WHAT)

Goal:**WHAT users need 全鎖定**(no implementation discussion)

| Acceptance | 對齊 |
|:---|:---|
| Requirement spec authored(≥ 500 行 + 11 必填欄位 per REQ,含 golden_scenario + anti_examples 三元組)| §6.4.10 §B.4 |
| Glossary ≥ 7 / Out of Scope ≥ 3 / Assumptions ≥ 2 / Constraints ≥ 2 | §6.4.10 §B.2 |
| **Bootstrap PM only**(invoker auto-add as PM,no MVT 3-role enforcement)⭐ v2 NEW | §F |
| spectra-review pass | §6.4.3 |
| PO 拍板 spec ship-as-is | §6.4.4 |
| Phase 0 signoff(`/pm signoff phase-0 --approver <PM>`)| §6.4.10 §B.5 |

**Phase 0 NO LONGER includes:** team coverage check(MVT 3-role)— moved to Phase 1。

### Phase 1 — Structuring(HOW we organize)⭐ EXPANDED v2

Goal:**STRUCTURE + 各 module 功能設計鎖定**

5-step dialogue(每 step PO confirm 進下一 step):

```
Step 1.1: Module split discussion + Module Overview document
  - Default rule: split by artifact-type
    (eg. backend .py / SKILL.md / memory.md = 3 modules)
  - 1-artifact-type project → default 1 module (no ceremony)
  - PO override accepted with reason
  - ⭐ Deliverable 2(2026-06-20 PO 補):<project>-modules-overview.md
    HUMAN-FIRST 文件(對齊 memory feedback_human_first_docs):
      📋 What it does (1-2 sentence plain prose,everyone reads first)
      👔 For PM:ownership candidate / effort / risk / cross-module deps / sequencing
      🔬 For QA:test surface / approach / acceptance criteria refs / key scenarios
      💻 For Developer:REQ coverage / functions / file paths / library deps
    NO YAML blob as main content;metadata 退 frontmatter only

Step 1.2: /pm build-team(full team composition)
  - 對齊 split 後實際 work units 配人
  - kuohsuming multi-role still legal (1-PO scenario)
  - MVT 3-role coverage check pass(現在才 enforce,不在 Phase 0)
  - team-roster.md frontmatter v2 schema lock

Step 1.3: Assign modules → team(matrix)
  - Each module gets ≥ 1 owner
  - Multi-owner allowed (1-PO 自身可兼)
  - state.md modules[].owner field populate

Step 1.4: Functional spec per module(WHAT each module delivers)
  - Output: <project>-<module>-functional-spec.md
  - Feature list per module(對齊 §6.4.11 §C.2 schema simplified)

Step 1.5: Design spec per module(HOW implementation works)
  - Output: <project>-<module>-design-spec.md
  - ⭐ 恆寫(D-035:5 份 spec 永遠在,不 skip);risk/tier 只控深度 —— low-risk/simple = 寫到 floor(1 component + covers_func + file_impact + test_seam),不省
```

**Phase 1 Exit Check List(v2 — 9 criteria,authoritative = §Subcommand: gate-check phase-1 inline list):**
- [ ] Step 1.1 module split locked(state.md modules[] populated)
- [ ] Step 1.1 `<project>-modules-overview.md` authored(HUMAN-FIRST 3-role per module)  ⭐ Round 1 spectra C1 fix
- [ ] Step 1.2 team-roster.md v2 schema + MVT 3-role coverage pass
- [ ] Step 1.3 every module has ≥ 1 owner
- [ ] Step 1.4 functional spec authored per module
- [ ] Step 1.5 design spec authored per module(D-035:恆寫,不 skip;low-risk = floor 深度)
- [ ] 每個 Phase 0 REQ 被 ≥ 1 module 覆蓋
- [ ] Dependency graph 無 circular
- [ ] PM 簽核 `phase_1_signoff = true`

### Phase 2 — Implementation Planning(HOW we execute)⭐ LIGHTENED v2

Goal:**WORK PLAN 鎖定**(task / timeline / risk),**no longer 寫 functional / design spec — 已在 Phase 1 完成**

| Acceptance | 對齊 |
|:---|:---|
| Per-module `<project>-<module>-plan.md`(task breakdown + timeline + risk)| §6.4.11 §C.3 |
| Solo project carve-out:Phase 2 可 collapse 進 Phase 1(PO override + log)| §K Discipline Invariant |
| PM 簽核 `phase_2_signoff = true` | §6.4.11 §C.7 |

### Phase 3-7

Unchanged from §6.4.11 §D-§H。

### Migration policy for existing projects(2026-06-20)

| Project | Current Phase | v2 Migration |
|:---|:---:|:---|
| `backend-schema-auto-sync` | Phase 1(just advanced)| **Option C rollback to Phase 0**(PO 2026-06-20 lock)→ team-roster.md clean to bootstrap-PM-only → re-advance under v2 contract |
| Future projects | n/a | Default v2 from /pm init |

---

## Subcommand Router

> ℹ️ **Confidence Tier per workflow**(對齊 Round 3 C4 fix):本表只列命令 → workflow mapping。每個 subcommand 的 Confidence Tier(🟢 high / 🟡 medium / 🔴 low)寫在對應 `## Subcommand: <name>` workflow 段內。整體 framework 見 §Auto Behavior Confidence Tier。

| User input | Section |
|---|---|
| `/pm help` | §Subcommand: help |
| `/pm init "<project>" [--type <T>]` | §Subcommand: init |
| `/pm use "<project>"` | §Subcommand: use |
| `/pm list [--archived\|--filter <pattern>]` | §Subcommand: list |
| `/pm status [--project <X>]` | §Subcommand: status |
| `/pm whereami` ⭐ v1.4 | §Subcommand: whereami(v1.4 — rev 1.17.3 §E.8.8.8 active project + CWD + branch alignment display)|
| `/pm start "<project>" [--from-verbal-brief]` | §Subcommand: start |
| `/pm advance-phase <N>` ⭐ v1.1.11 supports N<current rollback | §Subcommand: advance-phase |
| `/pm signoff phase-<N> --approver <X>` | §Subcommand: signoff |
| `/pm gate-check <phase>` | §Subcommand: gate-check |
| `/pm daily` | §Subcommand: daily |
| `/pm weekly` | §Subcommand: weekly |
| `/pm dashboard` | §Subcommand: dashboard |
| `/pm health-check` | §Subcommand: health-check |
| `/pm kpi-eval` | §Subcommand: kpi-eval |
| `/pm archive "<project>" [--reason]` | §Subcommand: archive |
| `/pm restore "<project>"` | §Subcommand: restore |
| `/pm delete "<project>" --force --reason` | §Subcommand: delete |
| `/pm archive --filter <p> --confirm` | §Subcommand: archive (bulk) |
| `/pm delete --filter <p> --force` | §Subcommand: delete (bulk) |
| `/pm onboard <eng> --replace-for <X> --module <M>` | §Subcommand: onboard |
| `/pm offboard <eng> --next-project <Y>` | §Subcommand: offboard |
| `/pm build-team <natural-language>` | §Subcommand: build-team(v1.4 — NL→YAML team management,對齊 proposal §6.4.14)|
| `/pm new-requirement --from --description --deadline` | §Subcommand: new-requirement |
| `/pm contract-change propose` | §Subcommand: contract-change propose |
| `/pm bootstrap-project [--scope minimal\|standard\|full] [--unattended] [--resume-from <step>]` | §Subcommand: bootstrap-project(new in v1.1 minor change,對齊 §6.4.13 governance)|
| `/pm push-gate` | §Subcommand: push-gate(v1.2 — Stage 1 push enforcement,對齊 §6.4.11 §E.8.4)|
| `/pm setup-worktree` | §Subcommand: setup-worktree(v1.2 — Stage 1 init,對齊 §E.8.2)|
| `/pm migration-status` | §Subcommand: migration-status(v1.2 — cross-phase visibility,對齊 §G.6.0.4)|
| `/pm migration-propose <feature-id>` | §Subcommand: migration-propose(v1.2 — schema discipline propose,對齊 §G.6.0.5)|
| `/pm migration-apply --env <dev\|staging\|prod>` | §Subcommand: migration-apply(v1.2 — env-specific apply,對齊 §G.6.0.6)|
| `/pm migration-mark-applied --env prod --version <NNN>` | §Subcommand: migration-mark-applied(v1.2 — prod audit,對齊 §G.6.0.7)|
| `/pm validate-discipline-invariant` | §Subcommand: validate-discipline-invariant(v1.2 — §K meta gate,對齊 §K.6)|
| `/pm deploy --target <staging\|prod> [--override-discipline --reason "<text>"]` | §Subcommand: deploy(v1.2 — Azure CLI + multi-precondition,對齊 §G.6.1 + §K.8)|
| `/pm sanity-check [--category <C>] [--priority <P>] [--carve-out --reason "<text>"]` ⭐ v1.4 rev 1.17.10 | §Subcommand: sanity-check(rev 1.17.10 — Layer 4 mainline pre-deploy sanity via Pilot v0 LIFF test runner)|
| `/pm sanity-status <project> [--tc=<id>] [--since=<date>] [--diff=<a>..<b>] [--schema-version]` ⭐ v1.4 rev 1.17.13 | §Subcommand: sanity-status(rev 1.17.13 — multi-QA aggregation visualization + schema-version flag;implements sanity-check REQ-015 + REQ-018 D.1)|
| `/pm sanity-submit-result <project> <csv-or-json>` ⭐ v1.4 rev 1.17.12 | §Subcommand: sanity-submit-result(rev 1.17.12 — manual fallback import;implements sanity-check REQ-014)|
| `/pm sanity-cleanup-logs <project>` ⭐ v1.4 rev 1.17.12 | §Subcommand: sanity-cleanup-logs(rev 1.17.12 — explicit eruda log wipe;implements sanity-check REQ-017 G.1)|
| `/pm sanity-export-logs <project> [--output=<path>] [--qa-identifier=<id>] [--then-wipe]` ⭐ v1.4 rev 1.17.12 | §Subcommand: sanity-export-logs(rev 1.17.12 — pre-wipe export tar.gz;implements sanity-check REQ-017 G.6)|
| `/pm sanity-reset-db <project> --confirm-with "yes-reset-database"` ⭐ v1.4 rev 1.17.13 NEW | §Subcommand: sanity-reset-db(rev 1.17.13 — full sanity_check_DB reset for catastrophic recovery / dev clean slate;implements sanity-check REQ-018 C.2;**DESTRUCTIVE — PROD reject + literal phrase + pre-archive 3 layer safety net**)|
| `/pm sanity-tc-regenerate <md-file-or-tc-id> [--auto-detect] [--force] [--dry-run]` ⭐ v1.4 rev 1.17.16 UPGRADE | §Subcommand: sanity-tc-regenerate(rev 1.17.16 — **rev 1.21 cascade**:`git diff origin/main --name-status` A/M/D/R CRUD branch + pm_tag content-addressable identity + soft tombstone via mark_sanity_tc_unavailable;implements sanity-check rev 1.21 commits 4861f03 + 04b738f)|
| `/pm sanity-tc-validate [<md-file>] [--all] [--check-drift]` ⭐ v1.4 rev 1.17.16 UPGRADE | §Subcommand: sanity-tc-validate(rev 1.17.16 — **rev 1.21 cascade**:加 pm_tag format check + cross-ref uniqueness;non-destructive,reports issues without writing)|
| `/pm sanity-tc-prune <tc-id> --confirm-with "yes-prune-tc-<id>"` ⭐ v1.4 rev 1.17.15 unchanged | §Subcommand: sanity-tc-prune(rev 1.17.15 — admin **hard-delete escape hatch** with literal phrase per [[delete-dialog-no-undo-hint]];distinct from regenerate D path soft tombstone — rev 1.21 cascade NIT clarification)|
| `/pm sanity-tc-coverage [--diff] [--category <C>] [--page <spa_path>] [--format markdown\|table\|json] [--include-unavailable]` ⭐ v1.4 rev 1.17.16 UPGRADE | §Subcommand: sanity-tc-coverage(rev 1.17.16 — **rev 1.21 cascade**:加 --page JSON path filter + --include-unavailable admin view;category × operation matrix + 3-role meeting prep)|
| `/pm sanity-tc-db-bootstrap [--with-seed] [--reset --confirm-with "yes-reset-local-sanity-db"]` ⭐ v1.4 rev 1.17.16 NEW | §Subcommand: sanity-tc-db-bootstrap(**rev 1.21 cascade NEW** — local MySQL setup via SSOT;Azure substring refuse safeguard;destructive --reset literal phrase per [[delete-dialog-no-undo-hint]];implements sanity-check rev 1.21 parent layer E 5th subcommand)|
| `/pm sanity-tc-create "<NL spec>"` ⭐ v1.4 rev 1.17.17 NEW | §Subcommand: sanity-tc-create(**rev 1.27 cascade NEW** — Claude-as-gate 4-folder discipline;NL → MD draft to `edit/tc-XXX-draft.md`;implements sanity-check rev 1.27 Q1=a edit/ git tracked)|
| `/pm sanity-tc-update <TC-id> "<patch desc>"` ⭐ v1.4 rev 1.17.17 NEW | §Subcommand: sanity-tc-update(**rev 1.27 cascade NEW** — Claude clone `source/` → `edit/tc-XXX-pending-update.md` + patch + schema validate)|
| `/pm sanity-tc-archive <TC-id> --reason "<text>"` ⭐ v1.4 rev 1.17.17 NEW | §Subcommand: sanity-tc-archive(**rev 1.27 cascade NEW** — Claude clone `source/` → `edit/tc-XXX-pending-archive.md` tombstone draft;Q5 不加 deprecation metadata field — reason 留 git commit message)|
| `/pm sanity-tc-confirm <tc-id\|--all>` ⭐ v1.4 rev 1.17.17 NEW | §Subcommand: sanity-tc-confirm(**rev 1.27 cascade NEW** — Q2=a multi-draft fail-fast + suffix-based promote `edit/` → `source/`(create/update)或 `archive/`(tombstone))|
| `/pm sanity-tc-discard <tc-id\|--all>` ⭐ v1.4 rev 1.17.17 NEW | §Subcommand: sanity-tc-discard(**rev 1.27 cascade NEW** — rm `edit/` draft;對齊 [[delete-dialog-no-undo-hint]] discard 是 staging only,不影響 confirmed `source/` 或 `archive/`)|
| `/pm sanity-tc-edit-list` ⭐ v1.4 rev 1.17.17 NEW | §Subcommand: sanity-tc-edit-list(**rev 1.27 cascade NEW** — scan `edit/` → markdown table report;read-only diagnostic)|
| `/pm sanity-tc-seed-from-generated [--limit N] [--dry-run] [-v]` ⭐ v1.4 rev 1.17.18 NEW | §Subcommand: sanity-tc-seed-from-generated(**rev 1.27 cascade NEW** — seed `Sanity_Test_Case_Definition_TBL` from existing `generated/*.json` snapshots,skip Claude extract path;DB sync drift recovery + cost-conscious dogfood;per PO 2026-06-28 「let pm skill convert JSON to tc table」 directive + 「Y go path (ii)」 authorize)|
| `/pm sanity-tc-backend [start\|restart\|stop\|status]` ⭐ v1.4 rev 1.17.19 NEW | §Subcommand: sanity-tc-backend(**rev 1.27 cascade NEW** — Flask startup lifecycle auto-management;QA/PM 不 直接 跑 shell;PM Skill 自動 pre-flight dispatch before sanity-tc-* family commands;per PO 2026-06-28 「A is ok + PM Skill 自動 run」 directive)|
| `/pm sanity-tc-backfill-pm-tag [--dry-run] [--verbose] [--limit N]` ⭐ v1.4 rev 1.17.20 NEW | §Subcommand: sanity-tc-backfill-pm-tag(**rev 1.28 cascade NEW** — one-time backfill missing pm_tag in legacy source/ MDs;0 Claude call + 0 DB write + 0 backend dependency;additive only per `[[delete-dialog-no-undo-hint]]`;per PO 2026-06-28 「why more 30 tc lose the pm tag」 root cause analysis + 3-layer solution)|
| `/pm rollback [--to <commit>]` | §Subcommand: rollback(v1.2 — zero-downtime swap-back,對齊 §G.6.2)|
| `/pm verify-runtime` | §Subcommand: verify-runtime(v1.2 — external runtime prerequisite audit,new in v1.1.10)|
| `/pm validate-req-spec <path>` | §Subcommand: validate-req-spec |
| `/pm validate-module-plan <path>` ⚠ v1 grandfather only | §Subcommand: validate-module-plan |
| `/pm validate-module-spec <module> [--all]` | §Subcommand: validate-module-spec |
| `/pm validate-shared-infra` | §Subcommand: validate-shared-infra |
| `/pm validate-implementation <module> [--all]` | §Subcommand: validate-implementation |
| `/pm validate-coverage [--all\|--module <dir>]` | §Subcommand: validate-coverage |
| `/pm validate-integration` | §Subcommand: validate-integration |
| `/pm validate-release` | §Subcommand: validate-release |
| `/pm validate-post-launch` | §Subcommand: validate-post-launch |
| `/pm validate-all` | §Subcommand: validate-all |
| `/pm-bug-review <slug> [--finding\|--pending-only\|--overrides-only]` | §Subcommand: pm-bug-review |
| `/pm weekly` | §Subcommand: weekly(v1.1.9 — 7-day aggregated daily)|
| `/pm health-check` | §Subcommand: health-check(v1.1.9 — multi-layer SKILL audit)|
| `/pm kpi-eval` | §Subcommand: kpi-eval(v1.1.9 — Phase 7 KPI verify)|
| `/pm requirement impact-analysis <REQ-id>` | §Subcommand: requirement impact-analysis(v1.1.12 phase-aware + cost-aware — §6.4.17 rev 1.15)|
| `/pm requirement drop <REQ-id> --reason "<text>"` | §Subcommand: requirement drop(v1.1.11 — §6.4.17)|
| `/pm requirement add-mid-phase <REQ-id> --reason "<text>"` | §Subcommand: requirement add-mid-phase(v1.1.11 — §6.4.17)|
| `/pm requirement modify <REQ-id> --aspect <X> --reason "<text>"` | §Subcommand: requirement modify(v1.1.11 — §6.4.17)|
| `/pm spec-rev-bump <project> --rev <X>.<Y> --reason "<text>"` | §Subcommand: spec-rev-bump(v1.1.11 — §6.4.17)|
| `/pm requirement split <REQ-id> --into <new-id-list> --reason "<text>"` | §Subcommand: requirement split(v1.1.13 — §6.4.17 specialized)|
| `/pm requirement merge --reqs <id-list> --into <new-id> --reason "<text>"` | §Subcommand: requirement merge(v1.1.13 — §6.4.17 specialized)|
| `/pm requirement move <REQ-id> --from <module> --to <module> --reason "<text>"` | §Subcommand: requirement move(v1.1.13 — §6.4.17 specialized)|
| `/pm assign-feature <fid> --to <eng> [--pair <X>]` | §Subcommand: assign-feature(v1.1.9 — manual ownership override)|
| `/pm contract-change status` | §Subcommand: contract-change status(v1.1.9)|
| `/pm contract-change rollback --change <N> --reason "<text>"` | §Subcommand: contract-change rollback(v1.1.9)|
| `/pm contract-change history --window <N>months` | §Subcommand: contract-change history(v1.1.9 — Evolution Report)|
| `/pm cross-project sync-decision <decision> --to <projects>` | §Subcommand: cross-project sync-decision(v1.1.9)|
| `/pm cross-project resource-check` | §Subcommand: cross-project resource-check(v1.1.9)|
| `/pm cross-project common-pattern` | §Subcommand: cross-project common-pattern(v1.1.9)|
| `/pm org-retrospective --window <N>months` | §Subcommand: org-retrospective(v1.1.9 — 半年 retro)|
| `/pm validate-modules-overview <path>` | §Subcommand: validate-modules-overview(v1.1.10 — SDLC v2 G1)|
| `/pm validate-functional-spec <path>` | §Subcommand: validate-functional-spec(v1.1.10 — SDLC v2 G1)|
| `/pm validate-design-spec <path>` | §Subcommand: validate-design-spec(v1.1.10 — SDLC v2 G1)|
| `/pm memory list [--type <T>\|--filter <pattern>]` | §Subcommand: memory list(v1.1.10 — G2)|
| `/pm memory add <name> --type <user\|feedback\|project\|reference>` | §Subcommand: memory add(v1.1.10 — G2)|
| `/pm memory update <name>` | §Subcommand: memory update(v1.1.10 — G2)|
| `/pm memory remove <name>` | §Subcommand: memory remove(v1.1.10 — G2)|
| `/pm draft-modules-overview` | §Subcommand: draft-modules-overview(v1.1.10 — G3 Step 1.1 helper)|
| `/pm draft-functional-spec <module>` | §Subcommand: draft-functional-spec(v1.1.10 — G3 Step 1.4 helper)|
| `/pm draft-design-spec <module>` | §Subcommand: draft-design-spec(v1.1.10 — G3 Step 1.5 helper)|
| `/pm decision-log search "<query>"` | §Subcommand: decision-log search(v1.1.10 — G4)|
| `/pm decision-log filter --since <date> [--until <date>]` | §Subcommand: decision-log filter(v1.1.10 — G4)|
| `/pm decision-log compact [--older-than <Nmonths>]` | §Subcommand: decision-log compact(v1.1.10 — G4)|
| `/pm daily-sync` | §Subcommand: daily-sync(v1.1.10 — G5 multi-dev ritual,1-PO no-op default)|

### v1.1 Planned(✅ Implemented in v1.1.9 — 2026-06-20 batch落地 12 commands)

以下命令在 user manual rev 1.8 demo,但**未在 SKILL.md v1.0 實作 workflow**。觸發這些命令時,SKILL 必須:
1. 回應「Not implemented in PM Skill v1.0. Planned for v1.1.」
2. 引用 user manual 對應 scene reference 給 user 看 demo
3. 不強制嘗試執行 — 避免產出假/錯結果

| 命令 | Manual reference | Status |
|---|---|---|
| `/pm weekly` | scene 6a Daily Briefing 變體 | ✅ Implemented(v1.1.9) |
| `/pm health-check` | scene 6/12 隱含 | ✅ Implemented(v1.1.9) |
| `/pm kpi-eval` | scene 10 Phase 7 KPI | ✅ Implemented(v1.1.9) |
| `/pm requirement impact-analysis <REQ-id>` | scene 15 mid-flight | ✅ Implemented(v1.1.9) |
| `/pm assign-feature <fid> --to <eng> [--pair <X>]` | scene 15 manual override | ✅ Implemented(v1.1.9) |
| `/pm contract-change status` | scene 14 Evolution Report 隱含 | ✅ Implemented(v1.1.9) |
| `/pm contract-change rollback --change <N> --reason` | scene 14 rollback | ✅ Implemented(v1.1.9) |
| `/pm contract-change history --window <N>months` | scene 14 Evolution Report | ✅ Implemented(v1.1.9) |
| `/pm cross-project sync-decision [...]` | scene 12 cross-project | ✅ Implemented(v1.1.9) |
| `/pm cross-project resource-check` | scene 12 dashboard | ✅ Implemented(v1.1.9) |
| `/pm cross-project common-pattern` | scene 12 dashboard | ✅ Implemented(v1.1.9) |
| `/pm org-retrospective --window <N>months` | scene 12 半年 retro | ✅ Implemented(v1.1.9) |

### v1.2 Planned(Multi-Dev → Production Workflow,對齊 proposal rev 1.12 §6.4.11 §E.8 / §F.6 / §G.6 / §K)

PO 2026-06-18 拍板 3-stage promotion model 後新增。**未在 SKILL.md v1.0/v1.1 實作 workflow**,觸發時走 fallback 並 cite proposal §6.4.11 對應段。

| 待實作命令 | Proposal reference | 對應 Phase | 預計 v1.2 |
|---|---|:---:|---|
| `/pm setup-worktree` ✅ Implemented(v1.1.8)| §6.4.11 §E.8.2 | **3(起始)— rev 1.17 amendment** | v1.2 |
| `/pm daily-sync` | §6.4.11 §E.8.3 | **3+(daily — worktree daily ritual)— rev 1.17 amendment** | v1.2(deferred — 1-PO 場景退化)|
| `/pm push-gate` ✅ Implemented(v1.1.7)| §6.4.11 §E.8.4 | **3+(per push — worktree commits)— rev 1.17 amendment** | v1.2 |
| `/pm advance-phase 5` (enhancement)| §6.4.11 §F.6 | 4→5 transition | v1.2(既有 advance-phase 接 §F.6)|
| `/pm migration-status` ✅ Implemented(v1.1.8)| §6.4.11 §G.6.0.4 | 跨 Phase 3-7 | v1.2 |
| `/pm migration-propose <feature-id>` ✅ Implemented(v1.1.8)| §6.4.11 §G.6.0.5 | 3(propose stage)| v1.2 |
| `/pm migration-apply --env <dev\|staging\|prod>` ✅ Implemented(v1.1.8)| §6.4.11 §G.6.0.6 | 5(staging)/ 6(prod)| v1.2 |
| `/pm migration-mark-applied --env prod --version <NNN>` ✅ Implemented(v1.1.8)| §6.4.11 §G.6.0.7 | 6(prod manual)| v1.2 |
| `/pm validate-discipline-invariant` ✅ Implemented(v1.1.8)| §6.4.11 §K.6 | 跨 Phase 0-7 + deploy precheck | v1.2 |
| `/pm deploy --target <staging\|prod>` ✅ Implemented(v1.1.8)| §6.4.11 §G.6.1(含 schema_migrations_aware + discipline_invariant gate)| 6 | v1.2 |
| `/pm deploy --override-discipline --reason "<text>"` ✅ Implemented(v1.1.8)| §6.4.11 §K.8 | 6(PO override 唯一 escape)| v1.2 |
| `/pm rollback [--to <commit>]` ✅ Implemented(v1.1.8)| §6.4.11 §G.6.2 | 6 / 7 | v1.2 |

**v1.2 Architecture Premise:**

> ⭐ **rev 1.17(2026-06-23 PO 拍板 Option A)**:Worktree lifecycle extended — Phase 3 entry trigger(not Phase 4)。**Rationale:** Phase 3 shared infra(schema SSOT + 共用 helper)若 commit 進 main,project 沒 ship 就污染 main(orphan schema risk)。Phase 3+4 同 worktree,Phase 5 才 merge,對齊 always-deployable main invariant。

```
Phase 0-2 ─── docs only ─── main(spec/requirement/plan — zero codebase change)
   ↓ /pm advance-phase 3 → AUTO trigger /pm setup-worktree(NEW timing,rev 1.17)
   ↓
Stage 0(Phase 3 末): V8 Cross-Module Spec Review Gate ⭐ rev 1.9 加(對齊 Gap 4 PO 拍板)
   • 5 engineer + Tech Lead + PO 共審 N module F-spec + D-spec
   • verdict=ship-as-is + 0 carry-over BLOCKER → spec read-only lock
   • 未過 → block /pm advance-phase 4
   ↓ Phase 3 signoff
   ↓
Stage 1: Team Worktree(dev/<project>,Phase 3 + Phase 4 同住 — rev 1.17)
   • Phase 3 shared infra(schema SSOT + helper)commits to worktree(NEW)
   • Phase 4 module dev commits to worktree(unchanged)
   • cross-module contract drift → /pm contract-change propose → lite V8(§E.4b)
   ↓ /pm advance-phase 5(auto merge dev/<project> → main)
Stage 2: Main(Phase 5 QA — 對齊 §F + staging migrations applied)
   • 此時 main 才見到 Phase 3+4 整個 bundle
   ↓ /pm migration-apply --env staging(integration phase)
   ↓ /pm migration-apply --env prod(prod print only)+ /pm migration-mark-applied --env prod
   ↓ /pm deploy --target prod(PO 拍板,含 schema_migrations_aware gate)
Stage 3: Azure Web App(production)

⭐ Invariant: main 永遠 always-deployable;Phase 3+4 WIP never visible in main
   • Project abandoned mid-way = git branch -D dev/<project>;main 0 cleanup
   • Multiple parallel projects = multiple dev/<project> worktrees coexist
```

**v1.2 Schema Migration Awareness(rev 1.8 加,對齊 memory `backend_schema_change_workflow`):**

| Artifact | 用途 |
|:---|:---|
| `laundry_db_create_tables.sql` | SSOT(既有) |
| `docs/migrations/manifest.yaml` | per-project migration index(forward/backward/verify 三樣) |
| `docs/migrations/<date>-<NNN>-<slug>.sql` | per-migration script |
| `docs/pm/<project>/migration-state.md` | per-env applied state tracker |

PM Skill 透過 file hash + manifest 達成 awareness,**對齊 PO 自 apply prod migration**(不開 prod DB execute 洞)。

**SKILL fallback when invoked:**

```
⚠ /pm <subcommand> 在 PM Skill v1.0 尚未實作(planned v1.1)。

📍 對應 user manual 場景 demo:
   docs/pm/pm-skill/docs/pm-skill-user-manual.md 場景 <N>

🎯 工作 alternative:
   - 手動依 manual 場景做(對齊 §6.4 contract)
   - 或 wait for v1.1 release(對齊 §6.4.13 Contract Change Governance)
```

---

## Subcommand: help

Output the command list verbatim (see manual rev 1.8 §場景 0). Group by Lifecycle / Reporting + Cross-Project / Project Lifecycle / Validator / Bug Review / V mode.

End with: `詳細用例見 docs/pm/pm-skill/docs/pm-skill-user-manual.md(rev 1.8,18 場景)`.

---

## Shared Guard: Mainline-Forbidden Commands(rev 1.17.3 §E.8.8.2)

> Applied at **Step 1** of all forbidden subcommand workflows when active=mainline。Single shared snippet to avoid 8x duplication。

**Forbidden commands when active=mainline:**
`/pm init mainline` / `/pm advance-phase <N>` / `/pm signoff phase-<N>` / `/pm gate-check phase-<N>` / `/pm setup-worktree` / `/pm rollback <N>` / `/pm archive` / `/pm restore`

**Guard snippet(reference as 「mainline-forbidden guard」 in workflows below):**

```python
# Step 1.0 — mainline-forbidden guard (rev 1.17.3 §E.8.8.2)
active = read("docs/pm/active-project.txt").strip()
if active == "mainline":
    abort(
        f"`/pm <this-subcommand>` not applicable when active=mainline. "
        f"Mainline has no phase lifecycle (rev 1.17.3 §E.8.8.2). "
        f"Use these mainline-allowed commands instead: "
        f"`/pm status mainline` / `/pm whereami` / `/pm push-gate` / "
        f"`/pm deploy` / `/pm validate-discipline-invariant`. "
        f"Or switch to a project first: `/pm use <project>`."
    )
```

**Confidence Tier:** 🟢 high(machine check + clear error message)

---

## Subcommand: init

**Arguments:** `"<project>"` required, `--type <production|training|poc|sandbox>` optional (default `production`).

**Workflow:**

0. **rev 1.17.3 — `mainline` reserved name guard:** If `<project>` == "mainline" → abort: `"`mainline` is reserved system project name per rev 1.17.3 §E.8.8.2. Choose a different name."`
1. Validate project name (kebab-case, no spaces, < 50 chars).
2. If `docs/pm/<project>/` already exists → abort: "Project already exists. Use `/pm use <project>` to switch or `/pm archive` first."
3. Create per-project subfolder:
   - `docs/pm/<project>/state.md` with frontmatter `current_phase: 0` + `project_type: <T>` + `created: <ISO8601>` + `sdlc_contract_version: v2`(⭐ v2 NEW — 對齊 §6.4.16 default)
   - `docs/pm/<project>/team-roster.md` (**bootstrap PM only** ⭐ — invoker auto-added as PM with `primary_role=PM`, `roles=[PM]`, `trust_tier=final_approver`;**no MVT 3-role enforce in Phase 0**;`coverage_status: bootstrap-only`;`coverage_missing_roles: [QA, Developer]`;`phase_0_carve_out: true` invariant per §6.4.14 §F)
   - `docs/pm/<project>/phase-gates.md` (copy from proposal §6.3.2 template)
   - `docs/pm/<project>/output-schemas.md` (copy from proposal §A.5 template)
   - `docs/pm/<project>/decision-log.md` (empty append-only)
   - `docs/pm/<project>/reports/` (empty dir)
   - `docs/pm/<project>/spec/` (empty dir — will hold `<project>-requirement-spec.md` + Phase 1+ artifacts per §6.4.16)
4. Create per-project module / review subfolders:
   - `docs/modules/<project>/` (empty, populated in Phase 1)
   - `docs/reviews/<project>/` (empty, populated by spectra-review)
5. If `docs/pm/_org/` does not exist → auto-create with org-roster / org-decision-log / org-retrospectives / contract-pack.
6. Set active project: write `<project>` to `docs/pm/active-project.txt` (overwriting).
7. Append to `docs/pm/_org/org-decision-log.md`:
   ```
   D-init-<seq>: project=<project> type=<T> created=<ISO8601> by=PO
   ```
8. Output matches scenario 0 PM Skill response format (see manual line 56-91).

**Confidence:** 🟢 high(file create / write operations,deterministic;name validation deterministic)

**SDLC v2 invariants(⭐ 2026-06-20 PO lock — canonical §6.4.16):**

- Step 3 bootstrap-PM-only:不在 Phase 0 enforce MVT 3-role(QA / Developer 由 Phase 1 Step 1.2 `/pm build-team` 補上)
- `state.md.sdlc_contract_version: v2` default(consumed by `/pm gate-check` dispatcher)
- `/pm advance-phase 1` 後跑 5-step dialogue(Step 1.1 → 1.5)
- Workflow consumers 必 `phase_0_carve_out: true` check 對齊 §6.4.14 §F bootstrap protection

**Project Type behaviors (locked here, referenced everywhere):**

| Type | delete safety | scaling override | auto-expiry |
|---|---|---|---|
| `production` | reject without `--force` + 7d no commit | §6.4.10 §C standard | none |
| `training` | direct delete OK | small-spec fast-track | 30d auto-archive |
| `poc` | needs `--force` but reason lenient | small-spec fast-track | 90d auto-archive |
| `sandbox` | direct delete OK | small-spec fast-track | 30d auto-archive |

---

## Subcommand: use

**Arguments:** `"<project>"` required. **Special:** `mainline` reserved system project name (rev 1.17.3).

**Workflow:**

1. **rev 1.17.3 — `mainline` special handling:**
   - If `<project>` == "mainline":
     - Require `--reason "<text>"`(≥ 30 chars per §E.8.8.4)。If missing → abort + prompt: `"Switching to mainline requires --reason (≥ 30 chars). Mainline ops bypass worktree workflow — explicit intent required."`
     - Verify `docs/pm/mainline/state.md` exists (auto-create with system_special schema if missing — see §E.8.8.2)
     - Update `docs/pm/active-project.txt` → `"mainline"`
     - Append to `docs/pm/mainline/state.md` `recent_switches[]`:
       ```yaml
       - to: mainline
         from: <previous-project>
         at: <ISO>
         reason: "<text>"
         duration_pending: true     # closed on switch back
       ```
     - Append `D-pm-switch-to-mainline-<id>` to `org-decision-log.md`
     - Echo onboarding banner:
       ```
       ⚠ Switching to mainline (= main branch direct ops)
       Reason: <text>
       All commits land on main branch directly.
       Switch back: /pm use <previous-project>
       Idle threshold: 60 min (PM Skill will prompt)
       ```
   - If switching back FROM mainline to a normal project:
     - Close pending entry in `docs/pm/mainline/state.md` `recent_switches[].duration_pending` → compute duration + set false
     - Update mainline metrics (active_duration_this_month += duration)
     - Append `D-pm-switch-back-from-mainline-<id>`
   - Continue to step 2 for normal flow

2. **Normal project flow:**
   - Verify `docs/pm/<project>/state.md` exists. If not → abort: "Project '<project>' not found. Run `/pm list` to see options or `/pm init` to create."
3. Write `<project>` to `docs/pm/active-project.txt`.
4. **rev 1.17.3 routing resolution(對齊 §E.8.8.1):**
   - For normal project,check `git ls-remote origin dev/<project>` to determine routing:
     - IF branch exists → routes to worktree at `../<project>/` + branch `dev/<project>`
     - ELSE → routes to mainline (main repo + branch main per pre-rev-1.17 contract)
   - Echo routing decision in status output.
5. Read `state.md` and display: project name / current_phase / project_type / last activity / routing target (worktree path OR mainline).
6. Output: `✅ Active project switched to <project>. Routing: <worktree path | mainline>. Subsequent commands target this.`

**rev 1.17.3 forbidden commands for mainline:**

When `active-project.txt = "mainline"`,the following commands abort with `"mainline has no phase lifecycle — N/A. Use /pm status mainline / /pm whereami / /pm push-gate instead."`:
- `/pm init mainline`(reserved name)
- `/pm advance-phase <N>`
- `/pm signoff phase-<N>`
- `/pm gate-check phase-<N>`
- `/pm setup-worktree`
- `/pm rollback <N>`
- `/pm archive`
- `/pm restore`

---

## Subcommand: list

**Arguments:** `[--archived]`, `[--filter <pattern>]`, `[--all]`(rev 1.17.3 — include system_special projects)。

**Workflow:**

1. Scan `docs/pm/*/state.md` (skip `_org`, `_archive` unless `--archived` flag set).
2. **rev 1.17.3 — filter system_special projects:** For each state.md,if frontmatter `type: system_special`(eg. `mainline`)→ skip from default list view。Only included if `--all` flag set。Shown in separate "System Projects" section if `--all`。
3. For each, read project name, current_phase, project_type, last activity (mtime).
4. Apply `--filter` pattern (glob match on project name) if provided.
4. Render as table:
   ```
   Project                    | Phase | Type        | Last Activity | Status
   ---------------------------|-------|-------------|---------------|--------
   namecard-v3-subscription   | 7     | production  | 2026-09-15    | active
   namecard-v3-team-account   | 4     | production  | 2026-09-14    | active
   training-小華-sandbox       | 0     | training    | 2026-09-10    | active(expires in 23d)
   ```

If `--archived`, scan `docs/pm/_archive/` instead and add column `archived_at`.

---

## Subcommand: status

**Arguments:** `[--project <X>]` (optional, defaults to active project).

**Workflow:**

1. Resolve active project (see §Active Project Context Detection).
2. Read sources(對齊 Round 2 N3 fix — source path 明示):
   - `docs/pm/<project>/state.md` — phase / signoffs / target_release_date / `outstanding_blockers` (YAML list)
   - `docs/pm/<project>/decision-log.md` — grep `status: pending` entries → contributes to outstanding_blockers count
   - `docs/reviews/<project>/_summary-*.md` Quality Health Score — `pending` / `no_decision` count → contributes to open_issues_count
3. Display: project / phase / signoffs / target_release_date / outstanding_blockers / open_issues_count / last_phase_advance.
4. Recommend next action based on phase + outstanding_blockers.

**Confidence:** 🟢 high(file reads + count aggregations deterministic)

---

## Subcommand: whereami(new in v1.4 — rev 1.17.3 §E.8.8.8)

> 對齊 proposal §6.4.11 §E.8.8.8。Read-only display of active project + expected CWD + branch + alignment status。Mitigates edge case: PO 切 project 後 cd 錯 dir。

**Arguments:** none

**Workflow:**

1. **Resolve active project:**
   - Read `docs/pm/active-project.txt`
   - If file missing OR empty → output: "📍 No active project set. Run `/pm use <project>` or `/pm use mainline --reason \"...\"`."
2. **Determine expected CWD + branch per §E.8.8.1 routing:**
   - If active == "mainline":
     - expected_cwd = <main repo dir>(detect via `git rev-parse --show-toplevel`)
     - expected_branch = "main"
   - Else (active = <project>):
     - Check `git branch -r | grep -q "origin/dev/<project>"`(local check first per §E.8.8.1 perf)
     - If branch exists:
       - expected_cwd = "../<project>/"
       - expected_branch = "dev/<project>"
     - Else (no remote worktree branch — pre-rev-1.17 / not setup-worktree'd):
       - expected_cwd = <main repo dir>
       - expected_branch = "main"
3. **Read current state:**
   - current_cwd = `pwd`
   - current_branch = `git branch --show-current`
4. **Output:**
   ```
   📍 Active project: <project>
                      (since <duration> ago, via /pm use)
                      <project>: routing → <worktree | mainline>
   📂 Expected CWD:   <expected path>
   📂 Your CWD:       <current path>
   🌿 Expected branch: <expected branch>
   🌿 Current branch:  <current branch>

   <alignment status>
   ```
5. **Alignment status:**
   - If CWD aligned AND branch aligned → `✅ Aligned — safe to commit`
   - If CWD mismatch → `⚠ MISMATCH (CWD) — suggest: cd <expected_cwd>`
   - If branch mismatch → `⚠ MISMATCH (branch) — suggest: git checkout <expected_branch>`
   - If both mismatch → `⚠⚠ DOUBLE MISMATCH — /pm use mismatch + likely wrong dir; suggest re-align`
6. **Mainline-specific banner**(if active=mainline):
   ```
   ⚠⚠ ACTIVE: mainline
       All commits go to main branch directly.
       Time active as mainline: <duration>
       Idle threshold: 60 min
       Switch back: /pm use <last-project>
   ```

**Confidence Tier:** 🟢 high(read-only display,deterministic git plumbing)

**Cross-references:**
- proposal §6.4.11 §E.8.8.8 whereami command spec
- §E.8.8.1 active-project routing rule
- §E.8.8.5 visual warning + idle timeout

---

## Subcommand: start

**Arguments:** `"<project>"` required, `[--from-verbal-brief]` optional.

**Workflow:**

1. Verify `docs/pm/<project>/state.md` exists and `current_phase == 0`.
2. If `--from-verbal-brief`:
   - Prompt user for 4 Q&A (see manual scene 1 lines 105-129).
   - From answers, derive atomic REQs aligned with §6.4.10 §B.4 schema (11 required fields 含三元組).
   - **【P3c 前關】Admission Gate** — 對每個 derived 候選跑 **rulebook §2.5 五項准入測試**(可追溯/有證據/值得寫/是what非how/有必要);沒過 → 路由 Open Questions(T1/T2)/ Out of Scope(T3/T5)/ 反推 what(T4);T3 carve-out=安全·資料·法遵;PO 可 override(記 decision-log)。**只有過閘門的候選才進下一步 authoring**;T3 評分同時定該 REQ priority。
   - **Triad authoring** — 對每個過閘門的 REQ 跑 **§Shared: Triad Authoring Behavior**(Auto-Completion 補 golden_scenario + anti_examples + Coverage Expansion 舉一反三 ~3 相鄰候選逐一討論;新候選同樣先過 §2.5 閘門);人給的 verbal brief 是片段,此步補全覆蓋面.
   - Auto-inject Glossary (≥ 7 terms target — see manual rev 1.6 N5 fix), Out-of-Scope (≥ 3), Assumptions (memory-inject from `~/.claude/projects/.../memory/MEMORY.md`), Constraints (memory-inject backend_change_rule / azure_webapp_runtime / etc.).
   - **【P3c 後關】Write-time 3-Role Sign-off** — 每個三元組齊的 REQ 寫入前跑 **rulebook §5.5**:async per-REQ 👔PM/🔬QA/💻Dev sign-off,**有人決定就走**(non-blocking;其餘轉 advisory → `/pm requirement modify`);`team_size==1` collapse 成 1 張三視角;high-stakes floor;verdict append 成 REQ signoff 註記(reject→Out of Scope 不刪 + revivable);結果匯總進 phase-0 signoff 證據。
3. Write draft Requirement Spec to `docs/<date>-<project>-requirement.md` rev .1 (or `docs/pm/<project>/requirement-spec.md` if user prefers per-project location — confirm with user)。**Frontmatter `schema_version: req-spec-v1.1`**(新建 spec triad required per §6.4.10 §G B1 discriminator)。
4. Update `state.md`: phase_0_kickoff_done: true.
5. Recommend next: `/spectra-review <requirement-spec-path>` (see manual scene 2).
6. Output matches manual scene 1 PM Skill response.

---

## Subcommand: advance-phase

**Arguments:** `<N>` (phase number 0-7).**N < current_phase = rollback path**(對齊 §6.4.17 P1 — PM-triggered ONLY)

**Workflow(v3,2026-06-20 — §6.4.17 rollback path added + rev 1.17.3 mainline guard):**

0. **Apply mainline-forbidden guard**(rev 1.17.3 §E.8.8.2 — see Shared Guard section above)。Abort if active=mainline。

1. Resolve active project + read `state.md.current_phase` as `<C>`.

2. **Direction dispatcher:**
   - If `<N> > <C>` → **forward path**(advance,steps 3-6 below)
   - If `<N> < <C>` → **rollback path**(對齊 §6.4.17 P1 — go to Step R1 below)
   - If `<N> == <C>` → abort:「Already at Phase <N>. No-op.」

3. **Forward path** — Verify `gate-check phase-<N-1>` has passed (read `state.md.phase_<N-1>_signoff`).
4. If not signed off → abort: "Phase <N-1> not signed off. Run `/pm gate-check phase-<N-1>` first."
5. Update `state.md.current_phase = <N>` + `phase_<N>_started_at` timestamp.

### Rollback path(對齊 §6.4.17 P1 — PM-explicit ONLY)

When `<N> < <C>`:

- **R1. Sub-prompt require `--reason "<text>"`** if not provided(reason ≥ 20 chars,對齊 §K.8 audit minimum)
- **R2. Show preview:**
   ```
   ⚠ Phase Rollback Preview
   Current phase: <C>
   Target phase: <N>
   Phases to revert: <C>, <C-1>, ..., <N+1>
   
   Artifacts preservation:
     - state.md.modules[] → phase_<C>_history.modules
     - spec/modules/* → spec/_phase<C>_rollback/<ISO>/
     - modules-overview.md kept as historical reference
   
   State resets:
     - current_phase = <N>
     - phase_<N+1>_signoff..phase_<C>_signoff = false
     - phase_<N+1>_started_at..phase_<C>_started_at cleared
   ```
- **R3. Require `CONFIRM ROLLBACK` 二次確認**(對齊 §K.8 BYPASS-style destructive phrase)。
- **R4. On confirm:**
   - Move `state.md.modules[]` to `phase_<C>_history.modules[]`(audit preserve)
   - Move `spec/modules/<C>/` → `spec/_phase<C>_rollback/<ISO>/`
   - Reset `state.md.current_phase = <N>` + phase signoff/started_at fields
   - Keep `modules-overview.md` as-is(historical reference per P3)
- **R5. Audit:** Append `D-rollback-<project>-<seq>: from=<C> to=<N> reason="<text>" preserved=[<list>] by=PO at=<ISO>`
5. Auto-trigger the phase's owning sub-skill / dialogue:
   - **Phase 1**(v2 EXPANDED — canonical proposal §6.4.16)→ 5-step dialogue:
     - **Step 1.1** module split discussion(default by artifact-type)+ 寫 `<project>-modules-overview.md`(HUMAN-FIRST 3-role 強制結構:📋 What it does / 👔 For PM / 🔬 For QA / 💻 For Developer per module + Big picture + dependency graph + coverage matrix)— 對齊 memory `feedback_human_first_docs`
     - **Step 1.2** `/pm build-team` full team composition + MVT 3-role check enforce(現在才強制,不在 Phase 0)
     - **Step 1.3** module ownership assignment(state.md modules[].owner populate);**functional_spec_author + design_spec_author default to module owner unless PO override**(對齊 §6.4.16 Step 1.3 + spectra Round 1 C3 fix)
     - **Step 1.4** functional spec per module(`<project>-<module>-functional-spec.md`)— 同 HUMAN-FIRST 3-role 結構
     - **Step 1.5** design spec per module(`<project>-<module>-design-spec.md`)— ⭐ **恆寫(D-035:5 份恆在,不 skip)**;risk_level 只控深度:medium|high = 完整;low-risk/simple = 寫到 floor(1 component + covers_func + file_impact + test_seam),不省
   - **Phase 2**(v2 LIGHTENED — canonical proposal §6.4.16)→ Per-module `<project>-<module>-plan.md`(task breakdown + timeline + risk only;functional / design 已在 Phase 1 完成);solo carve-out 可 collapse 進 Phase 1(PO override + log)
   - **Phase 3**(rev 1.17 amendment + rev 1.17.8 step renumber)→ **invoke `/pm setup-worktree` inline as Step 5.3**(對齊 §E.8.2 — auto-trigger 是 actual subcommand chain,not just doc reminder;**rev 1.17.8 C1 fix** — was Step 5.5 pre-rev-1.17.6,renamed to Step 5.3 to avoid collision with Phase 5 dispatch's Step 5.5 post-merge regression check)。On success:state.md updated with `worktree_branch: dev/<project>` + `phase_3_started_at`。Then proceed to Phase 3 shared infra setup on the new worktree。
   - **Phase 4** → V2 (implementation on existing worktree — no setup-worktree re-trigger;Step 4 idempotency check in §E.8.2 handles re-entry gracefully)
   - **Phase 5**(rev 1.17 amendment expansion of §F.6 + rev 1.17.2 CWD switch + rev 1.17.6 post-merge regression check + rev 1.17.8 scope generalization)→ **inline subroutine: merge `dev/<project>` → main + post-merge verify**:

     > ⭐ **rev 1.17.8 C5 scope generalization(2026-06-23,from same-session spectra-review):** Progressive Widening Verification(Step 5.5 Layer 2 + Step 5.7 Layer 3)applies to **ALL `dev/<project>` → main merges** — not strictly `/pm advance-phase 5→6` transition only。Empirical justification:**same risk pattern**(worktree code ≠ merged main code + semantic merge correctness + side-channel impact on other features)applies regardless of phase boundary specifics。Formal scope:
     > 1. `/pm advance-phase 5→6` transition(original rev 1.17.6+1.17.7 scope)
     > 2. **ALL Phase 6+ in-build-queue `dev/<project>` → main merges**(empirically validated:backend-schema-auto-sync F1 merge df9dc8a + F2 merge 5a20d68 — both Layer 2 PASS 9/9)
     > 3. Future analogous boundary transitions(eg. Phase 6→7 if introduced)
     >
     > **Carve-out mechanism**:Project may exempt specific merges via `state.md.phase_<N>_progressive_widening_carve_out: [<commit_hash>, ...]` with explicit reason field — for cases like doc-only merges where Layer 2 integration test 顯然 N/A。Carve-out 必走 PO authorize per `backend_change_rule` spirit。
     >
     > **Reader hint**:When implementer reads "Phase 5 dispatch" below,interpret as「any worktree → main merge under Phase 5+ semantics」not literal Phase 5 transition only。

     **Step 5.1 — Merge worktree → main:**
     ```bash
     cd <main repo dir>                                       # rev 1.17.2 — must run from main, NOT ../<project>/ worktree
     git checkout main && git pull origin main
     git merge --no-ff dev/<project> -m "phase-5(merge): <project> worktree → main per §F.6 rev 1.17"
     # do NOT push yet — rev 1.17.6 Step 5.5 + rev 1.17.7 Step 5.7 BOTH gate the push (rev 1.17.8 C3 fix — was outdated saying only Step 5.5 gates)
     ```
     Conflict handling: if `git merge` reports conflicts → resolve(append-only patterns usually clean union)or `git merge --abort` + leave worktree intact for engineer fix in `../<project>/`。

     **Step 5.5 — Post-merge regression check (Progressive Widening Layer 2) ⭐ rev 1.17.6(PO 2026-06-23 insight — worktree test pass ≠ merged main test pass):**
     ```bash
     # Re-run integration test suite from main HEAD per state.md.phase_5_staging_strategy
     # Project owner chooses command (Path A local / Path B staging) — PM Skill reads phase_5_staging_strategy hint
     # Example for Path A local:
     #   SCHEMA_SYNC_INTEGRATION_TEST=1 SCHEMA_SYNC_TEST_DB_HOST=127.0.0.1 ... python3 -m unittest <integration test module>
     ```
     - **on PASS**(all integration scenarios green on main HEAD)→ proceed to Step 5.7 mainline build sanity check
     - **on FAIL** → `git reset --hard ORIG_HEAD`(revert merge atomically)+ abort advance-phase + state.md.current_phase stays N + leave worktree intact for engineer investigation
     - **Catches:** (1) semantic merge conflict resolution correctness;(2) main divergence indirect impact on project code;(3) atomic merge ≠ semantic correctness gap
     - **Audit fields written on success:** `phase_<N>_post_merge_regression_check_at: <ISO>` + `phase_<N>_post_merge_regression_check_result: pass` + `phase_<N>_post_merge_regression_check_command: <command used>`

     **Step 5.7 — Mainline build sanity check (Progressive Widening Layer 3) ⭐ rev 1.17.7 NEW(PO 2026-06-23 catch #2 — project integration test pass ≠ full mainline build healthy):**
     ```bash
     # Layer 3 = wider sweep beyond project-scope integration test
     # Catches: (4) side-channel impact on OTHER features (not just project's own changes)
     #          (5) deployment env-dep surfaces (local Path A ceiling acknowledgment)
     # 
     # Sub-Layer 3a (zero-risk, always run): py_compile <project critical files>
     #   python3 -m py_compile <project's runtime *.py>
     # 
     # Sub-Layer 3b (low-risk): import project modules with safe-mode env
     #   <SAFE_MODE_ENV> python3 -c "import <project module>; print('Import OK')"
     #   (For backend-schema-auto-sync: SCHEMA_SYNC_MODE=disabled python3 -c "import schema_sync")
     # 
     # Sub-Layer 3c (requires deployment env vars OR project carve-out): full gunicorn cold start
     #   <SAFE_MODE_ENV + DEP_ENV_VARS> gunicorn --bind=127.0.0.1:<port> --timeout 30 --workers 1 \
     #     --pid /tmp/gunicorn-mainline-build.pid --log-file /tmp/gunicorn-mainline-build.log \
     #     --daemon app:app
     #   sleep 12  # cold start window
     # 
     # Sub-Layer 3d (depends on 3c): /health smoke test
     #   curl -s -o /tmp/health.body -w "%{http_code}" http://127.0.0.1:<port>/<endpoint per D2_health_check>
     #   expect: 200 + body matches expected (eg. "OK")
     ```
     **Coverage interpretation:**
     - **3a + 3b PASS** → enough for Phase 6 deploy gate unblock(proves no Phase 5/6 regression)→ proceed to Step 5.8
     - **3c + 3d blocked-by-env**(project's pre-existing local env limit — eg. missing `BOT_Manager_http_url` for LineBOT-style projects)→ log finding to `mainline_build_sanity_check.coverage: partial`,Path A 視為 partial pass,proceed to Step 5.8。**Acknowledges local Path A natural ceiling — Layer 4 Path B Azure staging needed for full verify**(⚠ **rev 1.17.9 update**:Layer 4 redefined as mainline pre-deploy sanity check via Pilot v0 LIFF test runner;staging E2E renumbered to **Layer 5**。"Layer 4 Path B Azure staging" 此處為 rev 1.17.7 historical context preserved per audit trail integrity)。
     - **3c FAIL with regression-shape stack trace**(syntax / import / new None-handling NOT from env)→ **REAL regression** → `git reset --hard ORIG_HEAD` + abort + state.md.current_phase stays N
     - **Distinguishing "blocked-by-env" vs "real regression"**:PO/PM judgment via stack trace inspection。Env-dep stack trace 通常 mentions specific env var (`os.environ.get('X')` returning None);regression 通常 mentions project's own .py files line numbers AND uses values that should always exist。
     - **Audit fields written**(rev 1.17.8 C2 fix — canonical verbose semantic names per impl alignment):
       - `phase_<N+1>_entry_gate.mainline_build_sanity_check.layer_3a_syntax_py_compile: pass | fail` + per-file evidence
       - `phase_<N+1>_entry_gate.mainline_build_sanity_check.layer_3b_safe_mode_project_imports: pass | fail` + import scope detail
       - `phase_<N+1>_entry_gate.mainline_build_sanity_check.layer_3c_full_gunicorn_cold_start: pass | blocked-by-env | fail` + crash_location/cause when blocked-by-env
       - `phase_<N+1>_entry_gate.mainline_build_sanity_check.layer_3d_health_smoke: pass | blocked-by-layer-3c | fail` + expected_endpoint
       - `phase_<N+1>_entry_gate.mainline_build_sanity_check.coverage: full | partial`
       - `phase_<N+1>_entry_gate.mainline_build_sanity_check.blocker_for_phase_<N+1>_deploy: true | false`
       - `phase_<N+1>_entry_gate.mainline_build_sanity_check.path_b_required: true | false`
       - `phase_<N+1>_entry_gate.mainline_build_sanity_check.finding: <text>`

     **Step 5.8 — Push + state transition(only after Step 5.5 AND Step 5.7 pass per their own criteria):**
     ```bash
     git push origin main
     # state.md update: current_phase: N → N+1 + phase_<N>_completed_at + main_merged_from: dev/<project>
     ```

     On success → state.md `worktree_branch: <kept until Phase 6 archive>` + `phase_<N+1>_started_at` set + `main_merged_from: dev/<project>` + `phase_<N>_post_merge_regression_check_*` audit fields + `phase_<N+1>_entry_gate.mainline_build_sanity_check.*` audit fields(canonical schema below)。Integration QA runs against newly-merged main per §F E2E。Worktree dir + branch NOT removed at Phase 5(留作 hotfix patch back per §F.6.1);Phase 6 archive 時才 cleanup(git worktree remove + branch -D)。

     > ⭐ **rev 1.17.8 C4 — canonical `mainline_build_sanity_check` schema(applies at BOTH top-level entry gate AND per-build-item nested,same field shape):**
     >
     > **Top-level entry gate context**(first event at phase transition merge):
     > ```yaml
     > state.md.phase_<N+1>_entry_gate.mainline_build_sanity_check:
     >   <canonical fields per Step 5.7 above>
     > ```
     >
     > **Per-build-item history context**(each F1/F2/etc. ongoing Phase N+ build merge):
     > ```yaml
     > state.md.phase_<N+1>_<feature_id>_<finding_slug>.layer_3_mainline_build_sanity_check:
     >   <SAME canonical fields per Step 5.7 above>
     > ```
     >
     > **Examples already in use**(backend-schema-auto-sync):
     > - `phase_6_entry_gate.mainline_build_sanity_check`(retroactive entry gate after f542888 advance-phase 6 merge)
     > - `phase_6_f1_engine_config_injection.layer_3_mainline_build_sanity_check`(F1 build merge df9dc8a per Progressive Widening scope extension)
     > - `phase_6_f2_cassl_disabled_typo_fix.layer_3_mainline_build_sanity_check`(F2 build merge 5a20d68 — same pattern)
     >
     > Both contexts use SAME canonical schema(C2 verbose semantic names per impl alignment)。Query tooling can `grep -r mainline_build_sanity_check state.md` to find all check events across project lifetime。
   - Phase 6 → release
   - Phase 7 → post-launch + retrospective
6. Append to `org-decision-log.md`:
   ```
   D-phase-advance-<project>-<seq>: project=<project> phase=<N-1>→<N> by=PO at=<ISO8601>
   ```

---

## Subcommand: signoff

**Arguments:** `phase-<N>` and `--approver <X>` (X = PO | boss | tech-lead).

**Workflow:**

0. **Apply mainline-forbidden guard**(rev 1.17.3 §E.8.8.2 — see Shared Guard section above)。Abort if active=mainline。
1. Read `state.md.phase_<N>_signoff_required_approvers` (typically `[PO, boss]` for major phases).
2. Verify gate-check has passed for phase-N (state.md.phase_<N>_gate_passed: true).
3. Update `state.md.phase_<N>_signoff.approvals.append({by: <X>, at: <ISO8601>})`.
4. If all required approvers signed → set `state.md.phase_<N>_signoff_complete: true`.
5. Output: which approvers still pending, or "Phase <N> fully signed off, ready for advance-phase <N+1>".

---

## Subcommand: gate-check(v2 — 2026-06-20 inline criteria + v1↔v2 dispatcher)

**Arguments:** `<phase>` (eg. `phase-0` or `phase-4`).

**Workflow:**

0. **Apply mainline-forbidden guard**(rev 1.17.3 §E.8.8.2 — see Shared Guard section above)。Abort if active=mainline。
1. Resolve active project.

2. **Contract version dispatcher**(對齊 §6.4.16 SDLC v2 migration policy):
   - Read `state.md.sdlc_contract_version`(若 unset:check `phase_2_signoff`,past=v1 grandfather / not-past=v2 default)
   - For phases 0/1/2 → criteria list 依 contract version 選 v1 vs v2(below)
   - For phases 3-7 → 同 v1(unchanged)

3. Read appropriate contract:

   **v2 (default for new + Phase 0/1 in-progress projects, canonical = §6.4.16):**
   - **phase-0**(v2 — bootstrap PM only,9 criteria):
     - C1: Requirement spec authored(≥ 500 行 + 11 必填欄位 per REQ,含 golden_scenario + anti_examples 三元組;triad completeness **依 §6.4.10 §G step 3 schema_version 分流 —— 唯 `req-spec-v1.1` triad required(缺項無 `[GAP]` → fail);其餘一切(`req-spec-v1` / `enhanced-v1` 等)grandfather warn**,對齊 requirement-spec-authoring-rules.md §3)
     - C2: Glossary ≥ 7 terms
     - C3: Out of Scope ≥ 3 items
     - C4: Assumptions ≥ 2 items(memory-inject)
     - C5: Constraints ≥ 2 items(memory-inject)
     - C6: **Bootstrap PM only** ⭐(team-roster.md has invoker as PM with primary_role=PM;`coverage_status` ∈ `{bootstrap-only, complete}`;**no MVT 3-role enforce**)
     - C7: spectra-review pass
     - C8: PO 拍板 spec ship-as-is
     - C9: `phase_0_signoff = true`(signed off by final_approver)
   - **phase-1**(v2 — 9 criteria,對齊 §6.4.16 Phase 1 Exit Check List):
     - C1: Step 1.1 module split locked(`state.md.modules[]` populated)
     - C2: Step 1.1 `<project>-modules-overview.md` authored(HUMAN-FIRST 3-role per module:📋 What it does + 👔 PM + 🔬 QA + 💻 Developer)— 對齊 memory `feedback_human_first_docs`
     - C3: Step 1.2 team-roster.md v2 schema + **MVT 3-role coverage pass**(現在才 enforce)
     - C4: Step 1.3 every `modules[].owner` populated
     - C5: Step 1.4 functional spec authored per module(`<project>-<module>-functional-spec.md`)— 同 3-role 結構
     - C6: Step 1.5 design spec authored per module(D-035:恆寫,不 skip;`risk_level=low` = floor 深度而非省略)
     - C7: 每個 Phase 0 REQ 被 ≥ 1 module 覆蓋(`modules[].covers_reqs` union = all REQs)
     - C8: Dependency graph 無 circular
     - C9: `phase_1_signoff = true`
   - **phase-2**(v2 — plan.md only + solo carve-out):
     - C1: Per-module `<project>-<module>-plan.md`(task breakdown + timeline + risk)
     - C2: Solo carve-out:若 `state.md.phase_2_collapsed_into_phase_1 = true`(PO override + log)→ skip per-module plan check
     - C3: `phase_2_signoff = true`

   **v1 (grandfather only — projects past Phase 2 signoff):**
   - phase-0 → §6.4.10 §B.1-B.5 + §K Exit Check List(v1 — includes MVT 3-role check)
   - phase-1 → §6.4.11 §B.3 + §B.7(v1 — `_plan.md` + validate-module-plan + REQ coverage + dep graph + signoff)
   - phase-2 → §6.4.11 §C.4 + §C.7(v1 — 3 specs per module R/F/P)

   **All versions(unchanged for phase 3-7):**
   - phase-3 → §6.4.11 §D.2 + §D.5
   - phase-4 → §6.4.11 §E.4 + §E.4a (Flaky Policy) + §E.7 + **§E.3 coverage criterion(C1):gate-check 實跑 `python3 scripts/pm_coverage_validator.py --all`(即 `/pm validate-coverage`),**exit ≠ 0 → ❌ 卡 gate**;檢 feature↔TC:每 done feature ≥1 TC = HARD、orphan TC = warn、format-mismatch(檔非空卻 0 parse)= HARD 存疑**
   - phase-5 → §6.4.11 §F.3 + §F.5
   - phase-6 → §6.4.11 §G.3 + §G.5
   - phase-7 → §6.4.11 §H.4 + §H.6

4. For each criterion, check the corresponding file/state and report ✅ / 🟡 deferred-non-blocking / ❌.
5. **Output format(v2 — 2026-06-20 加 traceability):**
   - 表 columns:`# | Criterion (§ ref) | State | Verdict`
   - 若 `phase_<N>_signoff = true` 已 set,banner:`(already signed off — re-running for audit)`
   - 若 contract version=v2 用過 v1 grandfather:banner:`(v1 grandfather mode)`
6. If any ❌ → output verdict "NOT ready" + actionable fix list(明示哪個 Step 該補哪 file)。
7. If all ✅(or 🟡 non-blocking only)→ output "Ready for signoff. Run `/pm signoff phase-<N> --approver PO`"。

**Confidence Tier:** 🟢 high(v2 — file/state checks deterministic + criteria explicit inline)

---

## Subcommand: daily

**Arguments:** none (auto-resolves active project + all active projects per scenario 12).

**Workflow:**

1. Read all `docs/pm/*/state.md` (active projects only).
2. For each, compute:
   - Overall progress (done / in-progress / planned features from functional.md status counts)
   - Team status (per-engineer commit rate, blocked count)
   - Anomalies (spec↔code↔test sync per §6.4.11 §E.3a invariant checks)
   - Flaky test watch (per-module + project totals per §E.4a)
   - Mid-flight REQ tracking (Phase 0 frozen Override entries from decision-log)
3. Generate Top-3 actions per §6.4.8 Fix Recommendation Algorithm.
4. Output matches manual scene 6a + scenes 5b/15 cross-references (blocker / mid-flight tracking).
5. Write the briefing to `docs/pm/<active-project>/reports/<date>-daily.md` (append-only).
6. **Auto Behavior Confidence Tier** (per manual rev 1.6 prefix): All auto-detected anomalies at medium tier; fallback = list raw evidence + ask PO. Never silent fail.

---

## Subcommand: dashboard

**Arguments:** none.

**Workflow:**

1. Scan `docs/pm/*/state.md` (skip `_org`, `_archive`).
2. For each, summarize: phase / day-progress / burndown / health (anomaly count).
3. Cross-project anomaly detection:
   - Resource conflict: engineer assigned in multiple projects with overlapping commit windows.
   - Common pattern: identical issue descriptions in ≥ 2 projects' decision-logs (LLM compare).
   - Best practice cross-pollination: high-value retrospective from project A applicable to project B's current phase.
4. Cross-project KPI rollup (per §7.5 三層 KPI).
5. Today's Top-3 actions.
6. Output format: see manual scene 12 lines 1131-1158.

**Confidence:** medium tier; common pattern detection is LLM-based, may have false positives. Always cite source decision-log entries for human verification.

---

## Subcommand: archive

**Arguments:** `"<project>"` or `--filter <pattern>` with `--confirm`. `[--reason "..."]`.

**Workflow:**

0. **rev 1.17.3 — mainline-archive guard:** If target is `mainline` → abort: `"mainline cannot be archived (perpetual_maintenance per rev 1.17.3 §E.8.8.2). It's a system reserved project, not a user-managed project."` Also: if active project (per active-project.txt) is mainline AND no `<project>` arg given → abort with same message。
1. Resolve target(s):
   - Single: verify `docs/pm/<project>/state.md` exists.
   - Bulk `--filter`: list matching projects; require `--confirm` flag + show match list before proceeding.
   - **Bulk 0-match guard(對齊 Round 2 N2 fix):** if `--filter` matches 0 projects → output "No projects match pattern `<pattern>`. Run `/pm list` to see available." and return (no abort error, no mutate).
2. Verify project is not in Phase 4+ (active development). If yes → abort: "Phase 4+ active project. Run §10.7 stop loss first."
3. If `state.md.project_type == production` → require `--reason` (non-empty).
4. Move `docs/pm/<project>/` → `docs/pm/_archive/<project>/`.
5. Also move `docs/modules/<project>/` and `docs/reviews/<project>/` to archive subfolders.
6. Append to `docs/pm/_org/org-decision-log.md`:
   ```
   D-archive-<seq>: project=<project> reason="<reason>" by=PO at=<ISO8601>
   ```
7. Set 7-day restore grace period: write `docs/pm/_archive/<project>/_archived-at.txt` with ISO8601.
8. **rev 1.17.3 — auto-switch to mainline on archive(對齊 §E.8.8.3):**
   - If active project was archived → update `active-project.txt` → `"mainline"`(was: clear to empty)
   - Echo:
     ```
     Project <project> archived.
     Active project switched to mainline (rev 1.17.3 §E.8.8.3).
     You're now on main branch (CWD: <main repo dir>).
     Worktree dir ../<project>/ cleanup pending (run `git worktree prune`).
     ```
   - Append `D-pm-switch-to-mainline-auto-<id>: trigger=archive_<project>` to org-decision-log.
9. **rev 1.17.12 — sanity eruda log auto-wipe(對齊 sanity-check REQ-017 G.1):**
   - Query `Sanity_Eruda_Log_TBL` rows count for `<project>`
   - 若 count = 0 → skip Step 9(no-op,echo "No eruda logs to wipe")
   - 若 count > 0 → **no-prompt chunked DELETE**(archive = decision finalized,對齊 `[[delete_dialog_no_undo_hint]]` archive ≠ soft delete invariant):
     - Chunk size 1000 rows / 100ms sleep gap(對齊 sanity REQ-017 R-NEW-F mitigation)
     - SQL transaction:`DELETE FROM Sanity_Eruda_Log_TBL WHERE project_name = '<project>'`
   - Write `Sanity_Lifecycle_Audit_TBL` audit row(對齊 sanity REQ-017 G.5):
     - `action='archive'` / `executed_by='pm-skill-caller:<user>'`(per REQ-017 G.5 normative format `<source-type>:<source-id>`)/ `rows_affected=<count>` / `bytes_freed=<sum>` / `executed_at=<now>`
   - Update `Sanity_Test_Result_TBL.eruda_log_wiped_at = NOW()` WHERE project_name = '<project>' AND eruda_log_wiped_at IS NULL(transparency 標記 per REQ-017 G.4)
   - Echo:
     ```
     Auto-wiped <N> eruda logs for <project> (<M> bytes freed) as part of archive.
     Sanity_Lifecycle_Audit_TBL audit row written.
     ```

**Confidence:** 🟢 high(file move + write deterministic + auto-switch deterministic + sanity wipe transaction-bounded);🟡 medium for bulk filter match recommendation(LLM-suggested patterns may have false positives → always list match preview before mutate)

---

## Subcommand: restore

**Arguments:** `"<project>"`.

**Workflow:**

0. **rev 1.17.3 — mainline-restore guard:** If target is `mainline` → abort: `"mainline cannot be restored (perpetual_maintenance — never archives per rev 1.17.3 §E.8.8.2)."`
1. Verify `docs/pm/_archive/<project>/_archived-at.txt` exists.
2. Compute days since archive. If > 7 → check `_archive/_cold/` (long-term archive). If still present, allow restore but warn user about staleness.
3. Move `docs/pm/_archive/<project>/` → `docs/pm/<project>/`.
4. Restore modules / reviews subfolders symmetrically.
5. Append audit entry to `org-decision-log.md`.
6. Suggest user run `/pm use <project>` if they want to switch context.
7. **rev 1.17.12 — eruda wipe history warning(對齊 sanity-check REQ-017 G.4 transparency invariant + Round 1 C-pm-1 fix):**
   - Query `SELECT MAX(eruda_log_wiped_at) FROM Sanity_Test_Result_TBL WHERE project_name = '<project>' AND eruda_log_wiped_at IS NOT NULL`
   - 若有 wipe history → display warning:
     ```
     ⚠ Note: eruda logs prior to <archive_date> were wiped during /pm archive.
       New sanity runs will capture fresh logs;
       historical logs unrecoverable unless export was taken
       via /pm sanity-export-logs <project> before archive.
     ```
   - **不 reverse** — 對齊 [[delete_dialog_no_undo_hint]] 慎思 invariant(once wiped, gone forever)
   - 若 null(從未 wipe) → skip warning(no-op)

---

## Subcommand: delete

**Arguments:** `"<project>"` (or `--filter <pattern>`), `--force`, `--reason "..."`.

**Workflow:**

1. Verify `--force` flag present (mandatory).
2. Verify `--reason` non-empty.
3. Check `state.md.project_type`:
   - `production`: also require `git log --since='7 days ago' -- docs/pm/<project>/` returns 0 commits. If recent commits → abort: "Recent activity detected. Re-confirm with explicit override clause in --reason."
   - `training`/`sandbox`: skip extra check.
   - `poc`: warn but allow.
4. For bulk `--filter`:
   - List matched projects.
   - Output: "About to PERMANENTLY DELETE the following projects: <list>. Continue? (yes/no)".
   - Wait for explicit "yes".
5. Append to `org-decision-log.md` BEFORE deleting (audit trail must survive delete):
   ```
   D-delete-<seq>: project=<project> reason="<reason>" by=PO at=<ISO8601>
   ```
6. `rm -rf docs/pm/<project>/`, `docs/modules/<project>/`, `docs/reviews/<project>/`.
7. If active project was deleted → clear `active-project.txt`.
8. Output: "Deleted. Audit entry preserved in `_org/org-decision-log.md` D-delete-<seq>."

**Confidence:** 🟢 high(file delete + audit deterministic);🔴 low for `--force` override decision when production type with recent commits — refuse to conclude;require explicit override clause in --reason per `references/lifecycle-policy.md` "Special rule (production overlay)"

---

## Subcommand: onboard

Per manual scene 13. Workflow:

1. Read `docs/pm/<project>/team-roster.md` (verify `--replace-for` engineer is current owner of `--module`).
2. Generate personalized onboarding pack (6 sections per scene 13):
   - 必讀清單 (~2 hours): requirement.md / functional.md / decision-log / departing engineer's last commits / flaky tests / cross_cutting_reqs
   - Unresolved items relevant to new engineer
   - Contacts (PO / Tech Lead / cross-module peers from team-roster)
   - Day 1-3 path
   - Memory + org knowledge inject (LDAP / domain etc.)
   - System auto-update (team-roster + _plan.md + decision-log)
3. Update `team-roster.md`: add new engineer + mark departing as `transferring`.
4. Update `_plan.md`: `<module>.owner: <old> → <new>` with effective date.
5. Append audit entry.

---

## Subcommand: offboard

Per manual scene 13. Workflow:

1. Run handover check (three-way invariant per §6.4.11 §E.3a):
   - functional.md no stale
   - execution_log present for all done features
   - actual_completion filled
   - tests.md flaky markers + revisit_at set
2. **Half-done feature handover** (per Round 3 N2 fix):
   - For status='🟡 in-progress' features:
     - Auto-split execution_log: completed vs pending acceptance
     - Context dump: push WIP branch as `wip/<feature>-acc-handover`
     - Knowledge points (required, free-text): "我寫到哪 / 下一步該怎做 / 我擔心的點"
   - Auto-append to successor's onboarding pack `unresolved` section.
3. Update team-roster: engineer status `active → transferring → moved`.
4. Append audit entry.

---

## Shared: Triad Authoring Behavior（三元組 authoring — 所有 REQ CRUD subcommand 共用）

> **SSOT:** `docs/pm/spec-authoring/requirement-spec-authoring-rules.md §5`。
> **Applies to:** `start`(Phase 0)/ `new-requirement` / `requirement add-mid-phase` / `requirement modify`(全兩步)/ `requirement split`(每子 REQ — **僅 Triad Auto-Completion**,Coverage Expansion 不強制,避免拆分時 scope creep)。
>
> **3-Phase REQ Authoring Pipeline（P3c — 本 §Shared 是中段;前後兩關見 rulebook）:**
> 1. **【前】§2.5 Requirement Admission Gate** — 候選需求先過 5-test(可追溯/有證據/值得寫/是what非how/有必要);沒過 → Open Questions / Out of Scope;過了才進 authoring
> 2. **【中】本 §Shared** — Triad Auto-Completion + Coverage Expansion(下述)
> 3. **【後】§5.5 Write-time 3-Role Async Sign-off** — 三元組齊、寫入 spec 前,async per-REQ 👔PM/🔬QA/💻Dev sign-off,**有人決定就走**;verdict append 成 REQ 註記(無 terminal,可修/救回);high-stakes floor;solo=collapse 1 張

當 create / update / delete 某 REQ 的三元組任一元素(REQ / golden_scenario / anti_examples）時,依序執行:

1. **Triad Auto-Completion — conditional 2-step 確認（D-036 修訂 D-008;rulebook §5.2 SSOT）** — 人給錨點,Claude 精煉 description(`Statement`)+ 草擬 `Why`(pain point)+ 缺的三元組:
   - 入口 REQ → 草擬 golden_scenario + anti_examples
   - 入口 golden → 草擬 REQ + anti_examples;入口 anti → 草擬 REQ + golden
   - **conditional 2-step 確認(D-036 修訂 D-008「整組一次」):** ★step-1 描述確認(僅 `Statement` 有實質改寫時,顯 diff)→ [sizing gate §7 SPL-1,裝不下則拆]→ ★step-2 三元組 batch 一次確認;缺項可不附但需**二次確認** + `[GAP]` 標記(§5.3)。**「多筆變更 batch 一次列全」保留**(供步驟 2 + split 多子 REQ)。
2. **Coverage Expansion（舉一反三,§5.4 定序在三元組確認之後）** — Claude 依全面視野列 **~3 個(總數,非每類 3)** 相鄰/隱含候選(sibling REQ / 額外 scenario / 額外 anti),**逐一**討論 add/mod/del(D-011);proposal-only + grounded 防 gold-plating。**「所有 mode 強制」= 對「一條 authoring 中的需求」強制展開一次;⚠️ 當觸發源是 `requirement split` 時,拆分不自動觸發舉一反三**(§Applies-to line + rulebook §7 scope-creep guard,D-036 C2-R2)。
3. 採納候選 → 回步驟 1 補其完整三元組 → 寫入 spec(11 欄位 §6.4.10 §B.4)

**Mode note:** discuss(V1/V6)先 conditional 2-step popup 後動檔;execute(V2/V4)直接 write-time(per-REQ `Why` 維持 optional,無 regression);delete 一律 PO-confirm。**觸發邊界(D-036 §5.1):ceremony 僅在討論收斂到「要 author/改此 REQ」時啟動,探索/一般討論不觸發。**

---

## Subcommand: new-requirement

Per manual scene 15. Workflow:

1. Atomize description → atomic REQs (LLM, schema §6.4.10 §B.4 — 11 欄位含三元組).
1.3. **【P3c 前關】Admission Gate** — 對每個 atomic 候選跑 **rulebook §2.5 五項准入測試**;沒過 → Open Questions(T1/T2)/ Out of Scope(T3/T5)/ 反推 what(T4);T3 carve-out=安全·資料·法遵;PO 可 override(記 log)。過閘門才續;T3 定 priority。
1.5. **Triad authoring** — 對每個過閘門的 REQ 跑 **§Shared: Triad Authoring Behavior**(Auto-Completion 補 golden_scenario + anti_examples + Coverage Expansion 舉一反三 ~3 相鄰候選逐一討論;新候選同樣先過 §2.5).
2. Module-fit analysis: compare to existing modules in `_plan.md`; recommend Option A (extend existing) vs Option B (create new module). Provide trade-offs.
3. Capacity check (per Round 3 C1 fix — evidence-based, not star ratings):
   - For each candidate engineer: list git log domain keyword hits + current workload from functional.md.
   - Recommend assignment + pair suggestion if domain gap.
4. Timeline impact with confidence intervals (per §Auto Behavior Confidence Tier, medium tier).
5. Contract Override check (§6.4.10 §L): if Phase 0 frozen broken → require PO ack with audit.
5.5. **【P3c 後關】Write-time 3-Role Sign-off** — 每個三元組齊的 REQ 寫入前跑 **rulebook §5.5**:async per-REQ 👔PM/🔬QA/💻Dev sign-off,**有人決定就走**(其餘 advisory → `/pm requirement modify`);`team_size==1` collapse;high-stakes floor;verdict append 成 REQ 註記(reject→Out of Scope 不刪 + revivable);匯總進 signoff 證據。
6. On PO approval, update: Requirement Spec (rev increment) + _plan.md + functional.md + decision-log.
7. Notify affected engineers (write to their pending action list).

---

## Subcommand: contract-change propose

Per manual scene 14. Workflow:

1. Wizard prompt for changes (interactive or via --changes flag).
2. Classify each: patch / minor / major per §6.4.13.
3. Impact analysis: scan all `docs/pm/*/state.md` for active projects affected.
4. Generate 12-week deprecation timeline (Week 0 ack / Week 1-4 migration / Week 5-12 cohabit / Week 12 EOL).
5. For each project: generate migration PR draft (best-effort, medium confidence — list manual fallback if auto fails).
6. Per-project `active_contract_version` in state.md updated when project migrates.
7. Write to `docs/pm/_org/contract-pack/<contract>-v<X>.md` + audit `org-decision-log`.

---

## Subcommand: bootstrap-project(new in v1.0.2,對齊 onboarding 兩階段 setup)

**Use case:** 新工程師 clone repo 後跑 `./setup.sh`(Phase 1 minimal)完,開 Claude Code 跑此命令(Phase 2 智能裝)。

**Arguments:**
- `--scope <minimal|standard|full>` 預設 `standard`(對齊 `infra-deps.yaml` scopes 段)
- `--unattended` 全 user_choice 取 default,no prompt(CI 友善)
- `--resume-from <step-name>` 從上次失敗步驟接續(對齊 audit recoverability)

**Workflow:**

### Step 1: 讀 deps spec

讀 `skills/pm-skill/references/infra-deps.yaml`(對齊 §6.4.10 §B.3 machine-readability)。

**Schema version 處理**(對齊 Round 3 N3 fix:forward-compat):

| yaml schema_version | SKILL 行為 |
|:---|:---|
| `infra-deps-v1`(SKILL 已知) | ✅ 正常處理 |
| `infra-deps-v0` 或更舊 | ⚠ 警告 + abort 提示 user 升 yaml |
| `infra-deps-v2` 或更新 | ⚠ 警告「SKILL 較舊,可能 missing 新 field」+ 退回 v1 sub-set fields 處理(best-effort) |
| 缺欄位 / 格式錯 | ❌ abort 提示具體 yaml line + 修法 |

### Step 2: 偵測平台 + 既有狀態

```bash
# Platform detection
case "$(uname -s)" in Linux*) PLATFORM=linux;; Darwin*) PLATFORM=macos;; *) abort;; esac

# 對 system[] 每項跑 verify command
# 已 installed → mark ✅ done
# 未 installed → mark ⏳ pending
```

### Step 3: Resume check(對齊 audit recoverability + Round 2 C3 fix:per-machine path)

讀 **per-machine local** install history(對齊 Round 2 C3 fix — install history 是 per-engineer-machine,不入 git):

```
~/.cache/pm-skill/install-history.md
```

(不存在則 `mkdir -p ~/.cache/pm-skill/` + 建立空 file)

Entries 格式(對齊 Round 2 N3 fix — step name 可枚舉):

```markdown
- step=system.python3 status=done at=2026-06-18T10:23:00Z platform=linux choice=apt
- step=system.mysql status=done at=... choice=docker
- step=python.primary status=fail at=... reason="pip 沒裝"
```

**Step name reference**(可用值,對齊 infra-deps.yaml 各 node):
- `system.python3` / `system.mysql` / `system.nodejs` / `system.docker`
- `python.primary` / `python.dev`
- `services.mysql_schema_init`
- `verify`(Step 9 整體)

**如果 `--resume-from <step-name>`:** skip 已 `done` 的 step,從指定 step 開始(用上述 dotted name)
**預設行為:** skip 全部 `done`,執行 `pending` / `fail`

### Step 4: Sudo cache check(對齊 PO 2026-06-18 拍板 Path B sudo handling)

**Confidence Tier: 🔴 low(password capture)**(對齊 Round 2 C2 fix)— SKILL **絕不可** 嘗試擷取 / 推測 / log password;Path B 模式 user 自行 terminal 輸入是**唯一合法路徑**。任何「自動處理 sudo password」邏輯都是 security violation。

**3 branches**(對齊 Round 3 C3 fix:加 no-sudo environment branch):

```bash
# Branch 0: 偵測 sudo 命令是否存在
if ! command -v sudo >/dev/null 2>&1; then
  GOTO: Branch C (no-sudo environment)
fi

# Branch detect:有 sudo 命令 → check cache
sudo -n true 2>/dev/null
```

- **Branch A(exit 0,passwordless cache OK)→** 進 Step 5 直接跑 sudo 命令

- **Branch B(exit non-zero,有 sudo 命令但需 password)→** 輸出 prompt:

  ```
  🔐 Sudo required for system-level installs.

  Some packages(python3-dev / mysql-server / etc)need sudo.
  Please run in your terminal NOW(caches your password for 15 min):

     sudo -v

  Then reply 'continue' to proceed,or 'skip' to bypass sudo steps,or 'abort' to stop.
  ```

  Wait for user reply(use **AskUserQuestion** tool 對齊 §6.4 Trust Hierarchy「PO override」精神):
  - `continue` → re-test `sudo -n true` after 5 sec,進 Step 5
  - `skip` → mark all `sudo_required: true` steps as skipped,append history
  - `abort` → exit with state preserved in install-history

- **Branch C(no sudo command / not in sudoers — eg. corporate shared host / Docker non-root container)→** 輸出:

  ```
  ⚠ 偵測到無 sudo 環境(命令不存在 OR user not in sudoers)

  自動 fallback:
    - 跳過所有 sudo_required: true 的 steps
    - 改建議 user-local install path:
      • python.isolation: venv(本機 venv,no sudo)
      • system.mysql: docker(若 Docker 可用) OR external(用既有外部 MySQL)
      • scope 改 minimal(只 verify 既有 Python3)

  建議跑:
    /pm bootstrap-project --scope minimal --unattended
  或:
    /pm bootstrap-project --scope standard
    (Claude 會自動 skip sudo steps + 改 user-local)

  reply 'continue' to proceed in no-sudo mode,or 'abort' to stop.
  ```

  - `continue` → mark sudo_required steps as skipped,改 user_choice 預設值為 venv/docker/external,進 Step 5
  - `abort` → exit

**重要:** **永不存 password / 永不 log sudo prompt content**(security per §Out of Scope)

### Step 5: User choice prompts(scope `standard`/`full` only)

對 `infra-deps.yaml` `system[]` 中含 `user_choice` 的項(如 mysql),用 AskUserQuestion 互動詢問:

```
🤔 MySQL install method?
  [a] Local install(預設 — 本機 dev 最常見)
  [b] Docker container(乾淨隔離 — 推薦對齊 Phase 3 試跑)
  [c] External(skip install,用既有外部 MySQL)
```

**若 `--unattended`:** 取 `scopes.<scope>.user_choice_defaults` 預設值,no prompt。

### Step 6: Execute install per choice

For each pending item:

1. 輸出 current step + 即將跑的 command
2. 用 Bash tool 跑 install command(對齊 Confidence Tier:🟢 high — deterministic apt/pip install)
3. **長跑命令**(eg. `pip install -r requirements.txt`): use `run_in_background: true`,完成通知接續
4. **Sudo 命令** 若 cache 過期 → 回 Step 4 重新請求
5. **失敗 handling:**
   - **transient fail(network)**:auto retry 1 次
   - **persistent fail**:診斷 + 給 user 選項:retry / skip / abort
6. **Success** → append history to **`~/.cache/pm-skill/install-history.md`**(對齊 Round 2 C3 fix — per-machine):`- step=<dotted.name> status=done at=<ISO> platform=<X> choice=<id>`

**Confidence Tier per step:**
- 🟢 high: file existence,verify commands,deterministic apt/pip/brew
- 🟡 medium: choosing install method per user_choice(LLM picks default for unattended);diagnose retry decision
- 🔴 low: never silent-retry destructive commands(drop database / overwrite credential file)— always 確認 PO

### Step 7: Post-install services(對齊 `services[]` section)

對每個 service entry(eg. `mysql_schema_init`):

1. Check `depends_on` 全 done
2. 跑 commands(若需 sudo,對齊 Step 4 cache)
3. 失敗給具體 fix path

### Step 8: Credentials verification(NOT auto-install,security boundary)

對 `credentials[]` 每項:

- `auto_action: verify_presence_only` → check file 在 `location` 存在(只 check 檔名,**never read content / log content**)
- `auto_action: prompt_user_to_set` → 提示「請設環境變數 `<name>`」+ 提供 `~/.bashrc` 加法範例 + 「設完跑 source ~/.bashrc」
- 輸出全 credentials checklist(✅ found / ⚠ missing / 🔐 manual setup needed)

**Sensitivity HIGH boundary**(對齊 Round 2 N2 fix):若 `sensitivity: HIGH`,SKILL **永不可** echo / log:
- 檔案 path(只 ✅ 存在 / ⚠ 缺失,不顯路徑)
- 檔案 metadata(size / mtime / owner)
- 環境變數 value(只 ✅ set / ⚠ unset,不顯內容)

**不主動 fix credentials**(對齊 §6.4 Trust Hierarchy:credentials 是 per-engineer secret 不屬 SKILL 邊界)。

### Step 9: Final verification(跑 `verify_targets[]`)

對每 verify_target 跑 command + match `expected_pattern`:

```
✅ python3 -c 'import flask; print(flask.__version__)' → 3.0.0
✅ mysql -u root -e 'SELECT 1;' → 1
✅ claude --version → 0.6.3
✅ gh auth status → Logged in to github.com as kuohsuming
```

**Optional verify skip rule(對齊 Round 2 C4 fix):**
若 `verify_target.optional: true` 且該 dep 在 Step 5 user_choice 被 skip(eg. mysql `choice: external`)→ 該 verify 標 `⏸ skipped(per user choice)`,**不計入 fail count**:

```
⏸ mysql -u root -e 'SELECT 1;' → skipped(user chose external MySQL,not local install)
```

**全 pass + skipped → Step 10**;**任何 required fail → 輸出 on_fail message + skip / fix-and-retry / abort 選項**

### Step 10: Output summary + next steps

```
🎉 Environment bootstrap complete(scope: <X>)

Installed:
  ✅ python3 3.11
  ✅ mysql 8.0(via Docker)
  ✅ nodejs 20.x
  ✅ Flask + SQLAlchemy + LINE SDK(via venv)

Skipped:
  ⏸ system_pip(per your choice → venv 使用)
  ⏸ requirements-dev.txt(per --scope standard,選 full 加上)

Pending manual:
  🔐 GCP service account JSONs → 跟 admin 拿(對齊 .gitignore 已排)
  🔐 LINE_CHANNEL_SECRET → 設環境變數

Audit:
  📜 install history → docs/pm/_org/install-history.md

Next:
  /pm init "test-onboarding" --type sandbox   # 試跑 PM Skill
  /pm dashboard                                # 看 active projects
  source .venv/bin/activate                    # 每次 new terminal 跑 Python 前
```

### Step 11: Audit(對齊 Round 2 C3 fix — per-machine cache + org summary 分離)

兩個 audit destinations:

1. **Per-machine local(完整細節,不入 git):**
   - `~/.cache/pm-skill/install-history.md`(對齊 Step 3 / Step 6 path)
   - 含所有 step + choice + retry + timing

2. **Org-level summary(完成狀態,可入 git):**
   - `docs/pm/_org/org-decision-log.md` 加一筆:
     ```
     D-bootstrap-<seq>: scope=<X> by=<user> at=<ISO> result=success steps_done=<N>
     ```
   - **不含**: machine config / username / paths / choice details(隱私 + 跨 machine 無意義)

---

**Sudo handling note**(對齊 PO 拍板 Path B):
- Claude **never** prompts user for password in chat(security — password 不入 LLM context)
- Claude **never** runs `sudo --stdin` or similar bypass
- Always 對齊 §gh auth login 模式:user 在 own terminal 跑 `sudo -v`,Claude wait + continue

**Confidence Tier overall:** 🟡 medium(整體 workflow 含 LLM 判斷 + user choice;每 step 個別 tier 已標)

**Fallback if all fail:** 提示 user 改用 manual install 對齊 `infra-deps.yaml` 手動跑各 command;保留 install-history.md 供他人接力。

---

## Subcommand: push-gate(new in v1.2 — Stage 1 push enforcement)

> 對齊 proposal §6.4.11 §E.8.4 + §E.3a 三向 invariant。「告一段落 + 會動」才能 push 到 team worktree(或 single-PO solo 也用)。

**Trigger:**
- Manual:`/pm push-gate`
- Auto:git pre-push hook(對齊 §E.8.5 範例)

**Arguments:** none(SKILL auto-detect scope from `git diff`)

**Workflow:**

1. **Resolve active project** per §Active Project Context Detection.

2. **Detect changed files** since last push:
   ```bash
   git diff --name-only @{push}..HEAD 2>/dev/null \
     || git diff --name-only HEAD~1..HEAD
   ```
   Filter for `*.py | *.js | *.html | *.css | *.md | *.sql`.

3. **Infer module(s) touched** from changed file paths:
   - Read `docs/pm/<project>/state.md.modules[]` for path mapping(若有)
   - Fallback:grep path 前綴 against `docs/modules/<name>/`

4. **Run 10 checks per module touched**(對齊 §E.8.4 + rev 1.17.3 §E.8.8.6 check 10):

   **Invariant subset (對齊 §E.3a 6 條):**

   | # | Check | 命令 |
   |:---:|:---|:---|
   | 1 | `every_feature_has_code_commit` | `for fid in $(yq '.features[] \| select(.status=="done") \| .id' functional.md); do git log --grep="$fid" --oneline \| wc -l; done` 必 ≥ 1 |
   | 2 | `every_feature_has_test_case` | `yq '.test_cases[] \| select(.derived_from_acceptance \| contains("<fid>"))' tests.md` count ≥ 1 |
   | 3 | `every_test_case_has_result` | 對 tests.md 每 TC,test-results.md 必有對應 run |
   | 4 | `execution_log_per_done_feature` | `yq '.features[] \| select(.id=="<fid>") \| .execution_log \| length'` ≥ 1 |
   | 5 | `actual_completion_filled` | done feature `actual_completion` ≠ null |
   | 6 | `no_stale_functional_md` | `stat -c %Y functional.md` ≥ `git log -1 --format=%ct -- <module-path>` |

   **Push-gate 專屬 3 條:**

   | # | Check | 命令 |
   |:---:|:---|:---|
   | 7 | `lint_pass` | `bash lint.sh`(對齊 memory `backend_lint_workflow`)exit 0 + F821/F 不增 baseline |
   | 8 | `no_uncommitted_changes` | `[ "$(git status --porcelain \| wc -l)" -eq 0 ]` |
   | 9 | `functional_md_updated` | 若 changed files 含 `*.py` / `*.js` 對應 feature → `git diff --name-only HEAD \| grep functional.md` 必有 |
   | **10** | **`active_project_alignment`** (rev 1.17.3 §E.8.8.6) | Read `docs/pm/active-project.txt`; determine expected branch + CWD per §E.8.8.1 routing; verify `git branch --show-current` AND `pwd` match。If mismatch → fail + suggest `cd <expected>` OR `git checkout <expected>` OR override via `CONFIRM PUSH MISMATCH` |

5. **Aggregate results:**
   - All ✅ → output `pass`,allow push
   - Any ❌ → output `fail` + per-check fix suggestion + exit 1(若 hook 模式)

6. **Audit(per push)** — append to `docs/pm/reports/<YYYY-MM-DD>-daily.md`:
   ```markdown
   ## Push Gate Results
   
   - 2026-06-18 14:32 | module=identity | verdict=pass | checks=10/10 | commit=<sha> | by=<engineer>
   ```
   若 daily report 不存在,SKILL 先建空檔加 frontmatter(對齊既有 daily template)。

7. **Output format example:**
   ```
   🚪 /pm push-gate — module: identity(changed: app.py, friend_identity.js, functional.md)
   
   Invariant subset(§E.3a):
     1️⃣ every_feature_has_code_commit       ✅
     2️⃣ every_feature_has_test_case          ✅
     3️⃣ every_test_case_has_result           ❌ TC-identity-005 missing run result
     4️⃣ execution_log_per_done_feature       ✅
     5️⃣ actual_completion_filled             ✅
     6️⃣ no_stale_functional_md               ✅
   
   Push-gate 專屬:
     7️⃣ lint_pass                            ✅ (ruff 0 / mypy baseline 不增)
     8️⃣ no_uncommitted_changes               ✅
     9️⃣ functional_md_updated                ✅
   
   Verdict: ❌ FAIL (1/9 check failed)
   
   Fix actionable:
     - TC-identity-005:跑 pytest tests/test_identity.py::test_005,
       append result to docs/modules/identity/test-results.md
   
   Emergency bypass(對齊 §K.4 — PO ack 必填):
     git push --no-verify
     
     ⚠ Bypass self-audit(對齊 spectra v1.1.8 Round 1 C6 fix + §K.9 metric source):
       1. `--no-verify` 是 push flag,不留 commit message trace
       2. Engineer 必 manually:
          a. /pm validate-discipline-invariant(audit lineage)
          b. /pm-bug-review <slug>(紀錄 emergency context + 24h root cause)
       3. K.9 metric source 優先序:
          state.md `discipline_overrides[]` (deterministic) >
          commit message grep (best-effort) >
          hook log absence (proxy)
       4. Phase 7 retrospective 是 ground truth audit point
   ```

**Edge cases / Fallback:**

| Scenario | 行為 |
|:---|:---|
| Module 無 `functional.md`(infra-only change)| Skip checks 1-5,只跑 6-9 |
| Project 無 `tests.md`(spec-only project)| Skip checks 2-3,只跑 1 + 4-9 |
| Project 無 `lint.sh`(eg. 純 docs project)| Skip check 7 + warning「lint.sh not found,對齊 memory:backend_lint_workflow」|
| `git status` detached HEAD | Abort + 提示「請先 checkout branch」|
| No staged + no recent commit(empty diff)| Output「Nothing to push,no-op」+ exit 0 |
| 5-engineer mode + cross-module change | Per-module 跑 9 check,verdict = AND of all modules |

**Confidence Tier:** 🟢 high(9 條 check 全機械化,對齊 §E.3a + §E.8.4 + §6.5 特性 2 Stage Gate)

**Cross-references:**
- proposal §6.4.11 §E.8.4 push-gate spec
- proposal §6.4.11 §E.3a 三向 invariant 6 條 + enforcement 命令
- proposal §6.4.11 §E.8.5 git pre-push hook 範例
- memory `backend_lint_workflow` — ruff F821/F + mypy baseline 不增
- §K.4 No Fast Path Policy — bypass = PO ack emergency only
- §K.9 override metrics — `--no-verify` 觸發 alarm count

---

## Subcommand: setup-worktree(new in v1.2 — Stage 1 init)

> 對齊 proposal §6.4.11 §E.8.2(**rev 1.17 — 2026-06-23 PO 拍板 Option A** + **rev 1.17.2 — 2026-06-23 PO 拍板 Q-B Yes**)。**Phase 2 → Phase 3 transition** 自動觸發(原 Phase 3 → Phase 4 已 deprecated),或 PO manual。建 **filesystem-isolated worktree dir `../<project>/`** with branch `dev/<project>`,Phase 3 shared infra + Phase 4 module dev 全 commit 到這。Phase 5 才 merge 回 main。

> **rev 1.17 rationale:** Phase 3 shared infra commits 進 main = 半成品污染風險(orphan schema if Phase 4 abandoned)。改 Phase 3 entry 觸發,main 保留 always-deployable invariant。
> **rev 1.17.2 rationale:** Same-dir `git checkout -b` 改 filesystem-isolated `git worktree add ../<project>` — folder name = project name + 多 project 平行 active + 無 wrong-branch commit 風險。

**Trigger:**
- Auto:`/pm advance-phase 3`(SKILL 自動觸發 — rev 1.17 改自 advance-phase 4)
- Manual:`/pm setup-worktree`

**Workflow:**

0. **Apply mainline-forbidden guard**(rev 1.17.3 §E.8.8.2 — see Shared Guard section above)。Abort if active=mainline。
1. **Resolve active project** + verify `state.md.current_phase` ≥ 2 + phase_2_signoff=true(對齊 Phase 2 lighten 後 plan.md ready)。
2. **Check git state:**
   - `git status --porcelain` 必 clean(無 uncommitted)
   - 否則 abort + 提示「先 commit 或 stash」
3. **Switch to main + pull:**
   ```bash
   git checkout main && git pull origin main
   ```
4. **Create worktree dir + branch(rev 1.17.2 — filesystem-isolated):**
   - Verify `../<project>/` 不存在(else abort + prompt manual cleanup)
   - 若 `dev/<project>` 不存在(`git rev-parse --verify origin/dev/<project>` 失敗):
     ```bash
     git worktree add ../<project> -b dev/<project>
     cd ../<project> && git push -u origin dev/<project>
     ```
   - 若 branch 已存在(re-entry / rollback case — idempotency per §E.8.2):
     ```bash
     git fetch origin dev/<project>
     git worktree add ../<project> dev/<project>
     ```
5. **Update `docs/pm/<project>/state.md`(in main repo,NOT in worktree):**
   ```yaml
   worktree_branch: dev/<project>
   worktree_path: ../<project>          # rev 1.17.2 — new field
   phase_3_started_at: <YYYY-MM-DD>     # rev 1.17 — changed from phase_4_started_at
   phase_2_signoff: true                # 對齊 Phase 2 plan.md lock
   migration_policy: rev_1_17_2_default # rev 1.17.2 — vs grandfather carve-out
   ```
   ```
   onboarding hint: "Switch CWD to ../<project>/ for Phase 3+4 development.
                    Return to main repo for /pm status / /pm advance-phase 5."
   ```
6. **Optional team roster** (5-engineer mode):
   - 若 `docs/pm/<project>/team-roster.md` 已存在 → echo team list
   - 若不存在 → prompt PO 填(skip if 1-PO)
7. **Append decision-log:**
   ```
   D-pm-<seq>: Phase 4 started. Worktree=dev/<project>. by=PO at=<ISO8601>
   ```
8. **Install pre-push hook** — **pure bash, no Claude CLI dependency**(對齊 spectra v1.1.8 Round 1 B1 fix):

   > ⚠ **設計理由(對齊 §E.8.5):** 原設計 hook 內呼叫 `claude /pm push-gate`,但 Claude Code CLI 主要 interactive,git hook minimal bash 環境可能失效。**改為 pure bash 跑 critical subset of 9 checks**(由 SKILL 自動寫入 hook);完整 9 check 仍可由 PO/engineer 手動 `/pm push-gate` 跑。Hook = fast deterministic gate;`/pm push-gate` = thorough audit。
   
   ```bash
   cat > .git/hooks/pre-push <<'HOOK_EOF'
   #!/bin/bash
   # Pure bash pre-push gate (對齊 §6.4.11 §E.8.4 critical subset)
   # Auto-installed by /pm setup-worktree, no Claude CLI dependency
   
   set -e
   FAILED=()
   
   while read local_ref local_sha remote_ref remote_sha; do
     [[ "$remote_ref" != "refs/heads/dev/"* ]] && continue
     
     # Check 1: no_uncommitted_changes (對齊 §E.8.4 #8)
     [ "$(git status --porcelain | wc -l)" -eq 0 ] \
       || FAILED+=("uncommitted changes present")
     
     # Check 2: lint_pass (對齊 §E.8.4 #7 + memory:backend_lint_workflow)
     if [ -f "lint.sh" ]; then
       bash lint.sh > /tmp/push-gate-lint.log 2>&1 \
         || FAILED+=("lint failed (see /tmp/push-gate-lint.log)")
     fi
     
     # Check 3: no_stale_functional_md (對齊 §E.8.4 #6)
     for FUNC in $(find docs/modules -name functional.md 2>/dev/null); do
       MODULE=$(dirname "$FUNC")
       FUNC_MTIME=$(stat -c %Y "$FUNC")
       LAST_CODE_MTIME=$(git log -1 --format=%ct -- "$MODULE/" 2>/dev/null || echo 0)
       [ "$FUNC_MTIME" -ge "$LAST_CODE_MTIME" ] \
         || FAILED+=("functional.md stale: $FUNC")
     done
     
     # Check 4: functional_md_updated when code changed (對齊 §E.8.4 #9)
     CHANGED=$(git diff --name-only "$remote_sha..$local_sha" 2>/dev/null || echo "")
     if echo "$CHANGED" | grep -qE '\.(py|js|html|css)$'; then
       echo "$CHANGED" | grep -q 'functional.md' \
         || FAILED+=("code changed but functional.md not in push")
     fi
   done
   
   if [ ${#FAILED[@]} -gt 0 ]; then
     echo "❌ push-gate failed (${#FAILED[@]} check(s)):"
     for F in "${FAILED[@]}"; do echo "  - $F"; done
     echo ""
     echo "Fix actionable above, then re-push."
     echo "若 emergency bypass (對齊 §K.4 — PO ack 必填):"
     echo "  git push --no-verify  ← ⚠ §K.9 audit 自報"
     echo ""
     echo "完整 9-check audit: /pm push-gate (interactive)"
     exit 1
   fi
   
   # Audit pass to daily report
   DATE=$(date +%Y-%m-%d)
   REPORT="docs/pm/reports/$DATE-daily.md"
   mkdir -p "$(dirname "$REPORT")"
   if [ ! -f "$REPORT" ]; then
     echo "---" > "$REPORT"
     echo "date: $DATE" >> "$REPORT"
     echo "---" >> "$REPORT"
     echo "" >> "$REPORT"
     echo "## Push Gate Results" >> "$REPORT"
   fi
   echo "- $(date +%H:%M) | verdict=pass | commit=$local_sha" >> "$REPORT"
   
   echo "✅ push-gate passed (4 critical checks)"
   exit 0
   HOOK_EOF
   chmod +x .git/hooks/pre-push
   ```
   
   **Hook checks vs `/pm push-gate` 9-check 對比:**
   
   | Check | Hook (pure bash) | /pm push-gate (interactive) |
   |:---|:---:|:---:|
   | every_feature_has_code_commit | ❌ skip(需 yq + complex)| ✅ |
   | every_feature_has_test_case | ❌ skip | ✅ |
   | every_test_case_has_result | ❌ skip | ✅ |
   | execution_log_per_done_feature | ❌ skip | ✅ |
   | actual_completion_filled | ❌ skip | ✅ |
   | no_stale_functional_md | ✅ | ✅ |
   | lint_pass | ✅ | ✅ |
   | no_uncommitted_changes | ✅ | ✅ |
   | functional_md_updated | ✅ | ✅ |
   
   → Hook 抓 4 個 deterministic + fast;完整 audit 仍可 `/pm push-gate` 手動跑(對齊 hybrid design)。

**Output:**
```
🌲 /pm setup-worktree — project: <name>

✅ main pulled (latest commit: <sha>)
✅ Branch dev/<name> created + pushed to origin
✅ state.md updated: worktree_branch / phase_3_started_at  # rev 1.17 — was phase_4_started_at
✅ Pre-push hook installed (.git/hooks/pre-push)

Phase 4 active. Next: /v2 start task <feature-id>
```

**Edge cases:**
- 既有 worktree branch + diverged:abort + 提示「先 rebase 或 reset」
- Single-PO 模式:skip team-roster prompt + simplified output

**Confidence Tier:** 🟢 high(git plumbing only,無 schema risk)

**Cross-references:** proposal §6.4.11 §E.8.1 Architecture / §E.8.2 spec / §E.8.5 hook

---

## Subcommand: migration-status(new in v1.2 — cross-phase visibility)

> 對齊 proposal §6.4.11 §G.6.0.4。Read-only dashboard,顯示 SSOT hash + per-env migration applied state。

**Trigger:** PO manual or auto by `/pm daily`

**Workflow:**

1. Resolve active project.
2. Read `docs/migrations/manifest.yaml`(若無 → output「No migrations defined for this project」+ exit 0)
3. Read `docs/pm/<project>/migration-state.md`(若無 → output「Migration state file missing,run /pm migration-propose first」)
4. Compute SSOT hash:
   ```bash
   sha256sum laundry_db_create_tables.sql | cut -d' ' -f1
   ```
5. Compare 對齊 state.md `schema_ssot_hash_current` field per env(dev/staging/prod)
6. Output visual matrix(對齊 §G.6.0.3):

```
📊 /pm migration-status — project: <name>

SSOT: laundry_db_create_tables.sql (hash: a3b1...)
last_updated: 2026-06-18

| Migration | dev | staging | prod | Applied by |
|:---:|:---:|:---:|:---:|:---|
| 001 | ✅ 2026-06-01 | ✅ 2026-06-02 | ✅ 2026-06-03 | PO |
| 002 | ✅ 2026-06-05 | ✅ 2026-06-06 | ⏳ pending | — |
| 003 | ✅ 2026-06-15 | ⏳ pending | ⏳ pending | — |

SSOT Sync State:
  - dev:    ✅ hash matches
  - staging: ⚠ behind 1 migration
  - prod:    ⚠ behind 2 migrations

Next Action:
  /pm migration-apply --env staging  (auto-apply migration 003)
  /pm migration-apply --env prod      (print only, then mark-applied)
```

**Confidence Tier:** 🟢 high(read-only,deterministic)

**Cross-references:** proposal §6.4.11 §G.6.0.2 manifest schema / §G.6.0.3 state file

---

## Subcommand: migration-propose(new in v1.2 — schema discipline propose)

> 對齊 proposal §6.4.11 §G.6.0.5 + memory `backend_schema_change_workflow`(SSOT + propose 必含 ALTER TABLE 3 樣)。

**Arguments:** `<feature-id>`(對齊 functional.md feature)

**Trigger:**
- Auto:`/v2 done <feature>` 若 `functional.md.features[].schema_change: true`
- Manual:PO 在 propose stage 主動跑(對齊 memory:backend_change_rule propose gate)

**Workflow:**

1. Resolve active project + verify `state.md.current_phase` == 3.
2. Read `docs/modules/<module>/functional.md`,find feature by ID,verify `schema_change: true`。
3. **Prompt PO for ALTER TABLE 3 樣**(對齊 memory):
   - forward_sql:`ALTER TABLE ... ADD COLUMN ...`
   - backward_sql:rollback path
   - verify_sql:`SELECT count(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE ...`
4. **Prompt additional metadata:**
   - rollback_safe(true/false)
   - expected_apply_duration_sec(integer)
   - 大表 alert:若 > 60s → warning「對齊 4-day pattern 慎重」
5. **Generate migration file** at `docs/migrations/<YYYY-MM-DD>-<NNN>-<slug>.sql`:
   - NNN 自動 sequence(讀 manifest.yaml 最大 id + 1,zero-padded 3 digits)
   - 內含 forward / backward / verify SQL 3 段(對齊 §G.6.0.2)
6. **Append manifest.yaml** new entry(對齊 §G.6.0.2 schema):
   ```yaml
   - id: "<NNN>"
     date: <YYYY-MM-DD>
     feature_id: <feature-id>
     file: <YYYY-MM-DD>-<NNN>-<slug>.sql
     forward_sql: |
       <as input>
     backward_sql: |
       <as input>
     verify_sql: |
       <as input>
     rollback_safe: <bool>
     expected_apply_duration_sec: <int>
   ```
7. **Update SSOT** `laundry_db_create_tables.sql`:
   - 將 forward_sql 應用到 SSOT(SKILL 提示 PO confirm before write)
   - 若 PO reject:abort + manifest entry 標 `ssot_pending: true`
8. **Update functional.md feature:**
   ```yaml
   schema_change: true
   migration_id: "<NNN>"
   ```
9. **Append decision-log:**
   ```
   D-pm-<seq>: Schema migration <NNN> proposed for <feature-id>. by=PO at=<ISO>
   ```

**Output:**
```
📝 /pm migration-propose — feature: <feature-id>

Generated:
  📄 docs/migrations/2026-06-18-002-add-bizcard-status.sql
  📋 manifest.yaml: entry 002 appended
  🔧 laundry_db_create_tables.sql: ALTER TABLE applied to SSOT
  📌 functional.md: <feature-id> tagged schema_change=true, migration_id="002"
  📚 decision-log: D-pm-<seq> appended

Next:
  /pm migration-apply --env dev      (verify forward_sql syntactically)
  /pm validate-shared-infra           (full Phase 3 gate)
```

**Edge cases:**
- functional.md feature 不存在 → abort
- schema_change: false → abort + 提示「先標 schema_change: true」
- SQL 語意錯(SKILL 不 validate semantic)→ memory rule:PO 必審

**Confidence Tier:** 🟡 medium(SQL 語意 PO 必審,SKILL 只負責 file plumbing + structural)

**Cross-references:** proposal §G.6.0.5 / §G.6.0.2 / memory:`backend_schema_change_workflow` + `backend_change_rule`

---

## Subcommand: migration-apply(new in v1.2 — env-specific apply)

> ⚠ **RUNTIME PREREQUISITE**(v1.1.10 added):dev/staging auto-execute 需 **`.env.dev` / `.env.staging` with DB connection vars**(`DB_HOST_*` / `DB_USER_*` / `DB_PASSWORD_*` / `DB_NAME`)。**Run `/pm verify-runtime` first**。若 .env 缺 → dev/staging path 退化為 prod print-only mode(safe degradation,non-blocking)。

> 對齊 proposal §6.4.11 §G.6.0.6。**Dev/staging auto-execute,prod print only**(對齊 memory:PO 自 apply prod)。

**Arguments:** `--env <dev|staging|prod>`

**Trigger:** PO manual

**Preconditions:**
- manifest.yaml valid + ≥ 1 entry
- env=prod 需 phase_5_signoff: true(對齊 §F)

**Workflow:**

**IF env in [dev, staging]:**

1. Read manifest.yaml + migration-state.md,filter `pending` migrations for target env.
2. 列 pending count,PO confirm(y/N)。
3. For each pending migration in sequence:
   - Print forward_sql to console
   - Execute via:
     ```bash
     mysql -h <env-db-host> -u <user> -p<pwd> <db> < forward_sql
     ```
     (credentials 從 `.env.<env>` 讀,memory `dep_management` 對齊)
   - Run verify_sql,若 count != 0 → abort + flag failed
4. Update migration-state.md:per-migration `applied[<env>] = <YYYY-MM-DD>`
5. Append decision-log per migration:
   ```
   D-pm-<seq>: Migration <NNN> applied to <env> by SKILL (auto). verify=pass.
   ```

**IF env == prod:**

1. Read manifest.yaml + migration-state.md,filter `pending` migrations for prod.
2. **NOT auto-execute.** SKILL 列 pending migrations + 每 migration forward_sql(可複製)
3. SKILL print reminder(對齊 memory):
   ```
   ⚠ 對齊 memory: backend_schema_change_workflow,prod migration 必 PO 自 apply。
   
   方式 A(Azure Portal Cloud Shell):
     mysql -h <prod-host> -u <user> -p <db>
     <貼 forward_sql>
   
   方式 B(本機 + Azure 連線):
     az mysql flexible-server connect --name <prod-server> --admin-user <user>
   
   Apply 完跑:
     /pm migration-mark-applied --env prod --version <NNN>
   ```
4. NOT update migration-state.md(等 mark-applied)
5. Append decision-log:
   ```
   D-pm-<seq>: Prod migration <NNN> printed for PO self-apply. Pending mark-applied.
   ```

**Output format(dev/staging,success):**
```
🔧 /pm migration-apply --env <env>

Applied:
  ✅ Migration 002 (2026-06-05): ALTER TABLE Friend_Bizcard ADD ...
     verify_sql: 1 row matched ✅
  ✅ Migration 003 (2026-06-15): CREATE INDEX ...
     verify_sql: 1 row matched ✅

migration-state.md updated.
decision-log: 2 entries appended.
```

**Output format(prod,print only):**
```
🛑 /pm migration-apply --env prod — PO SELF-APPLY REQUIRED

Pending(2):
  Migration 002:
    ALTER TABLE Friend_Bizcard ADD COLUMN profile_create_datetime TIMESTAMP;
  Migration 003:
    CREATE INDEX idx_bizcard_create_datetime ON Friend_Bizcard(...);

Apply via Azure CLI / Portal Cloud Shell.
Then:
  /pm migration-mark-applied --env prod --version 002
  /pm migration-mark-applied --env prod --version 003
```

**Edge cases:**
- 無 pending migration → output「Nothing to apply for <env>」
- forward_sql exec fail → abort,flag in state.md,don't apply later migrations(對齊 sequential safety)
- verify_sql 結果不 match → 同上

**Confidence Tier:**
- dev/staging: 🟡 medium(auto-execute,但 SQL exec 可能 fail)
- prod: 🔴 low(print only,PO 拍板)

**Cross-references:** proposal §G.6.0.6 + memory `backend_schema_change_workflow` + `dep_management`

---

## Subcommand: migration-mark-applied(new in v1.2 — prod audit)

> 對齊 proposal §6.4.11 §G.6.0.7。PO 自 apply prod migration 完後,SKILL mark + verify。

**Arguments:** `--env prod --version <NNN>` `[--reason <text>]`

**Trigger:** PO manual(only prod;dev/staging 由 migration-apply auto-mark)

**Prerequisites**(對齊 spectra v1.1.8 Round 1 C5 fix — 明示 implicit credential 假設):

| Optional file | 用途 | 缺則 fallback |
|:---|:---|:---|
| `.env.prod` 含 read-only DB credentials | `DB_HOST_PROD_RO` / `DB_USER_PROD_RO` / `DB_PASSWORD_PROD_RO` | SKILL 自動跑 verify_sql 驗 result |
| 上述 file 不存在 | (新 onboarding 場景)| SKILL prompt PO 自輸 verify_sql result(不 fail)|

> **對齊 memory:** `dep_management` — 用既有 mysql CLI(Azure Linux 3.0 native),不裝 Python driver / ORM;`backend_schema_change_workflow` — PO 自 apply prod migration,SKILL 只 mark + verify。

**Workflow:**

1. Verify `--env == prod`(reject 其他)
2. Read manifest.yaml entry for version `<NNN>`,fetch verify_sql。
3. **Attempt verify:**
   - 若 `.env.prod` 存在且包含 read-only DB credentials:
     ```bash
     mysql -h <prod-host> -u <readonly-user> -p<pwd> <db> -e "<verify_sql>"
     ```
     SKILL 自動驗 result
   - 若 credentials 不存在或 connection fail:
     ```
     ⚠ Prod DB read-only connection unavailable.
     Please paste verify_sql result manually:
       <verify_sql 印出>
     PO input: __________
     ```
     PO 自填 result
4. **Update migration-state.md:**
   ```yaml
   migrations:
     - id: "<NNN>"
       applied:
         prod: <YYYY-MM-DD>
   schema_ssot_hash_current_prod: <updated hash>
   ```
5. **Append decision-log:**
   ```
   D-pm-<seq>: Migration <NNN> applied to prod by PO at <ISO>. verify_sql result: <output>. reason: <text>
   ```
6. **Recompute SSOT sync state** + print next action if more pending。

**Output:**
```
✅ /pm migration-mark-applied — Migration <NNN> marked as applied to prod

Verify: 1 row matched ✅ (or: PO manual input: "1")
migration-state.md updated.
decision-log: D-pm-<seq> appended.

Remaining pending for prod: 1 (Migration 003)
Next: /pm migration-mark-applied --env prod --version 003
```

**Edge cases:**
- Version 已 applied → output「Already marked applied, no-op」
- Version 不在 manifest → abort
- verify_sql fail → flag manifest entry `prod_applied: failed` + 提示 rollback or fix

**Confidence Tier:** 🔴 low(PO 拍板 + audit-mandatory)

**Cross-references:** proposal §G.6.0.7 + memory `backend_schema_change_workflow`(PO 自 apply)

---

## Subcommand: validate-discipline-invariant(new in v1.2 — §K meta gate)

> 對齊 proposal §6.4.11 §K.6。**機械化 check Phase 0-7 順序 / signoff lineage / git no-verify count / direct main commit**。

**Trigger:**
- Auto:`/pm deploy` precondition(對齊 §G.6.1)
- Manual:PO audit

**Workflow:**

Run 6 checks(對齊 §K.6):

1. **Phase order check:**
   - Read `state.md.phase_<0..7>_signoff`
   - 必順序 ✅(無 skip / 無 reorder)
   - Fail:list skipped phases

2. **Signoff lineage check:**
   - 每 `phase_<N>_signoff: true` 必對應 `org-decision-log.md` 中 `D-phase-advance-*` entry
   - Fail:list missing audit entries

3. **Direct main commit check(對齊 §E.8 worktree → main only):**
   - `git log main --first-parent --format='%H %s'` 過去 30 day
   - 排除 merge commit(parent count ≥ 2)
   - 若 non-merge commit on main exists outside `/pm advance-phase 5` merge → flag
   - Fail:list direct-main commits

4. **Phase 6 signoff vs deploy commit check:**
   - 若 `last_deploy_commit` 設,verify `state.md.phase_6_signoff` corresponding `commit_hash` matches
   - Fail:deploy commit 沒過 Phase 6 gate

5. **Git no-verify count check(對齊 §E.8.4 + §K.9)** — ⚠ **BEST-EFFORT 機制**(spectra v1.1.8 Round 1 C1 fix):
   - `git log --grep "no-verify" --grep "skip-hooks" --since=30days` count
   - 若 ≥ 1 → flag(K.9 metrics 也會 alert)
   - Fail:list commits with --no-verify in message
   
   > ⚠ **Limitation:** `git push --no-verify` 是 push flag,**commit message 預設沒這 string**。此 grep 只 catch engineer self-annotated commit(eg. msg 寫「emergency, --no-verify push」)。**Best-effort proxy,非 deterministic**。補強 path:
   > 
   > | Source | 可靠度 | 對齊 |
   > |:---|:---|:---|
   > | **Primary:** `state.md.discipline_overrides[]` | ✅ deterministic | K.8 PO 主動 override 才 log |
   > | **Secondary:** 本 Check 5 grep commit message | 🟡 best-effort | self-annotated only |
   > | **Tertiary:** hook 自己 log invoke(若 bypassed 就無 log,proxy by absence)| 🟡 best-effort | hook design dependent |
   > 
   > → K.9 alarm 是 **directional indicator**,非 absolute count。Phase 7 retro 才有 ground truth audit(累計事件比較)。

6. **Phase advance via signoff check:**
   - 每 phase advance 必對應 prior phase signoff:true
   - Fail:list advance without signoff

**Output(pass):**
```
🛡 /pm validate-discipline-invariant — VERDICT: ✅ PASS

  1️⃣ Phase order check(0→1→2→3→4→5→6→7)           ✅
  2️⃣ Signoff lineage(7 entries in decision-log)     ✅
  3️⃣ Direct main commit check(只 merge from dev)     ✅
  4️⃣ Phase 6 signoff vs deploy commit                ✅
  5️⃣ Git no-verify count(過去 30 day)               ✅ (0 count)
  6️⃣ Phase advance via signoff                       ✅

Discipline invariant holds. Deploy can proceed.
```

**Output(fail):**
```
🛡 /pm validate-discipline-invariant — VERDICT: 🚫 FAIL

  1️⃣ Phase order check          ❌ Phase 5 skipped (advanced 4→6 directly)
  2️⃣ Signoff lineage              ✅
  ...
  5️⃣ Git no-verify count          ❌ 2 commits used --no-verify in last 30 days:
                                       - <sha1> 2026-06-15 "quick fix"
                                       - <sha2> 2026-06-17 "emergency"

Violations: 2
Remediation:
  - Phase skip: run /pm gate-check phase-5 + /pm advance-phase 5 properly
  - --no-verify usage: 對齊 §K.9 alarm threshold 1/month warning;若超 → freeze deploy

Override path(對齊 §K.8):
  /pm deploy --override-discipline --reason "<≥50 chars>"
  (need confirmation phrase "BYPASS DISCIPLINE")
```

**Confidence Tier:** 🟢 high(機械化 check,deterministic;對齊 §6.5 特性 2 Stage Gate)

**Cross-references:** proposal §6.4.11 §K(全)+ §G.6.1 precondition + §6.4.4 Trust Hierarchy + §E.8.4 push-gate

---

## Subcommand: deploy(new in v1.2 — Azure CLI + multi-precondition)

> ⚠ **RUNTIME PREREQUISITE**(v1.1.10 added,對齊 PO 抓 deploy Azure CLI gap):此命令依 **Azure CLI(`az`)+ Azure auth + `azure-config.yaml` + `smoke-test.sh`**,**均 not bundled** with PM Skill。**Run `/pm verify-runtime` first** 看哪些 prereq 已 met / setup guide。**Currently SPEC ONLY,workflow 設計完整但 executable 視 runtime config 而定**。

> 對齊 proposal §6.4.11 §G.6.1 + §K.8(override mechanism)。**Multi-precondition gate + PO 拍板 + Azure slot swap + post-deploy smoke + auto rollback fallback**。

**Arguments:**
- `--target <staging|prod>`(required)
- `--reason "<text>"`(required,≥ 50 chars if --target prod)
- `--dry-run`(optional,跑 precheck 但不真 deploy)
- `--override-discipline --reason "<text>"`(optional,對齊 §K.8 唯一 escape,confirmation_phrase=`BYPASS DISCIPLINE` required)

**Trigger:** PO manual(SKILL 不自動觸發,對齊 §6.4.4 trust hierarchy)

**Workflow:**

1. **Precondition checks** — **COLLECT-ALL mode**(對齊 spectra v1.1.8 Round 1 C4 fix,PO UX 友善):

   > **Mode policy:** SKILL **不 fail-fast**,**全 7 條 precondition 跑完再 verdict**(rev 1.17.9 updated 6 → 7 with Layer 4 sanity check addition)。一次列所有 fail + 一次列全 fix actionable,**PO 1 趟修完**(非多趟 round-trip)。
   
   執行順序(全 7 條都跑):
   
   - 1️⃣ `phase_5_signoff: true`
   - 2️⃣ `/pm validate-release` pass(對齊 §G.4)
   - 3️⃣ `rollback_plan_rehearsed: true`(對齊 §G.3)
   - 4️⃣ `smoke_test_all_pass: true`(staging if --target prod)
   - 5️⃣ **NEW** `schema_migrations_aware` gate(對齊 §G.6.0 + rev 1.8):
       - 跑 `/pm migration-status` 內部 check
       - 若 pending migrations exist for target env → flag fail(不立刻 abort)
   - 6️⃣ **NEW** `discipline_invariant_check: pass`(對齊 §K.6 + rev 1.10):
       - 跑 `/pm validate-discipline-invariant` 內部
       - 若 fail:flag fail(若 --override-discipline set + ONLY this fails → proceed)
   - 7️⃣ ⭐ **NEW rev 1.17.9 Layer 4** `phase_6_pre_deploy_sanity_check_pass` gate(對齊 §F.3 + §F.5 + Progressive Widening Layer 4):
       - Read `state.md.phase_6_pre_deploy_sanity_check.latest_status` — 必須 `pass`
       - Read `state.md.phase_6_pre_deploy_sanity_check.runs[last].executed_against_commit` — 必須 match current main HEAD(staleness check)
       - 若 stale(main has commits since last sanity check)→ flag fail with "sanity check stale,re-run required against current main HEAD"
       - 若 `latest_status: not_yet_executed` → flag fail with "Pilot v0 sanity_test_runner LIFF page never run for this project,build + run first"
       - 若 `latest_status: fail` → flag fail with "previous sanity check failed,investigate result_json_path + backend_log_path,fix + re-run"
       - **Carve-out:** check `state.md.phase_6_pre_deploy_sanity_check_carve_out[]` — if current target commit listed with explicit reason + PO authorize → bypass this gate(per `[[backend_change_rule]]` spirit:doc-only / config-only / infrastructure-only deploys may skip)
       - **Multi-device pool extension(Pilot v1 future):** if `state.md.phase_6_pre_deploy_sanity_check.pilot_version: v1` AND `multi_device_results[]` exists → additional check `concurrent_race_test_pass: true` for Phase 7 stress test gating
   
   **Aggregate verdict 邏輯**(rev 1.17.9 updated — 7 conditions per Progressive Widening Layer 4 addition):
   
   | Scenario | 行為 |
   |:---|:---|
   | 7 條全 pass | proceed Step 2 |
   | 任 condition fail + 無 override flag | abort + 列全 7 條 status + 一次給 fix actionable |
   | --override-discipline set + ONLY #6 fail | proceed Step 2(對齊 §K.8 rev 1.10.1 scope ONLY discipline) |
   | #7 fail with carve_out match | proceed Step 2(per `state.md.phase_6_pre_deploy_sanity_check_carve_out[]` audit trail)|
   | --override-discipline set + #6 fail + 其他 fail | abort + 提示「override scope 限 discipline,#X 也 fail 需先修」 |
   
   **Output 範例(任 condition fail):**
   ```
   🚀 /pm deploy --target prod — Precondition status:
     1️⃣ phase_5_signoff                ❌ phase_5_signoff is false
     2️⃣ /pm validate-release            ✅
     3️⃣ rollback_plan_rehearsed         ❌ last rehearsal > 30 days ago
     4️⃣ smoke_test_all_pass             ✅
     5️⃣ schema_migrations_aware         ❌ 2 pending migrations for prod
     6️⃣ discipline_invariant_check     ✅
   
   ❌ Deploy blocked. Fix all 3 items below:
     - Phase 5 signoff:跑 /pm signoff phase-5 --approver PO
     - Rollback rehearsal:跑 /pm rollback --dry-run + update rollback-plan.md
     - Pending migrations:跑 /pm migration-apply --env prod(print only)+ mark-applied 2 versions
   ```

2. **PO confirmation:**
   - SKILL 顯示 summary:
     ```
     Target: <env>
     Commit hash: <sha>
     Diff vs last prod tag: <stat>
     Rollback rehearsal date: <YYYY-MM-DD>
     E2E + perf SLA: ✅
     Schema migrations: ✅ aligned
     Discipline invariant: ✅ pass (or ⚠ overridden via --override-discipline)
     ```
   - Required PO input:`--reason "<text>"` + 型 `DEPLOY` 確認
   - 若 --override-discipline:額外要求型 `BYPASS DISCIPLINE`

3. **Tag release:**
   ```bash
   git tag release-$(date +%Y%m%d-%H%M)
   git push origin --tags
   ```

4. **Execute deploy via Azure CLI — SKU-aware**(對齊 `azure-config.yaml` `deploy_strategy` + spectra v1.1.10 C2 fix):

   4.0 Read `azure-config.yaml`(verify-runtime 設好):
   ```bash
   APP_NAME=$(yq '.web_app.name' azure-config.yaml)
   RG=$(yq '.resource_group' azure-config.yaml)
   STRATEGY=$(yq '.web_app.deploy_strategy' azure-config.yaml)
   ```
   
   4.1 **IF `deploy_strategy: slot_swap`(Standard+ SKU,zero-downtime):**
   ```bash
   SLOT_STAGING=$(yq '.web_app.slots.staging' azure-config.yaml)
   SLOT_PROD=$(yq '.web_app.slots.production' azure-config.yaml)
   # Pre-deploy code to staging slot
   az webapp deploy --resource-group "$RG" --name "$APP_NAME" \
     --slot "$SLOT_STAGING" --src-path . --type zip
   # Smoke test on staging slot first
   bash docs/release/smoke-test.sh --url "https://${APP_NAME}-${SLOT_STAGING}.azurewebsites.net/health"
   # Slot swap (zero-downtime cutover)
   az webapp deployment slot swap --resource-group "$RG" \
     --name "$APP_NAME" --slot "$SLOT_STAGING" --target-slot "$SLOT_PROD"
   ```
   
   4.2 **IF `deploy_strategy: direct`(Basic SKU,~30s downtime — 對齊 PO 2026-06-18 Option C 拍板):**
   ```bash
   # Build ZIP of project (exclude .git, __pycache__, node_modules, venv)
   zip -r /tmp/deploy.zip . \
     -x '.git/*' '__pycache__/*' 'node_modules/*' '.venv/*' '*.log' '.env*'
   
   # ZIP deploy 到 production(app 會 restart ~10-30s)
   az webapp deploy --resource-group "$RG" --name "$APP_NAME" \
     --src-path /tmp/deploy.zip --type zip --async false
   
   # Cleanup
   rm /tmp/deploy.zip
   ```

5. **Post-deploy smoke test:**
   - 跑 `docs/release/smoke-test.sh`(read endpoint from `azure-config.yaml.health_check`,retry 3×5s 對齊 app restart 時間)
   - 若 fail:**自動觸發 `/pm rollback`**(對齊 §G.6.1 安全網,SKU-aware 對齊 §G.6.2 4.1/4.2 同 strategy)

6. **Update state.md:**
   ```yaml
   phase_6_signoff: true            # 若 --target prod 且 smoke pass
   last_deploy_at: <ISO8601>
   last_deploy_commit: <sha>
   ```

7. **Write deploy log** `docs/release/<YYYY-MM-DD>-deploy-log.md`(對齊 §G.1 schema)。

8. **Append decision-log:**
   ```
   D-pm-<seq>: PO deploy --target <env>. commit=<sha>. reason: <text>. by=PO at=<ISO>.
   ```
   若 --override-discipline:額外 entry「override_used=true, override_scope=discipline_only」+ state.md `discipline_overrides[]` append。

9. **Output + next steps:**
   ```
   🚀 /pm deploy --target <env> — VERDICT: ✅ SUCCESS
   
   Azure slot state: swapped (took 47s)
   Smoke test: ✅ all pass
   Deploy log: docs/release/2026-06-18-deploy-log.md
   
   Next:
     /pm validate-post-launch     (啟動 Phase 7 observation window)
     /pm migration-status         (確認 prod schema aligned)
   ```

**Edge cases:**
- 任 precondition fail(無 override):abort + 列每個 fail
- Override 使用但 confirmation phrase 錯:abort
- Azure CLI fail(network/auth):abort,state.md 不 update
- Smoke fail:auto rollback,state.md flag deploy_failed
- --dry-run:跑 precheck 全 print,**不 execute Azure CLI**

**Confidence Tier:** 🔴 low(production-impacting,PO 拍板 final;SKILL 只執行)

**Cross-references:** proposal §G.6.1 / §G.6.0(migration gate)/ §K.6(discipline)/ §K.8(override)/ memory `azure_webapp_runtime` / `dep_management`

---

## Subcommand: sanity-check(new in v1.4 — rev 1.17.10 Layer 4 mainline pre-deploy sanity via Pilot v0 LIFF test runner)

> 對齊 rev 1.17.9 Progressive Widening Layer 4 spec(`phase_6_pre_deploy_sanity_check_pass` quality_bar)+ rev 1.17.10 Pilot v0 concrete impl(`templates/index_sanity_check.html` + `templates/sanity_test_cases.js`)。**Doc-only spec amendment;0 backend *.py change**(per `[[backend_change_rule]]`)。
>
> ⭐ **rev 1.17.10 Round 1 B1 closure 2026-06-24:** Test case schema field `target_url` moved REQUIRED → OPTIONAL because `index.html` IS the V3 SPA — most QA validations are in-SPA navigation(QA taps SPA's own UI),no URL Jump needed。`target_url` retained as optional for URL-driven deep link scenarios only(eg. LINE message tap → LIFF opens specific view via `hello_world_app` query-param dispatch;see TC-009 / TC-010 starter cases in `sanity_test_cases.js`)。Schema spec:**7 required + 7 optional = 14 total**。Dispatcher renders "→ Jump (deep link)" button only when `target_url` present;else shows "📍 navigate manually in SPA" hint。

### Purpose

After all dev/<project> branches have merged back to mainline,**before** `/pm deploy --target prod`,QA runs this command to launch the Pilot v0 sanity test runner on a real device against a local backend (ngrok + Flask + MySQL)。Covers what each F# build's Layer 2+3 cannot:**cumulative mainline integration**(per `[[phase_5_to_6_progressive_widening_verification]]` Layer 4)。

### Confidence Tier

🟡 medium — orchestrates worktree swap + local backend boot + QA real-device run + result capture。Worktree-default invariant 保 mainline 不被誤改;但 QA 必須真機 LINE login → human-in-loop friction。

### Preconditions

| # | Check | Source |
|:---:|:---|:---|
| 1 | `active_project` set | `active-project.txt` |
| 2 | Current branch == `main`(not worktree)| `git rev-parse --abbrev-ref HEAD` |
| 3 | `state.md.phase == 6` | active project state.md |
| 4 | `local_build_environment.py` `Const_Run_in_local_environment == True` | repo root |
| 5 | ngrok tunnel running(`curl http://localhost:4040/api/tunnels` returns 200 + 1+ tunnel)| local desktop |
| 6 | Local MySQL `laundry_DB` accessible(`mysql -u IoT_Manager -e 'USE laundry_DB'`)| local desktop |
| 7 | `templates/index_sanity_check.html` exists in repo | repo |
| 8 | `templates/sanity_test_cases.js` exists in repo + schema valid | repo |

任何 precondition fail → halt + show actionable hint(eg. "Run `python3 -m pip install pyngrok && ngrok start`" if Check 5 fails — **PO authorize 後才裝**)。

### Workflow Steps

```
Step 1 — Verify all 8 preconditions; halt with hint on first fail
Step 2 — Resolve worktree path:  /tmp/pm-sanity-<active_project>-<timestamp>
         (rev 1.17.10 Round 1 spectra-review C2 note: /tmp/ deliberately
          chosen over rev 1.17.2 ~/<project>/ convention because this is
          EPHEMERAL test workspace (not a dev workspace) — auto-cleanup
          via /tmp tmpfs + clear semantic separation from rev 1.17.2 dev
          worktrees that live for Phase 3+4 development duration.)
Step 3 — Open worktree on TEMP BRANCH (not main directly):
         git worktree add -b sanity-temp-<ts> /tmp/pm-sanity-<project>-<ts> main
         (rev 1.17.10 Round 1 spectra-review B3 fix: -b sanity-temp-<ts>
          isolates worktree commits from main branch ref. Without -b, any
          commit in worktree would advance main HEAD locally and pollute
          mainline working tree's git status.)
Step 4 — In worktree only (NOT mainline):
         cp templates/index_sanity_check.html templates/index.html
         git -C /tmp/pm-sanity-<project>-<ts> commit -am "sanity check swap"
         (commit lives on sanity-temp-<ts> branch in worktree only;
          never pushed; main branch ref untouched.)
Step 5 — Print prompt:
         "Open NEW terminal in worktree dir and run:
           cd /tmp/pm-sanity-<project>-<ts>
           python3 app.py
          Then mobile-scan ngrok QR for LIFF URL:
           https://<ngrok-id>.ngrok.io/liff/<bot_basic_id>"
Step 6 — Wait for QA to confirm: "QA done — result downloaded as sanity-run-*.csv"
Step 7 — QA uploads CSV to docs/pm/<project>/sanity-runs/<run_id>.csv
Step 8 — Read CSV summary; parse PASS/FAIL/SKIP counts; record run_id
Step 9 — Append phase_6_pre_deploy_sanity_check.runs[] entry in state.md:
         {
           run_id: "sanity-<ts>",
           executed_at: <ts>,
           executed_against_commit: <main HEAD sha>,
           device: <QA-provided string>,
           total_cases: N,
           passed: P,
           failed: F,
           skipped: S,
           verdict: PASS|FAIL|PARTIAL,
           csv_path: docs/pm/<project>/sanity-runs/<run_id>.csv,
         }
         Update phase_6_pre_deploy_sanity_check.latest_status accordingly
         Set phase_6_pre_deploy_sanity_check_pass = (verdict == PASS &&
                                                     P0_failures == 0)
Step 10 — Print SQL prompt for QA:
         "QA: run cleanup before discarding worktree:
            mysql -u IoT_Manager -p laundry_DB < cleanup_sanity_fake_data.sql
          Review pre-check counts → uncomment DELETEs → re-run → post-check 0"
Step 11 — Wait for QA confirm cleanup verified clean
Step 11.5 — ⭐ MID-DOGFOOD BUG FIX BRANCH (rev 1.17.11 PO directive 2026-06-24)
         If sanity check surfaces a real bug that's reproduced + fixable
         within same session, apply fix DIRECTLY to mainline source WITHOUT
         separate PM Skill Phase 1-6 project ceremony. Both-side invariant:
         (a) Fix mainline templates/*.html / frontend asset directly
         (b) Mirror same fix IN PARALLEL to active worktree's copy
         (c) Continue dogfood with both sides reflecting fix
         (d) Commit mainline changes to main with `fix:` prefix message
         (e) Append decision-log D-<project>-sanity-fix-<finding-slug>
         (f) Reference fix commit in state.md.phase_6_pre_deploy_sanity_check.runs[]
         Exclusions:
           - *.py changes still require propose-first per [[backend_change_rule]]
           - Architectural redesign findings → Phase 1-6 cycle
           - Beyond-same-session findings → normal cycle
         Rationale: sanity-discovered bugs are user-verified high-confidence;
         eat-own-dog-food speed matters; "fix both sides" preserves
         worktree-mainline parity for active dogfood.
         See: [[feedback_sanity_check_bug_fix_direct_main]] memory rule.

Step 12 — Discard worktree AND delete temp branch:
         git worktree remove /tmp/pm-sanity-<project>-<ts> --force
         git branch -D sanity-temp-<ts>
         (rev 1.17.10 Round 1 B3 fix: branch -D removes the temp branch
          so it doesn't accumulate in `git branch -a` over time.)
Step 13 — Append org-decision-log entry D-<project>-sanity-run-<id>
Step 14 — If phase_6_pre_deploy_sanity_check_pass == True:
         → ready for /pm deploy --target prod (Check #7 in deploy precondition will pass)
         Else:
         → block deploy; show FAILED case ids + suggested remediation
```

### Carve-out path

對齊 rev 1.17.9 carve-out mechanism。當 deploy 為:
- **doc-only**(只改 docs/*.md / proposal / decision-log)
- **config-only**(只改 azure-config.yaml / requirements.txt revisions)
- **infrastructure-only**(只改 schema_sync 變更但無 backend logic 變)

時可 propose carve-out:

```
/pm sanity-check --carve-out --reason "doc-only deploy: rev 1.17.10 spec amendment"
```

This appends to `state.md.phase_6_pre_deploy_sanity_check_carve_out[]`:

```yaml
- carve_out_id: <ts>
  applied_at: <ts>
  applied_against_commit: <main HEAD sha>
  reason: "<text>"
  approved_by: <PO id>
```

`/pm deploy --target prod` Check #7 then reads `carve_out[]` and accepts if active entry matches current HEAD。

### Output Contract

成功 case(verdict == PASS):

```
✅ Sanity Check PASS
   Run ID: sanity-2026-06-24-1430
   Device: iPhone 15 Pro (QA-RY)
   Cases: 8 total / 7 PASS / 0 FAIL / 1 SKIP
   CSV: docs/pm/<project>/sanity-runs/sanity-2026-06-24-1430.csv
   Mainline OK → /pm deploy --target prod precondition Check #7 will pass
```

Fail case(verdict == FAIL):

```
🔴 Sanity Check FAIL
   Run ID: sanity-2026-06-24-1430
   Failed cases:
     TC-003 [Profile/P0]: persona switch did not rehydrate content
     TC-005 [Schedule/P0]: binding lost after reload
   ⚠ /pm deploy --target prod BLOCKED until P0 failures resolved
   Next: investigate root cause → fix → /pm sanity-check re-run
```

### Audit Trail Convention

- `state.md.phase_6_pre_deploy_sanity_check.runs[]` — append-only
- `docs/pm/<project>/sanity-runs/*.csv` — one file per run, never overwrite
- `_org/org-decision-log.md` — D-<project>-sanity-run-<id> entry per run
- Worktree path — never persisted to main; ephemeral

### Cross-references

- proposal §F.3 quality_bar `phase_6_pre_deploy_sanity_check_pass`(rev 1.17.9)
- proposal §F.5 Exit Check List item #N(rev 1.17.9)
- `templates/index_sanity_check.html`(Pilot v0 dispatcher)
- `templates/sanity_test_cases.js`(SSOT for test cases — discussion via chat)
- `cleanup_sanity_fake_data.sql`(post-run DB hygiene)
- memory `[[phase_5_to_6_progressive_widening_verification]]` Layer 4
- memory `[[backend_change_rule]]`(0 *.py change in Pilot v0 build)
- memory `[[friend_fetch_cost]]`(no bulk-fetch in any sanity case)
- memory `[[public_vs_private_friend_data]]`(no real friend data in fake_data payloads)
- memory `[[delete_dialog_no_undo_hint]]`(cleanup script comments clarify destructive nature)

---

## Subcommand: sanity-status(rev 1.17.13 — multi-QA aggregation visualization + schema-version flag)

**Arguments:** `<project>` `[--tc=<id>]` `[--since=<date>]` `[--diff=<commit_a>..<commit_b>]` `[--schema-version]` ⭐ rev 1.17.13

**Purpose:** Implements sanity-check REQ-015 — visualize multi-QA aggregated sanity results across runs / devices / commits;reproducibility class(consistent / frequent / flaky / rare / no-bug)+ device/QA breakdown + fail_reason cluster + cross-commit regression detection。**rev 1.17.13:** 加 `--schema-version` flag per sanity-check REQ-018 D.1 — query `_schema_sync_log_sanity` 看當前 sanity schema rev(eg. `v1.0` = REQ-013/014/015 baseline / `v1.1` = REQ-017 eruda capture)→ decide feature compatibility(eg. eruda capture 是否 active)。

**Workflow:**

1. Resolve `<project>` → verify `docs/pm/<project>/state.md` exists
2. **Auth gate(對齊 sanity-check REQ-015 C6 2-layer architecture;rev 1.17.13 cascade per REQ-018 — Layer 2 明示 connect sanity_check_DB):**
   - **Layer 1 — Backend cmd path:** Try `query_sanity_test_results` cmd via backend dispatcher;若 LIFF user_id in PM-role whitelist or ENV `SANITY_QUERY_ALLOWED_IPS` 含 caller IP → proceed。Backend 自動 route to `sanity_check_DB` per sanity-check REQ-018 A.5 routing convention(`sanity_*` prefix or explicit list)
   - **Layer 2 — Direct DB path:** If `SANITY_DB_LOCAL_OVERRIDE=1` AND same-machine → bypass backend cmd dispatcher,**直接連 `sanity_check_DB`**(via `SANITY_DB_HOST` / `SANITY_DB_PORT` / `SANITY_DB_USER` / `SANITY_DB_PASSWORD` / `SANITY_DB_NAME` ENV vars per sanity-check REQ-018 B.4)— **不再隱含連 `laundry_DB`**(防誤連 production 資料,對齊 REQ-018 A.1 isolation invariant + R-NEW-DB-3 mitigation)。Auth = OS-level DB credentials of `sanity_db_user`(per REQ-018 A.6 least privilege)
   - Both paths reject → abort with error "Sanity query not authorized; configure ENV per sanity-check REQ-015 C6 + REQ-018 B.4"
2a. **`--schema-version` flag mode(NEW rev 1.17.13 per sanity-check REQ-018 D.1):**
   - Query `sanity_check_DB._schema_sync_log_sanity` ORDER BY synced_at DESC LIMIT 1 → return latest applied sanity schema rev string(eg. `v1.0` / `v1.1` / `v1.2`)
   - Render output:`Current sanity schema rev: <rev>;eruda capture <active|inactive>;eruda_log_wiped_at column <present|absent>;applied at <synced_at>`
   - Use case:PM decide if `/pm sanity-cleanup-logs` workflow can assume eruda tables exist;dogfood findings 對齊 schema baseline
   - **Return early after schema-version output** — skip Step 3-8(aggregation queries 與 schema introspection 為不同 use case)
3. **Default mode(no flags)— project overview:** Query `v_tc_reproducibility` view filtered by `project_name = <project>` AND `executed_at >= NOW() - 30 DAY`(per REQ-015 acceptance default window)
   - Render table:`TC ID | title | total_runs | pass_rate | fail_rate | confidence_class | device_count | qa_count | latest_run`
   - Top fail clusters section(top 3 by fail_count + fail_reason keyword cluster)
4. **`--tc=<id>` mode — single TC deep dive:**
   - Per (project_name, tc_id) latest 30 days:device breakdown + QA breakdown + reproducibility timeline
   - Render table:`device_info | qa_identifier | run_count | pass | fail | latest_status | latest_fail_reason`
5. **`--since=<date>` flag:** Override default 30-day window
6. **`--diff=<commit_a>..<commit_b>` mode — cross-commit regression:**
   - Per (project_name, tc_id):pre-commit-a pass_rate vs pre-commit-b pass_rate
   - Highlight TCs where fail_rate increased > 20% post-commit-b(suggested regression candidates)
7. **KPI ethical guard(對齊 REQ-015 C5 UI policy layer):** When displaying per-QA bug count → if `bugs_found < 10` for any qa_identifier → render `<N/A — hidden by ethical guard>`(防 ranking;raw data 仍存 backend per C5 invariant)
8. **Output format(rev 1.17.12 Round 1-patch C-pm-4 fix:具體 format options):**
   - **Default:** ASCII table to stdout(box-drawing borders `┌─┐│└─┘`,header bold)— 適合 terminal preview
   - **`--format=csv` flag:** CSV format to stdout(headers + comma-separated;直接 pipe 到 `xsv` / spreadsheet)
   - **`--format=json` flag:** JSON output to stdout(structured `{tcs: [...], aggregation: {...}}` schema 為 future Pilot v1 multi-device dashboard query 用)
   - **`--format=markdown` flag:** Markdown table to stdout(直接 paste 進 git commit message / PR description)
   - PM 可 redirect to file via shell(eg. `/pm sanity-status backend > sanity-status.txt`)

**Confidence:** 🟢 high(read-only query + deterministic aggregation)

---

## Subcommand: sanity-submit-result(rev 1.17.12 — manual fallback import)

**Arguments:** `<project>` `<csv-or-json-file>`

**Purpose:** Implements sanity-check REQ-014 — manual CSV/JSON bulk import to `Sanity_Test_Result_TBL`;解 backend availability dependency(R-1)+ 支援 offline QA + bulk historical import + CI/cron 自動化 ingestion。

**Workflow:**

1. Resolve `<project>` → verify state.md exists
2. Read CSV/JSON file from `<csv-or-json-file>` path
3. **Validate CSV schema match `Sanity_Test_Result_TBL` 22 columns(對齊 sanity REQ-006 + REQ-014 single source of truth;rev 1.8 B-new-1 fix 後 schema 含 `eruda_log_wiped_at`):**
   ```
   result_id, idempotency_token, run_id, project_name, tc_id, tc_definition_version,
   status, fail_reason, validate_prompt_results, autoFill_buttons_used, qa_identifier,
   device_info, executed_at, submitted_at, submit_method, sanity_build_version,
   frontend_version, backend_version, executed_against_commit, duration_sec, notes,
   eruda_log_wiped_at
   ```
4. **Per-row idempotency / INSERT semantics(對齊 REQ-014 C-new-1 fix):**
   - 若 row 含 `result_id` → backend `INSERT IGNORE`(已存在 UUID skip)
   - 若 row **不**含 `result_id` 但含 `idempotency_token` → `INSERT ... ON DUPLICATE KEY UPDATE result_id=result_id`(no-op update)
   - 若兩者皆無 → backend generate `result_id DEFAULT(uuid())` + client fallback generate `idempotency_token`
5. **Per-row `submit_method = 'manual'`**(audit identifiable per REQ-014 acceptance)
6. **Security gate(對齊 REQ-014 + R-NEW-8 mitigation;design spec OQ-4 細節):**
   - Per-project secret key 簽 CSV header(若 configured)
   - PM Skill caller IP allow-list check
   - 若 security gate fail → abort + 顯眼 banner
7. **Size / rate limits(per REQ-014 acceptance):**
   - Max 10,000 rows per CSV(超出 chunked 提示)
   - Max 100 CSV per hour per project(rate limit)
8. Invoke backend cmd `submit_sanity_test_result_bulk` with CSV payload
9. Report:`<X> rows accepted / <Y> rows rejected with detailed error per rejected row / <Z> total bytes ingested`

**Confidence:** 🟡 medium(file parsing + per-row validation + backend cmd dispatch — careful with malformed CSV / network failure)

---

## Subcommand: sanity-cleanup-logs(rev 1.17.12 — explicit eruda log wipe)

**Arguments:** `<project>`

**Purpose:** Implements sanity-check REQ-017 G.1 — explicit eruda log cleanup per project;對齊 `[[delete_dialog_no_undo_hint]]` 慎思 invariant(literal 'yes-cleanup' confirm);支援 pre-wipe export option。

**Workflow:**

1. Resolve `<project>` → verify state.md exists
2. **Query phase:** Count `Sanity_Eruda_Log_TBL` rows + estimate bytes for `<project>`
3. **Confirm prompt(對齊 `[[delete_dialog_no_undo_hint]]` 慎思 invariant):**
   ```
   Wipe <X> eruda logs (~<Y> MB) for <project>?
   This action cannot be undone.
   
   Type "yes-cleanup" to confirm (literal string, no enter substitute):
   ```
   - User input ≠ "yes-cleanup" → abort with no mutation
4. **Pre-wipe export option(對齊 REQ-017 G.6;rev 1.17.12 Round 1-patch B-pm-1 fix:3 branches mutually exclusive,Yes-export-and-wipe path return early to avoid Step 5-8 redundant DELETE + audit double-write):**
   ```
   Export logs to docs/pm/<project>/sanity-archive/ before wiping?
   [Yes export & wipe] / [Skip — direct wipe] / [Cancel]
   ```
   - **If user chooses "Yes export & wipe":**
     - Invoke `/pm sanity-export-logs <project> --then-wipe`(atomic 3-step per REQ-017 G.6 — Step 1 SHA-256 verify / Step 2 transaction wipe / Step 3 audit row write)
     - **`/pm sanity-export-logs --then-wipe` already handles wipe + `Sanity_Lifecycle_Audit_TBL` audit row + `eruda_log_wiped_at` transparency update**
     - **`/pm sanity-cleanup-logs` cmd then `return early`** — skip Step 5-8(`/pm sanity-export-logs` 已完成 wipe + audit;再執行 Step 5-8 會 audit double-write + analytics 誤算 — per Round 1 B-pm-1 fix)
     - Report:「Exported + wiped via `/pm sanity-export-logs --then-wipe`;see export-then-wipe audit row」
   - **If user chooses "Skip — direct wipe":** proceed to Step 5(direct chunked DELETE no export)
   - **If user chooses "Cancel":** abort with no mutation
5. **Chunked DELETE execution(對齊 REQ-017 G + R-NEW-F mitigation;rev 1.17.12 Round 1-patch:Step 5-8 only reached via Step 4 "Skip — direct wipe" path):**
   - Chunk size 1000 rows / 100ms sleep gap
   - SQL transaction:`DELETE FROM Sanity_Eruda_Log_TBL WHERE project_name = '<project>'`
   - 若 transaction fail → audit row `action='cleanup-logs-rollback'` + logs 不刪除 + cmd exit error
6. **Write `Sanity_Lifecycle_Audit_TBL` audit row(對齊 REQ-017 G.5 normative format):**
   - `action='cleanup-logs'` / `executed_by='pm-skill-caller:<user>'`(per REQ-017 G.5 `<source-type>:<source-id>`)/ `rows_affected=<count>` / `bytes_freed=<sum>` / `executed_at=<now>`
7. **Update `Sanity_Test_Result_TBL.eruda_log_wiped_at = NOW()` for affected rows**(transparency 標記 per REQ-017 G.4)
8. Report:`Wiped <X> rows from Sanity_Eruda_Log_TBL; <Y> bytes freed; audit_id <uuid>`

**Confidence:** 🟢 high(explicit confirm + transaction-bounded + audit trail);🔴 low if PROD MySQL connection failure(retry per OQ-14 design spec)

---

## Subcommand: sanity-export-logs(rev 1.17.12 — pre-wipe export tar.gz)

**Arguments:** `<project>` `[--output=<path>]` `[--qa-identifier=<id>]` `[--then-wipe]`

**Purpose:** Implements sanity-check REQ-017 G.6 — export eruda logs to tar.gz for offline diagnostic / archival before wipe。`--then-wipe` 提供 atomic 3-step transactional invariant(SHA-256 verify → transaction wipe → audit row)。

**Workflow:**

1. Resolve `<project>` → verify state.md exists
2. Default output path:`docs/pm/<project>/sanity-archive/<timestamp>-eruda-logs.tar.gz`(`.gitignore` 預設 exclude per REQ-017 R-NEW-H mitigation;`sanity-runs/` 是 CSV uploads 不衝突 per N-new-17 fix)
3. **Query phase:** Select `Sanity_Eruda_Log_TBL` rows for `<project>`(filter `--qa-identifier=<id>` 若指定)
4. **Pre-export 二次 PII scrub(對齊 REQ-017 E + R-NEW-H + C-new-8 fix):**
   - 套用 same 7-regex set(client + backend + export 三層 scrub,defense in depth = redundancy)
   - Verify scrub markers `[redacted-phone]` / `[redacted-email]` / `[redacted-id]` / `[redacted-line-user]` 出現
5. **Pack tar.gz with metadata.json(對齊 REQ-017 G.6 schema):**
   ```json
   {
     "project": "<project>",
     "exported_at": "<ISO8601>",
     "row_count": <N>,
     "pii_scrub_version": "v1-7regex",
     "qa_identifier_filter": "<id or null>"
   }
   ```
6. **Per-project secret key encrypt(對齊 R-NEW-H + design spec OQ-10;rev 1.17.12 Round 1-patch N-pm-3 fix:key path explicit):**
   - **Key path:** `docs/pm/<project>/sanity-archive-secret.key`(per-project,not shared cross-project for blast radius limitation)
   - 若 key 存在 → encrypt tar.gz with AES-256(crypto detail per OQ-10 design spec)
   - 若 key 不存在 → generate 32-byte random key + 寫 key file + 提示 user「妥善保管 — key 是 export 唯一解密方式;丟失 = 老 logs 永久 unreadable」
   - **Auto `.gitignore`:** 寫進 key 後自動 append `docs/pm/<project>/sanity-archive-secret.key` 到 `.gitignore`(防誤 commit;對齊 R-NEW-H mitigation)
   - Key rotation / revocation workflow 留 OQ-10 design spec
7. **Step 1 — Export verify(若 `--then-wipe` 啟用,對齊 REQ-017 G.6 C-new-10 3-step atomicity Step 1):**
   - SHA-256 checksum 計算 + 寫進 metadata.json
   - Tar decompress test(integrity check)
   - 若 Step 1 fail → exit error,no wipe,no audit row(per failure fallthrough)
8. **Step 2 — Transaction wipe(若 `--then-wipe` 啟用,Step 2):**
   - 同 `/pm sanity-cleanup-logs` chunked DELETE 機制(per N-new-22 fix)— `DELETE FROM Sanity_Eruda_Log_TBL WHERE project_name = '<project>'` 但包在 SQL transaction
   - 若 transaction fail → audit row `action='export-then-wipe-rollback'` + logs 不刪除 + cmd exit error
9. **Step 3 — Audit row(若 `--then-wipe` 啟用,Step 3):**
   - Both Step 1 + Step 2 success 才寫:`action='export-then-wipe'` / `executed_by='pm-skill-caller:<user>'` / `rows_affected=<count>` / `bytes_freed=<sum>` / `executed_at=<now>`
   - 整批 atomic success indicator
10. Report:`Exported <X> rows to <path> (<Y> MB); SHA-256 <hash>; <wiped or kept depending on --then-wipe>`

**Confidence:** 🟢 high(read + pack + checksum 都 deterministic);🟡 medium for AES encrypt path(crypto detail in OQ-10 design spec)

---

## Subcommand: sanity-reset-db(rev 1.17.13 — full sanity_check_DB reset for catastrophic recovery / dev clean slate)

**Arguments:** `<project>` `--confirm-with "yes-reset-database"`

**Purpose:** Implements sanity-check REQ-018 C.2 — drops + recreates ENTIRE `sanity_check_DB`(catastrophic recovery / dev clean slate)。**Per `[[delete-dialog-no-undo-hint]]`** 嚴格 literal `"yes-reset-database"` confirmation(比 `/pm sanity-cleanup-logs` `"yes-cleanup"` 更嚴格 — DB-level reset 非 row-level wipe)。

> ⚠ **DESTRUCTIVE — NO UNDO**:整 `sanity_check_DB` drop;ALL projects 的 sanity tables(`Sanity_Test_Result_TBL` / `Sanity_Test_Case_Definition_TBL` / `Sanity_Eruda_Log_TBL` / `Sanity_Lifecycle_Audit_TBL` + `_schema_sync_log_sanity`)全 wipe。**`<project>` arg 只用作 audit context label,不限制 wipe scope**(per REQ-018 C.2 — reset 是 DB-level,not project-level)。**PROD env 此 cmd 永遠 reject**(對齊 REQ-018 B.3 PROD skip pattern)。

**Workflow:**

1. Resolve `<project>` → verify `docs/pm/<project>/state.md` exists(audit context only)
2. **Environment gate(對齊 REQ-018 B.3 + C.2 PROD never reset):**
   - Check ENV `ENV_NAME`(or equivalent indicator):**若 `prod` / `production` → abort with error `"PROD env sanity-reset-db forbidden per REQ-018 B.3 — manual DB ops only for prod"`** + structured log `event=sanity_reset_rejected_prod`
   - Verify `SANITY_DB_NAME` 非空(若 PROD env skip pattern triggered → ENV 留空 → abort with `"sanity DB not initialized — nothing to reset"`)
3. **Confirmation gate(對齊 [[delete-dialog-no-undo-hint]] 嚴格 literal phrase):**
   - Require exact arg `--confirm-with "yes-reset-database"`(literal match;case-sensitive)
   - 若 missing or wrong phrase → abort with explicit error showing exact expected phrase + REQ-018 C.2 ref
   - **不接受** approximate / fuzzy matches(eg. "Yes" / "RESET" / "yes-reset" → reject)
4. **Pre-reset audit snapshot(NEW per REQ-018 D.3 audit archive option b cascade — protect lifecycle history):**
   - Before drop:export `Sanity_Lifecycle_Audit_TBL` → `docs/pm/_archive/sanity-audit/full-reset-<timestamp>.sql.gz`
   - 若 export fail → abort,no drop(per atomicity invariant)
   - 對齊 REQ-018 D.3 option b — clean slate 不破 historical trace
5. **Drop + recreate `sanity_check_DB`(bootstrap user scope per REQ-018 A.3 + C1 fix):**
   - Use `SANITY_DB_BOOTSTRAP_USER` + `SANITY_DB_BOOTSTRAP_PASSWORD` ENV vars(per REQ-018 A.3 bootstrap user — `sanity_db_admin` 或 root scope)
   - `DROP DATABASE IF EXISTS sanity_check_DB;`
   - `CREATE DATABASE IF NOT EXISTS sanity_check_DB CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;`
   - Re-grant `sanity_db_user` SELECT/INSERT/UPDATE/DELETE on new DB tables(per REQ-018 A.6 least privilege re-establish)
6. **Auto-sync schema(對齊 REQ-018 A.2 + A.3 backend startup pattern):**
   - Trigger `schema_sync.py --target sanity` against new `sanity_check_DB`(reuse auto-sync rev 1.1 machinery)
   - Verify `_schema_sync_log_sanity` populated with baseline rev string
7. **Audit row write(對齊 REQ-017 G.5 audit invariant):**
   - INSERT `Sanity_Lifecycle_Audit_TBL` row:`action='full-db-reset'` / `executed_by='pm-skill-caller:<user>'` / `project_name='<arg>'`(audit context label)/ `rows_affected=N/A` / `bytes_freed=<sum-pre-reset>` / `executed_at=<now>` / `pre_reset_audit_archive='<path>'`(per Step 4)
   - 即使 reset 後仍寫(per REQ-018 C.2 — reset 後 audit table 重建,1st row 即此 reset trace)
8. Report:`sanity_check_DB reset complete. Pre-reset audit archived to <path>. New schema rev: <rev>. <X> tables created. Run /pm sanity-status <project> --schema-version to verify.`

**Confidence:** 🔴 low(destructive DB-level op;requires bootstrap user privilege;PROD guard + literal phrase + pre-archive 3 layer safety net)

**Cross-references:**
- sanity-check REQ-018 C.2(主 acceptance)+ A.3 auto-create + A.6 least privilege + B.3 PROD skip + C1 bootstrap user
- memory `[[delete-dialog-no-undo-hint]]`(literal phrase + 慎思 invariant)
- memory `[[backend-change-rule]]`(bootstrap user GRANT 需 PO 授權 propose)
- 對應 `/pm sanity-cleanup-logs`(per-project rows wipe,less destructive)vs **此 cmd(DB-level reset,catastrophic)**

---

## Sanity TC Family — Pre-flight Invariant(rev 1.17.19 NEW per parent rev 1.27)

> 🎯 **All `/pm sanity-tc-*` commands 都 走 Flask backend cmd handler dispatch chain。** Flask 啟動 需 `SANITY_DB_HOST` / `USER` / `PASSWORD` / `PORT` env vars 才 connect MySQL `sanity_check_DB`。
>
> 📌 **PM Skill agent 自動 pre-flight invariant:** 在 dispatch 任 `/pm sanity-tc-{regenerate / seed-from-generated / coverage / validate / prune}` workflow 之前,先 自動 invoke `/pm sanity-tc-backend start`(idempotent — 若 Flask 已 connected → no-op)。**QA/PM/Developer 不 需 直接 跑 shell command** — pre-flight 對 user 透明。
>
> 🛡 **Per `[[backend-change-rule]]`:** 走 既有 Flask backend cmd handler dispatch(0 backend *.py change);Option A wrapper `app.sh` 是 shell-only ops layer。
>
> 🛡 **Per `[[delete-dialog-no-undo-hint]]`:** `stop` action explicit invocation only(destructive — 會中斷 其他 V3 dev work)。
>
> See `§Subcommand: sanity-tc-backend` for full workflow + `app.sh` + `.env` template usage。

---

## Subcommand: sanity-tc-regenerate(rev 1.17.16 — rev 1.21 cascade — git diff A/M/D/R CRUD branch + pm_tag identity)

> ⭐ **rev 1.17.16 cascade per sanity-check rev 1.21 (commits 4861f03 / 04b738f):** `git diff origin/main --name-status` returns A/M/D/R → per-status CRUD branch with pm_tag content-addressable identity preservation。

> 📌 **rev 1.17.17 cascade pending Phase 4(parent sanity-check rev 1.27 — Round 1-patch C1 fix):** detector scan 將從 `source/` only → **`source/ + archive/`** 2-folder scan(A/M/R 從 `source/` + D 從 `archive/` MD missing-from-source);A/M/R/D 4-branch 走 **Q4=a idempotent D-branch** via `mark_sanity_tc_unavailable` cmd(non-fatal `already_unavailable` error_code on re-run)。**此 section 描述 仍是 rev 1.17.16 既有 design(source/ only scan);Phase 4 detector behavior change(`scripts/sanity_tc_regenerate.py` MODIFY 加 archive/ scan + D-branch dispatch)land 後 才 cascade update。** Per `[[backend-change-rule]]` Phase 4 是 propose-first round,等 PO 「Y go」 才動 *.py。

**Arguments:**
- `<md-file-path>` OR `<tc-id>` (eg. `source/tc-101-bct-create.md` or `TC-101`)
- `--auto-detect` — process all MDs changed vs origin/main (per status)
- `--force` — bypass git diff check; treat all source/ MDs as MODIFIED
- `--dry-run` — parse + Claude extract + snapshot;skip backend cmd
- `--verbose` / `-v` — emit per-step diagnostics

**Implementation:** `scripts/sanity_tc_regenerate.py` (Phase 4 + 5 landed)。

**Workflow per git status:**

1. **Detect actions** via `git diff origin/main --name-status -- docs/pm/sanity-check/test-cases/source/`:
   - `A` (added) / `M` (modified) / `D` (deleted) / `R<sim>` (renamed) — each dispatched separately
2. **A path (NEW TC):**
   - Parse MD frontmatter + 4 sections
   - **Auto-gen pm_tag** if frontmatter `pm_tag:` 缺(per parent rev 1.21 Q2 拍板)— `secrets.token_bytes(5)` → 8-char base32 lowercase
   - **Write back pm_tag** to MD frontmatter via atomic tempfile + os.replace
   - Claude extracts REQ-019 22-field tc_json
   - Strip pm_tag if Claude leaked it (Round 1 B1 invariant defense)
   - POST `/cmd/insert_sanity_tc_definition` with pm_tag as **sibling body field** (NOT in tc_json)
   - Export `generated/<tc>.json` snapshot
3. **M / R path (existing TC modified or renamed):**
   - Read pm_tag from frontmatter (must exist post-Phase 5 backfill)
   - Claude extracts fresh tc_json
   - POST `/cmd/update_sanity_tc_definition` — backend looks up by pm_tag (NOT id) → atomic REMOVE+INSERT preserve pm_tag → resurrect if was tombstoned
4. **D path (MD git-deleted):**
   - **`git show origin/main:<deleted-path>`** extracts prior pm_tag from frontmatter
   - POST `/cmd/mark_sanity_tc_unavailable` — soft tombstone (status='unavailable', unavailable_at=NOW) — preserves row for future `Sanity_Test_Result_TBL` FK integrity (REQ-021 stub)
   - **`already_unavailable` error_code = non-fatal** (idempotent re-run)
5. **Fallback path:** M/R UPDATE returns not_found → orchestrator retries as INSERT (handles post-prune resurrect edge case)
6. **Report:** Summary shows action codes + pm_tag + auto-gen flag + resurrected flag per entry

**Confidence:** 🟡 medium (Claude extraction layer — humans verify generated JSON before PR merge)

**Cross-references:**
- sanity-check rev 1.21 parent (commits 24b8c59 / 718560a / 055b879 / 8839912 / 4861f03 / 04b738f)
- REQ-013 `Sanity_Test_Case_Definition_TBL` 14-column schema (rev 1.21)
- REQ-019 22-field SSOT (rev 1.18)
- REQ-020 TC Lifecycle Workflow SSOT (rev 1.21)
- Round 1 B1 closure: Claude MUST NOT output pm_tag
- Round 1 C3 closure: include_unavailable body field contract

---

## Subcommand: sanity-tc-validate(rev 1.17.16 — rev 1.21 cascade — pm_tag uniqueness + format)

> ⭐ **rev 1.17.16 cascade:** 加 pm_tag format compliance + cross-ref uniqueness check per Round 1 C closure。

**Arguments:**
- `<md-file>` OR `--all` (validate all source/*.md files)
- `--check-drift` — compare MD frontmatter vs `generated/<tc>.json` snapshot
- `--verbose` / `-v` — print per-file pass/fail

**Implementation:** `scripts/sanity_tc_validate.py` (Phase 5 landed)。

**Workflow:**

1. **Parse MD** + frontmatter required fields check (id / title / category / priority / operation_type)
2. **Per-MD format checks:**
   - `id` matches `^TC-\d{3}$` regex
   - **`pm_tag` matches `^[a-z2-7]{8}$` regex** if present (rev 1.21 NEW invariant)
   - `legacy_id` matches `^TC-\d{3}$` regex if present
   - `category` × ID range alignment (BCT 100-199 / Friend 200-299 / Schedule 300-399 / Profile 400-499 / OCR 500-599 / Coupon 600-699 / Auth 700-799 per REQ-019 100-799 convention)
3. **Cross-ref uniqueness checks:**
   - **`pm_tag` collision detection across MDs** (rev 1.21 NEW)
   - `legacy_id` collision detection
   - `id` collision detection
4. **Drift detection (`--check-drift`):** Compare MD vs `generated/<tc>.json` snapshot — surface stale TCs (MD changed but not regenerated)
5. **Report:** summary with passed / per-file errors / cross-ref errors / drift errors counts;non-destructive

**Confidence:** 🟢 high (read-only validation,no writes)

**Use case:** Pre-PR check + CI gate to catch pm_tag collisions early before they propagate to DB UNIQUE INDEX violation。

---

## Subcommand: sanity-tc-prune(rev 1.17.15 — admin hard-delete escape hatch + Round 1 NIT clarification)

> 📌 **rev 1.21 cascade clarification(per Round 1+2 audit-patch NIT):** This is the **admin HARD-DELETE escape hatch** — physical row removal,distinct from regenerate D path which走 soft tombstone via `mark_sanity_tc_unavailable` cmd。Future `Sanity_Test_Result_TBL` FK RESTRICT 反擋 if result rows reference this TC (雙層 safety per [[delete-dialog-no-undo-hint]] 慎思)。

**Arguments:** `<tc-id>` `--confirm-with "yes-prune-tc-<id-lowercase>"` (literal,case-sensitive)

**Workflow:**

1. Verify confirm phrase exact match (per [[delete-dialog-no-undo-hint]] 慎思 invariant)
2. Detect MD path: `source/tc-<id-num>-<slug>.md`
3. Backend cmd: POST `/cmd/delete_sanity_tc_definition` with `{id, confirm_phrase}`:
   - `error_code='literal_phrase_mismatch'` → backend rejected — phrase typo
   - `error_code='not_found'` → no row to delete
   - `error_code='fk_restricted'` → future Sanity_Test_Result_TBL FK 反擋 — must hard-delete result rows first or keep tombstoned
   - success → row physically removed
4. Delete corresponding `generated/<tc-id>.json` snapshot
5. Optional: remove MD source file manually (PM commit removal)
6. Audit log entry (future via `Sanity_Lifecycle_Audit_TBL` per REQ-017 G.5)

**Confidence:** 🔴 low (destructive — manual confirm + literal phrase + FK RESTRICT 雙層 safety)

**Use case:** Admin override for old TCs that should be permanently removed (eg. consolidation cleanup);regenerate D path soft tombstone is the normal removal flow。

---

## Subcommand: sanity-tc-coverage(rev 1.17.16 — rev 1.21 cascade — by-page filter + admin tombstone view)

> ⭐ **rev 1.17.16 cascade:** 加 `--page` JSON path filter (Option A YAGNI per parent rev 1.21 Q1=A 拍板) + `--include-unavailable` admin view (per Round 1 C3 body field contract)。

**Arguments:**
- `--diff` — show delta vs previous commit (deferred — see OQ)
- `--category <C>` — filter to single category (BCT/Profile/Schedule/Friend/OCR/Coupon/Auth)
- **`--page <spa_path>`** — filter by tc_json.target_spa_path substring (rev 1.21 NEW)
- `--format <markdown|table|json>` (default markdown)
- **`--include-unavailable`** — show tombstoned TCs (admin view; default OFF) (rev 1.21 NEW per Round 1 C3 contract)
- `--verbose` / `-v`

**Implementation:** `scripts/sanity_tc_coverage.py` (Phase 5 landed)。

**Workflow:**

1. POST `/cmd/query_sanity_tc_definitions` with body `{}` (default runtime drawer view) OR `{"include_unavailable": true}` (admin view)
2. Apply optional filters client-side (category / page via JSON path query)
3. Build matrix: category × operation_type × priority cross-product
4. Render per `--format`:
   - **markdown:** report with header + matrix table + per-category detail + tombstoned admin section (if --include-unavailable)
   - **table:** fixed-width pipe table (id / cat / pri / op / status / pm_tag)
   - **json:** raw matrix object for piping to other tools

**Confidence:** 🟢 high (read-only aggregation)

**Use case:** 3-role meeting prep — PM/QA/Dev 用此 report 看 coverage 演進 + 討論 gap 補強優先順序。Admin --include-unavailable 看 tombstone history 對 post-mortem 友善。

---

## Subcommand: sanity-tc-db-bootstrap(rev 1.17.16 NEW — rev 1.21 cascade 5th subcommand)

> ⭐ **rev 1.17.16 NEW per parent rev 1.21 layer E 5th subcommand directive** + PO 2026-06-26 「PM skill add new command for creating sanity check database & table for test case in local mysql server」拍板。Local MySQL dev setup walk-through — Azure substring refuse safeguard + literal phrase --reset。

**Arguments:**
- `--with-seed` — chain `/pm sanity-tc-regenerate --auto-detect --force` after schema for 16-TC initial backfill
- `--reset` (destructive) — DROP + recreate;requires `--confirm-with "yes-reset-local-sanity-db"` literal phrase
- `--confirm-with "<phrase>"` — literal confirmation for --reset (per [[delete-dialog-no-undo-hint]] 慎思)
- `--dry-run` — print mysql command without executing
- `--verbose` / `-v` — emit per-step diagnostics

**Implementation:** `scripts/sanity_tc_db_bootstrap.py` (Phase 5 landed)。

**Workflow:**

1. **Local-only safeguard check:**
   - Read `SANITY_DB_HOST` env (default `localhost`)
   - **Refuse** with exit code 2 if host contains `azurewebsites.net` / `mysql.database.azure.com` / `.azure.` substrings
   - For Azure/production schema cascade, use backend startup auto-sync rev 1.1 instead per [[backend-schema-change-workflow]]
2. **`--reset` literal phrase check:**
   - If `--reset` set without matching `--confirm-with "yes-reset-local-sanity-db"` → exit code 3
3. **SSOT execution:**
   - subprocess shell out: `mysql -h <host> -P <port> -u <user> [-p<password>] < sanity_db_create_tables.sql`
   - SSOT discipline:純執行 SSOT,**不** duplicate schema in PM Skill
   - Idempotent:SSOT uses `CREATE DATABASE IF NOT EXISTS` + `CREATE TABLE IF NOT EXISTS` for log
4. **`--with-seed` chain** (post-schema):
   - Run `python3 scripts/sanity_tc_regenerate.py --auto-detect --force` against source/ for 16-TC initial backfill
   - Per parent rev 1.21 Q3 git-diff-drives-CRUD: backfill replaces deprecated `seed/rev-1.18-seed.sql` path
5. **Post-bootstrap message:** 提示 Stage 2 UNIQUE INDEX promotion is manual or PM Skill follow-up (per design spec § 5.2)

**Confidence:** 🟢 high (schema is read-only SSOT,backfill via existing regenerate path)

**Exit codes (per design spec § 9.5.5 test scenarios):**
- 0 — success
- 2 — Azure host substring refused
- 3 — wrong/missing --reset literal phrase
- 4 — SSOT SQL file missing
- 5 — mysql CLI not on PATH or SSOT not readable
- 6/7 — internal helper script failures
- other — propagated from mysql CLI subprocess

**Use case:** Dev 新 setup local MySQL (no Flask running yet)— bootstrap walks SSOT execution + optional 16-TC seed for immediate sanity test runner availability。

---

## Subcommand: sanity-tc-create(rev 1.17.17 NEW — rev 1.27 cascade — Claude-as-gate 4-folder discipline)

> ⭐ **rev 1.17.17 NEW per parent sanity-check rev 1.27 directive**「Claude-as-gate MD mutation discipline + 4-folder TC source layout」+ PO 2026-06-28 6 拍板(Q1=a edit/ git tracked)。Claude 自然語言 → MD draft to `edit/`。**人類不可直接編** `source/` 或 `archive/` MD — 走此 subcommand entry。

**Arguments:**
- `"<NL spec>"` — 自然語言描述 TC 範圍 / cover scenario / fake data / validate prompts 等

**Implementation:** PM Skill 對話式 — Claude Edit/Write tool 寫 MD(per rev 1.27 spec-only,0 *.py change;對齊 `[[backend-change-rule]]`)。

**Workflow:**

1. **Parse NL spec** — Claude extract REQ-019 23-field 必要欄位(category / priority / operation_type / target_strategy / target_spa_path or target_url 等)
2. **Auto-gen TC-ID** — scan `source/` + `edit/` + `archive/` 找下個可用 ID(per REQ-019 100-799 convention 對應 category:BCT 100-199 / Friend 200-299 / Schedule 300-399 / Profile 400-499 / OCR 500-599 / Coupon 600-699 / Auth 700-799)
3. **Auto-gen pm_tag** — `secrets.token_bytes(5)` → 8-char base32 lowercase(per rev 1.21 content-addressable identity invariant)
4. **Schema validate** — REQ-019 23-field + rev 1.22 anti-pattern table 自動 enforce(過長 description > 200 char / dev jargon smoke/regression/dispatcher / `[[memory]]` refs)
5. **Write MD** — `docs/pm/sanity-check/test-cases/edit/tc-<id>-draft.md` 含 frontmatter + 4-section MD body(👔 PM Lens / 🔬 QA Lens / 💻 Developer Lens / 📝 QA Notes per `[[human-first-docs]]`)
6. **Report** — PO review path + suggest next step `/pm sanity-tc-confirm tc-<id>`

**Confidence:** 🟡 medium(Claude extraction layer + schema discipline + PO confirm gate)

**Cross-references:**
- parent req-spec rev 1.27 § 8 Glossary 「Claude-as-gate MD mutation discipline」 + 「4-folder TC source layout」
- REQ-019 23-field schema(rev 1.22 cascade)
- `/pm sanity-tc-confirm` promote path
- `/pm sanity-tc-discard` 棄掉 path

---

## Subcommand: sanity-tc-update(rev 1.17.17 NEW — rev 1.27 cascade — Claude clone source/ → edit/ pending-update)

> ⭐ **rev 1.17.17 NEW per parent sanity-check rev 1.27 directive**。Claude clone existing `source/` MD → `edit/` patch draft。**人類不可直接編** `source/` MD。

**Arguments:**
- `<TC-id>` — eg. `TC-104`
- `"<patch desc>"` — 自然語言描述變更(eg. 「把 timeout 改成 90 sec」 / 「加 negative variant boundary scenario」)

**Workflow:**

1. **Locate source/** — find `source/tc-<id-num>-<slug>.md`;若 not found → error
2. **Clone to edit/** — copy → `edit/tc-<id>-pending-update.md`(保留 pm_tag + 既有 metadata)
3. **Apply patch** — Claude 對齊 NL 描述 patch 對應欄位(frontmatter or MD section)
4. **Schema validate** — REQ-019 23-field + rev 1.22 anti-pattern
5. **Diff report** — PO 看 patch 對比 source/ 樣
6. **Report** — suggest `/pm sanity-tc-confirm tc-<id>` 套用,或 `/pm sanity-tc-discard tc-<id>` 棄

**Confidence:** 🟡 medium

**Cross-references:**
- `/pm sanity-tc-confirm` promote path(overwrites source/)
- `/pm sanity-tc-create` for brand new TC
- REQ-019 23-field schema

---

## Subcommand: sanity-tc-archive(rev 1.17.17 NEW — rev 1.27 cascade — Claude tombstone draft)

> ⭐ **rev 1.17.17 NEW per parent sanity-check rev 1.27 directive**。Claude clone existing `source/` → `edit/` tombstone draft;PO confirm 後 move 到 `archive/` → detector D-branch soft delete via `mark_sanity_tc_unavailable`。

**Arguments:**
- `<TC-id>` — eg. `TC-XXX`
- `--reason "<text>"` — required;落 git commit message(per Q5 不加 deprecation metadata field 進 spec — reason 全留 git history)

**Workflow:**

1. **Locate source/** — find `source/tc-<id>-<slug>.md`
2. **Clone to edit/** — copy → `edit/tc-<id>-pending-archive.md`(完整內容保留 + pm_tag 不變)
3. **Report** — preview「將歸檔 TC-XXX(`<title>`)」 + suggest `/pm sanity-tc-confirm tc-<id>`(confirm)或 `/pm sanity-tc-discard tc-<id>`(棄)

**Confirm 路徑(走 `/pm sanity-tc-confirm`):**
- `git mv edit/tc-<id>-pending-archive.md archive/tc-<id>.md`
- `git rm source/tc-<id>-<slug>.md`
- `git commit -m "archive: TC-<id> per <reason>"`(reason 從 archive command `--reason` flag 帶入 commit message)
- Phase 4 detector 之後跑 `/pm sanity-tc-regenerate --auto-detect` → D-branch soft delete DB row(Q4=a idempotent)

**Confidence:** 🔴 low(destructive intent — 走 `confirm` literal phrase 慎思 + DB soft delete 雙層 safety per `[[delete-dialog-no-undo-hint]]`)

**Cross-references:**
- parent req-spec rev 1.27 § 8 Glossary 「`archive/` folder」+ Q4=a idempotent
- `mark_sanity_tc_unavailable` backend cmd(rev 1.21)
- `/pm sanity-tc-prune` admin hard-delete escape hatch(rev 1.17.15 distinct from soft tombstone)

---

## Subcommand: sanity-tc-confirm(rev 1.17.17 NEW — rev 1.27 cascade — promote edit/ → source/ or archive/)

> ⭐ **rev 1.17.17 NEW per parent sanity-check rev 1.27 directive**。Promote `edit/` draft → `source/`(create / update)or `archive/`(archive)per suffix。**Q2=a 拍板 multi-draft 衝突 fail-fast** — 同 TC ≥ 2 draft 同存 一律 fail。

**Arguments:**
- `<tc-id>` — eg. `tc-104` 或 `TC-104`(case-insensitive),OR
- `--all` — promote 全 `edit/` 內 draft(Phase 5 dogfood re-confirm cycle 用)

**Workflow:**

1. **Scan edit/ for matching draft** — `edit/tc-<id>-*.md`(`-draft` / `-pending-update` / `-pending-archive`)
2. **Q2=a fail-fast uniqueness check** — 若 同 TC-id 找到 ≥ 2 draft → error + 列出 conflicting drafts + 要求 PO 先 `/pm sanity-tc-discard tc-<id>` 一個
3. **Suffix-based promote(Round 1-patch C2 fix:source slug 推導 invariant inline):**
   - `-draft.md` → `git mv edit/tc-<id>-draft.md source/tc-<id>-<slug>.md`(create new TC — slug 從 frontmatter title derive 或 NL spec 提示)
   - `-pending-update.md` → **source slug 推導:glob `source/tc-<id>-*.md` 找對應(必唯一;0 match → fall-back to A-branch new TC INSERT;≥ 2 match → fail-fast cross-collision error)** → overwrite `source/tc-<id>-<slug>.md` ← `edit/tc-<id>-pending-update.md` + `rm edit/`
     - **Re-confirm semantic(Round 1-patch B1 fix):** `-pending-update` suffix on a draft whose content matches `source/` byte-for-byte(eg. PHASE-7-RUNBOOK § 0.6.3 Phase 5 dogfood batch re-confirm cycle)→ promote 仍走;git commit history 留 audit trail(無 content delta — re-stamp 對齊 dogfood discipline)
   - `-pending-archive.md` → `git mv edit/tc-<id>-pending-archive.md archive/tc-<id>.md` + `git rm source/tc-<id>-<slug>.md`(slug 同 source/ glob 推導 — per C2 invariant 同 `-pending-update` 路徑)
4. **Git commit** — auto-stamp commit message based on operation(`create:` / `update:` / `archive:` / `re-confirm:` prefix)
5. **`--all` batch mode:** iterate 全 `edit/` TCs;single commit batch + 列 promote summary

**Confidence:** 🟢 high(deterministic git mv + suffix dispatch + fail-fast guard)

**Cross-references:**
- parent req-spec rev 1.27 § 8 Glossary 「`edit/` folder」 Q2=a fail-fast invariant
- `/pm sanity-tc-create / update / archive` upstream draft entries
- `/pm sanity-tc-regenerate --auto-detect` downstream DB sync(Phase 4 detector behavior change)

---

## Subcommand: sanity-tc-discard(rev 1.17.17 NEW — rev 1.27 cascade — rm edit/ draft)

> ⭐ **rev 1.17.17 NEW per parent sanity-check rev 1.27 directive**。Discard `edit/` draft;不影響 confirmed `source/` 或 `archive/`(staging only)。

**Arguments:**
- `<tc-id>` 或 `--all`

**Workflow:**

1. **Scan edit/ for matching draft** — `edit/tc-<id>-*.md`
2. **Confirm dialog** — list draft 內容 + 提示「將棄掉 N 個 `edit/` draft;此操作不影響 `source/` confirmed TC」(per `[[delete-dialog-no-undo-hint]]` 慎思 wording — 純粹說明 staging only,不暗示「軟刪 / 可還原」)
3. **rm edit/ matched draft(s)** — `git rm edit/tc-<id>-*.md`
4. **Git commit** — `discard: <N> edit/ draft(s)`

**Confidence:** 🟢 high(non-destructive — staging only;confirmed `source/` + `archive/` 不動)

**Cross-references:**
- `/pm sanity-tc-confirm` 互斥 path
- parent req-spec rev 1.27 § 8 Glossary 「`edit/` folder」 staging only invariant

---

## Subcommand: sanity-tc-seed-from-generated(rev 1.17.18 NEW — rev 1.27 cascade — JSON snapshot → DB sync skip Claude extract)

> ⭐ **rev 1.17.18 NEW per parent sanity-check rev 1.27 cascade** + PO 2026-06-28 「let pm skill convert JSON to tc table」 directive + 「Y go path (ii)」 authorize per `[[backend-change-rule]]`。**Implementation backend:** `scripts/sanity_tc_seed_from_generated.py`(stdlib only,~210 LOC)。

**Use case:** DB sync drift recovery + cost-conscious dogfood — 既有 `docs/pm/sanity-check/test-cases/generated/*.json` snapshots(從 previous regen cycle commit a78d552 + 後續 cascade)是 ground truth,**不需 重跑 30-50 min Claude extract**,直 POST 到 backend cmd handler 進 DB(`update_sanity_tc_definition` 主 path + fallback `insert_sanity_tc_definition` if `not_found`)。TC-104 sticky 60s Claude timeout 場景 也 透過 既有 51 snapshots ship 98%(missing 1 TC = TC-104 sticky 後續 dedicated fix)。

**Arguments:**
- `--limit N`(default 0 = all)— Process at most N JSON snapshots,for spot-check(eg. `--limit 1` 跑 1 TC verify chain)
- `--dry-run` — Assemble payload + 印 dispatch detail 但 skip backend POST(safe preview)
- `--verbose` / `-v` — per-TC dispatch detail print
- `--schema-rev <tag>`(default `rev-1.22`)— Schema rev tag stamp for audit row

**Workflow:**

1. **Glob `generated/tc-*.json`** — 既有 ~52 snapshots
2. **Per JSON:**
   - 從 對應 `source/<basename>.md` frontmatter 讀 `pm_tag`(per rev 1.21 content-addressable identity invariant)
   - 若 `pm_tag` 缺 → error report + skip(不 auto-gen — 這 是 seed-from-existing,不是 fresh create path)
   - Load JSON content + strip `pm_tag` if leaked(Round 1 B1 defense)
   - Build payload(同 `regenerate.py _dispatch_backend_cmd` payload shape — `pm_tag` sibling body field NOT in tc_json)
3. **`--dry-run`:** print intent + skip POST
4. **Live POST cascade:**
   - Try `update_sanity_tc_definition`(pm_tag lookup)
   - If `not_found` → fallback `insert_sanity_tc_definition`
   - Other errors → log + continue next TC
5. **Summary report:** inserted / updated / errors with per-TC `[cmd][ok/error]` line

**Env vars:**
- `SANITY_TC_BACKEND_BASE_URL`(default `http://localhost:8000`)— Flask backend base URL(set `http://localhost:5400` if Flask 跑 5400)
- `SANITY_TC_UPDATED_BY`(default `pm-skill-seed-cli`)— audit trail user identity
- `SANITY_TC_SCHEMA_REV`(default `rev-1.22`)— Override schema rev tag

**Confidence:** 🟡 medium(DB write + idempotent retry)— `[[delete-dialog-no-undo-hint]]` discipline:**0 destructive intent**(additive INSERT/UPDATE only;0 DELETE / 0 mark_unavailable;dry-run safe preview default suggested for first run)

**Cross-references:**
- parent req-spec rev 1.27 § 8 Glossary 「`generated/` JSON snapshots」 + 「4-folder TC source layout」
- `scripts/sanity_tc_seed_from_generated.py`(implementation)
- `scripts/sanity_tc_regenerate.py`(sibling — full Claude extract pipeline;use this when source/ MDs delta vs generated/)
- REQ-019 23-field schema(rev 1.22 cascade)
- 既有 backend cmd handlers `insert_sanity_tc_definition` + `update_sanity_tc_definition`(rev 1.21 Phase 3 commit 8839912)

**Distinction from sibling commands:**

| Command | Trigger source | Skip Claude? | Use case |
|:---|:---|:---:|:---|
| `/pm sanity-tc-regenerate` | source/ MD + git diff | ❌ | Source MD content delta + DB sync(完整 pipeline)|
| `/pm sanity-tc-seed-from-generated`(NEW)| 既有 generated/ JSON | ✅ | DB sync drift recovery(snapshot ground truth ready)|

**Typical first-run pattern:**
```
# Spot-check 1 TC chain works:
/pm sanity-tc-seed-from-generated --limit 1 --verbose

# Verify DB row delta:
mysql -e "SELECT COUNT(*) FROM sanity_check_DB.Sanity_Test_Case_Definition_TBL"

# Full batch (52 TCs ~5 min POST cycle):
/pm sanity-tc-seed-from-generated --verbose
```

---

## Subcommand: sanity-tc-backfill-pm-tag(rev 1.17.20 NEW — rev 1.28 cascade — legacy pm_tag backfill discipline)

> ⭐ **rev 1.17.20 NEW per parent sanity-check rev 1.28 cascade + PO 2026-06-28 「why more 30 tc lose the pm tag, root cause + solution + 3 specs」 directive。**
>
> **Why:** Pre-rev-1.27 era 53 source/ MDs 分 2 cohort:(a)16 初始 TCs(Phase 4 stubs commit 9a1fb31)走 Phase 7 Step 2 `sanity-tc-regenerate` auto-gen pm_tag cycle 取得 pm_tag in frontmatter ✅;(b)37 後續 batches 直接編 MD 跳過 PM Skill workflow → 沒 pm_tag ⚠。**`/pm sanity-tc-seed-from-generated` requires pm_tag(per design — 不 auto-gen)** → 37 TCs missing pm_tag 報 error。**rev 1.27 Claude-as-gate prevents recurrence**;此 subcommand 是 **one-time backfill for legacy migration**。

**Arguments:**
- `--dry-run` — Scan + log gen 但不 write to MD files(safe preview)
- `--verbose` / `-v` — per-MD diagnostic
- `--limit N` — process at most N files(spot-check)

**Implementation:** `scripts/sanity_tc_pm_tag_backfill.py`(NEW propose-first,~80 LOC stdlib,reuse 既有 `sanity_tc_pm_tag_gen.gen_pm_tag()` + `write_pm_tag_back()` helpers)。

**Workflow:**

1. **Glob `source/*.md`**
2. **Per MD:** parse frontmatter via `parse_md_file` sibling helper
3. **Check `pm_tag` key in frontmatter:**
   - If present → skip(no-op)
   - If missing → gen via `gen_pm_tag()`(8-char base32 lowercase per rev 1.21 invariant)
   - Write back via `write_pm_tag_back(md_path, tag)` atomic tempfile + os.replace
4. **`--dry-run`:** print intent + skip write
5. **Report summary:** N processed / N backfilled / N already-have / N errors

**Pre-flight chain:** **不需** `/pm sanity-tc-backend start`(0 backend dependency — 純 file mutation)。

**Confidence:** 🟢 high(additive only — 加 frontmatter field 不 mutate body content;0 Claude call,0 DB write,0 destructive intent per `[[delete-dialog-no-undo-hint]]`)

**Cross-references:**
- parent req-spec rev 1.28 § 8 Glossary 「Authoring discipline gap」 + 「pm_tag backfill discipline」
- `scripts/sanity_tc_pm_tag_backfill.py`(implementation,propose-first)
- `scripts/sanity_tc_pm_tag_gen.py`(既有 helper)
- `scripts/sanity_tc_md_parser.py`(既有 helper for parse + write_pm_tag_back)
- Sibling `sanity-tc-regenerate` Auto-gen path(does same thing 但 with Claude extract overhead;backfill is cost-optimized for pm_tag only)

**Typical use:**

```
# First-time backfill (post-rev 1.28 dogfood discovery)
/pm sanity-tc-backfill-pm-tag --dry-run --verbose      # preview (predicted 37 missing)
/pm sanity-tc-backfill-pm-tag --verbose                # actual backfill
git commit -m "chore(sanity): backfill pm_tag in 37 legacy source/ MDs"
/pm sanity-tc-seed-from-generated --verbose            # now 52 INSERT/UPDATE succeed
/pm sanity-tc-coverage --format table                  # verify 52/53 final DB state
```

**Future:** rev 1.27 Claude-as-gate prevents recurrence;backfill is one-time migration utility(may stay forever for legacy/import scenarios where bulk pm_tag-less MDs need adoption)。

---

## Subcommand: sanity-tc-backend(rev 1.17.19 NEW — rev 1.27 cascade — Flask startup auto-management)

> ⭐ **rev 1.17.19 NEW per parent sanity-check rev 1.27 cascade + PO 2026-06-28 「A is ok」 + 「PM Skill 自動 run」 directive。**
>
> **Why:** All `/pm sanity-tc-*` commands 走 Flask backend cmd handler dispatch。Flask 啟動 需 `SANITY_DB_*` env vars 才 connect MySQL sanity_check_DB。此 subcommand 自動 handle Flask lifecycle,QA/PM/Developer 不 直接 跑 shell。

**Arguments:**
- `start`(default)— Idempotent start;若 Flask 已 connected → no-op;若 沒 → start with env via `app.sh`
- `restart` — Kill existing Flask + start new with env(用 fix env drift / config refresh)
- `status` — Report Flask process(es) + sanity_check_DB connection state
- `stop` — Kill Flask(destructive — 中斷其他 V3 dev work,explicit invocation only)

**Implementation:**
- `app.sh`(internal shell wrapper,git-tracked)— Flask process lifecycle + env source
- `.env`(local secrets,git-ignored)— `SANITY_DB_HOST` / `USER` / `PASSWORD` / `PORT`
- `.env.example`(template,git-tracked)— sanity section appended per rev 1.27

**Workflow:**

1. **Read `.env`** — auto-source via `set -a; source .env; set +a`
2. **Validate required env** — fail-fast if `SANITY_DB_USER` / `PASSWORD` / `HOST` missing
3. **Per action dispatch:**
   - **`start`:** `pgrep -f "python.*app\\.py"` — if existing Flask + sanity_check_DB connected → no-op;else spawn `python3 app.py` 帶 sanity env via `nohup`
   - **`restart`:** kill existing PIDs + start new(同 `start` impl)
   - **`status`:** report `ps` + curl POST `query_sanity_tc_definitions` → 看 `success: true` 或 fail reason
   - **`stop`:** kill all `pgrep -f "python.*app\\.py"` PIDs
4. **Boot wait 5 sec** + verify backend cmd handler reachable + sanity_check_DB connected via curl
5. **Report** — PID + status + connection result

**Pre-flight chain invariant(PM Skill agent 自動 invocation):**

When QA/PM 跑 `/pm sanity-tc-{regenerate / seed-from-generated / coverage / validate / prune}`,PM Skill workflow internally **自動 invoke `/pm sanity-tc-backend start`**(idempotent)before main workflow runs。**QA/PM/Developer 不需 自己 跑** — pre-flight 對 user 透明。Per Sanity TC Family Pre-flight Invariant section above。

**Confidence:** 🟢 high(idempotent start + verify boot success + fail-fast env validation;stop 走 explicit invocation only per `[[delete-dialog-no-undo-hint]]`)

**Cross-references:**
- `app.sh`(implementation backend — shell wrapper,0 *.py change per `[[backend-change-rule]]`)
- `.env.example`(sanity section appended per rev 1.27)
- PHASE-7-RUNBOOK § 0 Pre-conditions(rev 1.27 cascade — 自動 handle replace manual env setup)
- 既有 sanity-tc-* family 12 commands — pre-flight chain target

**First-time dev setup(QA/PM 跑 1 次):**

```
cp .env.example .env
vim .env                          # fill SANITY_DB_PASSWORD with mysql root pwd
/pm sanity-tc-backend start       # → Flask up + sanity_check_DB connected ✅
```

**Daily dev workflow(PM Skill 自動 handle):**

```
/pm sanity-tc-seed-from-generated --limit 1 --verbose
   # PM Skill 內部自動:
   #   1. /pm sanity-tc-backend start  (idempotent → no-op if up)
   #   2. dispatch sanity-tc-seed-from-generated workflow
   #   3. report result
```

**Env drift fix:**

```
/pm sanity-tc-backend restart     # kill + start with fresh env
```

---

## Subcommand: sanity-tc-edit-list(rev 1.17.17 NEW — rev 1.27 cascade — staging visibility)

> ⭐ **rev 1.17.17 NEW per parent sanity-check rev 1.27 directive**。Read-only diagnostic — scan `edit/` → markdown table report。

**Arguments:** 無

**Workflow:**

1. **Scan edit/** — glob `edit/tc-*.md`
2. **Per-draft parse** — frontmatter `id` + `title` + mtime + suffix kind
3. **Render markdown table:**

| TC-ID | Title | Suffix | mtime | Action(suggested) |
|:---|:---|:---|:---|:---|
| TC-104 | timeout fix | pending-update | 2026-06-28 14:30 | `/pm sanity-tc-confirm tc-104` |
| TC-XXX | scenario obsolete | pending-archive | 2026-06-28 14:35 | `/pm sanity-tc-confirm tc-XXX` |
| TC-YYY | new identity flow | draft | 2026-06-28 14:40 | `/pm sanity-tc-confirm tc-YYY` |

4. **Multi-draft conflict warning** — 同 TC-id ≥ 2 draft → highlight + suggest `discard`(per Q2=a fail-fast preemptive surface)

**Confidence:** 🟢 high(read-only)

**Cross-references:**
- parent req-spec rev 1.27 § 8 Glossary 「`edit/` folder」 staging visibility
- `/pm sanity-tc-confirm` Q2=a fail-fast 衝突 catch

---

## Subcommand: rollback(new in v1.2 — zero-downtime swap-back)

> ⚠ **RUNTIME PREREQUISITE**(v1.1.10 added):此命令依 **Azure CLI(`az`)+ Azure auth + `azure-config.yaml`**(對齊 deploy 同要求)。**Run `/pm verify-runtime` first**。若 Azure CLI 未裝/未 auth → 真實 incident 撞到 = 無法 rollback,**emergency PATH 失效**。預先設好是 Phase 6 entry 紀律一部分。

> 對齊 proposal §6.4.11 §G.6.2。**Emergency PATH(對齊 §K.3),非 deploy bypass**。Zero-downtime Azure slot swap-back。

**Arguments:**
- `--to <commit>`(optional;default = previous prod tag)
- `--reason <text>`(required)

**Trigger:**
- PO manual(incident response)
- Auto:`/pm deploy` post-deploy smoke fail(對齊 §G.6.1 safety net)

**Preconditions:**
- `last_deploy_at` set(必有可 rollback 的 deploy)
- `azure_slot_state` in [swapped, failed]

**Workflow:**

0. **Apply mainline-forbidden guard**(rev 1.17.3 §E.8.8.2 — see Shared Guard section above)。Abort if active=mainline。Note: rollback applies to project phases,not mainline maintenance ops。
1. **Display rollback summary:**
   - 當前 prod commit vs target rollback commit
   - 影響的 feature list(diff)
   - PO confirm:型 `ROLLBACK`(對齊 confirmation_phrase pattern)

2. **Execute Azure rollback — SKU-aware**(對齊 `azure-config.yaml` `rollback_strategy` + spectra v1.1.10 C2 fix):

   2.0 Read `azure-config.yaml`:
   ```bash
   APP_NAME=$(yq '.web_app.name' azure-config.yaml)
   RG=$(yq '.resource_group' azure-config.yaml)
   STRATEGY=$(yq '.web_app.rollback_strategy' azure-config.yaml)
   ```

   2.1 **IF `rollback_strategy: slot_swap_back`(Standard+ SKU,zero-downtime):**
   ```bash
   SLOT_STAGING=$(yq '.web_app.slots.staging' azure-config.yaml)
   SLOT_PROD=$(yq '.web_app.slots.production' azure-config.yaml)
   az webapp deployment slot swap --resource-group "$RG" \
     --name "$APP_NAME" --slot "$SLOT_PROD" --target-slot "$SLOT_STAGING"
   # Effectively undo last swap(staging slot 仍保有 previous prod build)
   # 預期 < 60s(對齊 §G.6.2 SLA)
   ```

   2.2 **IF `rollback_strategy: redeploy_previous_tag`(Basic SKU,~30s downtime):**
   ```bash
   # Find previous release tag
   PREV_TAG=${ARGS_TO:-$(git tag --sort=-creatordate | grep '^release-' | sed -n '2p')}
   if [ -z "$PREV_TAG" ]; then
     echo "❌ No previous release tag found; cannot rollback"
     exit 1
   fi
   
   # Checkout previous tag in detached HEAD (safe)
   ORIG_BRANCH=$(git branch --show-current)
   git checkout "$PREV_TAG"
   
   # Build ZIP from previous tag's tree
   zip -r /tmp/rollback.zip . \
     -x '.git/*' '__pycache__/*' 'node_modules/*' '.venv/*' '*.log' '.env*'
   
   # Redeploy 上一版本
   az webapp deploy --resource-group "$RG" --name "$APP_NAME" \
     --src-path /tmp/rollback.zip --type zip --async false
   
   # Return to original branch
   git checkout "$ORIG_BRANCH"
   rm /tmp/rollback.zip
   ```

3. **若需 hard rollback to older commit** — ⚠ **二次 confirmation gate**(spectra v1.1.8 Round 1 C2 fix):

   3.1 SKILL 顯示 destructive operation warning:
   ```
   ⚠ Hard rollback uses `git push --force` on staging slot.
     This rewrites staging history (irreversible).
     Staging != main/master, but force-push 仍 destructive。
   
     Type 'FORCE STAGING' to confirm (對齊 K.8 confirmation_phrase pattern):
   ```
   
   3.2 PO 必輸 confirmation phrase(對齊 §K.8 pattern):
   - Match `FORCE STAGING` exact:proceed Step 3.3
   - Mismatch:abort + 建議 soft rollback(slot swap-back only,Step 2 already done)
   
   3.3 Execute hard rollback:
   ```bash
   git checkout <commit>
   git push origin HEAD:staging --force-with-lease  # safer than --force
   az webapp deploy --slot staging --src-path .
   az webapp deployment slot swap --name <app> --slot staging --target-slot production
   ```
   
   > **`--force-with-lease` vs `--force`:** lease 模式只在 remote 沒被別人 push 過時才允許 force(對齊 multi-engineer team safety)。1-PO 場景兩者等效,但 5-engineer 場景 lease 救 race condition。對齊 CLAUDE.md 「safer alternative」原則。
   
   3.4 Append decision-log:
   ```
   D-pm-<seq>: Hard rollback on staging via force-with-lease. from=<sha> to=<commit>. by=PO at=<ISO>.
   ```

4. **Post-rollback smoke test** (對齊 §G.1 schema)。

5. **Update state.md:**
   ```yaml
   phase_6_signoff: false           # rollback 後 Phase 6 需重新 sign off
   last_rollback_at: <ISO8601>
   last_rollback_reason: <text>
   last_rollback_commit: <sha>
   ```

6. **Append decision-log:**
   ```
   D-pm-<seq>: rollback. from=<bad-commit> to=<good-commit>. reason: <text>. by=PO at=<ISO>.
   ```

7. **24-hour root cause requirement**(對齊 §G.6.2 audit):
   - state.md flag `root_cause_documentation_due_at: <ISO + 24h>`
   - SKILL 每次 invoke 提示「⚠ <X> hours remaining to document root cause」直到 documented

8. **Optionally prompt:**
   ```
   Open /pm-bug-review for incident triage? (y/N)
   ```

**Output:**
```
↩ /pm rollback — VERDICT: ✅ SUCCESS

Rolled back: <bad-commit> → <good-commit>
Azure slot state: rolled_back (took 53s)
Post-rollback smoke: ✅ all pass

Audit:
  state.md updated (phase_6_signoff=false, last_rollback_*)
  decision-log: D-pm-<seq> appended
  root_cause_documentation_due_at: 2026-06-19 14:00 (24h)

⚠ Required next:
  1. Document root cause in 24h (對齊 §G.6.2)
  2. /pm-bug-review <slug>(if incident severe)
  3. Fix root cause + 走完整 SDLC re-deploy(對齊 §K.3 — rollback PATH,not bypass)
```

**Edge cases:**
- No previous deploy → abort + 提示「No deploy to rollback to」
- Rollback target commit 不存在 → abort
- Azure CLI fail → flag manual swap required + escalate
- 24h root cause 未 document → SKILL 在 `/pm status` 顯示紅旗 banner

**Confidence Tier:** 🔴 low(production-impacting,比 deploy 風險高 — 已壞才回退)

**Cross-references:** proposal §G.6.2 / §K.3(emergency PATH)/ §K.9(rollback 不算 override)/ §10.7 stop loss / `/pm-bug-review`

---

## Subcommand: build-team(**v1.4-validated-candidate** — 3 real invocations + 11 findings closed 2026-06-19)— NL→YAML team management,對齊 proposal §6.4.14

> **Workflow Lifecycle Stage:** `v1.4-validated-candidate`(對齊 proposal §6.4.15)— 3 invocations done(#18 mixed + #19 inquire + #20 refuse path);11 findings(4 BUG + 7 NIT)全 actionable closed;**待 14 day stable + 0 new critical** → promote to `v1.4`(production-ready)。

> 對齊 PO 2026-06-19 4 insights lock(Team Composition Contract):members vs consultants / default tier auto-grant / multi-PM all_approve / no-PM auto-postpone / MVT 3-role coverage。

> ⭐ **SDLC v2 context note(2026-06-20 PO lock — canonical §6.4.16):**
> - **Primary invocation context:** Phase 1 Step 1.2 — full team composition + MVT 3-role enforce 從 Phase 0 移到此
> - Phase 0 default `coverage_status: bootstrap-only`(PM only,QA / Developer 缺)— legal,不 refuse
> - Phase 1 Step 1.2 完成後 `coverage_status: complete`(MVT 3-role 全 cover by humans + AI_Agents)
> - 對齊 `phase_0_carve_out: true` trust_invariant(team-roster.md frontmatter)
> - 其他 phase 也可 invoke build-team(adjustments,non-primary)— 不限定 Phase 1

**Arguments:** `<natural-language>` describing team change(add / modify / remove / inquire)

**Trigger:** PO manual,or auto-prompted by other commands needing PM resolve

**Workflow:**

1. **Parse NL intent**(Claude LLM)— rev v1.4 強化(對齊 #18 BUG #1 fix):
   - intent enum: `add` | `modify` | `remove` | `inquire` | `bulk_add` | **`mixed`** ⭐
   - **mixed_intent semantics:** input 含 verify + modify(eg.「kuohsuming 三角色確認 + notes 加 X」)→ 自動分解 sub-operations:
     - `verify` sub-op:check existing roles/fields(no change,output report)
     - `modify` sub-op:apply specific field change
     - Workflow 順序跑 sub-ops,**每 sub-op 各自 Step 5 confirm**
   - target: existing member by id/name OR new
   - extracted_fields: {name, roles, expertise, modules, notes, ...}
   - missing_required: list(若 intent=add)
   - **無 modification needed**(eg. pure inquire 或 verify w/ no diff)→ skip Step 5/6,直接 Step 7-9
   - **member_type ambiguous parse fallback**(對齊 #20 NIT #7 fix):
     - 若 input 明含 keyword「ai_agent」/「agent」/「bot」/「automation」 → member_type=ai_agent
     - 若 input 含明顯人名 / email / GitHub handle / Chinese name → member_type=human
     - 若 ambiguous(eg.「add a test runner」)→ **sub-prompt**:「Add as human or ai_agent?(h/a)」
     - 預設 fallback:**human**(對齊 §6.4.14 §A「team primarily human」)

1.5. **Pre-execution validation gate**(對齊 #20 BUG #4 fix:fail-fast for invariant violations):
   
   Run before Step 3 sub-prompts(避免浪費 PO 時間):
   
   - **REQ-013 F-9**(AI_Agent never PM):若 `member_type=ai_agent` AND roles 含 `PM` → **REFUSE**(go to Step 5b refuse output)
   - **REQ-014 §F bootstrap**:若 `intent=remove` + last active human → **REFUSE**(對齊 bootstrap protection)
   - **REQ-014 §F bootstrap**:若 `intent=remove` + last active PM → **WARN + sub-prompt**「(a) promote 其他 member 為 PM (b) accept no-PM postpone state」
   - **REQ-014 §A consultant constraints**:若 target 是 consultant + 試加 `trust_tier=approver` → **REFUSE**
   - **All validations pass** → continue Step 2

2. **Classify target as member or consultant**:
   - **若 intent=inquire** → **SKIP Step 2-6,go to Step 7**(read-only path,對齊 #19 NIT #3 fix)
   - "Claude / GPT / general-purpose AI" → consultants section
   - Specialized agent / scoped tool → members(member_type=ai_agent)
   - Human name → members(member_type=human)

3. **Resolve missing required fields**(sub-prompt):
   - 缺 role → sub-prompt「`<name>` 的 role(s)?」
   - 缺 contact / trust_tier override → optional

4. **Verify(existing)or Apply(new)default tier** — rev v1.4 強化(對齊 #18 NIT #1 fix):

   - **若 intent=add**(new member):**Apply** default trust_tier:
     - primary_role=PM → `final_approver`
     - primary_role=QA → `module_owner`
     - primary_role=Developer → `contributor`
     - member_type=ai_agent → `contributor`(never PM)
   - **若 intent=modify**(existing member):**Verify** trust_tier 對齊既有 invariants(對齊 §6.4.14 §B priority resolution):
     - 若 explicit trust_tier set → kept
     - 若 primary_role 改變 → re-derive default tier
     - 若 primary_role 不變 → no change
   - **若 intent=verify**(no change scope):Read-only check trust_tier consistent with default
   - **若 intent=remove**:N/A(skip)
   - **若 intent=inquire**:N/A(skip,read-only)— 對齊 #19 NIT #4 fix

5. **Show diff before/after** + **PO confirm tier**(rev v1.4 強化,對齊 #18 BUG #2 fix):

   **Confirm tier 依 destructiveness 三層:**
   
   | Stakes | Examples | Required confirm phrase |
   |:---|:---|:---|
   | 🟢 **low**(non-destructive)| modify notes / expertise / contact / capacity / inquire | **`y`** (簡 confirm) |
   | 🟡 **medium**(structural change)| add new member / modify roles / modify primary_role / modify trust_tier / modify assigned_modules | **`CONFIRM TEAM`**(對齊 §K.8 pattern)|
   | 🔴 **high**(destructive)| remove member / remove last PM / remove last human | **`FORCE TEAM`** + secondary phrase per bootstrap protection sub-prompt |
   
   - 若 mixed_intent:每 sub-op 各自 confirm,**worst-tier wins**
   - confirm phrase mismatch → abort + audit「PO confirm phrase mismatch」

5b. **Refuse output template**(對齊 #20 NIT #6 fix):
   
   若 Step 1.5 validation gate REFUSE → 輸出 standardized template:
   
   ```
   ❌ /pm build-team REFUSED
   
   Reason: <human-readable explanation>
   Source: <REQ ID + proposal section refs>
   
   Suggestion(若 alternative path exists):
     Try: "<corrected command>"
     Reference: <why this works>
   
   No team-roster changes applied.
   ```
   
   Then exit workflow + Step 9 audit(log refuse event,non-state-change)

6. **Update team-roster.md** YAML frontmatter

7. **Re-check MVT coverage + output**(對齊 §6.4.14 §E)— rev v1.4 強化(對齊 #19 BUG #3 fix output format intent-dependent):
   
   ```python
   coverage = check_team_coverage(team_roster)
   ```
   
   **Output format depends on intent:**
   
   - **For add/modify/remove**(verdict + change summary):
     ```
     ✅ Team Complete  (或  ⚠ Incomplete: missing [PM])
     Changes applied:
       + <field>: <new value>
       - <field>: <removed>
     Next: <next action suggestion>
     ```
   
   - **For inquire**(full team status report):
     ```
     📊 Team Status — <project>
     
     ┌──────────────────────────────────────────────┐
     │ Members (N active human + ai_agent)          │
     ├──────────────────────────────────────────────┤
     │ <list of members + roles + assigned_modules>  │
     └──────────────────────────────────────────────┘
     ┌──────────────────────────────────────────────┐
     │ Consultants (N general-purpose)              │
     ├──────────────────────────────────────────────┤
     │ <list of consultants + used_for>             │
     └──────────────────────────────────────────────┘
     
     📋 MVT Coverage: ✅ / ⚠
       PM:        <member ids>
       QA:        <member ids>
       Developer: <member ids>
     
     📋 Postponed Commands: <count> (none / list)
     
     📋 Last activity:
       - Last build-team invocation: <date> (#<event>)
       - Phase signoff: <phase / date / approver>
     ```
   
   - **For verify(within mixed_intent)**:print「✅ Verified: <fields unchanged>」no full status

8. **Surface postponed_commands**(對齊 §6.4.14 §D)— rev v1.4 強化(對齊 #18 NIT #2 fix):
   ```python
   # "PM newly assigned" semantic 明示:
   #   = team transitions from no-active-PM → has-active-PM
   #   ≠ existing PM modifies notes / verifies roles(same PM)
   
   was_no_pm = (before_state.active_pm_count == 0)
   is_now_pm = (after_state.active_pm_count > 0)
   pm_newly_assigned = was_no_pm and is_now_pm
   
   if pm_newly_assigned:
       postponed = state.postponed_commands
       if postponed:
           print(f"ℹ Found {len(postponed)} postponed command(s) waiting for PM:")
           for i, cmd in enumerate(postponed):
               print(f"  [{i+1}] {cmd.command} (postponed {time_ago(cmd.postponed_at)})")
           prompt: "Resume? (y/N/skip)"
   # else(same PM verify/modify):skip surface,no prompt
   ```

9. **Audit** — rev v1.4 強化(對齊 #19 NIT #5 + #20 NIT #6 fix):
   
   **All invocations logged for §6.4.15 lifecycle tracking:**
   
   - Append decision-log `D-team-<seq>`(包含 read-only inquire + refuse events — for invocation count)
   - team-roster.md frontmatter update:
     - `last_build_team_invocation`: <ISO date>
     - `build_team_invocation_count`: ++
     - `build_team_findings_total`: 累計
   
   **State.md side-effects depend on intent:**
   - **add/modify/remove**:update `team_size` / `team_coverage_status` / `team_coverage_missing_roles` / `postponed_commands`(if surfaced)
   - **inquire**:no state.md side-effects(read-only,**但 invocation 仍 log decision-log + team-roster frontmatter for lifecycle tracking**)
   - **refuse**:log decision-log refuse event + reason,**no team-roster / state.md mutation**

**Bootstrap protection**(對齊 §6.4.14 §F):

| Scenario | Behavior |
|:---|:---|
| Remove last active human | **Refuse**(must `/pm archive`) |
| Remove last active PM | Warn + sub-prompt:「(a) promote 其他 (b) accept no-PM postpone state」 |
| project_type=sandbox 跑 deploy 無 team | Allowed(carve-out) |

**AI_Agent constraints**(對齊 §6.4.14 §E):

- 試填 `roles: [PM]` → **Refuse**(human-only PM invariant)
- `member_type=ai_agent` 必明列 `scope` + `permitted_actions` + `forbidden_actions`

**Consultant constraints**:

- 試 `trust_tier: <any approver>` → **Refuse**(advisory_only invariant)
- 不可 `assigned_modules`(對齊 contract_with_team)

**Cross-command integration**:

- `/pm signoff` / `/pm deploy` / `/pm rollback` 跑前對 final_approver resolve;若 caller not approver → refuse
- `/pm advance-phase 1` 跑前 hard-block 若 MVT incomplete(non-sandbox)
- `/pm verify-runtime` Layer 6 = team coverage soft reminder
- `/pm status` 顯示 coverage table + postponed_commands list

**Edge cases**:

| Scenario | Behavior |
|:---|:---|
| NL parse fail(ambiguous)| Print parse result + ask PO clarify |
| Existing member 名稱 conflict | Sub-prompt:「modify existing 還是 add new with different id?」 |
| Multi-member NL("小明小華都加入") | Split → multiple sub-add operations + confirm batch |
| Inquire mode("team 多少人?")| Read-only output team-roster summary |

**Confidence Tier:** 🟡 medium(NL parse 可能 misinterpret,但每動作 PO 必 confirm)

**Cross-references:**
- proposal §6.4.14 Team Composition Contract(完整 spec)
- proposal §6.4.4 Trust Hierarchy(本 contract 強化)
- backend-schema-auto-sync spec REQ-013 + REQ-014
- memory `user_working_style`(1-PO multi-role 對齊)

---

## Subcommand: verify-runtime(new in v1.1.10 — external runtime prerequisite audit)

> **設計理由:** v1.2 8 個 commands 的 workflow 多依 external runtime(Azure CLI / mysql / .env / azure-config / smoke-test.sh 等)。Workflow spec 寫得到,**不代表 runtime 真能跑**。本命令是**第 3 層 audit**(spec layer + impl layer + **runtime layer**)— 補 spectra-review #14 漏的 runtime dimension(對齊 PO 抓 deploy Azure CLI gap)。

**Trigger:** PO manual or auto by `/pm deploy` / `/pm rollback` / `/pm migration-apply` precheck

**Workflow:**

1. **Detect platform** — `uname -s`(linux / macos)+ 對齊 memory `azure_webapp_runtime`(Azure Linux 3.0 awareness)

2. **Check core CLI tools(全 commands 共用)**:

   | Tool | Detection | Used by |
   |:---|:---|:---|
   | `git` | `which git` | All commands |
   | `yq` | `which yq` | push-gate / migration-* |
   | `mysql` CLI | `which mysql` | migration-apply / migration-mark-applied |
   | `gh` CLI | `which gh` | general |
   | `python3` | `which python3` | scripts |
   | `bash lint.sh` | `[ -f lint.sh ]` | push-gate Check 7 |

3. **Check Azure CLI + auth(deploy + rollback 專用)**:
   ```bash
   which az || echo "❌ Azure CLI not installed"
   az account show 2>/dev/null || echo "❌ Azure auth not done (need az login)"
   ```

4. **Check Azure config file** `azure-config.yaml`(deploy + rollback 需要)+ **SKU auto-detection**(rev v1.1.11 added):
   - Expected schema(對齊 §G.6.1 SKU-aware deploy_strategy):
     ```yaml
     subscription_id: <uuid>
     resource_group: <name>
     region: <azure-region>
     web_app:
       name: <azure-app-name>
       sku_tier: <Basic|Standard|...>   # auto-detected
       slots:
         production: production
         staging: <slot-name|null>      # null if Basic SKU
       deploy_strategy: direct|slot_swap  # auto-set from sku_tier
       rollback_strategy: redeploy_previous_tag|slot_swap_back
     health_check:
       endpoint: /health
       expected_status: 200
       expected_body: OK
     ```
   - 若缺 → deploy / rollback 不知道操作哪個 Azure resource
   - **SKU auto-detection logic**(若 `az` CLI + auth available):
     ```bash
     SKU=$(az webapp show --name <app> --resource-group <rg> \
       --query 'sku' -o tsv 2>/dev/null)
     case "$SKU" in
       Basic) STRATEGY=direct; ROLLBACK=redeploy_previous_tag ;;
       Standard|Premium*) STRATEGY=slot_swap; ROLLBACK=slot_swap_back ;;
       *) STRATEGY=direct; ROLLBACK=redeploy_previous_tag ;;  # safe default
     esac
     ```
   - 若 `azure-config.yaml` 缺失 → SKILL 提示「Run `/pm verify-runtime --setup-azure-config` 自動 populate」(needs az CLI + login first)

5. **Check `.env.<env>` files**(migration-apply 需要):
   - `.env.dev`:`DB_HOST_DEV`, `DB_USER_DEV`, `DB_PASSWORD_DEV`, `DB_NAME`
   - `.env.staging`:同上 staging variant
   - `.env.prod`(optional,read-only):`DB_HOST_PROD_RO`, `DB_USER_PROD_RO`, `DB_PASSWORD_PROD_RO`
   - 缺 → migration-apply dev/staging auto-execute 失敗 / mark-applied auto-verify 失敗(可 PO 自輸 fallback)

6. **Check smoke-test.sh**(deploy post-deploy 用):
   - `[ -f docs/release/smoke-test.sh ]`
   - 缺 → deploy post-deploy smoke 改 skip + warn

7. **Map each missing dep to affected `/pm` commands** — 列「以下 commands DEAD / PARTIAL / OK」表。

### Layer 3 / 4 / 5 Cross-Doc Coherence Checks(rev v1.1.13 added)

> ⚠ **Designed to catch the bug type PO 2026-06-18 抓到**:tools 用了但沒在 SSOT(SSOT drift)、decision-log 紀錄了 install 但 SSOT 沒同步、workflow 假設 active project 但無 state.md。前 15 輪 spectra-review 都沒抓到的 cross-doc coherence dimension。

8. **Layer 3 — Tool ↔ SSOT Drift Detection**:

   ```bash
   # Extract tools used in SKILL.md (regex 對 --version / az / mysql / yq etc.)
   USED=$(grep -ohE '\b(git|gh|curl|wget|zip|jq|yq|az|mysql|python3|node|npm|docker)\b' \
     skills/pm-skill/SKILL.md | sort -u)
   
   # Extract SSOT names (with alias map: azure_cli→az, nodejs→node)
   SSOT=$(yq '.system[].name' skills/pm-skill/references/infra-deps.yaml \
     | sed -e 's/azure_cli/az/' -e 's/nodejs/node/' | sort -u)
   
   # Drift = USED but NOT in SSOT
   DRIFT=$(comm -23 <(echo "$USED") <(echo "$SSOT"))
   ```
   
   每 drift 列「used N times in SKILL.md but missing from infra-deps.yaml,recommend add entry」。

9. **Layer 4 — Decision-log ↔ SSOT Drift Detection**:

   ```bash
   # Extract D-dep-* entries from decision-log
   INSTALLED=$(grep -oE 'D-dep-[0-9]+:.*install\s+\K[a-z_-]+' \
     docs/decision-log.md 2>/dev/null | sort -u)
   
   # Verify each has corresponding SSOT entry
   for tool in $INSTALLED; do
     yq ".system[] | select(.name == \"$tool\")" infra-deps.yaml > /dev/null \
       || echo "⚠ D-dep audit mentioned $tool but missing in SSOT"
   done
   ```
   
   Reverse check:SSOT 有但 decision-log 沒 audit → 提示「missing audit for $tool install」(對齊 memory:dep_management propose+ack 紀律)。

10. **Layer 5 — Workflow ↔ Project Lifecycle Drift**:

    ```bash
    # Workflows that read state.md
    STATE_USERS=$(grep -lE 'state\.md|active project' skills/pm-skill/SKILL.md \
      | wc -l)
    
    # Check if active project exists
    ACTIVE=$(cat docs/pm/active-project.txt 2>/dev/null)
    if [ -z "$ACTIVE" ]; then
      echo "⚠ $STATE_USERS workflow sections read state.md but no active project"
      echo "  Suggestion: /pm init \"<project>\" to enable full workflow capability"
    fi
    ```
    
    Flag workflows assuming project state when none initialized(對齊 PO 2026-06-18 dry-run 抓到的 root cause:4/6 precondition 失敗 because state.md missing)。

8. **Output verdict + setup guide:**

   ```
   📋 /pm verify-runtime
   
   Platform: Linux 6.8.0 / x86_64
   Project: <active project>
   
   Core CLI Tools:
     ✅ git                           (/usr/bin/git)
     ✅ yq                            (/usr/local/bin/yq)
     ✅ mysql                         (/usr/bin/mysql)
     ✅ gh                            (/usr/bin/gh)
     ✅ python3                       (/usr/bin/python3)
     ✅ lint.sh                       (present in project root)
   
   Azure Deployment:
     ❌ Azure CLI(az)                NOT installed
     ❌ Azure auth                    N/A (no az to check)
     ❌ azure-config.yaml             missing
     ❌ smoke-test.sh                 missing
   
   Database / Migration:
     ❌ .env.dev                      missing
     ❌ .env.staging                  missing
     ❌ .env.prod                     missing (optional, can fallback to PO input)
   
   ╔══════════════════════════════════════════════════════════════╗
   ║ /pm Command Functional Status                                 ║
   ╠══════════════════════════════════════════════════════════════╣
   ║ ✅ Fully Functional(5 commands):                              ║
   ║    /pm setup-worktree                                         ║
   ║    /pm push-gate                                              ║
   ║    /pm migration-status         (read-only)                   ║
   ║    /pm migration-propose        (file plumbing)               ║
   ║    /pm validate-discipline-invariant                          ║
   ║                                                               ║
   ║ ⚠ Partial(2 commands,fallback path 可用):                   ║
   ║    /pm migration-apply --env prod    (print only, no DB exec) ║
   ║    /pm migration-mark-applied --env prod  (PO manual verify)  ║
   ║                                                               ║
   ║ 🚫 NON-Functional(3 commands):                                ║
   ║    /pm migration-apply --env dev      (need .env.dev)         ║
   ║    /pm migration-apply --env staging  (need .env.staging)     ║
   ║    /pm deploy --target staging/prod   (need az CLI + config)  ║
   ║    /pm rollback                       (need az CLI + config)  ║
   ╚══════════════════════════════════════════════════════════════╝
   
   To enable:
   
     [1] Azure CLI(對齊 memory:dep_management — propose PO ack first):
         azure-cli 在 Linux 3.0 對齊 memory:azure_webapp_runtime
         Install:
           sudo apt install azure-cli      (Ubuntu/Debian/WSL)
           sudo tdnf install azure-cli      (Azure Linux 3.0)
         Then:
           az login                          (browser flow)
     
     [2] azure-config.yaml(template):
         📄 /pm verify-runtime --print-template > azure-config.yaml
         (fills sample structure; PO 自填 subscription_id / resource_group)
     
     [3] .env.<env> files(per environment):
         Refer to docs/pm/runtime-env-template.md (created on first verify-runtime
         if missing). Sample:
           .env.dev:DB_HOST_DEV=... DB_USER_DEV=... DB_PASSWORD_DEV=... DB_NAME=laundrydb
     
     [4] smoke-test.sh(opt):
         echo '#!/bin/bash' > docs/release/smoke-test.sh
         chmod +x docs/release/smoke-test.sh
         # PO 加實際 smoke check(eg. curl /healthz)
   
   Next:
     - PO propose `dep_management` 加 azure-cli to requirements / system deps
     - PO 設 azure-config.yaml
     - 再跑 /pm verify-runtime 確認
   ```

**Edge cases:**

| Scenario | 行為 |
|:---|:---|
| `--print-template` flag | 印 azure-config.yaml + .env.* template,exit 0 |
| 完全綠燈 | output「✅ All v1.2 commands functional」+ exit 0 |
| Partial 綠燈 | output 列哪些 partial + 解法,verdict=partial |
| Detect Azure Web App runtime via web app metadata(future v1.3)| 對齊 memory:azure_webapp_runtime Linux 3.0 check |

**Confidence Tier:** 🟢 high(read-only audit,deterministic;對齊 §6.5 特性 2 Stage Gate 機械化原則)

**Cross-references:**
- memory `dep_management`(PO ack 前不可裝)
- memory `azure_webapp_runtime`(Linux 3.0 awareness)
- memory `backend_schema_change_workflow`(SSOT + PO 自 apply)
- §G.6.0.6 migration-apply prerequisites
- §G.6.0.7 migration-mark-applied prerequisites
- §G.6.1 deploy preconditions
- §G.6.2 rollback preconditions
- §K.6 validate-discipline-invariant cross-check

**Spectra-review #14 反饋(eat-own-dog-food iteration learning):**

第 14 輪 review 漏抓 runtime layer(B1 抓到 hook Claude CLI 但沒類推到 deploy az CLI)。本命令是補強。**未來 spec 設計**:Trigger / Workflow / Output / Edge cases / Confidence Tier / Cross-references / **Runtime Prerequisites** 7 段(目前 6 段),把 runtime 列為 first-class concern。

---

## Subcommand: validate-coverage(v1.2 — REQ→TC coverage gate,operationalizes §6.4.11 E.3/E.3a)

**Arguments:** `--all`(掃 `docs/modules/*/`)或 `--module <dir>`(單一 module)。

**用途:** deterministic 覆蓋 gate —— 把 §6.4.11 E.3「Spec↔Code↔Test 三向 invariant」的 `every_feature_has_test_case` + bidirectional orphan 檢查做成真 gate(此前 E.3a 只是 spec 內 pseudo-check)。本 command 檢 **feature↔TC**(via `tests.md` E.1 `derived_from_acceptance`)。**REQ→TC 覆蓋為 compose**:REQ→**module** 由 gate-check phase-1 C7 保證(`modules[].covers_reqs`,**粗粒度**),feature→TC 由本 command 保證;**中間 module→feature 的 REQ-level 精確追溯為 open gap**(C7 是 REQ→module 非 REQ→feature,故不宣稱端到端 REQ→TC 已保證)。

**Workflow:**

1. 跑 `python3 scripts/pm_coverage_validator.py --all`(或 `--module <dir>`)。
2. 每 module 掃 `docs/modules/<name>/{functional.md, tests.md}`:
   - **top-down(HARD FAIL):** 每個 `status=done` 的 feature 必有 ≥1 TC 的 `derived_from_acceptance` 引用它 → 缺 = ❌ 卡 gate
   - **bottom-up(WARN):** 每個 TC 的 `derived_from_acceptance` 必 resolve 到既有 feature → 否則 orphan / 殭屍 TC
3. 輸出覆蓋矩陣 + 缺口清單(哪個 feature 無 TC / 哪個 TC 是孤兒)。
4. **無 `functional.md`+`tests.md` 的 module → graceful skip**(Phase 0-3 專案不被卡)。

**Gate 掛點:** gate-check phase-4 criterion(**非** lint.sh CI —— TC 於 Phase 4 才存在)。

**限制(誠實):** deterministic **linkage** 檢查(每 feature 有 TC 指過來),**非** correctness(TC 真的測對 = framework G6 executable pass);與 triad(golden+anti,`requirement_spec_triad_validator.py`)+ G6 執行互補。stdlib only。`--selftest` 內嵌 fixture 可驗邏輯。

**Confidence:** 🟢 high(deterministic id 比對)。

---

## Subcommand: validate-* (delegates to spectra-review v2.0)

> ⚠ **SDLC v2 applicability(2026-06-20 spectra Round 1 C2 fix):**
> - `validate-req-spec` — applies to **both v1 and v2** projects(Phase 0 deliverable same artifact)
> - `validate-module-plan` — **v1 grandfather only**(v2 path 不產生 `_plan.md`,Phase 1 用 `<project>-modules-overview.md` 替代);v2 equivalent `validate-modules-overview` deferred to v1.2 planned
> - `validate-module-spec` — **v1 grandfather only**(v2 Phase 1 已拆 functional + design spec,deferred validators)
> - `validate-shared-infra / implementation / integration / release / post-launch` — applies to both(Phase 3-7 unchanged)

For `validate-req-spec / module-plan / module-spec / shared-infra / implementation / integration / release / post-launch`:

1. Read appropriate contract section from proposal §6.4.10/11.
2. Run machine checks(deterministic — 🟢 high confidence):
   - File existence / required sections present
   - grep forbidden patterns(TBD / TODO / non-testable acceptance)
   - YAML frontmatter schema validation
   - structural sanity(no_circular_deps / all_root_reqs_covered / etc.)
   - **triad completeness(validate-req-spec only,per §6.4.10 §G step 3 + requirement-spec-authoring-rules.md §3):** 每 REQ 恰 1 golden_scenario + ≥ 1 anti_examples;無 orphan;缺項若已 `[GAP]` + 二次確認 → warning 非 fail
3. For subjective quality(LLM judgment — 🟡 medium confidence)→ invoke **spectra-review v2.0**:
   - `/spectra-review <target-path> --mode pm-skill-<artifact-type>`
   - Pass active project context(spectra writes to `docs/reviews/<active-project>/`)
   - spectra produces F1 per-round log + F2 aggregate summary per §6.4.3.C contract
4. Compose results into single verdict + actionable fix list(per manual scene 3/8/9/10 demo outputs):
   - Machine check fails → list as gate-blocker
   - spectra-review BLOCKERS → list as gate-blocker
   - spectra-review CONCERNS → list as gate-warning
   - spectra-review NITS / STRENGTHS → list as gate-pass-with-notes
5. Suggest `/pm-bug-review <target-slug>` to walk PO through spectra's `no_decision` findings.

For `validate-all`: run all 8 per-phase validators + cross-phase lineage check(per §6.4.11 §J.2).

**Confidence:** 🟢 high(machine checks);🟡 medium(spectra-review delegation, follow Confidence Tier per finding)

**Spectra-review v2.0 contract:** SKILL at `skills/spectra-review/SKILL.md`(this dir's sibling),aligned to §6.4.3 / §6.4.4 Default vs Override / 7-field finding schema / F1+F2 file output.

---

## Subcommand: pm-bug-review

Per proposal §6.4.5 / manual scene 2. Workflow:

1. Read `docs/reviews/<active-project>/_summary-<target-slug>.md` (F2 aggregate per §6.4.3.C).
2. Filter by `--finding` or `--pending-only` or `--overrides-only`.
3. For each finding, display: tier / spectra default values (severity / fix_economics / dependencies / decay) / decision options [a-i].
4. On PO override: validate non-empty reason, write override 三件套 (by/at/reason) per §6.4.4.
5. Auto-recalc `roi.value` from new severity / difficulty.
6. Append to `docs/pm/<active-project>/decision-log.md`.
7. Update F2 summary file Quality Health Score (`po_overrides++`).
8. Output: new fix recommendation order per §6.4.8 algorithm.

---

# v1.1.9 Batch — v1.1 Planned 12 commands 落地(2026-06-20)

> 對齊 proposal §6.4.13 Contract Change Governance(minor change tier — 加 commands 不破壞既有 v1.0/v1.1 schema)。每命令 ~15-25 行 workflow + Confidence Tier。

---

## Subcommand: weekly(v1.1.9 — 2026-06-20)

**Arguments:** none(auto-resolves all active projects)

**Workflow:**

1. Read all `docs/pm/<project>/state.md`(active projects only)。
2. Aggregate last 7 days from `docs/decision-log.md` + each `docs/pm/<project>/decision-log.md`:
   - Phase advances / signoffs
   - Spectra-review verdicts(ship-as-is / fix-blockers / revise)
   - Build-team mutations
   - Schema migrations(if any)
   - Deploys / rollbacks(if any)
3. Compute aggregates:
   - Velocity:phase advances / week
   - Quality:total findings(BLOCKER/CONCERN/NIT counts)
   - Discipline:override_metric_count(對齊 §K.9)
   - Coverage:projects with `team_coverage_status: complete` count
4. Output report:
   ```
   📅 PM Skill Weekly Report — <ISO week>
   ═══════════════════════════════════════════════════════
   Active projects: <N> | Phase advances: <N> | Findings: <N>
   
   Per-project summary:
     - <project>: phase=<N> | last advance=<date> | health=<emoji>
   
   Cross-project highlights:
     - Pending decisions: <count>
     - Spectra rounds: <count>
     - Discipline overrides: <count>(對齊 §K.9 1/month threshold)
   
   ⚠ Attention items:
     - <项目 + reason>
   ```

**Confidence Tier:** 🟢 high(read-only aggregations + deterministic)

---

## Subcommand: health-check(v1.1.9 — 2026-06-20)

**Arguments:** `[--project <X>]`(optional,defaults to active)

**Workflow:**

1. Resolve active project。
2. Run multi-layer audit:
   - **Layer 1 — Schema drift:** state.md frontmatter has required fields(對齊 §6.4.10 §B)
   - **Layer 2 — Phase compliance:** current_phase + signoff lineage consistent
   - **Layer 3 — Team coverage:** team-roster.md coverage_status 對齊 phase(Phase 0 = bootstrap-only OK / Phase 1+ = complete required)
   - **Layer 4 — Spec freshness:** upstream_spec mtime / last spectra-review date / stale > 30 days warn
   - **Layer 5 — Decision-log integrity:** no orphan D-entries / no future timestamps
   - **Layer 6 — Memory rules:** PM Skill memory references resolve(`feedback_*` / `project_*` exist)
   - **Layer 7 — Workflow lifecycle:** workflow stage marker 對齊 §6.4.15(build-team v1.4-validated-candidate 等)
3. Report per-layer ✅ / ⚠ / ❌ + summary verdict:
   ```
   🩺 Health Check — <project>
   Layer 1 Schema drift:        ✅
   Layer 2 Phase compliance:    ✅
   Layer 3 Team coverage:       ⚠(Phase 1 but coverage=bootstrap-only — Step 1.2 pending)
   Layer 4 Spec freshness:      ✅(2 days old)
   Layer 5 Decision-log:        ✅
   Layer 6 Memory rules:        ✅
   Layer 7 Workflow lifecycle:  ✅
   
   Verdict: 🟡 1 warning(non-blocking)
   ```

**Confidence Tier:** 🟢 high(file/field checks deterministic)

---

## Subcommand: kpi-eval(v1.1.9 — 2026-06-20)

**Arguments:** `[--project <X>]`

**Workflow:**

1. Resolve active project + verify `current_phase == 7`(post-launch)。
2. Read per-phase signoff metadata + spec acceptance criteria + post-launch metrics from `state.md`。
3. Compute KPIs(對齊 proposal §6.4.11 §H.4):
   - Spec → ship cycle time(Phase 0 start → Phase 6 deploy)
   - Spectra rounds 平均 / total findings closed
   - Override metrics(對齊 §K.9 alarm thresholds)
   - Production incident count(post-launch window)
   - Memory rule violations count
   - Phase signoff median lag
4. Output:
   ```
   📊 KPI Evaluation — <project> Phase 7
   ────────────────────────────────────
   Spec → ship:           <X> days
   Spectra avg rounds:    <N>(target ≤ 3)
   Discipline overrides:  <N>(alarm @ 3/month per §K.9)
   Prod incidents:        <N>(target 0)
   Memory violations:     <N>(target 0)
   
   Verdict: <pass/needs-improve>
   ```

**Confidence Tier:** 🟡 medium(metric definitions stable;subjective verdict)

---

## Subcommand: requirement impact-analysis(v1.1.12 — 2026-06-20 phase-aware + cost-aware,§6.4.17 rev 1.15)

**Arguments:** `<REQ-id>` required(eg. `REQ-005`)

**Workflow(rev 1.15 phase-aware logic):**

1. Resolve active project + read `<project>-requirement-spec.md` + `state.md`。
2. Locate target REQ section + read `state.md.current_phase` as `<C>`。
3. Walk dependency graph(對齊 §6.4.10 §B.5):
   - Direct upstream / downstream REQs
   - Modules covering this REQ(state.md modules[].covers_reqs)
4. **Per-phase impact assessment(對齊 §6.4.17 rev 1.15 phase-aware):**
   - For each phase P in `[0, 1, ..., C]`:
     - **P=0:** check requirement-spec section + Phase 0 signoff state
     - **P=1:** check modules-overview.md + functional spec files + design spec files
     - **P=2:** check plan.md per module
     - **P=3:** check shared-infra artifacts
     - **P=4:** check `backend/*.py` + `SKILL.md` + memory files mentioning this REQ(grep)
     - **P=5:** check integration test files / scenarios
     - **P=6:** check release artifacts(deploy logs / signed off?)
     - **P=7:** check post-launch metrics referencing this REQ
   - Tally artifacts per phase + estimate rework cost(per phase cost table in §6.4.17)
5. **Compute Tier(對齊 §6.4.17 rev 1.15 4-tier + cost-aware):**
   - `cascade_scope_tier`:based on module count + downstream REQ count(⭐ Round 2 C2 fix thresholds:1 module + 0-3 downstream → 🟢🟡 / 1 module + ≥ 4 downstream → 🟠 / 2-3 modules → 🟠 / 4+ modules → 🔴)
   - `rework_cost_tier`:
     - < 15 min → 🟢
     - 15-60 min → 🟡
     - 60-240 min → 🟠
     - \> 240 min → 🔴 major-rework
   - **Tier = max(cascade_scope_tier, rework_cost_tier)**(worst-of-both wins)
6. **PM placement suggestions(對齊 §6.4.17 P5):**
   - For **drop**:list modules losing REQ + remaining count;flag if any empties
   - For **add**:suggest closest module by artifact-type match;or「new module needed」if no fit
   - For **modify**:list modules + specs that need re-author + per-phase impact
7. Output(rev 1.15 format with per-phase table):
   ```
   💥 Impact Analysis — REQ-<NNN> (current_phase = <C>)
   ════════════════════════════════════════════════════════════
   
   📊 Direct dependency graph:
     Upstream:   [<REQ-ids>]
     Downstream: [<REQ-ids>]
     Module:     [<module-ids>]
   
   🗓 Per-phase impact (Phase 0 to <C>):
     ┌──────┬─────────────┬────────────────────────────┬──────────┐
     │ Phase│ Status      │ Affected artifacts         │ Re-do min│
     ├──────┼─────────────┼────────────────────────────┼──────────┤
     │ 0    │ ✅ COMPLETED │ spec amendment + rev bump  │ 15-25    │
     │ 1    │ 🟡 IN PROG  │ modules-overview + specs   │ 30-60    │
     │ 2    │ ⏳ NOT STRT │ N/A                        │ 0        │
     │ ...  │ ...         │ ...                        │ ...      │
     └──────┴─────────────┴────────────────────────────┴──────────┘
   
   📈 Total rework cost: ~<N> min(cost source:proposal §6.4.17 rev 1.15 cost reference table ⭐ Round 2 C1 fix)
   
   ⚠ Cascade Tier(§6.4.17 rev 1.15):  🟢/🟡/🟠/🔴
     cascade_scope_tier: 🟡(1 module + 4 downstream)
     rework_cost_tier:   🟡(45 min)
     final tier:         🟡 patch
   
   👔 PM placement suggestion:
     - Recommended:<module-id>(reason)
     - Alternative:<module-id>
     - Or:create new module(name suggestion)
   
   🎯 Suggested action sequence:
     1. /pm requirement {drop|add-mid-phase|modify} <REQ-id> --reason "<text>"
     2. /pm spec-rev-bump <project> --rev <X>.<Y>
     3. /pm spectra-review --quick(amended spec)
   
   ⚠ If Tier=🔴 major-rework:
     Option A: Accept high rework cost(対齊 §6.4.17 P3 minimum re-author at current phase)
     Option B: /pm advance-phase <N<current> --reason "..." --confirm-rollback
              (rollback to earlier phase + re-do — 對齊 P1 PM-explicit ONLY)
   ```

**Confidence Tier:** 🟡 medium(graph walk + phase artifact scan deterministic + cost estimate heuristic)

---

## Subcommand: requirement drop(v1.1.11 — 2026-06-20 §6.4.17)

**Arguments:** `<REQ-id>` required, `--reason "<text>"` required(≥ 20 chars)

**Workflow:**

1. Run `requirement impact-analysis <REQ-id>` internally to get Tier + affected modules。
2. **PM sub-prompt(對齊 §6.4.17 P5):**
   - If Tier=🟢 no-cascade → confirm `(Y/n)` 直接 drop
   - If Tier=🟡 patch(module 仍 ≥ 1 REQ remaining)→ confirm + apply
   - If Tier=🟠 re-assign(module empties)→ PM sub-prompt:
     ```
     ⚠ Dropping <REQ-id> will empty module <module-id>.
     PM action:
       (a) Remove module entirely(specs moved to spec/_phase1_history/<module>/)
       (b) Cancel drop
     ```
3. **Apply PM choice(對齊 §6.4.17 P3 minimum re-author):**
   - Update requirement-spec(remove REQ section)+ rev bump
   - Update state.md modules[X].covers_reqs(remove REQ-id)
   - If module empties + PM chose (a):
     - Move spec/modules/<X>/ → spec/_phase1_history/<X>/<ISO>/
     - Remove `<X>` from state.md modules[]
     - Update modules-overview.md(remove module section)
   - If module non-empty:
     - Edit affected functional/design spec(remove REQ-X Feature/section)— **only affected module**
4. **Audit(P4):** Append `D-req-drop-<seq>: req=<id> reason="<text>" module-action="<action>" tier="<tier>"`
5. Run `spectra-review --quick` on amended spec(P5)

**Confidence Tier:** 🟡 medium(file edits deterministic;module empties decision needs PM)

---

## Subcommand: requirement add-mid-phase(v1.1.11 — 2026-06-20 §6.4.17)

**Arguments:** `<REQ-id>` required(eg. `REQ-016`),`--reason "<text>"` required(≥ 20 chars)

**Workflow:**

1. Sub-prompt for REQ definition(11 必填欄位 per §6.4.10 §B.4,canonical):id / title / description / priority / rationale / acceptance / **golden_scenario** / **anti_examples** / dependencies / proposed_module / source_evidence(三元組:golden 1:1 + anti 1:N per requirement-spec-authoring-rules.md §3)
1.5. **Triad authoring** — 跑 **§Shared: Triad Authoring Behavior**(Auto-Completion 補 golden_scenario + anti_examples + Coverage Expansion 舉一反三 ~3 相鄰候選逐一討論)
2. Validate REQ-id 不衝突(no existing REQ-id same)
3. Run impact-analysis to suggest module placement。
4. **PM sub-prompt(對齊 §6.4.17 P5):**
   ```
   New REQ-<id> classification:
     Artifact-type signature: <inferred>
     Closest existing module: <module-id>(reason)
   
   PM action:
     (a) Add to <suggested-module>(recommend)
     (b) Add to other existing module:<list>
     (c) Create new module:<name>(if artifact-type 不 fit any existing)
     (d) Defer(mark as deferred for now,not assigned)
   ```
5. **Apply PM choice(對齊 §6.4.17 P3 minimum re-author):**
   - Append REQ-X section to requirement-spec + rev bump
   - If (a)/(b):
     - state.md modules[chosen].covers_reqs += [REQ-X]
     - Re-author chosen module's functional-spec(add Feature for REQ-X)
     - Re-author chosen module's design-spec(add functions/files for REQ-X)
     - **其他 modules 不動**(P2 + P3)
   - If (c):
     - state.md modules[] += new module entry
     - Scaffold spec/modules/<new>/ folder
     - Author NEW module's functional/design spec
     - Update modules-overview.md(add new module section)
   - If (d):mark deferred in spec only
6. **Audit(P4):** Append `D-req-add-mid-phase-<seq>: req=<id> reason="<text>" module-action="<action>" tier="<tier>"`
7. Run `spectra-review --quick`

**Confidence Tier:** 🟡 medium(file edits + spec scaffold deterministic;PM placement decision)

---

## Subcommand: requirement modify(v1.1.11 — 2026-06-20 §6.4.17)

**Arguments:** `<REQ-id>` required, `--aspect <description|acceptance|golden_scenario|anti_examples|priority|effort|risk|status>` required, `--reason "<text>"` required(≥ 20 chars)

> **Aspect 分類(N1 fix):** `description|acceptance|golden_scenario|anti_examples|priority` = §6.4.10 §B.4 spec schema 欄位(改動走 spec rev bump);`effort|risk|status` = per-REQ tracking metadata(state.md,非 spec 11 欄位,改動不觸發 spec rev bump)。

**Workflow:**

1. Locate REQ + show current value of aspect。
2. Sub-prompt for new value。
2.5. **Triad reconciliation(INV-3 per requirement-spec-authoring-rules.md §6.2 UP5)** — 若 aspect ∈ {description, golden_scenario, anti_examples} → 回檢三元組是否仍一致(改 golden/anti → 回檢 REQ 語意;改 REQ desc → 回檢 golden/anti 是否仍描述得準);必要時跑 **§Shared: Triad Authoring Behavior** 補正。
3. Run impact-analysis to identify affected modules / specs。
4. **PM sub-prompt(對齊 §6.4.17 P5):**
   ```
   REQ-<id> aspect "<aspect>" change:
     Old: <text>
     New: <text>
   
   Affected modules: <list>
   Affected specs:
     - <module-A>-functional-spec.md(Feature mentioning REQ-<id>)
     - <module-A>-design-spec.md(implementation detail of REQ-<id>)
   
   PM action:
     (a) Re-author affected specs(only <module-A>)
     (b) Log change without re-author(if trivial — eg. priority change)
     (c) Cancel
   ```
5. **Apply PM choice(對齊 P3 minimum re-author):**
   - Update requirement-spec REQ-X section + rev bump
   - If (a):re-author affected module's specs(只 that module)
   - If (b):log only,no spec change
6. **Audit(P4):** Append `D-req-modify-<seq>: req=<id> aspect=<aspect> reason="<text>" module-action="<action>"`
7. Run `spectra-review --quick`

**Confidence Tier:** 🟡 medium(scope deterministic;trivial-vs-substantive decision needs PM)

---

## Subcommand: spec-rev-bump(v1.1.11 — 2026-06-20 §6.4.17)

**Arguments:** `<project>` required(or default active),`--rev <X>.<Y>` required(semver),`--reason "<text>"` required(≥ 20 chars)

**Workflow:**

1. Resolve project + locate spec file(`docs/pm/<project>/spec/<project>-requirement-spec.md`)
2. Verify rev format(X.Y where X/Y ∈ integers,X.Y ≥ current rev)
3. Update spec frontmatter:`rev: <X>.<Y>` + add inline annotation `> ⭐ Rev <X>.<Y>(<ISO>):<reason>`
4. Append revision table entry(if spec has one)
5. **Audit(P4 mandatory):** Append `D-spec-rev-<seq>: project=<project> rev=<X>.<Y> reason="<text>" prev_rev=<prev>`

**Confidence Tier:** 🟢 high(frontmatter edit + decision-log deterministic)

---

## Subcommand: requirement split(v1.1.13 — 2026-06-20 §6.4.17 specialized)

**Arguments:** `<REQ-id>` required(source REQ to split),`--into <new-id-list>` required(comma-separated,eg. `REQ-005a,REQ-005b`),`--reason "<text>"` required(≥ 20 chars)

**Workflow:**

1. Resolve active project + locate source REQ + read state.md。
2. Run impact-analysis internally(phase-aware per §6.4.17 rev 1.15)。
3. Sub-prompt for each new REQ-id 的 carve-out content:
   - Which acceptance criteria(F-1, F-2, ...)go to each new REQ
   - Each new REQ retains source's 11 必填欄位 schema(含 golden_scenario + anti_examples — 拆分後每子 REQ 各自 1:1 golden + ≥1 anti per requirement-spec-authoring-rules.md §7)
3.5. **Triad authoring per child** — 對每個新子 REQ 跑 **§Shared: Triad Authoring Behavior 之 Triad Auto-Completion**(確保各子 REQ 恰 1 golden_scenario + ≥ 1 anti_examples;source 三元組按情境分配到子 REQ)。**Coverage Expansion 於 split 不強制**(拆分非新增相鄰需求的時機,避免 scope creep)。
4. Show preview + require `CONFIRM SPLIT`:
   ```
   ⚠ Splitting <source-id> into <new-id-list>:
     Source REQ retained acceptance: [<list>]
     <new-id-1>: [<carved acceptance>]
     <new-id-2>: [<carved acceptance>]
   
   Module assignment(PM 拍板 per new REQ-id):
     <new-id-1>: <module>(default same as source)
     <new-id-2>: <module>(default same as source)
   
   Spec impact: drop source + add N new REQs(rev bump)
   ```
5. On confirm(對齊 §6.4.17 P3 minimum re-author + P4 audit):
   - Update requirement-spec:replace source REQ section with N new REQ sections(rev bump)
   - Update state.md modules[].covers_reqs(replace source-id with new-id-list)
   - Update modules-overview.md coverage matrix
   - Re-author affected modules' functional + design specs(remap source feature → new features)
6. **Audit(P4):** Append `D-req-split-<seq>: source=<id> into=<new-id-list> reason="<text>" affected-modules=[...]`
7. Run `spectra-review --quick`

**Confidence Tier:** 🟡 medium(carve-out semantic needs PM judgment)

---

## Subcommand: requirement merge(v1.1.13 — 2026-06-20 §6.4.17 specialized)

**Arguments:** `--reqs <id-list>` required(≥ 2 REQ-ids,comma-separated),`--into <new-id>` required(target),`--reason "<text>"` required(≥ 20 chars)

**Workflow:**

1. Resolve active project + locate all source REQs。
2. Run impact-analysis on each source REQ(phase-aware per §6.4.17 rev 1.15)。
3. Verify source REQs are mergeable(same module assignment + compatible 9-field schema)。**⭐ Round 2 C4 fix:** if sources span DIFFERENT modules → output **escape sequence**: 「Cross-module merge not supported directly. Run `/pm requirement move <REQ-id> --to <target-module>` for each source first to align modules,then `/pm requirement merge`」 + abort。
4. Sub-prompt for merged REQ content:
   - Combined title / description / acceptance / dependencies
   - Merged risk(take max of sources)
   - Merged effort(sum of sources)
   - Decision on conflicting fields(if any)
5. Show preview + require `CONFIRM MERGE`:
   ```
   ⚠ Merging <source-id-list> into <new-id>:
     Combined acceptance: [<list>]
     Combined dependencies: [<list>]
     Target module: <module>(must be same across sources)
   
   Spec impact: drop N sources + add 1 new(rev bump)
   ```
6. On confirm:
   - Update requirement-spec:remove source REQ sections + add merged REQ section
   - Update state.md modules[].covers_reqs(remove sources + add new)
   - Update modules-overview.md coverage matrix
   - Re-author affected module's functional + design specs(consolidate features → new feature)
7. **Audit(P4):** Append `D-req-merge-<seq>: sources=<list> into=<new-id> reason="<text>"`
8. Run `spectra-review --quick`

**Confidence Tier:** 🟡 medium(field reconciliation needs PM judgment;same-module precondition deterministic)

---

## Subcommand: requirement move(v1.1.13 — 2026-06-20 §6.4.17 specialized)

**Arguments:** `<REQ-id>` required, `--from <module-id>` required, `--to <module-id>` required, `--reason "<text>"` required(≥ 20 chars)

**Workflow:**

1. Resolve active project + verify source `<from>` module covers REQ-id + target `<to>` module exists。
2. Run impact-analysis(phase-aware)— REQ content unchanged,only ownership changes。
3. Verify target module's artifact-type compatible(若 source REQ artifact-type=`python-runtime` 目標 module artifact-type=`markdown` 警示)。
4. Show preview + require `CONFIRM MOVE`(non-destructive but cross-module audit):
   ```
   ⚠ Moving <REQ-id> from <from-module> to <to-module>:
     REQ content: unchanged
     Module changes:
       <from-module>.covers_reqs: -[<REQ-id>]
       <to-module>.covers_reqs:   +[<REQ-id>]
     Spec impact: remove Feature from <from> functional/design;
                  add Feature to <to> functional/design
     Artifact-type compatibility: ✅/⚠
   ```
5. On confirm:
   - Update state.md modules[<from>].covers_reqs -= [REQ-id]
   - Update state.md modules[<to>].covers_reqs += [REQ-id]
   - Re-author <from> module's functional + design specs(remove REQ-X Feature)
   - Re-author <to> module's functional + design specs(add REQ-X Feature)
   - Update modules-overview.md coverage matrix
   - **Note:** requirement-spec REQ section NOT changed(content unchanged)
6. **Audit(P4):** Append `D-req-move-<seq>: req=<id> from=<from> to=<to> reason="<text>"`
7. **No spec-rev-bump needed**(REQ content unchanged,只 module assignment change — ⭐ Round 2 C3 fix:proposal §6.4.17 rev 1.16 L5078 documented exception to P4 universal-audit rule;state.md modules[] change 仍 audit via D-req-move-<seq> but spec frontmatter rev untouched since spec content unchanged)
8. Run `spectra-review --quick`(quick check no cross-module contract break)

**Confidence Tier:** 🟢 high(state.md edit + 2 spec edits deterministic;artifact-type compat warning heuristic)

---

## Subcommand: assign-feature(v1.1.9 — 2026-06-20)

**Arguments:** `<feature-id>` required, `--to <engineer-id>` required, `[--pair <engineer-id>]` optional

**Workflow:**

1. Resolve active project + read team-roster.md + state.md modules[]。
2. Locate feature in module functional spec:
   - grep `<feature-id>` across `<project>-*-functional-spec.md`
3. Verify `<engineer-id>` is active team member(team-roster.md members[]).
4. Verify `<engineer-id>` has appropriate role for feature(eg. Developer for implementation features)。
5. Show preview + require `(Y/n)` confirm:
   ```
   Assign feature <fid> in module <module-id>:
     - assigned_to: <engineer-id>
     - paired_with: <pair-id> (if provided)
     - previous owner: <prev>
   Confirm? (Y/n)
   ```
6. On confirm:
   - Update feature entry in functional spec(`assigned_to:` field)
   - Append decision-log:`D-assign-<seq>: feature=<fid> from=<prev> to=<eng> [--pair <X>] reason="manual override"`
7. Report success。

**Confidence Tier:** 🟢 high(file edit + audit deterministic)

---

## Subcommand: contract-change status(v1.1.9 — 2026-06-20)

**Arguments:** none

**Workflow:**

1. Read all `D-contract-change-*` entries from `docs/decision-log.md` + `docs/pm/_org/org-decision-log.md`。
2. Classify by status:`pending` / `applied` / `rolled-back`。
3. Output table:
   ```
   📜 Contract Changes Status
   ────────────────────────────
   Pending:
     - C-<seq>: <description> (proposed <date>)
   Applied:
     - C-<seq>: <description> (applied <date>)
   Rolled-back:
     - C-<seq>: <description> (rolled back <date>, reason <text>)
   
   Open count: <N> | Last applied: <date>
   ```

**Confidence Tier:** 🟢 high(grep + categorize deterministic)

---

## Subcommand: contract-change rollback(v1.1.9 — 2026-06-20)

**Arguments:** `--change <seq>` required, `--reason "<text>"` required(≥ 20 chars)

**Workflow:**

1. Locate `D-contract-change-<seq>` entry in decision-log。
2. If status != `applied` → abort:「Cannot rollback non-applied change」。
3. Read change body for files affected。
4. Show preview + require `CONFIRM ROLLBACK`(對齊 §K.8 BYPASS pattern — destructive):
   ```
   ⚠ Rollback contract change C-<seq>:
     - Affected files: [<list>]
     - Original change date: <date>
     - Rollback reason: "<text>"
   Type `CONFIRM ROLLBACK` to proceed:
   ```
5. On confirm:
   - Restore original content via git revert / patch
   - Append `D-contract-rollback-<seq>: original=C-<seq> reason="<text>" by=PO at=<ISO>`
6. Output success + suggest follow-up(re-spectra-review if applicable)。

**Confidence Tier:** 🟡 medium(file restore deterministic;side-effect needs PO judgment)

---

## Subcommand: contract-change history(v1.1.9 — 2026-06-20)

**Arguments:** `[--window <N>months]`(default 6)

**Workflow:**

1. Read all `D-contract-change-*` entries from past N months。
2. Aggregate by:contract section(eg. §6.4.10 / §6.4.11 / §6.4.14 / §6.4.16)+ change tier(major / minor / patch per §6.4.13)。
3. Output Evolution Report:
   ```
   📈 Contract Evolution Report — past <N> months
   ─────────────────────────────────────────────────
   Section §6.4.10:  3 changes(1 major + 2 patch)
   Section §6.4.14:  2 changes(2 minor)
   Section §6.4.16:  1 change(NEW — SDLC v2 adoption rev 1.13)
   
   Total: <N> changes | Major: <N> | Minor: <N> | Patch: <N>
   
   Top contributors(top decisions):
     - D-sdlc-v2-001: SDLC v2 adoption(2026-06-20)
     - D-spectra-round-1-001: cross-doc audit pass
   ```

**Confidence Tier:** 🟢 high(read + aggregate deterministic)

---

## Subcommand: cross-project sync-decision(v1.1.9 — 2026-06-20)

**Arguments:** `<decision-text>` required, `--to <project1,project2,...>` required, `[--reason "<text>"]`

**Workflow:**

1. Verify all `<project>` targets exist(`docs/pm/<project>/state.md` exists for each)。
2. Show preview + require `(Y/n)` confirm:
   ```
   Sync decision across N projects:
     Decision: "<text>"
     Targets: [<project list>]
     Reason: "<text>"
   Confirm? (Y/n)
   ```
3. On confirm:
   - Append `D-cross-sync-<seq>` to `docs/pm/_org/org-decision-log.md`
   - Append same to each target project's `decision-log.md`
   - Log:`D-cross-sync-<seq>: text="<decision>" applied-to=[<list>] reason="<text>"`
4. Output:cross-link confirmation。

**Confidence Tier:** 🟢 high(multi-file append deterministic)

---

## Subcommand: cross-project resource-check(v1.1.9 — 2026-06-20)

**Arguments:** none

**Workflow:**

1. Read all `docs/pm/<project>/team-roster.md`(active projects only)。
2. Aggregate by member id(eg. kuohsuming)across projects。
3. Compute capacity:
   - For each member:total roles count(eg. PM × 3 projects = 3 hats)
   - Detect overload:`primary_role` PM × > 2 projects → warn
4. Output:
   ```
   👥 Cross-Project Resource Check
   ──────────────────────────────────
   kuohsuming:
     - Active in 3 projects(backend-schema-auto-sync / pm-skill / spectra-review)
     - Primary PM count: 3 ⚠(overload — consider delegate)
     - Multi-role count: PM=3 / QA=3 / Developer=3
   
   Verdict: ⚠ 1 overload risk
   ```

**Confidence Tier:** 🟡 medium(definition of overload heuristic)

---

## Subcommand: cross-project common-pattern(v1.1.9 — 2026-06-20)

**Arguments:** none

**Workflow:**

1. Read all `docs/pm/<project>/state.md` modules[] + all functional specs。
2. Detect common patterns:
   - Repeated module names across projects(eg. `memory-rule-update` in 2 projects)
   - Repeated artifact types(eg. `python-runtime` 在 N modules)
   - Common REQ themes(eg. multiple specs use REQ-related-to-audit)
3. Output:
   ```
   🔍 Common Patterns Across Projects
   ─────────────────────────────────
   Repeated modules:
     - memory-rule-update(in 2 projects)→ candidate for shared template
   
   Common artifact types:
     - python-runtime: 5 modules across 3 projects
     - markdown: 8 modules across 4 projects
   
   Suggestion:
     - Consider creating shared template for memory-rule-update
   ```

**Confidence Tier:** 🟡 medium(pattern detection heuristic)

---

## Subcommand: org-retrospective(v1.1.9 — 2026-06-20)

**Arguments:** `[--window <N>months]`(default 6)

**Workflow:**

1. Read all `docs/pm/<project>/decision-log.md` + `docs/pm/_org/org-decision-log.md` from past N months。
2. Aggregate:
   - Projects launched / archived
   - Phase advances per project
   - Spectra-review rounds total
   - Critical findings closure rate
   - Discipline overrides usage(§K.9)
   - Memory rules added(saved per session)
   - Workflow lifecycle promotions(per §6.4.15)
3. Identify themes:
   - Most successful patterns(low override + fast phase advance)
   - Most challenging areas(repeated overrides or stuck phases)
   - Knowledge accumulation(new memory rules)
4. Output Retro Report:
   ```
   🔄 Org Retrospective — past <N> months
   ════════════════════════════════════════
   📈 Wins:
     - Successful projects: <N>
     - Memory rules added: <N>(knowledge accumulated)
     - Workflow lifecycle promotions: <N>(v1.x → validated)
   
   ⚠ Challenges:
     - Discipline overrides: <N>(threshold @ 3/month per §K.9)
     - Stuck phases: <list>
     - Repeated review rounds: <patterns>
   
   📚 Top learnings(memory rules added past <N>m):
     - <name>: <description>
   
   💡 Recommendations:
     - <next-quarter improvements>
   ```

**Confidence Tier:** 🟡 medium(aggregation deterministic + recommendations heuristic)

---

---

# v1.1.10 Batch — 14 commands gap closure(2026-06-20)

> 對齊 proposal §6.4.13 Contract Change Governance(minor change tier)。Groups:G1(SDLC v2 validators)+ G2(memory ops)+ G3(spec drafters)+ G4(decision-log ops)+ G5(daily-sync)。

---

## Subcommand: validate-modules-overview(v1.1.10 — G1 SDLC v2)

**Arguments:** `<path>` optional(default `docs/pm/<active>/spec/<active>-modules-overview.md`)

**Workflow:**

1. Resolve target path.
2. Verify file exists + parse markdown structure.
3. Machine checks:
   - Frontmatter has `project / artifact: modules-overview / phase: 1 / phase_step: "1.1" / sdlc_contract: v2`
   - 🗺 Big picture section present
   - Per module 4 mandatory sections present:`📋 What it does` / `👔 For PM` / `🔬 For QA` / `💻 For Developer`
   - 🔗 Module dependency graph section present
   - 📊 Coverage matrix table present(all REQs covered)
4. HUMAN-FIRST checks:
   - 📋 What it does sections have plain prose(not YAML blob)
   - 3-role sections have actual content(not placeholder)
5. Delegate quality check to spectra-review(invoke with `--quick` mode)
6. Output verdict per dimension:
   ```
   ✅ Structure: 4-section per module(N modules ×4 = 4N sections)
   ✅ HUMAN-FIRST: plain prose detected
   ⚠ Coverage matrix: missing REQ-XXX
   ```

**Confidence Tier:** 🟢 high(structural check)+ 🟡 medium(HUMAN-FIRST heuristic)

---

## Subcommand: validate-functional-spec(v1.1.10 — G1 SDLC v2)

**Arguments:** `<path>` required(eg. `docs/pm/<project>/spec/<project>-<module>-functional-spec.md`)

**Workflow:**

1. Verify file exists + parse markdown.
2. Machine checks:
   - Frontmatter has `module / parent_project / phase_step: "1.4" / sdlc_contract: v2`
   - 3-role sections present per feature(👔/🔬/💻)
   - Feature list table 對齊 §6.4.11 §C.2 simplified schema
   - All features cross-ref module's covers_reqs(no orphan feature)
3. HUMAN-FIRST + dependency checks(同 validate-modules-overview)
4. Output verdict.

**Confidence Tier:** 🟢 high

---

## Subcommand: validate-design-spec(v1.1.10 — G1 SDLC v2)

**Arguments:** `<path>` required

**Workflow:**

1. Verify file exists + parse markdown.
2. Machine checks:
   - Frontmatter has `module / parent_project / phase_step: "1.5" / sdlc_contract: v2`
   - HOW sections per feature(functions / file paths / library deps / invariants)
   - File paths schema:`backend/*.py` / `<project>/skills/.../SKILL.md` / etc.
   - Cross-ref functional-spec features 1:1
3. Output verdict.

**Confidence Tier:** 🟢 high

---

## Subcommand: memory list(v1.1.10 — G2)

**Arguments:** `[--type <user|feedback|project|reference>]`, `[--filter <pattern>]`

**Workflow:**

1. Read `~/.claude/projects/-home-hsuming-AzureLineBOT-main/memory/MEMORY.md`(or current project's memory dir)
2. Parse one-line entries(format `- [Title](file.md) — hook`)
3. For each entry,read frontmatter `metadata.type`
4. Apply `--type` / `--filter` filters
5. Output table:
   ```
   🧠 Memory Index — <N> entries
   ─────────────────────────────────
   Type      | Name                              | Hook
   feedback  | human-first-docs                  | shareable docs must contain 3-role perspectives
   project   | v2-backend-integration            | deploy loop bundle→templates
   ...
   ```

**Confidence Tier:** 🟢 high

---

## Subcommand: memory add(v1.1.10 — G2)

**Arguments:** `<name>` required(kebab-case), `--type <user|feedback|project|reference>` required, `[--description "<text>"]`

**Workflow:**

1. Validate name(kebab-case,no spaces)
2. Map type to file prefix:`user_<name>.md` / `feedback_<name>.md` / `project_<name>.md` / `reference_<name>.md`
3. Verify file doesn't exist(abort if duplicate)
4. Sub-prompt for body content if not piped:
   - Rule(1 sentence)
   - Why(reason)
   - How to apply(when/where)
5. Write file with frontmatter:
   ```yaml
   ---
   name: <name>
   description: <text>
   metadata:
     type: <type>
   ---
   ```
6. Append entry to `MEMORY.md` index(`- [Title](file.md) — hook`)
7. Append `D-memory-add-<seq>` to decision-log
8. Output success path

**Confidence Tier:** 🟢 high(file create + index append)

---

## Subcommand: memory update(v1.1.10 — G2)

**Arguments:** `<name>` required

**Workflow:**

1. Locate memory file by name.
2. Show current content.
3. Sub-prompt for what to change(body / description / frontmatter)
4. Apply edit.
5. Update `MEMORY.md` hook if description changed.
6. Append `D-memory-update-<seq>` to decision-log
7. Output diff.

**Confidence Tier:** 🟡 medium(edit semantics may need PO judgment)

---

## Subcommand: memory remove(v1.1.10 — G2)

**Arguments:** `<name>` required

**Workflow:**

1. Locate memory file.
2. Show preview + require `CONFIRM REMOVE`(對齊 §K.8 destructive pattern).
3. On confirm:
   - Delete file
   - Remove entry from `MEMORY.md` index
   - Append `D-memory-remove-<seq>: name=<name> reason="<text>" by=PO at=<ISO>`
4. Output success(restore via git if needed within 7 days).

**Confidence Tier:** 🟡 medium(destructive — confirm phrase enforced)

---

## Subcommand: draft-modules-overview(v1.1.10 — G3 Step 1.1 helper)

**Arguments:** none(uses active project)

**Workflow:**

1. Resolve active project + read `<project>-requirement-spec.md` + state.md modules[].
2. Verify `state.md.modules[]` is populated(if empty,prompt PO to run `/pm advance-phase 1` Step 1.1 split first).
3. For each module,auto-draft:
   - 📋 What it does(from REQ descriptions + module artifact_type)
   - 👔 For PM(owner = state.md modules[].owner / risk_level / effort heuristic)
   - 🔬 For QA(test approach from artifact_type + key scenarios from REQ acceptance)
   - 💻 For Developer(REQ coverage list + suggested file paths from artifact_type)
4. Generate Big picture + dependency graph + coverage matrix.
5. Write to `docs/pm/<project>/spec/<project>-modules-overview.md`(對齊 §6.4.16 Step 1.1 deliverable structure)
6. Sub-prompt PO review + confirm.

**Confidence Tier:** 🟡 medium(LLM draft + PO review)

---

## Subcommand: draft-functional-spec(v1.1.10 — G3 Step 1.4 helper)

**Arguments:** `<module-id>` required

**Workflow:**

1. Resolve active project + read requirement spec + modules-overview + module entry in state.md.
2. Auto-draft per feature(從 module covers_reqs 衍生):
   - Feature ID + name
   - 📋 What it delivers(plain prose)
   - 👔 For PM(estimate / dependency)
   - 🔬 For QA(test surface / acceptance criteria refs)
   - 💻 For Developer(input/output / behavior / edge cases)
3. Write to `docs/pm/<project>/spec/modules/<module>/<project>-<module>-functional-spec.md`
4. Sub-prompt PO review + confirm.

**Confidence Tier:** 🟡 medium

---

## Subcommand: draft-design-spec(v1.1.10 — G3 Step 1.5 helper)

**Arguments:** `<module-id>` required

**Workflow:**

1. Resolve active project + read requirement + modules-overview + functional spec for module.
2. Auto-draft HOW per feature:
   - Function signatures
   - File paths(對齊 module artifact_type)
   - Library dependencies(對齊 memory `dep_management`)
   - State / DB / API contracts
   - Forward-compat invariants
3. Write to `docs/pm/<project>/spec/modules/<module>/<project>-<module>-design-spec.md`
4. Sub-prompt PO review.

**Confidence Tier:** 🟡 medium

---

## Subcommand: decision-log search(v1.1.10 — G4)

**Arguments:** `"<query>"` required

**Workflow:**

1. Grep across:
   - `docs/decision-log.md`(repo-wide)
   - `docs/pm/_org/org-decision-log.md`
   - `docs/pm/<project>/decision-log.md`(active project)
2. Output matches with context(eg. 2 lines before/after):
   ```
   🔍 Search 'BYPASS DISCIPLINE' — 3 matches:
     docs/decision-log.md:142
       D-override-001: BYPASS DISCIPLINE by=PO reason="emergency hotfix" at=2026-06-18
   ```
3. Sort by date desc.

**Confidence Tier:** 🟢 high

---

## Subcommand: decision-log filter(v1.1.10 — G4)

**Arguments:** `--since <YYYY-MM-DD>` required, `[--until <YYYY-MM-DD>]`, `[--type <prefix>]`

**Workflow:**

1. Walk decision-logs.
2. Filter entries by:
   - Timestamp range
   - Prefix(eg. `D-spectra-` / `D-phase-advance-` / `D-override-`)
3. Output filtered table sorted by date.

**Confidence Tier:** 🟢 high

---

## Subcommand: decision-log compact(v1.1.10 — G4)

**Arguments:** `[--older-than <Nmonths>]`(default 12)

**Workflow:**

1. Identify entries older than N months across decision-logs.
2. Show preview + require `CONFIRM COMPACT`(對齊 §K.8 destructive — moves entries).
3. On confirm:
   - Move old entries to `docs/decision-log-archive-<YYYY-MM>.md`(grouped by quarter)
   - Update active decision-logs to remove archived entries
   - Append `D-compact-<seq>: archived=<count> entries cutoff=<date>` to active log
4. Output success.

**Confidence Tier:** 🟡 medium(destructive — entries moved not deleted)

---

## Subcommand: daily-sync(v1.1.10 — G5 multi-dev ritual)

**Arguments:** none

**Workflow:**

1. Resolve active project + read team-roster.md.
2. **1-PO scenario check:** if `team_size == 1` AND `coverage_status` 非 `bootstrap-only` → output: `1-PO scenario detected — daily-sync is no-op. Use /pm daily for regular report.` + log + return.
3. Multi-dev scenario(team_size > 1):
   - For each engineer in team-roster.md members[]:
     - Show: last commit timestamp(git log per dev)
     - Show: open tasks(state.md modules[].owner = engineer)
     - Show: signoff pending(state.md phase_<N>_signoff_details.approvals missing this engineer)
   - Compute sync delay:engineers with > 24h no-commit → ⚠ flag
4. Output multi-dev sync table:
   ```
   👥 Daily Sync — <project> (<N> engineers)
   ────────────────────────────────────────
   Engineer    | Last commit | Open tasks | Signoff pending
   kuohsuming  | 2h ago      | 3          | (none)
   001         | 25h ago ⚠   | 2          | phase-1
   ```
5. Append `D-daily-sync-<seq>` to project decision-log.

**Confidence Tier:** 🟢 high(git log + state.md reads deterministic;1-PO no-op safe)

---

## Audit Trail Convention

Every state-mutating operation MUST:

1. Append entry to `docs/pm/_org/org-decision-log.md` (cross-project actions) OR `docs/pm/<project>/decision-log.md` (project-internal).
2. Entry format: `D-<type>-<seq>: <key-value-pairs> by=<actor> at=<ISO8601>`
3. Operations that delete files: append BEFORE deletion so audit survives.
4. Never silently mutate state; user-facing output always cites which audit file was written.

## Project Type Lock (referenced by archive/delete)

| Type | Source of Truth | Behavior |
|---|---|---|
| `production` | `state.md.project_type: production` | Strictest; archive needs reason, delete needs `--force` + 7d quiet |
| `training` | `state.md.project_type: training` | Permissive; supports 30d auto-archive |
| `poc` | `state.md.project_type: poc` | Middle; supports 90d auto-archive |
| `sandbox` | `state.md.project_type: sandbox` | Permissive; supports 30d auto-archive |

`/pm init` sets this at creation. **Upgrade path(對齊 Round 2 N4 fix)** — real-world POC → production / sandbox → poc 升級需求,以下兩條路徑擇一:

**Path A:Lightweight in-place upgrade**(`v1.1 planned`)— `/pm convert-type <project> --from <old> --to <new> --reason "..."`:
- 必填 reason,寫入 `_org/org-decision-log.md` `D-type-upgrade-<seq>`
- 允許方向:sandbox → training / training → poc / poc → production(只升不降)
- 拒絕方向:production → poc 等降級(降級代表設計改變,應走 archive + re-init)
- 自動保留歷史 audit:state.md 內 `project_type_history: [{from, to, at, by, reason}]` array
- 對齊 audit 連續性(downgrade 不允許因會混淆 lifecycle 安全等級)

**Path B:Archive + re-init**(v1.0 唯一可行)— 重型升級:
- `/pm archive "<project>" --reason "type upgrade"`
- `/pm init "<project>-v2" --type <new-type>`
- state.md 內 `predecessor_project: <old>`(audit 連續性靠 cross-reference)
- 適合「順便重整 module 結構」的大轉型

預設 v1.0 走 Path B(safe);Path A 待 v1.1 落地。

## Auto-expiry Daemon (conceptual; manual currently)

Training/sandbox projects past expiry should auto-archive. For now, `/pm dashboard` surfaces expired projects with action recommendation. Future Phase E落地 may add cron-like trigger.

## Auto Behavior Confidence Tier (user-facing convention)

Per manual rev 1.6 prefix block. Every SKILL output containing "auto-detected / auto-generated / 自動 ..." behavior MUST classify into 3 tiers:

| Tier | Confidence | Behavior on failure |
|:---:|:---:|---|
| 🟢 high | ≥ 90% | Abort + specific error |
| 🟡 medium | 60-90% | List evidence + ask PO; do not silent-confirm |
| 🔴 low | < 60% | Refuse to conclude; output raw data only |

Default for analytical outputs (impact analysis / module-fit / capacity estimate): medium tier with explicit fallback.

## Sub-Skill Integration

PM Skill orchestrates these sibling skills (under `skills/`):

| Sub-skill | When invoked |
|---|---|
| `spectra-review` (per proposal §6.4.3) | All `/pm validate-*` + Phase 0 Requirement Spec review |
| `namecard-v2-ddd-guardian` V0-V6 | Phase-specific tactical work (V1 planning / V2 implementation / V4 cross-doc review / V8 cross-module review) |

When delegating, pass the target file path + active project context. Sub-skill output schema is contracted in proposal §6.4.3 (spectra-review) and equivalent contracts for V0-V8 (deferred to Phase E per §6.4.12 future contracts table).

## Out of Scope

- Does NOT auto-edit code (delegate to V2 implementation skill or user).
- Does NOT run `git` commands beyond `log` / `status` reads (state mutations go through file writes for audit trail).
- Does NOT call external APIs (LINE / Azure / etc.) — those are owned by their respective service skills.
- Does NOT make decisions on behalf of user — Confidence Tier 🔴 low forces human escalation.
- Does NOT bypass `/pm gate-check` for advance-phase. No "skip gate" flag exists.

## Tone

Concise, structured, evidence-based. When uncertain, defer to PO with cited evidence (per Trust Hierarchy §6.4.4 — PO override > SKILL estimate).

Never rubber-stamp; always run relevant checks before reporting success.

Never invent file paths / project names / engineer skills — always read from state files.

## Version

- **v1.0** (2026-06-17) — Initial implementation aligned with proposal rev 1.6 + manual rev 1.8.
- **v1.0.1** (2026-06-17) — spectra-review Round 1 fix(1 BLOCKER + 3 CONCERN + 5 NIT 全 close):B1 移除 12 個 unimplemented commands + 加 §v1.1 Planned 段 fallback(Option C MVP 路線);C1 全文路徑 reference 統一 + Convention note;C2 frontmatter description 縮短;C3 Start Here 加 repo bootstrap 3 行;N1 init/archive/delete workflow 標 Confidence Tier;N2 bulk archive 0-match guard;N3 status outstanding_blockers source path 明示;N4 Project Type 加 upgrade path(Path A v1.1 planned / Path B archive+re-init);N5 加 `references/output-templates.md` stub。Round 2 verify verdict=ship-as-is。
- **v1.1** (2026-06-18) — minor change(對齊 §6.4.13 governance):新增 `/pm bootstrap-project` subcommand(11 步驟 workflow,Phase 2 智能 installer)+ `references/infra-deps.yaml` SSOT spec(180 行,system/python/services/credentials/verify_targets/scopes 6 段)+ AI-native two-phase setup 範式(setup.sh Phase 1 minimal + Claude Phase 2 智能)。spectra Round 1+2 全 close:scopes.include dotted path schema fix / sudo Path B 🔴 low Confidence Tier 明示 / install-history per-machine ~/.cache/ 分離 / optional verify_target skip rule。
- **v1.1.1** (2026-06-18) — spectra Round 3(setup.sh + SKILL cross-cutting handoff)fix:Step 4 加 no-sudo environment Branch C(corporate / Docker / no sudoers fallback)+ Router 表加 Confidence Tier note + Step 1 yaml schema_version forward-compat policy(v0/v1/v2 各自處理)+ Version section bump 對齊 router 表 v1.1 標註。Round 4 verify verdict=ship-as-is(對齊 spectra Round 3 9 fix 全 100% close)。
- **v1.1.2** (2026-06-18) — spec-only update(對齊 proposal rev 1.6 → rev 1.7):新增 §v1.2 Planned 段(6 命令:setup-worktree / daily-sync / push-gate / advance-phase 5 enhancement / deploy / rollback)+ proposal rev reference 更新 1.6 → 1.7 + Multi-Dev → Production 3-stage 架構 premise 文檔化。**workflow 未實作,觸發走 fallback;等 PO 授權 v1.2 落地**(對齊 §6.4.13 Contract Change Governance — 屬 minor change,加 commands 但不破壞既有 v1.0/v1.1)。
- **v1.1.3** (2026-06-18) — spec-only update(對齊 proposal rev 1.7 → rev 1.8 Cluster A):新增 §v1.2 Planned 段 4 個 schema migration commands(`/pm migration-status` / `/pm migration-propose <feature-id>` / `/pm migration-apply --env <env>` / `/pm migration-mark-applied --env prod --version <NNN>`)+ v1.2 Architecture Premise 加 staging migration apply 步驟 + Schema Migration Awareness 4 artifact 文檔化。**PM Skill aware DB migration 的 file hash + manifest 機制設計完整,對齊 memory `backend_schema_change_workflow` 100%**;workflow 仍未實作,等 PO 授權 v1.2 落地。
- **v1.1.4** (2026-06-18) — spec-only update(對齊 proposal rev 1.8 → rev 1.9 Gap 4 V8 pre-coding):v1.2 Architecture Premise 加 **Stage 0 V8 Cross-Module Spec Review Gate**(Phase 3 末 5 engineer+Tech Lead+PO 共審 N module F-spec+D-spec / verdict=ship-as-is / spec lock state)+ `/pm advance-phase 4` workflow 對齊 §D.2 V8 verdict check + `/pm contract-change propose` 對齊 §E.4b mid-flight drift check trigger / lite V8 workflow。**核心轉變記錄:V8 從 Phase 4 mid+end 移到 Phase 3 末,Phase 4 only 在 cross-module contract change 才觸發 lite drift check;對齊 PO 哲學「all module cross review job in done before coding」;workflow 仍未實作,等 PO 授權 v1.2 落地**。
- **v1.1.5** (2026-06-18) — spec-only update(對齊 proposal rev 1.9 → rev 1.10 Gap 5 No Fast Path Policy):v1.2 Planned 加 2 個 discipline 命令(`/pm validate-discipline-invariant` 機械化 check Phase 0-7 順序 + signoff lineage + git no-verify count;`/pm deploy --override-discipline --reason "<text>"` PO 唯一 escape valve + confirmation_phrase=BYPASS DISCIPLINE + override 自動 escalate next 3 retro)+ Architecture Premise 加 K.3 emergency response distinction(rollback=PATH vs fast track=BYPASS)。**核心:對齊 PO 拍板「紀律很重要,該走得還是要走,以策安全,小心駛得萬年船」+ 對齊 5 條 memory rule 哲學(backend_change_rule / dep_management / delete_dialog_no_undo_hint / friend_identity_change / backend_schema_change_workflow);override metrics alarm(1 月 1 次 warning / 2 次 escalate / 3 次 freeze)。Workflow 仍未實作,等 PO 授權 v1.2 落地**。
- **v1.1.6** (2026-06-18) — spec-only update(對齊 proposal rev 1.10 → rev 1.10.1 Spectra Round 1 fix #13):router 表 2 個 discipline 命令 rev 標籤 1.10.1→1.10 還原(歷史保留);SKILL.md 全 proposal rev refs 1.10 → 1.10.1。**No new command**,純 spec patch trace(對齊 7 fix:B1 override scope + B2 spec re-entry + C1-5 contract row / D-spec / alarm fallback / prod migration / V8 gate);workflow 未實作,等 PO 授權 v1.2 落地。
- **v1.1.7** (2026-06-18) — **v1.2 first implementation — `/pm push-gate` workflow** 落地(PO 拍板 Option B Critical Path Batch 第 1 命令):Subcommand Router 加 `/pm push-gate` entry(active);v1.2 Planned 表 push-gate 標 ✅ Implemented;新加 `## Subcommand: push-gate` workflow section(9 條 check / 7 步 workflow / 6 edge case fallback / audit per push to daily report / pre-push hook 對齊 §E.8.5)。**對齊 proposal §6.4.11 §E.8.4 + §E.3a 三向 invariant + memory `backend_lint_workflow` + §K.4 No Fast Path Policy + §K.9 override metrics**。8 命令 Critical Path Batch 第 1/8。Confidence Tier 🟢 high(全機械化 check)。
- **v1.1.14-deferred** (2026-06-18) — ⭐ 2026-06-20 spectra Round 2 B3 fix:relabeled from `v1.1.14-spec` to `v1.1.14-deferred`(non-monotonic with surrounding v1.4-validated → v1.1.x — explicit deferred tag clarifies status). **Phase 3 CI/CD wrap migration spec(design-only,未實作)**:PO 抓 CI/CD vs /pm deploy 共存 conflict 後催生 — 寫 `docs/2026-06-18-phase-3-cicd-wrap-migration-spec.md`(~600 行 design-complete spec,13 sections + 3 appendix):goal-state architecture(PM Skill wraps gh workflow run,**single deploy executor = Actions**)+ canonical `.github/workflows/deploy.yml` template(OIDC auth + auto rollback + tag-on-success)+ Azure OIDC vs Service Principal setup(對齊 §4 推薦 OIDC passwordless)+ /pm deploy v1.3 Step 4 改寫(gh workflow run + run watch + audit Actions URL)+ azure-config.yaml `cicd` schema 段(`pm_skill_wraps.enabled` toggle,backward compat)+ Phase 1→2→3 migration checklist(每 phase 5-8 pre-flight checks)+ risk analysis 7 條 + 8 OQ 待 PO 拍板 + validation 3-step plan。**等 PO 觸發 Phase 2(LIFF-Beauty repo stable)後啟動 Phase 3 真實實作**。Spec rev v1.0,non-blocking design 累積。
- **v1.4-validated-candidate** (2026-06-19) — **`/pm build-team` 3 invocations + 11 findings all fixed(eat-own-dog-food #18+#19+#20)**:7 new fixes apply Step 1 加 member_type ambiguous parse fallback(對齊 #20 NIT #7);Step 1.5 加 NEW pre-execution validation gate(fail-fast for REQ-013 F-9 + REQ-014 §F bootstrap protection + consultant constraints,對齊 #20 BUG #4);Step 2 加 inquire mode skip explicit(#19 NIT #3);Step 4 加 inquire skip(#19 NIT #4);Step 5b 加 NEW refuse output template(#20 NIT #6);Step 7 加 intent-dependent output format(verdict for modify;full status for inquire,對齊 #19 BUG #3);Step 9 加 audit special cases(inquire log invocation;refuse log event,no team-roster mutation,對齊 #19 NIT #5)。Lifecycle stage upgrade `v1.4-tested` → `v1.4-validated-candidate`(對齊 §6.4.15 Validated gate part 2 satisfied:100% close rate;part 3 needs ≥ 14 day stable → production-ready)。
- **v1.4-tested** (2026-06-19) — **`/pm build-team` first real invoke + 4 findings fix(eat-own-dog-food #18)**:Workflow Step 1 加 `mixed` intent enum + mixed_intent sub-op decomposition(對齊 BUG #1 fix);Step 4 拆「Verify(existing)or Apply(new)default tier」明示 intent-based logic(對齊 NIT #1 fix);Step 5 加 confirm tier 3 層(low=`y` / medium=`CONFIRM TEAM` / high=`FORCE TEAM`)(對齊 BUG #2 fix);Step 8 加 「pm_newly_assigned semantic 明示 was_no_pm AND is_now_pm」(對齊 NIT #2 fix)。Workflow lifecycle stage upgrade `v1.4-spec` → `v1.4-tested`(對齊 proposal §6.4.15 new lifecycle concept)。
- **v1.4-spec** (2026-06-19) — **Team Composition Contract 落地 spec — `/pm build-team` workflow + §6.4.14 proposal section**(對齊 PO 2026-06-19 連續 4 insights lock):新加 `## Subcommand: build-team` workflow section(9 步 NL→YAML / sub-prompt 缺 role / default tier auto-grant / MVT coverage check / postponed_commands resume / bootstrap protection / AI_Agent constraints / consultant constraints / cross-command integration);proposal §6.4.14 Team Composition Contract 完整 8 sub-sections;backend-schema-auto-sync spec REQ-013 + REQ-014;state.md.postponed_commands[] field 新加;cross-command team coverage gates 加(hard block /pm advance-phase 1 + /pm deploy --target prod + /pm signoff phase-N + /pm rollback;soft reminder /pm status + /pm daily + /pm verify-runtime Layer 6)。**Workflow 未實作**(team-roster v2 + spec/proposal/SKILL.md spec ready,etc PO 觸發 v1.4 implementation)。Cross-refs:本 session 第 6 個 PO architectural insight(team-roster design)+ meta-dogfood eat-own-dog-food #16 累積 17 個 findings。
- **v1.1.13** (2026-06-18) — **Cross-doc coherence detection 內建化(PO meta-question:「有內建命令找這類 bug 嗎?」)**:`infra-deps.yaml` system + 4 entries(`git` / `gh` / `curl` / `zip` — drift detection 用 SKILL.md grep 抓到 git 用 58 次但不在 SSOT,zip 11 次,等);scopes 全 4 個(minimal/standard/full/deploy)update — minimal 加 git+curl,standard 加 git+gh+curl,full 加 4 個 + zip,deploy 加 git+curl+zip。**SKILL.md `/pm verify-runtime` 加 3 個新 check** — Layer 3 Tool↔SSOT drift(grep workflow tools vs SSOT)、Layer 4 Decision-log↔SSOT drift(D-dep-* 跟 SSOT 雙向 audit)、Layer 5 Workflow↔Project Lifecycle drift(workflow 讀 state.md 但 no active project warn)。**這是針對 PO 連抓 2 個 cross-doc bug(spectra-review 15 輪沒抓到)而 systematize 的工具化補強**。對齊 memory:dep_management(propose+ack 必有 SSOT 同步)+ §6.5 特性 2(Stage Gate 機械化)。
- **v1.1.12** (2026-06-18) — **`infra-deps.yaml` SSOT drift fix(PO 抓 az/jq/yq 沒進 setup 清單)**:`infra-deps.yaml` `system` section 加 3 個 deploy tools — `azure_cli`(propose_required: true 對齊 memory:dep_management 嚴格 propose+ack,install_script Microsoft 官方 + post_install_note az login)+ `jq`(apt install)+ `yq`(GitHub release binary 因 Ubuntu 22.04 repo 沒 v4);`verify_targets` 加 4 條(jq / yq mikefarah-flavor / az / az auth);`scopes` 更新 — `standard` 加 jq+yq(/pm deploy file plumbing 可看)/ `full` 加 jq+yq+az(完整 prod-like deploy)/ **新加 `deploy` scope**(extends standard + azure_cli + post_install_required_manual 列 az login / azure-config.yaml / .env.*)。**今天 ad-hoc install(D-dep-001/D-dep-003 audit)現在進 SSOT,新 dev machine `/pm bootstrap-project --scope deploy` 可一條龍裝完**。對齊 PO 真實抓到的「Spec → Impl → Runtime → **SSOT** drift」第 5 層(spectra-review #15 漏抓,#16 candidate)。
- **v1.1.11** (2026-06-18) — **SKU-aware Deploy + Real LineBOT Azure Setup 落地**(PO 2026-06-18 Option C 拍板):/pm deploy Step 4 拆 4.1 slot_swap(Standard+)/ 4.2 direct ZIP deploy(Basic SKU,~30s downtime,$0 cost);/pm rollback Step 2 拆 2.1 slot_swap_back / 2.2 redeploy_previous_tag;/pm verify-runtime Step 4 加 SKU auto-detection logic + `azure-config.yaml` v1 schema 完整化(sku_tier / deploy_strategy / rollback_strategy / health_check / upgrade_path)+ `--setup-azure-config` 自動 populate hint。**真實 Azure setup 落地**:`azure-config.yaml` 建好(`liffbeauty.azurewebsites.net` / RG=`beautyreservation_group` / japaneast / Basic SKU / direct strategy);`docs/release/smoke-test.sh` 建好 + 對 live prod `/health` 200 OK 確認可用;`.env.example` template(3 envs)+ `docs/decision-log.md` 建立(D-dep-001 install azure-cli + D-dep-002 SKU Option C)。對齊 proposal rev 1.12 §G.6.1 SKU-aware spec + spectra v1.1.10 C2 fix(deploy 讀 azure-config)。**`/pm deploy` 從 spec-only 進化為 real-working**(Basic SKU direct deploy path)。
- **v1.1.10** (2026-06-18) — **Runtime Prerequisite Audit Layer**(PO 抓 deploy Azure CLI gap → 補第 3 層 audit dimension):新加 `/pm verify-runtime` 命令(Subcommand Router entry + workflow section)— 6 段 check(platform / core CLI / Azure CLI+auth / azure-config.yaml / .env.<env> / smoke-test.sh)+ map missing deps to which `/pm` commands DEAD/PARTIAL/OK + setup guide(對齊 memory:dep_management PO ack first)。3 個 affected commands 加 RUNTIME PREREQUISITE banner — `deploy` / `rollback`(均需 az CLI + auth + azure-config.yaml)/ `migration-apply`(dev/staging 需 .env.<env>)。**核心:Spec layer + Impl layer + Runtime layer 三層 audit 完整化;spectra-review #14 漏的 runtime dimension 補上;PO 真實抓 gap 是 dogfooding 最高價值**。Confidence Tier 🟢 high(read-only audit)。對齊 memory `azure_webapp_runtime`(Azure Linux 3.0)+ `dep_management`(無 unauthorized install)。
- **v1.1.9** (2026-06-18) — **Spectra Round 1 fix (eat-own-dog-food #14, implementation-level 首次)** — 1 BLOCKER + 6 CONCERN 全 close:**B1** setup-worktree pre-push hook 改 pure bash(不依 Claude CLI,跑 4 critical check;完整 9-check 仍 `/pm push-gate` interactive);**C1** validate-discipline Check 5 加 best-effort caveat + 3-tier metric source 表(deterministic / best-effort / proxy);**C2** rollback Step 3 加 `FORCE STAGING` 二次確認 + `--force-with-lease` 改 safer alternative(對齊 CLAUDE.md);**C3** proposal §G.6.0.2 加 `ssot_pending: bool` field(對齊 spec → impl drift 收回,proposal rev 1.10.1 → 1.10.2);**C4** deploy Step 1 改 **COLLECT-ALL mode**(6 條 precondition 全跑完一次列 fix,PO 1 趟修完);**C5** migration-mark-applied 加 Prerequisites section(`.env.prod` optional,缺則 PO 自輸 fallback);**C6** push-gate emergency bypass output 改寫 metric source 3-tier hierarchy + Engineer self-audit checklist。Round 2 verify verdict=ship-as-is。**首次 implementation-level review 抓到 spec → impl gap(B1 hook runtime)= 真實 dogfooding 價值**。
- **v1.1.8** (2026-06-18) — **Critical Path Batch 2/8 — 8/8 完成 — 7 個剩餘 v1.2 commands workflow 落地**(PO 拍板 Option A 直接跑完整 batch):新加 7 個 `## Subcommand:` sections — `setup-worktree`(Stage 1 init,git plumbing + pre-push hook install,🟢 high)/`migration-status`(read-only visual matrix,🟢 high)/`migration-propose <fid>`(SQL 3 樣 prompt + manifest entry + SSOT update + functional.md tag,🟡 medium)/`migration-apply --env <env>`(dev/staging auto-execute + prod print only 對齊 memory:PO 自 apply,🟡 medium / 🔴 low)/`migration-mark-applied --env prod --version <NNN>`(verify_sql 自動 + PO 自填 fallback + state.md update,🔴 low)/`validate-discipline-invariant`(6 條 machine check 對齊 §K.6,🟢 high)/`deploy --target <env> [--override-discipline]`(multi-precondition + Azure CLI slot swap + auto rollback fallback + override scope ONLY discipline,🔴 low)/`rollback [--to <commit>]`(zero-downtime swap-back + 24h root cause requirement 對齊 §G.6.2 + §K.3,🔴 low)。Subcommand Router 加 7 active entries;v1.2 Planned 表全 7 標 ✅ Implemented(v1.1.8)。**Critical Path Batch 8/8 完成,1-PO+Claude + 5-engineer 工作流 full coverage;對齊 proposal rev 1.12 §E.8 / §G.6.0 / §G.6.1 / §G.6.2 / §K 全 spec + memory `backend_schema_change_workflow` / `backend_lint_workflow` / `dep_management` / `azure_webapp_runtime` 100%**。SKILL.md 從 ~1100 行成長到 ~1850+ 行。Confidence Tier framework consistent。
- **v1.1.9b** (2026-06-20) — **v1.1 Planned 12 commands batch 落地**(⭐ 2026-06-20 spectra Round 2 B3 fix:renumbered from v1.1.9 to avoid collision with 2026-06-18 entry above)(PO 2026-06-20 directive `implement v1.1 planned`):新加 12 個 `## Subcommand:` sections — `weekly`(7-day aggregated daily,🟢 high)/`health-check`(multi-layer SKILL audit 7 layers,🟢 high)/`kpi-eval`(Phase 7 KPI verify,🟡 medium)/`requirement impact-analysis <REQ-id>`(blast radius graph walk,🟡 medium)/`assign-feature <fid> --to <eng> [--pair <X>]`(manual ownership override,🟢 high)/`contract-change status`(grep + classify pending/applied/rolled-back,🟢 high)/`contract-change rollback --change <N> --reason "<text>"`(CONFIRM ROLLBACK destructive phrase,🟡 medium)/`contract-change history --window <N>months`(Evolution Report aggregate by section + tier,🟢 high)/`cross-project sync-decision <text> --to <projects>`(multi-file append + audit,🟢 high)/`cross-project resource-check`(member overload detect,🟡 medium)/`cross-project common-pattern`(pattern detection heuristic,🟡 medium)/`org-retrospective --window <N>months`(half-year retro aggregate + themes,🟡 medium)。Subcommand Router 加 12 active entries;v1.1 Planned 表全 12 標 ✅ Implemented(v1.1.9)。**對齊 proposal §6.4.13 Contract Change Governance — minor change tier,加 commands 不破壞既有 v1.0-v1.2 schema**。SKILL.md 從 ~2700 行成長到 ~3100+ 行。
- **v1.5-sdlc-v2**(2026-06-20)— SDLC v2 Contract promoted to canonical(proposal rev 1.13 §6.4.16);Phase 0/1/2 reorder(team-build 從 Phase 0 移到 Phase 1 Step 1.2;Phase 1 EXPANDED 5-step + modules-overview.md HUMAN-FIRST 3-role 強制結構;Phase 2 LIGHTENED plan.md only + solo carve-out);/pm gate-check + /pm init + /pm build-team + /pm advance-phase 1 workflows aligned per spectra Round 1 audit(0 BLOCKER + 3 CONCERN closed via micro-fix in commit 46c398d);memory `feedback_human_first_docs` saved as cross-doc invariant。
- **v1.1.10** (2026-06-20) — **Gap closure batch — 14 commands across G1-G5**(PO 2026-06-20 directive `implement all 14`,coverage audit follow-up):新加 14 `## Subcommand:` sections:**G1 SDLC v2 validators(3):** `validate-modules-overview` / `validate-functional-spec` / `validate-design-spec`(全 🟢 high structural check + 🟡 HUMAN-FIRST heuristic)。**G2 memory ops(4):** `memory list`(🟢)/ `memory add <name> --type`(🟢)/ `memory update <name>`(🟡)/ `memory remove <name>` CONFIRM REMOVE 對齊 §K.8(🟡)。**G3 spec drafters(3):** `draft-modules-overview`(Step 1.1 helper)/ `draft-functional-spec <module>`(Step 1.4 helper)/ `draft-design-spec <module>`(Step 1.5 helper)— 全 🟡 medium(LLM draft + PO review)。**G4 decision-log ops(3):** `decision-log search "<query>"`(🟢)/ `decision-log filter --since <date>`(🟢)/ `decision-log compact --older-than <Nmonths>` CONFIRM COMPACT(🟡)。**G5 daily-sync(1):** 1-PO scenario auto no-op + multi-dev table(🟢)。Subcommand Router 加 14 active entries。**對齊 proposal §6.4.13 minor change tier — additive 不破壞既有 schema;closes 14/14 PM Skill gap items per coverage audit**。SKILL.md 從 ~3100 → ~3500+ 行。Confidence Tier distribution:8🟢 + 6🟡。
- **v1.1.11** (2026-06-20) — **Mid-Phase Requirement Change Governance — §6.4.17 + 4 new commands**(PO 2026-06-20 directive `A regarding re-split`,proposal rev 1.14):**5 principles:** P1 NEVER auto rollback(PM via `/pm advance-phase <N<current>` + CONFIRM ROLLBACK §K.8)/ P2 NEVER auto module reorg(PM via `/pm requirement *` + sub-prompt)/ P3 minimum spec re-author(僅 affected modules)/ P4 audit mandatory / P5 PM-driven placement。**4-tier cascade matrix:** 🟢 no-cascade / 🟡 patch / 🟠 re-assign / 🔴 ~~rollback~~(folded into `/pm advance-phase` backward path)。**5 new commands:** `requirement drop <id> --reason`(empties module → PM sub-prompt)/ `requirement add-mid-phase <id> --reason`(PM placement:existing module / create new / defer)/ `requirement modify <id> --aspect <X> --reason`(PM re-author decision)/ `spec-rev-bump <project> --rev <X>.<Y>`(post-signoff amendment audit)。**Enhanced commands:** `requirement impact-analysis` enhanced(tier + placement suggestion)+ `advance-phase` supports N<current rollback path(R1-R5 sub-workflow + CONFIRM ROLLBACK + artifacts preservation to `_phase<X>_rollback/<ISO>/`)。對齊 §6.4.13 minor change tier + §6.4.16 SDLC v2 Phase 1 cascade + §K.8 destructive phrase + memory `feedback_human_first_docs`(amendment 仍 3-role)。**核心:Phase 1+ developer 想 drop/add/modify REQ 但保留已完成 functional/design spec,PM 拍板 module placement,not auto reorg**。SKILL.md 從 ~3500 → ~3700+ 行。
- **v1.1.12** (2026-06-20) — **`/pm requirement impact-analysis` phase-aware + cost-aware Tier**(對齊 PO 2026-06-20 enhancement `both`,eat-own-dog-food #39 findings,proposal rev 1.15):**Phase-aware logic** — Step 4 rewritten:read `state.md.current_phase` + for-each phase P ∈ [0..C] assess artifact impact:Phase 0(spec rev bump + spectra --quick 15-25 min)/ Phase 1(modules-overview + functional + design spec re-author 30-60 min)/ Phase 2(plan.md 15-20 min)/ Phase 3(shared infra 15 min)/ Phase 4(Python/SKILL/memory code refactor + tests 30-180 min/module)/ Phase 5(integration 30-60 min)/ Phase 6(release 60-180 min)/ Phase 7(metrics 120-480 min)。**Cost-aware Tier 4th 🔴 major-rework** added(> 240 min cost — code refactor + tests + integration + possibly deploy abort);**Tier formula:** `Tier = max(cascade_scope_tier, rework_cost_tier)` worst wins。**Output format:** per-phase impact table + total cost + tier breakdown + PM placement + action sequence + 🔴 fallback options(Option A current-phase apply,Option B `/pm advance-phase <N<current>` rollback per P1)。對齊 §6.4.17 rev 1.15 + P3 minimum re-author + P5 PM-driven choice。
- **v1.1.13** (2026-06-20) — **§6.4.17 specialized operations — 3 commands batch**(對齊 PO 2026-06-20 directive Option B,proposal rev 1.16,close Phase 1 真實 trigger gaps from coverage audit):**3 specialized requirement commands added:** **`/pm requirement split <REQ-id> --into <new-id-list> --reason`** — carve-out source REQ into N new REQs(PM-assigned acceptance criteria per new + per-new module placement)+ CONFIRM SPLIT + spec rev bump(🟡)/ **`/pm requirement merge --reqs <id-list> --into <new-id> --reason`** — consolidate N REQs into 1(same-module precondition + PM field reconciliation:title/desc/acceptance/dependencies/risk-max/effort-sum)+ CONFIRM MERGE + spec rev bump(🟡)/ **`/pm requirement move <REQ-id> --from <module> --to <module> --reason`** — non-destructive ownership transfer(REQ content unchanged)+ artifact-type compat warning + CONFIRM MOVE + NO spec rev bump(🟢)。**對齊 P3 minimum re-author + P4 audit + P5 PM-driven + spectra --quick**。Subcommand Router 加 3 entries。Coverage audit 8/8 specialized scenarios:close 3/8(split / merge / move)+ defer 5(bulk / rename / restore / history / diff)pending dogfood findings。
- Future minor changes: add inline; bump version when contract-pack semantics change.

## See Also

- `docs/pm/pm-skill/spec/pm-skill-proposal.md` rev 1.12 — full contract spec(含 §6.4.11 §E.8 / §F.6 / §G.6 v1.2 Multi-Dev Workflow Commands + §K Discipline Invariant)
- `docs/pm/pm-skill/docs/pm-skill-user-manual.md` rev 1.8 — 18 scenarios + appendices
- `docs/pm/pm-skill/docs/pm-skill-proposal-highlights.md` — boss-facing 5-min brief
- `../spectra-review/SKILL.md` — design review skill (delegated by validate-*)
- `references/lifecycle-policy.md` — detailed archive/delete safety rules (this dir)
- `references/output-templates.md` — daily / dashboard / briefing output format templates(對齊 Round 2 N5 fix)
