# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2026-09-17

### Changed

- The tech tree is grouped by shelf (terminal and shell; version control and GitHub; config and formats; languages and code; data; web, networks and APIs; ship and run; agents and the harness; docs and versioning; knowledge and Obsidian; what is coming), each topic with a depth (basics, working knowledge, deep), instead of ages with career ranks. The game's tree view, the vault's Tech tree note, the generated topic notes (tag per shelf), the Obsidian graph groups (one colour per shelf) and `docs/ROADMAP.md` follow. The ages remain only as the player's XP ladder (Intern to Expert).

### Added

- Ten artifacts on the campus island, each a prop you walk up to and inspect: the cafe (client, server, protocol: 200, 404, 429, 503), the fountain (a cache), the well (a database: scan, index, transaction), the lighthouse (DNS), the dock (containers: build, push, run), the windmill (cron and hooks), the balloon (the cloud and its meter), the mountain (the stack in six layers), the market stall (an API and its docs) and the bridge (MCP). Each prints a terminal-style demo per button, ends with a question from Rolinda and links the vault notes. Found artifacts turn green, count in the HUD, travel in the progress code (`artifacts`), appear in the vault note Artifacts and earn the Collector badge; the play-through visits all ten.
- Terminal setup modules from Tom's toolbox (MIT): `vibe dotfiles` lists, shows and installs zsh (completion dropdown, history suggestions, palette highlighting, fzf, a tmux picker), tmux (the bottom bar, j/k/i/l panes), Ghostty (the R2-D2 high-contrast theme), Starship (the prompt), AeroSpace (tiling) and the R2-D2 Obsidian theme into the vault; backups for anything that differs, one source line in `~/.zshrc`, `--dry-run`, `--brew`; a Terminal setup screen in `just start`.
- Three tech nodes: Git hooks (pre-commit to pre-push, `core.hooksPath`, pre-commit and lefthook), Agent hooks (Claude Code's events, scopes, matchers and exit codes, with this repo's own hook as the example) and Interfaces (GUI, TUI, CLI, API, MCP and ACP, with sourced history from Unix to ACP).
- Obsidian feature modules: `vibe vault feature <id>` and `--all` bootstrap one note per feature the official help documents (thirty-five: links, backlinks, graph view, tags, properties, callouts, embeds, templates, daily notes, unique notes, bookmarks, search, quick switcher, command palette, hotkeys, slash commands, workspaces, outline, note composer, slides, canvas, bases, web viewer, Obsidian URI, Obsidian CLI, community plugins, CSS snippets, Sync, Publish, Web Clipper, Obsidian Flavored Markdown, file recovery, page preview, random note, footnotes) with the exact commands, the syntax and a five-minute try, plus working example files (a JSON Canvas, a base, a template, a deck, a CSS snippet, a daily template). The facts live in `vibemap/data/obsidian.json`, extracted from obsidianmd/obsidian-help; `docs/OBSIDIAN.md` is generated from it by `just tree`.

## [0.3.0] - 2026-09-17

### Added

