- A progress code is now checked whole before anything is merged, in the game
  and in the terminal alike: an island neither side has, a field of the wrong
  shape, a version that is not a number and a companion with no pixels are
  each refused by name, and a refused code leaves the camp exactly as it was.
  `vibe import` answers with that one sentence instead of a Python traceback.
- How many stops an island has is the campaign's to say on both sides, so a
  camp that adds a ninth stop can send it and a code cannot invent one.
- The XP inside a code is no longer added on top of the XP an import awards.
  XP derives from the log, which is what `vibe undo` hands back.
- A code from a camp nobody named no longer names the player `<your_name>`.
- A saved record in the browser is checked field by field before it becomes
  state: an island the game does not build, stops that are not numbers and a
  record that is not an object each cost that field and never the evening.
  The player is told which part started fresh.
- A code from a newer `vibe` now says the game is the old side and how to
  rebuild it, instead of asking for another export.
- Export selects the code in the box, so a browser that refuses the clipboard
  still leaves one keystroke that works, and the Sync panel names the command
  a camp really has: `vibe import <code>`. The box has an accessible name.
- Motion set to "No animations" stops Rolinda's typewriter too.
- The progress line in the onboarding menu counts stops the campaign has
  rather than a hard-coded 32.
