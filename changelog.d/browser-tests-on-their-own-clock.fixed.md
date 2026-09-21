- The browser tests no longer depend on when or where they run. Every page
  fixture now comes from one helper in `tests/conftest.py`: it shifts the
  page's clock to noon of the same day (shifted, never frozen, so sheet dwell,
  the speed run achievement and the dashboard's days still measure), keeps a
  record of every toast the page raised so a test asks `GamePage.toasts()`
  instead of reading a notice that expires after five seconds, and refuses a
  screenshot written anywhere but `tests/out`, which is what used to leave
  `docs/media/pets-game/*.png` changed after a green run.
- A wait that runs out now says which wait it was and how many frames the page
  drew while it waited, and the camera landing carries a budget of its own with
  the measurement behind it, because the game advances its animations by at
  most 0.05 s a frame and a software renderer stretches a 1.4 s glide into
  seconds of wall clock.
