---
name: camp-progress
description: Tracks the eight Vibe Code Camp workstreams, awards XP and records what was built, through the vibe CLI. Use when the user finished a workstream ("mark 3 done", "I built the chart"), asks "where am I", "what is next", "check my progress", wants the progress map or Map.md, or wants to export or import the progress code that syncs with the game.
allowed-tools: Bash(uv run vibe *) Bash(just *)
---
# Vibe Code Camp progress

The CLI is the source of truth: `uv run vibe <command>` (`uv run vibe --help` lists them; `just status`, `just check` and `just vault` wrap the common ones).

- `status`: where the user is in the campaign, with XP and quests
- `check [n]`: verify the definition of done for workstream n (1 to 8) and award the XP; all workstreams when n is omitted
- `done <n> "what I built"`: mark workstream n done and write its vault note
- `map`: rebuild `vault/Camp/Map.md` (Mermaid) from the state
- `vault build` and `vault lint`: rebuild the vault notes and the map, then report orphans and dead links
- `export`: print the code to paste into the game (Roadmap, Import progress)
- `import <code>`: take a code exported from the game (Roadmap, Export progress)
- `explain <n>`: the workstream in plain words; `persona`: the mentor voice; `start`: the onboarding terminal
- `scores`: the summary of `workspace/data/scores.csv`

When the user finishes a workstream: run `check <n>`. If it reports the definition of done unmet, say what is missing instead of forcing it; use `done <n> "..."` only when the user explicitly says to mark it done. Then use the obsidian-notes skill to enrich the note with what was actually built (file names, decisions, one thing learned), then `vault build` and `vault lint`. End with one line: what changed, and the next workstream.

Do not hand-edit `Map.md` or the state file; the CLI regenerates them.
