# Study: sokrypton/aoe (Age of Epochs)

What a browser Age-of-Empires clone written with Claude Code can teach Vibe Code Camp. Studied on 2026-09-16 from a fresh clone of https://github.com/sokrypton/aoe at commit `b8f3346`. Live game: https://ageofepochs.com.

## Licence, first

The repo ships a `LICENSE` file: **GNU GPL version 2 or later** (the README says so too, "the same license Blender uses"). Vibe Code Camp is MIT. GPL code copied into an MIT project makes the combined work GPL, so:

- **Nothing is copied.** No JavaScript, no `sprites.png`, no CSS, no test harness code. Everything below is ideas and structure, which copyright does not cover.
- The Python test harness in `tests/` and the build script in `tools/` were written from scratch for this repo.
- If Tom ever wants to lift actual code, the game would have to become GPL-2.0-or-later. That is Tom's call, not the agent's.

## Architecture in one paragraph

Plain JavaScript, no bundler, no framework, no build step: 31 files under `js/` (33k lines) loaded by synchronous `<script src>` tags in a fixed order, with `boot.js` last so it can enable the Start button only when everything above it has run. Two thin HTML shells (`index.html` for phone and desktop, `classic.html` for the AoE2 look) share one engine; all shared markup lives in `js/page-shell.js`, and a `window.UI_VARIANT` flag picks the skin, so the two views cannot drift apart. The engine is split hard into **simulation** (`core`, `logic`, `ai`, `entities`, `pathfinding`, `commands`, `lockstep`, `determinism`, `save`, `loop`) and **viewer** (`render*`, `ui`, `audio`, `input`). The sim never reads viewer state; the viewer never writes sim state except through `submitCommand`. Everything the sim does is also runnable headless in `tools/sim.html`, which is what makes seeded, diffable, all-AI matches possible.

## Map and sprites

- **The map** is a `MAP x MAP` grid of tile records `{t: terrain, res, occupied}`. `genMap()` builds it procedurally from a seed (bases, forests, gold, berries, wildlife) with distances scaled from the original 60x60 board. A scenario loader can bypass generation with a blank grass base.
- **Projection** is classic 2:1 isometric: tile width 64, height 32, `toIso(x,y) = ((x-y)*32, (x+y)*16)` and its exact inverse. One function, `mapToScreen`, is the only world-to-screen seam; renderers may not re-spell it inline.
- **The camera is quantised** to whole pixels before drawing. Every drawable rounds its own position, so a fractional camera makes stationary things vibrate by a pixel while panning. Rounding once, at the seam, keeps the scene rigid and makes hit tests agree with what was drawn.
- **Units and buildings are drawn procedurally** on a 2D canvas with paths, gradients and per-age equipment tables. There are only ten `drawImage` calls in the whole renderer. `sprites.png` (2048x2560, an 8x10 grid of 256px cells) is the **HUD icon sheet**, referenced from CSS via `background-position` rules generated at startup from one `SPRITE_CELLS` table. A Python script (Pillow) grows and re-sheets it.
- **Fog** is a per-tile 0/1/2 level (unexplored, explored, visible), memoised per building until fog changes.
- **No per-frame allocation**: scratch arrays and pools are module-level and reused every frame. Draw order uses depth proxies so a unit can sort between the back and front halves of a gate.
- `tools/render-parity.js` hashes rendered pixels and diffs them against a git ref: a viewer refactor must move zero pixels.

## How tests are run

`tools/run-tests.sh` is the pre-commit battery, cheapest failure first:

1. `node --check` on every JS file (syntax).
2. `stats-audit.js`: informational diff against a reference table, never gates.
3. `behavior-tests.js`: PASS/FAIL assertions on game mechanics, driven headlessly through Playwright on `tools/sim.html`. Each section gets a fresh page; an in-page helper `window.__T.ok(name, condition)` collects results; the driver prints `PASS  [section] name` lines and exits 1 on any failure. `grep=<name>` runs one section.
4. `hud-tests.js`: command plus DOM assertions on the real `index.html`.
5. Sim smoke: one seeded 14k-tick self-play match run twice; findings must be empty and the two checksums equal.

The Playwright harness (`tools/lib/harness.js`) is a static file server over the repo plus a browser launch with channel fallbacks (system Chrome first, `playwright-core`, no browser download) and `key=value` argument parsing. `mp-tests.js` drives live WebRTC and is excluded from the battery because it needs the network.

Rules the author wrote down after being bitten: run the suite closest to the blast radius while iterating and the full battery before committing; test the real entry point (the click path), not just the mechanism; a stashed tree makes `git stash` comparisons use the wrong baseline; profile before optimising and compare medians of three or more runs; a behaviour-neutral refactor must reproduce the seed checksum exactly.

## How multiplayer works

Two generations, and the history matters because the first is the right size for us.

**Generation 1 (the deleted `MULTIPLAYER.md`, recovered from git history).** Host-authoritative over PeerJS/WebRTC using PeerJS's free public signalling server. The host runs the simulation; the guest sends clicks and renders the world state the host broadcasts about 15 times a second. Payload went from 290 KB to 1.8 KB per sync by never sending fog (each client derives it), sending the map once and then only changed cells, rounding coordinates, and deflating every message with the browser's `CompressionStream`. Sequence numbers plus a `request-full-sync` message recover from gaps; a protocol version handshake refuses mismatched builds (GitHub Pages caching makes stale-versus-fresh real); the host rewrites its URL to `?host=<id>` so a crashed host can reclaim its id and recover the world from the guest's mirror.

