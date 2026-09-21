- The build finds the game's modules instead of being told them. A module's
  file name is its place in the load order (two digits, an optional letter, a
  dash), so `tools/build.py` reads `src/game/*.js` in that order and a new
  module needs no edit to the build, which is what made two branches that each
  added one collide. A second source folder, `src/galaxy/`, is read the same
  way after it and may be absent. The generated parts (the campaign, `CONFIG`,
  `PETS`, the items, the tech tree and the notes module) are anchored to the
  module they sit in front of, so a rename is a loud build fault, and a file
  whose name is not a place is refused with its name. `game/vibe-map.html`
  comes out byte for byte the same as the hand-written list produced.
