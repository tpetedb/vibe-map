- A browser shard in CI claims its test files by name or by pattern
  (`tests/test_game_qol*.py`), and one shard is the default: a browser test
  file no pattern claims runs there. A new browser test is run from the moment
  it exists, without an edit to `.github/workflows/ci.yml`, which is what made
  two branches that each added one collide. `tools/ci_shards.py` expands the
  matrix the same way for the shard jobs and for the guard, and the guard still
  refuses a file in no shard or in two, now also a pattern that claims nothing,
  and prints the whole split when it fails.
