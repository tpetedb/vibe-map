# Source

Issue #148 and its comments (`gh issue view 148 --comments`), and the lists at the top of tests/test_harness_determinism.py: the two files that still read a toast off the screen (STILL_READ_THE_SCREEN: test_game_bottles.py, test_game_ui.py) and the two that build their own game page (HAND_BUILT_PAGES: test_game_phone.py, test_game_news.py). Both lists may only shrink; this order empties them.

# What

- Convert the toast reads in test_game_bottles.py and test_game_ui.py to GamePage.toasts() / toast_said() (fed by RECORD_TOASTS in conftest.py).
- Move the hand-built pages in test_game_phone.py and test_game_news.py onto the shared fixtures in conftest.py (the shifted clock, the toast record, the write guard), adding a fixture if a profile is missing.
- The remaining #148 items that live in these files (guard blind spots, frame_count() swallowing errors, sleeps) with a test each.
- Not in this order: .github/workflows/ci.yml (retained Playwright traces go to a follow-up if still wanted).
