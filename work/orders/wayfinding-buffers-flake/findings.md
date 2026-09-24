# wayfinding-buffers-flake

`tests/test_game_qol_wayfinding.py::test_a_walk_makes_its_buffers_once_and_not_every_frame` failed in car K2's CI (#202, qol shard) with (3, 7). Cause, found by a probe: in `src/game/31-animate.js` `animate()` a dust puff appears only when `Math.random() < dt*14`; the first puff of a session uploads the shared `shape("dust", SphereGeometry(.09,5,5))`, four buffers. If no puff lands in the first three frames of the walk, those four are counted after `made`, and the test fails. Forcing `Math.random` to 0.999 for those frames reproduces (3, 7) on plain main d2025a0. So it is a pre-existing flake in main, not caused by any car. A reproduction is at /Users/maxgroupit/.claude/jobs/5d0da65f/tmp/buffers_dust_late_repro.py.

Do: change only the test so it starts counting after the dust shape has been uploaded, for example wait (with a page-side condition, never a sleep) until a dust puff exists or until the dust geometry is in the renderer's memory, then take `made`. Keep the bound `after - made <= 2`. Do not change `src/`. Show the late-puff reproduction failing before and passing after.

builder:
