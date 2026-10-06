# AI Principles

> Purpose: one shared operating contract for all AI tools used in this repo
> Last Updated: 2026-08-06(§3 fallback enum `V1`→`V0` + §4.1 適用範圍 V0–V6→V0–V7 —— 修正 `ac28ab0` 遷移時寫出三種不一致範圍;PO 授權)
> Previously: 2026-06-30(V7 spec compliance mode added per SCR rev 0.2.3 D-058 + Track 3 propose-first authorize)

## 1. Source Of Truth

- Project rules live in this repo.
- IDE-specific prompts, chat presets, or adapters must not override repo rules.
- If a tool supports local skills, it should use [skills/namecard-v2-ddd-guardian/SKILL.md](skills/namecard-v2-ddd-guardian/SKILL.md).
- If a tool does not support local skills, it must still follow this file and [docs/index.md](docs/index.md).

## 2. Bootstrap Read Order

Read in this order before major work:

1. `docs/ai-principles.md`
2. `docs/index.md`
3. Relevant L1/L2 canonical docs from `docs/index.md`
4. Relevant L3 Primary doc for the task

## 3. Mode Map

- `V0`: bootstrap only; read rules and gather context
- `V1`: quick discussion; prefer analysis over code
- `V2`: direct development; implement allowed work end-to-end
- `V3`: review mode; findings first, summary second
- `V4`: doc proposal only; no runtime edits
- `V5`: DDD convergence; fix boundaries, invariants, and ownership
- `V6`: long-form analysis; high-stability reasoning and explicit assumptions
- `V7`: spec compliance review; code ↔ 3-layer spec(req/func/design)compliance via `/spec-compliance-review` skill(per `docs/pm/v7-spec-compliance-review/spec/scr-requirement-spec.md`)

If the user explicitly names `V0` to `V7`, follow it. Otherwise default to `V2`.

> **Requirement spec authoring（跨 mode gate）**：任何 mode 下,若要 create / update / delete requirement spec 的三元組任一元素(REQ / Golden Scenario / Anti-example),必須遵守 `docs/pm/spec-authoring/requirement-spec-authoring-rules.md`（V4 建/改 spec 為主要入口;discuss mode 走 decision-time popup;delete 一律 PO-confirm）。此為 entry-agnostic gate,詳見 `CLAUDE.md` §Requirement Spec Authoring Gate。

## 4. Shared Execution Rules

### 4.1 Three Immutable Execution Rules

以下三條規則適用於所有 skill、所有 mode（V0–V7）、所有工具（Claude Code / Antigravity / Codex）。**無例外、不可覆寫。**

#### Rule A — Spec-First Gate

> 必須有規格文件後，才能修改程式或活動。

- 修改 runtime code、config、SQL、activity 之前，對應的 canonical doc（L1/L2/L3 Primary 或 Supporting）必須已存在且涵蓋此次變更
- 若 spec 不存在：先建立或補齊 spec，取得使用者確認後才能動 code
- 若 spec 存在但不涵蓋此次變更：先更新 spec，再改 code
- **「spec 涵蓋」的判斷標準**：見 `ddd-doc-maintenance.md §7`（Spec Completeness Standard）— Universal Minimum M1–M5 全部通過，且 type-specific 要求中與本次改動相關的也通過
- **違反此規則 = guardian violation，必須回到 Plan phase**

#### Rule B — Release Note Mandatory

> 每次修改文件、程式、或活動都需要有 release note。

- 任何修改 canonical docs、runtime code、SQL、config、SKILL/governance 文件，都必須在 `release/changes/` 新增一筆 changeset
- 唯二例外：(1) 純討論（V1 Quick Discussion）(2) 不影響語義的 typo fix
- **無 release note = Ship 未完成**

#### Rule C — Dependency Impact Check

> 每次修改前必須查詢前後關聯文件或程式，確認是否需同步新增、修改、或刪除。

執行步驟：

1. 列出本次修改直接影響的文件與程式清單
2. 對每一項，查詢 `docs/dependency-map.md §1–§6`（L1/L2/governance/runtime 的 file-level 依賴清單）找出 upstream / downstream
3. 判定每一項關聯是否需要同步修改：
   - **規格清楚** → 在同一任務中一起修改
   - **規格不清楚** → 停下來，向使用者說明不清楚之處，討論確認後再進行
4. **Topic-level blast radius check**：查詢 `docs/dependency-map.md §8`（Cross-Topic Dependency Map）
   - 若改動命中 §8.1 觸發條件（L1/L2 改動、Auth Handshake、Identity Manager、OCR Flow、domain-model §6 Lifecycle…）→ 評估 topic-level 爆炸半徑；在 closeout 附 G5 細表
   - 若未命中 → 記一行「G5 查粗表，無高影響上游觸發」
5. 不得跳過此步驟直接修改單一檔案

**「規格不清楚就停下來討論」是硬性 gate，不是建議。**

> **配套工具**：
> - `docs/dependency-map.md §8` — Cross-Topic Dependency Map（粗表 + 細表格式）
> - `docs/ai-contract-pack-index.md` — 修改 Wave 1 主題前讀取的約束摘要索引
> - `docs/spec-traceability-matrix.md` — Primary Spec → 實作 runtime files 的正向追溯
> - `docs/acceptance-evidence-matrix.md` — Invariant → 驗收證據映射（B2 blocking condition 判斷依據）

---

- Respect the repo's DDD and layer boundaries.
- Router / handler / use-case / service / store / policy responsibilities must remain aligned with canonical docs.
- Do not invent new project rules outside repo docs.
- If code and docs drift, fix the drift instead of silently choosing one side.
- Do not use hardcoded UI copy when the project already uses managed copy/i18n.
- Frontend-initiated integration analysis between `v2` UI and legacy/backend sources must be written into the relevant `*-integration-notes.md`, not left only in chat.
- If one integration track spans multiple topics, add or update a dedicated Supporting integration note and link it from `docs/index.md` and/or the relevant topic docs.
- Any doc or runtime delta introduced by that integration must be explicitly annotated as belonging to that integration track.
- If a frontend-initiated integration changes an existing `v2` runtime file, add a short adjacent code comment that marks the integration track, the touched responsibility, and whether the behavior is still transitional or backend-authoritative.
- If a legacy file from `AzureLineBOT_ai` needs annotation or modification for integration analysis, treat the legacy repo as read-only reference first: copy the working file into `v2`, then annotate or modify only the `v2` copy.
- Any such working copy must clearly record frontend notes, backend notes, and removal status.
- Unless the user explicitly decides otherwise, the default removal status for a working copy is `User Decision Required`; do not delete it automatically. This is a transitional integration rule and may be removed after the legacy track sunsets.
- Security boundaries defined in `docs/security-governance.md` apply to all modes and all tools.
- When a task crosses a trust boundary（token / credential path、`innerHTML` injection、`localStorage` write、user input → display、external navigation、或其他 security-sensitive crossing）, verify compliance with `docs/security-governance.md §2` S1–S7 before shipping.
- If local skills are available, use `skills/namecard-v2-ddd-guardian/references/security-review.md` as the quick operating guide; otherwise apply `docs/security-governance.md §5` directly.

## 5. Release Note Rule

- Any user-facing or behavior-changing task must add exactly one changeset file under `release/changes/`.
- Release notes are generated from changeset files plus git history.
- Do not rely on commit messages alone for release notes.
- One task should map to one changeset, even if multiple IDEs touched the same path.

## 6. Task Isolation Rule

- Prefer one task per branch or `git worktree`.
- Do not let multiple IDEs edit unrelated work in the same branch at the same time.
- If multiple IDEs work on the same task, they still share one changeset and one release-note intent.

## 7. Definition Of Done

A task is not done until these are satisfied when applicable:

- Canonical docs are updated.
- Runtime changes are validated with syntax checks, tests, or smoke checks.
- One changeset exists for behavior changes.
- The final summary references the real files changed.

## 8. Release Workflow Entry Points

- Template: `release/changes/_template.md`
- Generator: `node scripts/release/generate-release-notes.mjs --version vX.Y.Z`
- Guard check: `node scripts/ci/check-release-changeset.mjs --base <ref> --head <ref>`

See [docs/release-note-workflow.md](docs/release-note-workflow.md) for the detailed process.
