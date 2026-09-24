- Every browser test now takes its game page from the shared fixtures, so the
  phone and file URL tests run on the same noon clock, toast record and write
  guard as the rest, and the bottle and signpost tests ask the toast record
  what was said instead of reading a notice that expires after five seconds.
- The test guards see a toast selector kept in a parameter default, a dict, a
  class attribute or a helper module, read `.tstats` as the title screen it is,
  and see a game page opened with `new_page()` or under another name for
  `GamePage`. A new guard names the tests that still wait on the wall clock.
- A wait for more frames no longer passes at once when the page could not say
  how many it had drawn, and a wait that runs out on a closed page says so
  instead of reporting a negative number of frames.
