---
title: "Subagents and multi-agent"
date: 2026-09-16
tags: [tech, imperial]
---
# Subagents and multi-agent

A subagent is a second model instance with its own instructions and context, called by the first for a bounded job (scorekeeper). Teams of agents split large work; the risk is coordination cost and compounding errors, so keep each one's job small and testable.

**History.** AutoGPT (March 2023) showed loops of agents; they mostly wandered. 2025 harnesses added typed subagents with their own tools and permissions, which is what made delegation reliable.

**Try in five minutes.** The 23:00 workstream: create the scorekeeper, run it, read its note.

- Docs: [Subagents](https://code.claude.com/docs/en/sub-agents), [Source: Significant-Gravitas/AutoGPT repository (created March 2023)](https://github.com/Significant-Gravitas/AutoGPT)
- Unlocks: [[Headless agents and scheduling]]
- Age: Imperial Age · Level: Senior

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #imperial
