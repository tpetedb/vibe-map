---
title: "CI/CD and automation"
date: 2026-09-16
tags: [tech, git]
---
# CI/CD and automation

Continuous integration: every push runs the tests and checks in a clean machine. Continuous delivery: passing pushes deploy. GitHub Actions is a YAML file in .github/workflows/. This is where headless agents also live: a PR review bot is claude -p in a workflow.

**History.** CruiseControl (ThoughtWorks) was registered in March 2001, Hudson was renamed Jenkins in January 2011, Travis CI started in 2011, GitHub Actions became generally available in November 2019. CI made 'it works' a machine's opinion instead of a person's.

**Try in five minutes.** Ask Claude: 'add a GitHub Actions workflow that runs python3 workspace/python/scores.py and the three DuckDB queries on every push'. Push. Watch the tab.

- Docs: [GitHub Actions quickstart](https://docs.github.com/en/actions/quickstart), [Claude Code GitHub Actions](https://code.claude.com/docs/en/github-actions), [Source: SourceForge, CruiseControl project (registered 2001-03-23)](https://sourceforge.net/projects/cruisecontrol/), [Source: Jenkins blog, Jenkins! (January 2011)](https://www.jenkins.io/blog/2011/01/29/jenkins/), [Source: travis-ci/travis-ci repository (February 2011)](https://github.com/travis-ci/travis-ci), [Source: GitHub changelog, Actions generally available (November 2019)](https://github.blog/changelog/2019-11-11-github-actions-is-generally-available/)
- Unlocks: [[Headless agents and scheduling]], [[Tests and evals]]
- Shelf: Git and GitHub · Depth: Deep

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #git
