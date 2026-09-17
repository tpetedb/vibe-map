---
title: "YAML in practice: CI and Compose"
date: 2026-09-16
tags: [tech, formats]
generated: d57018d32b2d
---
# YAML in practice: CI and Compose

YAML is data shaped by indentation: a map is key: value, a list is lines starting with a dash, nesting is two spaces. Strings rarely need quotes, which is the trap: no, yes, on and 3:30 can turn into booleans or numbers unless you quote them. One file can hold several documents separated by ---, so a stray separator silently splits your config. CI (GitHub Actions) and Docker Compose chose it because a pipeline is a nested list of steps that people read and diff more often than machines do.

**History.** YAML began in 2001 and the 1.0 spec was published in 2004 by Clark Evans, Oren Ben-Kiki and Ingy dot Net; the 1.2.2 revision (October 2021) clarified the spec without changing it. GitHub Actions became generally available in November 2019 with YAML workflows.

**Try in five minutes.** Read .github/workflows/ci.yml and change the Python version in one place.

- Docs: [GitHub Actions workflow syntax](https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions), [Docker Compose file reference](https://docs.docker.com/reference/compose-file/), [Source: YAML 1.0 specification (2004)](https://yaml.org/spec/1.0/), [Source: YAML 1.2.2 specification (revision 2021-10-01)](https://yaml.org/spec/1.2.2/), [Source: GitHub changelog, Actions generally available (November 2019)](https://github.blog/changelog/2019-11-11-github-actions-is-generally-available/)
- Unlocks: [[CI-CD and automation]], [[Docker and containers]]
- Shelf: Config and formats · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #formats
