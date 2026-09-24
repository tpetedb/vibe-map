# The board

Two teams build this repository at once, Team Claude and Team Codex. The board coordinates them. This page covers who sits on the board, what it decides, what it never overrides, and how every session reads and writes the two shared files. The tool is `tools/board.py`, the memory how-to is the skill `shared-memory`, the history is ADR 0018 and the current memory design is DECISION #193 section 4.

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
| `just board` | The held slots, a process cross-check, the memory digest, then the room's newest entries and the checked-out orders as far as the session-start budget goes, and the landed orders. `just board --full` prints the last 30 entries whole and every checked-out order. |
| `just board-say "<who>" "<KIND>: <text>"` | Appends one entry as a single write, under the room's lock. |
| `just board-slot take\|free <job> "<who>"` | Reserves or frees a heavy job slot. |
| `python3 tools/board.py mirror` | Posts DECISION and verified LANDED entries to issue #95, once each. A manager runs this, never a hook. |

- **Kinds.** Each entry opens with one kind: DECISION (the board only), QUESTION, HANDOFF, CHECKPOINT, SLOT or LANDED. Nobody types a claim, and the reader never takes a typed LANDED on trust; both columns are derived from facts:
  - An order is **checked out** when its branch is checked out in some worktree. That is not proof that an agent is working on it.
  - An order has **landed** when its accepting review is on `origin/main`.
  - The manager who lands an order types one `LANDED <order-id>` entry, the note that goes to issue #95. `mirror` posts it only when the derived landed column agrees.
- **Slots.** A slot is taken only by an explicit `SLOT take job=<id>` entry and freed only by `SLOT free job=<id>`. A process scan can show that an unknown job is running, but it never takes or frees a slot. Unknown stays unknown. Any browser battery is a heavy job, and so is any other job expected to run longer than ten minutes.
- **Session start.** At the start of every session (every start source each client names: startup, resume, clear, compact, and fork in Claude Code), the SessionStart hooks (`.claude/settings.json` and `.codex/hooks.json`) run `python3 tools/board.py read`. Claude and Codex see the same text. A hook only reads local files: it never contacts GitHub and never fails a session.
  - The whole text stays under 9,000 characters, because Claude Code gives a model at most 10,000 characters of hook output and only a 2,000-character preview beyond that. The slots and the memory digest come first; the room's newest entries and the checked-out orders fill what is left.
  - A bare `python3` may be the 3.9 that macOS ships. The reader still prints the room, the slots and the digest there; the checked-out and landed columns read unknown, because `tools/work.py` needs 3.11.

## The memory: long-term, searched

