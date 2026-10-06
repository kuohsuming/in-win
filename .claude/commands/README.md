# `.claude/commands/` — Project-Level Slash Commands

> **Audience:** Team members who just cloned the repo. This explains what auto-loads when you start a Claude Code session at the repo root.

## What's here

| File | Triggers | Function |
|---|---|---|
| `pm.md` | `/pm <subcommand>` | Dispatcher for PM Skill (AI Project Assistant). All 18+ subcommands routed to `skills/pm-skill/SKILL.md`. |
| `pm-bug-review.md` | `/pm-bug-review <slug>` | Walks through spectra-review findings + records PO decisions. |

## How it works after `git clone`

1. You clone the repo to `~/<wherever>/AzureLineBOT-main/`.
2. Start Claude Code in that directory: `cd AzureLineBOT-main && claude`.
3. Claude Code auto-detects `.claude/commands/*.md` and registers each as a slash command.
4. Type `/pm help` and PM Skill loads + responds with the command list.

**No extra installation required.** The whole PM Skill design (proposal + manual + SKILL.md + slash commands) syncs via git.

## What does NOT sync via git

- Your personal Claude memory (`~/.claude/projects/.../memory/MEMORY.md`) — that's local to each Claude install.
- IDE-specific config (VSCode settings etc.) outside `.claude/`.

## Related docs

- `docs/pm/pm-skill/docs/pm-skill-proposal-highlights.md` — 5-minute brief (start here if new)
- `docs/pm/pm-skill/docs/pm-skill-user-manual.md` — 18 usage scenarios
- `skills/pm-skill/SKILL.md` v1.0.1 — actual implementation logic

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `/pm help` → "Unknown command: /pm" | You started Claude Code in a directory above `~/<...>/AzureLineBOT-main/` | `cd` into the repo root first |
| `/pm` works but says "SKILL.md not found" | You're running from `~/<...>/AzureLineBOT-main/` but SKILL.md was moved | Verify `skills/pm-skill/SKILL.md` still exists |
| Slash command list doesn't show `pm` | Claude Code session started before files existed | Restart Claude Code |
