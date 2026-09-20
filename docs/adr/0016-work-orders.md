# ADR 0016: A task for an agent is a work order, and its acceptance is a command

Status: Proposed, 2026-09-21

## Context

Most of this product is built by agents working in parallel, several at a time, each in its own worktree. Three days of that taught what goes wrong, and none of it was the agents' ability to write code:

- **The task lived in a prompt.** A builder's brief said which files were its own and which checks had to pass, in prose, and nothing held it to either. Whether a batch was "done" was whatever the report said.
- **Collisions were found at merge time.** Two builders touching `src/style.css` or `tools/build.py` only met in the train car. Avoiding that was a triage agent reading finding lists and proposing groups by hand.
- **Defects hid between pull requests.** A security guard from one branch and new HTML from another were each green alone and wrong together. So were a new scene module and a new rule for removing things from the scene.
- **The plan was not in the repository.** When the orchestrating session died, its finding lists and batch tables died with it and had to be dug out of a transcript.
- **Nobody reviewed.** The builder's own tests were the only judge of the builder's own work.

Tom asked for the opposite, explicitly: themed teams with managers who coordinate, every stage proven deterministically, review by another agent against the task, the criteria and the output, embedded in the harness with hooks, recipes, templates and skills, and the GitHub issues as the place the agents talk.

## Decision

**A task is a file.** `work/orders/<id>/order.toml` names the team, the branch, the files the order owns (files or folders, never globs), the orders it needs first, and its acceptance criteria. A criterion is either a `check`, a shell command where exit 0 is pass, or a `judge`, a ruling a named role has to write down. Every order has at least one check. The format carries `v = 1` and an unknown version is refused.

**Teams are themes with paths.** `work/teams.toml` lists the teams (state, scene, panels, content, cli, harness, docs) and the paths each answers for; a path belongs to the first team that covers it, and a test fails when a tracked file belongs to none. An order owns files of its own team. Another team's file goes in `cross` and needs that team's sign-off file before the order is accepted. That is what "managers discuss with each other" comes down to: the talk is on the issue, the agreement is a file that can be checked.

**One tool decides, and everything calls it.** `tools/work.py` (standard library only, so a hook can run it with a bare `python3`) checks that orders are readable, that no two active orders own the same file, that a branch changed nothing outside its order, that every check passes, that the review is by someone else, rules on every criterion with evidence and is tied to a full commit id after which neither the order file nor the branch's own contribution to the files it owns changed (compared as a verbatim patch id, so a clean sync with main keeps a review and any edit ends it, a change of indentation included; the review and the sign-offs themselves are left out, or an order that owns `work/` would end its review by committing it), and that every cross team signed. The `work-*` recipes, the hooks and CI are three doors to the same checks.

**The harness holds agents to it, not the prompt.** A `PreToolUse` hook refuses an edit outside the orders on the current branch and names the team that owns the file. It fails open: anything it cannot read lets the edit through, because a broken order has to stay repairable and the checks refuse it later anyway. The same hook notes which subagent edited under which order, and a `SubagentStop` hook uses that, not the wording of a report, to run the order's checks and send the subagent back once with the failing output; a subagent's report does not reliably reach a hook. A session is only sent back when its report's first line is `order: <id>`, because `Stop` fires at the end of every turn and a check takes minutes. The stop hook lets go on the second attempt, because a hook that always blocks never ends, and it ends its own checks inside the hook's time limit. It is a reminder for a cooperative agent and nothing more: an edit made through a shell is seen by no hook. Everything that decides whether work lands (`work-check`, `work-accept`, CI) fails closed.

**Status is derived, never stored.** An order is active while its branch is checked out in some worktree and landed once its review is on `main`. `just work-plan <goal>` turns a goal into launch groups: what an order needs comes first, no two orders in a group own the same file, and a group fits the budget of four. Landed orders are swept at a release, like changelog fragments.

**The issue is the conversation, the repository is the record.** An order may name an issue. The tool keeps one status comment there, rewritten in place from the same data the checks use, and prints the thread for an agent to read before it starts. It shows only comments from people who can push here: on a public repository anyone can comment, and an agent that takes instructions from an issue takes them from anyone.

**Nothing of this reaches a learner's camp.** `tools/sync_template.py` renders the camp's `settings.json` without the hooks that call `tools/work.py`, and the skill is product-only.

## Consequences

- A review lapses when an owned file changes after it, and that includes the orchestrator's own fixes in a train car. That is friction on purpose: a fix made while combining branches is unreviewed code.
- Orders cost a few minutes to write. One-line fixes by a person need none; CI only judges pull requests that carry an order.
- The budget stays four. A bigger swarm means more roles and more groups, not more agents at once: two sessions already ended on the account's spend limit.
- A train car carries several orders, so CI checks ownership only on a single order's pull request; each order in a car was checked where it was built.
- The CI step runs after the tests and is red until the review lands. A builder is done when everything else is green; the last step turning green is the reviewer's doing.
- `result.json` is a file the builder can write, so it only speeds up the builder's own loop. `work-accept` measures again.
- This very change went through its own review twice before it was accepted. The first found sixteen defects, three of them high: a test the change broke and CI hid, a scaffold that locked the edit hook, and a stop hook reading a field a subagent's report never reaches. The second found that an order owning `work/` ended its own review by committing it, that two tests passed only because the builder's machine ignores `__pycache__` globally, and that a change of indentation slipped past the review. Each fix has a test, and the tests now run without the machine's git configuration. That is the argument for the review stage.
- On a fork's pull request the CI step is safe to run (branch names arrive as variables, no criterion is executed, the job reads only) and is not a gate: the fork's own copy of the tool runs, and `by` is free text. It guards collaborators against mistakes, not the repository against strangers; branch protection and a person's merge do that.
- Known and accepted: `touched.json` is never pruned; agents on a Python older than 3.11 run without the hooks, with a line on stderr saying so.
- The check commands run with `shell=True` from a file in the repository. That is the same trust as the `justfile`: whoever can merge an order can already run code here.
- Not decided yet: a saved Workflow script that runs plan, build, check, review and improve as one deterministic pipeline, and whether managers should be standing agents or, as now, roles called at three fixed points.
