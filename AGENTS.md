# in-win AI Bootstrap

This repository may be edited with multiple AI-enabled IDEs (Claude Code primary, VSCode + Codex, others).
All tools must follow the same repo-owned rules. Framework adapted from AzureLineBOT.

## Read Order

1. [docs/ai-principles.md](docs/ai-principles.md) — Mode Map V0-V7 + Immutable Rules A/B/C
2. [Downloads/表面平整檢查系統_需求規格書.md](Downloads/表面平整檢查系統_需求規格書.md) — current requirement spec
3. [docs/pm/5-spec-authoring-framework.md](docs/pm/5-spec-authoring-framework.md) — spec authoring standard
4. [skills/pm-skill/SKILL.md](skills/pm-skill/SKILL.md) if the tool supports local skills
5. [skills/spec-compliance-review/SKILL.md](skills/spec-compliance-review/SKILL.md) for spec-compliance work

## Common Rules

- Repo rules live in `docs/ai-principles.md`, not in IDE-specific settings.
- If the user specifies `V0` to `V7` mode, follow it per `docs/ai-principles.md` §3.
- If behavior changes, add one file under `docs/release/changes/`.
- Prefer one task per branch or `git worktree`.

## Files That Must Never Be Auto-Modified

`docs/ai-principles.md`, `docs/ddd-doc-maintenance.md`, `AGENTS.md`, `CLAUDE.md`, `.gitignore` — require explicit user instruction before modification.
