# Your Vibe Code Camp

This folder is a camp: the place where you play the course and build your own thing. It was made by `vibe new`, from the template inside the `vibe` command. It does not contain the game's engine, the terminal companion's code or the course's tests; those live in the product repository, https://github.com/tpetedb/vibe-map, and reach you through the hosted game and the installed `vibe` command.

## Three zones

| Zone | Folder | Who edits it |
|---|---|---|
| **Your workspace** | `workspace/` | You and your agent. Everything you build during the course lands here: the game from workstream 1, the scores CSV and its queries, the chart, the tool. Empty on day one apart from a README. |
| **Your notes** | `vault/` | The terminal companion writes the course notes; you and your agent add your own. Open it in Obsidian. |
| **Configuration** | `vibe.toml`, `justfile`, `AGENTS.md`, `CLAUDE.md`, `.agents/`, `.claude/`, `.github/` | The settings of the camp and the rules and skills your agent works with here. You change them on purpose, and the course teaches you how. |

The state of your progress lives in `.vibe/state.json` (ignored by git) and travels to the game as a progress code (`vibe export`, `vibe import`).

## Every session

```bash
just start        # the terminal menu: checks, the pet, the launchers
just camp         # the game in the browser, the vault in Obsidian, your status here
just check 1      # verify the definition of done for a workstream, earn the XP
just vault        # rebuild the notes and lint for dead links
```

The commands the lessons give you run inside `workspace/`; the checks look there. The full loop between the terminal, the game and Obsidian: https://github.com/tpetedb/vibe-map/blob/main/docs/LONG-GAME.md

## Separation of concerns, on purpose

The layout is the first lesson. Product code you did not write stays out of your way; configuration is visible but separate; your own work has one home. The roadmap topic "Separation of concerns" (Dijkstra, Parnas, Ousterhout) explains why this matters beyond this folder, and "Building the builder" explains why the configuration zone is worth your time.
