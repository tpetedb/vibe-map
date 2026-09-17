# ADR 0006: Configuration has three nested levels, each flat inside

Status: Accepted, 2026-09-17

## Context

`vibe.toml` at the root of a camp held everything: the learner's name, persona and difficulty next to the repository URL of the product, the shadow map and the build defaults. A beginner opening it could not tell which lines were about them and which were about the machinery, and there was nowhere at all to put "how the game itself is built", because the game's world scale, island radius and palette were literals spread through `src/game/*.js`.

The course teaches separation of concerns and then teaches building the builder. A single flat settings file contradicts both lessons on the first screen a learner opens. It also blocked the thing the brief asks for: a learner who wants to change the game, not just their journey through it, had no file to change and no copy of the game to change it in.

Nesting is the part that needs a decision, because it is easy to nest too far. Three levels is the smallest number that separates the three questions a reader actually asks: how is this repository built and checked, how is the product made, and who am I in it.

## Decision

Three levels, nested, each flat inside. Nothing is nested twice.

- **Repository configuration** stays where the tools demand it: `pyproject.toml`, `justfile`, `.github/`, `.claude/`, `.agents/`. These are never moved, because uv, just, GitHub Actions and Claude Code look for them by name at the root. Documented, not relocated.
- **Source configuration** is how the product is made. It is split in two because the product is two things with two build paths. The game's settings are `src/config/00-config.js`, which `tools/build.py` concatenates ahead of the game modules and which therefore has to be JavaScript the browser reads with no build step of its own. The CLI's settings are data under `vibemap/data/` (`campaign.json`, `resources.md`, `obsidian.json`, the camp template) plus `vibemap/tech.py`, which ship inside the installed package and are read by Python. One folder could not serve both: a file cannot be both a `<script>` the browser executes and package data `importlib.resources` finds in a wheel.
- **Journey configuration** is `config/camp.toml` in a camp: name, persona, difficulty, provider, theme, vault mode, finale dates. Every knob has a default, so the file is optional and deleting it falls back rather than breaking.

`config/camp.toml` replaced `vibe.toml` for two reasons. It puts the journey level in a folder named for what it is, so the root of a camp shows `workspace/`, `vault/` and `config/` and the learner can name the three zones from the listing alone. And it leaves the root free for the repository level, which is where the tools insist on being. The old name is still read as a camp marker and as configuration for one release, and every command prints one line saying so and naming the new path. At the end of that release it is retired: a camp that still has only `vibe.toml` is told to move the file rather than having its settings quietly ignored, because a settings file that is read by nobody is worse than one that is missing.

The product checkout carries a `config/camp.toml` of its own, so it is a valid camp as well as the product. The played instance, the play-through tool and the tests all need a camp to run in, and a checkout that is not one would need a second code path in `vibemap/project.py` for "the repository" next to "a camp".

## Consequences

- `docs/CONFIG.md` is the contract, one table per level, in the form "to change X, edit Y, then run Z". A setting that is not in that table is a bug in the layout, not in the document.
- `vibemap/project.py` finds a camp by `config/camp.toml`, then `vibe.toml`, then a built `game/vibe-map.html`, and `VIBE_HOME` overrides all three. One resolver, used by every command.
- The fork is what makes the source level reachable. A learner cannot edit `src/config/` in the product, because the product is not theirs and is not on their machine; `vibe fork` puts a copy with its own `src/config/` in `workspace/forks/vibe-map/`, and the production island's forking stop is where they first open it. Without the fork the middle level would be a level only maintainers ever see, which would make the lesson a diagram instead of an exercise.
- `tools/build.py` has to resolve every input relative to the folder holding it, or to `--root DIR`, because it now runs in two places: the product and a fork.
- Splitting the source level in two is a real cost. Someone adding a setting has to decide whether it belongs to the game or to the CLI, and `docs/CONFIG.md` and `docs/MAINTAINERS.md` both have to say so. The alternative, one settings file loaded by both, would mean a build step for the CLI or a parser for TOML in the browser, and the game is one file with no CDN.
- The deprecation is time-boxed on purpose. One release of a warning is short enough that the two names never become two supported layouts.
