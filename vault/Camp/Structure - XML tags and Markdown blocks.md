---
title: "Structure: XML tags and Markdown blocks"
date: 2026-09-17
tags: [tech, agents]
generated: 18f4f1731a31
---
# Structure: XML tags and Markdown blocks

Structure tells the model which words are instructions, which are data and which are examples. XML tags do that unambiguously: wrap each kind of content in its own tag (`<instructions>`, `<context>`, `<input>`, `<example>`), keep the names consistent, nest when the content nests (`<documents>` holding `<document index="1">`), and ask for output in a tag when you need to find it. Markdown does the human side: headings for sections, bullets for parallel items, numbered lists for order, fenced code blocks (three backticks with a language) for anything that must be copied exactly, tables for config. A good agent prompt mixes them: Markdown to read, XML to parse.

**History.** XML tags for prompts are Anthropic's recommendation since the first Claude prompting guide; the current best-practices page keeps them for mixing instructions, context, examples and variable input, and for formatting output. Markdown (2004) became the writing format of READMEs, AGENTS.md and Obsidian, so both the agent and the human read it; fenced code blocks come from GitHub Flavored Markdown (2009) and every agent honours the language tag.

**Try in five minutes.** Take the five-line prompt from the previous topic and wrap it: `<task>`, `<goal>`, `<constraints>`, `<context>`, `<done>`. Put the file you want changed inside `<input>` and the shape of the answer inside `<output>`. Ask for the answer as a Markdown table with a fenced diff. Notice how much less the model has to guess.

- Docs: [Anthropic, structure prompts with XML tags](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#structure-prompts-with-xml-tags), [Anthropic, control the format of responses](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#control-the-format-of-responses), [GitHub Flavored Markdown spec, fenced code blocks](https://github.github.com/gfm/#fenced-code-blocks), [Source: Anthropic, prompting best practices, XML tags and output format sections](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- Unlocks: [[Markdown and Obsidian]], [[AGENTS.md]]
- Shelf: Agents and the harness · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #agents