The memory is `memory.jsonl` in the same folder, with `index.json` derived from it. There is no server (DECISION #193 section 4): every read and write goes through `tools/board.py`, which costs a session less context than an MCP server and needs nothing installed.

| Command | What it does |
|---|---|
| `just memory-search <word>` | Entities and indexed orders that hold every word, one line each; `--full` on `board.py memory search` prints every observation and relation. Any `python3`. |
| `just memory-add <kind:slug> "<fact>" <team> "<src>"` | Appends one observation, creating the entity if new, then rebuilds the index. `--replace` and `--relate` on `board.py memory add`. |
| `just memory-index` | Rebuilds `index.json` from the memory and `work/orders/`. |
| `just memory-lint` | Checks the caps, the name and observation format, secret-looking lines and relations that point nowhere. |

- **One lock.** `memory add` takes the memory's lock, reads the file, writes a new one and renames it into place, rebuilds the index and only then lets go. Two writers in two processes at once lose nothing, and a reader never sees half a file.
- **The index.** One row per entity and per work order: `id`, `order`, `topic`, `owner`, `status`, `next`. An order is open, building, improve, accepted or landed, read from its folder and `origin/main`; an entity is current or superseded. It holds no clock, so rebuilding an unchanged state changes nothing. The orders come from the checkout that ran the command.
- **Python.** `memory add` and `memory index` need 3.11, because they read orders through `tools/work.py`; run them with `uv run`. Under an older `python3` they refuse and write nothing.

The room is where work happens now: claims, slots, handoffs, questions. The memory holds what a later session would otherwise have to work out again. When a DECISION or LANDED entry changes how people work, it also becomes a `decision:` or `rule:` entity that cites the room entry or issue #95.

- **Reading.**
  - The session-start digest has every `rule:` and `gotcha:` entity and the ten newest `decision:` entities.
  - Before opening docs about an unfamiliar area, run one search with a single keyword or a prefix such as `gotcha:`. Subagents do the same, because they get no session-start hook.
  - Never read the whole file into a context window. Search it.
- **Writing.** Write only at a checkpoint or a landing, and only a fact another session would otherwise have to rediscover. Search first. To change a fact, add the new one with `--replace` naming the old one.
- **Names.** Every name has the form `kind:slug`. The kind is one of `rule`, `gotcha`, `decision`, `contract`, `component` or `team`, and `entityType` is the kind. For example, `gotcha:gh-pr-merge-auto-mode` or `component:tools/board.py`.
- **Observations.** Each observation has the form `YYYY-MM-DD [team:<claude|codex|board>] <one fact>, src: <path|PR #n|ADR n|room entry id>`. It is at most 200 characters, and each entity has at most 8.
- **Relations.** The relation types are `owns`, `depends_on`, `supersedes` and `documented_in`. A relation may only point at an entity that exists.
- **Caps.** The memory holds at most 300 entities. Over that, fold the details into a doc and leave a pointer. Semantic search comes only after a measured need.
- **Refusals.** A write that would add a lint problem is refused whole.
- **Never store:**
  - secrets, tokens, `.env` contents, or anything from a path the deny lists block
  - personal data or scores
  - text copied from a tracked file (point to the file instead)
  - transient status (that goes in the room)
  - anything `AGENTS.md` already says

## Setup on a machine

- **Claude Code.** Nothing to approve: the SessionStart hook reads the board, and Bash writes it through `tools/board.py`.
- **Codex.** Codex writes the room and the memory only through `just codex` (for example `just codex resume --last`), which starts `codex` with `--add-dir "$(git rev-parse --path-format=absolute --git-common-dir)/board"`, the absolute board in the git common dir. The tracked `.codex/config.toml` names no writable root, because a relative one is not a directory in a linked worktree and Codex then refuses every shell tool; a plain `codex` session reads the board, and `board.py` names this flag when it tries to write. Nothing under `.agents/` or elsewhere in `.git` is writable.
- **A linked worktree takes its hooks and its trust from the main checkout.** In a linked worktree Codex reads project hooks (`.codex/hooks.json` and any `[hooks]` in `.codex/config.toml`) from the main checkout's `.codex/`, never from the worktree's copy, and `/hooks` keys their trust by the main checkout's path; the commands still run with the worktree as the working directory (openai/codex PR 21969). A hook change on a branch therefore takes effect only once the main checkout has it. A worktree also inherits the main checkout's project trust from `[projects."<main checkout>"]` in `~/.codex/config.toml`, so trusting the main checkout once, in Codex's own trust prompt, covers every worktree. Approving the SessionStart entry once in `/hooks`, in Codex's own prompt and bypassing nothing, turns it on for the main checkout and every worktree; until then `just codex` puts the output of `tools/board.py read` in front of the first prompt, so the digest comes by instruction. No MCP server is registered on either client.
- **Once, in a checkout with an untracked `.codex/hooks.json`.** The main checkout had one, holding Codex's copies of the work-order hooks. Git refuses the pull that brings the tracked file ("untracked working tree files would be overwritten by merge"), so move it aside first: `mv .codex/hooks.json .codex/hooks.json.local`, pull, compare, then delete the local copy. The tracked file carries the same four work-order hooks as `.claude/settings.json` (a test keeps them equal) plus the SessionStart reader. `.codex/agents/`, Codex's role definitions, stays untracked and is not touched.
- **Camps.** Camps get none of this: `tools/sync_template.py` leaves out the hook and the skill.
