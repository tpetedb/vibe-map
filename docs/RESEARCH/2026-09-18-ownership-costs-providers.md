# Who pays for what, template versus fork, and what each coding harness can do

Research for [issue #90](https://github.com/tpetedb/vibe-map/issues/90). Read-only: web plus this repository. Every claim below carries the sentence that supports it, the URL it came from, and the date it was fetched. All pages were fetched on **2026-09-18**. Where a page does not answer a question, this report says so instead of guessing.

Pricing is given as structure only: who is billed, what is included, what needs which plan. Numbers that move are left as links.

Contents: [A. Billing](#a-billing-from-githubs-docs) - [B. Template versus fork](#b-template-versus-fork) - [C. Coding harnesses](#c-coding-harnesses) - [D. A free route](#d-a-free-route) - [1. Every way this project could cost Tom money](#1-every-way-this-project-could-put-a-cost-on-the-repository-owner) - [2. Recommendation: template or fork](#2-recommendation-template-versus-fork) - [3. Capability matrix](#3-capability-matrix) - [4. Corrections needed in providers.py](#4-corrections-needed-in-vibemapproviderspy)

---

## A. Billing, from GitHub's docs

### A.1 GitHub Actions

Source: <https://docs.github.com/en/billing/concepts/product-billing/github-actions>, fetched 2026-09-18.

> "GitHub Actions usage is **free** for **self-hosted runners** and for **public repositories** that use standard GitHub-hosted runners."

Included monthly minutes on private repositories, from the same page: GitHub Free 2,000, GitHub Pro 3,000, GitHub Team 3,000, GitHub Enterprise Cloud 50,000.

Runner rates matter only once a repository is private. The same page prices "macOS 3-core or 4-core (M1 or Intel)" at "$0.062" per minute against "Linux 2-core (x64)" at "$0.006", so a macOS minute costs roughly ten Linux minutes.

**This repository is public** (`gh repo view tpetedb/vibe-map`: `"visibility":"PUBLIC"`), so `ci.yml`, `nightly.yml`, `news.yml` and `pages.yml` are free today, including the two `runs-on: macos-latest` jobs in `ci.yml` and the `macos-latest` playthrough in `nightly.yml`.

**Gap**: the billing page does not state who is billed for a workflow run triggered by a pull request from a fork. That question is answered indirectly: the run happens in the upstream repository's Actions context, and for a public repository that context is free by the sentence above.

### A.2 Workflows from forks

Source: <https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository>, fetched 2026-09-18.

> "Workflows on pull requests to public repositories from some outside contributors will not run automatically, and might need to be approved first."

> "By default, all first-time contributors require approval to run workflows."

The page lists three tightenings of that policy: approval for first-time GitHub users, approval for any first-time contributor, and approval for all external contributors to the repository.

Source: <https://docs.github.com/en/actions/how-tos/manage-workflow-runs/approve-runs-from-forks>, fetched 2026-09-18.

> "Workflow runs triggered by a contributor's pull request from a fork may require manual approval from a maintainer with write access."

Secrets do not travel to those runs. From <https://code.claude.com/docs/en/github-actions>, fetched 2026-09-18:

> "On public repositories, GitHub withholds secrets from runs triggered by fork pull requests, so the review runs only on pull requests from branches in the same repository."

Scheduled workflows behave differently in a fork. Source: <https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows>, fetched 2026-09-18:

> "When a public repository is forked, scheduled workflows are disabled by default."

The same page notes that in public repositories scheduled workflows are disabled automatically after 60 days without repository activity. The Claude Code Actions page repeats this: "GitHub runs scheduled workflows only from the default branch and, in public repositories, disables the schedule after 60 days without repository activity."

That is the relevant fact for `news.yml` (`cron: "0 6 * * 1"`) and `nightly.yml` (`cron: "0 3 * * *"`): a fork of this repository does not silently start running them, and this repository's own schedules stop if the repository goes quiet for two months.

### A.3 Codespaces

Source: <https://docs.github.com/en/billing/concepts/product-billing/github-codespaces>, fetched 2026-09-18.

> "Compute usage is charged to the account that owns the codespace."

> "Codespaces created from a forked repository are billed to your personal account" unless the upstream organization has opted to pay.

Included personal quotas from the same page: GitHub Free "15 GB-month" storage and "120 hrs" compute; GitHub Pro "20 GB-month" and "180 hrs". And: "GitHub plans for organizations and enterprises do not include a free quota."

So a learner who presses **Code, Codespaces** on `tpetedb/vibe-map`, on a repository made from the template, or on a fork, spends their own included hours. Tom is not billed for their session.

**Prebuilds are the exception**, and they are billed to the repository side. Source: <https://docs.github.com/en/codespaces/prebuilding-your-codespaces/about-github-codespaces-prebuilds>, fetched 2026-09-18:

> "Each prebuild that's created consumes storage space that will either incur a billable charge or, for repositories owned by your personal GitHub account, will use some of your monthly included storage."

> "Running a prebuild configuration workflow will either consume some of the GitHub Actions minutes included with your account, if you have any, or it will incur charges for GitHub Actions minutes."

This repository has no `.devcontainer/` directory and no prebuild configuration today, so this cost is zero and stays zero as long as nobody adds one.

### A.4 Pages

Source: <https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits>, fetched 2026-09-18.

> "GitHub Pages source repositories have a recommended limit of 1 GB."

> "Published GitHub Pages sites may be no larger than 1 GB."

> "GitHub Pages sites have a *soft* bandwidth limit of 100 GB per month."

> "GitHub Pages sites have a *soft* limit of 10 builds per hour."

> "If your site exceeds these usage quotas, we may not be able to serve your site, or you may receive a polite email from GitHub Support suggesting strategies for reducing your site's impact on our servers."

Pages overage is therefore throttling and a polite email, not an invoice. GitHub Free includes "GitHub Pages in public repositories" (<https://docs.github.com/en/get-started/learning-about-github/githubs-plans>, fetched 2026-09-18).

`pages.yml` here copies three HTML files into `site/` and deploys. The built game is one file; there is no bundle of assets to blow through 1 GB. The build-per-hour soft limit is the one to watch, because `pages.yml` triggers on every push to `main` that touches `game/**`, and `news.yml` commits a rebuilt `game/vibe-map.html` weekly.

### A.5 Git LFS

Source: <https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-storage-and-bandwidth-usage>, fetched 2026-09-18.

> "When you **download** a Git LFS file, the bandwidth you use is included in the **repository owner's bandwidth usage**."

> "Forking and pulling a repository counts against the parent repository's bandwidth usage."

Included per account: GitHub Free and GitHub Pro each 10 GiB bandwidth and 10 GiB storage (same page). Without a payment method and with a zero budget, "Git LFS usage is blocked for the rest of the calendar month."

This is the one GitHub product where other people's actions bill the repository owner directly. **This repository uses no LFS** (no `.gitattributes`), and template repositories cannot use it anyway: "Your template repository cannot include files stored using Git LFS" (<https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository>, fetched 2026-09-18).

### A.6 Spending limits and budgets

Source: <https://docs.github.com/en/billing/tutorials/set-up-budgets>, fetched 2026-09-18.

> "To create a new budget, click **New budget**"

> "This option is not available for user-level budgets, which always enforce a hard stop."

That second sentence is the important one for a personal account: a user-level budget is a hard stop by construction, not an alert. The page names Codespaces, GitHub Advanced Security, Copilot AI credits and Spark AI credits as budgetable products, and references Actions and Packages in organization contexts.

**Gap**: the page does not say what the default budget is for a new personal account, and it does not exhaustively enumerate which SKUs a personal budget can scope. Set the budget explicitly rather than assuming a default.

### A.7 Plans

Source: <https://docs.github.com/en/get-started/learning-about-github/githubs-plans>, fetched 2026-09-18. GitHub Free for personal accounts includes:

> "unlimited public repositories with a full feature set, and on unlimited private repositories with a limited feature set"

plus "2,000 minutes per month" of Actions, "120 GitHub Codespaces core hours per month", "15 GB GitHub Codespaces storage per month", and "GitHub Pages in public repositories". GitHub Pro raises Actions to "3,000 GitHub Actions minutes per month" and Codespaces to "180 GitHub Codespaces core hours per month" and "20 GB", and adds protected branches, required reviewers and code owners.

**Gap worth flagging for this repository**: `docs/MAINTAINERS.md` relies on branch protection on `main`, and branch protection appears in the list above as something Pro adds. The page as fetched does not say whether protected branches are available on Free for public repositories, which is the case that matters here. Branch protection demonstrably works on this repository today, so the practical answer is settled by observation; the documented answer is not, and a learner deciding whether to protect a private camp repository should check the plans page rather than trust this report.

### A.8 Copilot Free

Source: <https://docs.github.com/en/copilot/get-started/plans>, fetched 2026-09-18.

> "Limited to 2000 completions per month on Copilot Free."

> "All plans include Copilot CLI and Copilot app."

Copilot Free is restricted to "Auto model selection only" and carries "An allowance of GitHub AI Credits". The agents table shows Copilot Free with "Agent mode" and "Model Context Protocol (MCP)". "Third-party Agents (public preview)" starts at Copilot Pro.

**Gap**: the page does not state a monthly chat-request number for Copilot Free, and it does not say who pays when a Free user's credits run out. Treat the credit allowance as the binding limit and link to the plans page rather than quoting a figure.

### A.9 The Copilot coding agent

Source: <https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent>, fetched 2026-09-18.

> "Copilot cloud agent is available for all paid Copilot plans."

It runs in "its own ephemeral development environment, powered by GitHub Actions" and "uses GitHub Actions minutes and AI credits".

Those Actions minutes are the repository's. On a public repository they are free by A.1; on a private one they are billed to the repository owner. This is the mechanism by which somebody else's use of Copilot could spend the repository owner's Actions allowance.

**Gap**: the page does not say whether coding agent sessions consume premium requests, and it does not mention `AGENTS.md`.

---

## B. Template versus fork

### B.1 What a template copies

Source: <https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template>, fetched 2026-09-18.

> "A new fork includes the entire commit history of the parent repository, while a repository created from a template starts with a single commit."

> "Commits to a fork don't appear in your contributions graph, while commits to a repository created from a template do appear in your contribution graph."

> "A fork can be a temporary way to contribute code to an existing project, while creating a repository from a template starts a new project quickly."

> "branches created from a template have unrelated histories, which means you cannot create pull requests or merge between the branches"

The generator can "include the directory structure and files from all branches in the template, and not just the default branch."

Source: <https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository>, fetched 2026-09-18.

> "Anyone with access to the template repository can generate a new repository with the same directory structure and files as your default branch."

> "Your template repository cannot include files stored using Git LFS."

**Gaps, stated plainly.** Neither page, as fetched, says what happens to **issues, pull requests, stars, repository settings, Actions secrets, or Pages configuration** when a repository is generated from a template. Both pages describe only directory structure, files and branches. Do not tell a learner "the template copies your settings" or "the template does not copy secrets" on the strength of these pages; the safe statement is the one the docs do make: a generated repository gets the files and the directory structure, in a single commit, with unrelated history.

Neither page states whether a repository created from a template can itself be marked as a template, nor which permission level is required to mark one. That question is unanswered by the first-party pages fetched here.

Empirically, `tpetedb/vibe-map` is already a template: `gh repo view tpetedb/vibe-map --json isTemplate` returns `"isTemplate":true`, with `"forkCount":0`.

### B.2 What a fork carries

Source: <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/about-forks>, fetched 2026-09-18.

> "Forks are repositories that start as copies of another repository, called the upstream repository. A fork has its own settings and permissions but stays connected to the upstream repository."

> "A fork's visibility is tied to the upstream repository's repository network."

> "All repositories in a repository network share the same visibility setting. A repository network includes the upstream repository, its forks, and forks of those forks."

On visibility changes: when "a public repository is made private," its public forks "stay public in a separate network"; when "a private repository is made public," private forks "stay private but disconnect into separate private networks."

**Gap**: the page as fetched does not explicitly state that you can open a pull request from a fork back to the upstream repository, although the whole fork-and-pull model rests on it and the approval page in A.2 describes exactly those runs ("a contributor's pull request from a fork").

The practical consequences for a learner who forks rather than generates:

- A fork of this public repository **cannot be made private**. A learner's camp, with their notes and their scores, would be public. That alone decides the question for a course that writes an Obsidian vault of personal notes.
- Their commits do not appear in their contributions graph.
- Their pulls of LFS objects would count against the parent's bandwidth (A.5), though this repository has none.
- Scheduled workflows in their fork are off by default (A.2), so `news.yml` and `nightly.yml` would not fire for them without an explicit enable, which is the desired behaviour.
- Their entire history is the upstream history, which is exactly wrong for "this is my camp, and its first commit is mine."

### B.3 Templates and Codespaces

Codespaces billing follows the account that owns the codespace, whichever way the repository was created (A.3). No fetched page says that repositories created from templates behave differently from any other repository with respect to Codespaces. The only template-plus-Codespaces cost worth naming is a prebuild configured on the template itself, which bills the template owner (A.3).

---

## C. Coding harnesses

Everything in this section is per vendor, first party, fetched 2026-09-18.

### C.1 Claude Code

**How you pay.** <https://code.claude.com/docs/en/setup>:

> "Claude Code requires a Pro, Max, Team, Enterprise, or Console account. The free claude.ai plan does not include Claude Code access."

Also from that page, on billing routes: "You can also use Claude Code with a third-party API provider like Amazon Bedrock, Google Cloud's Agent Platform, or Microsoft Foundry." And <https://code.claude.com/docs/en/costs>: "Claude Code charges by API token consumption. For subscription plan pricing (Pro, Max, Team, Enterprise), see claude.com/pricing."

**Install.** "curl -fsSL https://claude.ai/install.sh | bash", or `brew install --cask claude-code`, or `npm install -g @anthropic-ai/claude-code` (<https://code.claude.com/docs/en/setup>).

**Print mode.** <https://code.claude.com/docs/en/cli-reference>:

> `claude -p "query"` - "Query via SDK, then exit"

> `--print`, `-p` - "Print response without interactive mode"

> `--output-format` - "Specify output format for print mode (options: `text`, `json`, `stream-json`)"

Piping is documented: `cat logs.txt | claude -p "explain"`.

**Memory file.** <https://code.claude.com/docs/en/memory>:

> "Claude Code reads `CLAUDE.md`, not `AGENTS.md`. If your repository already uses `AGENTS.md` for other coding agents, create a `CLAUDE.md` that imports it so both tools read the same instructions without duplicating them."

This is exactly what this repository does: `CLAUDE.md` is `@AGENTS.md` plus Claude-only extras. The onboarding copy in `src/body.html` already says so.

**Skills, hooks, subagents, MCP.** All documented and all first party: skills at `/docs/en/skills`, hooks at `/docs/en/hooks`, subagents in `.claude/agents/` (<https://code.claude.com/docs/en/sub-agents>: "Claude Code scans `.claude/agents/` and `~/.claude/agents/` recursively"), MCP at `/docs/en/mcp`. Subagents work headless: "In non-interactive mode and the Agent SDK, set `CLAUDE_AGENT_SDK_DISABLE_BUILTIN_AGENTS=1` to remove all built-in types and supply only your own."

**Headless in CI.** <https://code.claude.com/docs/en/github-actions>. Authentication is either `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN`, "an OAuth token that authenticates with your Claude subscription, available on Pro, Max, Team, and Enterprise plans." Cost, in the vendor's own words:

> "GitHub Actions minutes: the Claude Code GitHub Action runs on GitHub-hosted runners, which consume your GitHub Actions minutes."

> "API tokens: each interaction consumes tokens based on the length of prompts and responses... If you authenticate with an OAuth token, runs use your Claude subscription instead of API billing."

And an access control worth knowing before wiring anything like this into a public repository: "on issue and pull request events, the triggering user must have write access to the repository", and bot actors are rejected unless listed.

**Sign-in inside a codespace.** Not covered by any page fetched. The general flow is "log in by running `claude` and following the browser prompts", or set `ANTHROPIC_API_KEY`. Whether the browser handoff works inside a Codespaces terminal is **not documented on the pages fetched**; do not assert it either way in course copy.

### C.2 OpenAI Codex CLI

**How you pay.** <https://learn.chatgpt.com/docs/codex/cli>: "choose **Sign in with ChatGPT** or another available sign-in method". The page does not enumerate which ChatGPT plans include Codex, so link the plans page rather than naming tiers. For automation, <https://learn.chatgpt.com/docs/non-interactive-mode>: "API keys are the right default for automation because they are simpler to provision and rotate", with the variable `CODEX_API_KEY`.

**Install.** From the CLI page: `curl -fsSL https://chatgpt.com/codex/install.sh | sh`, `npm install -g @openai/codex`, and `brew install --cask codex`.

**Print mode.** `codex exec "..."`. From the non-interactive page:

> "Codex streams progress to `stderr` and prints only the final agent message to `stdout`"

Default sandbox is read-only; `--sandbox workspace-write` and `--sandbox danger-full-access` escalate. `--json` emits JSON Lines; `--output-schema` enforces a schema.

**Memory file.** AGENTS.md, natively: the CLI page documents `/init` to "create an AGENTS.md file with instructions for Codex."

**MCP.** Documented: "add local or remote MCP servers".

**CI.** The non-interactive page points at `openai/codex-action`, which "starts a secure proxy for the OpenAI API key".

**Gaps**: hooks and subagents for Codex are not covered by any page fetched here. Skills in the Agent Skills sense are not mentioned. Sign-in inside a codespace is not documented.

### C.3 Gemini CLI

**How you pay.** <https://github.com/google-gemini/gemini-cli> README: signing in with a personal Google account gives "60 requests/min and 1,000 requests/day" with Gemini 3 models and a 1M token context window. A Gemini API key from AI Studio gives "1000 requests/day" with model selection and usage-based billing. Vertex AI is the enterprise route, via `GOOGLE_API_KEY` and `GOOGLE_GENAI_USE_VERTEXAI=true`.

This is the most generous free hosted route of the five.

**Install.** `npx @google/gemini-cli`, `npm install -g @google/gemini-cli`, `brew install gemini-cli`, `sudo port install gemini-cli`.

**Print mode.** <https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/headless.md>: headless mode activates "when the CLI is run in a non-TTY environment or when providing a query with the `-p` (or `--prompt`) flag." `--output-format json` returns "a single JSON object containing the response and usage statistics"; the streaming form emits newline-delimited events. Exit codes: `0` success, `1` general or API error, `42` input validation failure, `53` turn limit exceeded.

**Memory file.** <https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/gemini-md.md>: the default is `GEMINI.md`, with a global file at `~/.gemini/GEMINI.md`, and the name is configurable through `context.fileName`, which "accepts an array of filenames like `["AGENTS.md", "CONTEXT.md", "GEMINI.md"]`". So AGENTS.md works, but only after configuration.

**Hooks, subagents, MCP, extensions, custom commands.** All present in the docs index (<https://github.com/google-gemini/gemini-cli/blob/main/docs/index.md>): "**Subagents:** Using specialized agents for specific tasks", "**Hooks:** Customize Gemini CLI behavior with scripts", "**MCP servers**", "**Extensions:** Extend Gemini CLI with new tools and capabilities", "**Custom commands:** Personalized shortcuts".

**Gap**: sign-in inside a codespace is not documented on the pages fetched.

### C.4 GitHub Copilot: the CLI and the coding agent

**How you pay.** <https://docs.github.com/en/copilot/how-tos/set-up/install-copilot-cli>: "An active GitHub Copilot subscription". <https://docs.github.com/en/copilot/get-started/plans>: "All plans include Copilot CLI and Copilot app", so Copilot Free qualifies, within its credit allowance. <https://docs.github.com/en/copilot/concepts/agents/about-copilot-cli>: "Each time you interact with Copilot in Copilot CLI's interactive interface, or use Copilot CLI programmatically, AI credits are consumed based on the number of tokens processed."

**Install.** `npm install -g @github/copilot`, `brew install --cask copilot-cli`, `winget install GitHub.Copilot`, or `curl -fsSL https://gh.io/copilot-install | bash`.

**Print mode.** <https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-programmatic-reference>: `copilot -p PROMPT` will "Execute a prompt in non-interactive mode. The CLI runs the prompt and exits when done." Three further flags matter for a bridge that pipes the output:

> `-s`: "Suppress stats and decoration, outputting only the agent's response. Ideal for piping output in scripts."

> `--no-ask-user`: "Prevent the agent from pausing to seek additional user input."

> `--allow-all-tools`: "Allow every tool to run without explicit permission for each tool."

Non-interactive authentication uses, in precedence order, `COPILOT_GITHUB_TOKEN`, `GH_TOKEN`, `GITHUB_TOKEN`.

**Memory file, hooks, custom agents, MCP.** <https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli>: custom instructions from `.github/copilot-instructions.md` are "automatically included", and "Agent files such as `AGENTS.md`" are supported. "Copilot CLI comes with the GitHub MCP server already configured". <https://docs.github.com/en/copilot/concepts/agents/about-copilot-cli>: "Custom agents allow you to create different specialized versions of Copilot for different tasks" and "Hooks allow you to execute custom shell commands at key points during agent execution."

**Sign-in.** "If you are not currently logged in to GitHub, you'll be prompted to use the `/login` slash command." In a codespace, `GITHUB_TOKEN` is present in the environment, which by the precedence list above would authenticate the CLI. That inference is **not** stated on any page fetched, so it is flagged as an inference, not a documented fact.

**The coding agent.** See A.9: paid plans only, runs on GitHub Actions, "uses GitHub Actions minutes and AI credits".

**Gap**: no fetched page states an exit-code contract for `copilot -p`.

### C.5 OpenCode, with any provider key or a local model through Ollama

**How you pay.** <https://opencode.ai/docs/providers/>: bring your own API key, stored by `/connect` in `~/.local/share/opencode/auth.json`. OpenCode Zen is the curated hosted option ("Sign in to **OpenCode Zen** and click **Create API Key**"); OpenCode Go is "a low cost subscription plan that provides reliable access to popular open coding models"; existing subscriptions such as ChatGPT Plus, GitHub Copilot and GitLab Duo can be connected directly.

**The free route.** The same page documents Ollama as an OpenAI-compatible provider, no key:

```json
{
  "provider": {
    "ollama": {
      "npm": "@ai-sdk/openai-compatible",
      "baseURL": "http://localhost:11434/v1",
      "models": {"llama2": {"name": "Llama 2"}}
    }
  }
}
```

LM Studio and llama.cpp are listed alongside it on the same terms.

**Install.** <https://opencode.ai/docs/>: `curl -fsSL https://opencode.ai/install | bash`, `npm install -g opencode-ai`, `brew install anomalyco/tap/opencode`, `paru -S opencode-bin`.

**Print mode.** <https://opencode.ai/docs/cli/>: "Run opencode in non-interactive mode by passing a prompt directly", syntax `opencode run [message..]`. Flags: `--model`/`-m` "Model to use in the form of provider/model", `--agent`, `--format` ("default (formatted) or json (raw JSON events)"), `--attach`, `--share`, `--continue`/`-c`, `--session`/`-s`. A headless server can be started and attached to: `opencode run --attach http://localhost:4096 "prompt here"`.

**Memory file.** <https://opencode.ai/docs/rules/>: local `AGENTS.md` or `CLAUDE.md` traversing up from the current directory, then `~/.config/opencode/AGENTS.md`, then `~/.claude/CLAUDE.md` as a Claude Code fallback. "The first matching file wins in each category. For example, if you have both `AGENTS.md` and `CLAUDE.md`, only `AGENTS.md` is used."

**Agents.** The `--agent` flag on `opencode run` is the documented selector.

**Gaps**: hooks and MCP for OpenCode are not covered by the three pages fetched. Do not claim either in course copy without a fetch of the relevant page.

### C.6 Ollama

Source: <https://docs.ollama.com/quickstart>, fetched 2026-09-18.

> "Run Gemma 4 E2B on your computer. No API key required."

> "For local models, skip this step and select Local"

The OpenAI-compatible endpoint is `http://localhost:11434/v1/chat/completions`, which is the `baseURL` OpenCode's Ollama config points at. An API key is needed only for Ollama's cloud models.

---

## D. A free route

A learner with no subscription at all can do the following, each backed above:

| What | How | Cost |
|---|---|---|
| Play the whole game | `curl` the single HTML file, or the hosted Pages copy. Path A in `docs/QUICKSTART.md`. | Nothing. No account, no install, works offline. |
| Every lesson's text | The game carries the full lesson, the commands and the definition of done for each workstream. | Nothing. |
| The CLI, the checks, the XP, the vault | `uv tool install`, `vibe new`, `vibe check`, `vibe done`, `vibe vault lint`, Obsidian. `vibemap/quests.py` only reads `workspace/`; nothing in the quest path calls a model. | Nothing beyond uv, git and Obsidian, all free. |
| SQL and Python workstreams | DuckDB and python3 over `workspace/data/scores.csv`. | Nothing. |
| Publish their game | GitHub Pages from a public repository, Free plan (A.7), `_github/workflows/pages.yml` in the template. | Nothing, within the soft limits in A.4. |
| A coding agent, hosted | Gemini CLI signed in with a personal Google account: "60 requests/min and 1,000 requests/day". | Nothing. |
| A coding agent, in the terminal and in the editor | Copilot Free: "All plans include Copilot CLI and Copilot app", limited to "Auto model selection only" and "2000 completions per month". | Nothing, within the credit allowance. |
| A coding agent, fully local and offline | OpenCode plus Ollama: "No API key required". | Nothing but disk, RAM and time. |

What they will miss:

- **Claude Code itself.** "The free claude.ai plan does not include Claude Code access." Everything the course phrases as a Claude Code feature (the `/hooks` menu, `.claude/skills/`, `.claude/agents/`, `claude mcp add`, `/rewind`, `/memory`) needs a paid Claude plan. The equivalents exist elsewhere: hooks and custom agents in Copilot CLI, hooks and subagents in Gemini CLI, agents in OpenCode, MCP in all four. The concepts transfer; the exact commands in `src/game/87-onboarding.js` and in the workstream sheets do not.
- **Model quality on a local model.** No first-party page claims a local 7B model performs like a hosted frontier model, and this report does not either.
- **Copilot Free's model choice**, which is "Auto model selection only", so a workstream that asks a learner to compare models cannot be done on Copilot Free.
- **The Copilot coding agent**, which is "available for all paid Copilot plans" only.

What the title screen says today: `src/game/87-onboarding.js` line 119 sets the prerequisite copy to "a Mac or Linux terminal, about fifteen minutes to install the tools, a GitHub account, and a paid plan for Claude, Codex or Gemini." That is honest about a paid plan but misses three free routes that now exist: Gemini CLI on a personal Google account, Copilot Free, and OpenCode with Ollama. `src/body.html` line 135 says "You need two things: a terminal, and Claude Code signed in", and line 102 says to sign in with "your Claude account (Pro, Max, Team or Enterprise)", which matches the setup page and is correct as far as it goes. `docs/QUICKSTART.md` step 3 lists all five providers but says "Everything that talks to a model runs the CLI you already pay for", which is now too narrow.

---

## 1. Every way this project could put a cost on the repository owner

Ordered by how plausible the cost is today. "Closed" means what to do or keep doing.

| # | Mechanism | Who pays now | Why | How to close it |
|---|---|---|---|---|
| 1 | **Actions minutes on `ci.yml`, `nightly.yml`, `news.yml`, `pages.yml`, including the two `macos-latest` jobs** | Nobody | "GitHub Actions usage is free for ... public repositories that use standard GitHub-hosted runners" (A.1) | Keep the repository public. If it is ever made private, the macOS jobs cost about ten times a Linux minute: move the browser job to `ubuntu-latest` and set a hard budget first (A.6). |
| 2 | **Workflow runs from fork pull requests** | Nobody | Same sentence as above, plus first-time contributors need approval by default (A.2) | Keep the approval setting at "Require approval for all external contributors" in Settings, Actions, Fork pull request workflows. Never use `pull_request_target` in this repository. |
| 3 | **Codespaces opened by learners on this repository, on a repository made from the template, or on a fork** | The learner | "Compute usage is charged to the account that owns the codespace" (A.3) | Already closed by GitHub's model. Say so in the course copy so learners know they are spending their own 120 free hours. |
| 4 | **Codespaces prebuilds** | The repository owner, in storage and Actions minutes (A.3) | Prebuild storage and the prebuild workflow are billed to the account | Do not add a prebuild configuration. There is no `.devcontainer/` today; if one is added for convenience, add it without a prebuild. |
| 5 | **Git LFS bandwidth from clones and forks** | The repository owner: "Forking and pulling a repository counts against the parent repository's bandwidth usage" (A.5) | LFS bandwidth is charged to the parent, not the downloader | Never track a file with LFS here. A template repository cannot contain LFS files anyway, and this repository has no `.gitattributes`. Keep it that way, and keep `game/vibe-map.html` a plain committed file. |
| 6 | **Pages bandwidth and build rate** | Nobody in money; the site may stop being served | Soft limits of 100 GB per month and 10 builds per hour, "we may not be able to serve your site" (A.4) | Keep the site to the handful of HTML files `pages.yml` copies. `pages.yml` is already path-filtered to `game/**`, which keeps the build rate low. Do not add a per-commit asset pipeline. |
| 7 | **The Copilot coding agent, if it is ever enabled on this repository** | The repository owner's Actions minutes and AI credits (A.9) | It runs "powered by GitHub Actions" and "uses GitHub Actions minutes and AI credits" | Do not enable it here. Free on a public repository for the minutes, but it is a live channel into the repository; it needs a paid plan and repository access to trigger, so the exposure is small. |
| 8 | **A Claude Code GitHub Action, if one is ever added** | Actions minutes plus either an API key's bill or the OAuth token holder's subscription (C.1) | "If you authenticate with an OAuth token, runs use your Claude subscription instead of API billing" | Do not add a `@claude` workflow to this public repository with Tom's personal OAuth token in it. If one is ever wanted, note that the action already requires the triggering user to have write access, and that "on public repositories, GitHub withholds secrets from runs triggered by fork pull requests". |
| 9 | **`news.yml` writing to `main` on a schedule** | Nothing in money | `permissions: contents: write`, a weekly cron and `workflow_dispatch` | Not a cost, but it is the one workflow that can change `main` unattended, and it commits a rebuilt `game/vibe-map.html`, which then triggers `pages.yml`. Worth knowing when reading build-rate limits. Scheduled workflows in public repositories also stop after 60 days of inactivity (A.2), so a quiet month means stale news, not a bill. |
| 10 | **The learner's own model spend** | The learner | `vibemap/chat.py` and `vibemap/providers.py` shell out to the learner's local CLI; nothing in this repository holds a key | Already closed by design, and worth stating in the copy: "A browser page cannot reach a terminal subscription, so `vibe chat serve` runs a loopback HTTP bridge" (`vibemap/chat.py`), bound to `127.0.0.1` with a pairing code. |

**The one action to take regardless**: set a personal budget at GitHub with a hard stop, because "user-level budgets ... always enforce a hard stop" (A.6). It costs nothing and turns every entry above into a bounded failure.

---

## 2. Recommendation: template versus fork

**Keep the template. Do not switch to a fork model, and do not advertise forking as the way in.** `tpetedb/vibe-map` is already `isTemplate: true`; the recommendation is to keep it and to sharpen the copy.

The evidence, in order of weight:

1. **A fork of a public repository cannot be private.** "A fork's visibility is tied to the upstream repository's repository network" and "All repositories in a repository network share the same visibility setting" (B.2). This course writes an Obsidian vault of a learner's own notes, their scores and their state into their repository. Making that public by construction is the wrong default, and it is not fixable inside the fork model.
2. **A camp should start with the learner's own first commit.** "a repository created from a template starts with a single commit" (B.1). `vibe new` already makes the camp's first commit; `nightly.yml` tests exactly that. A fork would instead hand the learner several hundred commits of engine history they did not write.
3. **Contributions count.** "Commits to a fork don't appear in your contributions graph, while commits to a repository created from a template do appear in your contribution graph" (B.1). For a course whose reward loop is XP and visible progress, the green squares matter.
4. **No accidental upstream pull requests.** "branches created from a template have unrelated histories, which means you cannot create pull requests or merge between the branches" (B.1). A fork puts a "Contribute" button on every learner's camp, aimed at Tom's repository.
5. **No LFS bandwidth exposure.** "Forking and pulling a repository counts against the parent repository's bandwidth usage" (A.5). Irrelevant today because there is no LFS, but the template route removes the whole class of risk permanently, and a template repository cannot hold LFS files anyway.
6. **The template is not even the main route.** `README.md` already says: "Most people should not: `uv tool install git+https://github.com/tpetedb/vibe-map` and `vibe new` give you a camp without the engine." That is the right ordering, and it should stay: the installed `vibe` command plus `vibe new` first, the template second for people who want the engine, and forking never.

Two honest caveats, from the gaps in B.1:

- The GitHub pages fetched do **not** say whether a repository generated from a template carries over settings, Actions secrets, issues or Pages configuration. Course copy must not claim either way. The safe sentence is: "Use this template gives you the files and folders in a single commit, on a history of your own."
- The pages fetched do **not** say whether a repository created from this template can itself be marked as a template. If that matters (a learner wanting to hand their camp to their own team), it needs a separate check against the repository settings page rather than an assertion here.

One change to make in the copy: `src/game/87-onboarding.js` line 54 currently offers "Use this template" as the first thing a newcomer reads, before the install. Given README already says most people should not, the onboarding text should lead with `uv tool install` plus `vibe new` and mention the template second.

---

## 3. Capability matrix

Read against the course features. **works** = documented and directly usable. **partly** = usable with the stated caveat. **not available** = no first-party documentation found, which is stated as "docs silent" where that is the reason.

| Feature | Claude Code | OpenAI Codex CLI | Gemini CLI | GitHub Copilot CLI | OpenCode (any key, or Ollama) |
|---|---|---|---|---|---|
| **Chat bridge** (`vibe chat serve`, one question, streamed) | works: `claude -p "query"`, `--output-format stream-json` | works: `codex exec "..."`, final message on stdout, progress on stderr | works: `gemini -p "..."`, `--output-format stream-json` | partly: `copilot -p PROMPT` works, but add `-s` to "Suppress stats and decoration" and `--no-ask-user` or the bridge streams session furniture and can hang on a question | works: `opencode run "..."`, `--format json` for raw events |
| **`vibe explain`** (one prompt, one answer) | works | works | works | partly: same `-s` and `--no-ask-user` caveat | works |
| **`vibe council`** (twelve prompts, one topic) | works | works | partly: the free Google-account tier is "60 requests/min and 1,000 requests/day", so twelve calls are fine but a loop is not | partly: "AI credits are consumed based on the number of tokens processed"; Copilot Free's allowance is the ceiling | works; free and unmetered against a local Ollama model |
| **Skills** (Agent Skills, `.agents/skills/`) | works: `/docs/en/skills`, and `.claude/skills/` symlinks are already in this repo | not available: docs silent on skills | partly: no "skills" concept, but "Custom commands: Personalized shortcuts" and "Extensions" cover the same ground | partly: "Custom agents allow you to create different specialized versions of Copilot for different tasks", plus custom instructions; no Agent Skills format documented | not available: docs silent on skills; `--agent` selects an agent instead |
| **Hooks** (workstream 4) | works: `/docs/en/hooks`, PreToolUse can block | not available: docs silent on hooks | works: "Hooks: Customize Gemini CLI behavior with scripts" | works: "Hooks allow you to execute custom shell commands at key points during agent execution" | not available: docs silent on hooks in the pages fetched |
| **Subagents** (workstream 8) | works: `.claude/agents/`, and headless too | not available: docs silent on subagents | works: "Subagents: Using specialized agents for specific tasks", plus remote subagents | works: custom agents | partly: `--agent` selects an agent for a run; no delegation model documented |
| **MCP** (workstream 5) | works: `/docs/en/mcp`, `claude mcp add` | works: "add local or remote MCP servers" | works: "MCP servers" in the docs index | works: "Copilot CLI comes with the GitHub MCP server already configured" | not available: docs silent in the pages fetched |
| **Scheduled headless runs** (workstream 8) | works: `claude -p` in cron or Actions; `anthropics/claude-code-action` with `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN` | works: `codex exec` is documented for "CI, pre-merge checks, scheduled jobs"; `CODEX_API_KEY` for automation; `openai/codex-action` for GitHub | works: headless mode triggers on a non-TTY; documented exit codes 0, 1, 42, 53 | works: `copilot -p` with `COPILOT_GITHUB_TOKEN`, `GH_TOKEN` or `GITHUB_TOKEN`; no documented exit-code contract | works: `opencode run`, and a headless server to attach to |
| **Reads AGENTS.md** | partly: "Claude Code reads `CLAUDE.md`, not `AGENTS.md`"; the documented fix is `@AGENTS.md` in CLAUDE.md, which this repo already does | works: `/init` creates AGENTS.md | partly: default is `GEMINI.md`; `context.fileName` accepts `["AGENTS.md", ...]` | works: "Agent files such as `AGENTS.md`" plus `.github/copilot-instructions.md` | works: AGENTS.md first, CLAUDE.md as fallback |
| **How you pay** | Pro, Max, Team, Enterprise or Console. "The free claude.ai plan does not include Claude Code access." | Sign in with ChatGPT, or an API key (`CODEX_API_KEY`) for automation | Free with a personal Google account, or an AI Studio key, or Vertex AI | Any Copilot plan, including Free ("All plans include Copilot CLI") | Bring your own key, OpenCode Zen, OpenCode Go, a connected subscription, or a local model for nothing |
| **Sign-in inside a codespace** | not documented | not documented | not documented | partly: `/login` interactively; the token precedence list (`COPILOT_GITHUB_TOKEN`, `GH_TOKEN`, `GITHUB_TOKEN`) suggests a codespace's built-in token would work, but no page states it | not documented |

The same matrix as data `vibemap/providers.py` could load. Values are `works`, `partly`, `unavailable` or `undocumented`; every `partly` carries its reason in `notes`.

```json
{
  "version": 1,
  "checked": "2026-09-18",
  "features": [
    "chat_bridge",
    "explain",
    "council",
    "skills",
    "hooks",
    "subagents",
    "mcp",
    "scheduled_headless",
    "agents_md"
  ],
  "providers": {
    "claude": {
      "label": "Claude Code",
      "print_argv": ["claude", "-p", "{prompt}"],
      "pays": "subscription",
      "free_tier": false,
      "docs": "https://code.claude.com/docs/en/cli-reference",
      "memory_file": "CLAUDE.md",
      "capabilities": {
        "chat_bridge": "works",
        "explain": "works",
        "council": "works",
        "skills": "works",
        "hooks": "works",
        "subagents": "works",
        "mcp": "works",
        "scheduled_headless": "works",
        "agents_md": "partly"
      },
      "notes": {
        "agents_md": "Reads CLAUDE.md, not AGENTS.md; the documented fix is an @AGENTS.md import.",
        "pays": "Requires Pro, Max, Team, Enterprise or Console. The free claude.ai plan does not include Claude Code."
      }
    },
    "codex": {
      "label": "OpenAI Codex CLI",
      "print_argv": ["codex", "exec", "{prompt}"],
      "pays": "subscription_or_api_key",
      "free_tier": false,
      "docs": "https://learn.chatgpt.com/docs/non-interactive-mode",
      "memory_file": "AGENTS.md",
      "capabilities": {
        "chat_bridge": "works",
        "explain": "works",
        "council": "works",
        "skills": "undocumented",
        "hooks": "undocumented",
        "subagents": "undocumented",
        "mcp": "works",
        "scheduled_headless": "works",
        "agents_md": "works"
      },
      "notes": {
        "chat_bridge": "Progress goes to stderr, the final message to stdout. Default sandbox is read-only.",
        "scheduled_headless": "CODEX_API_KEY for automation; openai/codex-action on GitHub."
      }
    },
    "gemini": {
      "label": "Gemini CLI",
      "print_argv": ["gemini", "-p", "{prompt}"],
      "pays": "free_tier_or_api_key",
      "free_tier": true,
      "docs": "https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/headless.md",
      "memory_file": "GEMINI.md",
      "capabilities": {
        "chat_bridge": "works",
        "explain": "works",
        "council": "partly",
        "skills": "partly",
        "hooks": "works",
        "subagents": "works",
        "mcp": "works",
        "scheduled_headless": "works",
        "agents_md": "partly"
      },
      "notes": {
        "council": "A personal Google account is 60 requests per minute and 1,000 per day.",
        "skills": "No Agent Skills format; custom commands and extensions cover the same ground.",
        "agents_md": "Default is GEMINI.md; context.fileName can be set to AGENTS.md.",
        "scheduled_headless": "Exit codes 0 success, 1 error, 42 input validation, 53 turn limit."
      }
    },
    "copilot": {
      "label": "GitHub Copilot CLI",
      "print_argv": ["copilot", "-p", "{prompt}", "-s", "--no-ask-user"],
      "pays": "subscription",
      "free_tier": true,
      "docs": "https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-programmatic-reference",
      "memory_file": "AGENTS.md",
      "capabilities": {
        "chat_bridge": "partly",
        "explain": "partly",
        "council": "partly",
        "skills": "partly",
        "hooks": "works",
        "subagents": "works",
        "mcp": "works",
        "scheduled_headless": "works",
        "agents_md": "works"
      },
      "notes": {
        "chat_bridge": "Needs -s to suppress stats and decoration, and --no-ask-user so it cannot block on a question.",
        "council": "AI credits are consumed per token; Copilot Free's allowance is the ceiling.",
        "skills": "Custom agents and custom instructions, not the Agent Skills format.",
        "scheduled_headless": "COPILOT_GITHUB_TOKEN, then GH_TOKEN, then GITHUB_TOKEN. No documented exit-code contract."
      }
    },
    "opencode": {
      "label": "OpenCode",
      "print_argv": ["opencode", "run", "{prompt}"],
      "pays": "byo_key_or_local",
      "free_tier": true,
      "docs": "https://opencode.ai/docs/cli/",
      "memory_file": "AGENTS.md",
      "capabilities": {
        "chat_bridge": "works",
        "explain": "works",
        "council": "works",
        "skills": "undocumented",
        "hooks": "undocumented",
        "subagents": "partly",
        "mcp": "undocumented",
        "scheduled_headless": "works",
        "agents_md": "works"
      },
      "notes": {
        "council": "Free and unmetered against a local Ollama model.",
        "subagents": "--agent selects an agent for a run; no delegation model documented.",
        "pays": "Bring your own key, OpenCode Zen, OpenCode Go, a connected subscription, or Ollama at http://localhost:11434/v1 for nothing."
      }
    }
  }
}
```

---

## 4. Corrections needed in `vibemap/providers.py`

Checked every field of every entry against the vendor page cited beside it. The verdict first: **all five install commands and all five print-mode invocations are correct as written.** The corrections below are about output hygiene, one stale docs link, and one missing fact.

**Correct, confirmed against first-party docs on 2026-09-18:**

- `claude`: `["claude", "-p", p]` and `curl -fsSL https://claude.ai/install.sh | bash` both appear verbatim in the Claude Code docs.
- `codex`: `["codex", "exec", p]` and `brew install --cask codex` both appear verbatim on `learn.chatgpt.com/docs/codex/cli`.
- `gemini`: `["gemini", "-p", p]` and `brew install gemini-cli` both appear in the README.
- `copilot`: `["copilot", "-p", p]` and `brew install --cask copilot-cli` both appear in GitHub's docs.
- `opencode`: `["opencode", "run", p]` and `brew install anomalyco/tap/opencode` both appear on opencode.ai.

**The corrections:**

1. **Copilot's print mode needs `-s` and `--no-ask-user`.** GitHub documents `-s` as "Suppress stats and decoration, outputting only the agent's response. Ideal for piping output in scripts", and `--no-ask-user` as "Prevent the agent from pausing to seek additional user input." Without the first, `stream()` pushes session metadata into the chat panel. Without the second, a clarifying question turns into a 180 second hang ending in the `DEFAULT_TIMEOUT` kill in `chat.py`. Change the argv to `["copilot", "-p", p, "-s", "--no-ask-user"]`.

2. **ANSI is stripped from stderr but not from streamed stdout.** `stream()` yields `proc.stdout` lines straight to the caller, and `_strip_ansi` is applied only to `stderr` in both `ask()` and `stream()`. Codex, Gemini and Copilot all colour their terminal output. The chat panel renders whatever arrives, so escape sequences reach the page. Either apply `_strip_ansi` per yielded line in `stream()` and to `result.stdout` in `ask()`, or set `NO_COLOR=1` in `_clean_env()`, which is the cheaper fix and matches how the pet code already respects `NO_COLOR`.

3. **`_strip_ansi` only matches SGR sequences.** The pattern `\x1b\[[0-9;]*m` misses cursor movement, erase-line and the `\x1b[?25l` cursor-hide that progress spinners emit. Widen it to `\x1b\[[0-9;?]*[a-zA-Z]`.

4. **The `codex` docs URL is a redirect, not a 404, but it is not the page the entry means.** `https://learn.chatgpt.com/docs/non-interactive-mode` resolves and is the right topic. Leave it, but note that the canonical CLI landing page is now `https://learn.chatgpt.com/docs/codex/cli` after a 308 from `developers.openai.com/codex/cli`. If a single link per provider is wanted, the CLI page is the better first stop for a learner and the non-interactive page is the better one for this module. Prefer the non-interactive page and keep it.

5. **The `gemini` docs URL points at the repository root.** `https://github.com/google-gemini/gemini-cli` is correct but unhelpful for the thing this module does. Point it at the headless page: `https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/headless.md`.

6. **`ProviderMissing` and the quickstart both imply every provider costs money.** `QUICKSTART.md` step 3 says "Everything that talks to a model runs the CLI you already pay for". Gemini CLI on a personal Google account, Copilot Free, and OpenCode against Ollama are all free. The `Provider` dataclass has no field to express this, so nothing downstream can offer a learner a free route. Add `free_tier: bool` (and optionally `pays: str`) to `Provider`, populated from the JSON above, and use it in the `vibe provider` output and in the chat panel's "not installed" message.

7. **Gemini's documented exit codes deserve a specific error.** `42` is "Input validation failure" and `53` is "Turn limit exceeded". Both surface today as the generic `f"{provider.label} exited {result.returncode}"`. A learner who hits 53 on a council run should be told the turn limit was reached, not given a number.

8. **The module docstring's date is stale.** It says "checked 2026-09-16"; the checks above are 2026-09-18. Bump it when the argv changes land.

9. **`ask()`'s Claude-only retry keys on an English substring.** `if "model catalog" in result.stderr` is a heuristic against a message that can change. It is documented behaviour in `QUICKSTART.md`'s troubleshooting section, so it should stay, but it deserves a comment saying it is a string match on an error message and is expected to rot, which the existing comment does not say.

**Not a correction, but worth recording**: nothing in `providers.py` or `chat.py` holds or reads a model API key. `_clean_env()` strips the parent Claude Code session's variables and passes everything else through, so the learner's own CLI credentials are what authenticate. That is the right design and it is the reason item 10 in the cost table is already closed.

---

## Sources

Every page below was fetched with WebFetch on 2026-09-18.

- <https://docs.github.com/en/billing/concepts/product-billing/github-actions>
- <https://docs.github.com/en/billing/concepts/product-billing/github-codespaces>
- <https://docs.github.com/en/codespaces/prebuilding-your-codespaces/about-github-codespaces-prebuilds>
- <https://docs.github.com/en/actions/how-tos/manage-workflow-runs/approve-runs-from-forks>
- <https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows>
- <https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository>
- <https://docs.github.com/en/billing/tutorials/set-up-budgets>
- <https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits>
- <https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-storage-and-bandwidth-usage>
- <https://docs.github.com/en/get-started/learning-about-github/githubs-plans>
- <https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template>
- <https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository>
- <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/about-forks>
- <https://docs.github.com/en/copilot/get-started/plans>
- <https://docs.github.com/en/copilot/how-tos/set-up/install-copilot-cli>
- <https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli>
- <https://docs.github.com/en/copilot/concepts/agents/about-copilot-cli>
- <https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-programmatic-reference>
- <https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent>
- <https://code.claude.com/docs/en/setup>
- <https://code.claude.com/docs/en/cli-reference>
- <https://code.claude.com/docs/en/costs>
- <https://code.claude.com/docs/en/memory>
- <https://code.claude.com/docs/en/sub-agents>
- <https://code.claude.com/docs/en/github-actions>
- <https://learn.chatgpt.com/docs/codex/cli>
- <https://learn.chatgpt.com/docs/non-interactive-mode>
- <https://github.com/google-gemini/gemini-cli>
- <https://github.com/google-gemini/gemini-cli/blob/main/docs/index.md>
- <https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/headless.md>
- <https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/gemini-md.md>
- <https://opencode.ai/docs/>
- <https://opencode.ai/docs/cli/>
- <https://opencode.ai/docs/providers/>
- <https://opencode.ai/docs/rules/>
- <https://docs.ollama.com/quickstart>

Repository files read: `vibemap/providers.py`, `vibemap/chat.py`, `.github/workflows/ci.yml`, `.github/workflows/news.yml`, `.github/workflows/nightly.yml`, `.github/workflows/pages.yml`, `vibemap/data/template/_github/workflows/pages.yml`, `docs/QUICKSTART.md`, `src/body.html`, `src/game/87-onboarding.js`, `README.md`.
