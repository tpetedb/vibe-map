@AGENTS.md

# Claude Code specifics

- Skills for this camp live in `.agents/skills/`; `just setup` links them into `.claude/skills/` so you load them automatically.
- A subagent `scorekeeper` in `.claude/agents/` summarises `workspace/data/scores.csv` into the vault.
- A PostToolUse hook backs up `workspace/data/` to `backups/` after every edit (`.claude/settings.json`).
- Vault path for the Obsidian skill: `vault/`.
