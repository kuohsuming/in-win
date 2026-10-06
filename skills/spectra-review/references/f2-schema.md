# Spectra-Review v2.0 — F2 Aggregate Summary Schema

> **Loaded by:** SKILL.md §F2 Aggregate Summary. Authoritative source: `docs/pm/pm-skill/spec/pm-skill-proposal.md` §6.4.3.C.

## File Path Convention

- **PM Skill mode:** `docs/reviews/<active-project>/_summary-<target-slug>.md`
- **OpenSpec mode:** F2 not required (legacy F1-only workflow)

## Section 0: Frontmatter

```yaml
---
target: <full path of target file>
target_slug: <slug used in filename>
total_rounds: <N>
last_round_date: <YYYY-MM-DD>
last_verdict: ship-as-is | fix-blockers | revise-design
schema_version: enhanced-v1
contract_version: spectra-contract-v1
---
```

## Section 1: Cumulative Findings Tally (append-only)

```markdown
## Cumulative Findings Tally

| Round | Date | BLOCKER | CONCERN | NIT | STRENGTH | Verdict |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | YYYY-MM-DD | X | X | X | X | <verdict> |
| 2 | YYYY-MM-DD | X | X | X | X | <verdict> |
| **Total** | | **X** | **X** | **X** | — | — |
```

**Invariants:**
- Previous round rows are IMMUTABLE (INV-1)
- "Total" row computes BLOCKER + CONCERN + NIT cumulative across ALL rounds (STRENGTH excluded — strengths preserved per round, not cumulative)

## Section 2: Issue Status Matrix

Per-finding row, accumulating across rounds.

```markdown
## Issue Status Matrix

| Round | ID | Tier | Title | severity_score | fix_roi | Status | PO 決策 |
|:---:|:---:|:---:|:---|:---:|:---:|:---:|:---|
| 1 | B1 | 🔴 | ... | <X> | <X> | ⏸ no_decision | — |
| 1 | C1 | 🟡 | ... | <X> | <X> | ✅ fixed | accept(Round 1) |
| 2 | B2 | 🔴 | ... | <X> | <X> | ⏸ no_decision | — |
```

**Status enum:**

| Status | Meaning |
|---|---|
| `✅ fixed` | PO accepted + fix landed |
| `⏳ pending` | PO accepted but fix not yet implemented |
| `⏸ no_decision` | PO has not yet adjudicated |
| `❌ rejected` | PO explicitly rejected the finding |
| `🔁 deferred` | PO deferred to later phase |
| `✅ valued` | STRENGTH preserved (accept) |

**Invariants (INV-2):**
- Every finding from F1 logs MUST appear here
- "no_decision" findings MUST be explicitly listed (not omitted)
- Override audit trail visible via PO 決策 column

## Section 3: Quality Health Score

```markdown
## Quality Health Score

- total_findings: <N>
- fixed: <N>
- pending: <N>
- no_decision: <N>          ⭐ PM Skill /pm gate-check 重點
- rejected: <N>
- deferred: <N>
- valued: <N>(STRENGTH)
- **fix_rate**: <%>          = fixed / (total - strengths)
- **close_rate**: <%>        = (fixed + rejected + deferred + valued) / total
- avg_severity_open: <X.X>
- po_overrides: <N>         ⭐ 透明度 metric
- convergence_signal: ✅ | ⚠ | ❌
```

**Convergence signal rule:** ✅ if last 2 rounds 0 new BLOCKER + 0 new CONCERN. ⚠ if only 1 round meets. ❌ otherwise.

## Section 4: Hotspot History

```markdown
## Hotspot History

| Round | Hotspot | 等級 | 是否解 |
|:---:|:---|:---:|:---:|
| 1 | <finding name + early/late ratio> | 🔥🔥🔥 | ⏸ pending | ✅(fix detail) |
```

## Section 5 (optional): Override Audit Trail

```markdown
## Override Audit Trail(對齊 §6.4.4 / §6.4.6)

| Round | Finding | Field | Default | Override | By | At | Reason |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| 2 | B1 | severity.score | 8.0 | 5.5 | PO | 2026-06-17 | "..." |
```

## Section 6 (optional): Cross-Round Drift Detection

```markdown
## Cross-Round Drift Detection(對齊 §6.4.7)

If override_rate(per-finding default → value)> 50% in a round → flag:
"⚠ spectra-review baseline 可能偏離,建議下次 Phase Gate 重 calibrate"
```

## Section 7: PM Skill Reader Interface

```markdown
## PM Skill Reader Interface(對齊 §6.4.3)

- 讀 frontmatter `total_rounds=<N>` / `last_verdict=<V>`
- 讀 Quality Health Score → `no_decision=<N>` 觸發 gate-check warning if > 0
- 讀 Issue Status Matrix → fix recommendation sort:
  - Primary: severity_decay[current_phase].value DESC
  - Secondary: fix_economics.roi.value DESC
  - Tertiary: dependencies.blocks.length DESC
- Gate-check verdict logic per §6.4.10.B.2
```

## Append Order per Round

When Round N completes:

1. Update frontmatter `total_rounds=N` / `last_round_date` / `last_verdict`
2. Append Section 1 row for Round N
3. Append Section 2 rows for new findings; update existing rows for `Status` changes
4. Recalculate Section 3 (Quality Health Score) entirely
5. Append Section 4 row(s) if any new Hotspots
6. Append Section 5 row(s) if Round N has overrides
7. Recalculate Section 6 drift detection

NEVER:
- Delete previous round rows
- Modify previous round numbers / dates / verdicts
- Skip Status enumeration (must list ALL findings including no_decision)
