---
title: "Security and permissions"
date: 2026-09-16
tags: [tech, imperial]
---
# Security and permissions

Agents run commands. Give them the least they need: a folder, a permission list, hooks that veto dangerous commands, secrets in the environment, and a git history to undo. Prompt injection (instructions hidden in data the agent reads) is the new phishing.

**History.** Least privilege dates to Saltzer and Schroeder, 1975: 'every program and every user of the system should operate using the least set of privileges necessary to complete the job'. It applies unchanged to agents; the harness enforces it with permissions and hooks.

**Try in five minutes.** Open .claude/settings.json; add a PreToolUse hook that blocks 'rm -rf'. Test it.

- Docs: [Claude Code permissions](https://code.claude.com/docs/en/permissions), [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/), [Source: Saltzer and Schroeder, The Protection of Information in Computer Systems (1975)](https://web.mit.edu/Saltzer/www/publications/protection/)
- Unlocks: [[Cost, tokens and model choice]]
- Age: Imperial Age · Level: Senior

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #imperial
