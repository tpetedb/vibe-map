---
name: develop-camp
description: Develops, reviews and improves Vibe Code Camp in this repo, meaning the game built from src/, the vibe CLI, the tech tree, the syllabus and these skills. Use for any change request on this product, such as "fix the game", "add a world", "add a workstream", "edit a tech note", "change the copy", "review it and make it better", "make it work on my phone", and before touching more than one file.
---
# Develop Vibe Code Camp

Read `AGENTS.md` first, every session: the file map, the ways of working, the test loop and the code style. `docs/MAINTAINERS.md` has the three zones and how a change travels between them, `docs/BRIEF.md` what was asked for and why, `docs/AOE-STUDY.md` the conventions adopted from sokrypton/aoe. Open issues are the priority list.

## Where things live

- Game source: `src/` (`src/game/*.js` modules in load order, `src/style.css`, `src/head.html`, `src/body.html`, `src/config/`). `src/vendor/` holds three bundles and their licences, three.js, Motion and d3-force, copied in and never edited. `game/vibe-map.html` is built by `just build` (`tools/build.py`, plain concatenation). Never hand-edit the built file; `just build-check` catches it. `vibemap/data/fork_source/` is a mirror of `src/` that the installed command carries: run `uv run python tools/sync_fork_source.py` after any change under `src/`.
- One source for the game and the CLI: `vibemap/data/campaign.json` (evenings, workstreams, mentors).
- Tech tree: one TOML file per topic under `vibemap/data/topics/<pack>/`, scaffolded by `tools/new_topic.py`; `vibemap/tech.py` is only the shape the generators read. `just tree` regenerates the notes, the tree JS and `docs/ROADMAP.md`, then rebuilds the game. No pasting. See `docs/TOPICS.md` and `docs/adr/0013-topics-as-data.md`.
- CLI: `vibemap/` (`uv run vibe <cmd>`). Tests: `tests/` (`just test`; browser smoke only: `just smoke`).

## Loop for any change

1. Restate the request in one line and name the files you will touch. Ask if tone or scope is unclear (the jargon is intentional; Rolinda speaks plainly).
2. Edit in `src/`, then `just build`. Game rules: one output file, no CDN, the vendor bundles embedded, public functions on `window` (`window.__S()` is the state and `window.__debug()` the view the browser tests read, and they exist for tests only), state in `S` with the view derived from it. New 3D materials go through `mat()`; run `fixColors(scene)` after building geometry.
3. Test: `just smoke` (Playwright: Chromium with software WebGL, WebKit as the iPhone proxy; screenshots in `tests/out/`). Zero page errors is the bar. Open a screenshot and look at it. `just test` runs everything; `uv run pytest tests/<file> -k <name>` runs one.
4. Gate: `just verify-quiet` (ruff and tests), `just build-check`, `just tree-check`, `just style-check` (no em dashes, no emoji). Say "done" only after they print OK.
5. A change under `src/`, `vibemap/` or `tools/` adds one fragment `changelog.d/<slug>.<type>.md` (`changelog.d/README.md` has the types); CI refuses the pull request without it, and `CHANGELOG.md` is written by a release, never by a branch.
6. Commit in logical steps, one line each: what and why. Push a branch and open a pull request; `main` only takes green, up-to-date pull requests. `just sync-main` catches the branch up.
7. End with one line: what changed.

## Review checklist ("review it and make it better")

- Every link is https and points to an official doc page; `just links-check`, then open three at random.
- Every workstream section has: pairing, concept, do-this with commands, definition of done, Rolinda's question, docs line.
- Mobile: no fixed overlays besides the title; sheet and vault scroll natively; HUD fits 360px wide.
- Performance: shadow map 2048 or lower; under 300 draw calls; no per-frame allocations in `animate()` beyond the existing Vector3s.
- Copy: no em dashes, no emoji; Rolinda plain, everyone else jargon; no dated claims without a year.
- Accessibility: buttons have text, canvas has aria-label, Enter works on the roadmap buttons.

## Adding things

- World: add a config to `WORLDS` in `src/game/20-worlds.js` (palette, sky, land blobs, plots, way, river, extras); `buildWorld(id)` does the rest. Test with `setWorld('id')` in the console, then `just smoke`.
- Workstream: new section `s-N` in `src/body.html`, entry in `CH` and `SAY[N]` (`src/game/00-state.js`), a `building(N)` case (`src/game/12-buildings.js`), pairing, vault note, syllabus section, and `vibemap/data/campaign.json`. Eight is the current count; bump every `8`.
- Tech note: edit the topic's TOML file under `vibemap/data/topics/<pack>/` (`tools/new_topic.py` scaffolds a new one, or a whole pack), then `just tree`.
- Diagrams in docs or notes: the mermaid-diagrams skill (palette classDefs, ISO 5807 shapes, a legend).
