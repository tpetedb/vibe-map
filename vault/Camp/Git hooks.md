---
title: "Git hooks"
date: 2026-09-17
tags: [tech, git]
generated: b152775317db
---
# Git hooks

Scripts git runs at moments in its own lifecycle: pre-commit before a commit is written, commit-msg to check the message, pre-push before anything leaves the machine, post-checkout and post-merge after a switch. A non-zero exit aborts the step. They live in .git/hooks (not versioned), or in a folder you commit and point at with core.hooksPath; the pre-commit framework and lefthook manage them from a config file.

**History.** Hooks have been in git since the first releases (the githooks manual page lists thirty of them); core.hooksPath arrived in Git 2.9 (June 2016) so a team can version its hooks; pre-commit (Yelp, 2014) and lefthook (Evil Martians, 2019) turned them into a one-line install.

**Try in five minutes.** In this repo: `mkdir -p .githooks && printf '#!/bin/sh
uv run ruff check vibemap tests tools
' > .githooks/pre-commit && chmod +x .githooks/pre-commit && git config core.hooksPath .githooks`. Then commit something with a lint error and watch it refuse.

- Docs: [githooks manual](https://git-scm.com/docs/githooks), [Pro Git, Customizing Git: Git Hooks](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks), [pre-commit framework](https://pre-commit.com/), [lefthook](https://github.com/evilmartians/lefthook), [Source: githooks manual, default hooks directory and core.hooksPath](https://git-scm.com/docs/githooks), [Source: Git 2.9.0 release notes (core.hooksPath)](https://github.com/git/git/blob/master/Documentation/RelNotes/2.9.0.adoc)
- Unlocks: [[Agent hooks]], [[CI-CD and automation]]
- Shelf: Git and GitHub · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #git
