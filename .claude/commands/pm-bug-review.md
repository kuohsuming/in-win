---
description: PM Skill — Bug Review console for PO to adjudicate spectra-review findings. Walk through findings + accept/override/defer/reject decisions with audit trail.
---

User typed `/pm-bug-review $ARGUMENTS`.

## Your task

Load the PM Skill and execute the bug-review workflow:

1. **Read** `skills/pm-skill/SKILL.md` §Subcommand: pm-bug-review for the full workflow.
2. **Parse** `$ARGUMENTS`:
   - First token: target slug (eg. `subscription-business-proposal`)
   - Optional flags: `--finding <id>` / `--pending-only` / `--overrides-only`
3. **Locate** F2 summary file: `docs/reviews/<active-project>/_summary-<target-slug>.md` per §6.4.3.C contract.
4. **Walk** through findings per filter, prompting PO for decisions (`[a]` accept / `[b]` override / etc.) per SKILL.md workflow.
5. **Apply** PO decisions per §6.4.4 Default vs Override architecture:
   - On override: validate non-empty reason, write override 三件套 (by/at/reason).
   - Auto-recalc `roi.value` from new severity / difficulty.
6. **Update** F2 summary file + append to `docs/pm/<active-project>/decision-log.md`.
7. **Output** new fix recommendation order per §6.4.8 algorithm.

## Argument parsing examples

| `$ARGUMENTS` | target_slug | filter |
|---|---|---|
| `subscription-business-proposal` | subscription-business-proposal | (all) |
| `req-spec --pending-only` | req-spec | pending |
| `req-spec --finding B1` | req-spec | finding B1 |
| `req-spec --overrides-only` | req-spec | existing overrides |

## Edge cases

- **Empty `$ARGUMENTS`** → list all `docs/reviews/<active-project>/_summary-*.md` for user to pick.
- **No matching summary file** → output: "No _summary file at <expected path>. Run spectra-review first."
- **No findings matching filter** → output: "No findings match filter. Run without filter to see all."

## Audit trail

Every PO decision in this workflow MUST:

1. Append to `docs/pm/<active-project>/decision-log.md`:
   ```
   D-pm-bug-review-<round>.<seq>: <target_slug>.<finding_id> <field> <old> → <new> | reason: ... | by: PO at: <ISO8601>
   ```
2. Update F2 summary `Quality Health Score.po_overrides` count.
3. Update F2 Issue Status Matrix row for that finding.
