# ADR 0015: An experience is a view over one shared core, and where a topic happened is data

Status: Accepted, 2026-09-21

## Context

The game is one way to travel the course: four islands, eight stops each, a walker. Tom asked for a second way, next to it and not instead of it: topics placed where they happened in history, on tiny planets that carry a small dome of the real place at its true spot on a little globe, a ship between them, one line that shows the whole journey, and the islands left exactly as they look today. He also asked that configuration, data, the Python side and the browser side each stay separate. `docs/GALAXY.md` is the full proposal with its research, critique and accessibility requirements.

Three things in the repository decide what is cheap and what is not:

- Progress lives in `S` per stop and per topic, never per scene. The progress code, `state.json`, the quests and the vault have no idea what the player was looking at.
- The scene code and the rest are in one folder, `src/game/`, in one load order. Nothing states which modules are "the island view" and which are "the game", so a second view has nothing to plug into.
- 65 of 70 topics have a sourced `history` field, but the place in it is prose. A view cannot put "Postgres 1986 (Berkeley)" on a map without guessing, and ADR 0010 does not allow guessing about real organisations.

## Decision

**An experience is a view, and there can be more than one.** An experience registers under an id (`islands`, `galaxy`) and implements one small contract: `build`, `dispose`, `tick`, `goTo`, `where`, `listing`. Everything else (state, saving, the progress code, the sheet, the vault, search, settings, chat, the dashboard) is core and may not reference a mesh or an experience by name. Dependencies point one way: data, then the Python side and the build, then configuration, then core, then the experience. An experience writes progress only through core.

**One progress, and the choice of view is a preference.** `S.experience` is new, defaults to `islands`, starts from `experience` in `config/camp.toml`, and stays out of the progress code: a code says what was done, not how it was looked at. No format version changes, because no existing field changes meaning.

**Where a topic happened is data, with a source.** A topic gains `[[origins]]` (place, year, one-line claim, source link, one marked primary). A place is one file of its own under `vibemap/data/places/` (kind, era, region, latitude and longitude when the place is on Earth, which globe carries it, a look, a landmark, a source). `vibemap/places.py` loads and validates them the way `topics.py` does: an unknown place, a missing source or a topic with two primary origins or none fails loudly with the file name, while a topic that carries no origin yet still loads and is reported by `places.problems()`. The build injects them as `PLACES`. The CLI reads the same data (`vibe places`, origins in `vibe topic`).

**`listing()` is part of the contract, not an extra.** A canvas is one opaque image to assistive technology, so every experience must return what it shows as plain data, and the non-3D twin (the journey list, the place list) is built from it first. What the canvas can do, the list can do.

**The islands are frozen by test before the seam is cut.** Golden screenshots of the four islands land first. The contract is then introduced by naming what exists, with no file moved; moving files into `src/core/` is a later, separate change that the same screenshots have to survive.

**The game stays one file** (ADR 0001). Galaxy is procedural geometry from a small kit, no textures, no models, under 80 KB added. Only the active experience builds a scene; switching disposes the other through `discard()`.

## Consequences

- A third experience (a plain 2D map, a text-only course) costs a view, not a game. That is the real return on the seam, and the list twin is already most of a text-only course.
- Core modules that reach into the scene today (`openCh` moving the camera, the minimap, "walk me there") have to go through `goTo` and `where`. Finding them is phase 2's work and is where the refactor can go wrong; the golden screenshots are the guard.
- Seventy topics need origins sourced by hand, pack by pack. A claim about a real company or lab is checked against its link before it merges, the same bar ADR 0010 set for quotes. The loader makes a gap a failing test instead of an empty planet.
- The smoke test runs one script against every registered experience by id. Something that cannot be tested through the contract does not belong in an experience.
- `fork_source` and the template carry the new folders, so `tools/sync_fork_source.py` and the build's file list change with phase 2, not before.
- Accessibility rules bind the design, not only the result: travel is autopilot, every zoom level is also a button, and with reduced motion every camera move is a cut (`docs/GALAXY.md`, section 6).
- Open, to decide when version zero exists: whether Galaxy is offered on the title screen, and whether the star map replaces the vault's graph view or sits next to it.

## Amendments

**2026-09-21, on acceptance: a place is one file, not a row in `places.toml`.** The proposal put every place in one `vibemap/data/places.toml`. Five research orders source the packs at the same time, and a shared file is a shared conflict: exactly the reason ADR 0013 gave for making a topic one file in a pack. Places are therefore one `vibemap/data/places/<id>.toml` each, with the same schema, and the loader reads the folder. The eras moved with them, from `tree.toml` into `vibemap/places.py`, because an era places a place and not a topic: a lab sits in one arm of the map for its whole life while the topics made there span decades.
