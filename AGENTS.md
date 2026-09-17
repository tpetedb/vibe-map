# AGENTS.md

Instructions for any AI coding agent working in this repository. Format: https://agents.md (plain Markdown, no required fields). Claude Code reads this through `CLAUDE.md`.

## Project overview

A gamified course and a template: a single-file 3D browser game (`game/vibe-map.html`), a terminal companion with quests and XP (`vibemap/`), a small data pipeline in the learner's workspace (`workspace/data/`, `workspace/sql/`, `workspace/python/`), and an Obsidian vault (`vault/`) that grows as the learner progresses. Keep it small and readable. One file per concern; a dependency only when it removes real work.

## File map

Three zones, explained in `docs/MAINTAINERS.md`: the **product** (the engine: `src/`, `vibemap/`, `tools/`, `tests/`), the **template** a camp starts from (`vibemap/data/template/`, kept in sync by `tools/sync_template.py`), and the learner's **workspace** (`workspace/`; here it holds the worked example). The rest of the top level is this repository's own configuration for agents and CI.

| Path | Owns |
|---|---|
| `game/vibe-map.html` | The built game, one file, three.js embedded, no CDN. Produced by `just build` from `src/`; never hand-edit once `src/` exists. |
| `src/` | The game's source parts in load order; `tools/build.py` concatenates them and injects the campaign, the tech notes and `CONFIG` from `vibe.toml`. `src/vendor/` holds three.js r128, Motion 12, d3-force 3 and the Lucide licence, never edited; `src/game/05-icons.js` is generated from Lucide SVGs. |
| `vibemap/data/` | Package data the game and the CLI share: `campaign.json` (four evenings, twelve mentors), `resources.md` (the curated links; `docs/RESOURCES.md` is generated from it), `obsidian.json` (thirty-five Obsidian features extracted from the official help; `docs/OBSIDIAN.md` and the feature notes are generated from it). `vibemap/tech.py` is the tech tree. Installed copies of the CLI carry all three. |
| `workspace/` | The learner's zone: `game/index.html` from workstream 1, `data/scores.csv`, `sql/`, `python/`. Nothing may depend on its contents; `vibemap/quests.py` only reads it. |
| `vibemap/data/template/` | The camp skeleton `vibe new` copies (README, AGENTS, CLAUDE, vibe.toml, justfile, workspace, `_claude/`, `_agents/skills/`, `_github/`). Underscore folders become dot-folders in the camp. Skills, hook and subagent are synced from `.agents/` and `.claude/`; a test fails when they drift. |
| `vibemap/` | The CLI package: `cli.py` (click commands), `state.py` (pydantic models, versioned), `quests.py` (auto-verified workstreams and XP), `vault.py` (Obsidian writer and lint), `scores.py` (polars and DuckDB), `tui.py` (the `just start` onboarding), `personas.py` and `themes.py` (presets), `config.py` (`vibe.toml`), `pet.py` (the companion), `obsidian.py` (feature notes), `dotfiles.py` (terminal setup modules from `data/dotfiles/`). |
| `vibemap/project.py` | Where a camp is: `VIBE_HOME`, else the nearest ancestor with a `vibe.toml`. The CLI installs globally (`uv tool install vibe-map`) and runs in any camp; `vibe new` writes a slim camp from the template, without the engine. |
| `tools/regen_tree.py` | Emits the tree notes JS, the tree JS, `docs/ROADMAP.md` and `docs/RESOURCES.md` from the package data. Never hand-edit those outputs. |
| `tests/` | The pytest battery: CLI and quest unit tests, build check, Playwright smoke tests in Chromium and WebKit. |
| `workspace/data/scores.csv` | The system of record for scores. Columns `played_at,player,score,duration_s`; never rename without changing `workspace/sql/` and `workspace/python/`. |
| `docs/` | `MAINTAINERS.md` (the zones and how a change travels), `SYLLABUS.md` (the course), `ROADMAP.md` (generated), `RESOURCES.md` (curated links), `AOE-STUDY.md` (what sokrypton/aoe taught us). |
| `vault/` | The Obsidian vault. `vault/Camp/Tonight.md` is the hot cache; every note is reachable from it. `.obsidian/` is pre-configured. |
| `.agents/skills/` | Skills in the Agent Skills standard. `.claude/skills/` holds symlinks to them. |
| `justfile`, `agents.just` | Every task a human or an agent runs. `just` lists them; `just start` onboards. |

## Ways of working

- Say what you are about to do before you touch more than one file. Restate the request in one line and name the files.
- The game stays one file with no CDN and three.js embedded. Edit `src/`, run `just build`, test the built file.
- State is data, the view is derived. Everything persisted lives in the game's `S` object or the CLI's `state.json`; the DOM, the 3D scene and the vault notes are rebuilt from it, never the other way round.
- One helper per concept (`mat()`, `fixColors()`, `onLandW()`, `Vault.write()`). Never re-spell the raw check at a call site.
- Comments state constraints and why, in one or two lines. Never narrate changes ("replaced the old X"), never date a comment, never reference line numbers in other files.
- Versioned formats fail loudly. The progress code and `state.json` carry a version; an unknown version is refused with a clear message, not patched around.
- Scores are a system of record. Never reset or rewrite `workspace/data/scores.csv` without asking.
- Python dependencies are welcome when they remove real work. Declare them in `pyproject.toml`, install with `uv`, never bare pip.
- After every change, end with one line: what changed.

## Test loop

Adopted from sokrypton/aoe, see `docs/AOE-STUDY.md`:

1. While iterating, run the test closest to the blast radius: `just test-one "tests/test_cli.py"` or `just smoke`.
2. Before every commit, the full battery: `just verify` (ruff, pytest with Playwright, build check). Zero page errors in the browser is the bar.
3. Test the entry point, not the mechanism. The smoke test clicks the real buttons; it does not call `claim()` directly.
4. Take a screenshot and look at it. They land in `tests/out/`.
5. Regenerate, never hand-edit: `just tree` after editing `vibemap/tech.py`.

## Commands

- `just` lists everything. `just start` is the onboarding menu. `just setup` installs what is missing.
- Run the game: `just game`. Build it: `just build`.
- Progress and quests: `uv run vibe status`, `uv run vibe check`, `uv run vibe done <n>`.
- Scores: `uv run vibe scores`, `duckdb -c "$(cat workspace/sql/top_runs.sql)"`, `python3 workspace/python/scores.py`.
- Tests: `just test`. Full gate: `just verify`.

## Code style

- Python: `from __future__ import annotations`, frozen dataclasses or pydantic models, a `__main__` guard, `ruff format` at line length 88, `basedpyright` basic.
- SQL: lowercase keywords, one clause per line, a comment above the query explaining the question it answers.
- HTML/JS: no build step beyond concatenation, no minification of our own code, comments where the logic is not obvious.
- Copy: no em-dashes anywhere. Rolinda speaks plainly; everyone else speaks corporate. Ask before changing tone.

## Notes and memory

- The Obsidian vault is `vault/`. One note per topic in `vault/Camp/`. Frontmatter with `title`, `date` and `tags`. Link generously with `[[wikilinks]]`. Date entries newest first.
- After a session, write or update the note for what was built and link it from `vault/Camp/Tonight.md`. `uv run vibe vault lint` finds orphans and dead links.

## Git

- Commit after every change you would be sad to lose. Message: what and why, one line.
- Never force-push. Never rewrite history on `main`. Push feature branches and open a draft PR; Tom merges.

## Security

- No secrets in the repo. Tokens go in `.env` (gitignored, see `env.example`) or the OS keychain.
- Do not run commands that delete outside this folder.
