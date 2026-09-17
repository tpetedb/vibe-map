---
title: "Headless agents and scheduling"
date: 2026-09-16
tags: [tech, ship]
---
# Headless agents and scheduling

claude -p runs the agent as a command: prompt in, result out, no chat. Put it in launchd, cron, a GitHub Action or a webhook and you have automation that reasons. This is where the leverage is for a business: one boring job, done on a timer, forever.

**History.** Cron is older than almost everything in this tree: its manual page is in Sixth Edition Unix, dated October 1974. The new part is that the scheduled job can now read a mailbox, decide, and write a note. Programmatic agents (2025) are the successor of the scheduled script.

**Try in five minutes.** The 23:00 workstream: schedule the scorekeeper for 08:00.

- Docs: [Run Claude Code programmatically](https://code.claude.com/docs/en/headless), [launchd tutorial](https://www.launchd.info), [Source: TUHS, V6 cron(8) manual page](https://www.tuhs.org/cgi-bin/utree.pl?file=V6/usr/man/man8/cron.8)
- Unlocks: [[Tests and evals]], [[Cost, tokens and model choice]]
- Shelf: Ship and run · Depth: Deep

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #ship
