# Writing a topic

The tech tree is data: one TOML file per topic, in a pack. This page is how to
add one, what the schema allows, and the bar a topic has to clear before it
lands. Why it is TOML and why it is one file per topic: `docs/adr/0013-topics-as-data.md`.

## Where things live

```
vibemap/data/topics/
  tree.toml          the ages (the XP ladder), the shelves, the depths
  core/
    pack.toml        the pack: title, blurb, shelf, maintainer notes, reading order
    unix.toml        one topic
    bash.toml
vibemap/data/places/
  bell-labs.toml     one place a topic can have happened at
```

`vibemap/topics.py` is the loader and the schema. `vibemap/tech.py` turns what it
loads into the lists the generators read, so a new topic reaches the roadmap, the
vault notes and the game as soon as you run `just tree`. `vibemap/places.py` is
the same pair for places, and it is what an origin's `place` is checked against.

## Add one

```sh
uv run python tools/new_topic.py pack cloud --title "The cloud pack" --shelf ship
uv run python tools/new_topic.py topic cloud s3 --title "Object storage" --shelf ship --age castle --depth 2
```

The scaffolder writes the file with the keys in the right order, today as the
date of check, and `TODO` markers where you have to write. It also adds the id
to the pack's reading order. Then, in this order:

1. Write the words, from the official documentation (see the content rule below).
2. `just tree` regenerates `tools/generated/`, `docs/ROADMAP.md` and `docs/RESOURCES.md`.
3. `just build` rebuilds the game, and `uv run python tools/sync_fork_source.py` the
   copy a fork carries.
4. `uv run pytest tests/test_topics.py` validates every topic against the schema.
5. `uv run vibe topic <id>` reads it back the way a learner sees it.

Never hand-edit anything under `tools/generated/`, `docs/ROADMAP.md` or
`docs/RESOURCES.md`: they are outputs.

## The content rule

Every topic is written from the project's own official documentation, fetched
while writing. Nothing from memory.

- Every factual sentence is traceable to one of the URLs the topic cites.
- Versions, flags and commands are exactly as the docs give them.
- `checked` records the day you read those pages. Move it when you read them again.
- Three to six sources. The first ones are what a learner should read; a
  `Source: ...` label marks a citation for a claim in the history.
- No em dashes and no emoji anywhere (`uv run python tools/checks.py style`).

## What a topic has

| Key | Required | What it is |
|---|---|---|
| `id` | yes | The file name without `.toml`, lowercase, no spaces. |
| `title` | yes | What the vault note is called. It must survive `vault.safe_title()` unchanged: no `/`, no `:`, no `\| * ? " < >`, or every wikilink to it dies. |
| `age` | yes | The rung of the XP ladder: `dark`, `feudal`, `castle`, `imperial`, `future`. |
| `shelf` | yes | A shelf id from `tree.toml`, the group the topic is read in. |
| `depth` | yes | 1 basics, 2 working knowledge, 3 deep. |
| `summary` | yes | What it is and when you would reach for it. |
| `for_agents` | no | The agent-facing half of the prose. The tree joins it to the summary with one space. |
| `history` | yes | The mental model and the real history, five sentences, each one sourced. |
| `try_it` | yes | The smallest real thing, five minutes, on a laptop. |
| `sources` | yes | `[[sources]]` blocks with `label`, `url` and an optional `checked` date. |
| `origins` | while the pack is migrated | `[[origins]]` blocks: where this happened (below). |
| `unlocks` | no | Topic ids this one leads to. An unknown id fails the load. |
| `prerequisites` | no | Topic ids to read first. Also checked. |
| `checked` | new topics | The day the sources were read. |
| `minutes` | no | How long the topic takes, end to end. |
| `hands_on` | no | The exercise (below). |
| `covered_elsewhere` | no | `true` for a topic whose prose is a handwritten vault note. It then carries no prose at all. |

Prose goes in a literal string, so nothing needs escaping:

```toml
summary = '''A justfile is a file of named commands you run with `just RECIPE`.'''
```

## Where it happened

A topic sits somewhere: a lab, a company, a university, a network. That is data
too, with the same bar as a quote (ADR 0010), and it is what the Galaxy view
puts on the map (`docs/GALAXY.md`, ADR 0015).

```toml
[[origins]]
place = "bell-labs"     # a file in vibemap/data/places/; uv run vibe places
year = 1969
what = "A small team of researchers at Bell Labs releases the first version of Unix."
source = "https://ethw.org/UNIX"
primary = true          # exactly one: where the topic lives

[[origins]]             # any others are echoes: the same topic, somewhere else
place = "a-standards-body"
year = 2025
what = "Apple's macOS 26.0 Tahoe is registered as a UNIX 03 product on 29 August 2025."
source = "https://www.opengroup.org/openbrand/register/brand3725.htm"
```

Rules, all of them checked:

- The source is https, it was opened while writing, and the page says what the
  line says: the year, the actor and what happened. The town may instead come
  from the place file's own source only when that source locates the actor or
  event there at the relevant date, or from a dated first-party page that does,
  listed under `[[sources]]` and named in the comment above the origins. A
  current contact address does not prove an earlier event's town, building or
  exact address. If no such page supports
  the historical location, leave the origin out and record the gap, or use an
  appropriate abstract place supported by the event source.
- `year` is a year the page gives, never the year you read the page. A page
  that carries the fact but no date needs a second page that carries the date,
  and then the line says what that page says.
