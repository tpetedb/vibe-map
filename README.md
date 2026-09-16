# Vibe Code Camp (vibe-map)

From intern to expert in one evening, with wine. A 3D island game, a syllabus, a template repo and a terminal companion for learning to build with AI coding agents. Internal codename: Project Grimoire.

Repo: https://github.com/tpetedb/vibe-map · clone `git clone git@github.com:tpetedb/vibe-map.git`

A starter repository for one evening of learning to build with AI coding agents, and for everything you build after it. It pairs with the game (Project Grimoire) but stands on its own.

What you get:

- `AGENTS.md`: provider-agnostic instructions any coding agent reads (Codex, Cursor, Copilot, Gemini CLI, Claude Code via import). See https://agents.md
- `CLAUDE.md`: one line that imports `AGENTS.md`, plus the few things only Claude Code understands (hooks, subagents, vault path).
- `.agents/skills/`: five skills in the Agent Skills open standard (https://agentskills.io): Obsidian notes, Mermaid diagrams, DuckDB SQL, Python for data, and the Grimoire progress skill. `scripts/setup.sh` links them into `.claude/skills/` so Claude Code sees them too.
- `.claude/agents/scorekeeper.md`: a subagent that only does one job.
- `.claude/settings.json`: one hook that backs up `data/` after every edit.
- `grimoire/cli.py`: a small terminal companion. It tracks which workstreams you finished, writes the note for each one into your vault, draws a Mermaid map of your progress, and exports a code you can paste into the game (and back).
- `data/`, `sql/`, `python/`: a real scores file, DuckDB queries and a Python script to learn on.
- `vault/`: an Obsidian vault that the CLI and the agent write into.
- `docs/RESOURCES.md`: curated, real courses and references, all clickable.
- `HANDOVER.md`: read this first if you are an agent continuing the work.
- `game/grimoire.html`: the game itself, one file.
- `.agents/skills/develop-grimoire` and `install-grimoire`: one skill to develop this product, one to install and use it (you choose which dependencies).
- `docs/ROADMAP.md`: the tech tree from intern to expert in five ages, with history and five-minute tries.

## For the agent

Read `HANDOVER.md`. It starts with what Tom must do himself, then Task 0 (study sokrypton/aoe, Age of Epochs II), then the priority list.

## Quickstart (Mac)

1. On GitHub, press **Use this template**, create your own repo, clone it.
2. `bash scripts/setup.sh` (installs the GitHub CLI, uv, DuckDB, links skills, initialises the vault). Read the script first; it is short.
3. Install Claude Code following https://code.claude.com/docs/en/quickstart, then run `claude` in this folder.
4. Open `vault/` in Obsidian: https://help.obsidian.md/manage-vaults
5. `python3 grimoire/cli.py status`

Then open the game and walk to the 18:00 signpost.

## The eight workstreams

| Time  | Workstream            | You end up with                              | Docs |
|-------|-----------------------|----------------------------------------------|------|
| 18:00 | Innovation Hub        | a playable single-file game                  | https://code.claude.com/docs/en/quickstart |
| 19:00 | Centre of Excellence  | AGENTS.md rules that stop you repeating yourself | https://agents.md · https://code.claude.com/docs/en/memory |
| 20:00 | Data Warehouse        | scores.csv, DuckDB queries, a Python chart   | https://duckdb.org/docs/ · https://docs.python.org/3/tutorial/ |
| 21:00 | Business Continuity   | git history, a rollback, one hook            | https://code.claude.com/docs/en/hooks-guide |
| 21:30 | Stakeholder Bridge    | one MCP integration                          | https://code.claude.com/docs/en/mcp |
| 22:00 | Knowledge Tree        | a linked vault and its graph                 | https://help.obsidian.md/plugins/graph |
| 22:30 | Go-to-Market          | the game at a public URL                     | https://docs.github.com/en/pages/quickstart |
| 23:00 | Autonomous Operations | headless Claude on a schedule, a subagent    | https://code.claude.com/docs/en/headless |

## Sync with the game

- `python3 grimoire/cli.py export` prints a code. In the game: Roadmap, "Import progress", paste it.
- In the game: Roadmap, "Export progress", copy the code, then `python3 grimoire/cli.py import <code>`.

## Licence

MIT. Fork it, change it, rename it.
