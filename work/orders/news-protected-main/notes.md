# News publication recovery

Issue: #174. Failed run: https://github.com/tpetedb/vibe-map/actions/runs/35719856171.
The old workflow pushed directly to protected main and received GH006.

The workflow checks out main, serializes publishers, generates the news and game,
and uploads all four generated files as `news-snapshot` before publication. The
publisher commits only those files to `automation/daily-news`, pushes normally,
and opens a PR against main. It never merges, force-pushes or changes protections.
An existing open PR is left for review. When generated files changed, any
existing branch without an open PR is preserved and reported as requiring
attention, including a merged branch that was not deleted. After merging, the
maintainer must confirm the branch's work is integrated and delete it before the
next update. This deliberately preserves
manual follow-up commits and squash-merged history rather than guessing safety.

The repository currently reports `can_approve_pull_request_reviews=false`.
An administrator may enable Settings > Actions > General > Workflow permissions >
Allow GitHub Actions to create and approve pull requests. This implementation
does not change that setting. Without it, the push still preserves the snapshot
branch; the failed run's summary gives a `gh pr create` command for a maintainer.
The artifact remains available if even pushing fails. There is no extra secret.

Official source opened 2026-09-22:
https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow
GitHub now creates approval-required workflow runs for PRs opened or updated by
GITHUB_TOKEN. A writer selects **Approve workflows to run** in the PR merge box,
then waits for required CI and reviews before merging. This is not automatic
approval or a branch-protection bypass.

Verification: six regression tests failed before the publisher existed, then all
six passed. Tests run the CLI against disposable real Git repositories and a
fake gh executable: new PR, no changes, pending PR, denied PR, existing branch,
and unrelated staged files. They assert main stays unchanged and only news
outputs reach the remote branch. No live news PR was created in these tests.
The workflow wiring is also checked (seven focused tests total). The first broad
non-browser run passed 699 tests and exposed a missing bullet in this change's
changelog fragment. That was corrected; all 32 changelog tests and seven news
publisher tests then passed together. `just sync-main` fast gates passed and
committed the synchronized work, including the regenerated Map note date.
