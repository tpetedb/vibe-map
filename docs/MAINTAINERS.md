# Maintainers: how this repository is laid out and why

Read this before changing anything. It explains the three zones, which one a file belongs to, and how a change in one reaches the others. The learner-facing version of the same idea is the `README.md` that `vibe new` writes into a camp.

## The problem it solves

A learner should start in an empty folder that is theirs and build up from there. The product that makes that possible (the game, the `vibe` command, the checks, the tests) is a lot of code, and it should not be lying around in the learner's folder, because a beginner cannot tell "the thing I am learning with" from "the thing I am building" from "the settings that make my agent behave". Three concerns, three homes.

## Three zones

```mermaid
flowchart LR
  P["Product (this repository)<br/>src/, vibemap/, tools/, tests/"]:::proc
  T[("Template<br/>vibemap/data/template/")]:::store
  F[("Fork source<br/>vibemap/data/fork_source/")]:::store
  C["A camp (a learner's folder)<br/>workspace/, vault/, config/camp.toml, .agents/, .claude/"]:::term
  H["Hosted game<br/>tpetedb.github.io/vibe-map"]:::io
  I["Installed vibe command<br/>uv tool install vibe-map"]:::io
  P -->|"just build, release"| H
  P -->|"tag, uv tool install"| I
  P -->|"tools/sync_template.py"| T
  P -->|"tools/sync_fork_source.py"| F
  F -->|"vibe fork copies"| C
  I -->|"vibe new copies"| C
  H -->|"progress code"| C
  classDef term fill:#00A86B,stroke:#00D084,color:#000000
  classDef proc fill:#0067A5,stroke:#0088CC,color:#FFFFFF
  classDef io fill:#FF8C1A,stroke:#FFA94D,color:#000000
  classDef store fill:#9A2A2A,stroke:#F04923,color:#FFFFFF
```

