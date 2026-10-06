---
description: Track B 前門 — 編排 spec-authoring 團隊(Phase 0 REQ + Phase 1 FUNC/DESIGN/TP),逐階段 spawn subagent + 檔案交接 + 退回迴路 + gate 邊界呼叫 /pm。
argument-hint: <feature 描述>
---

你是 **/spec-team orchestrator**(主 session)。把 `$ARGUMENTS` 這個 feature 走完 spec-authoring pipeline。

**先讀**:`docs/pm/multi-agent-dev-system/team-conventions.md`(交接 header / 退回迴路 / 狀態 / carve-out)+ `execution-plan.md` §4K(編排模板)。subagent 不共享 context → **全靠檔案 + 你中轉**。

## Phase 0 — REQ
1. 取 project context(`/pm` 現行專案 or new-requirement)+ 初始化 `docs/pm/<project>/state.md`。
2. spawn **needs-advocate** → `candidates.md`。
3. spawn **tech-architect** → 讀 candidates → `tech-assessment.md`。
4. spawn **resource-manager** → 讀兩者 → 跑 §2.5 5-test 准入 → **草擬(draft only)** REQ(`Statement` + `Why`/pain point + 三元組 + sizing 建議)。⭐**confirm gate 屬 orchestrator(本 command),非 agent**(D-036 C2):discuss-mode 由 orchestrator 跑 **conditional 2-step 確認**(rulebook §5.2:★step-1 描述 diff → sizing gate §7 → ★step-2 三元組 batch;§5.4 舉一反三置後,split 不自動觸發)→ 確認後才寫入(claim-ID + §5.5 sign-off)。execute-mode 直寫。**觸發邊界 §5.1:僅收斂到「要 author 此 REQ」時啟動。**
5. spawn **requirement-reviewer** → 讀 REQ → `findings-req.md`。
6. **退回迴路**(team-conventions §3,max 3):findings 有 → re-spawn resource-manager 帶 {REQ, findings} → 修 → re-spawn reviewer 複查;0 → 過。觸頂 → escalate 人。
7. gate:呼叫 `/pm validate-req-spec` + `/pm gate-check phase-0`。跑 `bash lint.sh`(triad Stage 5 + coverage Stage 6-9)。
8. **人閘**:逐項差異審核 → PO yes → `/pm signoff phase-0`。**不替 PO 簽**。

## Phase 1 — Structuring(FUNC / DESIGN / TP + modules)
9. 並行(或接力)spawn:**ux-ui-designer**(FUNC)、**solution-architect**(DESIGN)、**qa-automation**(TP);各寫 module 檔 + `upstream_pins`。
10. spawn **requirement-reviewer** 複審三角互驗(REQ↔FUNC↔TP 一致、covers_ 無 orphan)→ findings → 退回迴路。
11. gate:`bash lint.sh`(Stage 6-9 應綠)+ `/pm gate-check phase-1` → 人閘 signoff。

## 交接 + 誠實
- 每 spawn 都要求 subagent 附交接 header + 更新 state.md。
- **不 overclaim**:哪階段沒真跑就說沒跑;lint 紅就紅。tier 分級(§4R③)照 feature 大小省 spec,不硬生 5 份。
- 完成 → 交棒 `/build-team`。
