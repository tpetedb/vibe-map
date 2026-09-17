---
title: "Prompting: task, goal, hard constraints"
date: 2026-09-17
tags: [tech, agents]
---
# Prompting: task, goal, hard constraints

A prompt an agent can act on has five parts: the task (what to do), the goal (why, so it can make the small decisions), the hard constraints (what must never change: files, APIs, style rules, budgets), the context it cannot infer (which repo, which conventions, what already exists) and the definition of done (what output, checked how). Anthropic's own rule: show the prompt to a colleague with no context; if they would be confused, the model will be too. Say what to do rather than what not to do, put the steps in order when order matters, and explain the why behind a constraint so the model generalises instead of guessing.

**History.** Prompt engineering became a discipline with the instruction-tuned models of 2022; Anthropic's prompting guide (2024, kept current for every model since) codified the same advice for Claude: be clear and direct, add context and motivation, give three to five examples, structure with tags, give a role; OpenAI's guide says the same in other words. The best practices page for the current models keeps the golden rule and adds guidance for agentic work: autonomy versus safety, long-horizon state, not over-thinking.

**Try in five minutes.** Rewrite one prompt you sent today in five labelled lines: Task, Goal, Hard constraints, Context, Done when. Send both versions to `claude -p` and compare. Then put the five lines in a skill so you never type them again.

- Docs: [Anthropic, prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices), [Anthropic, be clear and direct](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/be-clear-and-direct), [OpenAI, prompt engineering guide](https://platform.openai.com/docs/guides/prompt-engineering), [Source: Anthropic, prompting best practices (the golden rule, sequential steps, examples, context)](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- Unlocks: [[Structure - XML tags and Markdown blocks]], [[The symbols - slash, at, bang, hash]], [[Context window and prompts]], [[Skills (Agent Skills standard)]]
- Shelf: Agents and the harness · Depth: Basics

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #agents
