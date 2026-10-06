---
description: Spectra-Review v2.0 — Adversarial design review skill. Dual-mode: OpenSpec proposals (legacy) + PM Skill artifacts (req-spec / module-plan / module-spec / etc.). Produces 4-tier findings (BLOCKERS / CONCERNS / NITS / STRENGTHS) with 7-field schema, F1 per-round log + F2 aggregate summary, Minerva 4-ability framework, Confidence Tier explicit.
---

User typed `/spectra-review $ARGUMENTS`.

## Your task

Load the Spectra-Review skill and dispatch:

1. **Read** `skills/spectra-review/SKILL.md` for the full workflow + dual-mode detection.
2. **Parse** `$ARGUMENTS`:
   - First token: target path (eg. `docs/foo.md`) or OpenSpec change name (eg. `2026-05-20-vehicle-plate-field`)
   - Optional flag: `--lite` → invoke Lite Mode (legacy 100-line simple output)
   - Optional flag: `--mode <X>` → explicit mode override (eg. `--mode pm-skill-req-spec`)
3. **Detect mode** per SKILL.md §Mode Detection table:
   - `openspec/changes/<name>/` → OpenSpec(legacy)
   - `docs/2026-*-requirement.md` → PM Skill Requirement Spec
   - `docs/modules/<project>/_plan.md` → PM Skill Module Plan
   - `docs/modules/<project>/<module>/...` → PM Skill Module Spec
   - `docs/2026-*-pm-skill-*.md` or `skills/*/SKILL.md` → PM Skill Meta(self-review)
   - Other markdown → PM Skill Generic doc
   - No clear match → list modes + ask user
4. **Resolve active project** for path conventions:
   - Read `docs/pm/active-project.txt` if PM Skill mode
   - Or detect from target path
5. **Execute** review per SKILL.md §What to Check + §Finding Schema + §Output Format
6. **Apply** Confidence Tier per finding output (🟢 / 🟡 / 🔴)
7. **Audit** all state mutations per SKILL.md §PM Skill Integration

## Argument parsing examples

| `$ARGUMENTS` | Target | Mode | Flag |
|---|---|---|---|
| `docs/pm/pm-skill/spec/pm-skill-proposal.md` | full path | pm-skill-meta | — |
| `docs/foo-requirement.md --lite` | path | pm-skill-req-spec | lite |
| `2026-05-20-vehicle-plate-field` | OpenSpec change name | openspec | — |
| `docs/modules/subscription/_plan.md` | full path | pm-skill-module-plan | — |
| `<empty>` | none | ask user | — |

## Output side-effects

### enhanced mode (default)

Writes 2 files MUST:
1. **F1 per-round log:** `docs/reviews/<active-project>/<date>-spectra-<target-slug>-round-<N>.md`(append-only)
2. **F2 aggregate summary:** `docs/reviews/<active-project>/_summary-<target-slug>.md`(round 1 creates,subsequent rounds append rows)
3. **Audit entry:** `docs/pm/<active-project>/decision-log.md`(append)

### lite mode

Inline output only(no file persistence).

## Edge cases

- **Empty `$ARGUMENTS`** → ask user which target(list OpenSpec changes + recently-modified docs)
- **Target file not found** → abort with clear path expectation + suggest closest match
- **No active project context for PM Skill mode** → ask user `/pm use <project>` first or pass `--project <X>`
- **Round number conflict** (re-run same round) → confirm overwrite intent before mutating F1/F2

## Confidence Tier

Apply per SKILL.md §Confidence Tier table:

- Finding evidence citation: 🟢 high
- Naming / counting checks: 🟢 high
- Severity score estimate: 🟡 medium(LLM + Calibration Baseline)
- Cross-impact analysis: 🟡 medium
- Anti-Bias self-judgment: 🟡 medium
- Inferring design intent: 🔴 low(always cite evidence)

If a finding's confidence is 🔴 low → DO NOT conclude;list raw data only.

## Audit trail

Every spectra-review run appends to `docs/pm/<active-project>/decision-log.md`:

```
D-spectra-<round>.<finding_id>: <target_slug> tier=<T> severity_default=<X> | by: SKILL at: <ISO8601>
```

For meta-review (eg. on SKILL.md or proposal §6.4): use the `pm-skill-itself` project context if no active project (creates `docs/pm/_org/decision-log.md` entry).

## Composes with `/pm-bug-review`

After spectra-review produces F2 with `no_decision` findings:
- User runs `/pm-bug-review <target-slug>` (separate slash command)
- That command reads F2,walks PO through each finding,records Default vs Override decisions
- Updates F2 Quality Health Score + appends decision-log
