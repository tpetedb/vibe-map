# .agents/

One source for every agent client that works in this repository. A person edits
`config.toml` at the repository root; everything here is the rest of the source;
the files Claude Code and Codex read are rendered from it and never edited by
hand. The design is DECISION #193 (issue #193); the board keeps its full text in
the runtime store, `<git common dir>/board/harness/DECISION-final.md`.

## What is active

`python3 .agents/utils/harness.py explain` prints every effective value, the file
it comes from and when a change to it takes effect: now, at the next spawn, at
the next session after a sync, or after Codex re-trusts its hooks.

## Where to change it

| Change | File |
|---|---|
| The profile, the model table, how many agents, the providers | `config.toml` (the root) |
| What a profile means | `conf/profiles/strict.toml`, `balanced.toml`, `fast.toml`: complete files, the same keys each, no inheritance |
| Which model and effort a role gets | `conf/models/tom.toml` |
| A subagent (name, description, instructions, model role) | `conf/roles/<name>.toml` |
| A hook either client runs | `conf/hooks.toml` |
| The permission floor: deny and ask rules | `conf/policy.toml` |
| MCP servers (none today) | `conf/mcp.toml` |
| What Claude reads beyond AGENTS.md | `context/claude.md`, rendered into `CLAUDE.md` |
| A new rendered text file | a template in `templates/`, whose first line names its output |
| Something for your machine only | `config.local.toml` here, untracked |

Then `uv run python .agents/utils/harness.py sync`. It renders
`.claude/settings.json`, `.claude/agents/`, `.codex/config.toml`,
`.codex/hooks.json`, `.codex/agents/` and `CLAUDE.md`, links every skill into
`.claude/skills/`, and writes `generated.lock`. It reads tracked files only: add
a new source file to git before you sync.

`config.local.toml` is a private overlay with the keys of a profile. It is never
rendered into a tracked file, and it may only make a value stronger: a weaker
one is refused before anything spawns, and needs a reviewed change to the
profile instead.

```toml
# .agents/config.local.toml
version = 1
local_checks = "affected-plus-security"
loop = { iterations = 10, wall_minutes = 30 }
```

## How to check it

- `python3 .agents/utils/harness.py check`: exit 1 when an output was edited by
  hand, an input changed without a sync, or an output differs from a fresh
  render. Standard library only; CI and hooks call it.
- `python3 .agents/utils/harness.py doctor`: offline health. The schemas, the
  lock, the skill links (repaired on the way), each root-to-leaf AGENTS.md chain
  against the Codex budget, the model ids against the client's own list, and
  Codex project trust and hook trust as two separate values.
- `python3 .agents/utils/harness.py pick <role> --provider claude|codex`: the
  model and effort a spawn gets. Never another provider's model.

## How to recover

- Drift: run `sync`, read the diff, commit it. An output someone edited by hand
  is overwritten; move the change into its source first.
- A broken link under `.claude/skills/`: `doctor` or `sync` repairs it.
- Codex hook trust missing: start `codex` here and approve the hooks in `/hooks`.
- Project trust missing: answer the trust prompt the next time `codex` starts in
  the main checkout. Codex 0.156.1 decides a checkout's trust by its own
  `[projects]` entry, else the main checkout's, so a linked worktree inherits it
  unless it carries an entry of its own, and doctor reports which entry decided.
  A worktree also runs the main checkout's `.codex/hooks.json`, approved once in
  `/hooks` for every checkout (openai/codex PR 21969).

## The rest of the folder

| Path | What |
|---|---|
| `skills/` | Skills in the Agent Skills standard, read in place by Codex and most other clients |
| `utils/harness.py` | `sync`, `check`, `doctor`, `explain`, `pick` |
| `templates/` | Jinja2 for text outputs; JSON and TOML are written by the generator itself |
| `generated.lock` | The hash of every output and every input at the last sync |
| `tasks/` | A pointer to `work/orders/`, never a second ledger |
| `memory/` | A pointer to the shared memory, which lives in the runtime store |
