# ci-shard-rebalance

Task (issue #205): every PR waits about 77 minutes on two browser shards, smoke and qol; ui, phone, bridges, panels and webkit take 10 to 30. `smoke` is the default shard (`default: true` in `.github/workflows/ci.yml`), so every browser file no other shard claims lands there: the hunt files dominate. From car K2's run (#202, job 107470214388): `test_game_hunt_f.py::test_the_artifact_surfaces_are_photographed` 213s and 187s, `test_game_hunt_b.py` cases at 60 to 105s each; the shard ran 133 tests in 66 minutes. `qol` carries `tests/test_game_qol*.py` and `tests/test_game_state.py`.

Do: measure (use `gh run view --job <id> --log` of recent runs on main for the `--durations` lines, and `uv run python tools/ci_shards.py --files smoke` for what the default collects; `gh api --allow-escape-sequences repos/tpetedb/vibe-map/actions/jobs/<id>/logs` works for a job log). Then add shards, for example `hunt` (tests/test_game_hunt*.py, split in two if it alone is over 35 minutes), `qol` split into two patterns, and a `galaxy` shard for tests/test_game_galaxy.py and tests/test_game_experience.py if they are in the default. Keep `smoke` as the default with headroom. Runners are free on this public repo; more shards is fine. Change only ci.yml's matrix (tools/ci_shards.py reads it back; do not change its code unless a guard forces it, and then say why). Record the table of shard to measured or estimated minutes here.

builder: builder-ci-shard-rebalance

## Measured

Sources: main's run 35947748862 (d2025a00, green, the fast case) and car K2's run 35948008834 (the slow case). The shards run pytest with `-q`, so a log gives each shard's total, its ten slowest tests, and a timestamp at every 72nd test. Per-file numbers below come from those checkpoints and the slowest-10 lists, spread over the per-file test counts of `pytest --collect-only -m "browser and not integration"`; they are estimates, not per-file measurements.

| Old shard | Tests | main run | K2 run |
|---|---|---|---|
| smoke (default) | 132 / 133 | 35 min | 66 min |
| qol | 113 / 137 | 76 min | 90 min |
| bridges | 57 | 29 min | 30 min |
| panels | 74 | 22 min | 22 min |
| ui | 50 | 17 min | 15 min |
| phone | 45 | 17 min | 11 min |
| webkit | 33 | 15 min | 28 min |

Checkpoints: smoke's first 72 tests (build, bottles, experience, 49 of hunt_b) took 20 min on main and 42 on K2; its last 60 took 15 and 24. Qol's first 72 (qol, feedback, settings, 15 of wayfinding) took 55 min on main; its last 41 (21 of wayfinding, state) 21 min. The same smoke files ran 1.9 times slower on K2's runner, so the slow column is what the split is sized against. Qol costs about 40 to 48 s a test on both runs.

## The split, estimated minutes of pytest (setup adds about 1)

| Shard | Files | Tests | fast runner | slow runner |
|---|---|---|---|---|
| hunt | test_game_hunt_b | 53 | 17 | 32 |
| qol-feedback | test_game_qol_feedback, test_game_state | 43 | 27 | 28 |
| qol | test_game_qol, test_game_qol_settings | 34 | 27 | 28 |
| bridges | unchanged | 57 | 29 | 30 |
| pictures | test_game_hunt_f, test_game_experience | 30 | 12 | 22 |
| qol-wayfinding | test_game_qol_wayfinding | 36 | 21 | 22 |
| panels | unchanged | 74 | 22 | 22 |
| webkit | unchanged | 33 | 15 | 28 |
| smoke (default) | smoke, stops, grow, bottles, and unclaimed: build, harness_determinism, media | 49 | 6 | 10 |
| ui | unchanged | 50 | 17 | 15 |
| phone | unchanged | 45 | 17 | 11 |

Slowest estimated shard: hunt, about 32 min on the slow runner. `test_game_hunt_b.py` is one file and a shard claims whole files, so it cannot be split further here; if it grows, the file is what splits. K2 adds `test_game_qol_continuity.py` (24 tests, about 14 min, two cases at 134 and 160 s): no pattern claims it, so it lands in the default smoke shard, about 24 min on the slow runner, still under hunt. A later order can give it a qol home once it is on main (a pattern that claims nothing today fails the guard).
