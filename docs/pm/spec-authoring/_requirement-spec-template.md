---
title: "[Topic] Requirement Spec"
owner: "[bounded context / team]"
status: Draft   # Draft | Active | Deprecated
spec_version: YYYY-MM-DD.1
last_updated: YYYY-MM-DD
spec_dirty: false
authors:
  - "[PM]"
reviewers:
  - "[Dev — feasibility]"
  - "[QA — testability]"
memory_rules_cited: []
---

# [Topic] Requirement Spec

> Authoring 規則見 `docs/pm/spec-authoring/requirement-spec-authoring-rules.md`(逐條 checklist + 三元組不變式)。
> 通用完整性標準見 `ddd-doc-maintenance.md §7`(M1–M5)。

## 1. Purpose

（一句話:這份 spec 管什麼 / 為什麼要做）

## 2. Problem Statement

- Who suffers + from what pain + evidence

## 3. Success Metric

- 業務指標(不是實作指標),可量測

## 4. Scope

### ✅ In-scope
-

### ⛔ Non-goals（防 scope creep）
-

## 5. Requirements（三元組:每條 REQ = REQ + Golden Scenario + Anti-example）

> 規則:1 REQ = 1 golden scenario(1:1);≥1 anti-example(1:N)。缺項需二次確認 + `[GAP]`。

### REQ-001 — [testable「user can X」句型]

- **Priority:** P0 | P1 | P2
- **Why（pain point）:** [這條需求解什麼痛點 / 價值;餵 §2.5 准入 necessity。D-036:discuss-mode 新 REQ 必確認,execute-mode / 既有 spec optional（缺=`[GAP]`）]
- **AC（可量測）:** [metric / threshold / 可觀察結果，禁 vague]

**Golden Scenario（情境 / happy path）:**
> Given [前置] → When [動作] → Then [可觀察結果]

**Anti-example（邊界 — 什麼不算滿足）:**
- ❌ [邊界 1]
- ❌ [邊界 2]

<!-- 涉資料 → 補 Data Contract(D1/D2);涉狀態 → 補 State list + trigger(S1/S2) -->

---

### REQ-002 — ...

（同上結構）

---

## 6. Constraints

- Regulatory / timeline / budget / 適用的 memory rules

## 7. Impacted Stakeholders

-

## 8. Open Questions

- [OPEN] ...（若無,寫「無」）

## 9. Revision History

| Rev | Date | Author | Change |
|---|---|---|---|
| YYYY-MM-DD.1 | YYYY-MM-DD | [author] | Baseline |
