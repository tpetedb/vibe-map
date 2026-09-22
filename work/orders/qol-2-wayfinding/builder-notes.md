# What this order built, and what it left

Six of the nine proposals in `findings.md` are built here, in the order the
ranking in issue #127 puts them in, each with its own test in
`tests/test_game_qol_wayfinding.py` seen failing first. Two of the six are
built as far as this order's files reach and no further, and that is said
below, in the changelog fragment and in the pull request.

| Proposal | Where it lives | Its tests |
|---|---|---|
| 2, walk me there | `walkTo()`, `planRoute()` and `walkWatch()` in `30-input.js`, the button and Shift and Enter in `41-search.js` | the three palette tests, the walk round the hub, the walk that cannot get nearer, the two about leaving the island |
| 3, the arrow at the edge of the screen | `32-minimap.js`, the guide block | the six arrow tests |
| 6, the marker stays, with a way to it | `clearAim()` in `30-input.js`, `tickPath()` in `31-animate.js` | the two marker tests, the buffer count, the two that count the dashes on the screen |
| 14, hurrying | `running()` in `30-input.js`, one multiplication in `31-animate.js` | the four hurrying tests |
| 16, the map you can tap | `32-minimap.js`, the taps, the big map and the stop list | the five map tests |
| 7, the idle half | `saverIdle()` in `31-animate.js` | the four saver tests |

## Half built, and who finishes it

Both halves are in files of the panels team that this order does not own, so
they want one small follow-up order there (proposed id
`qol-2b-wayfinding-panels`, owning `src/game/85-settings.js` and
`src/game/40-sheet.js`, which today are both in `hunt-w-settings-news`, so it
goes in a launch group after that one):

- **Proposal 3, the Settings row.** The guide reads `S.settings.guide` (on,
  next, off) and defaults by difficulty, and a test holds that. There is no
  row for it: `guide` is in neither `SETTINGS_DEFAULTS` nor `SETTINGS_OPTIONS`,
  so a player at normal cannot turn the arrow off and one at expert cannot
  turn it on. The follow-up adds the two entries and the row.
- **Proposal 2, the Roadmap.** The palette, the map and the map's list walk
  there; the Roadmap's rows have no button, because `renderMap()` is in
  `40-sheet.js`. `walkTo(n)` is the seam it calls. The flight and then the
  walk, for a stop on another island, belongs with it: the palette and the map
  only list this island's stops, so the Roadmap is the one place that needs
  it, and `walkTo()` refuses a walk during a flight, which is what the chain
  builds on.

## Not built

Three want a second order, and none of these three is started:

- **12, remappable keys.** The row that captures a key belongs in
  `src/game/85-settings.js`. Shipping the map without the row would be a
  setting nobody can set.
- **13, gamepad.** Independent of the six above, and of a size that would have
  made this pull request harder to review rather than better.
- **15, fast travel to a visited island.** It wants a destination list and the
  island rebuild path.

## What the first review changed

