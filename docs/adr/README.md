# Architecture decision records

One file per decision, in Michael Nygard's form (Title, Status, Context, Decision, Consequences), numbered in order and never renumbered. Write the next one with the `adr` skill (`.agents/skills/adr/SKILL.md`). A reversed decision is not deleted: a new record supersedes it and links back. `AGENTS.md` says what the rules are; this folder says why.

| ADR | Title | Status |
|---|---|---|
| [0001](0001-single-file-game.md) | The game is one HTML file, built from src/ by concatenation | Accepted, 2026-09-16 |
| [0002](0002-aoe-ideas-only.md) | From sokrypton/aoe we take ideas and structure, never code | Accepted, 2026-09-16 |
| [0003](0003-python-dependencies-welcome.md) | Python dependencies are welcome, managed by uv | Accepted, 2026-09-16 |
| [0004](0004-quests-verify-real-work.md) | Quests award XP for verified work, never for self-report alone | Accepted, 2026-09-16 |
| [0005](0005-mini-games.md) | A mini-game earns its place by teaching something the learner keeps | Accepted, 2026-09-17 |
| [0006](0006-config-levels.md) | Configuration has three nested levels, each flat inside | Accepted, 2026-09-17 |
| [0007](0007-artifacts-as-tasks.md) | Every artifact is a task with a deterministic check, not only a demo | Accepted, 2026-09-17 |
| [0008](0008-mentor-encounters.md) | A mentor encounter is a sourced dialogue plus one exercise that is checked | Accepted, 2026-09-17 |

Next number: 0009. The form: https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
