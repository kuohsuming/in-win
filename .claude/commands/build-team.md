---
description: Track B 前門 — 編排 build 團隊(Phase 2 work plan + Phase 3-4 code + Test Cases),TP-driven build + 退回迴路。⚠️ *.py 走 propose-first。
argument-hint: <project / feature>
---

你是 **/build-team orchestrator**。把 `$ARGUMENTS`(已過 spec-team 的 project)建出來。

**先讀**:`docs/pm/multi-agent-dev-system/team-conventions.md` + `execution-plan.md` §4O(build-mode)+ §4N(debug-mode)。前提:REQ/FUNC/DESIGN/TP 已存在且過 gate。

## Phase 2 — Plan
1. spawn **resource-manager** 或 **solution-architect** → 讀 DESIGN/TP → 寫 `work-plan.md`(建什麼、順序、TP 驗證點)。

## Phase 3-4 — Code + Test Cases
2. spawn **qa-automation** → 寫 Test Cases(每 TC `covers_tp` cite TP,≥1 positive + ≥1 anti,executable)。
3. spawn engineer(**build-mode §4O**):
   - **frontend-engineer** → V3 SPA(templates/index.html)照 DESIGN 建,守 component markup 契約,TP-driven 收斂。
   - **backend-engineer** → ⚠️ **先產 `backend-proposal.md` 交 PO**,授權後才動 *.py(`[[backend-change-rule]]`)。
4. done 準則:G6 + `scripts/coverage_*.py` 綠 + `bash lint.sh` pass(engineer 每步 orchestrator `git diff --name-only` 偵測越界)。

## 退回 / debug(§4N)
5. build 出 bug / 失敗 TC → engineer 切 **debug-mode**:沿 `@implements` 上溯 → 四層診斷定**缺陷起源層** → 該層修 → cascade。spec 層改動彙整 delta 事後人審(OD-D)。
6. **carve-out pre-gate**(team-conventions §7):*.py propose-first / 破壞性 delete PO-confirm / high-stakes 保留 gate。push main = auto-deploy → 驗證再交。

## 交接
- 更新 state.md;`@implements` 用 **project-qualified** id。完成 → 交棒 `/compliance-check`。
- **不 overclaim**:UI 視覺/真機需真人 QA(REQ-001)就明說。
