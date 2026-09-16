# Handover for the next agent

You are picking up Vibe Code Camp (internal codename Project Grimoire): a one-evening course in building with AI coding agents, packaged as a 3D browser game, a syllabus, a template repo and a terminal companion. Owner: Tom. Learner: Lotte (Chief of Staff, plays games, likes spreadsheets). Character: Rolinda (knows nothing about AI, insufferable about wine). Tone: over-the-top corporate jargon on top of real, useful content; Rolinda speaks plainly. No em-dashes anywhere.

Read in this order: this file, `AGENTS.md`, `docs/ROADMAP.md`, then `.agents/skills/develop-grimoire/SKILL.md` before touching the game.

## What exists

| Path | What | State |
|---|---|---|
| `game/grimoire.html` | The game. Single file, ~1 MB, three.js r128 embedded (no CDN). 4 worlds, 8 workstreams, physics, vault with 111 notes and a tech tree, progress import/export. | Works on desktop Chrome and Android Claude app. Not yet verified on iOS Safari. |
| `docs/SYLLABUS.md` | Written version of the course, incl. tech tree. Also published as a Claude artifact. | Complete; the pre-flight and per-workstream lesson blocks were written in another session, review for consistency. |
| `docs/ROADMAP.md` | The tech tree, generated from `tools/tech.py` (see below) | Generated |
| `docs/RESOURCES.md` | Curated links | Curated by hand, all official pages |
| `grimoire/cli.py` | Terminal companion: status, done, map, export, import, scores | Tested, stdlib only |
| `.agents/skills/*` | 7 skills in the Agent Skills standard | Written, not yet exercised by an agent |
| `.claude/agents/scorekeeper.md`, `.claude/settings.json` | Subagent and backup hook | Hook shape follows the docs; verify it fires on your Claude Code version |
| `data/`, `sql/`, `python/` | Sample data, 3 DuckDB queries (tested), 1 script (tested) | Done |
| `scripts/setup.sh` | Mac setup | Read it; it installs things |

## How the game is built (important before editing)

The HTML was produced by scripted edits, so some structure is unusual:
- Everything is in one `<script>` IIFE after the embedded three.js. Public functions are attached to `window` (start, openSheet, claim, openVault, openTree, setWorld, nextWorld, exportProgress, importProgress, ...).
- State `S` is persisted in `localStorage["grimoire3"]`. Shape: `{name, done:[1..8], rolls, versions, bridges, date, wine, world, creature}`.
- Worlds are the `WORLDS` config; `buildWorld(id)` rebuilds the whole scene. Add a world by adding a config, no other code.
- Buildings are `building(k)` cases 1..8; plots come from `W.plots`; the path is a Catmull-Rom through `W.way`.
- The vault is `NOTES` (id -> {t, md}); notes are a tiny Markdown subset: `#` title, `-` bullets, `**bold**`, `[label](url)`, `[[wikilink]]`, trailing `#tags`. The tech tree is `AGES`/`TREE`. Both the 32 tech notes and `docs/ROADMAP.md` are generated from `tools/tech.py`; edit that, regenerate, do not hand-edit both.
- Layout: the 3D stage is a normal block at the top, everything else flows below (no fixed layers; Android webviews scroll badly otherwise).
- Colours: materials go through `mat()` which converts sRGB to linear; use it, or run `fixColors()` on anything you add.

## What Tom has to do himself (the agent cannot)

1. `gh auth login` once, so the agent can create Pages and PRs.
2. Approve every install the install-grimoire skill proposes; it will not install without a yes.
3. Push. The agent commits locally and never pushes; run `git push` when a batch looks good.
4. On GitHub: Settings, tick "Template repository"; Settings, Pages, source main / root (or let the agent run `gh` and confirm).
5. Test on your phone after each Pages deploy and paste what you see (screenshot or error text) back to the agent.
6. Confirm the go-live dates in the finale picker and Lotte's actual free evenings.
7. Decide the licence question in task 0 below before any code from sokrypton/aoe is reused.

## Task 0: learn from sokrypton/aoe (Age of Epochs II)

Tom wants the ideas from https://github.com/sokrypton/aoe folded into this product. It is a browser Age-of-Empires-style game in plain JavaScript (`js/`, sprites, `classic.html`, `tests/`, `MULTIPLAYER.md`), live at https://ageofepochs.com, and it has a `CLAUDE.md` that describes how its author works with Claude Code on a game of this kind.

Do this, in order:
1. `gh repo clone sokrypton/aoe ../aoe` and read `CLAUDE.md`, `README.md`, `MULTIPLAYER.md`, the `tests/` folder and the top of `js/`. Write a one-page note `docs/AOE-STUDY.md`: architecture, how sprites and the map are done, how tests are run, how multiplayer works, and every convention in its CLAUDE.md worth adopting here.
2. Check the licence. If the repo has no LICENSE file, nothing is copied; only ideas and structure are reused. Say so in the study note.
3. Adopt into `AGENTS.md`/`CLAUDE.md` the conventions from its CLAUDE.md that fit (test loop, file layout, how to describe a game change), and say which you skipped and why.
4. Propose, do not build yet: a "classic view" of the campus as a 2D sprite map in the style of aoe alongside the 3D view, and a multiplayer mode where Tom, Lotte and Rolinda walk the same island (aoe's MULTIPLAYER.md is the reference). Estimate size, list risks, ask Tom which to build.
5. If Tom says yes to either, build it as a separate `src/` module with its own tests, behind a toggle, without breaking the single-file output.

## Known gaps and suggested next work, in priority order

1. Repo URL is set in the game (`id="tplink"`, https://github.com/tpetedb/vibe-map). Clone: `git clone git@github.com:tpetedb/vibe-map.git`.
2. iOS Safari test of the game (tap-to-move, joystick, sheet scrolling, WebGL memory with 2048 shadow map; drop to 1024 if it stutters).
3. Split `game/grimoire.html` into `src/` files with a tiny build (concat) so it is editable, while keeping the single-file output. Keep three.js embedded.
4. Fact-check the 32 tech notes against a primary source each and add the citation to the note's Docs line. Dates are believed correct but were written from memory.
5. Exercise every skill with Claude Code once and fix what does not trigger (descriptions decide triggering).
6. Add `tests/`: a Playwright smoke test that starts the game, imports a code, claims a workstream, opens the vault (the previous session's tests are in `tools/tests/`).
7. Content: Lotte's actual game will replace `game/index.html` on the night; nothing should depend on its contents.
8. The dates in the finale picker are placeholders; confirm with Tom.

## Ground rules

- Never push to remotes, never rewrite history, never run DDL. Tom does remote git himself.
- Do not add dependencies to the CLI. The game stays one file with no CDN.
- Ask before changing the tone of any copy; the jargon is intentional.
- End every change with one line: what changed.
