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
```

`vibemap/topics.py` is the loader and the schema. `vibemap/tech.py` turns what it
loads into the lists the generators read, so a new topic reaches the roadmap, the
vault notes and the game as soon as you run `just tree`.

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

`kind` is one of the kinds in `vibemap/artifact_checks.py` (`script`, `justfile`,
`dockerfile`, `duckdb`, `fastapi`, `workflow`, `mcp`, `sqlite`, `sklearn`,
`frontmatter`, `files`); the rest of the keys are that kind's spec, exactly as an
artifact writes it. A topic and an artifact are verified by the same code.

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
