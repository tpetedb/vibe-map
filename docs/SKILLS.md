# Skills

What each skill in this repo does, when Claude Code loads it, how to prove that it does, and where the vendored ones come from.

## How skills load

- Skills live in `.agents/skills/<name>/SKILL.md`, the cross-tool folder of the Agent Skills standard (https://agentskills.io). Claude Code reads `.claude/skills/`, so link them once (`scripts/setup.sh` and `just setup` run the same loop):

  ```
  mkdir -p .claude/skills && for d in .agents/skills/*/; do n=$(basename "$d"); [ -e ".claude/skills/$n" ] || ln -s "../../.agents/skills/$n" ".claude/skills/$n"; done
  ```

- At startup Claude sees only `name` and `description`. The description decides whether a skill loads for a prompt, so it says what the skill does and when to use it, with the words a person would type. The spec caps it at 1,024 characters; Claude Code truncates description plus `when_to_use` at 1,536. The body loads only when the skill fires. `/name` loads a skill by hand. Docs: https://code.claude.com/docs/en/skills
- Some skills pre-approve their own commands with `allowed-tools` (`camp-progress`: `uv run vibe`, `just`; `duckdb-sql`: `duckdb`; the four documentation skills `semver`, `changelog`, `adr` and `readme-quickstart`: read-only commands such as `uv run vibe --version`, `git tag -l`, `git log`, `git diff`, `ls`), so the learner is not asked for permission on every call.

## The skills

| Skill | What it does | Loads when the user says | Origin |
|---|---|---|---|
| `adr` | Writes an architecture decision record in Nygard's form (Title, Status, Context, Decision, Consequences) into `docs/adr/` and updates the index | "write an ADR", "record this decision", "why did we choose", "document the trade-off", "supersede ADR 3" | house |
| `changelog` | Keeps `CHANGELOG.md` in Keep a Changelog 1.1.0 form: Unreleased on top, six kinds of change, ISO dates, compare links | "update the changelog", "add a changelog entry", "release notes", "cut a release", "what changed since" | house |
| `develop-camp` | Develops, reviews and improves this product: game from `src/`, CLI, tech tree, syllabus, skills | "fix the game", "add a world", "add a workstream", "review it and make it better", any change touching more than one file | house |
| `duckdb-sql` | Answers questions about `data/scores.csv` with DuckDB SQL, teaches one construct per query | "top runs", "best score", "average per player", "who is winning", "write SQL", anything about `sql/` | house |
| `camp-progress` | Tracks the eight workstreams through `uv run vibe` (status, check, done, map, vault, export, import) | "mark 3 done", "where am I", "what is next", "check my progress", "export my progress code" | house |
| `install-camp` | Installs and runs the course on a Mac, every dependency chosen by the user | "set up vibe", "install the course", "is my machine ready", "start the evening" | house |
| `mermaid-diagrams` | Draws Mermaid diagrams in the house conventions: ISO 5807 shapes, palette classDefs, a legend | "draw a diagram", "flowchart", "show me how these connect", "visualise the plan" | house |
| `obsidian-notes` | Writes and links notes in `vault/Camp/` with wikilinks, dated sections, tags, sources | "write a note about", "add to the vault", "log what we built tonight", "update Tonight.md" | house |
| `python-data` | Small readable Python for reading the CSV, summaries and charts, run with uv | "write a script", "make a chart", "plot", "automate this", "do it in Python" | house |
| `readme-quickstart` | Writes or repairs a README that gets a stranger from clone to a working run on the first screen, after makeareadme.com and the doc-doc templates | "write a README", "improve the README", "add a quickstart", "how do people get started", "document how to run this" | house |
| `semver` | Picks the next version with Semantic Versioning 2.0.0 and bumps `pyproject.toml`, `vibemap/__init__.py` and the git tag | "bump the version", "is this a breaking change", "release 0.3.0", "tag it", "what does 0.x mean" | house |
| `webapp-testing` | Drives a local web app with Playwright: screenshots, console logs, element discovery, a server helper | "test the game in a browser", "take a screenshot of the page", "check the console for errors", "Playwright" | vendored, https://github.com/anthropics/skills/tree/main/skills/webapp-testing, Apache-2.0 |
| `verification-before-completion` | Refuses to claim done, fixed or passing without running the proving command first | fires on its own before "done", "fixed", "tests pass", a commit or a PR | vendored, https://github.com/obra/superpowers/tree/main/skills/verification-before-completion, MIT |

Not a skill but in the same family: the `scorekeeper` subagent (`.claude/agents/scorekeeper.md`) summarises `data/scores.csv` into `vault/Camp/Scores.md`; say "summarise the scores into the vault" or `@scorekeeper`. The PostToolUse hook in `.claude/settings.json` copies `data/` into `backups/` after every Edit or Write; `/hooks` lists it.

## Test that each one triggers

Start `claude` in this folder. Type `/` and confirm every folder in `.agents/skills/` appears by name. Then type each phrase in a fresh session and check the transcript for the `Skill(<name>)` call before the answer. One negative per skill: a phrase that must not load it.

| Skill | Phrases that must load it | Must not load it |
|---|---|---|
| `adr` | "write an ADR for why the game is one file" | "update the changelog" |
| | "record the decision to use uv, with the trade-offs" | |
| `changelog` | "add what we did tonight to the changelog" | "bump the version" |
| | "cut release 0.3.0 in the changelog" | |
| `develop-camp` | "review the game and make it better" | "what is DuckDB?" |
| | "add a winter world to the game" | |
| | "change Rolinda's line in workstream 3" | |
| `duckdb-sql` | "what is the best score per player?" | "draw a chart of the scores" |
| | "how many runs did Lotte play?" | |
| | "explain sql/streaks.sql to me" | |
| `camp-progress` | "I finished workstream 2, mark it done" | "draw a flowchart of tonight" |
| | "where am I in the campaign?" | |
| | "give me the code to paste into the game" | |
| `install-camp` | "set up vibe on this Mac" | "add a world to the game" |
| | "what do I need installed for tonight?" | |
| | "start the evening" | |
| `mermaid-diagrams` | "draw a flowchart of how the CLI and the game sync" | "where am I in the campaign?" |
| | "make a diagram of the vault for the Knowledge Tree note" | |
| `obsidian-notes` | "write a note about what we learned about hooks" | "what is the best score?" |
| | "add tonight's build to Tonight.md" | |
| `python-data` | "write a Python script that charts scores per player" | "what is the best score per player?" |
| | "automate the summary in Python" | |
| `readme-quickstart` | "rewrite the README quickstart so it works with uv" | "write a note about READMEs" (that is `obsidian-notes`) |
| | "there is no README, write one" | |
| `semver` | "should this be 0.3.0 or 1.0.0?" | "add a changelog entry" |
| | "bump the version and tag it" | |
| `webapp-testing` | "open the game in a headless browser and screenshot the title" | "run the smoke tests" (that is `just smoke`, develop-camp) |
| | "check the browser console for errors on game/vibe-map.html" | |
| `verification-before-completion` | ask for any change, then "is it done?" or "commit it" | a plain question |

Overlaps to know:

- "map": `camp-progress` owns the progress map (`vault/Camp/Map.md`, generated); `mermaid-diagrams` draws new diagrams.
- A release is three skills in order: `changelog` (what changed, in `CHANGELOG.md`), `semver` (the number), then the commit and tag. `adr` records why a decision was made (`docs/adr/`); `readme-quickstart` records how to run the result.
- Scores: a question is `duckdb-sql`; a script or a chart is `python-data`; "update Scores.md in the vault" is the `scorekeeper` subagent.
- Tom's toolbox ships a personal `mermaid-diagrams` skill in `~/.claude/skills/`. The project skill follows the same conventions (shapes, palette, legend), so whichever one Claude Code picks gives the same result.

## Vendored skills: policy and provenance

Policy: MIT or Apache-2.0 only; copied verbatim except the emoji and em dashes the house style check (`just style-check`) rejects; an attribution line at the top of the body names the source URL, licence and commit and lists every change; the licence text sits in `LICENSE` next to `SKILL.md`.

| Skill | Source | Licence | Commit | Changes |
|---|---|---|---|---|
| `webapp-testing` | https://github.com/anthropics/skills/tree/main/skills/webapp-testing | Apache-2.0 (per-skill `LICENSE.txt` upstream, Copyright 2026 Anthropic, PBC) | `34040c9c568585f6929bedeaad110ad08f079624` | two emoji removed; `license:` line names the file |
| `verification-before-completion` | https://github.com/obra/superpowers/tree/main/skills/verification-before-completion | MIT (Copyright 2025 Jesse Vincent) | `b36e0829c6d0140e93cfef2ca599b1b07d4a7797` | ten check and cross emoji became "Do:" and "Don't:"; `license:` line added |

Considered and not vendored:

- `mcp-builder` (anthropics/skills, Apache-2.0): the course connects to MCP servers in workstream 5, it does not build them; the skill carries about 100 KB of reference material and a dozen emoji. Recommend as a personal skill for whoever writes a server.
- `test-driven-development` and `systematic-debugging` (obra/superpowers, MIT): TypeScript examples, eval artefacts in the folder, and the house rule already lives in `AGENTS.md` (tests in `tests/`, `uv run pytest`).
- `git-advanced-workflows` (wshobson/agents, MIT): rebase, cherry-pick, bisect, reflog; the wrong audience for workstream 4. `git-pr-workflows` in the same repo ships agents and commands, no skill.
- Commit-message skills (`stefanholdermans/git-commit-message`, `rvanbaalen` gist, both MIT, single-author): they enforce Conventional Commits, which conflicts with the house rule "what and why, one line". Install one with `npx skills add <owner/repo>` if a learner wants the convention.

To vendor another: check `LICENSE` first; copy the folder; add the attribution line; run `just style-check`; add a row here.
