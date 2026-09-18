# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- An analytics dashboard, in the game and in the terminal, on one event shape: `{ts, kind, id, world}` with `v` for a number of seconds. The game records into `S.events` through one helper, `track(kind, id, v)` (`src/game/00-state.js`), from the places where something happens: a session start, a stop opened and delivered, an artifact inspected, a mentor met, a mentor verified or an artifact built on import, the time a screen stayed open, and a minute tick while the island is on screen. The log is capped at 600 events and compacts a day of ticks into one before it drops anything, it stays in the browser, and the progress code still carries no events, so an import merges none. The Stats button on the HUD opens the panel (`src/game/89-dashboard.js`): six KPI tiles with sparklines, a ring per island, XP over time, a day-by-hour heatmap, bars for the time per stop, the path you took and a feed of recent events, all inline SVG, all derived from the state, working from 393px up.
- `vibe dashboard` writes `workspace/dashboard.html` from `.vibe/state.json`, the vault and `workspace/data/scores.csv` and opens it (`--no-open` to skip, `--out` to place it elsewhere, `--json` to print the numbers instead). It is one self-contained file with no script and no network, in the same design as the game panel: the tokens come from `vibemap/palette.py` (`css_tokens()`), and a test keeps them equal to the game's `:root` in `src/style.css`.

### Changed

- `main` is protected on GitHub: pull requests only, both CI jobs green and up to date, no force pushes or deletion, enforced for admins; release tags are immutable; merged branches are deleted automatically; secret scanning with push protection and Dependabot security updates are on. `docs/MAINTAINERS.md` and `AGENTS.md` say so.

## [0.9.0] - 2026-09-17

### Added

- Three configuration levels, nested, each flat inside, with `docs/CONFIG.md` as the table of "to change X, edit Y" for both a camp and the product. The repository level stays where the tools demand it; the source level is `src/config/` for the game (world scale, island radius, palette) and `vibemap/data/` for the CLI; the journey level moves from `vibe.toml` to `config/camp.toml` (name, persona, difficulty, provider, theme, vault mode, finale dates). `vibe new` writes `config/camp.toml`, and this checkout has one too so it stays a valid camp.

- `vibe fork` copies `src/`, its vendor files, `tools/build.py` and the generated inputs into `workspace/forks/vibe-map/`, with a `justfile`, a `README.md` with the challenges and a versioned `fork.json`; `just build` there produces the learner's own game file. `vibe check --fork` verifies that the fork exists, that its `src/config/` is no longer the product's and that it builds. A fork is the learner's copy to break and repair; the course keeps living in the product.

- A deterministic check on every stop of winter, desert and production where a deliverable exists, with the note check as the floor underneath all of them. The check reads what is on disk and every hint names the exact path: a backprop reproduction in `workspace/winter/backprop/`, a mermaid transformer in `workspace/winter/transformer.md`, a recorded local model run in `workspace/winter/local-model.md`, makemore and its samples in `workspace/winter/makemore/`, both ends of the vibe dial in `AGENTS.md`, six dot entries explained in `workspace/desert/dotfiles.md`, the learner's own pytest green under `workspace/`, a hook in `.claude/settings.json` that gates rather than bookkeeps, a spec with sections in `workspace/specs/`, a workflow under `.github/workflows/` that parses and runs ruff or pytest, a job with two recorded runs in `workspace/jobs/`, five eval cases in `workspace/evals/`, a Brewfile, a ghostty config and a zshrc in `workspace/dotfiles/`, a GitHub remote with a second branch, a reflog that remembers a rebase or a revert, a permissions allow list, two agents compared in `workspace/agents/comparison.md`, and `workspace/dotfiles/` as a git repository with `install.sh` and a README. The four winter stops that are genuinely reading only say so in the check name.

