---
title: "Mitchell Hashimoto"
date: 2026-09-16
tags: [people]
---
# Mitchell Hashimoto

*Creator of Ghostty; co-founder of HashiCorp*

Co-founded HashiCorp (Vagrant, Terraform), then spent his time building Ghostty: a terminal emulator that is fast, native on macOS, and configured with one plain text file. Writes carefully about how he uses AI agents in his own work.

**What they would tell you**
- A tool you use for eight hours a day deserves to be excellent.
- Configuration should be one readable file.
- Use agents for the parts you understand well enough to review.

**Going deeper**
Ghostty's docs are the reference for the terminal setup at Evening 4 Stop 2. His public writing on working with AI is unusually concrete about what he lets agents do and what he does not, which makes it a good counterweight to hype in either direction.

**Rolinda asks:** Why did the Terraform man build a terminal?

## The encounter
- Why build another terminal?
- Mitchell Hashimoto: Because you are in it all day. He started Ghostty and libghostty after HashiCorp, where he was on the first engineering team behind Terraform and Vault. ([mitchellh.com](https://mitchellh.com))
- Where do its settings live?
- Mitchell Hashimoto: In one file called config.ghostty in your config folder. Plain key = value lines, and a comment is a line that starts with a hash. ([Ghostty configuration reference](https://ghostty.org/docs/config))
- How much do I have to configure?
- Mitchell Hashimoto: Almost nothing. The defaults are meant to be sensible, and every key also works as a command-line flag. ([Ghostty configuration reference](https://ghostty.org/docs/config))

## Your exercise: One readable config file
About 10 minutes, in `workspace/mentors/hashimoto/`. Status: not yet.

1. Write workspace/mentors/hashimoto/config.ghostty with at least three key = value lines for a terminal you would actually want.
2. Above each one, a comment line starting with a hash that says why, not what.
3. Keys are lowercase; a value can be quoted or bare. Read the docs first.
4. Add notes.md with ## What I learned.

Checked by `vibe check --mentor hashimoto`: config.ghostty has three settings and a reason above each.

The plaque on the island reads: One readable config file.


## Sources
- [Ghostty](https://ghostty.org)
- [Ghostty configuration reference](https://ghostty.org/docs/config)
- [mitchellh.com](https://mitchellh.com)

Back to [[Your path]]

#people
