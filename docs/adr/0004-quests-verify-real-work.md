# ADR 0004: Quests award XP for verified work, never for self-report alone

Status: Accepted, 2026-09-16

## Context

The course is a game: eight workstreams per evening, XP, levels named after the ages of the tech tree, badges. In the first companion, progress was self-reported: `done 3` marked a workstream done, and the game imported the code. Self-report is worth nothing as a signal. A learner who skims can claim everything, a learner who did the work gets the same number, and an agent asked to "mark it done" does so without looking.

What the course wants the learner to build is visible in the repo: `game/index.html` is no longer the placeholder, `AGENTS.md` has rules, `sql/` has queries, `git log` has commits, `.claude/settings.json` has a hook, the vault has linked notes. A check can look.

Some outcomes cannot be checked exactly from the repo (a deployed URL, a scheduled job on another machine), and a learner must be able to move on when a check is wrong or the evening is short.

## Decision

We will award XP only through checks that inspect the repository: files and their content, git history, the vault, the settings, test results. `vibe check N` runs the checks for workstream N and reports each with a hint; `vibe done N` runs them first and claims only when they pass.

We will let `vibe done N --force` claim anyway, at half XP, and record which checks passed and failed in the state file next to the claim.

We will grade by difficulty: lenient checks always apply, strict ones from `hard` up, extra ones from `expert` up; XP is 100 times the difficulty multiplier.

We will treat a stop claimed in the game as a claim and never as a check: `vibe import` awards half the XP, says in plain words that the stop is imported and not verified, and names the `vibe check` that pays the rest. `vibe status` marks such a stop `i` instead of `x`, and the first check that passes tops it up to full, the same way it tops up a `--force` claim.

We will let `vibe check` exit 1 when any check failed and 0 when they all passed, so the course's own gate can be a step in a hook or a workflow. `--no-claim` changes what is recorded, never the exit code.

We will keep the checks with the campaign: a workstream without a quest and hints is a test failure.

## Consequences

- XP means something: the state file records what was verified, and the vault note for the workstream lists the checks that passed.
- The checks must track the campaign and the repo layout. A renamed file breaks a check, and a check that is wrong frustrates a learner who did the work; `--force` is the escape hatch, and its half XP is the honest price of not being checked.
- Checks that shell out (git, the tests) run with a timeout and never crash the CLI: a crashed check is a failed check with a message.
- The game's progress code still exists and `vibe import` reads it, but the verified state file is the source of truth, not the game.
- Half XP for an unchecked claim is the same price everywhere: forced, imported from the game, or both. The state file holds one log entry per payment, so the top-up is arithmetic on data that is already there and nothing has to remember whether a stop was ever paid.
- The exit code makes a failed check a normal failure for any tool that runs it. A crashed check is still a failed check with a message, never a traceback in the detail column.
- A learner who wants full XP has to do the work. That is the course.
