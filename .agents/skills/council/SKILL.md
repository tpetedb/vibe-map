---
name: council
description: Convene the twelve mentors of Vibe Code Camp on one question, llm-council style (each answers in character from their recorded ideas, they review each other anonymised, a chairman writes minutes to the vault). Use when the user asks "what would the mentors say", "ask the council", "get several opinions on", or wants a decision note with a verdict and next steps.
allowed-tools: Bash(uv run vibe *) Read
---
# Council of mentors

The pattern is Andrej Karpathy's llm-council (https://github.com/karpathy/llm-council):
several answers, anonymised peer review, one chairman synthesis. Here the
"models" are the mentors in `src/data/campaign.json`, each grounded in their
recorded ideas and sources, so nobody invents a quote.

## Fast path (one command)

```bash
uv run vibe council "Should a beginner learn git before Python?"
uv run vibe council "How do I keep an agent from deleting my data?" --mentors cherny,hashimoto,torvalds
```

It writes `vault/Camp/Council - <topic>.md` with Verdict, Where they agree,
Where they disagree, What to do tonight, Ranking, and every answer. It uses the
provider in `vibe.toml` (claude, codex, gemini, copilot or opencode).
Add `--dry-run` to see the prompts without calling anything.

## Agent path (subagents, no extra CLI calls)

When you are the agent and the user wants it live in the session:

1. Read the mentors from `src/data/campaign.json`; pick at most four whose
   `ideas` touch the question.
2. Spawn one subagent per mentor with this brief: "You are NAME, ROLE. Answer
   only with positions attributable to these recorded ideas and sources: IDEAS,
   SOURCES. If they do not cover the question, say so in character. At most
   180 words, plain language, no lists." Collect the answers.
3. Spawn one reviewer per mentor with the other answers labelled A, B, C
   (anonymised): rank them for a beginner with one sentence each.
4. Write the minutes yourself with exactly these headings: Verdict, Where they
   agree, Where they disagree, What to do tonight, Ranking. Save it to
   `vault/Camp/Council - <topic>.md` with frontmatter, tags
   `#council #decision`, links to each mentor note and to [[Tonight]], and add
   a line to Tonight's Build log. No em dashes, no emoji.

## Rules

- Never attribute a claim a mentor has not made in their recorded ideas or
  sources; "I have not written about this" is a valid answer.
- Keep the anonymisation in the review stage; reveal names only in the minutes.
- The minutes are advice for one evening, not a verdict on the field.
