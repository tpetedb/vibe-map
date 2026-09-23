---
name: shared-memory
description: How any agent of either team reads and writes the shared memory of this repository (the official MCP memory server, one graph for every worktree, Claude and Codex) and the board room next to it. Use at the start of work in an unfamiliar area, before writing down a lesson, a gotcha, a rule or a decision another session will need, when asked "what do we know about", "remember this", "is there a gotcha for", or when posting to the board.
---
# Shared memory and the board room

There are two shared files, both in `$(git rev-parse --path-format=absolute --git-common-dir)/board/`. They are never committed.

- **`ROOM.md`** is the room: append-only and short-term. Claims, slots, handoffs, questions and decisions go here.
- **`memory.jsonl`** is the memory: a searched graph of facts that a later session would otherwise have to work out again.

`work/BOARD.md` is the protocol. This skill covers the day-to-day use.

## Reading

1. **Main sessions** already have the digest: the SessionStart hook ran `python3 tools/board.py read`. It contains every `rule:` and `gotcha:` entity and the ten newest `decision:` entities.
2. **Subagents** get no hook. Before opening docs about an unfamiliar area, run one `search_nodes` with a single keyword or a prefix, such as `search_nodes("gotcha:")` or `search_nodes("board.py")`.
   - The search is a case-insensitive substring match on one string, so do not send it a sentence.
3. **To look something up by name**, use `open_nodes(["rule:no-em-dashes"])`.
4. **Never call `read_graph`.** It dumps the whole graph into your context. Both client configs switch it off and `tools/board.py` refuses it.

## Writing

Write only at a checkpoint or a landing, and only a fact another session would otherwise have to rediscover.

1. Run `search_nodes` first.
   - If the entity exists, call `add_observations`.
   - Otherwise call `create_entities` with `entityType` set to the kind.
2. **Names** have the form `kind:slug`. The kind is one of `rule`, `gotcha`, `decision`, `contract`, `component` or `team`. For example: `gotcha:gh-pr-merge-auto-mode`, `component:tools/board.py`.
3. **Each observation** is one line, at most 200 characters:
   `YYYY-MM-DD [team:claude] <one fact>, src: <path|PR #n|ADR n|room entry id>`
   - Point to the source. Never copy its text.
   - An entity holds at most 8 observations.
4. **To change a fact,** call `delete_observations` on the old line, then `add_observations` with the new one. The server has no edit tool.
5. **Relations** are `owns`, `depends_on`, `supersedes` and `documented_in`, and they only point at entities that exist.
6. When a board DECISION changes how people work, also store it as a `decision:` or `rule:` entity whose `src:` is the room entry id or issue #95.
7. Run `just memory-lint` after a batch of writes.

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

Kinds: DECISION (the board only), QUESTION, HANDOFF, CHECKPOINT, SLOT. The reader works out which orders are checked out and which have landed from `tools/work.py`, so never post those by hand.

## When it misbehaves

| Symptom | Fix |
|---|---|
| The server is missing in Claude | `claude mcp get memory`. Approve the project server once. |
| The server is missing in Codex | `codex mcp list`. The project must be trusted. |
| A write seems lost | `just memory-lint`, then search again. Writes are serialized, so report it on the board. |
| The graph is getting big | At about 300 entities, fold the details into a doc and leave a pointer. ADR 0018 names the switch to Basic Memory. |
