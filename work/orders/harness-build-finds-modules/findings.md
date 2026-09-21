# Why

`tools/build.py` names every module of `src/game/` in a hand-written list (the bottles had to add `19c-bottles.js` to it). So every order that adds a module owns `tools/build.py`, and no two of them can be built at once: the same trap the CI shard list was before `harness-ci-shards`. Galaxy adds a folder of modules.

# What

- The load order IS the file name: two digits, an optional letter, a dash. The build takes `src/game/*.js` sorted by that, and a second source folder (`src/galaxy/`, which does not exist yet) the same way after it, so the next order can add it without touching the build.
- The modules the build generates or injects between the files (`50-notes.js`, the campaign, `CONFIG`, `PETS`) keep their exact places. The proof that nothing moved is that `game/vibe-map.html` comes out byte-identical to main's (criterion c3).
- A file that does not fit the naming rule is refused loudly, with its name. `tools/sync_fork_source.py` mirrors what the build read, so check it still does.
