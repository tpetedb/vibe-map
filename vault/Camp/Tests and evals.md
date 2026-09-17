---
title: "Tests and evals"
date: 2026-09-16
tags: [tech, code]
generated: 8cb0839caa27
---
# Tests and evals

A test runs code and checks the result. An eval does the same for an agent: a set of tasks with known good answers, run after every change to AGENTS.md or a skill. Without tests, an agent will happily make things worse faster.

**History.** JUnit was written by Kent Beck and Erich Gamma on a flight to OOPSLA in 1997, pytest's lineage starts in 2004, property-based testing arrived with QuickCheck (ICFP 2000). Model evals became an engineering discipline around 2023; today teams keep an eval set next to their instruction files.

**Try in five minutes.** Ask Claude: 'write pytest tests for workspace/python/scores.py and run them'. Then break scores.py and watch them fail.

- Docs: [pytest](https://docs.pytest.org), [Anthropic: evals guide](https://docs.claude.com/en/docs/test-and-evaluate/develop-tests), [Source: Martin Fowler, xUnit (Kent Beck's account of JUnit's origin)](https://martinfowler.com/bliki/Xunit.html), [Source: pytest history](https://docs.pytest.org/en/stable/history.html), [Source: QuickCheck (Claessen and Hughes, ICFP 2000)](https://www.cse.chalmers.se/~rjmh/QuickCheck/)
- Unlocks: [[CI-CD and automation]]
- Shelf: Languages and code · Depth: Deep

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #code
