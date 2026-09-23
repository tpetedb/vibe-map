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
| [0009](0009-local-chat-bridge.md) | In-game chat is answered by a loopback bridge the player starts, never by a key in the page | Accepted, 2026-09-18 |
| [0010](0010-real-names-and-live-content.md) | Real organisations and people appear by name as plain text, and everything they say is a link to their own words | Accepted, 2026-09-18 |
| [0013](0013-topics-as-data.md) | A topic of the tech tree is one TOML file in a pack, not a row in a Python list | Accepted, 2026-09-18 |
| [0014](0014-no-decorative-csp.md) | No Content-Security-Policy until it can block an injected script | Accepted, 2026-09-19 |
| [0015](0015-experiences-share-one-core.md) | An experience is a view over one shared core, and where a topic happened is data | Accepted, 2026-09-21 |
| [0016](0016-work-orders.md) | A task for an agent is a work order, and its acceptance is a command | Proposed, 2026-09-21 |
| [0017](0017-own-camp-own-bill.md) | A camp and its bill belong to the learner | Accepted, 2026-09-22 |
| [0018](0018-shared-memory.md) | The teams share one board room and one memory, read by one command at session start | Accepted, 2026-09-24 |

Next number: 0019. 0011 and 0012 were reserved for work that did not land and are never reused: a number names one decision, forever. The form: https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions
