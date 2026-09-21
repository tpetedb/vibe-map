# What (phase 2 of docs/GALAXY.md, without moving a single file)

- `tests/golden/`: one picture per island (campus, winter, desert, prod) at a fixed camera, a fixed clock and a fixed seed, taken from the built game. A test compares the live render with them. Decide the tolerance from measurement on this machine AND from what a CI runner renders (run the test in the pull request's CI before you settle it); compare structure (downscaled, per-region mean colour) rather than exact pixels if exact pixels cannot hold across machines. These pictures are what lets every later Galaxy order prove it did not touch the islands.
- `src/game/24-experience.js`: the registry and the contract of ADR 0015. `EXPERIENCES.islands = { name, build, dispose, tick, goTo, where, listing }`, each delegating to what already exists (`buildWorld`, the animate loop's per-frame work, `openCh`, the walk-to seam from quality-of-life batch 3, and so on). `activeExperience()` reads the preference (`S.settings.experience`, default `islands`; a URL parameter `?experience=` wins, for tests) and never writes it. NOTHING calls the registry yet: boot and the panels keep calling what they call today. Switching the call sites over is `galaxy-v0`'s work, once the files it needs are free.
- `listing()` for islands returns the stops as plain data: id, title, island, state (done, next, ahead). It is what the accessible list twin will be built from.

# Why nothing else is touched

`00-state.js`, `90-boot.js`, `85-settings.js` and `31-animate.js` belong to orders of the second wave that are being built now. This order owns one new module and its tests, so it can run beside all of them.
