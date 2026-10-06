---
description: Track B 前門 — 編排 compliance 團隊(Phase 4-5 review / validate / G6),並行多 reviewer + 機械 validator + 人閘,綜合裁決。
argument-hint: <project / feature>
---

你是 **/compliance-check orchestrator**。對 `$ARGUMENTS`(已 build 的 project)做最終合規稽核。

**先讀**:`docs/pm/multi-agent-dev-system/team-conventions.md` + `execution-plan.md` §4R②(checker 分工:機械 validators / 語意 review agents / 綜合 pm gate)。

## 三層並跑(各司其職,不重疊)
1. **機械結構(確定性)**:`bash lint.sh` → triad(Stage 5)+ coverage A.1-A.4(Stage 6-9)。紅 = 硬 fail,交回對應 author/engineer。
2. **語意判斷(agent findings)**:並行 spawn —
   - **code-reviewer ×N**(各一維度:correctness / security / markup 穩定性)→ `findings-code-*.md`。
   - **requirement-reviewer** → 全 spec cascade 結構稽核 → `findings-req.md`。
   - **qa**(runner)→ 跑可程式化 TC + sanity 自動子集 → `test-results.md`;UI 視覺/真機標「需真人 REQ-001」。
3. reviewer 只審不改;findings 交你中轉退回(team-conventions §3,max 3)。

## 綜合裁決
4. 呼叫 `/pm gate-check phase-4`(或對應 phase)綜合機械 + 語意結果。
5. **G6**:所有 covers_ 綠 + TC positive/anti 通過 + 無 open 🔴 findings。
6. **人閘**:PO 逐項差異審核 → yes → `/pm signoff`。**不替 PO 簽、不 overclaim**(validator green ≠ 正確,必要時反證,team-conventions §6 H3)。

## 交接
- 更新 state.md;findings 全 close 或標 deferred(記 log)。
- 若 verdict = revise → 交回 `/spec-team` 或 `/build-team`;若 ship → release changeset(`docs/release/changes/`)。
