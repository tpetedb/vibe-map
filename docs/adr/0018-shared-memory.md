# ADR 0018: The teams share one board room and one memory, read by one command at session start

Status: Accepted, 2026-09-24. The memory half is superseded by DECISION #193 section 4 (the board, 2026-09-24): the memory is `memory.jsonl` plus a derived `index.json`, written through `tools/board.py memory add|search|index` under one lock, and no memory server ships. The room, the reader, the digest, the lint and the session-start hooks below still stand. What follows is kept as the record of the server choice and its runner-up.

Superseded by: DECISION #193 section 4 (issue #193; the decision file is `.git/board/harness/DECISION-final.md` in the shared board folder)

## Context

Since 2026-09-23 two teams build this repository at once: Team Claude (Claude Code) and Team Codex (Codex CLI and app). There are up to about eight sessions at a time, spread over dozens of worktrees. Each new session re-read `AGENTS.md`, `docs/BRIEF.md`, the forum issue #95, progress logs and private memory notes. Some of those notes were Claude-only and invisible to Codex. The result was the same tokens spent again, and two teams with two different pictures of the work. Tom asked for a forum where the agents stay aligned (issue #96) and for shared memory that cuts tokens without losing quality. Nothing in it may cost him money or need his keys.

The board (Codex gpt-6-astra and Claude Fable 5.1) decided the shape in its local room between 21:00Z and 21:43Z on 2026-09-23. The candidates were researched against their first-party repositories and docs that same day:

| Candidate | Local, no key | Claude and Codex | Verdict |
|---|---|---|---|
| Official MCP memory server (`@modelcontextprotocol/server-memory`, MIT, modelcontextprotocol/servers) | yes, one JSONL file, no daemon | both, over stdio | chosen |
| Basic Memory (basicmachines-co/basic-memory, AGPL-3.0) | yes | both | runner-up |
| mem0 / OpenMemory, Graphiti, Letta | no: an LLM key, Docker or a server | through MCP | rejected |
| claude-mem | a background model on every session | Claude only | rejected |
| Serena | yes | both | code retrieval, not memory |
| beads, mcp_agent_mail | yes | both | coordination; the board room does that |

Sources:

- https://github.com/modelcontextprotocol/servers/tree/main/src/memory
- https://github.com/basicmachines-co/basic-memory
- https://code.claude.com/docs/en/mcp
- https://code.claude.com/docs/en/hooks
- https://code.claude.com/docs/en/permissions
- https://learn.chatgpt.com/docs/config-file/config-reference
- https://learn.chatgpt.com/docs/hooks

The source of the pinned version (2026.8.31) shows how the server writes. Every change reloads the whole file, edits it and renames a new file into place. There is no lock between processes, so two sessions writing at the same moment lose one of the writes.

## Decision

**The room.** The short-term channel is `ROOM.md` in `<git common dir>/board/`. It is shared by every worktree and never committed.

- It is append-only.
- Each entry is written in one write, under a lock.
- Each entry's id is derived from its own text.
- `tools/board.py` (standard library only, importable from Python 3.9) reads and appends it. `work/BOARD.md` is the one-page protocol.
- Checked-out and landed orders are worked out from `tools/work.py`. The manager who lands an order also types one LANDED entry, the note for issue #95, and it is mirrored only when `tools/work.py` confirms it.
- Heavy job slots are explicit reservations. A scan of running processes only cross-checks them.
- DECISION and verified LANDED entries are mirrored to issue #95 by a manager, never by a hook.

**The memory.** The long-term memory is the official MCP memory server, pinned to 2026.8.31, with one `memory.jsonl` next to the room.

- Both clients load it from tracked files: Claude from `.mcp.json`, Codex from `.codex/config.toml`. Both go through `scripts/memory-mcp.sh`.
- The script starts the server behind `tools/board.py memory-serve`. That process takes a lock around every change the server makes, from request to response, so writes from any number of processes are serialized. The lock is held for at most 10 seconds per write (the real write takes milliseconds); after that the client gets an error saying the write may not have happened, and the lock is free for every other session. It also refuses `read_graph` and the whole-graph resource.
- Both configs deny `read_graph` as well: `permissions.deny` in `.claude/settings.json` and `disabled_tools` in `.codex/config.toml`.
- Entities are named `kind:slug`.
- Each observation is dated, tagged with its team and carries a source pointer. It is at most 200 characters.
- The caps are 300 entities and 8 observations per entity. `just memory-lint` enforces them and refuses secret-looking lines.

