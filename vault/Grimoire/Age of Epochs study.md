---
title: Age of Epochs study
date: 2026-09-16
tags: [decision, concept]
---
# Age of Epochs study

What Project Grimoire learned from sokrypton/aoe, a browser Age of Empires built with Claude Code. Ideas only: that repo is GPL-2.0-or-later and this one is MIT, so no code or art crosses over.

## 2026-09-16
- Studied the architecture (simulation versus viewer, thin HTML shells sharing one engine), the 2:1 isometric map, the procedural canvas renderer, the Playwright test battery and two generations of multiplayer.
- Adopted into AGENTS.md: a file map, constraint-only comments, one helper per concept, a targeted-then-full test loop, test the entry point, versioned formats that fail loudly.
- Skipped: determinism rules, the tick timebase, statistical batches. There is no shared simulation here.
- Proposed, not built: a classic 2D view of the campus (recommended) and a three-walker multiplayer (not before the first evening).
- links: [[Tonight]], [[Evening 1]], [[Resources]]

## Sources
- https://github.com/sokrypton/aoe
- https://ageofepochs.com
- docs/AOE-STUDY.md in this repo

#decision #concept
