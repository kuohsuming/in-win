# Track B Team Conventions（11 agents + 3 commands 共用契約）

> 所有 `.claude/agents/*.md`（Track B 執行者）+ `.claude/commands/*.md`（編排入口）共同遵守。
> 薄 agent 檔只寫「角色行為 + 讀哪份 rules + 輸出契約」,通用規約一律指回本檔（DRY）。
> SSOT：`execution-plan.md` §4J（agent schema/退回迴路）+ §4K（編排/交接/狀態)。

## 1. 檔案交接 header（每個 agent 產出檔頂端必附;延伸既有 `@governed-by`,不新造)

```
<!--
@produced-by: <本 agent name>
@covers: <REQ-xxx / FUNC-xxx / ...（feature: 一句)>
@next: <下一手 agent name>
@governed-by: <本階段依循的 Track A rulebook 路徑>
-->
```
下一手 agent 一讀就知「誰產的 / 對應啥 / 我該接 / 依哪份 rules」。subagent 不共享 context → **全靠檔案 + orchestrator 中轉**（§4J 原則六,不靠記憶）。

## 2. Findings 檔 schema（reviewer/runner 產出）

每筆:`{id, severity, location, issue, suggested_fix}`。severity = 🔴 BLOCKER / 🟡 CONCERN / 🟢 NIT（對齊 spectra 校準）。

## 3. 退回迴路（author ↔ reviewer,orchestrator 中轉)

```
author → artifact 檔 → reviewer → findings 檔 → orchestrator:
  ├─ findings 有 → re-spawn author(全新 instance,帶 {artifact, findings} 從檔重建)→ 修 → re-spawn reviewer 複查 → 回頭
  └─ findings 0 → 過,進下一階段
```
- **max-rounds = 3**:觸頂不收斂 → escalate 人（防無限迴圈)。
- 收斂追蹤:findings ID → author 回報哪些修 → orchestrator 對照。
- **持久化分工(2026-07-05 pilot finding #1/#2 釐清)**:純 reviewer(requirement-reviewer/code-reviewer)= Read-only,**回傳 findings 文字 → orchestrator 落地** findings 檔(確保物理碰不到被審 artifact);advisory-author(tech-architect)+ 一般 author = 自寫產物檔(Write)。

## 4. 狀態/進度（重用 `docs/pm/state.md`,擴 agent 層,不新造)

```yaml
current_phase: 0
agents: {needs-advocate: done, tech-architect: done, resource-manager: in-progress}
retback_rounds: 1
findings_open: 2
```
standing interrupt 隨時可讀此檔 inspect;PO 隨時可搶方向盤（原則六)。

## 5. ID 慣例 —— Project-qualified identity（§3.4.1,硬規則)

- REQ-id 僅 **project 內唯一**（afv/backend/sanity 皆有 REQ-001）。REQ 真身 = `(project, REQ-id)`。
- **spec 內引用** bare（`REQ-001-G1`);**跨邊界**（code `@implements`、agent 之間傳 id）用 **qualified** `<project>:REQ-001-G1`。
- claim-ID `REQ-<id>-G1/A<k>`、vkp-ID `TP-<id>.vkp-<n>`:stable / monotonic / never-reuse / never-reindex。

## 6. 寫 validator/checker 必守 6 條硬約束（§9 H1-H6)

引 `proposals/coverage-validators-proposal.md §9`:**H1 identity 必帶 project(禁全域 bare-id map)** · H2 selftest 含 cross-project case · H3 落地後反證(green≠正確) · H4 scope=真 canonical id def · H5 stdlib-only + WARN→BLOCKING · H6 cite-parent 需 parent 存在。

## 7. Carve-out pre-gate（任一 agent 動手前先攔,3 條硬規則)

1. **`*.py` 改動 = propose-first**：任何後端 Python 改動必先提案 + 等 PO 授權（`[[backend-change-rule]]`）。engineer agent **不得**自行改 *.py,先產「提案檔」交人。
2. **任一層破壞性 delete = PO-confirm 一律必做**（`[[delete-dialog-no-undo-hint]]`;預設 Deprecate 優先於硬刪;REQ-ID 永不重用)。
3. **high-stakes claim 傳播**（risk_class ≠ normal）保留較強 gate,不 auto 過。

## 8. 只審不改 enforcement

- **純 reviewer（requirement-reviewer / code-reviewer)= tools 只 Read/Grep/Glob**（物理改不了;它們審**別人的** artifact,不得修改)。
- **advisory-author（tech-architect)= Read/Grep/Glob + Write**:它產出**自己的**評估 artifact(tech-assessment.md)故需 Write;「只審不改」對它的意義 = **不改 REQ/spec/code**(無 Edit/Bash),soft 補同下(orchestrator `git diff` 偵測越界)。〔2026-07-05 pilot finding #1:原把 tech-architect 歸純 reviewer→無法寫自己產物,已修〕
- **author / test-author / engineer（needs-advocate / resource-manager / solution-architect / ux-ui-designer / qa-automation / engineer)= 需 Write/Edit（本該可寫)**→ 軟補:system prompt 硬性「禁碰不該碰的檔」+ orchestrator 每步 `git diff --name-only` 偵測越界 → flag 退回。
- **runner（qa)= +Bash**：只跑不改,同軟補。

## 9. 成本分層（per-agent model tiering,§4M)

reviewer / runner 便宜（haiku/sonnet）· judgment（resource-manager / solution-architect / tech-architect)= opus · engineer / test-author = sonnet。各 agent 檔 frontmatter `model:` 明訂。

## 10. Protected files（絕不自動改)

`docs/action-inventory.md` · `copy-inventory.md` · `ai-principles.md` · `dependency-map.md` · `ddd-doc-maintenance.md` · `CLAUDE.md` / `AGENTS.md` / `GEMINI.md` · `.gitignore` —— 需 PO 明示才動（見 CLAUDE.md）。
