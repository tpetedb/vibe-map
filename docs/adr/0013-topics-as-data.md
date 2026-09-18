# ADR 0013: A topic of the tech tree is one TOML file in a pack, not a row in a Python list

Status: Accepted, 2026-09-18

## Context

The tech tree was one Python list, `T` in `vibemap/tech.py`: fifty-four eight-tuples of strings, sixteen hundred lines, with a second dictionary (`CATEGORY`) placing each id on a shelf at a depth. Everything downstream reads that list: `tools/regen_tree.py` writes the vault notes, the tree the game embeds and `docs/ROADMAP.md`; `vibemap/campaign.py` turns it into `TechNode`s for the CLI and the vault; the game's tree screen and the dashboard read the generated JS.

That shape held while one person wrote the whole tree in one sitting. It stops holding the moment content is written in parallel. Three content packs and a roadmap composer start at once, and a tuple in a shared list means every author edits the same sixteen-hundred-line file, every pull request conflicts with every other, a topic cannot be reviewed on its own, the position of a field is its only name, and nothing can be validated: a missing history, a link to a topic that does not exist and a shelf that is a typo all produce a tree that is quietly wrong rather than a failure.

A topic is also about to gain fields the tuple has no room for: sources with a date of check, prerequisites, an estimated time, and a hands-on exercise with a folder in the workspace and a check spec.

The content rule the packs are written under makes this sharper. Every factual sentence has to be traceable to a URL that was fetched while writing, with the date it was read recorded. That is data about data, and it belongs next to the sentence it justifies.

## Decision

The tree moves into `vibemap/data/topics/`: `tree.toml` (the ages, the shelves, the depths), and one folder per pack with a `pack.toml` and one `<id>.toml` per topic. `vibemap/topics.py` is the loader and the schema (pydantic); `vibemap/tech.py` keeps its public surface (`T`, `AGES`, `CATEGORIES`, `DEPTHS`, `CATEGORY`, `category()`) and is now built from what the loader returns, so nothing downstream changed.

**TOML, not JSON.** A topic is mostly long prose that quotes commands: `git commit -am "why"`, `just --dump --dump-format json`, backticks around a flag, apostrophes in ordinary English. In JSON every one of those double quotes is escaped, there are no multi-line strings and no comments, so the author edits an escaped line and the reviewer reads a diff of escapes. TOML's literal strings (`'''...'''`) take quotes, backslashes and backticks verbatim, a basic string covers the short keys, and a comment above a key survives. Python 3.12 reads TOML with `tomllib` in the standard library, so the choice adds no dependency. TOML has no writer in the standard library, which is fine: the only thing that writes a topic is `tools/new_topic.py`, and it writes from a template string, which is how a scaffold should work anyway.

**A pack is a folder.** `pack.toml` gives it a title, a blurb, the shelf it mostly lives on, maintainer notes and a `topics` list that is the reading order. Packs load by their `order` then their id, so the order is stable; a file the pack does not list still loads, after the listed ones and by id, so a topic dropped into the folder is never ignored in silence. A topic's `pack` is the folder it sits in and may not be written as a key.

**Everything wrong fails loudly, with the file name.** A duplicate id, an unknown shelf, an unknown age, an unknown depth, a link or a prerequisite that names no topic, a file whose `id` is not its file name, a pack that lists a file it does not have, and any key the schema does not know are all a `ValueError` naming the file. `tests/test_topics.py` holds the rest: every source is a URL, a topic written under the content rule carries a date of check and at least three sources, a hands-on names a check kind that exists in `vibemap/artifact_checks.py`, and no file still carries a scaffold marker.

**The migration is proved by byte-identical output.** `tools/regen_tree.py` and `tools/build.py` produce exactly the same `tools/generated/notes.js`, `tools/generated/tree.js`, `docs/ROADMAP.md`, `docs/RESOURCES.md` and `game/vibe-map.html` before and after the move. That was the acceptance test for this change and it is the reason nothing else in the repository had to be touched.

**One seam was added while moving.** A topic's prose may be split into `summary` and `for_agents`; the tree joins them back into one paragraph. It exists because the agent-facing half of a long topic is what a reader skips and what an agent needs, and the joined text is identical to what the tuple held.

## Consequences

- A topic is a reviewable unit. A pull request that adds one touches one new file and one line of `pack.toml`, so three content packs can be written at the same time without a single conflict.
- The schema is the contract for the content packs. A field that is not in `vibemap/topics.py` does not exist, and a topic that does not validate does not load, so a pack cannot half-land.
- Fifty-four small files are read at import of `vibemap.tech`. They are cached for the process and add a few milliseconds to a CLI command, which is well under the cost of importing pydantic.
- The camp ships the packs: the files live under `vibemap/data/`, so an installed `vibe` carries them and `vibe topics` works in any camp, with no checkout.
- `vibemap/tech.py` stays as the name everything imports, which means there are two words for the same thing for a while (the tree and the topics). That is deliberate: renaming the imports is a change with no content in it, and it would have made this diff impossible to review against the byte-identical bar.
- Prose in TOML is one long line per field. Editors soft-wrap it; a diff of a changed sentence is a diff of the whole paragraph. The alternative, hard-wrapped multi-line strings, would put line breaks into the text itself, which the game and the vault would then render.
