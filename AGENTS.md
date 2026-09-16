# AGENTS.md

Instructions for any AI coding agent working in this repository. Format: https://agents.md (plain Markdown, no required fields). Claude Code reads this through `CLAUDE.md`.

## Project overview

A learning project: a single-file browser game, a small data pipeline around it, and an Obsidian vault that records what was learned. Keep it small and readable. Prefer one file over a framework.

## Ways of working

- Single-file architecture for the game: `game/index.html`, no external dependencies, double-click to play.
- Data lives in `data/scores.csv` with the columns `played_at,player,score,duration_s`. Never change the column names without also changing `sql/` and `python/`.
- Scores are a system of record. Never reset or rewrite `data/scores.csv` without asking.
- After every change, end with a one-line summary of what changed.
- Say what you are about to do before you touch more than one file.

## Commands

- Run the game: open `game/index.html` in a browser.
- Query scores: `duckdb -c "$(cat sql/top_runs.sql)"` or `python3 python/scores.py`
- Progress: `python3 grimoire/cli.py status`
- Tests: none yet. If you add Python beyond one file, add `pytest` and a `tests/` folder.

## Code style

- Python: standard library first; add a dependency only when it removes real work. Format with `ruff format` if available.
- SQL: lowercase keywords, one clause per line, comments above the query explaining the question it answers.
- HTML/JS: no build step, no minification, comments where the logic is not obvious.

## Notes and memory

- The Obsidian vault is `vault/`. One note per topic in `vault/Grimoire/`. Link generously with `[[wikilinks]]`. Date entries.
- After a session, write or update the note for what was built and link it from `vault/Grimoire/Tonight.md`.

## Git

- Commit after every change you would be sad to lose. Message: what and why, one line.
- Never force-push. Never rewrite history on `main`.

## Security

- No secrets in the repo. Tokens go in the environment or the OS keychain.
- Do not run commands that delete outside this folder.
