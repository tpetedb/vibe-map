---
title: "The symbols: slash, at, bang, hash"
date: 2026-09-17
tags: [tech, agents]
generated: 2a00cb49a008
---
# The symbols: slash, at, bang, hash

Every agent chat has a few characters that are not words. In Claude Code, a line that starts with `/` is a command or a skill (`/help`, `/init`, `/compact`, `/memory`), a line that starts with `!` runs a shell command and puts its output in the session, and `@` followed by a path mentions a file so the agent reads it (type a letter after it for completion). In CLAUDE.md, `@path` imports another file at launch; inside backticks it stays literal. `#` is a Markdown heading at the start of a line and a tag inside Obsidian (`#tech`); `[[Note]]` is an Obsidian link; `---` fences frontmatter; three backticks fence code; `<tag>` is structure for the model; `$` starts a shell variable and `~` is your home folder. Knowing which parser reads which symbol is half of not being surprised.

**History.** Slash commands come from IRC (1988), file mentions with `@` from Twitter-era chat, `!` for shell escapes from editors like vi and ed, `#` for headings from Markdown (2004) and for tags from Twitter (2007), double brackets from wikis (WikiWikiWeb, 1995) and Obsidian; Claude Code documents its own set on the interactive-mode page.

**Try in five minutes.** In Claude Code type `/help`, then `!uv run vibe status`, then `@config/camp.toml what does the pet table do`. Open `CLAUDE.md` and see the `@AGENTS.md` import at the top. Then open the vault in Obsidian and click a `#tech` tag.

- Docs: [Claude Code, interactive mode (quick commands)](https://code.claude.com/docs/en/interactive-mode), [Claude Code, memory and @path imports](https://code.claude.com/docs/en/memory), [Obsidian, internal links](https://help.obsidian.md/Linking+notes+and+files/Internal+links), [Source: Claude Code interactive mode reference, the quick commands table (/ command or skill, ! shell mode, @ file path mention)](https://code.claude.com/docs/en/interactive-mode), [Source: Claude Code memory page, import additional files with @path](https://code.claude.com/docs/en/memory)
- Unlocks: [[Skills (Agent Skills standard)]], [[Memory - the vault as long-term memory]], [[Bash and shell scripts]]
- Shelf: Agents and the harness · Depth: Basics

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #agents
