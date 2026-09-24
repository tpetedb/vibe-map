order: issue59-docs-played
role: builder

The branch was first merged with `origin/main` at `df937a2`, then again after
PR #185 landed at `0222b50`, using `just sync-main --no-fetch`. Git ancestry
confirmed each main head as an ancestor. The generated vault map conflict was
resolved to the current main output, leaving no vault delta in this order.

The focused documentation, played-camp, and media tests pass together. I also
ran the `regen_played.py` command itself against a disposable local checkout
and bare Git remote. Its dry run changed neither checkout nor remote. Its
regeneration produced a clean local commit with all 32 stops, a scripted fork,
and the gameplay GIF, while the bare remote stayed at its original commit.
The rollback, dirty-target, ignored-data, and explicit-push cases are covered
by `tests/test_regen_played.py` using temporary repositories.

Independent pre-review found that an unrelated clean camp with an origin
could pass the old target check. The tool now requires played-repository
identity on both fetch and push URLs before any mutation. A clean product
remote and a misdirected push URL are negative test cases. A second run with
the same product leaves the reviewed commit intact; a tracked source
fingerprint makes that check before staging. Matching ignored learner files
remain in place, and the MCP example names the destination checkout rather
than the discarded temporary stage.

I regenerated the GIF from the post-#185 built game, opened it and sampled its
27 frames. They show the walker on
the campus-to-winter bridge, the winter Roadmap, the first workstream with the
claim button, and the winter island after the claim. The media test also
checks bridge-deck state and the claim through the running game.

External follow-up: the repository owner still needs to upload
`docs/media/hero.png` as the GitHub social preview after this work lands. The
separate played repository has not been changed or pushed by this recovery.

The first sandboxed `just sync-main --no-fetch` printed success even though
Git said it could not lock `ORIG_HEAD` and `index.lock` under the parent
repository's `.git/worktrees/codex-issue59-docs/` (operation not permitted).
That command returned exit 0 but did not merge `origin/main`; an unsandboxed
retry completed the merge. This is a separate `tools/sync_main.py` error
handling defect outside this order's owned files.

I removed the incidental regenerated `vault/Camp/Map.md` date and hash delta
from this order's diff. It reflected the day of the sync, not played-camp
behavior. `docs/media/README.md` now uses the supported
`uv run python tools/tui_media.py --pets` command.

Final local evidence on the post-#185 branch: 18 documentation and
played-generator tests passed, all 8 media tests passed, Ruff and formatting
passed, the style and whitespace guards passed, and a disposable invocation
of the actual command completed dry run, regeneration and a no-change repeat
with 32 stops and an unchanged bare remote. The board directed this order to
use the protected PR's full CI gate instead of a duplicate local full
`just verify`; no full local suite completion is claimed. Independent review
and exact-head CI are still required before integration.