- A new production stop, Fork the game, with four challenges checked one at a time by `vibe check --fork <challenge>`: `exists` (the fork is there and was made by `vibe fork`), `config` (its `src/config/` differs from the product's and it still builds), `topic` (a stop or a tree node of the learner's own in the fork's generated data) and `repair` (a build that failed and then passed, from `repair.json` that `just record` writes in the fork, or from the fork's git history). The challenges print and claim under that stop's heading rather than a production 0, and the fork now carries `tools/record_build.py` and a `just record` task.

- Mentor encounters. Each of the twelve mentors now has a dialogue of three or four exchanges in the game, walked one question at a time, where every line is a paraphrase of something that person is on record saying, with the link it came from next to it. Each encounter sets one exercise of under fifteen minutes in `workspace/mentors/<id>/` and `vibe check --mentor <id>` (or `--all`) verifies it without a network: Karpathy's bigram model must print the likeliest character after "a", Torvalds's script must produce the same blob hash as `git hash-object`, Hinton's twenty steps of gradient descent must land on the target, Sutton's brute-force search must beat the rule you invented, and the note-shaped exercises (Cherny's CLAUDE.md rule with the command that proves it, Wu's spec-plan-todo, LeCun's what mattered against what you could throw away, Li's ten labelled rows, Amodei's falsifiable forecast, Olah's mermaid circuit, Hashimoto's one readable config file, opencode's one prompt across two providers) must hold the sections the exercise asks for. A verified encounter is worth half a workstream in XP, turns the mentor's ring green and raises a plaque on their spot with their one line on it, writes the encounter and the exercise into their vault note, and earns the `mentored` badge when all twelve are done. The progress code carries the verified mentors inside version 2, so an older game or an older `vibe` ignores the key and keeps working.

- Artifacts became tasks. Each of the twenty artifacts on the islands keeps its demo and gains a "Do it for real" section written from the official documentation of the thing it stands for, with the page it came from linked on the sheet: `http.server` for the cafe, `functools.lru_cache` for the fountain, `sqlite3` for the well, `socket` for the lighthouse, the Docker "Writing a Dockerfile" page for the dock, the GitHub Actions events reference for the windmill, the AWS On-Demand Instances page for the balloon, `platform` for the mountain, FastAPI's First Steps for the market stall, the MCP build-a-server quickstart for the bridge, the DuckDB Python API for the factory, `queue` for the post office, uv's Working on projects for the shop, the git `gitignore` reference for the bank, `concurrent.futures` for the data centre, the Claude API rate limits page for the energy grid, `collections.Counter` for the library, the Claude Code subagents page for the office, `csv` for the households and scikit-learn's `train_test_split` for the school. Every task is under twenty minutes, lives in `workspace/artifacts/<id>/`, and the commands it gives are the ones its documentation gives, behind the same Commands disclosure the lessons use.

- `vibe check --artifact <id>` (or `--all`) verifies what was actually built, deterministically and offline: a Dockerfile whose instructions all parse and, when Docker is installed, an image that builds; a DuckDB pipeline whose gold table has rows; a FastAPI app its own test client gets 200 from; a workflow file that parses and carries a schedule trigger and a job with steps; an MCP config that lists a server with a command; a SQLite file with an indexed table that holds rows; a queue script whose output shows two deliveries, one retry and one dead letter in that order; a subagent file with valid frontmatter; and eleven more. A check that wants a tool this machine does not have says so, with the install command, instead of failing. The checks live in `vibemap/artifact_checks.py`, one function per kind, named from the `real` block in `vibemap/data/campaign.json`.

- The progress code carries an `artifactsBuilt` list, added inside version 2 so an older game or an older `vibe` ignores the key and keeps working. An artifact built for real is worth half a workstream in XP, reads "built for real" on the sheet and in the Artifacts vault note, and earns the new `builder` badge when all twenty are done.

- A fresh-camp end-to-end run: `tools/fresh_camp.py` installs nothing, starts the `vibe` process a learner installs, makes a camp with `vibe new`, proves that workstream 1, workstream 3 and a winter note check all refuse on an empty camp, scripts the two campus deliverables, proves the checks then pass, exports the progress code and imports it into a second camp. It runs nightly against `uv tool install .`, and `tests/test_fresh_camp.py` runs the same journey against the checkout.

