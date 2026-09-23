# The board

Two teams build this repository at once, Team Claude and Team Codex. The board coordinates them. This page covers who sits on the board, what it decides, what it never overrides, and how every session reads and writes the two shared files. The tool is `tools/board.py`, the memory how-to is the skill `shared-memory`, and the reasons are in ADR 0018.

## Who sits on it

- **Codex gpt-6-astra**, general manager of Team Codex.
- **Claude Fable 5.1**, general manager of Team Claude.

The board has sat since 2026-09-23, at Tom's request, and it coordinates every running agent of both teams. A DECISION stands once both members have agreed to it in the room. Tom is the owner: whatever he says overrides the board.

## What it decides

- **Scope and sequence.** Which order goes to which team, what waits on what, and handoffs between teams.
- **Review swaps.** Who reviews whom. The reviewer always comes from the other team, and a board member never reviews their own work.
- **Machine use.** The four heavy local jobs across both teams (the host's budget) and which model does which kind of work.
- **The harness itself.** Changes to it go through an order like any other change.

A DECISION entry records what was decided, the two options considered, who proposed it, who agreed, and which order or PR it changes.

## What it never overrides

- `just work-check <id>`, which is what done means for an order.
- `just work-accept <id>`: a current review that accepts, plus every sign-off the order needs.
- CI on the pull request's exact head, and branch protection on `main`.
- Tom.

The board can narrow an order, defer part of it or stop it. It cannot merge unmet criteria and it cannot skip a gate.

## The room: short-term, append-only

The room is `ROOM.md` in `$(git rev-parse --path-format=absolute --git-common-dir)/board/`. It is shared by every worktree and never committed. Each entry has a header line, `## <UTC time> [<model>, effort <e>, <role>, team:<claude|codex>]`, followed by the text. Its id is derived from the entry itself, so every reader shows the same id. Entries are never edited or deleted.

| Command | What it does |
|---|---|
| `just board` | The last 30 entries, the checked-out orders, the landed orders, the held slots, a process cross-check and the memory digest. |
| `just board-say "<who>" "<KIND>: <text>"` | Appends one entry as a single write, under the room's lock. |
| `just board-slot take\|free <job> "<who>"` | Reserves or frees a heavy job slot. |
| `python3 tools/board.py mirror` | Posts DECISION and verified LANDED entries to issue #95, once each. A manager runs this, never a hook. |

- **Kinds.** Each entry opens with one kind: DECISION (the board only), QUESTION, HANDOFF, CHECKPOINT or SLOT. CLAIM and LANDED are derived from facts rather than typed:
  - An order is **checked out** when its branch is checked out in some worktree. That is not proof that an agent is working on it.
  - An order has **landed** when its accepting review is on `origin/main`.
- **Slots.** A slot is taken only by an explicit `SLOT take job=<id>` entry and freed only by `SLOT free job=<id>`. A process scan can show that an unknown job is running, but it never takes or frees a slot. Unknown stays unknown. Any browser battery is a heavy job, and so is any other job expected to run longer than ten minutes.
- **Session start.** At the start of every session, the SessionStart hooks (`.claude/settings.json` and `.codex/hooks.json`) run `python3 tools/board.py read`. Claude and Codex see the same text. A hook only reads local files: it never contacts GitHub and never fails a session.

## The memory: long-term, searched

The memory is `memory.jsonl` in the same folder. It is the official MCP memory server (`@modelcontextprotocol/server-memory@2026.8.31`), started by `scripts/memory-mcp.sh` for both clients. `tools/board.py` sits in front of the server. It holds a lock around every write, so two sessions writing at once lose nothing, and it refuses the whole-graph read.

The room is where work happens now: claims, slots, handoffs, questions. The memory holds what a later session would otherwise have to work out again. When a DECISION or LANDED entry changes how people work, it also becomes a `decision:` or `rule:` entity that cites the room entry or issue #95.

- **Reading.**
  - The session-start digest has every `rule:` and `gotcha:` entity and the ten newest `decision:` entities.
  - Before opening docs about an unfamiliar area, run one `search_nodes` with a single keyword or a prefix such as `gotcha:`. Subagents do the same, because they get no session-start hook.
  - Never call `read_graph`. Both configs switch it off and the proxy refuses it.
- **Writing.** Write only at a checkpoint or a landing, and only a fact another session would otherwise have to rediscover.
  - Run `search_nodes` first. If the entity already exists, use `add_observations`.
  - To change a fact, delete the old observation, then add the new one.
- **Names.** Every name has the form `kind:slug`. The kind is one of `rule`, `gotcha`, `decision`, `contract`, `component` or `team`, and `entityType` is the kind. For example, `gotcha:gh-pr-merge-auto-mode` or `component:tools/board.py`.
- **Observations.** Each observation has the form `YYYY-MM-DD [team:<claude|codex|board>] <one fact>, src: <path|PR #n|ADR n|room entry id>`. It is at most 200 characters, and each entity has at most 8.
- **Relations.** The relation types are `owns`, `depends_on`, `supersedes` and `documented_in`. A relation may only point at an entity that exists.
- **Caps.** The memory holds at most 300 entities. Over that, fold the details into a doc and leave a pointer. At about 300 entities, or when substring search stops finding things, it is time to switch to Basic Memory (ADR 0018).
- **Never store:**
  - secrets, tokens, `.env` contents, or anything from a path the deny lists block
  - personal data or scores
  - text copied from a tracked file (point to the file instead)
  - transient status (that goes in the room)
  - anything `AGENTS.md` already says

`just memory-lint` checks the caps, the name and observation format, secret-looking lines and relations that point nowhere.

## Setup on a machine

- **Claude Code.** Approve the `memory` server from `.mcp.json` once when prompted, then run `claude mcp get memory`.
- **Codex.** Trust the project, then run `codex mcp list`. It should show `memory` enabled and `read_graph` disabled. Codex asks you to trust the SessionStart hook in its own prompt; grant it there and bypass nothing.
- **Camps.** Camps get none of this: `tools/sync_template.py` leaves out the hook, the deny rule and the skill.
