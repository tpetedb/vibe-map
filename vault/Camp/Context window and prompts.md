---
title: "Context window and prompts"
date: 2026-09-16
tags: [tech, imperial]
---
# Context window and prompts

The context window is the model's working memory for one conversation: everything it can see right now, in tokens. Files, instructions, tool output all compete for it. Specificity, scope and 'what not to touch' win because the model cannot read your mind and cannot remember last week without a file.

**History.** GPT-3 had a 2,048-token window (2020); Claude went to 100k in May 2023; Gemini 1.5 ran a million tokens in February 2024 and Claude Sonnet 4 in August 2025. Bigger windows did not remove the need for good instructions; they moved it to what you load.

**Try in five minutes.** Give the same task twice: 'make it cooler' and 'add a purple badge, keep stats, touch nothing else'. Compare the diff.

- Docs: [Claude prompt engineering](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview), [Claude Code best practices](https://code.claude.com/docs/en/best-practices), [Source: GPT-3 paper, section 2 (context window of 2048 tokens)](https://arxiv.org/abs/2005.14165), [Source: Anthropic, Introducing 100K context windows (May 2023)](https://www.anthropic.com/news/100k-context-windows), [Source: Google, Gemini 1.5 (February 2024)](https://blog.google/technology/ai/google-gemini-next-generation-model-february-2024/), [Source: Claude Sonnet 4 1M token context (August 2025)](https://claude.com/blog/1m-context)
- Unlocks: [[AGENTS.md]], [[Skills (Agent Skills standard)]]
- Age: Imperial Age · Level: Senior

<!-- generated from tools/tech.py; edit there -->

Back to [[Tech tree]]

#tech #imperial