- A `nightly` workflow for everything marked `integration`: the fresh-camp run and the full play-through, on a nightly schedule, on every `v*` tag and on demand. `ci` keeps the pull-request loop fast.

- A `browser` marker, applied automatically to any test that takes a browser fixture, so CI can split the battery without anyone labelling a new test by hand. Tests that read the workflows back assert the split holds.

- Three architecture decision records for the cycle: `0006-config-levels.md` (three nested levels, why `config/camp.toml` replaced `vibe.toml` and why the product checkout is also a camp), `0007-artifacts-as-tasks.md` (why a demo alone earns no XP, why every walkthrough is written from the official documentation of the thing, why the check is deterministic and offline) and `0008-mentor-encounters.md` (why a paraphrase with its source and never an invented quote, why an exercise is under fifteen minutes, why a verified encounter is worth half a workstream). All three explain why the progress code stayed at version 2 and gained keys inside it.

- `tools/script_camp.py`, one home for the deliverables a learner would have built: the stop deliverables of winter, desert and production, the twenty artifact fixtures, the twelve mentor exercises and the four fork challenges. `tests/test_stops.py` and `tests/test_artifact_tasks.py` read their scripted set from it instead of carrying their own, and the nightly regeneration of the played instance uses it to script a camp before it plays. It is safe to run in a camp that already has history and a remote: it adds nothing that is there, overwrites nothing the learner wrote, and leaves the repository on the branch it found it on.

- `vibe mentor` lists the twelve mentors with their island and whether the encounter is verified, `vibe mentor <id>` prints the exercise, its steps and the check that reads it, and `vibe mentor <id> --start` scaffolds `workspace/mentors/<id>/` with a stub of the file and a `notes.md`. The scaffold never makes the check pass, and an existing file is kept, not overwritten.

- The camp's Pages workflow publishes the learner's fork at `/fork/` when they have built and committed one.

### Changed

- The title screen puts the form first. The four steps, the name box and the Go row sit directly under the title and the campaign stats; the framing paragraph, the roles and the full brief moved below the Go button, and step 3 carries an honest prerequisites line (a terminal, about fifteen minutes, a GitHub account, a paid plan for Claude, Codex or Gemini). The Go and Resume buttons, the word for a stop in the HUD, the four KPI labels and the second line of the tagline are theme strings now: the studio preset says Start, Stops, Progress, Streak, Connections and Found, and the wine-night preset keeps Kick off the engagement, OKRs, Velocity and Synergy. A theme in `themes/<name>.toml` needs the five new keys, and an old file is refused with the missing names.

- The mini-games were audited against what they teach; the decision and the reasoning are in `docs/adr/0005-mini-games.md`. The mascot generator and the roll ledger are gone, along with `S.mascot` and `S.rolls`. Workstream 1 now builds the prompt you paste into Claude Code from your three sentences, workstream 2 runs a vague and a precise change request against the same component without a mascot in sight, and workstream 3 renames a column and shows the binder error DuckDB really prints. The release ledger, the connectors and the note graph are kept; opening workstream 6 now draws the graph, which only the playthrough tool used to do.

- The production island's stop 6 is Fork the game; Claude in Chrome, which was a two-click install with nothing to check, is folded into stop 5 (Claude Code, the power settings) as the browser surface, with its sources. The island still lays out eight plots, so nothing in the game, the progress code or the badges had to learn a ninth. Every stop on the three later islands gained a "Checked by" line in `docs/SYLLABUS.md` saying what the check reads.

- `tools/build.py` concatenates `src/config/*.js` before the game modules and resolves every input relative to the folder that holds it, or to `--root DIR`, so a fork builds on its own. `WORLD_SCALE`, the island radius and the palette moved out of the game modules into `src/config/00-config.js`.

