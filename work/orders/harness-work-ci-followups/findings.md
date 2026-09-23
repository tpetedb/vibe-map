# Source

Issue 149 and its comments: the lows the reviews of #151 and #152 left in tools/work.py and tools/ci_shards.py, plus the two `work.py ci` rules that cost CI cycles when landing (comment of 21 September: a plan riding with code, and one order plus a loose change). Read it with `just work-thread harness-work-ci-followups`.

# What

- git calls use `--literal-pathspecs`; the W2 test uses a real pathspec-magic file name.
- touched.json keeps the last edit per agent; the TOUCHED_KEEP comment says what is true.
- One CLI-level test that runs `tools/work.py` as a process.
- `plan` prints the groups, then "blocked by" for orders waiting on another goal, and calls only a real cycle a cycle.
- `ci` judges `ships_code` per order (a plan order with an empty builder whose owned files are untouched needs no review) and judges strays against each order branch's own contribution, not the whole pull request.
- `tools/ci_shards.py`: `browser_test_files()` honours pytest's exit code; a `--files` test; one fnmatch helper; the quoted default "false" becomes a boolean.
- `validate` warns on a criterion that runs pytest on an integration-marked file without `-m 'not integration'`.

Not in this order: `tools/sync_main.py` (Team Codex, same issue), AGENTS.md.
