# Ecosystem: what makes coding agents better

A verified catalogue for Vibe Code Camp. Stars, licences and last-push dates come from `gh api` on 2026-09-16; every other URL was fetched the same day. Licence "none" means GitHub found no licence file, "custom" means a non-standard one: read the terms before copying.

## 1. Skill collections (Agent Skills standard)

The standard lives at [agentskills.io](https://agentskills.io): a skill is a folder with a `SKILL.md` whose frontmatter needs only `name` and `description` ([specification](https://agentskills.io/specification)). Agents load the description at startup and the body only when a task matches.

| Project | What it is | Stars, licence, pushed | Why it matters here | Try it |
| --- | --- | --- | --- | --- |
| [anthropics/skills](https://github.com/anthropics/skills) | Anthropic's own: `docx`, `pdf`, `pptx`, `xlsx`, `skill-creator`, `webapp-testing`, `frontend-design`, `mcp-builder` | 176,697, none detected (per-skill files), 2026-09-10 | Beginner fit: `skill-creator` for a first skill, office-file skills for real deliverables, `webapp-testing` for the game | `/plugin install skill-creator@claude-plugins-official` |
| [obra/superpowers](https://github.com/obra/superpowers) | Jesse Vincent's workflow skills: `brainstorming`, `writing-plans`, `test-driven-development`, `systematic-debugging`, `verification-before-completion`, `using-git-worktrees` | 287,592, MIT, 2026-09-14 | The course already vendors `verification-before-completion` in `.agents/skills/`; `brainstorming` then `writing-plans` is the beginner path | Copy a skill folder into `.claude/skills/` |
| [mattpocock/skills](https://github.com/mattpocock/skills) | Matt Pocock's "Skills for Real Engineers" | 263,543, MIT, 2026-09-15 | Short, single-purpose skills with model `description` lines | Read three `SKILL.md` files first |
| [wshobson/agents](https://github.com/wshobson/agents) | 90+ plugins pairing subagents with skills: `developer-essentials`, `debugging-toolkit`, `git-pr-workflows`, `python-development` | 39,727, MIT, 2026-09-14 | Installable marketplace, so learners see plugins and skills together | `/plugin marketplace add wshobson/agents` |
| [agentskills/agentskills](https://github.com/agentskills/agentskills) | The spec repo plus the `skills-ref` validator | 25,410, Apache-2.0, 2026-08-09 | Mechanical frontmatter check for learners | `skills-ref validate ./my-skill` |

## 2. Claude Code plugins and marketplaces

Docs: [discover and install plugins](https://code.claude.com/docs/en/discover-plugins), [create plugins](https://code.claude.com/docs/en/plugins). A plugin bundles skills, agents, hooks, MCP and LSP servers; a marketplace is a catalogue of plugins. Commands: `/plugin marketplace add owner/repo`, `/plugin install name@marketplace`, `claude --plugin-dir ./my-plugin` to test, `claude plugin validate ./my-plugin` before sharing.

| Marketplace | What it is | Stars, licence, pushed | Why it matters here | Try it |
| --- | --- | --- | --- | --- |
| [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | Registered automatically on first run: `github`, `commit-commands`, `code-review`, `feature-dev`, `hookify`, `ralph-loop`, `security-guidance`, `skill-creator`, `plugin-dev`, `pyright-lsp`, `learning-output-style` | 36,428, Apache-2.0, 2026-09-16 | The curated set; `learning-output-style` is built for learners | `/plugin install learning-output-style@claude-plugins-official` |
| [anthropics/claude-plugins-community](https://github.com/anthropics/claude-plugins-community) | Third-party plugins that passed Anthropic's automated screening, pinned to commit SHAs | 4,147, Apache-2.0, 2026-08-25 | Where a learner's plugin can end up | `/plugin marketplace add anthropics/claude-plugins-community`, then `/plugin install <name>@claude-community` |
| [anthropics/claude-code](https://github.com/anthropics/claude-code) (`plugins/`) | Demo marketplace `claude-code-plugins`: `ralph-wiggum`, `hookify`, `code-review`, `commit-commands` | 145,402, none, 2026-09-16 | Small, readable plugins to copy from | `/plugin marketplace add anthropics/claude-code` |
| [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) | Curated directory of skills, agents, status lines and plugins | 54,171, custom, 2026-09-16 | The browsing list to point learners at | Read the README |

## 3. Hooks

Docs: [hooks](https://code.claude.com/docs/en/hooks). Events include `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Notification`, `Stop`, `SessionEnd`. Five handler types: `command`, `http`, `mcp_tool`, `prompt` (a model judges the call) and `agent` (a subagent verifies). A command hook reads JSON on stdin; exit code 2 blocks on `PreToolUse`, `UserPromptSubmit` and `Stop`. Hooks are deterministic where `CLAUDE.md` is advisory ([best practices](https://code.claude.com/docs/en/best-practices)). Patterns from the docs:

- Format on save: `PostToolUse`, matcher `Edit|Write`, `"command": "prettier --write", "args": ["${tool_input.file_path}"]`; use `ruff format` for Python.
- Guardrail: `PreToolUse`, matcher `Bash`; read `.tool_input.command` with `jq`, print a reason to stderr and `exit 2` when it starts with `rm -rf`.
- Notification: `SessionEnd` runs `notify-send "Claude Code" "Session ended"`; on macOS use `osascript -e 'display notification ...'`.
- Stop gate: a `Stop` hook runs the tests and exits 2 until they pass; Claude Code ends the turn anyway after 8 consecutive blocks. This repo's own `PostToolUse` hook that backs up `data/` is the local example.

| Collection | What it is | Stars, licence, pushed | Why it matters here | Try it |
| --- | --- | --- | --- | --- |
| `hookify` (official plugin) | Writes a hook from a plain-English request into `.claude/hookify.*.local.md`, no code | see marketplace | The non-programmer's way in | `/plugin install hookify@claude-plugins-official`, then `/hookify Warn me when I use rm -rf commands` |
| [karanb192/claude-code-hooks](https://github.com/karanb192/claude-code-hooks) | Tested hooks as installable plugins: safety, cost, observability | 513, MIT, 2026-09-16 | Blocks `.env` reads, `curl \| sh`, force-push to main | Add as a marketplace, install one hook |
| [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) | 20+ hooks inside a kit that also serves Codex, OpenCode and Cursor | 260,083, MIT, 2026-09-15 | Working examples for most events | Read `hooks/` |
| [disler/claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery) | One worked example per hook event | 3,921, none, 2026-03-04 | Clearest teaching repo, six months stale | Read, do not install blindly |

## 4. Loops and autonomy

| Entry | What it is | Stars, licence, pushed | Why it matters here | Try it |
| --- | --- | --- | --- | --- |
| [Ralph loop](https://ghuntley.com/ralph/) (Geoffrey Huntley, 2025-07-14) | "Ralph is a Bash loop": `while :; do cat PROMPT.md \| claude-code ; done`, one task per iteration, tests as back-pressure | n/a | The whole idea of autonomy in one line | `while :; do claude -p "$(cat PROMPT.md)"; done` |
| `ralph-loop` (official plugin) | Ralph inside one session: a `Stop` hook re-feeds the prompt until the completion promise appears | see marketplace | No external shell loop, safe to teach | `/plugin install ralph-loop@claude-plugins-official`, then `/ralph-loop "Make the tests pass" --completion-promise "DONE"` |
| [`/loop`](https://code.claude.com/docs/en/scheduled-tasks) (built in) | Re-run a prompt on an interval inside a session; units `s m h d`, minimum 1 minute, expires after 7 days, `.claude/loop.md` sets the default prompt. The Desktop app adds [local scheduled tasks](https://code.claude.com/docs/en/desktop-scheduled-tasks) that survive restarts | n/a | Cron without leaving the terminal | `/loop 5m check whether the tests pass`, or `remind me at 3pm to push the branch` |
| [Routines](https://code.claude.com/docs/en/routines) (cloud, research preview) | Saved prompt, repo and connectors run on a schedule (minimum 1 hour), an API call or a GitHub event; Pro, Max, Team, Enterprise | n/a | Runs with the laptop closed | `/schedule daily PR review at 9am` |
| [Headless `claude -p`](https://code.claude.com/docs/en/headless) | Non-interactive runs; `--bare` skips hooks and plugins; `--permission-mode auto --permission-prompts none` for unattended runs | n/a | The building block of every loop | `claude --bare -p "Summarize README.md" --allowedTools "Read"` |
| [GitHub Actions](https://code.claude.com/docs/en/github-actions), [anthropics/claude-code-action](https://github.com/anthropics/claude-code-action) | `@claude` in issues and PRs, or a `prompt` on any event including `schedule: cron: "0 9 * * *"` | 8,890, MIT, 2026-09-15 | Cron in the cloud without Routines | `/install-github-app`, then `uses: anthropics/claude-code-action@v1` |

Cron from the docs: `*/5 * * * *` every five minutes, `0 9 * * 1-5` weekdays at 9am local. Fan-out from best practices: `for file in $(cat files.txt); do claude -p "Migrate $file" --allowedTools "Edit,Bash(git commit *)"; done`.

## 5. Multi-model councils and debate

| Project | What it is | Stars, licence, pushed | Why it matters here | Try it |
| --- | --- | --- | --- | --- |
| [karpathy/llm-council](https://github.com/karpathy/llm-council) | Local web app. Stage 1: every model answers alone. Stage 2: each model ranks the others' anonymised answers for accuracy and insight. Stage 3: a Chairman compiles the final answer. Uses OpenRouter; default council GPT-5.1, Gemini 3.0 Pro, Claude Sonnet 4.5, Grok 4, Gemini as Chairman | 24,871, none, 2025-11-22 (author says unsupported) | The reference design for the course's council of mentors | `uv sync`, `npm install` in `frontend/`, `OPENROUTER_API_KEY` in `.env`, `./start.sh`, open `localhost:5173` |
| [BeehiveInnovations/zen-mcp-server](https://github.com/BeehiveInnovations/zen-mcp-server) | MCP server that lets Claude Code consult Gemini, OpenAI, Grok, Ollama in one session | 11,750, custom, 2025-12-15 | Closest thing to a council inside Claude Code | Add as an MCP server, ask for a second opinion |
| [togethercomputer/MoA](https://github.com/togethercomputer/MoA) | Mixture-of-Agents: layers of proposer models feed an aggregator | 2,977, Apache-2.0, 2025-01-07 | Research ancestor of the chairman step | Read the README |
| [composable-models/llm_multiagent_debate](https://github.com/composable-models/llm_multiagent_debate) | ICML 2024 code: models see each other's answers and revise over rounds | 552, none, 2025-04-24 | The academic root of debate | Read the paper |
| [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) (Anthropic, 2024-12-19) | Names the parts: parallelization with voting, evaluator-optimizer | n/a | Vocabulary for the lesson | Read once |

The pattern in five sentences. Send the same question to several different models independently, so no model sees another's draft before writing its own. Strip the names off the drafts and hand each model the full set to rank for accuracy and insight, which turns every member into a reviewer who cannot play favourites. Aggregate the rankings so the group's judgement, not any single vote, decides which drafts carry weight. Give one model the chairman role: it reads all drafts and rankings and writes the single answer the user sees, noting where the council disagreed. Keep every stage inspectable, because the cross-opinions are often more useful than the verdict.

## 6. MCP servers for a non-programmer

Docs: [MCP in Claude Code](https://code.claude.com/docs/en/mcp). Local: `claude mcp add --transport stdio <name> -- <command>`. Remote: `claude mcp add --transport http <name> <url>`. `/mcp` lists connections. With a claude.ai login, the Google Drive, Gmail, Calendar and Slack connectors enabled on claude.ai appear in `/mcp` automatically, the easiest route for most learners. The official [registry](https://registry.modelcontextprotocol.io/) ([modelcontextprotocol/registry](https://github.com/modelcontextprotocol/registry), 7,256, custom) is the directory; official plugins such as `github`, `notion`, `figma` and `slack` bundle a server plus setup. Obsidian servers are in section 8.

| Server | What it is | Stars, licence, pushed | Why it matters here | Try it |
| --- | --- | --- | --- | --- |
| [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) | Reference servers: `filesystem`, `fetch`, `git`, `memory`, `time`, `sequentialthinking` | 90,388, custom, 2026-09-03 | Filesystem is the first server to try | `claude mcp add --transport stdio filesystem -- npx -y @modelcontextprotocol/server-filesystem ~/Documents` |
| [github/github-mcp-server](https://github.com/github/github-mcp-server) | GitHub's official server, hosted at `https://api.githubcopilot.com/mcp/` | 32,974, MIT, 2026-09-16 | Issues and PRs without leaving the chat | `/plugin install github@claude-plugins-official`, or `claude mcp add --transport http github https://api.githubcopilot.com/mcp/ --header "Authorization: Bearer YOUR_GITHUB_PAT"` |
| [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp) | Browser automation through the accessibility tree | 37,178, Apache-2.0, 2026-09-14 | Lets Claude play and test the game in a real browser | `claude mcp add --transport stdio playwright -- npx -y @playwright/mcp@latest` |
| [taylorwilsdon/google_workspace_mcp](https://github.com/taylorwilsdon/google_workspace_mcp) | Gmail, Calendar, Docs, Sheets, Drive, Tasks; community, no official Google server found | 3,177, MIT, 2026-09-15 | For learners on an API key rather than a claude.ai login | Follow the README OAuth setup |

## 7. Provider CLIs and their non-interactive flags

Only `claude` was installed on the research machine, so the other flags are verified from official docs, not from `--help`.

| CLI | Repo (stars, licence) | Install | Non-interactive | Docs |
| --- | --- | --- | --- | --- |
| Claude Code | [anthropics/claude-code](https://github.com/anthropics/claude-code) (145,402, none) | `curl -fsSL https://claude.ai/install.sh \| bash`, or `brew install --cask claude-code`, or `npm install -g @anthropic-ai/claude-code` ([setup](https://code.claude.com/docs/en/setup)) | `claude -p "prompt"`; add `--output-format json`, `--bare`, `--allowedTools "Read"`, `--permission-mode auto --permission-prompts none` | [headless](https://code.claude.com/docs/en/headless) |
| OpenAI Codex CLI | [openai/codex](https://github.com/openai/codex) (124,728, Apache-2.0) | `npm i -g @openai/codex`, or `brew install codex`, or `curl -fsSL https://chatgpt.com/codex/install.sh \| sh` | `codex exec "prompt"`; `codex exec -` reads the prompt from stdin; `--json`, `-o out.md`, `--sandbox workspace-write`; `--full-auto` is deprecated | [CLI](https://learn.chatgpt.com/docs/codex/cli), [non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode) |
| Gemini CLI | [google-gemini/gemini-cli](https://github.com/google-gemini/gemini-cli) (107,019, Apache-2.0) | `npm install -g @google/gemini-cli`, or `brew install gemini-cli`, or `npx @google/gemini-cli` | `gemini -p "prompt"`; `--output-format json` or `stream-json`; exit codes 0, 1, 42 (input), 53 (turn limit). Approval flags such as `--yolo` are not on the headless page: unverified | [headless](https://geminicli.com/docs/cli/headless/) |
| GitHub Copilot CLI | [github/copilot-cli](https://github.com/github/copilot-cli) (11,177, custom) | `npm install -g @github/copilot`, or `brew install --cask copilot-cli`, or `curl -fsSL https://gh.io/copilot-install \| bash` ([install](https://docs.github.com/en/copilot/how-tos/set-up/install-copilot-cli)) | `copilot -p "prompt" -s --allow-tool='shell(git:*)'`; `--allow-all-tools`; `--output-format json`; `--model=claude-haiku-4.5` | [run programmatically](https://docs.github.com/en/copilot/how-tos/copilot-cli/automate-copilot-cli/run-cli-programmatically), [reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-programmatic-reference) |
| OpenCode | [sst/opencode](https://github.com/sst/opencode) (207,898, MIT) | `curl -fsSL https://opencode.ai/install \| bash`, or `npm i -g opencode-ai` | `opencode run "prompt"`; `--format json`; `-m provider/model`; `-c` continues; `--auto` approves | [CLI](https://opencode.ai/docs/cli/) |
| llm (Simon Willison) | [simonw/llm](https://github.com/simonw/llm) (12,513, Apache-2.0) | `uv tool install llm`, or `brew install llm` | `llm "prompt"`; providers via `llm install llm-anthropic`, `llm-gemini`, `llm-ollama`; not an agent, but the cheapest way to script a council | [llm.datasette.io](https://llm.datasette.io/) |

## 8. Obsidian plus AI

| Project | What it is | Stars, licence, pushed | Why it matters here | Try it |
| --- | --- | --- | --- | --- |
| [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) | Claude Code plugin and Agent Skills set (15 skills) that turns sources into linked, cited notes; vault stays plain Markdown; built on Karpathy's LLM Wiki pattern | 15,005, MIT, 2026-09-10 | Nearest published cousin of this course's `vault/` | Follow `docs/install-guide.md` in the repo |
| [Obsidian CLI](https://obsidian.md/help/cli) (official) | Built into Obsidian 1.12.7+; enable under Settings, General, Command line interface | n/a | Claude Code drives the vault from Bash with no server (app must be running) | `obsidian search query="meeting notes"`, `obsidian daily` |
| [coddingtonbear/obsidian-local-rest-api](https://github.com/coddingtonbear/obsidian-local-rest-api) | Obsidian plugin exposing a REST API and a built-in MCP server | 2,931, MIT, 2026-08-31 | One plugin, no extra process; the base most vault servers stand on | Install in Obsidian, copy the API key |
| [MarkusPfundstein/mcp-obsidian](https://github.com/MarkusPfundstein/mcp-obsidian) | MCP server over the Local REST API | 4,421, MIT, 2026-08-31 | Most-starred vault server | `uvx mcp-obsidian` with `OBSIDIAN_API_KEY` set |
| [StevenStavrakis/obsidian-mcp](https://github.com/StevenStavrakis/obsidian-mcp) | File-based server; Obsidian need not be open | 733, MIT, 2026-09-10 | Works on a vault that is only a folder, like `vault/` here | Point it at the vault path |

## 9. People and sources worth citing

| Who | Cite for | Verified output |
| --- | --- | --- |
| Andrej Karpathy | The wiki pattern and the council pattern | [LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) `llm-wiki.md` (2026-04-04), [llm-council](https://github.com/karpathy/llm-council), [nanochat](https://github.com/karpathy/nanochat) (58,071, MIT, "The best ChatGPT that $100 can buy") |
| Simon Willison | Daily, sceptical, hands-on notes on every agent release; the `llm` CLI | [simonwillison.net](https://simonwillison.net/) (posts through 2026-09-14), [simonw/llm](https://github.com/simonw/llm) |
| Boris Cherny | Created Claude Code; five parallel instances in separate checkouts, plan mode first, then one-shot implementation | [Building Claude Code with Boris Cherny](https://newsletter.pragmaticengineer.com/p/building-claude-code-with-boris-cherny) (Pragmatic Engineer, 2026-03-04) |
| Anthropic engineering | Agent patterns, context engineering, long-running harnesses, tool design, skills | [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) (2024-12-19), [Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) (2025-09-29), [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) (2025-11-26), [Writing effective tools](https://www.anthropic.com/engineering/writing-tools-for-agents) (2025-09-11), [Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) (2025-10-16), [Best practices](https://code.claude.com/docs/en/best-practices) (the old anthropic.com URL redirects here) |
| Geoffrey Huntley | The Ralph loop and how a coding agent works inside | [Ralph](https://ghuntley.com/ralph/) (2025-07-14), [how-to-build-a-coding-agent](https://github.com/ghuntley/how-to-build-a-coding-agent) (5,825, none, 2026-09-12) |

Jesse Vincent, Matt Pocock and Seth Hobson are cited in section 1 through their skill repos.

## Surprises

1. Obsidian now ships an official CLI (1.12.7+). `obsidian search query="..."` from a Claude Code Bash tool reaches the vault with no MCP server, no API key and no plugin.
2. Ralph became an Anthropic plugin. `ralph-loop` in the official marketplace is a `Stop` hook that re-feeds the prompt until a completion promise appears, and `/loop 5m ...` gives cron inside a session with a seven-day expiry. The autonomy lesson can be taught with built-ins alone.
3. Karpathy's LLM Wiki is not code. It is a prose "idea file" meant to be pasted into any agent, and [claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) (15,005 stars, MIT) implements it for Claude Code while leaving the vault as plain Markdown.
4. Routines are cron with the laptop closed. `/schedule daily PR review at 9am` saves a cloud routine that can also fire from an HTTP POST or a GitHub pull-request event, on any paid plan.
5. A skill written for the course runs elsewhere. The client list at [agentskills.io](https://agentskills.io) includes Gemini CLI, Codex, Copilot, Cursor, OpenCode, [Goose](https://github.com/block/goose) (54,362 stars) and personal assistants such as [OpenClaw](https://github.com/openclaw/openclaw) (389,871 stars), so the `SKILL.md` folders in `.agents/skills/` are already portable.

## Companions

| Tool | Repo | What we took |
|---|---|---|
| claude-buddy | [btcromesh/claude-buddy](https://github.com/btcromesh/claude-buddy) (MIT) | The eighteen sprites, the idle and blink sequence and the seeded roll behind `vibe pet`, ported to `vibemap/pet.py`. It is the /buddy feature Claude Code shipped in 2.1.89 and pulled in 2.1.97, extracted into a single-file CLI. |
| any-buddy | [cpaczek/any-buddy](https://github.com/cpaczek/any-buddy) (WTFPL) | Nothing vendored; the reference for the eye and hat options. |

## Embedded in the game

| Library | Licence | Where |
|---|---|---|
| three.js r128 | MIT | the island |
| Motion 12 | MIT | springs on the sheet, the roadmap and the KPI count-up; optional |
| d3-force 3 (with d3-quadtree, d3-timer, d3-dispatch) | ISC | the vault graph: a cooled simulation with collision, pan and zoom |
| Lucide | ISC | the icons on every button in the HUD, the sheet and the vault toolbar |

## Obsidian and agents

| Tool | Repo | What it adds |
|---|---|---|
| claude-obsidian | [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) (MIT) | Fifteen Claude Code skills for a wiki-style vault: `/claude-obsidian:wiki` initialises and routes, `wiki-ingest` turns sources into linked pages with provenance, `wiki-query` answers read-only from the vault, `wiki-lint` reports dead links, orphans and stale indexes, `wiki-mode` supports LYT, PARA and Zettelkasten filing. `just obsidian-plugin` clones it; then `claude --plugin-dir ~/.claude/plugins/claude-obsidian` in this repo gives Claude those skills on `vault/`. |
