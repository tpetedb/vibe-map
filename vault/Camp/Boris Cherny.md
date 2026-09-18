---
title: "Boris Cherny"
date: 2026-09-16
tags: [people]
generated: 0d1113f87342
---
# Boris Cherny

*Creator and head of Claude Code, Anthropic*

Built Claude Code as an internal experiment at Anthropic in 2024; it became the company's main coding tool and then a product. Previously a principal engineer at Meta and author of Programming TypeScript. Runs five Claude sessions in his terminal and five to ten on the web, each in its own checkout.

**What they would tell you**
- Start in plan mode, iterate on the plan, then let Claude one-shot the implementation.
- CLAUDE.md is a record of mistakes: when a pattern goes wrong, update the file so the next session avoids it.
- Give Claude a way to verify its own work; it roughly doubles or triples quality.
- Keep the setup vanilla. The tool works out of the box; complexity is debt.

**Going deeper**
His team keeps Sutton's Bitter Lesson framed on the wall and builds for the model six months from now, on the reasoning that scaffolding tuned to today's model becomes debt when the next one ships. His personal CLAUDE.md for the Claude Code repo is about 2,500 tokens and every team keeps its own in git. He tags coworkers' PRs to have learnings written back into it. Around 10 to 20 percent of his parallel sessions get abandoned; that is expected, not failure.

**Rolinda asks:** How many of your parallel sessions actually finish?

## The encounter
- My agent keeps making the same mistake.
- Boris Cherny: Then write the mistake down in CLAUDE.md the moment you see it. That is how his team uses the file: every time Claude does something wrong, a line goes in, several times a week. ([How Boris uses Claude Code (curated)](https://howborisusesclaudecode.com/))
- How do I get better work than my first try?
- Boris Cherny: Give it a way to check itself. He calls a feedback loop the most important thing for quality: a test suite for a backend, a browser for a frontend, a simulator for mobile. ([How Boris uses Claude Code (curated)](https://howborisusesclaudecode.com/))
- Do I need an elaborate setup first?
- Boris Cherny: No. His own configuration is surprisingly vanilla. The tool is meant to be useful on the day you install it. ([How Boris uses Claude Code (curated)](https://howborisusesclaudecode.com/))
- And you really run several at once?
- Boris Cherny: Five to ten sessions, each in its own checkout or worktree, so they never fight over the same files. ([How Boris uses Claude Code (curated)](https://howborisusesclaudecode.com/))

## Your exercise: One rule, and the command that proves it
About 10 minutes, in `workspace/mentors/cherny/`. Status: not yet.

1. Think of one thing your agent got wrong today.
2. Write workspace/mentors/cherny/CLAUDE.md with a heading ## Rules and one rule that would have prevented it.
3. Add a heading ## How it is verified with the command that would catch it (a test, a linter, a build).
4. Add notes.md with ## What I learned and a few sentences of your own.

Checked by `vibe check --mentor cherny`: CLAUDE.md holds a Rules section and a How it is verified section.

The plaque on the island reads: Write the mistake down.


## Sources
- [Building Claude Code with Boris Cherny (Pragmatic Engineer)](https://newsletter.pragmaticengineer.com/p/building-claude-code-with-boris-cherny)
- [Inside the workflow of Claude Code's creator (InfoQ)](https://infoq.com/news/2026/01/claude-code-creator-workflow/)
- [His thread on X](https://x.com/bcherny/status/2007179832300581177)
- [How Boris uses Claude Code (curated)](https://howborisusesclaudecode.com/)

Back to [[Your path]]

#people
