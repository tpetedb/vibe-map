@AGENTS.md

# Claude Code specifics

- Skills for this project live in `.agents/skills/` (Agent Skills standard). `just setup` links them into `.claude/skills/` so you load them automatically. `develop-camp` is the loop for any change to this product; `install-camp` is for setting a machine up.
- A subagent `scorekeeper` exists in `.claude/agents/`. Use it for anything that summarises `workspace/data/scores.csv` into the vault.
- Work orders (`work/`, skill `work-order`): Claude Code subagents `builder`, `reviewer` and `team-manager` exist in `.claude/agents/` and all run on Fable; mixing in Opus cost more overall than Fable alone. A PreToolUse hook refuses an edit outside the order on the current branch; a SubagentStop hook sends a subagent that edited under an order back once if `just work-check <id>` fails, and a Stop hook does the same for a session whose report starts with `order: <id>`. They are reminders; `work-check`, `work-accept` and CI decide. At most four build at once.
- A PostToolUse hook backs up `data/` to `backups/` after every edit (`.claude/settings.json`).
- Vault path for the Obsidian skill: `vault/`.
- Before a commit: `just verify`. Before touching the game: the file map in `AGENTS.md` and the conventions in `docs/AOE-STUDY.md`.
- Other sessions may be active in this repo (`git worktree list`). Work in a worktree and never pop a shared stash.
