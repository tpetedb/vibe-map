@AGENTS.md

# Claude Code specifics

- Skills for this project live in `.agents/skills/` (Agent Skills standard). `just setup` links them into `.claude/skills/` so you load them automatically. `develop-camp` is the loop for any change to this product; `install-camp` is for setting a machine up.
- A subagent `scorekeeper` exists in `.claude/agents/`. Use it for anything that summarises `data/scores.csv` into the vault.
- A PostToolUse hook backs up `data/` to `backups/` after every edit (`.claude/settings.json`).
- Vault path for the Obsidian skill: `vault/`.
- Before a commit: `just verify`. Before touching the game: the file map in `AGENTS.md` and the conventions in `docs/AOE-STUDY.md`.
- Other sessions may be active in this repo (`git worktree list`). Work in a worktree and never pop a shared stash.
