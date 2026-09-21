# Source

Issue 148, all four items and its comments. Read it with `just work-thread harness-test-determinism`.

# Findings

### D1 Between 23:00 and 24:00 UTC a browser test fails on any branch
`src/game/18-avatar.js` grants Night owl when `new Date().getHours()>=23`; its toast replaces the one `tests/test_game_avatar.py::test_walking_over_a_collectible_picks_it_up` reads. Do not freeze `Date`: the game measures sheet dwell, the speed-run achievement and dashboard days with `Date.now()`. The four page fixtures in `tests/conftest.py` repeat the same lines: one helper, which adds an init script that shifts `Date` to noon of the same day and lets it run at real speed. A test that wants the night sets its own hour, and one such test proves Night owl fires at 23:30 and not at 12:00.

### D2 Tests read toasts from the screen, and toasts expire on a timer
`toast()` removes a toast after 5000 ms of wall clock. `tests/test_game_state.py` already carries a local record (`window.__toastLog`, a MutationObserver installed by init script). Move it into the page helper as `GamePage.toasts()`, convert the pickup test, and add a guard: no browser test reads `#toast` text directly.

### D3 Running the browser tests rewrites tracked files
`tests/test_game_pet.py` writes `docs/media/pets-game/*.png`. Test output belongs in `tests/out/`. Guard: a test that fails when a browser test file writes under a tracked path (assert on the paths the tests pass to `screenshot`, not on `git status` after the fact).

### D4 The zoom test stalls at its first level on Android, sometimes
`tests/test_game_camera.py::test_every_zoom_level_holds_the_phone_budget[game_android]` timed out in `wait_for_function` (20 s) on two heads and passed on re-runs. `_zoom_is` and `until(LANDED)` raise the same bare timeout: name the wait that expired in the failure message. Find out which one it is (run it under CPU throttling locally) and either fix the cause or, if the heaviest scene simply needs longer to land on a software renderer, say so in the test with the measured number. A performance finding goes to the scene team as a note, not into this order.
