# Why

`90-boot.js` calls `applyTheme()`, `init3d()` and `applySettings()` at load. The whole game is wrapped in one function, so only function declarations are hoisted: a top-level `const` or `let` of a module that loads after boot does not exist yet when boot runs. `harness-build-finds-modules` placed `src/galaxy/` after `src/game/`, as its order text asked (the orchestrator's mistake, caught by its reviewer). `galaxy-places-schema` tried to fix it and had to revert, because `tests/test_build.py` pins the current order and was not among its files. This order owns both.

# What

- Every module of every folder in `MODULE_DIRS` comes before `90-boot.js`. Say it as a constraint in the comment, and test it: the test that pins `src/galaxy/` after the game changes to pin it before boot.
- While `src/galaxy/` does not exist, the built game is byte-identical to main's (criterion c3).
- The fork mirror still carries exactly what the build read.
