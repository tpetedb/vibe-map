---
title: "LLM versus harness"
date: 2026-09-16
tags: [tech, imperial]
---
# LLM versus harness

The LLM is the model: text in, text out, no memory, no hands. The harness is everything around it: the loop that calls it repeatedly, the tools it can run (bash, edit file), the files it reads first (AGENTS.md), permissions, hooks, memory. Claude Code, Codex CLI, Cursor are harnesses. Most of the difference in results comes from the harness and what you put in it, not from the model.

**History.** Transformer 2017 (Google, 'Attention is all you need'). GPT-3 2020. ChatGPT November 2022. Claude March 2023. MCP November 2024. Agentic coding harnesses: Cursor's agent mode November 2024, Claude Code February 2025, Codex CLI April 2025. AGENTS.md August 2025.

**Try in five minutes.** Run claude in the template folder and ask 'what files did you read before answering?'. That list is the harness.

- Docs: [Anthropic: building effective agents](https://www.anthropic.com/research/building-effective-agents), [How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works), [Source: Attention Is All You Need (arXiv, June 2017)](https://arxiv.org/abs/1706.03762), [Source: Language Models are Few-Shot Learners (arXiv, May 2020)](https://arxiv.org/abs/2005.14165), [Source: OpenAI, Introducing ChatGPT (November 2022)](https://openai.com/index/chatgpt/), [Source: Anthropic, Introducing Claude (March 2023)](https://www.anthropic.com/news/introducing-claude), [Source: Anthropic, Introducing the Model Context Protocol (November 2024)](https://www.anthropic.com/news/model-context-protocol), [Source: Cursor changelog 0.43 (November 2024)](https://cursor.com/changelog/0-43-x), [Source: Anthropic, Claude 3.7 Sonnet and Claude Code (February 2025)](https://www.anthropic.com/news/claude-3-7-sonnet), [Source: openai/codex repository (April 2025)](https://github.com/openai/codex), [Source: openai/agents.md repository (August 2025)](https://github.com/openai/agents.md)
- Unlocks: [[Context window and prompts]], [[Your harness - AGENTS.md, CLAUDE.md, dotfiles for agents]]
- Age: Imperial Age · Level: Senior

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #imperial