- The `vibe` package: a click CLI (`uv run vibe`) with status, check, done, map, vault, export, import, scores, council, explain, init, play, start, persona, theme, toolbelt, provider, difficulty, mode and mentor, and rich output in the house palette.
- Quests that verify real work: `vibe check N` inspects the repo and awards XP, `vibe done --force` claims at half XP, levels mirror the ages of the tech tree, badges (ADR 0004).
- Versioned pydantic state, migrated on load, and config in `vibe.toml` with unknown keys refused; personas, themes, a toolbelt report, model providers, the council of mentors, and a Textual onboarding screen (`just start`).
- The vault builder with lint, a committed vault baseline of 96 notes, and the Obsidian vault pre-configured: graph colour groups by tag, a dark base in the house palette, note templates, `docs/VAULT.md`.
- The Python toolchain: a uv project with `pyproject.toml`, a `justfile` with agent recipes, style and link checks in `tools/checks.py` (ADR 0003).
- Browser tests with Playwright: seven Chromium smoke tests and a WebKit iPhone battery (tap, joystick, sheet scroll, HUD width, WebGL draw budget); pytest tests for the CLI (state migration, the progress code version gate, quests, vault build and lint, scores through polars and DuckDB).
- `src/`: the game split into source files with a concatenating build, `tools/build.py --check` to catch hand edits, and `vibemap/data/campaign.json` as the one source for game and CLI (ADR 0001).
- The tech tree fact-checked: every history claim cited to a primary source (137 sources), new nodes for .env, zsh, YAML and TOML, and now Semantic Versioning, changelogs, ADRs and the README.
- Docs: `docs/AOE-STUDY.md` (ADR 0002), `docs/DESIGN.md`, `docs/ECOSYSTEM.md`, `docs/SKILLS.md`, `docs/COOKBOOK.md` generated from the personas, `docs/adr/` with four decision records, and this changelog.
- Skills: `council` for agents; `semver`, `changelog`, `adr` and `readme-quickstart` for the documentation habits; vendored `webapp-testing` (Apache-2.0) and `verification-before-completion` (MIT).
- An installable CLI: `uv tool install vibe-map` puts `vibe` on the PATH; it finds the camp from any subfolder (`vibe.toml`, or `VIBE_HOME`), ships the campaign, the tech tree and the resources as package data (`vibemap/data/`, `vibemap/tech.py`), and `vibe new [dir] [--github OWNER/NAME]` clones the template or creates a repo from it.
- Lucide icons (ISC) on the HUD, the enter pill, the sheet, the roadmap rows and the vault toolbar (`src/game/05-icons.js`, `iconize()` for static markup).
- The vault graph runs on d3-force (ISC): a simulation that cools and stops, pan by dragging, zoom with the wheel, labels only on hubs and the selection, an Open in Obsidian button that deep-links to the real vault (`obsidian://open`) or to the vault folder on GitHub when hosted.
- A terminal pet: `vibe pet` (show, animate, configure, gallery), a strolling companion on the launch screen of `just start`, a `[pet]` table in `vibe.toml`. Sprites and the deterministic roll ported from claude-buddy (MIT), plus a crab of our own.
- `docs/QUICKSTART.md` (three paths in, numbered, with what you should see) and `docs/ABOUT.md` (why it looks like this, whose toolbelt it is); a fourth onboarding screen with the campaign map; the version and theme stamped on the title screen.
- The template pieces: CI and Pages workflows, `env.example`, `scripts/setup.sh` with `--check` and `--yolo`, zsh helpers, `just break`, `just rescue`, `just council`, `just explain`, and a Claude model fallback for print mode.

### Changed

- The product is Vibe Code Camp everywhere: the Python package is `vibemap`, the command is `vibe`, the config is `vibe.toml`, state lives in `.vibe/`, the vault folder is `vault/Camp/`, the game is `game/vibe-map.html`, the skills are `develop-camp`, `install-camp` and `camp-progress`. The game reads progress from the new `vibemap1` key and, once, from the old `grimoire3` key, so nobody loses an evening.
- The title screen: the island renders and orbits behind the panel from the first frame, the brief folds away, a stats row and a monospace kicker replace the wall of text, and the call to action sits above the fold on a phone. Every leftover cyan, violet and pink (callouts, the vault reader, the path rows, the world picker) maps to the five hues; no gradients anywhere.
- The default theme is `studio`: professional, plain, coffee, with Rolinda's questions intact. `wine-night` keeps the original jargon and pairings as an optional mode (`vibe theme wine-night`).
- `AGENTS.md` adopts the file map, comment and test-loop conventions studied in sokrypton/aoe, ideas only (ADR 0002), and the standard-library-only rule for Python is lifted (ADR 0003).
- The seven house skills rewritten for the `src/` layout and the uv CLI.
- The existing Python formatted with ruff; regenerated outputs stay byte-identical.
- The onboarding test runs on injectable paths instead of the real config.

### Removed

- The fantasy layer: the Grimoire codename, the summoned creature with strength and wisdom, the dice, the spell and the dragon. In their place: a project mascot with speed, insight and charm, logged runs, releases and a coffee scoreboard. The satire of corporate language stays.

### Fixed

- Walking on every browser: the collision check called `onLand`, which did not exist (the helper is `onLandW`), so moving Lotte threw a ReferenceError.
- The phone HUD: the name pill takes its own row and the KPIs sit below the buttons.
- The backup hook in `.claude/settings.json`.

## [0.1.0] - 2026-09-16

The initial package on `main`: the course as one folder, no dependencies beyond Python 3.

### Added

- The single-file 3D game `game/vibe-map.html` and the placeholder `game/index.html` for workstream 1.
- `vibemap/cli.py`, a standard-library terminal companion (`uv run vibe status`), with `vibemap/campaign.json`.
- `AGENTS.md`, `CLAUDE.md`, `HANDOVER.md`, seven house skills in `.agents/skills/`, the `scorekeeper` subagent and the backup hook.
- `data/scores.csv`, three DuckDB queries in `sql/`, and `python/scores.py`.
- The Obsidian vault seed in `vault/Camp/`, `README.md`, `docs/SYLLABUS.md`, `docs/RESOURCES.md` and `docs/ROADMAP.md`.
- The tech tree source `tools/tech.py` with its generator `tools/regen_tree.py`.

[Unreleased]: https://github.com/tpetedb/vibe-map/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/tpetedb/vibe-map/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/tpetedb/vibe-map/compare/v0.1.0...v0.3.0
[0.1.0]: https://github.com/tpetedb/vibe-map/releases/tag/v0.1.0