- CI runs the whole battery. It used to run three unit files and three browser files, which left ten test files (artifacts, reset, grow, onboarding, notes, obsidian, pet, project, news, dotfiles) running nowhere but a maintainer's laptop. The WebKit file is now its own step with one rerun of what failed, which tells a lost WebGL context apart from a real defect, and the pytest command no longer passes a second `-q` that was swallowing the summary of failures.

- `vibe status` counts the encounters next to the artifacts (`K/12 mentors met`), and `status --json` carries `mentors`, `artifacts` and `artifacts_built` for the scripts that read it. The onboarding terminal shows the same three numbers, and the grow-mode hint follows the state: after every artifact is found it asks for one built for real, then for a mentor's exercise.

- The mentor screen in the game says each thing once. The summary list of ideas was a second telling of the dialogue, which now carries every idea with the link it was paraphrased from; the list stays in the mentor's vault note.

- The docs are finalised against the merged layout: `docs/CONFIG.md` gained the fork challenges, `repair.json` and the mentor workspace; `docs/MAINTAINERS.md` says how an artifact check and a mentor encounter travel to a learner; `docs/QUICKSTART.md` and `docs/LONG-GAME.md` carry the three new checks and the fork; `docs/SYLLABUS.md` describes an encounter and a Do it for real task; `docs/BRIEF.md` maps the professionalize cycle to the pull requests that delivered it and rewrites its gaps honestly; and the camp README tells a learner what the island asks them to build. A fork is a learner feature and never our development workflow: work on the product happens in the product.

### Deprecated

- `vibe.toml` at a camp root is still read, and still marks a camp, for one release. Every command says so in one line and points at `config/camp.toml`.

### Removed

- `tools/split_game.py`, the one-shot that cut the 2026-09-16 monolith into `src/` by line number. `src/` has been the source since, and the script read a file that no longer has those lines.

### Fixed

- The browser tests wait for signals the page produces instead of for a wall clock: the walker's own frame counter (a new read-only seam next to `window.__debug()`), the demo scripts behind the artifact terminal (`window.__demos()`), a settle helper for a spring or a smooth scroll, and the state, note or message a click actually produces. Every `wait_for_timeout` is gone from `tests/` and from `tools/play.py`. The fixed waits were hiding a failure: the game falls back to the roadmap list when the 3D scene will not start, and a test that waited 600 ms carried on regardless. It now fails loudly, which is how a seeded record with an out-of-range stop number was found.

## [0.8.0] - 2026-09-17

### Changed

- The docs separate a camp from the product repository. `docs/LONG-GAME.md` and `docs/QUICKSTART.md` no longer promise `just setup --check`, a `.venv`, Playwright browsers, `just verify` or `just build` to a learner in a camp, the "Where things end up" table labels every row camp or product, and the troubleshooting tables say what a camp does instead. The camp README leads with the next command and what you get, then a zones table written for the learner (your work in `workspace/`, notes in `vault/`, the rest is settings), says `just` needs `brew install just` and that every recipe also runs as `vibe <thing>`, moves `just scores` out of the day-one list, and tells the learner that the regenerated `vault/Camp` notes belong in git; the camp AGENTS.md says the same. Every code block now installs with `uv tool install git+https://github.com/tpetedb/vibe-map`, with the PyPI form as a footnote. Two dead sources are fixed: the Git 2.9.0 release notes (`.adoc`) and the dotfiles placeholder, now the GitHub dotfiles guide.

### Fixed

