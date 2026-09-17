---
title: "Agent hooks"
date: 2026-09-17
tags: [tech, imperial]
---
# Agent hooks

The same idea inside a coding agent: shell commands (or HTTP endpoints, MCP tools, prompts) that Claude Code runs at points in its lifecycle. PreToolUse can block a tool call, PostToolUse can react to an edit (this repo backs up data/ after every edit), UserPromptSubmit can add context, Stop can keep the agent working, SessionStart can load state. Configured under hooks in settings.json, filtered by a matcher, fed JSON on stdin; exit 2 blocks, JSON on stdout decides.

**History.** Claude Code documents thirty-two hook events, from SessionStart and PreToolUse to PreCompact and WorktreeCreate, in five configuration scopes (user, project, local, managed policy, plugins); the vibe-map repo uses one PostToolUse hook and Tom's toolbox ships guard hooks as a template.

**Try in five minutes.** Open .claude/settings.json in this repo, read the PostToolUse hook, then add a PreToolUse hook with matcher Bash whose command is `jq -e '.tool_input.command | test("rm -rf") | not' >/dev/null || exit 2`. Ask Claude to delete a folder with rm -rf and watch the refusal.

- Docs: [Claude Code hooks reference](https://code.claude.com/docs/en/hooks), [Claude Code hooks guide](https://code.claude.com/docs/en/hooks-guide), [This repo's hook](https://github.com/tpetedb/vibe-map/blob/main/.claude/settings.json), [Source: Claude Code hooks reference (events, scopes, exit codes)](https://code.claude.com/docs/en/hooks)
- Unlocks: [[Security and permissions]], [[Headless agents and scheduling]]
- Age: Imperial Age · Level: Senior

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #imperial
