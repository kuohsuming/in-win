---
description: PM Skill — AI Project Assistant orchestrating 8-stage SDLC. Subcommands: help / init / use / list / status / start / advance-phase / signoff / gate-check / daily / dashboard / archive / restore / delete / onboard / offboard / new-requirement / contract-change propose / validate-* / pm-bug-review.
---

User typed `/pm $ARGUMENTS`.

## Your task

Load the PM Skill and dispatch to the appropriate subcommand workflow:

1. **Read** `skills/pm-skill/SKILL.md` for the full Subcommand Router + workflows.
2. **Parse** `$ARGUMENTS` (raw string from user). First token = subcommand name. Remaining = subcommand args.
3. **Resolve** active project context per SKILL.md §Active Project Context Detection.
4. **Execute** the matching workflow from SKILL.md §Subcommand: <name>.
5. **Apply** Confidence Tier convention (🟢 high / 🟡 medium / 🔴 low) per SKILL.md §Auto Behavior Confidence Tier.
6. **Audit** all state mutations per SKILL.md §Audit Trail Convention.

## Argument parsing examples

| `$ARGUMENTS` | Subcommand | Args |
|---|---|---|
| `help` | help | — |
| `init "my-project" --type sandbox` | init | project="my-project", type=sandbox |
| `daily` | daily | — |
| `gate-check phase-0` | gate-check | phase=0 |
| `archive "old-project" --reason "done"` | archive | project="old-project", reason="done" |
| `contract-change propose` | contract-change propose | (nested subcommand) |
| `validate-req-spec docs/foo.md` | validate-req-spec | path=docs/foo.md |

## Edge cases

- **Empty `$ARGUMENTS`** → respond with `/pm help` workflow (show command list).
- **Unknown subcommand** → list valid subcommands + suggest closest match.
- **Subcommand exists in §v1.1 Planned section of SKILL.md** → respond with fallback per SKILL.md instructions (NOT IMPLEMENTED in v1.0, cite manual scene reference).

## Path conventions

When SKILL.md says "read `../../docs/...`" — that's relative to SKILL.md location. From your CWD (repo root, eg. `~/AzureLineBOT-main/`), resolve as `docs/...`.

When SKILL.md says "write to `docs/pm/<project>/...`" — that's a runtime operational path from repo root, so write directly to `docs/pm/<project>/...` (or `docs/pm/<project>/...` if user is operating in the namecard subdirectory — confirm with active-project.txt location).

## Audit trail confirmation

Before any state mutation (file write / move / delete), confirm intent with user IF the operation:
- Deletes any file (`/pm delete`, `/pm archive`)
- Mutates `_org/org-decision-log.md` (always append-only, but show the entry before append)
- Sets a new `active-project.txt` (show old → new value)

After mutation, output the file path that was written/changed for verifiability.