**Generation 2 (current `js/lockstep.js`).** Deterministic lockstep with bounded rollback. Every peer runs the full simulation from the same seed and the same tick-stamped command stream. The sim never waits; a command that arrives late rewinds to the nearest snapshot (a ring of 30 snapshots, one every 10 ticks, about five seconds) and re-simulates. Topology is a host-relay star: guests talk only to the host, the host forwards commands stamped with the sender's seat, and seat equals team. Identity is a persistent browser token bound to a seat, so a reconnect lands on the same seat. Checksums are exchanged only for ticks older than the rollback window, and a mismatch is a loud desync alarm. The whole design rests on the determinism rules: sim-only random and trig, no wall clock, stable sorts with an id tiebreak, and every new sim field added to the hash.

The one place aoe breaks its own no-dependency habit: `peerjs` and `qrcode-generator` come from unpkg.

## Conventions from its CLAUDE.md, and what we do with them

Adopted into `AGENTS.md` (2026-09-16):

| Convention | Why it fits Vibe Code Camp |
|---|---|
| A **file map** table: file, what it owns | Our game is about to be split into `src/`; the map is how the next agent finds things. |
| Comments state **constraints and why**, tersely; never change-narration, datelines, war stories or line-number references | The game was produced by scripted edits and has almost no comments; this is the rule for the ones we add. |
| **One helper per concept**, never re-spell the raw check at call sites | `mat()`, `fixColors()`, `onLandW()` already are this; make it explicit. |
| **Test loop**: targeted while iterating, the full battery before a commit, exit non-zero on any failure, cheapest failure first | Our `tests/` folder and the `uv run pytest` battery follow the same order. |
| **Test the entry point, not the mechanism** | The smoke test clicks the real buttons; it does not call `claim()` directly. |
| **Versioned formats fail loudly**, no back-compat shims | The progress code between CLI and game gets a version field. |
| **Sim versus viewer**: state is data, the view is derived | For us: everything persisted lives in `S`, the DOM and the 3D scene are rebuilt from it, never the other way round. |
| **Thin shells, shared markup in one place** | The classic view proposal below reuses the same sheet, vault and HUD markup. |
| **Profile first, compare medians** | Applied when the shadow map or draw call budget is touched. |
| Reference values and fidelity decisions live in a doc, not in code comments | This file, and the citation on every tech note. |

Skipped, and why:

- **Determinism rules** (sim random, sim trig, hashing new state): there is no shared simulation to keep in lockstep. Adopt only if the multiplayer proposal below is built with lockstep, which it should not be.
- **The TPS / T30 timebase**: a walking character driven by a three.js clock delta does not need authored tick durations.
- **Statistical batch rules** (40 runs per arm): there is no AI to balance.
- **AoE2 fidelity tables**: domain-specific.
- **GoatCounter analytics** in the HTML shells: a privacy decision for Tom, not a convention.

## Proposals (not built; Tom decides)

### A. Classic view: the campus as a 2D map alongside the 3D island

What: a second renderer, canvas 2D, drawing the same `WORLDS` config (land blobs, plots, path, river, extras) as an isometric or top-down map in the Age of Epochs style, behind a "Classic" toggle next to the world picker. Same `S`, same sheet, same vault, same HUD. Input produces a target position exactly as tap-to-move does today, so the walking logic is shared.

- Size: 600 to 900 lines in `src/game/classic.js`, one tile painter per plot type, one evening of agent work plus a test that renders each world and hashes the canvas.
- Value: runs where WebGL does not (old iPads, locked-down laptops), far cheaper on a phone battery, and it visibly ties the tech tree's Age of Empires metaphor to the map.
- Risks: two renderers to keep in sync (mitigation: both read only `WORLDS` and `S`; the 2D view starts read-only and gains tap-to-move second); the single file grows by about 40 KB; art quality is the real cost, procedural 2D takes iteration.

### B. Multiplayer: Tom, Lotte and Rolinda on the same island

What: three walkers sharing one island. There is no shared simulation to synchronise, only positions, names and claims, which makes aoe's lockstep the wrong tool and its generation-1 design the right size: one peer hosts, every peer broadcasts its own position about ten times a second, claims are relayed by the host, and Rolinda is a scripted walker run by the host.

- Size: 300 to 500 lines in `src/game/net.js` plus a lobby panel in the sheet, one evening of agent work; the test needs two browser contexts.
- Dependency: PeerJS (MIT) must be **embedded**, not loaded from a CDN, to keep the one-file rule; about 90 KB minified. Signalling uses PeerJS's public server or Tom's own `peerjs --port` on a Raspberry Pi.
- Risks: corporate networks block WebRTC (no mitigation besides a relay); the public signalling server has no uptime promise; three walkers on one island tempts a chat feature, which is where scope goes to die.
- Not recommended before the classic view: it is fun, but nothing in the course needs it.

Recommendation: build A if either; skip B until the first evening has happened.

## Sources

- https://github.com/sokrypton/aoe (CLAUDE.md, README.md, tools/README.md, js/, git history of MULTIPLAYER.md)
- https://ageofepochs.com
- https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
