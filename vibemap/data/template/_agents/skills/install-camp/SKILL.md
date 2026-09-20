---
name: install-camp
description: Installs, sets up and runs Vibe Code Camp on this Mac, with the user choosing every dependency. Use for "set up vibe", "install the course", "get me ready for the evening", "is my machine ready", "what do I need installed", "start the evening", or to run the game, the CLI or the vault.
---
# Install and use Vibe Code Camp

Nothing is installed without the user choosing it. Present the menu first, then act only on the chosen items. `vibe start` (or `just start`) is the interactive version of this menu; offer it once the `vibe` command is there.

Work out where you are before you advise, because the two places need different things:

- **A camp** (this folder has `config/camp.toml` and `workspace/`, and no `pyproject.toml`). The engine is not here: it reaches the learner through the installed `vibe` command and the hosted game. Commands are plain `vibe <thing>`, and every `just` recipe is one line that calls it.
- **A product checkout** (it has `src/`, `vibemap/`, `tools/`, `tests/` and a `pyproject.toml`). There the commands are `uv run vibe <thing>`, `just setup` runs `scripts/setup.sh`, and the course documents live in `docs/`.

## Menu (ask, then do)

Show this list and ask which to install (all, some, none):

1. Homebrew (needed for the rest on macOS): https://brew.sh
2. uv, the Python installer the `vibe` command rides on: `brew install uv`
3. The `vibe` command itself: `uv tool install git+https://github.com/tpetedb/vibe-map`, then `vibe --version`
4. just, the task runner behind `just start` and `just check`: `brew install just`
5. GitHub CLI `gh` (workstream 7, and `vibe new --github`): `brew install gh`
6. DuckDB CLI (workstream 3): `brew install duckdb`
7. Obsidian app (workstream 6): `brew install --cask obsidian`
8. A coding agent, on the user's own subscription (every workstream from 2 on): Claude Code (https://code.claude.com/docs/en/quickstart), Codex, Gemini CLI, Copilot CLI or OpenCode. Then `vibe provider <id>`.
9. Docker Desktop or OrbStack (a few artifact tasks, optional): https://orbstack.dev
10. Node (only for community skills via `npx skills add`): `brew install node`

`vibe toolbelt` lists what is present and what is missing with the command for each, and `vibe toolbelt --install missing` does the rest. Before each install: say what it is, what it is for, the size class (MB or GB), and the exact command. After each: verify with `<tool> --version`.

## Always safe (no installs)

- Set the camp up: `vibe init` (or `just setup`) writes the progress file, builds the vault and links the skills into `.claude/skills/`.
- Link skills by hand if that is all that is wanted: `mkdir -p .claude/skills && for d in .agents/skills/*/; do n=$(basename "$d"); [ -e ".claude/skills/$n" ] || ln -s "../../.agents/skills/$n" ".claude/skills/$n"; done`
- Run the game: `vibe play` (the hosted one), or `vibe play --offline` to cache a copy next to the camp and open that.
- Progress: `vibe status`; sync with the game through `vibe export` and `vibe import` (the camp-progress skill).
- Vault: open `vault/` in Obsidian; `vibe vault build` rebuilds the notes and the map, `vibe vault lint` reports orphans and dead links.
- Read the course: `vibe topics` and `vibe topic <id>` for the tech tree, `vibe explain <n>` for a stop in plain words, `vibe artifact` for the things on the islands. In a product checkout the same material is written out under `docs/`.

## Optional (ask first, each one)

- In a product checkout only: `just setup` runs `scripts/setup.sh` (gh, uv, DuckDB, Obsidian, skill links, vault and first commit in one go) and `uv run playwright install chromium webkit` fetches the browsers the game tests need, which is hundreds of MB. Show the script before running it.
- Community skill packs: `npx skills add <owner/repo> --skill <name>` (needs Node).

Finish with: what is installed, what was skipped, and the one command to start the evening (`claude` in this folder, or whichever agent the user installed).
