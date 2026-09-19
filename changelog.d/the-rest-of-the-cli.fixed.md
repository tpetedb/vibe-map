- `vibe status` draws the same four marks as the campaign map in `vibe start`
  (`x` checked, `i` claimed but not verified, `>` next, `.` to do) and prints
  the legend whenever the grid is drawn, so a forced claim no longer shows an
  unexplained `i`. How many stops an evening has comes from the campaign now,
  not from an `8` typed into the command.
- `vibe check` refuses two targets instead of running the first and exiting 0,
  and an empty `--mentor`, `--artifact` or `--topic` is refused the way an
  unknown id is rather than quietly checking campus stop 1.
- `vibe check --fork all` claims the forking stop when the four challenges
  pass, as the source always promised; one challenge says what it proved and
  claims nothing, instead of telling everyone their fork builds.
- Raising the difficulty no longer pays out again for a stop a check already
  verified. A stop claimed in the game or with `--force` is still topped up.
- A hint at beginner and easy is the whole hint; at normal and hard it stops
  after the first sentence, which is the difference the difficulty table
  promises.
- `vibe fork --force` says what it is about to delete and asks first.
- `vibe toolbelt --install <unknown>` is one red line, not a traceback, and
  `--install missing` on a complete tier says so instead of printing nothing.
- `vibe council` convenes the mentors of the island you are on, says who did
  not fit at the four-seat table, and refuses an empty question before it
  spends a provider call.
- `vibe explain` escapes what the provider wrote, so an answer containing
  square brackets no longer dies with a markup error; it diffs from the first
  commit and says so when the history is shorter than `-n`, and `-n 0` blames
  the argument rather than the repository.
- `vibe news --limit 0` no longer empties `News.md` and `news.json`, and
  `--limit -1` is refused instead of being read as a Python slice. `vibe news`
  rebuilds Tonight, so the note it writes is never an orphan.
- `vibe scores` in a camp that has not played yet exits 0 with one line, so
  `just scores` stops reporting day one as a failed recipe.
- `vibe play`, `vibe dashboard` and the play launcher print the path when the
  machine has no opener, instead of raising `FileNotFoundError`, and
  `vibe play --offline` reports a network it cannot reach instead of a urllib
  traceback.
- `vibe start` says it needs a terminal instead of hanging when stdin is a
  pipe.
- `vibe pet --all` refuses to be combined with a write, rather than printing
  the gallery and dropping `--species` on the floor.
- `vibe import` writes the companion chosen in the game into
  `config/camp.toml`, the way `vibe pet` carries it the other way.
