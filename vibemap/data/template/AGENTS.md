# AGENTS.md

Instructions for any AI coding agent working in this camp. Format: https://agents.md (plain Markdown). Claude Code reads this through `CLAUDE.md`.

## What this folder is

A Vibe Code Camp: a learner's own workspace, their notes, and the configuration of the tools that help them. The course engine (the game, the `vibe` command, the checks) is not here; it is installed as the `vibe` command and served as a hosted game. Do not try to find or edit its source in this folder.

## Zones

| Path | Owns | Rule |
|---|---|---|
| `workspace/` | The learner's own projects: `workspace/game/index.html` from workstream 1, `workspace/data/scores.csv`, `workspace/sql/`, `workspace/python/`, anything else they build. | Build here. Ask before deleting. `workspace/data/scores.csv` is a system of record: never reset or rewrite it without asking. |
| `vault/` | The Obsidian vault. `vault/Camp/Tonight.md` is the hub. | One note per topic in `vault/Camp/`, frontmatter with `title`, `date`, `tags`, generous `[[wikilinks]]`. `vibe vault lint` must stay clean. |
| `vibe.toml` | Name, persona, difficulty, provider, theme, vault mode. | Change through `vibe name`, `vibe persona`, `vibe difficulty`, `vibe theme` or `just start`, not by hand, so the schema is enforced. |
| `.agents/skills/`, `.claude/`, `AGENTS.md`, `justfile`, `.github/` | The agent and automation configuration of this camp. | Editing these is part of the course (workstreams 2, 4, 7, 8). Keep changes small and say why in the commit. |
| `.vibe/` | Progress state, ignored by git. | Never edit by hand; `vibe done`, `vibe check`, `vibe import`. |

## Commands

- `vibe status`, `vibe check <n>`, `vibe done <n> "what I built"`: progress and checks.
- `vibe vault build`, `vibe vault lint`: the notes.
- `vibe export`, `vibe import <code>`: sync with the game.
- `just` lists the rest; `just start` is the terminal menu.

## Ways of working

- Say what you are about to do before you touch more than one file.
- Tests before claims: a workstream is done when `vibe check <n>` says so, not when the code looks right.
- Commit after every change you would be sad to lose. Message: what and why, one line.
- No secrets in the repo. Tokens go in `.env` (ignored) or the OS keychain.
- After every change, end with one line: what changed.
