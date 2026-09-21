- A browser test that takes a page fixture no longer depends on when or where
  it runs. Every one of those fixtures now comes from one helper in
  `tests/conftest.py`: it shifts the page's clock to noon of the same day
  (shifted, never frozen, so sheet dwell, the speed run achievement and the
  dashboard's days still measure, and pinned to one instant, so the clock runs
  on across a reload), keeps one record of every toast the page raised so a
  test asks `GamePage.toasts()` instead of reading a notice that expires after
  five seconds, and refuses a screenshot written anywhere but `tests/out`,
  which is what used to leave `docs/media/pets-game/*.png` changed after a
  green run. Two files still read a toast off the screen and two still build
  their own page; both lists are named in `tests/test_harness_determinism.py`,
  both may only shrink, and both are on issue 148.
- A wait that runs out now says which wait it was and how many frames the page
  drew while it waited, and a wait for a toast adds what the page did say. The
  camera landing carries a budget of its own with the measurement behind it,
  because the game advances its animations by at most 0.05 s a frame and a
  software renderer stretches a 1.4 s glide into seconds of wall clock.
