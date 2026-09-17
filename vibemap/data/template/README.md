# Your Vibe Code Camp

## Start here

```bash
just start        # the terminal menu: who you are, what the machine has, where to go
```

You should see a screen with your name, your field and a difficulty, then a launcher list. From there: the game in the browser, the vault in Obsidian, your status in this terminal.

`just` does not come with a Mac: `brew install just` puts it there. You never need it, though. Every recipe in this camp is one line that calls the `vibe` command, so `just check 1` and `vibe check 1` do the same thing; `just` on its own lists them all.

## What you get

This folder is a camp: the place where you play the course and build your own thing. It was made by `vibe new`. The course engine (the game, the checks, the `vibe` command itself) is not here; it reaches you through the hosted game and the installed command, so nothing in this folder is code you did not write.

| Where your things are | Folder | What it is |
|---|---|---|
| Your work | `workspace/` | Everything you build during the course: the game from workstream 1, the scores CSV and its queries, the chart, the tool. Empty on day one apart from a README. The lessons run here and the checks look here. |
| Your notes | `vault/` | The course notes. `vibe` writes them, you and your agent add your own. Open it in Obsidian. |
| Settings | `config/camp.toml`, `justfile`, `AGENTS.md`, `CLAUDE.md`, `.agents/`, `.claude/`, `.github/` | How the camp and your agent behave. You will be taught to change these; until then, leave them alone. |

The state of your progress lives in `.vibe/state.json` (ignored by git) and travels to the game as a progress code (`vibe export`, `vibe import`).

## Every session

```bash
just start        # the terminal menu: checks, the pet, the launchers
just camp         # the game in the browser, the vault in Obsidian, your status here
just check 1      # verify the definition of done for a workstream, earn the XP
just vault        # rebuild the notes and lint for dead links
```

From workstream 3 on, when `workspace/data/scores.csv` exists, `just scores` summarises it and `just scores top_runs` runs a query from `workspace/sql`.

The full loop between the terminal, the game and Obsidian: https://github.com/tpetedb/vibe-map/blob/main/docs/LONG-GAME.md

## The notes belong in git

`vibe` regenerates the notes under `vault/Camp/`, so a check or a vault build leaves the tree dirty. That is the point: the notes are the record of what you did. Commit them. `git add -A && git commit -m "what I learned"` is the right move after a session, and it will include the regenerated notes.

## Separation of concerns, on purpose

The layout is the first lesson. Code you did not write stays out of your way; settings are visible but separate; your own work has one home. The roadmap topic "Separation of concerns" (Dijkstra, Parnas, Ousterhout) explains why this matters beyond this folder, and "Building the builder" explains why the settings zone is worth your time.
