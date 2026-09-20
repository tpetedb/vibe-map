# ADR 0007: Every artifact is a task with a deterministic check, not only a demo

Status: Accepted, 2026-09-17

## Context

Artifacts stand on the four islands: the cafe, the well, the lighthouse, the dock, the windmill, the factory, the post office, the shop, the bank, the data centre, the energy grid, the library, the office, the households, the school and the rest. Each one carries a fake terminal that demonstrates its concept, and each demo is good: the cafe really does show a request, a status code and a body.

A demo is a thing the learner watches. Pressing a button in a panel and reading the output that panel was written to produce teaches the shape of an idea and nothing about doing it. Nothing is on the machine afterwards, nothing can be checked, and the artifact is worth no XP that was earned rather than collected. ADR 0004 already says quests award XP for verified work and never for self-report alone; the artifacts were the largest part of the game that the rule did not reach.

The two obvious ways to fix that both fail. Writing our own walkthrough of Docker or FastAPI means a second source of truth that goes stale and teaches our idea of the tool rather than the tool. Checking the work by asking a model means a check that costs money, needs a network, and gives a different answer on a Tuesday.

## Decision

Every artifact keeps its demo and gains a "Do it for real" task: a `real` block in `vibemap/data/campaign.json` with a title, a time under twenty minutes, a workspace directory, the documentation page it was written from, numbered steps, the commands that documentation gives, a definition of done and one `check` spec.

- **Written from the official documentation of the thing.** The cafe is `http.server`, the well is `sqlite3`, the dock is Docker's "Writing a Dockerfile" page, the windmill is the GitHub Actions events reference, the market stall is FastAPI's First Steps, the bridge is the MCP build-a-server quickstart, the factory is the DuckDB Python API, and so on for every one. The page is linked on the sheet, and the commands the task gives are the commands that page gives. When the tool changes, the page is the thing that changed and the walkthrough is corrected against it; we never become the second source of truth for somebody else's tool.
- **One home per task.** The work lives in `workspace/artifacts/<id>/`, which is the learner's zone and is where the check looks. The learner can find it without the game running.
- **The check is deterministic and offline.** `vibe check --artifact <id>` (or `--all`) reads what is on disk or runs it: a Dockerfile whose instructions all parse, a SQLite file with an indexed table holding rows, a FastAPI app that answers 200 to its own test client, a workflow file with a schedule trigger and a job with steps, an MCP config that names a server with a command, a queue script whose output shows two deliveries, then one retry, then one dead letter. The checks are one function per kind in `vibemap/artifact_checks.py`, kept out of `quests.py` so that the artifact family can grow without touching the workstream checks. Nothing reaches the network and nothing asks a model.
- **A missing tool is reported, never failed.** Each kind has two layers. The floor is offline and always runs: the file exists and holds what the documentation asks for. The confirmation runs the thing for real, and when the tool it needs is not installed the check says so with the install command and passes on the floor. A learner without Docker Desktop still builds a Dockerfile that parses and still earns the artifact; they are told exactly what they did not prove.
- **The progress code gains `artifactsBuilt` inside version 2.** The code stays at `v: 2`. An unknown key is ignored by an older game and by an older `vibe`, so a learner on last week's install loses the new list and keeps everything else. A version 3 would be refused outright by both sides, which is correct for a change that breaks a reader and wrong for a key that is additive. The versioned format still fails loudly; it simply is not failing here.

## Consequences

- An artifact built for real is worth half a workstream in XP, reads "built for real" on the sheet and in the Artifacts vault note, and building every one earns the `builder` badge. The sheet now distinguishes inspected from built, which is the distinction the brief cares about.
- Every task is one more thing that can go stale, and they go stale when someone else's documentation moves. That is accepted: a stale link is visible and cheap to fix, a walkthrough we invented is neither.
- `vibemap/artifact_checks.py` carries one kind of check per shape of deliverable, and the honest failure modes of each. It is the largest single file the check system has, and it is a file a maintainer reads one function at a time.
- Checks run the learner's own code. They do so with the interpreter running `vibe`, in the artifact's own directory, under a timeout, which is the same contract the mentor exercises use.
- A task that cannot be checked deterministically and offline does not ship. That rules out anything needing an account, a paid API or a network, and it is the reason the tasks lean on standard-library modules and local tools.
