---
title: "Cat Wu"
date: 2026-09-16
tags: [people]
generated: cd292a154249
---
# Cat Wu

*Founding engineer and product lead, Claude Code*

Co-built Claude Code from the first internal prototype and shaped it into a product used far beyond engineering. Talks about the workflows Anthropic's own engineers discovered: slash commands for feature development and first-pass code review, subagents for narrow jobs.

**What they would tell you**
- Let Claude be the product manager first: ask what you want, write the spec, then the plan, then the to-do list.
- Automate the first pass of code review; keep a human on the merge.
- Non-technical users find uses the team never imagined; design for that.

**Going deeper**
Anthropic runs a /code-review command on every pull request internally, and a /feature-dev command that forces the spec-plan-todo sequence. The lesson for a non-engineer is that the sequence matters more than the code: the agent is much better at executing a plan it helped write than at guessing what you meant.

**Rolinda asks:** What do the non-engineers at Anthropic use it for?

## The encounter
- Who reviews what the agent wrote?
- Cat Wu: A slash command does the first pass on every pull request inside Anthropic. A person still approves the merge. ([How to use Claude Code like the people who built it (Every, with Cat Wu and Boris Cherny)](https://every.to/podcast/how-to-use-claude-code-like-the-people-who-built-it))
- Where do I start when I do not know the code?
- Cat Wu: With the sequence the team's feature command forces: ask what is actually wanted, build the specification, then a detailed plan, then a to-do list. ([How to use Claude Code like the people who built it (Every, with Cat Wu and Boris Cherny)](https://every.to/podcast/how-to-use-claude-code-like-the-people-who-built-it))
- I am not an engineer.
- Cat Wu: That is the design goal. They work to lower the barrier for people who are not: it should be intuitive enough that you drop in and it works, with point-and-click surfaces next to the terminal. ([How to use Claude Code like the people who built it (Every, with Cat Wu and Boris Cherny)](https://every.to/podcast/how-to-use-claude-code-like-the-people-who-built-it))

## Your exercise: Spec, plan, to-do, in that order
About 12 minutes, in `workspace/mentors/wu/`. Status: not yet.

1. Pick one small thing you want built this week.
2. Write workspace/mentors/wu/spec.md with three headings: ## Spec, ## Plan, ## To-do.
3. Under Spec say what done looks like; under Plan the steps; under To-do the list you would hand an agent.
4. Add notes.md with ## What I learned.

Checked by `vibe check --mentor wu`: spec.md has a Spec, a Plan and a To-do section.

The plaque on the island reads: Spec, plan, to-do.


## Sources
- [How to use Claude Code like the people who built it (Every, with Cat Wu and Boris Cherny)](https://every.to/podcast/how-to-use-claude-code-like-the-people-who-built-it)

Back to [[Your path]]

#people
