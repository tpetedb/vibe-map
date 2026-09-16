# ADR 0002: From sokrypton/aoe we take ideas and structure, never code

Status: Accepted, 2026-09-16

## Context

sokrypton/aoe (Age of Epochs, https://github.com/sokrypton/aoe) is a browser Age of Empires clone written with Claude Code: plain JavaScript, no bundler, a hard split between simulation and viewer, a Playwright test battery, and a written set of rules its author learned the hard way. It is the closest existing project to what this repo builds. It was studied on 2026-09-16 from a fresh clone at commit `b8f3346`; the study is `docs/AOE-STUDY.md`.

Its `LICENSE` is GNU GPL version 2 or later. This repository is MIT. Copying GPL code, sprites or CSS into an MIT project makes the combined work GPL, which would change what every learner who clones the template receives. Ideas, architecture and conventions are not covered by copyright; code and assets are.

## Decision

We will copy nothing from sokrypton/aoe: no JavaScript, no `sprites.png`, no CSS, no test harness code. What we adopt is an idea or a structure, written again from scratch here: the file map in `AGENTS.md`, the comment conventions, the test loop (the closest test while iterating, the full battery before a commit, test the entry point not the mechanism, look at the screenshot), the fixed script load order, and the cheapest-failure-first order of the battery.

We will record what was adopted and why in `docs/AOE-STUDY.md`, so a reader can check that the line was kept.

If the owner ever wants to lift actual code, the game becomes GPL-2.0-or-later. That is the owner's decision, recorded in a new ADR that supersedes this one. No agent makes it.

## Consequences

- The repository stays MIT, and the template stays free to relicense, rename and sell.
- Re-implementation costs time: the Python test harness in `tests/` and `tools/build.py` were written new instead of ported.
- Agents working here must be told the rule, and are: `AGENTS.md` and the study say "ideas only". A review of any file that resembles an aoe file is a licence check before it is a style check.
- The classic view and the multiplayer proposed in the study stay proposals until someone designs them from the ideas alone.
