# Handover for the next agent

You are picking up Vibe Code Camp (internal codename Project Grimoire): a gamified course in building with AI coding agents, packaged as a 3D browser game, a terminal companion with quests and XP, an Obsidian vault, a syllabus and a template repo. Owner: Tom. Learner: Lotte (Chief of Staff, plays games, likes spreadsheets). Character: Rolinda (knows nothing about AI, insufferable about wine). Tone: over-the-top corporate jargon on top of real, useful content; Rolinda speaks plainly. No em-dashes anywhere, no emoji.

Read in this order: this file, `AGENTS.md`, `docs/adr/README.md`, then `.agents/skills/develop-grimoire/SKILL.md` before touching the game.

## State on 2026-09-16 (end of the one-shot session)

Everything below is built, tested and committed on `main` after the PR from `feat/grimoire-oneshot`.

| Area | What exists | Proof |
|---|---|---|
| Game | `src/` in 22 parts, built into `game/grimoire.html` (1 MB, three.js r128 and Motion 12 embedded, no CDN). Theme, dates, repo URL and shadow map come from `grimoire.toml` through `tools/build.py`. Design tokens from `docs/DESIGN.md`. Pre-flight is back on the roadmap. Export code carries `v:2`. | `just build`, `tests/test_build.py`, `tests/test_game_smoke.py`, `tests/test_game_webkit.py` (iPhone WebKit), `tests/test_game_playthrough.py` (every island, stop, mentor and the finale, zero page errors) |
| CLI | `grimoire/` package: click commands, rich output in the house palette, pydantic state (versioned, migrates v1) and config (unknown keys refused), quests with checks that inspect the repo, XP and levels, badges, personas, themes, toolbelt, providers, council, note-taking methods, Textual onboarding (`just start`). | `tests/test_cli.py`, `tests/test_tui.py` |
| Vault | `vault/` pre-configured (graph colours by tag, dark base, templates); `grimoire vault build` writes 100 lint-clean notes; `vault lint` finds orphans and dead links. | `uv run grimoire vault lint` |
| Docs | Syllabus, generated Roadmap (40 tech nodes, every date sourced), Cookbook (generated from personas), Design, Ecosystem, Vault, Note methods, Skills, Age of Epochs study, ADRs, CHANGELOG. | `just cookbook`, `just tree`, `tools/checks.py links` |
| Template | CI and Pages workflows, `env.example`, `scripts/setup.sh` (`--check`, `--yolo`), `scripts/grimoire.zsh`, `justfile` plus `agents.just`. | `.github/workflows/`, `just --list` |
| Media | `docs/media/`: hero, four islands, roadmap, vault, tree, phone, gameplay GIF, rendered by `just media`. | |

## What Tom has to do himself (the agent cannot)

1. On GitHub: Settings, Pages, source **GitHub Actions**, so `pages.yml` can publish the game at the Pages URL. Then run the workflow once (Actions, pages, Run workflow).
2. Test the game on an iPhone with real Safari (the WebKit tests are the closest headless proxy) and paste what you see back to the agent.
3. Confirm the go-live dates in `grimoire.toml` `[finale] dates` (placeholders: Fridays and Saturdays from 25 September to 23 October 2026) and Lotte's actual free evenings.
4. Decide on the classic 2D view proposal in `docs/AOE-STUDY.md` (recommended) and the multiplayer proposal (not recommended before the first evening).
5. `git tag v0.1.0 e08deb6` and, when 0.2.0 ships, `git tag v0.2.0`, so the CHANGELOG links resolve.
6. If you want `grimoire explain` and `grimoire council` on a provider other than Claude Code, install that CLI (`uv run grimoire toolbelt --tier provider`) and set it with `uv run grimoire provider <id>`; only the Claude path was exercised end to end.

## Known gaps and suggested next work, in priority order

1. **Classic view** (docs/AOE-STUDY.md, proposal A): a 2D canvas map of the campus behind a toggle, reading the same `WORLDS` config. One evening of work, the strongest visual addition left.
2. **Persona guides on the islands**: a walker per persona (the cleaning CEO, the pabo teacher...) as extra characters, using `src/game/11-character.js`. The data is in `grimoire/personas.py`; the game does not read it yet.
3. **Roadmap mode** (`[learner] mode = "roadmap"`): the config and the `roadmap_done` state exist, the quests do not; every tech node should become a quest whose check is a vault note with the "Try in five minutes" done.
4. **marimo notebook** for workstream 3 (`uv add marimo`, `marimo edit python/scores.py`): the design doc recommends it; not started.
5. **Council in the game**: the CLI and the skill exist; a "Convene" button on the roadmap that shows the last minutes from the vault would close the loop.
6. Textual onboarding: a fourth screen with the campaign grid (`docs/DESIGN.md` specifies it) is not built; `grimoire status` covers it in the terminal.
7. `tools/checks.py links` reports two pre-existing placeholders as broken (`http://localhost:8000` in the localhost lesson, `github.com/YOUR-USER/dotfiles` in the syllabus); both are intentional.

## How the game is built (important before editing)

- Edit `src/`, never `game/grimoire.html`. `just build` concatenates in the order in `tools/build.py` and injects `CONFIG` (from `grimoire.toml`), the campaign JSON, the generated tech notes and the tree.
- Everything is in one IIFE. Public functions are attached to `window` (start, openSheet, claim, openVault, openTree, setWorld, nextWorld, exportProgress, importProgress, ...). `window.__S()` returns the state, `window.__debug()` the walker, draw calls and mentors, for tests only.
- State `S` is persisted in `localStorage["grimoire3"]`. Shape: `{name, done, doneW, path, rolls, versions, bridges, date, wine, world, creature}`.
- Worlds are `WORLDS` in `src/game/20-worlds.js`; `buildWorld(id)` rebuilds the scene. Buildings are `building(k)` in `12-buildings.js`. The vault is `NOTES` (handwritten in `50-notes.js`, generated tech notes injected). The tech tree and the 40 tech notes come from `tools/tech.py` via `just tree`; never hand-edit outputs.
- Layout: the 3D stage is a normal block, everything else flows below (no fixed layers). Colours: `mat()` converts sRGB to linear; use it or `fixColors()`. Motion is optional: `fx()` and `countUp()` in `00-state.js` degrade to instant when `window.Motion` is missing or reduced motion is on.
- Tests: `just smoke` while iterating, `just verify` before a commit. The play-through (`tests/test_game_playthrough.py`, about a minute) is the strongest guard; it found a stray closing tag in workstream 6 and a `ReferenceError` in the walking code that no smoke test saw.

## Ground rules

- Never force-push, never rewrite history on `main`, never run DDL. Push feature branches and open a PR; Tom merges (he asked for merges when a branch is green, so an agent may merge a green PR he has approved in his instructions).
- Python dependencies are welcome when they remove real work (ADR 0003). Declare them in `pyproject.toml`, install with `uv`.
- The game stays one file with no CDN. Anything vendored is embedded in `src/vendor/` with its licence named in `tools/build.py`.
- Ask before changing the tone of any copy; the jargon is intentional. Serious voices are themes, not edits.
- End every change with one line: what changed.
