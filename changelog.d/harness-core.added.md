- The harness core (DECISION #193 sections 1 to 3). `config.toml` at the root
  is the one file a person edits: the profile, the safeguards, the autonomy,
  the providers, the agent budget, the model table and the usage thresholds.
  Three complete profiles (strict, balanced, fast), Tom's model table and the
  roles, hooks and permission floor live under `.agents/conf/`.
- `.agents/utils/harness.py`: `sync` renders `.claude/settings.json`,
  `.claude/agents/`, `.codex/config.toml`, `.codex/hooks.json`,
  `.codex/agents/` and `CLAUDE.md` from tracked sources and records every hash
  in `.agents/generated.lock`; `check` finds drift with the standard library
  only; `doctor` checks schemas, the lock, the skill links, each AGENTS.md
  chain against the Codex budget, the model ids against the client's list, and
  reports Codex project trust and hook trust as two values; `explain` prints
  every effective value with its source and when it applies; `pick` gives the
  model and effort for a role on one provider, never another provider's.
- A private overlay, `.agents/config.local.toml`, may only make a value
  stronger; a weaker one is refused before anything spawns.
- The skills are linked into `.claude/skills/` with relative links, repaired
  on every sync and doctor, and copied where links cannot be made.
- `.claude/settings.json` gains deny rules for secrets and forced pushes and an
  ask rule on `config.toml`. The builder subagent runs on Opus 5.5, the
  reviewer on Opus 5.5 at medium effort and the team manager on Fable 5.1, as
  the model table says; the Codex agents get Sol and Astra.
- `tools/work.py` accepts a path `.agents/generated.lock` lists as
  regenerable, but only when `harness.py` renders it: a hand-maintained file
  listed there is refused. Such a file changed by an order that does not own
  it passes `work.py check` and `work.py ci` only while `harness.py check`
  reproduces it, and the edit hook refuses a hand edit to it outright.
  `work.py check` and `work.py ci` run `harness.py check` themselves whenever
  the lock exists and fail on drift, in a pull request that carries no order
  too.
  `just harness-sync`, `harness-check`, `harness-doctor`, `harness-explain`
  and `harness-pick` run the tool.
- `doctor` reads Codex trust the way Codex 0.156.1 resolves it: a checkout's
  own `[projects]` entry first, else the main checkout's, and in a linked
  worktree the hooks of the main checkout's `.codex/hooks.json`, keyed by that
  path.
- `sync` removes an output an earlier lock lists only where `harness.py`
  renders, never a hand-maintained file or a path outside the repository; a
  profile or model table that git does not track is refused; a Codex role may
  run at effort max, which the installed client lists for every GPT model.
- Camps get the permission floor too: through `tools/sync_template.py` the
  camp settings carry the deny rules, a sandbox block that is off, and the ask
  rule on `./config.toml`, a file a camp does not have.
