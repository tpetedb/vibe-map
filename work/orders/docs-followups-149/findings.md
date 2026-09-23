# Source

Issue 149: the docs sign-off items, and issue 95's "current contracts" block, which has outgrown a comment. Read with `just work-thread docs-followups-149`.

# What

- docs/SKILLS.md and docs/CONFIG.md name only recipes and skills that exist; a test holds them to it.
- docs/CONFIG.md and ADR 0001 describe how the build finds modules today (by folder and name, boot last), not GAME_ORDER.
- ADR 0016 moves to Accepted and says what touched.json keeps and when it is pruned.
- docs/CONTRACTS.md (new): one dated line per contract other agents depend on (HUD structure, S keys, progress code, config keys, CLI exit codes, conftest helpers, generated files, data shapes), each with its PR. Issue 95 then points to it.

Not in this order: MAINTAINERS.md, BRIEF.md, README.md (Team Codex, #59); the MAINTAINERS lines become a one-line follow-up after #59 lands.
