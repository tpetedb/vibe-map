# ADR 0008: A mentor encounter is a sourced dialogue plus one exercise that is checked

Status: Accepted, 2026-09-17

## Context

Twelve real people stand on the islands: Cherny, Wu, Karpathy, LeCun, Hinton, Li, Sutton, Amodei, Olah, Hashimoto, Torvalds and the OpenCode team. Meeting one used to be two clicks. The learner pressed "Tell me more" or "Not interested", a paragraph appeared, a path was stored and a vault note was written. Nothing was learned that the learner could show anyone, and the choice was the only thing that mattered.

Putting real people in a game raises a problem the rest of the course does not have. A person who is on record has said particular things, in particular words, in places that can be linked. Writing dialogue for them is writing words they did not say. Quoting them verbatim at length is somebody else's text in our file, and a quotation mark in a game is read as a quotation whether or not the sentence is one.

The second problem is scale. Twelve encounters at an hour each is a second course. Twelve encounters at two clicks each is the thing being replaced.

## Decision

Each mentor has an `encounter` in `vibemap/data/campaign.json` with a dialogue and one exercise.

- **A paraphrase, with the source beside it, never an invented quote.** Every line the mentor speaks is our own sentence about something that person is on record saying, and it carries the index of the source it came from, which is rendered as a link on the mentor's card and in their vault note. Nothing is in quotation marks. This is the same rule ADR 0002 applies to sokrypton/aoe, one level up: ideas and structure, attributed, never the words. It also means a wrong line is falsifiable. A reader can open the link and see that we got it wrong, which is the only honest way to put a living person in a game.
- **The dialogue is walked one question at a time**, three or four exchanges, so the learner reads the mentor's answer to a question they just asked rather than a biography.
- **One exercise, under fifteen minutes, offline.** It lives in `workspace/mentors/<id>/` and it is the smallest thing that makes the idea true on the machine: Karpathy's bigram model prints the likeliest character after "a", Torvalds's script produces the same blob hash as `git hash-object`, Hinton's twenty steps of gradient descent land on the target, Sutton's brute-force search beats the rule the learner invented, and the note-shaped ones (Cherny's CLAUDE.md rule with the command that proves it, Wu's spec-plan-todo, Olah's mermaid circuit, Hashimoto's one readable config file, and the rest) must hold the sections the exercise asks for. Fifteen minutes is the budget that makes twelve encounters possible in the evenings the course actually has; offline is what makes the check deterministic and free, as it is for the artifacts.
- **`vibe check --mentor <id>` (or `--all`) verifies it**, running the learner's script with the interpreter running `vibe` and matching the line the exercise says it prints, or reading the file for the sections it asks for. A note of at least twenty-five of the learner's own words under `## What I learned` is the strict-level floor, as it is everywhere else.
- **A verified encounter is worth half a workstream in XP.** Fifteen minutes of real work against an hour of a workstream is roughly the ratio, and the same share the artifacts use, so the two families stay comparable and a learner cannot farm XP by picking the cheaper one. It is deliberately not a whole workstream: an encounter is a detour, and the campaign's thirty-two stops stay the spine.
- **The plaque is the visible consequence.** A verified encounter turns the mentor's ring green and raises a plaque on their spot with their one line on it, writes the encounter and the exercise into their vault note, and all twelve earn the `mentored` badge. A consequence that is only a number in a status command is not a consequence; the island has to look different.
- **The progress code gains `mentors` inside version 2**, for the same reason `artifactsBuilt` did: the key is additive, an older game and an older `vibe` ignore it and keep working, and a version 3 would refuse a code that both sides can read perfectly well.

## Consequences

- Twelve dialogues and twelve exercises are content with a maintenance cost. Sources move and people say new things; the source list per mentor is the thing to check when a link dies, and a line whose source is gone is rewritten or removed rather than kept.
- The encounters are the part of the game where being wrong is a reputational matter, not a bug. Review of a mentor line is review of the source, and a new line without a source does not ship.
- Exercises run the learner's own code, offline and under a timeout, which is the same contract `vibemap/artifact_checks.py` uses. The mentor checks stay in `vibemap/quests.py` because they share the note check and the difficulty levels with the workstreams.
- `vibe mentor <id> deep|skip` still records a path, so the old choice survives as the thing that colours the vault; the encounter is what earns the plaque.
- Twelve encounters and twenty artifacts at half a workstream each are a large share of the XP a learner can earn outside the thirty-two stops. Any future family of side work is held to the same share, so the ladder does not drift.
