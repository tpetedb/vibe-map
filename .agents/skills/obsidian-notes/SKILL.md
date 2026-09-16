---
name: obsidian-notes
description: Write and link notes in the Obsidian vault at vault/. Use whenever asked to document, remember, summarise, or "write a note about" something.
---
# Obsidian notes

The vault is a folder of Markdown files. Obsidian conventions: https://help.obsidian.md/links

Rules:
- One note per topic, in `vault/Grimoire/<Topic>.md`. Title line `# <Topic>`.
- Link related notes with `[[Topic]]` wikilinks. Every new note links to at least two existing ones and is linked from `vault/Grimoire/Tonight.md`.
- Date new entries: `## YYYY-MM-DD` sections, newest first.
- Tags at the bottom: `#workstream`, `#concept`, `#people`, `#decision`.
- Keep a "Sources" section: real URLs only, one per line.

Template:

```
# <Topic>

<two-sentence summary>

## <YYYY-MM-DD>
- what was built or decided
- links: [[Related]], [[Related2]]

## Sources
- https://...

#concept
```

Check the result with `python3 grimoire/cli.py map`, which rebuilds `vault/Grimoire/Map.md`.
