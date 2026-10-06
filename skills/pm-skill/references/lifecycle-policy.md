# PM Skill — Project Lifecycle Policy

> **Loaded by:** `SKILL.md` for `/pm archive`, `/pm restore`, `/pm delete` subcommands.
> **Source of truth:** Aligned with user manual rev 1.8 Appendix A + FAQ Q4/Q9/Q10 and Round 6 Option B fix.

## Safety Matrix

| Operation | Production | Training | POC | Sandbox |
|---|---|---|---|---|
| `/pm archive <p>` | needs `--reason` | direct OK | needs `--reason` | direct OK |
| `/pm archive --filter X --confirm` | needs `--confirm` + match list shown | same | same | same |
| `/pm restore <p>` (within 7d) | always allowed | same | same | same |
| `/pm restore <p>` (> 7d, in `_cold`) | warn staleness, allow | same | same | same |
| `/pm delete <p> --force` | reject if any commit in `docs/pm/<p>/` last 7d | direct OK | warn but allow | direct OK |
| `/pm delete --filter X --force` | 2-step confirm | 2-step confirm | 2-step confirm | 2-step confirm |

**Special rule (production overlay):**

For `production`-type projects, even with `--force` and `--reason`, the operation is blocked if:

```bash
git log --since='7 days ago' -- "docs/pm/<project>/" | wc -l > 0
```

To proceed, user must add a clause to `--reason` explicitly acknowledging recent activity (eg. `"recent activity acknowledged - intentional reset"`). This is a tripwire against muscle-memory mistakes.

## Phase-aware Block

Projects in **Phase 4 or later** (active development / integration / release / post-launch) cannot be archived or deleted directly. They must first go through `§10.7 stop loss` decision flow:

1. PO writes stop loss reason to `docs/pm/<project>/decision-log.md` (`D-stop-loss-<seq>`).
2. Run `/pm advance-phase 8` (special "closed/aborted" phase marker, not a real phase).
3. Then archive/delete is unblocked.

Rationale: prevents accidental destruction of expensive Phase 4+ work.

## Bulk Operation Safety

`/pm archive --filter <pattern>` and `/pm delete --filter <pattern>` MUST:

1. First print the match list (one project per line) with phase / type / last activity.
2. Wait for explicit `yes` from user before any state mutation.
3. Audit each individual project in `_org/org-decision-log.md` (not a single bulk entry — per-project granularity).
4. If any single project fails its individual safety check, abort the entire batch (no partial application).

## Audit Trail Format

Append to `docs/pm/_org/org-decision-log.md`:

```
D-archive-<seq>: project=<p> reason="..." by=PO at=<ISO8601>
D-restore-<seq>: project=<p> from_grace=true|false days_archived=<N> by=PO at=<ISO8601>
D-delete-<seq>: project=<p> reason="..." force=true type=<production|training|poc|sandbox> by=PO at=<ISO8601> commits_last_7d=<N>
```

Audit entries are append-only and survive deletion of the project's own files. This is the "delete-but-not-forget" property — you can prove the project existed and why it was removed.

## 7-day Grace Period (Restore window)

When `/pm archive` runs:

1. Files move to `docs/pm/_archive/<project>/`.
2. Write `docs/pm/_archive/<project>/_archived-at.txt` with ISO8601 timestamp.
3. For the next 7 days, `/pm restore <project>` moves them back to `docs/pm/<project>/`.
4. After 7 days, an auto-mover (or `/pm dashboard` recommendation) shifts them to `docs/pm/_archive/_cold/<project>/`.

Files in `_cold/` are still restorable but `/pm restore` warns about staleness ("Archived 23 days ago. Recover anyway? y/n").

## Auto-expiry for non-production

For projects with `project_type` in `{training, sandbox}`:

- After 30 days since last commit/state mutation, `/pm dashboard` flags as "expires soon".
- After 60 days, recommend `/pm archive` (auto-suggest).
- Eventually, an auto-archive daemon may move them; for now, manual.

For `poc`:

- After 90 days similar flow.

For `production`:

- No auto-expiry. Production projects are kept indefinitely unless explicitly deleted.

## Recovery Paths (when things go wrong)

| Scenario | Recovery |
|---|---|
| `/pm archive` wrong project, < 7d | `/pm restore <p>` |
| `/pm archive` wrong project, > 7d | `/pm restore <p>` from `_cold/` (allowed with warning) |
| `/pm delete` wrong project, files gone | `git checkout <last-good-sha> -- docs/pm/<project>/` (relies on git) |
| `/pm delete` wrong project, no git | `_org/org-decision-log.md` D-delete entry still exists; rebuild from audit trail (degraded) |

The `_org/org-decision-log.md` is the **last line of defense** — it's append-only and never deleted by any `/pm` operation.

## Why this matters

The training-project use case (5 engineers × N sandboxes per workshop) creates legitimate volume that requires bulk operations. But bulk operations are exactly where catastrophic mistakes happen ("oh I meant to delete training-*, not production-*").

The safety overlay:

1. `--type` at init = source of truth for what is "safe to delete easily".
2. `--force` + `--reason` = explicit intent.
3. 7-day quiet check = protects against muscle memory.
4. Phase-aware block = protects expensive Phase 4+ work.
5. Bulk confirmation = protects against typo in pattern.
6. Audit-before-delete = post-mortem capability.

No single defense is enough. The combination provides defense-in-depth.
