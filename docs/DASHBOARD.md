# The dashboard

The dashboard answers one question: what did the learner actually do. The game
and the terminal show the same campaign from the state each one can observe.
Neither view is a second system of record.

## In the game

Press **Stats** in the HUD. The panel has summary tiles, one progress ring per
island, XP over time, activity by day and hour, time spent at stops, the route
through mentor encounters and a feed of recent events. A chart with no events
says that plainly instead of inventing a line.

The game records events for claims, mentors, artifacts, collectibles and other
actions in this browser. The panel derives every number and chart from that
event log and the rest of the saved game state. Reloading rebuilds the view.

## In the terminal

Run `uv run vibe dashboard`, or `just dashboard`. It writes
`workspace/dashboard.html` from `.vibe/state.json`, the vault and
`workspace/data/scores.csv`, then opens the report. `uv run vibe dashboard
--json` prints the same calculated values for another tool to read. The HTML
file is generated output and can be removed and written again.

The browser and terminal cannot report identical dwell time. The game knows
how long a sheet stayed open. The CLI has verified checks and timestamps, but
no browser session clock, so it does not pretend otherwise.

## Saved state

The game keeps its event log and progress in its `S` object in local storage.
The terminal reads the versioned `.vibe/state.json`. A progress code carries
campaign progress between them; each dashboard then derives its own view from
the state it has.

## Accessibility

Every chart is inline SVG with `role="img"` and an `aria-label` that states its
reading. Data marks expose readable labels where the chart supports them, and
labels and shape carry the meaning, so colour is never the only distinction.
The panel is keyboard reachable, closes with Escape and has an explicit empty
state.

## Responsible code and checks

- `src/game/89-dashboard.js` records and renders the in-game view.
- `vibemap/dashboard.py` calculates and writes the terminal report.
- `tests/test_game_dashboard.py` drives the Stats panel through its controls.
- `tests/test_dashboard.py` checks the report, JSON output and shared event
  meanings.

The visual tokens shared by both views are documented in
[`DESIGN.md`](DESIGN.md).
