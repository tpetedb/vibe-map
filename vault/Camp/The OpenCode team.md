---
title: "The OpenCode team"
date: 2026-09-16
tags: [people]
---
# The OpenCode team

*Open-source terminal coding agent*

An open-source agent for the terminal that works with Claude, GPT, Gemini and local models, reads AGENTS.md and the Agent Skills standard. Useful as the second opinion that shows which parts of your setup are yours and which belong to the vendor.

**What they would tell you**
- Provider-agnostic by design: swap the model, keep the workflow.
- Open source means you can read how the agent decides.
- Local models are a first-class option.

**Going deeper**
Install it once, run it on the template repo, and compare notes with the Claude Code sessions. The interesting result is not which is better; it is how much of your AGENTS.md and skills carry over unchanged, which is the measure of how portable your setup really is.

**Rolinda asks:** So this one is free and it reads my rules too?

## The encounter
- Is there an open alternative?
- The OpenCode team: opencode is an open source coding agent that runs in your terminal, your editor or on the desktop. ([OpenCode](https://opencode.ai))
- Am I tied to one model?
- The OpenCode team: No. It reaches more than seventy-five providers through Models.dev, local models included. ([OpenCode](https://opencode.ai))
- Do I have to rewrite my rules for it?
- The OpenCode team: It reads AGENTS.md, walking up from the folder you are in, then a global file, and it can fall back to a CLAUDE.md. ([Rules and AGENTS.md](https://opencode.ai/docs/rules/))
- And the licence?
- The OpenCode team: MIT, in the open on GitHub, so you can read how the agent decides instead of guessing. ([OpenCode on GitHub](https://github.com/sst/opencode))

## Your exercise: The same prompt, two providers
About 12 minutes, in `workspace/mentors/opencode/`. Status: not yet.

1. Write workspace/mentors/opencode/providers.md with ## The same prompt and ## What I would keep.
2. Under the first, one prompt you use often, written out in full.
3. Under the second, what stays the same whichever model runs it: your rules file, your checks, your review step.
4. Add notes.md with ## What I learned.

Checked by `vibe check --mentor opencode`: providers.md holds one prompt and what survives a change of model.

The plaque on the island reads: Swap the model, keep the rules.


## Sources
- [OpenCode](https://opencode.ai)
- [OpenCode on GitHub](https://github.com/sst/opencode)
- [Rules and AGENTS.md](https://opencode.ai/docs/rules/)

Back to [[Your path]]

#people