- A play-through of the browser game in Chromium and on an iPhone-sized WebKit turned up nineteen defects; all of them are fixed. A signpost now wins over an artifact when both are in range, and the mountain's detection radius no longer reaches over the Business Continuity plot, so stop 4 can be entered by walking. An empty name is refused at the title screen instead of starting the evening as `<your_name>`: the placeholder is never written to the saved state, and the HUD and the walker's label show the chosen character until a name is typed. The walker's label is rebuilt when the name changes and shrinks to fit its plate. A name with a quote or an accent is handled: the setup guide single-quotes it for the shell, and the camp directory folds accents (`Jorg` and the accented spelling get the same folder). `?reset` in the URL now runs after the saved record is read, so it no longer loses the name, the look, the play mode and the settings. Full screen is asked for on the document rather than on the stage, so the sheet and the vault stay visible. Escape closes the sheet and the vault, and opening either focuses its close button. A theme that does not pair wine gets its own pairing line from the theme data, and a theme with no pairings loses the blocks altogether. On a phone the title box is opaque, covers the HUD and keeps its primary button in view; the full-experience guide renders below that button. Resume is offered to anyone who has been here before, not only after a stop is done. The vault graph keeps its labels on the canvas and drops the labels of small nodes when zoomed out; the tech tree says it scrolls sideways and has buttons for it; "Open in Obsidian" becomes "Vault on GitHub" when the game is not served from a file. Workstreams 7 and 8 have real command blocks that fold with the difficulty. A progress code whose version is not 2 is refused with a clear message. Stale paths and counts: `workspace/python/scores.py`, `workspace/data/scores.csv`, `vault/Camp/Scores.md`, eight workstreams rather than six, and workstream 3 now teaches the schema the check reads (`played_at,player,score,duration_s`) at the path it reads it from.
- A stop on winter, desert or production is green only when the learner wrote the note: the check ignores everything vibe writes into it (the stub, the claim bullets, the campaign sources) and asks for a dated section of their own, forty of their own words and two links beyond the generated ones; the strict check asks for a source they added. A claim now replaces the stub section instead of contradicting it, and a second entry on the same day joins that heading. `vibe undo <n>` un-claims a stop, hands the XP back and drops the claim from the note, and `vibe done --force` on a finished stop says so and changes nothing. `vibe scores` says there are no scores yet instead of raising, in both forms. Generated vault notes carry a hash of what vibe wrote, so a rebuild, a switch to grow mode and back never overwrite a note the learner edited, and the library never overwrites a camp note. One name: the state follows `vibe.toml` while it holds the placeholder, and `vibe name` writes both and rebuilds the vault. Skills are counted once in workstream 2, the hint keeps its `[[links]]` and names the file as it is spelled on disk, `vibe vault build` counts the folder, `vibe status` congratulates a finished campaign and points at the next island, expert and god run pytest without colour, `vibe theme` and the docs separate the camp from the product, `vibe news --help` names both files, the toolbelt reads Obsidian as installed, and two dead links (git RelNotes, the dotfiles placeholder) are real links again. In the onboarding terminal, Play goes through the same path as `vibe play`, the news button runs `vibe news` only, and the tests button is greyed in a camp with one line saying why.
- The game no longer crashes on the Roadmap, a stop or the inn prompt when WebGL failed before the island set a world; a progress reset keeps the chosen character and play mode; the setup guide escapes the name. Expert and god difficulty work in a camp: expert runs the learner's `workspace/**/test_*.py`, god adds the vault lint (the product keeps its own gates). `vibe news` in a camp writes `.vibe/news.json` instead of a fourth top-level folder. `vibe new --name` also sets the learner's name in `vibe.toml`. `vibe new` reports when git could not commit (and refuses `--github` without a commit), survives a package without the skills tree, prints the real path, and copies the template inside the package-resources context. Remaining `data/`, `sql/` and `python/` mentions moved to `workspace/` in AGENTS.md, CLAUDE.md, two skills, the personas, the cookbook, two game notes and the vault; `env.example` names `VIBE_NAME` and is synced into the template.

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

[Unreleased]: https://github.com/tpetedb/vibe-map/compare/v0.9.0...HEAD
[0.9.0]: https://github.com/tpetedb/vibe-map/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/tpetedb/vibe-map/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/tpetedb/vibe-map/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/tpetedb/vibe-map/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/tpetedb/vibe-map/compare/v0.4.1...v0.5.0
[0.4.1]: https://github.com/tpetedb/vibe-map/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/tpetedb/vibe-map/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/tpetedb/vibe-map/compare/v0.1.0...v0.3.0
[0.1.0]: https://github.com/tpetedb/vibe-map/releases/tag/v0.1.0
