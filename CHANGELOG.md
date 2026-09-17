# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.7.0] - 2026-09-17

### Changed

- Three zones, separated: the learner's own work now lives in `workspace/` (`workspace/game/index.html`, `workspace/data/scores.csv`, `workspace/sql/`, `workspace/python/`), the checks, the scorekeeper, the backup hook, the Pages workflow, the lessons and the skills follow; `vibe new` writes a slim camp from a template shipped inside the package (README, AGENTS.md, CLAUDE.md, vibe.toml, justfile, the learner skills, the hook and subagent, a Pages workflow, an empty workspace), builds the vault and makes the first commit, instead of cloning the whole engine; `vibe play` opens the hosted game outside the product repository, `--offline` caches a copy. `docs/MAINTAINERS.md` explains the layout and how a change travels; `tools/sync_template.py` keeps the template's skills, hook and subagent equal to the product's, with a test.
- `<your_name>` is the default name everywhere Lotte used to be one: the state file, vibe.toml, the game's title screen and the terminal onboarding show the placeholder and say to type your name plainly, without the angle brackets. Lotte remains a character you can pick.

### Added

- Two roadmap topics with sources: Separation of concerns (Dijkstra's EWD 447, Parnas 1972, Conway 1968, Ousterhout, Twelve-Factor config, Team Topologies) and Building the builder (Engelbart's bootstrapping, Brooks's No Silver Bullet, Grove's leverage, AGENTS.md, Claude Code memory), both pointing at the camp's own layout as the worked example.

## [0.6.0] - 2026-09-17

### Added

- A much bigger map. One constant, `WORLD_SCALE` (1.6), is applied once at load to every coordinate the game uses (land, plots, path, river, lake, bridge, prop positions, mentors, artifacts), while buildings and walkers keep their size; walking speed, the camera, the fog and the sky distances scale with it so the feel stays the same, and the inn stays at the origin. Every stop now has its own path: a spur leaves the ring at the plot and runs outward over a causeway to an annex, a small land blob with a flag that carries the stop's hour. An annex is hidden until its stop is done and pops in with the building's confetti when the stop is claimed (or imported), so the level grows as you play; annexes of done stops are there on load. Two new pictures, `docs/media/island-campus-start.png` and `island-campus-expanded.png`, come from `tools/campus_shots.py`.
- Onboarding in the game: the title screen is a four-step form on a first visit. Who you are (Lotte, Frank, Max, Rolinda, or your own name; each preset is a different walker), how hard (beginner to god, changeable later under Settings), how you want to play (just the game, or the full experience: a setup guide with the exact commands for the terminal, the camp folder and Obsidian, plus the export and import loop that keeps the two in sync), go. Returning players get the resume button first.
- Commands fold by difficulty: every command block in a lesson is a `Commands` disclosure, open at beginner, easy and normal, folded at hard, expert and god, always one click away. The setup guide's commands are always open.
- Setup guide screen from the Roadmap, and `vibe name` to set your name in the terminal.
- A naming convention for local camps, `vibe-map-<name>-<YYYY-MM-DD>`: `vibe new` without a directory uses it (`--name` picks the person part, else the login), and the setup guide suggests it with your name and today's date.
- Three roadmap topics on the agents shelf: Prompting (task, goal, hard constraints, context, definition of done), Structure (XML tags for the model, Markdown blocks for the reader, fenced code for anything copied) and The symbols (what `/`, `!`, `@`, `#`, `[[ ]]`, `---` and backticks mean to Claude Code, CLAUDE.md, Markdown and Obsidian), all sourced to the Anthropic and Claude Code docs.
- Reset progress: a two-click button on the Roadmap and in Settings takes the game back to the start of the roadmap (every stop undone, artifacts and mentor choices cleared, name and settings kept), and `?reset` on the URL does the same for the hosted game: https://tpetedb.github.io/vibe-map/?reset

## [0.5.0] - 2026-09-17

### Added

- Ten more artifacts, spread over the four islands, each with its own small procedural building (`src/game/17-artifact-props.js`) that the walker goes round: the factory (a data pipeline: raw, bronze, silver, gold; a failed run that reruns cleanly; batch versus stream) and the post office (queues and pub/sub: a letter delivered later, at-least-once delivery, a dead-letter shelf) on the campus; the shop (a package registry: `uv add` as buying, the lockfile as the receipt, a yanked version) and the bank (secrets and auth: a token is a key, `.env` is the safe, a leaked key revoked and rotated) in the sandbox; the data centre (an inference request's path, latency by region, a cold start, batch versus interactive), the energy grid (tokens as watts, a rate limit as a fuse, autoscaling, a budget alarm) and the library (RAG: a question becomes a vector, the nearest shelves, a citation, a stale index) in cold storage; the office (planner, worker, reviewer, `AGENTS.md` as the handbook, a review gate that rejects, subagents as departments), the households (users and privacy: data minimisation, anonymisation, a GDPR request) and the school (train and test split, overfitting caught by the test, a benchmark) in production. The roadmap card, the README and the tests count twenty; the play-through inspects the artifacts of every island.
- Settings in the game (the HUD's Settings button): map size (compact, big, the whole window), a full-screen button, vault mode, pairings, shadows, motion, walking speed; persisted with the progress, applied at once. The map is bigger by default (84 percent of the window).
- `vibe news`: six AI feeds (OpenAI news, Hugging Face blog, Simon Willison, Claude Code releases, the GitHub changelog, arXiv cs.AI; `[news] feeds` in `vibe.toml`) into `data/news.json` and the vault note News; the news is embedded into the game at build time and shown on the Roadmap; a weekly `news` GitHub Action pulls, rebuilds and commits so a forked repo and its hosted game stay current. Standard library only.
- `docs/LONG-GAME.md`: the command-by-command setup for playing over weeks with the terminal, the game and Obsidian side by side, and `just camp` to open all three.
- Grow mode for the vault: `vibe vault mode grow` keeps every note in `vault/_library` (excluded from Obsidian's graph and search) and unlocks notes into the camp as the campaign earns them (a stop's notes and their links, an artifact's notes, a mentor, the Obsidian feature notes when the vault stop is done, `vibe vault unlock` by hand). Tonight reports what is here and what is waiting; the in-game vault applies the same rules (`?vault=grow` previews it) so the graph grows as you play; `vibe vault mode full` restores everything; a Vault choice on the onboarding screen; `vibemap/grow.py`, three tests and a Playwright test.
- `docs/ECOSYSTEM.md` lists claude-obsidian (AgriciDaniel, MIT), the Claude Code skill set for wiki-style vaults, with `just obsidian-plugin` to fetch it and the one-line `claude --plugin-dir` to use it on this vault.

## [0.4.1] - 2026-09-17

### Fixed

- `vibe --version` reported 0.3.0 after the 0.4.0 release: the version string was pinned in `vibemap/__init__.py`. It now comes from the installed package metadata, with a test that it matches `pyproject.toml`.

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

[Unreleased]: https://github.com/tpetedb/vibe-map/compare/v0.7.0...HEAD
[0.7.0]: https://github.com/tpetedb/vibe-map/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/tpetedb/vibe-map/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/tpetedb/vibe-map/compare/v0.4.1...v0.5.0
[0.4.1]: https://github.com/tpetedb/vibe-map/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/tpetedb/vibe-map/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/tpetedb/vibe-map/compare/v0.1.0...v0.3.0
[0.1.0]: https://github.com/tpetedb/vibe-map/releases/tag/v0.1.0
