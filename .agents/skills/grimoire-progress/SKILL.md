---
name: grimoire-progress
description: Track the eight Grimoire workstreams and record what was built. Use when the user says they finished a workstream, asks "where am I", wants the map, or wants to sync progress with the game.
---
# Grimoire progress

The CLI is the source of truth: `python3 grimoire/cli.py`.

- `status`: which workstreams are done
- `done <n> "what I built"`: mark workstream n (1-8) done and write its vault note
- `map`: rebuild `vault/Grimoire/Map.md` (Mermaid) from the state
- `export`: print the code to paste into the game
- `import <code>`: take a code from the game

When the user finishes a workstream: run `done`, then use the obsidian-notes skill to enrich the note with what was actually built (file names, decisions, one thing learned), then `map`.
