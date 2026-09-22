# Recovery review, 2026-09-22

Reviewer: codex-review-qol4-recovery. Builder: codex-root-recovery.

This review covers the uncommitted recovery delta against `c8d1ff59a1d1d95ebc403ab316771afb4e529050`, not a renewed acceptance of the entire order. No blocking findings in that delta.

## Behavior and coverage

The achievement interval now reads `clock.elapsedTime`. The frame loop advances that clock before `tickAvatar`, while movement alone uses the capped 0.05-second delta. Sparse frames therefore no longer turn a one-second achievement interval into twenty rendered frames. Reduced motion zeros the ambient animation phase, not `clock.elapsedTime`, so achievements continue with motion disabled.

The visibility handler stops the same clock and restores its elapsed value on return. Hidden time does not advance the achievement interval. A lower elapsed value after clock replacement causes one fresh check rather than waiting for the prior clock's timestamp. Repeated checks cannot duplicate an achievement because `unlock` and `achCheck` both consult persisted achievement IDs. Flight and missing-avatar early returns retain their existing behavior.

The new controlled-clock tests assert that First light starts absent and appears after two simulated seconds with only one or two frames. Both motion settings are covered, without a real-time sleep. The builder recorded that both failed with the old capped-delta implementation.

The toast-record tests retain agreement between the raised counter and stored records, and now assert exactly one repair notice and exactly one First light notice. Removing the intermediate total of exactly one avoids assuming that the achievement cannot arrive behind the title screen. Checking zero `.tst` cards after removal tests transient cards directly; the independent Saved indicator may legitimately remain in the shared container. These changes do not weaken the record's loss or duplication checks.

## Independent verification

Ran:

```sh
uv run pytest -q tests/test_game_qol_feedback.py tests/test_harness_determinism.py -k 'earned_achievements_follow_elapsed_time or hidden_page_stops or toast_record_holds_each_notice_once or toast_record_outlives'
git diff --check
```

Both commands exited 0. All five selected browser cases passed. Test output: `/tmp/vibe-qol4-independent-review.log`. The tests include page-error assertions. I also inspected the generated game and fork-source diff and confirmed they mirror the source change.

No source files, tests, or formal review records were edited by this reviewer. Full verification, the complete order criteria, current state/panels sign-offs, and a formal review tied to the committed implementation remain required before delivery. Earlier review findings outside this recovery delta remain outside this interim ruling.