| Zone | Where | What belongs there | Who edits it |
|---|---|---|---|
| **Product** | `src/`, `game/vibe-map.html`, `vibemap/` (except `data/template/`), `tools/`, `tests/`, `pyproject.toml`, `uv.lock`, `docs/` | Everything that makes the course work: the game's source and its one-file build, the terminal companion, the checks and XP, the vault builder, the tech tree, the tests. | Maintainers and their agents, through `just verify` and a PR. |
| **Template** | `vibemap/data/template/` | The skeleton of a camp: `README.md`, `AGENTS.md`, `CLAUDE.md`, `config/camp.toml`, `justfile`, `env.example`, `workspace/README.md`, `_gitignore`, `_claude/` (hook and subagent), `_agents/skills/` (the learner skills), `_github/workflows/pages.yml`, `_github/CODEOWNERS` (a teaching example), `_devcontainer/` (the camp's Codespaces container, light: no Playwright). Dot-folders are stored with an underscore so packaging and git never skip them; `vibe new` puts the dots back. | Maintainers. The skills, the hook and the subagent are copied from this repository's own `.agents/` and `.claude/` by `tools/sync_template.py`; a test fails when they drift. |
| **Workspace** | `workspace/` in a camp, and in this repository | The learner's own work: `workspace/game/index.html` (workstream 1), `workspace/data/scores.csv`, `workspace/sql/`, `workspace/python/` (workstream 3), `workspace/artifacts/<id>/` (what an artifact's Do it for real task asked them to build), `workspace/mentors/<id>/` (the exercise a mentor set), `workspace/forks/vibe-map/` (their own copy of the game, from `vibe fork`), the island folders `workspace/winter/`, `workspace/desert/`, `workspace/specs/`, `workspace/jobs/`, `workspace/evals/`, `workspace/agents/` and `workspace/dotfiles/`, and anything else. Nothing in the product depends on its contents; the checks in `vibemap/quests.py` only read it. | The learner. In this repository the folder holds the worked example (Lotte's game, the sample scores) so the tests and the play-through have something to check. |

`config/camp.toml` is this checkout's journey configuration, which is what makes it a valid camp; `docs/CONFIG.md` has the three configuration levels and the table of which setting lives where. Three more things sit at the top level of the product and belong to it: `data/news.json` (the world feed `vibe news` pulls from `vibemap/data/sources.json`, baked into the game by the build and copied to `game/news.json` for the runtime refresh; a camp keeps its copy in `.vibe/`), `scripts/setup.sh` (the machine setup for a product checkout) and `HANDOVER.md` (the note for the next session). The remaining top-level files are this repository's own **configuration for agents and CI**: `AGENTS.md`, `CLAUDE.md`, `.agents/skills/` (fifteen skills; `develop-camp` is product-only and stays out of the template), `.claude/` (the backup hook and the scorekeeper subagent), `.github/workflows/` (ci, pages, news), `.github/CODEOWNERS` (who a pull request asks for review; the generated folders are listed so a request that names one means a generator was skipped), `.devcontainer/` (Codespaces and any dev container; `scripts/setup.sh` is the macOS equivalent), `justfile` and `agents.just`. The camp gets its own, smaller set of the same things from the template.

## How a change travels

| You changed | Then | It reaches the learner through |
|---|---|---|
| `src/config/` (world scale, palette) or `src/` (the game) | `just build`, `just verify`, PR, release | the hosted game after Pages deploys; `vibe play --offline` caches a copy from `main` |
| `vibemap/` (the CLI, the checks, the vault) | `just verify`, PR, release, tag | `uv tool install --force git+https://github.com/tpetedb/vibe-map@vX.Y.Z` |
| `vibemap/tech.py` (the roadmap) | `just tree` (regenerates the notes, the tree JS, `docs/ROADMAP.md`), `just build` | both of the above |
| an artifact's `real` block in `vibemap/data/campaign.json` (the Do it for real walkthrough, the doc link, the check spec) | `just build` (the campaign is injected into the game), `just verify` | the hosted game for the walkthrough, `uv tool install` for the check |
| `vibemap/artifact_checks.py` (a check kind, one function per kind, named from the `real` block) | `just verify` (`tests/test_artifact_tasks.py`), PR, release, tag | `uv tool install`, as any CLI change |
| a mentor encounter: the `encounter` dialogue and exercise in `vibemap/data/campaign.json`, plus `mentor_quest` in `vibemap/quests.py` | `just build`, `just verify`; every dialogue line needs its source index | the hosted game for the dialogue and the plaque, `uv tool install` for `vibe check --mentor <id>` |
| `src/config/00-config.js` alone (world scale, island radius, palette) | `just build`; a learner's fork has its own copy, so nothing in `tools/build.py` may assume the product's path | the hosted game, and a fork after `just build` there |
| `src/`, `src/vendor/`, `tools/build.py` or `tools/generated/` | `uv run python tools/sync_fork_source.py`, then `just verify`; the mirror in `vibemap/data/fork_source/` is what an installed `vibe fork` copies into a camp, and a test fails when it drifts | `uv tool install`, then `vibe fork` in any camp |
| `.agents/skills/`, `.claude/settings.json`, `.claude/agents/scorekeeper.md` | `uv run python tools/sync_template.py`, then `just verify` | `vibe new` on the next install; existing camps copy what they want |
| `vibemap/data/template/` (README, AGENTS, justfile, config/camp.toml, pages.yml, CODEOWNERS, `_devcontainer/`) | edit in place, `just verify` (`tests/test_onboarding.py` runs `vibe new` into a temp folder) | `vibe new` on the next install |
| `workspace/` in this repository | nothing else; it is the worked example | never; each camp has its own |
| `vibemap/quests.py` extra checks | remember a camp has no `tests/` and no `just verify`: expert runs the learner's `workspace/**/test_*.py`, god adds the vault lint | `uv tool install`, as any CLI change |

## What a camp contains and what it does not

`vibe new` writes about thirty files and builds the vault. It does not write `src/`, `vibemap/`, `tools/`, `tests/` or `pyproject.toml`: a camp has no Python project of its own and no build. Its `justfile` calls the installed `vibe` directly. `vibe play` opens the hosted game (or the local build when run inside this repository, or a cached copy after `vibe play --offline`). Progress moves between the game and the camp as a code (`vibe export`, `vibe import`), never as files.

People who want the engine press **Use this template** on GitHub or clone this repository; then they have a product checkout that is also a valid camp (it has a `config/camp.toml` and a `workspace/`), which is how the tests and the played instance work.

## Branch protection

`main` is protected on GitHub, and the rules hold for admins too:

- Changes reach `main` only through a pull request whose two CI jobs (lint, unit tests, generated files in sync; Playwright in Chromium and WebKit) are green and whose branch is up to date with `main`.
- No force pushes, no deletion, review threads resolved before merge.
- Release tags `v*` are immutable (a tag ruleset refuses updates and deletion).
- Branches are deleted automatically after their pull request merges.
- Secret scanning with push protection and Dependabot security updates are on. The played instance `tpetedb/vibe-map-played` refuses force pushes and deletion of `main` but takes direct pushes, because its regeneration script writes to it.

An agent that hits one of these rules reports it; it never works around it.

## Catching up with main, and the files that conflict

Strict checks mean a branch has to be up to date with `main` at the moment its checks go green, so with several branches open every merge sends the others back for another round. Almost every conflict that round produces is in a file nobody wrote: a generated output, or `CHANGELOG.md`.

Both are removed at the source.

- **The changelog is written by a release, not by a branch.** A branch adds `changelog.d/<slug>.<type>.md` with its bullets; `uv run python tools/changelog.py release X.Y.Z` (`just release X.Y.Z`) writes the dated section into `CHANGELOG.md`, moves the compare links and deletes the fragments. `just changelog` prints the Unreleased view in between. The check in CI's lint job refuses a pull request that changes `src/`, `vibemap/` or `tools/` without a fragment, and one that edits `CHANGELOG.md` outside a release. Keep a Changelog 1.1.0 stays the published form. towncrier is the packaged version of this idea and was read first: it assembles at a `start_string` marker and knows nothing about the compare-link block a Keep a Changelog file ends with ([its configuration reference](https://towncrier.readthedocs.io/en/stable/configuration.html)), so it would have to be templated back into this format, which is more work than the hundred lines in `tools/changelog.py` and one more dependency.
- **A generated file is resolved by regenerating it.** Take either side, run the generators in dependency order, and the result is what both branches meant. `just sync-main` is that: merge `origin/main`, resolve the generated conflicts that way, refuse and name the file when a real source conflict is left (`git merge --abort` undoes it), then run the fast gates. One exception to watch: a vault note written by hand rather than by `vibe vault build` is not regenerated, so resolve `vault/` yourself before running it if your branch wrote one.

`.gitattributes` supports the policy with the two things that work in a fresh clone:

| Attribute | What it does | Source |
|---|---|---|
| `merge=binary` on the generated outputs | One of git's three built-in merge drivers: keep our version in the work tree and leave the path conflicted for the user to sort out. So a two megabyte built game never gets conflict markers written through it, and the conflict is still reported, which is what makes the regenerate step impossible to skip. | [gitattributes, the merge attribute](https://git-scm.com/docs/gitattributes) |
| `linguist-generated=true` on the same set | GitHub collapses the file in a diff by default and leaves it out of the repository's languages, so a review reads the source change. | [Customizing how changed files appear on GitHub](https://docs.github.com/en/repositories/working-with-files/managing-files/customizing-how-changed-files-appear-on-github) |

A **custom** merge driver would do more (it could run the generator itself), but git only knows a driver that `git config merge.<name>.driver` names, and that configuration lives in each clone, not in the repository. Nothing here relies on it, and nothing should: a rule that works only on the machine that set it up is worse than no rule.

## Merge queue: checked, not available here

A merge queue would fix the remaining cost, which is that every branch has to be rebuilt after every merge. It is not available for this repository. GitHub's own announcement of general availability says: "Merge queue is available on private and public repos on the GitHub Enterprise Cloud plan and all public repos owned by organizations" ([GitHub Changelog, 12 July 2023](https://github.blog/changelog/2023-07-12-pull-request-merge-queue-is-now-generally-available/), read 2026-09-18). `tpetedb/vibe-map` is public but owned by a personal account on Pro, not by an organization, so it qualifies under neither half.

The recommendation, for Tom or the orchestrator to decide, is therefore **not** to chase it:

1. Keep the fragments and `just sync-main`. They remove the conflicts, which is the expensive half of falling behind.
2. If the queue is ever wanted, the only route is moving the repository into an organization (free), after which the queue is enabled on the `main` ruleset and pull requests are added with **Merge when ready** instead of auto-merge. That changes the URL of the repository and of the Pages site, every camp's remote, and the `vibe new --github` path, so it is not a harness decision.
3. Until then, the cheap substitute is what the agents already do: arm auto-merge, run `just sync-main` when the branch falls behind, and land one thing at a time.

Nothing in this repository's settings was changed to write this down.

`.github/CODEOWNERS` names who a pull request asks for review. It works in a public repository on every plan and in a private one on GitHub Pro or above; the same is true of protected branches and of Pages. A camp made private with `vibe new --github you/camp --private` therefore needs Pro before workstream 7 can publish its game, which is the table in the camp's own `README.md`. Changing the visibility of an existing repository is the owner's call and never an agent's.

## Where the rules live

- `AGENTS.md` (this repository): the file map, ways of working, the test loop, code style. Every agent reads it through `CLAUDE.md`.
- `vibemap/data/template/AGENTS.md`: the same for a camp, shorter, with the zones table and the rule that `workspace/data/scores.csv` is a system of record.
- `docs/adr/`: decisions with their why.
- `CHANGELOG.md`: Keep a Changelog form, written only by a release from the fragments in `changelog.d/` (see "Catching up with main" below).

## The idea behind it

Separation of concerns is Dijkstra's phrase (EWD 447, 1974): study one aspect at a time, in isolation, without pretending the others do not exist. Parnas (1972) says where to cut: around the decisions most likely to change, hiding each behind an interface. Here the decisions are "how the game is built", "what a camp starts with" and "what the learner makes", and each has one folder. The roadmap teaches both ideas under "Separation of concerns" and "Building the builder" (the meta step: this template, these skills and this document exist to make the next build, by you or by an agent, cheaper), with the sources.