**Session start.** A SessionStart hook for Claude (`.claude/settings.json`) and one for Codex (`.codex/hooks.json`) run the same `python3 tools/board.py read`. Both clients get the same text, in this order:

- the held slots
- a memory digest: every rule and gotcha and the ten newest decisions, in under 6,000 characters
- the newest room entries, one line each, at most 30
- the checked-out orders
- the landed orders

The whole text stays under 9,000 characters: Claude Code gives a model at most 10,000 characters of hook output and only a 2,000-character preview beyond it. The digest comes before the long lists, so what the budget cuts is older room lines and checked-out orders, never the memory.

`.codex/hooks.json` also carries the four work-order hooks Codex already ran from an untracked copy (the edit guard, the data backup, SubagentStop and Stop), the same as `.claude/settings.json`; a test keeps them equal, so tracking the file takes nothing away from Codex.

Camps get none of this. `tools/sync_template.py` leaves out the hook, the deny rule and the skill.

**The switch condition.** Move to Basic Memory when the graph reaches about 300 entities, or when a question cannot be answered by a substring search on one keyword.

## What changed with DECISION #193 section 4

The board reviewed the memory as part of the cross-provider harness (issue #193) and kept the record format, not the server:

- No MCP memory server publishes a measured coding gain (the board's facts F117), the reference servers are described by their maintainers as educational, not production-ready (F102, https://github.com/modelcontextprotocol/servers), and command-line tools are more context-efficient than MCP (F114, https://code.claude.com/docs/en/costs).
- `scripts/memory-mcp.sh`, the pinned server, `board.py memory-serve`, `.mcp.json`, `[mcp_servers.memory]` and the `read_graph` deny rule were removed. The entities seeded through the server stay in `memory.jsonl` and pass the lint.
- `board.py memory add` takes the same lock the proxy took, reads the file, renames a new one into place and rebuilds `index.json` (id, order, topic, owner, status, next action, from the records and `work/orders/`) before it lets go. A test runs two CLI writers at once and loses nothing.
- Codex writes the board only when launched with `--add-dir` and the absolute common dir's board, which `just codex` passes; the tracked `.codex/config.toml` names no writable root, since a relative one breaks every shell tool in a linked worktree (amended A2).
- Search is agentic first: `board.py memory search`, a substring match on every word (F111, https://claude.com/blog/building-agents-with-the-claude-agent-sdk). Semantic search waits for a measured need; its measured gain is on repositories of 1,000 files and more (F112, https://cursor.com/blog/semsearch), and this one is far below that.
- The switch condition below (Basic Memory) is replaced by that rule.

## Consequences

The consequences as recorded when the server was chosen:


- A session starts with at most 9,000 characters about the state of the work, the same for both teams, instead of re-reading the logs. Anything left out of the digest is one `search_nodes` call away. Most of the saving comes from the digest and from the missing whole-graph read, not from the server.
- Both files live in `.git`. They are not backed up by a push, and deleting the clone deletes them. Anything that must outlive the clone goes into a tracked doc, and the graph points at it.
- The first start of the server fetches the pinned package from npm. After that, npm's cache serves it offline.
- The memory's search is a case-insensitive substring match on one string. The naming convention (a kind prefix, one keyword) is what makes it usable, and its limits are the switch condition above.
- Why not Basic Memory now:
  - its licence is AGPL
  - it needs a pre-release dependency
  - it registers projects in machine-local config, which breaks "the tracked files are the setup"
  - it has open SQLite writer-blocking issues
- The Codex hook, and Codex's trust of the project config, are granted through the client's own prompts. The Codex reviewer of the order proves both on the installed client. If the Codex app starts MCP servers outside the repository, the documented fallback is a machine-local `codex mcp add memory -- sh <repo>/scripts/memory-mcp.sh`.
- `AGENTS.md` gets a one-line pointer to `work/BOARD.md` in a follow-up, once the order that currently holds `AGENTS.md` has landed.
