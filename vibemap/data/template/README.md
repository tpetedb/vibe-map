# Your Vibe Code Camp

## Start here

```bash
just start        # the terminal menu: who you are, what the machine has, where to go
```

You should see a screen with your name, your field and a difficulty, then a launcher list. From there: the game in the browser, the vault in Obsidian, your status in this terminal.

`just` does not come with a Mac: `brew install just` puts it there. Most recipes are one line that calls the `vibe` command, so `just check 1` and `vibe check 1` do the same thing, and you never need `just` for those. Five do more: `setup` also links the skills into `.claude/`, `camp` opens Obsidian next to the game, `scores` picks a query file, and `break` and `rescue` are git recipes with no `vibe` equivalent. `just` on its own lists them all.

## What you get

This folder is a camp: the place where you play the course and build your own thing. It was made by `vibe new`. The course engine (the game, the checks, the `vibe` command itself) is not here; it reaches you through the hosted game and the installed command, so nothing in this folder is code you did not write.

| Where your things are | Folder | What it is |
|---|---|---|
| Your work | `workspace/` | Everything you build during the course: the game from workstream 1, the scores CSV and its queries, the chart, the tool, the mentor exercises in `mentors/`, the artifact tasks in `artifacts/` and your fork of the game in `forks/`. Empty on day one apart from a README. The lessons run here and the checks look here. |
| Your notes | `vault/` | The course notes. `vibe` writes them, you and your agent add your own. Open it in Obsidian. |
| Settings | `config/camp.toml`, `justfile`, `AGENTS.md`, `CLAUDE.md`, `.agents/`, `.claude/`, `.github/`, `.devcontainer/` | How the camp, your agent and the cloud container behave. You will be taught to change these; until then, leave them alone. |

The state of your progress lives in `.vibe/state.json` (ignored by git) and travels to the game as a progress code (`vibe export`, `vibe import`).

## Every session

```bash
just start        # the terminal menu: checks, the pet, the launchers
just camp         # the game in the browser, the vault in Obsidian, your status here
just check 1      # verify the definition of done for a workstream, earn the XP
just vault        # rebuild the notes and lint for dead links
vibe chat serve --pair <code>   # the game's Ask panel, answered by your own agent
```

The **Ask** button (or the **C** key) in the game answers questions about the stop
you are on. It needs the bridge above: one command, loopback only, paired with the
code the panel shows, and your subscription never leaves your machine. Without it
the panel searches the notes embedded in the game.

From workstream 3 on, when `workspace/data/scores.csv` exists, `just scores` summarises it and `just scores top_runs` runs a query from `workspace/sql`.

## What the island asks you to build

Two things on the islands leave work on your machine, next to the stops.

- A mentor sets you one exercise of under fifteen minutes. It lives in `workspace/mentors/<id>/`: whatever the exercise asks for, plus a `notes.md` with a `## What I learned` section in your own words. `vibe check --mentor <id>` (or `--mentor all`) verifies it, and their plaque goes up on the island.
- An artifact's sheet has a **Do it for real** task, written from the official documentation of the thing it stands for. You build it in `workspace/artifacts/<id>/`. `vibe check --artifact <id>` (or `--artifact all`) looks at what you built and runs it; if it needs a tool you do not have, it tells you which one instead of failing.
- On the production island you take the game apart. `vibe fork` copies it into `workspace/forks/vibe-map/`, where `just build` makes your own copy and `vibe check --fork` runs the four challenges. That folder is yours to break.

```bash
vibe check --mentor all
vibe check --artifact all
vibe check --fork
```

The full loop between the terminal, the game and Obsidian: https://github.com/tpetedb/vibe-map/blob/main/docs/LONG-GAME.md

## The notes belong in git

`vibe` regenerates the notes under `vault/Camp/`, so a check or a vault build leaves the tree dirty. That is the point: the notes are the record of what you did. Commit them. `git add -A && git commit -m "what I learned"` is the right move after a session, and it will include the regenerated notes.

## Playing without installing anything: Codespaces

`.devcontainer/` is a recipe for a Linux container with uv, just, duckdb, the
GitHub CLI and the `vibe` command already in it. Push this camp to GitHub, then
**Code**, **Codespaces**, **Create codespace on main**, and you have the whole
camp in a browser tab. Two ports are labelled for you: 8000 for your game
(`python3 -m http.server 8000 --directory workspace/game`) and 7717 for
`vibe chat serve`. A forwarded port is private to you until you say otherwise.

It is your repository, so the codespace is yours: the compute is charged to the
account that owns it, out of the free hours every personal account gets. Set a
spending limit of zero if you want those hours to be a hard stop. Prebuilds make
a codespace start faster and cost Actions minutes and storage, so none is set up
here; switch one on only if you decide you want to pay for it.

## Public camp or private camp

`vibe new --github you/camp` makes the repository public. `--private` makes it
private, and three things then depend on the plan of the account that owns it:

| What | Public repository | Private repository |
|---|---|---|
| GitHub Pages (`.github/workflows/pages.yml`, workstream 7) | every plan | GitHub Pro or above; on GitHub Free the repository has to be public |
| Protected branches, required reviewers | every plan | GitHub Pro or above |
| `.github/CODEOWNERS` (who is asked to review what) | every plan | GitHub Pro or above |

Nothing else changes. On GitHub Free, a private camp still gets git, issues,
Actions and Codespaces; you just cannot publish the game from it, so keep the
camp public or upgrade before workstream 7.

## Separation of concerns, on purpose

The layout is the first lesson. Code you did not write stays out of your way; settings are visible but separate; your own work has one home. The roadmap topic "Separation of concerns" (Dijkstra, Parnas, Ousterhout) explains why this matters beyond this folder, and "Building the builder" explains why the settings zone is worth your time.
