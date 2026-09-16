@AGENTS.md

# Claude Code specifics

- Skills for this project live in `.agents/skills/` (Agent Skills standard). `scripts/setup.sh` links them into `.claude/skills/` so you load them automatically.
- A subagent `scorekeeper` exists in `.claude/agents/`. Use it for anything that summarises `data/scores.csv` into the vault.
- A PostToolUse hook backs up `data/` to `backups/` after every edit (`.claude/settings.json`).
- Vault path for the Obsidian skill: `vault/`.
