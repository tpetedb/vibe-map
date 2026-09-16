---
name: install-grimoire
description: Install, set up and run Project Grimoire on this machine, with the user choosing which dependencies to install. Use when asked to "set up grimoire", "install the course", "get me ready for the evening", or to run the game, CLI or vault.
---
# Install and use Grimoire

Nothing is installed without the user choosing it. Present the menu first, then act only on the chosen items.

## Menu (ask, then do)

Show this list and ask which to install (all, some, none):

1. Homebrew (needed for the rest on macOS): https://brew.sh
2. GitHub CLI `gh` (workstream 7): `brew install gh`
3. uv, Python environments (workstream 3): `brew install uv`
4. DuckDB (workstream 3): `brew install duckdb`
5. Obsidian app (workstream 6): `brew install --cask obsidian`
6. Claude Code (all workstreams): follow https://code.claude.com/docs/en/quickstart
7. Docker Desktop or OrbStack (tech tree only, optional): https://orbstack.dev
8. Node (only if the user wants community skills via `npx skills add`): `brew install node`

Before each install: say what it is, what it is for, the size class (MB or GB), and the exact command. After each: verify with `<tool> --version`.

## Always safe (no installs)

- Link skills for Claude Code: `mkdir -p .claude/skills && for d in .agents/skills/*/; do n=$(basename $d); [ -e .claude/skills/$n ] || ln -s ../../.agents/skills/$n .claude/skills/$n; done`
- Initialise the vault and state: `python3 grimoire/cli.py init`
- Run the game: `open game/grimoire.html` (or `python3 -m http.server 8000` then http://localhost:8000/game/grimoire.html)
- Check progress: `python3 grimoire/cli.py status`; sync with the game via `export` / `import`.
- Read the course: `docs/SYLLABUS.md`; the roadmap: `docs/ROADMAP.md`.

## Optional (ask first, each one)

- `scripts/setup.sh` does items 2 to 5 plus links, vault and first commit in one go. Show the script before running it.
- Community skill packs: `npx skills add wshobson/agents --skill <name>` (needs Node).

Finish with: what is installed, what was skipped, and the one command to start the evening (`claude` in this folder).
