# Claude Code Bootstrap — in-win(表面平整檢查系統)

> 本檔改編自 `AzureLineBOT/CLAUDE.md`,沿用其 AI 開發框架(V-mode / spec authoring / PM Skill / SCR / Spectra Review / multi-agent team)。
> AzureLineBOT 專屬內容(LINE Bot runtime、sanity TC、`lint.sh`、action/copy inventory)已移除。

讀這份檔案後,立刻依序讀取:

**A. 每次必讀**

1. `docs/ai-principles.md` — Mode Map V0-V7 + Immutable Rules A/B/C
2. `Downloads/表面平整檢查系統_需求規格書.md` — 本專案目前的需求規格書
3. `docs/pm/active-project.txt` — current active PM project(若存在)

**B. 按工作類型讀**

| 觸發條件 | 讀 |
|---|---|
| 要 **寫或改 spec** 時 | `docs/pm/5-spec-authoring-framework.md` — spec authoring standard |
| 要判斷 **spec 夠不夠完整** 時 | `docs/ddd-doc-maintenance.md` — spec completeness standard |
| 觸發下方 **Requirement Spec Authoring Gate** 時 | `docs/pm/spec-authoring/requirement-spec-authoring-rules.md` — 三元組不變式 |
| 用 `/spec-team` `/build-team` `/compliance-check` 時 | `docs/pm/multi-agent-dev-system/team-conventions.md` + `execution-plan.md` |

> ⚠️ `docs/ai-principles.md` 等框架文件原為 AzureLineBOT 撰寫,其中提到 `docs/CONTEXT.md`、`docs/dependency-map.md`、`docs/index.md`、`lint.sh` 等檔案在本 repo **尚不存在**;遇到時視為「本專案待建立」,不要假設其內容。

讀完 A 組後才開始工作。若使用者指定 V0-V7,依 `docs/ai-principles.md` §3 Mode Map 執行。

**預設模式為 V2(直接開發)。**

## Skill Triggers

| Trigger | Skill | Location |
|---|---|---|
| `/pm <subcommand>` | PM Skill(AI Project Assistant) | `skills/pm-skill/SKILL.md` |
| `/spec-compliance-review <target>` 或 `V7 <target>` | V7 SCR(Specification Compliance Reviewer) | `skills/spec-compliance-review/SKILL.md` |
| `/spectra-review <target>` | Spectra Review(enhanced-v1 quality review) | `skills/spectra-review/SKILL.md` |

Multi-agent team 前門(`.claude/commands/`):`/spec-team <feature>` → `/build-team <project>` → `/compliance-check <project>`;subagent 定義在 `.claude/agents/`。

PM Skill 對齊 `docs/pm/pm-skill/spec/pm-skill-proposal.md`。V7 SCR 對齊 `docs/pm/v7-spec-compliance-review/spec/scr-requirement-spec.md`。Spectra Review 對齊 `docs/pm/spectra-review/spec/spectra-review-requirement-proposal.md`。

## Requirement Spec Authoring Gate(entry-agnostic,跨 mode 常駐硬規則)

任何**討論結論或提案**指向 create / update / delete 某 requirement spec 的**三元組任一元素**(REQ / Golden Scenario / Anti-example)時,不論當前 V-mode,**必須**遵守 `docs/pm/spec-authoring/requirement-spec-authoring-rules.md`:

- **discuss mode(V1/V6)**:先攤開 decision-time 影響 + Triad Auto-Completion 草擬缺的元素 → **conditional 2-step popup**(rulebook §5.2 SSOT):★step-1 描述確認(僅 `Statement` 有實質改寫)→ [sizing gate §7 SPL-1,太大則拆]→ ★step-2 三元組 batch 一次確認;僅在使用者答「是」後才離開 discuss-only 動檔。缺 golden/anti 需二次確認 + `[GAP]` 標記。**觸發邊界(§5.1):ceremony 僅在討論收斂到「要 author/改此 REQ」時啟動 —— 探索 / 一般 V1 討論不觸發。**
- **execute mode(V2/V4)**:直接依 write-time 全規則(§4 checklist + §6 CRUD delta)。
- **Coverage Expansion(所有 mode 強制)**:**舉一反三**列 ~3 個相鄰/隱含候選(sibling REQ / 額外 scenario / 額外 anti-example),**逐一**討論 add/mod/del(proposal-only,grounded,防 gold-plating)。
- **准入閘門(§2.5)**:候選需求須過 5-test(可追溯 / 有證據 / 值得寫 / 是what非how / 有必要)才寫入,否則進 Open Questions / Out of Scope / 反推 what;T3 carve-out=安全·資料·法遵;PO 可 override(記 log)。
- **寫入前 3-role sign-off(§5.5)**:三元組齊後、寫入 spec 前,per-REQ 派 👔PM/🔬QA/💻Dev sign-off(non-blocking);solo=collapse 1 張。
- **delete(任何 mode)**:破壞性 → **PO-confirm 一律必做**;預設 Deprecate 優先於硬刪;REQ-ID 永不重用。

## Files That Must Never Be Auto-Modified

The following files require **explicit user instruction** before any AI tool may modify them:

| File | Role |
|------|------|
| `docs/ai-principles.md` | Repo Law |
| `docs/ddd-doc-maintenance.md` | Repo Law — spec completeness standard |
| `CLAUDE.md`, `AGENTS.md` | AI Bootstrap |
| `.gitignore` | Repo Config |

**Rule:** If a task appears to require modifying any of these files, stop and ask the user to confirm the intent before proceeding.

## Definition of Done

- Canonical docs(需求規格書 / spec)are updated when required
- A changeset exists for user-facing or behavior-changing work(per Rule B, under `docs/release/changes/`)
- Relevant syntax checks, tests, or smoke steps were run when available
