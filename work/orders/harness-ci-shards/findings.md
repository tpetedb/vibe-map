# Why

Every order that adds a browser test has to add the file to a shard list in `.github/workflows/ci.yml`, and `tests/test_repo.py::test_every_browser_test_file_is_in_exactly_one_shard` fails until it does. So every such order owns `ci.yml`, no two of them can be built at once, and the one real conflict in train car 147 was exactly this line.

# What

- A shard may name files by pattern (`tests/test_game_qol*.py`), and `tools/ci_shards.py` expands patterns the same way for CI and for the guard.
- One shard is the default for a browser test file no pattern claims, so a new file always runs somewhere.
- The guard keeps its three promises: every browser test file runs, none runs twice, no shard names a file that does not exist. A pattern that matches nothing fails it.
- The shard durations stay balanced: print the split in the guard's failure message.
- Nothing else in `ci.yml` changes: the two required contexts keep their names (`test_the_required_context_is_its_own_job_and_keeps_its_name`).
