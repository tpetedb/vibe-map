
## Codex recovery, 2026-09-22

The original implementation and review history are preserved. The recovery builder is codex-root-recovery. Failed PR CI showed achievement waits at roughly one frame per second: `tickAvatar` accumulated movement `dt`, capped at 0.05 seconds per frame, so a nominal one-second check took more than 20 frames. Two new tests use Playwright's controlled clock to render sparse frames with motion on and off. Both failed before the fix; both pass using the game's elapsed clock, which already pauses while hidden. A rebuilt island's clock reset triggers a fresh check.

The focused run after that change passed five cases and reproduced the toast-record test's assumption that First light could only arrive after Resume. That assumption is invalid because the game also checks behind the title. The assertion now verifies exact individual message counts and agreement with the game's toast counter, regardless of arrival order. The transient-toast removal assertion targets `.tst` cards, leaving the independent saved indicator free to remain.

Ownership now includes tests/test_harness_determinism.py; the prior harness-test-determinism order is already integrated, and work validation reports zero active collisions. No acceptance criteria were removed. Full verification, independent review and current state/panels sign-offs remain required.
