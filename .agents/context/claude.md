# Claude Code specifics

- The harness: `config.toml` at the root is the one file a person edits. `.claude/settings.json`, `.claude/agents/`, `.codex/` and this file are rendered from `.agents/` by `uv run python .agents/utils/harness.py sync`; `python3 .agents/utils/harness.py check` finds drift, `explain` says where each value comes from. Edit the source, never an output (`.agents/README.md`).
- Skills for this project live in `.agents/skills/` (Agent Skills standard). `harness.py sync` and `harness.py doctor` link each one into `.claude/skills/` with a relative link (a copy where links cannot be made), so you load them automatically. `develop-camp` is the loop for any change to this product; `install-camp` is for setting a machine up.
- A subagent `scorekeeper` exists in `.claude/agents/`. Use it for anything that summarises `workspace/data/scores.csv` into the vault.
- Work orders (`work/`, skill `work-order`): Claude Code subagents `builder`, `reviewer` and `team-manager` exist in `.claude/agents/`, each on the model and effort its role gets in `.agents/conf/models/`. A PreToolUse hook refuses an edit outside the order on the current branch; a SubagentStop hook sends a subagent that edited under an order back once if `just work-check <id>` fails, and a Stop hook does the same for a session whose report starts with `order: <id>`. They are reminders; `work-check`, `work-accept` and CI decide. At most four build at once.
- A PostToolUse hook backs up `data/` to `backups/` after every edit (`.claude/settings.json`).
- Vault path for the Obsidian skill: `vault/`.
- Before a commit: `just verify`. Before touching the game: the file map in `AGENTS.md` and the conventions in `docs/AOE-STUDY.md`.
- Other sessions may be active in this repo (`git worktree list`). Work in a worktree and never pop a shared stash.
