---
name: develop-camp
description: Develops, reviews and improves Vibe Code Camp in this repo, meaning the game built from src/, the vibe CLI, the tech tree, the syllabus and these skills. Use for any change request on this product, such as "fix the game", "add a world", "add a workstream", "edit a tech note", "change the copy", "review it and make it better", "make it work on my phone", and before touching more than one file.
---
# Develop Vibe Code Camp

Read `HANDOVER.md` first, every session: architecture, ground rules, priority list. `AGENTS.md` has the conventions, `docs/AOE-STUDY.md` the ones adopted from sokrypton/aoe.

## Where things live

- Game source: `src/` (`src/game/*.js` modules in load order, `src/style.css`, `src/head.html`, `src/body.html`, `src/vendor/three.min.js`). `game/vibe-map.html` is built by `just build` (`tools/build.py`, plain concatenation). Never hand-edit the built file; `just build-check` catches it.
- One source for the game and the CLI: `src/data/campaign.json` (evenings, workstreams, mentors).
- Tech tree: `tools/tech.py`. `just tree` regenerates the notes, the tree JS and `docs/ROADMAP.md`, then rebuilds the game. No pasting.
- CLI: `vibemap/` (`uv run vibe <cmd>`). Tests: `tests/` (`just test`; browser smoke only: `just smoke`).

## Loop for any change

1. Restate the request in one line and name the files you will touch. Ask if tone or scope is unclear (the jargon is intentional; Rolinda speaks plainly).
2. Edit in `src/`, then `just build`. Game rules: one output file, no CDN, three.js embedded, public functions on `window`, state in `S`, layout in normal flow. New 3D materials go through `mat()`; run `fixColors(scene)` after building geometry.
3. Test: `just smoke` (Playwright: Chromium with software WebGL, WebKit as the iPhone proxy; screenshots in `tests/out/`). Zero page errors is the bar. Open a screenshot and look at it. `just test` runs everything; `uv run pytest tests/<file> -k <name>` runs one.
4. Gate: `just verify-quiet` (ruff and tests), `just build-check`, `just tree-check`, `just style-check` (no em dashes, no emoji). Say "done" only after they print OK.
5. Commit locally, one line: what and why. Never push.
6. End with one line: what changed.

## Review checklist ("review it and make it better")

- Every link is https and points to an official doc page; `just links-check`, then open three at random.
- Every workstream section has: pairing, concept, do-this with commands, definition of done, Rolinda's question, docs line.
- Mobile: no fixed overlays besides the title; sheet and vault scroll natively; HUD fits 360px wide.
- Performance: shadow map 2048 or lower; under 300 draw calls; no per-frame allocations in `animate()` beyond the existing Vector3s.
- Copy: no em dashes, no emoji; Rolinda plain, everyone else jargon; no dated claims without a year.
- Accessibility: buttons have text, canvas has aria-label, Enter works on the roadmap buttons.

## Adding things

- World: add a config to `WORLDS` in `src/game/20-worlds.js` (palette, sky, land blobs, plots, way, river, extras); `buildWorld(id)` does the rest. Test with `setWorld('id')` in the console, then `just smoke`.
- Workstream: new section `s-N` in `src/body.html`, entry in `CH` and `SAY[N]` (`src/game/00-state.js`), a `building(N)` case (`src/game/12-buildings.js`), pairing, vault note, syllabus section, and `src/data/campaign.json`. Eight is the current count; bump every `8`.
- Tech note: edit `tools/tech.py`, then `just tree`.
- Diagrams in docs or notes: the mermaid-diagrams skill (palette classDefs, ISO 5807 shapes, a legend).
