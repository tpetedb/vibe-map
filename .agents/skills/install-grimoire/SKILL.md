---
name: install-grimoire
description: Installs, sets up and runs Vibe Code Camp (Project Grimoire) on this Mac, with the user choosing every dependency. Use for "set up grimoire", "install the course", "get me ready for the evening", "is my machine ready", "what do I need installed", "start the evening", or to run the game, the CLI, the tests or the vault.
---
# Install and use Grimoire

Nothing is installed without the user choosing it. Present the menu first, then act only on the chosen items. `uv run grimoire start` (or `just start`) is the interactive version of this menu; offer it when uv is already there.

## Menu (ask, then do)

Show this list and ask which to install (all, some, none):

1. Homebrew (needed for the rest on macOS): https://brew.sh
2. uv, Python and the project environment (workstreams 1 and 3, the tests): `brew install uv`, then `uv sync` in this folder
3. just, the task runner behind `just start`, `just game`, `just test`: `brew install just`
4. GitHub CLI `gh` (workstream 7): `brew install gh`
5. DuckDB CLI (workstream 3): `brew install duckdb`
6. Obsidian app (workstream 6): `brew install --cask obsidian`
7. Claude Code (all workstreams): follow https://code.claude.com/docs/en/quickstart
8. Playwright browsers for the game tests (hundreds of MB): `uv run playwright install chromium webkit`
9. Docker Desktop or OrbStack (tech tree only, optional): https://orbstack.dev
10. Node (only for community skills via `npx skills add`): `brew install node`

Before each install: say what it is, what it is for, the size class (MB or GB), and the exact command. After each: verify with `<tool> --version`.

## Always safe (no installs)

- Link skills for Claude Code: `mkdir -p .claude/skills && for d in .agents/skills/*/; do n=$(basename "$d"); [ -e ".claude/skills/$n" ] || ln -s "../../.agents/skills/$n" ".claude/skills/$n"; done`
- Run the game: `just game` or `open game/grimoire.html`
- Progress: `uv run grimoire status`; sync with the game via `export` and `import` (the grimoire-progress skill)
- Vault: open `vault/` in Obsidian; `uv run grimoire vault build` rebuilds the notes and the map
- Read the course: `docs/SYLLABUS.md`; the tech tree: `docs/ROADMAP.md`; the links: `docs/RESOURCES.md`; the skills: `docs/SKILLS.md`

## Optional (ask first, each one)

- `just setup` runs `scripts/setup.sh`: gh, uv, DuckDB, Obsidian, skill links, vault and first commit in one go. Show the script before running it.
- Community skill packs: `npx skills add <owner/repo> --skill <name>` (needs Node). `docs/SKILLS.md` lists what is already vendored.

Finish with: what is installed, what was skipped, and the one command to start the evening (`claude` in this folder).
