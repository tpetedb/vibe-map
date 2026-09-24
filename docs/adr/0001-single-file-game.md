# ADR 0001: The game is one HTML file, built from src/ by concatenation

Status: Accepted, 2026-09-16. Amended 2026-09-23: the build finds its modules by name (#162, #178), and the paths below are the ones on main.

## Context

The game is the learner's first artefact of the evening: workstream 1 ends with "a playable single-file game". The learner double-clicks a file. There is no server, no package manager and no build tool on their side yet. The game must also work offline (a venue without wifi is a real case) and deploy to GitHub Pages in workstream 7 without configuration.

The game draws its 3D island with three.js. Loading three.js from a CDN keeps the file small but ties every run to the network and to a third party's URL staying alive. Embedding it makes the file about 1 MB.

The source outgrew one file for editing: state, scene, character, buildings, worlds, input, animation, the sheet, notes, the vault, minigames, the finale, sync and boot. An agent editing a file of that size makes slow, risky edits. sokrypton/aoe (ADR 0002) showed that plain script files in a fixed load order, without a bundler, hold up at 33k lines.

## Decision

We will ship the game as one file, `game/vibe-map.html`, with three.js, Motion and d3-force embedded from `src/vendor/`, no CDN and no external request.

We will keep the source in `src/`: `head.html` (with the placeholders the build fills, one of them from `icon.svg`), `style.css`, `body.html`, `errors.js` (the error panel, in a script of its own ahead of the vendored libraries), `src/config/*.js` (the source configuration a fork edits) and the modules in `src/game/`, then in `src/galaxy/` when that folder exists. `tools/build.py` concatenates them inside one function and injects the campaign from `vibemap/data/campaign.json`, the generated tech notes and tree from `tools/generated/`, and the journey values from `config/camp.toml` as `CONFIG`. Concatenation is the whole build: no bundler and no minifier of our own code, so the output stays readable.

A module's file name is its place in the load order: two digits, an optional letter that splits a number, a dash, lowercase words (`MODULE_NAME` in `tools/build.py`). The build sorts each folder by that name and moves `game/90-boot.js` to the very end, after every folder, because boot calls functions at load that read constants other modules declare. Inside the one wrapping function a function declaration is ready before any line runs, but a `const` or `let` stays uninitialized until its own line has run, so a read that comes earlier throws. Any other file in a module folder stops the build.

We will never hand-edit `game/vibe-map.html`. `tools/build.py --check` fails when the file differs from a fresh build, and the test suite runs that check.

## Consequences

- Double-click works, offline works, Pages works, and an evening does not depend on a CDN being up.
- The built file is over 1.5 MB and its diffs are unreadable; review `src/` diffs instead. The vendored three.js is one fixed version, upgraded by replacing the file.
- There is no module system. Files share globals in load order (config first, then state, boot last), so the file name is part of the design: a new module is a new file whose number puts it after everything it reads, and nothing else is registered. The build refuses a misnamed file rather than leaving it out in silence.
- `game/index.html` is the learner's own file from workstream 1; nothing may depend on its contents.
- Every edit ends with `just build`. Forgetting it fails `just verify`, which is the point.
