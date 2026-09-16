# ADR 0001: The game is one HTML file, built from src/ by concatenation

Status: Accepted, 2026-09-16

## Context

The game is the learner's first artefact of the evening: workstream 1 ends with "a playable single-file game". The learner double-clicks a file. There is no server, no package manager and no build tool on their side yet. The game must also work offline (a venue without wifi is a real case) and deploy to GitHub Pages in workstream 7 without configuration.

The game draws its 3D island with three.js. Loading three.js from a CDN keeps the file small but ties every run to the network and to a third party's URL staying alive. Embedding it makes the file about 1 MB.

The source outgrew one file for editing: state, scene, character, buildings, worlds, input, animation, the sheet, notes, the vault, minigames, the finale, sync and boot. An agent editing a file of that size makes slow, risky edits. sokrypton/aoe (ADR 0002) showed that plain script files in a fixed load order, without a bundler, hold up at 33k lines.

## Decision

We will ship the game as one file, `game/grimoire.html`, with three.js and motion embedded from `src/vendor/`, no CDN and no external request.

We will keep the source in `src/`: `head.html`, `style.css`, `body.html`, `src/game/*.js` in numbered load order, `src/data/campaign.json`. `tools/build.py` concatenates them and injects the campaign JSON, the generated tech notes and tree, and the constants from `grimoire.toml`. Concatenation is the whole build: no bundler and no minifier of our own code, so the output stays readable.

We will never hand-edit `game/grimoire.html`. `tools/build.py --check` fails when the file differs from a fresh build, and the test suite runs that check.

## Consequences

- Double-click works, offline works, Pages works, and an evening does not depend on a CDN being up.
- The built file is about 1 MB and its diffs are unreadable; review `src/` diffs instead. The vendored three.js is one fixed version, upgraded by replacing the file.
- There is no module system. Files share globals in load order (state first, boot last), so `GAME_ORDER` in `tools/build.py` is part of the design and a new file must be added there.
- `game/index.html` is the learner's own file from workstream 1; nothing may depend on its contents.
- Every edit ends with `just build`. Forgetting it fails `just verify`, which is the point.
