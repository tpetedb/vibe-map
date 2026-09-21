# What this order built, and what it left

Six of the nine proposals in `findings.md` are built here, in the order the
ranking in issue #127 puts them in, each with its own test in
`tests/test_game_qol_wayfinding.py` seen failing against a build of `main`
first.

| Proposal | Where it lives | Its tests |
|---|---|---|
| 2, walk me there | `walkTo()` in `30-input.js`, the button and Shift and Enter in `41-search.js` | the three palette tests |
| 3, the arrow at the edge of the screen | `32-minimap.js`, the guide block | the five arrow tests |
| 6, the marker stays, with a line to it | `clearAim()` in `30-input.js`, `tickPath()` in `31-animate.js` | the two marker tests |
| 14, hurrying | `running()` in `30-input.js`, one multiplication in `31-animate.js` | the three hurrying tests |
| 16, the map you can tap | `32-minimap.js`, the taps, the big map and the stop list | the five map tests |
| 7, the idle half | `saverIdle()` in `31-animate.js` | the four saver tests |

Three are not built, and none of them is half built. They want a second order:

- **12, remappable keys.** The keys can be read through one map, but the row
  that captures a key belongs in `src/game/85-settings.js`, which this order
  does not own (it is batch 1's file, landed in #145). Shipping the map
  without the row would be a setting nobody can set.
- **13, gamepad.** Independent of the six above, and of a size that would have
  made this pull request harder to review rather than better.
- **15, fast travel to a visited island.** It wants a destination list and the
  island rebuild path. `walkTo()` refuses a walk during a flight, which is the
  seam it will build on.

Two things the findings ask for need a file this order does not own:

- The Settings row for `S.settings.guide` (proposal 3) is in
  `src/game/85-settings.js`. The guide reads the setting and defaults by
  difficulty, so the mode works; there is no dropdown for it yet.
- The "Walk there" button on a Roadmap row (proposal 2) is
  `renderMap()` in `src/game/40-sheet.js`, batch 3's file. The palette has the
  action, the Roadmap does not; `walkTo(n)` is the seam it will call.
