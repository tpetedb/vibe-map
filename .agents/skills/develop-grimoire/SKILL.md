---
name: develop-grimoire
description: Develop, review and improve Project Grimoire (the game in game/grimoire.html, the CLI, skills, docs, tech tree). Use for any change request, bug, review, refactor, new world, new workstream, new tech note, or "make it better" on this product.
---
# Develop Grimoire

Read `HANDOVER.md` first, every session. It has the architecture and the priority list.

## Loop for any change

1. If HANDOVER.md Task 0 (sokrypton/aoe study) is not done, do it first. Restate the request in one line and name the files you will touch. Ask if tone or scope is unclear (the jargon is intentional).
2. Edit. For the game: keep it one file, no CDN, three.js embedded, functions on `window`, state in `S`, layout in normal flow. Use `mat()` or `fixColors()` for new 3D materials. Run `fixColors(scene)` after building new geometry.
3. Test with Playwright headless (`tools/tests/*.py`; `--use-gl=swiftshader` for WebGL). Zero page errors is the bar. Take a screenshot and look at it.
4. Regenerate, never hand-edit: tech notes and ROADMAP come from `tools/tech.py` via `python3 tools/regen_tree.py`.
5. Commit locally with a one-line message. Do not push.
6. End with one line: what changed.

## Review checklist ("review it and make it better")

- Every link is https and points to an official doc page; open three at random.
- Every workstream section has: pairing, concept, do-this with commands, definition of done, Rolinda's question, docs line.
- Mobile: no fixed overlays besides the title; sheet and vault scroll natively; HUD fits 360px wide.
- Performance: shadow map 2048 or lower; under 300 draw calls; no per-frame allocations in `animate()` beyond the existing Vector3s.
- Copy: no em-dashes; Rolinda plain, everyone else jargon; no dated claims without a year.
- Accessibility: buttons have text, canvas has aria-label, Enter works on the roadmap buttons.

## Adding things

- World: add to `WORLDS` (palette, sky, land blobs, plots, way, river, extras). Test by `setWorld('id')` in the console.
- Workstream: new section `s-N`, entry in `CH`, `SAY[N]`, `building(N)`, pairing, vault note, syllabus section, CLI `WS`. Eight is the current count; bump every `8`.
- Tech note: edit `tools/tech.py`, regenerate, paste `tools/generated/*.js` into the game.
