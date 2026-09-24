---
name: shared-memory
description: How any agent of either team reads and writes the shared memory of this repository (one memory.jsonl and a derived index.json for every worktree, Claude and Codex, written only through tools/board.py) and the board room next to it. Use at the start of work in an unfamiliar area, before writing down a lesson, a gotcha, a rule or a decision another session will need, when asked "what do we know about", "remember this", "is there a gotcha for", or when posting to the board.
---
# Shared memory and the board room

Three shared files sit in `$(git rev-parse --path-format=absolute --git-common-dir)/board/`. None is ever committed.

- **`ROOM.md`** is the room: append-only and short-term. Slots, handoffs, questions, checkpoints and decisions go here.
- **`memory.jsonl`** is the memory: facts a later session would otherwise have to work out again.
- **`index.json`** is derived from the memory and `work/orders/`: one row per entity and per order (id, order, topic, owner, status, next action). Never edit it; `memory add` and `memory index` rebuild it.

There is no memory server. Every read and write goes through `tools/board.py`. `work/BOARD.md` is the protocol; this skill covers the day-to-day use.

## Reading

1. **Main sessions** already have the digest: the SessionStart hook ran `python3 tools/board.py read`. It holds every `rule:` and `gotcha:` entity and the ten newest `decision:` entities.
2. **Subagents** get no hook. Before opening docs about an unfamiliar area, search once:
   `just memory-search gotcha:` or `python3 tools/board.py memory search "sync-main"`
   - The search is case-insensitive and matches substrings. Several words must all match, so use one or two words, never a sentence.
   - It also finds the indexed orders, with their status and next action.
   - `--full` prints every observation and the entity's relations.
3. Do not `cat` the memory file into your context. Search it.

## Writing

Write only at a checkpoint or a landing, and only a fact another session would otherwise have to rediscover.

```sh
just memory-add gotcha:gh-pr-merge-auto-mode "gh pr merge is denied in auto mode; hand Tom the command" claude "PR #192"
# or, with the options:
uv run python tools/board.py memory add <kind:slug> "<one fact>" --team claude|codex|board --src "<pointer>" [--replace "<old text>"] [--relate type=kind:slug]
```

1. Search first. `memory add` appends to an entity that exists and creates one that does not.
2. **Names** have the form `kind:slug`. The kind is one of `rule`, `gotcha`, `decision`, `contract`, `component` or `team`, and `entityType` is set from it.
3. **Each observation** is stored as one line, at most 200 characters:
   `YYYY-MM-DD [team:claude] <one fact>, src: <path|PR #n|ADR n|room entry id>`
   - The date is today in UTC. Point to the source; never copy its text.
   - An entity holds at most 8 observations.
4. **To change a fact,** add the new one with `--replace "<text in the old one>"`. The old observation is dropped in the same write.
5. **Relations** are `owns`, `depends_on`, `supersedes` and `documented_in`, and they point only at entities that exist: `--relate supersedes=decision:old-one`.
6. A write that would break the lint (a bad name, a ninth observation, a secret-looking line, a relation to nothing) is refused whole and nothing is written.
7. When a board DECISION changes how people work, also store it as a `decision:` or `rule:` entity whose `src:` is the room entry id or issue #95.

`memory add` and `memory index` need Python 3.11, because the index reads work orders through `tools/work.py`: run them with `uv run`. Search and lint run on any `python3`.

## Never store

- secrets, tokens, `.env` contents, or anything from a path the deny lists block
- personal data or scores
- code or text copied from a tracked file: point to the file instead
- transient status, such as who is working on what right now: that belongs in the room
- anything `AGENTS.md` already says

## The room

| To do this | Run |
|---|---|
| Read the room and the digest | `just board` |
| Post an entry | `just board-say "<model>, effort <e>, <role>, team:<claude\|codex>" "CHECKPOINT: ..."` |
| Take a heavy job slot (a browser battery, or anything over ten minutes) | `just board-slot take <job> "<who>"` |
| Free the slot when the job ends | `just board-slot free <job> "<who>"` |

Kinds: DECISION (the board only), QUESTION, HANDOFF, CHECKPOINT, SLOT, and LANDED from the manager who landed an order. The reader works out which orders are checked out and which have landed from `tools/work.py`, so never post a claim. A typed `LANDED <order-id>` is the note for issue #95, and `mirror` posts it only when the reader's landed column agrees.

## When it misbehaves

| Symptom | Fix |
|---|---|
| `memory add` says it needs Python 3.11 | Run it with `uv run python tools/board.py ...` or `just memory-add`. |
| Codex cannot write the board | Start it with `just codex`, which adds `--add-dir "$(git rev-parse --path-format=absolute --git-common-dir)/board"`; no writable root is tracked. |
| Codex shows no digest in a worktree | Its project hooks are off there: `just codex-trust` once, then approve them in `/hooks`. Until then `just codex` puts the digest in the first prompt. |
| A write seems lost | `just memory-lint`, then search again. Writes are serialized, so report it on the board. |
| The memory is getting big | At about 300 entities, fold the details into a doc and leave a pointer. |