- `what` is one line, plainly what happened, not why it matters. A judgement
  ("widely influential"), a reason the source does not give, and anything
  inferred from an address line all belong to somebody else, not to us.
- Exactly one origin is `primary`. Two, or none, is refused by file name.
  A topic cannot have two origins at the same place. `year` must be a TOML
  integer, not a quoted number, boolean or float.
- A topic with no origin at all still loads: packs are sourced one at a time.
  `uv run python -c "from vibemap import places; print(places.problems(packs=['core']))"`
  lists what is still missing, one sentence per file. `shelves=[...]` narrows it
  to one shelf.

If a place is missing, name the requested place and its primary source on the
work order's issue. The content team assigns its place file to an order that
owns `vibemap/data/places/`; a topic order does not edit around its ownership.
An assigned place writer uses this format:

```toml
# vibemap/data/places/bell-labs.toml
id = "bell-labs"                   # the file name, without .toml
name = "Bell Labs, Murray Hill"
kind = "lab"                       # lab, company, university, city, network,
                                   # cloud, orbit, standards, foundation
region = "us-east"                 # one of the regions in vibemap/places.py
era = "mainframe"                  # the arm of the map: mainframe, personal,
                                   # open-source, data, agents
globe = "earth"                    # earth, datacentre or cloud
lat = 40.684                       # only on the earth globe, and within a
lon = -74.402                      # quarter of a degree of the real address
look = "campus"                    # the diorama kit: campus, tower, lab, hall,
                                   # racks, nebula, lanes, station, house, harbour
landmark = "mountain-avenue-plaque"  # one silhouette that stands there, as a
                                   # slug, and never a logo, a wordmark or a
                                   # mascot: a place inherits ADR 0010
source = "https://ethw.org/Milestones:Bell_Telephone_Laboratories,_Inc.,_1925-1983"
```

The place's own source has to carry what the file says about it, the landmark
included: a thing that stands in the next town is a wrong fact, printed by
`vibe places <id>` and drawn on the map. Use `generic-marker` when no physical
landmark is supported. It requests a plain marker, not a claim that an object
stands there. Never model a real building, organisation mark or product.
`look` is a fictional diorama kit, not evidence about the location. City-level
coordinates locate a town, not a historical office or a private home.

An open-source project with no single address is not a guess about an office:
it sits at `the-internet`, the way a hosted service sits at `the-cloud` and a
specification at `a-standards-body`. `uv run vibe places` lists every place and
what comes from it; `uv run vibe places <id>` is one of them.

## The hands-on

Under twenty minutes, runs on a laptop, no cloud account, no paid service, and
checked offline and deterministically.

```toml
[hands_on]
title = "One recipe, run twice"
path = "workspace/topics/justfile"   # optional; the default is workspace/topics/<id>
minutes = 15
done = "just greet prints your name"
check = { kind = "justfile", file = "justfile", recipes = 2, parameter = true }
```

`kind` is one of the kinds in `vibemap/artifact_checks.py` (`script`, `module`,
`justfile`, `dockerfile`, `duckdb`, `fastapi`, `workflow`, `mcp`, `sqlite`,
`sklearn`, `frontmatter`, `files`); the rest of the keys are that kind's spec,
exactly as an artifact writes it. A topic and an artifact are verified by the
same code.

`module` is `script` for an exercise whose library nobody here depends on. It
names the imports it needs and the command that installs them, runs the script
when they are present, and says what to install when they are not, rather than
marking a learner wrong for not having `dbt` on this machine:

```toml
check = { kind = "module", file = "run_dbt.py", modules = ["dbt"], install = "uv add dbt-duckdb", prints = ["ok: True"] }
```

For the learner:

```sh
uv run vibe topic justfile --start      # makes the folder and the stub file
uv run vibe check --topic justfile      # 0 when it passes, 1 when it does not
```

A passing check records the topic in `roadmap_done`, which the vault note shows
as done and the progress code carries as `topics`.

## The review checklist

- [ ] The file is named `<id>.toml` and its `id` matches.
- [ ] The title survives `safe_title()` and is not the title of another topic.
- [ ] Shelf, age and depth exist in `tree.toml` and the depth is honest.
- [ ] Every factual sentence is covered by a cited URL that was fetched today.
- [ ] Exactly one origin is primary, its place exists, and every origin's source
      was opened and says the year, actor and event it claims; its town is
      supported at the relevant date by that page, the place file's source or
      a dated first-party page listed under `[[sources]]`.
- [ ] Three to six sources, all https, each with a label that says what it is.
- [ ] `try_it` is a command a learner can paste, and it works.
- [ ] The hands-on is under twenty minutes, offline, and its check fails before
      the work and passes after it. Both were run.
- [ ] `unlocks` and `prerequisites` name topics that exist.
- [ ] No `TODO` left, no em dash, no emoji.
- [ ] `just tree`, `just build`, `tools/sync_fork_source.py` and
      `uv run pytest tests/test_topics.py` are green.

## Packs

A pack is a folder that is written, reviewed and versioned together.

```toml
id = "core"
title = "The core map"
blurb = '''What the pack covers and who it is for.'''
shelf = "shell"         # the shelf it mostly lives on
order = 0               # packs load by order, then by id
maintainer = '''How this pack is reviewed and what it never does.'''
topics = ["unix", "bash"]
```

`topics` is the reading order, and it is also the order of the roadmap and of
the notes. A file the list does not mention loads after the listed ones, by id.
Two packs may not use the same topic id; the loader refuses it by name.