- **A walk goes round.** `aim()` plans the way once, when the destination is
  taken: a one metre grid over the island, a cell free where the walker has
  room (on land with the shore a good half metre off on every side, clear of
  every obstacle by the walker's width and a little more), A* over the free
  cells, then every corner the walker can see past dropped. The frame loop
  steers at the next corner. A tap on the ground gets the same way as a stop.
  I walked every ordered pair of stops on all four islands on a real GPU, and
  again hurrying, before calling it done; the numbers are in the pull request.
- **A walk that cannot get nearer ends and says so.** `walkWatch()` measures
  the way that is left on the game's own clock; 1.2 s with no progress is a
  toast and the marker out. The shore no longer ends a walk silently: the
  watch is the one thing that does.
- **A walk belongs to its island.** `aimStale()` is asked once a frame and
  compares the scene the walk was taken on with the scene there is, so the
  bridge, the flight and the cut reduced motion makes of the flight are one
  rule, and `22-archipelago.js` is back to what main has. The flight ends the
  walk at take-off rather than on landing.
- **The way is dashes, not a GL line.** A line is one device pixel wide on any
  screen. Each dash is one instance of one mesh, a light plate on a dark one,
  unlit and outside the fog and the tone curve, so it has three to one against
  any ground from one of its two colours. Its buffers are made once; a frame
  of a walk writes matrices into them. The tests count `createBuffer` calls
  and count the dashes' pixels in a screenshot on the laptop and the Pixel
  profile.
- **The arrow test is in the state its name needs.** Seven stops delivered
  puts the arrow on the zoom buttons at the right hand edge, and the tap goes
  to the button under it. With `pointer-events:auto` back on `#guide` it fails.
- **Tap to hurry** listens for Shift on its own, down and up with no other key
  between, so Shift and Tab does not latch it, and it says which way it went.

The arrow points and takes no press. It was a button in the first round, and
in CI the phone's zoom buttons lost a tap to it
(`test_every_zoom_level_holds_the_phone_budget[game_android]`): it moves with
the camera, so sooner or later it sits on another control. It is an indicator
now, with `pointer-events: none`. Walking there is asked for where the
controls stay put: the palette, a plot on the map, a row in the map's list.

## Codex recovery, 2026-09-22

The interrupted worktree contained the routing, path-mesh, world-change and
Shift-and-Tab fixes above, plus a staged removal of the old per-transition
`clearAim()` calls. Those changes were preserved. The builder identity is now
`codex-recover-wayfinding`; the first review remains an independent improve
ruling until a new reviewer checks the recovered revision.

An additional regression reproduced the first review's held Shift after
window focus loss. It failed with running still true after blur; clearing
the held keys and the pending Shift-only gesture on blur makes it pass.
The existing toggle setting remains latched deliberately.

The first review's remaining low findings are deferred, not rejected:
`32-minimap.js` still computes guide metadata every frame, limits the large
map's list to 120 px, lacks a next-stop label in that list and repeats color
literals. Toast placement can overlap the map. `41-search.js` still closes
the palette without presenting a refused walk's reason. These need a follow-up
order after this order releases its files; they are separate from the high
and medium findings addressed here. The panels follow-up above remains
necessary before proposals 2 and 3 are complete.

Fresh validation results and screenshot observations are recorded below as
they complete. Earlier all-pairs gameplay claims above belong to the previous
builder's notes and are not claimed as fresh Codex gameplay evidence.

Recovery validation so far:

- `uv run pytest -q tests/test_game_qol_wayfinding.py`: passed the 35 tests
  collected before the additional focus-loss regression was added.
- `uv run pytest -q tests/test_game_qol_wayfinding.py -k losing_window_focus`:
  failed before the input reset, then passed after it.
- `uv run pytest -q -m 'not browser and not integration'`: 687 collected,
  passed.
- Ruff checks, `uv run python tools/checks.py style`, the sink guard,
  `just generated` and `git diff --check`: passed.
- Inspected the fresh desktop walking and Android path screenshots: the
  outlined dashes read against grass and show the route around the fountain.
  The iPhone big-map screenshot confirms the list-height limitation already
  recorded by the reviewer. These are automated screenshot observations,
  not a claim of fresh manual gameplay.
- Full `just verify` was started and interrupted to respect the shared
  machine's browser-test budget. It still needs to finish before committing.
- `work-thread` required network escalation. Bare system `python3` lacks
  `rich`; run work commands with `PATH="$PWD/.venv/bin:$PATH"` so their
  declared Python checks use the project environment.

The takeoff regression was strengthened to inspect the path during flight,
not only after landing. It failed: `has` was false and marker opacity zero,
but the path remained visible because the flight branch skips `tickPath()`.
`clearAim()` now calls `hidePath()` immediately. The strengthened flight test
and the reduced-motion cancellation test both pass. Lint, style, sinks and
all generated checks passed again after this change. The full wayfinding
criterion and full verification still need a fresh run on this final source.

The orchestrator identified the full-battery blocker as issue #175: two stale
integration assertions on main, being fixed in `codex-fork-integration`.
Hold full verification until that prerequisite lands, then commit only after
fresh required checks, run `just sync-main`, `just work-check
qol-2-wayfinding`, push and obtain a new independent review. PR #165's body
already discloses the deferred features and pending verification. No recovery
commit has been made yet; both inherited and new changes remain in this
worktree, including the originally staged archipelago cancellation cleanup.

Fresh manual gameplay in Chrome through the supported CUA browser tools:
served this worktree on `127.0.0.1:8767`, created a separate tab and a fresh
`Wayfinding test` player in Just the game mode. Search for `20:00`, then the
real Walk there button, moved the player around the fountain to the Data
Warehouse signpost. The visible dashes were clear and disappeared on arrival;
locked-stop feedback correctly said Centre of Excellence must be delivered.
Bigger opened all eight named map stop buttons. Choosing the Innovation Hub
row closed the large map, walked back and produced Enter Innovation Hub.
That button opened the lesson. Closing it, reloading, then Resume preserved
the test player's name and returned to the campus. The temporary tab and
local server were closed after verification. No completion or reward was
claimed in this manual session, and no console-error claim is made from AX
and screenshot observations alone.
