---
title: "Cookbook"
date: 2026-09-16
tags: [recipe]
---
# Cookbook

Recipes for a Chief of Staff. Each one is a prompt you paste into your provider, a definition of done, and the workstream it belongs to. Every persona has its own set; switch with `grimoire persona <id>`.

## The week in one page
Workstream 2. Turn a folder of meeting notes into a one-page brief.

```text
Read every .md file in notes/, list the decisions made, the open decisions with an owner, and the three risks. Write brief.md. Do not invent anything that is not in the notes.
```

**Done when:** brief.md exists and every line traces to a note.

## Meeting cost dashboard
Workstream 3. A chart of minutes per decision by meeting.

```text
Using data/meetings.csv, write sql/cost_per_decision.sql in DuckDB and a Python script that draws a bar chart to python/out/. Explain the one SQL construct I have not seen.
```

**Done when:** The chart opens and the worst meeting is obvious.

## Monday morning agent
Workstream 8. An agent that drafts the weekly agenda every Monday at 07:30.

```text
Write a script that runs the provider in print mode with the prompt in prompts/agenda.md and writes agenda-<date>.md. Then show me the crontab line for Monday 07:30.
```

**Done when:** A file appears on Monday without you touching the keyboard.

Back to [[Your field]] · [[Tonight]]

#recipe
