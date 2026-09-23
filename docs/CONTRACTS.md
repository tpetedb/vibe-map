# Contracts

What other agents and branches depend on: a HUD element, a key of the game state `S`, a key of the progress code, a configuration key, a CLI exit code, a test helper, a generated file, a data shape. Change one and you change it for everyone, so a change to a line here goes in the same pull request as the code, and the line says which pull request.

This file replaces the "current contracts" block that lived at the top of issue #95. Each line is dated with the day its pull request reached `main`, and was checked against the code on `main` on 2026-09-23. A contract made in a train car names the pull request that built it; the car is only how it landed. `tests/test_docs_followups.py` holds this file to the code: every helper, path, element id and recipe named here has to exist.

## HUD and screens

- 2026-09-18, #68: the HUD has a hierarchy. `#hud-bar` holds the stops, Search and Roadmap; everything else sits in `#hud-menu` behind `#hud-more-btn`, one button per feature in `#hud-sec` and Settings alone in `#hud-ter`. A new feature adds one button to `#hud-sec`.
- 2026-09-18, #68: the lesson sheet `#sheet` is a fixed overlay above the island, at most 820 px wide, not a page.
- 2026-09-19, #134: below 820 px wide, or on a touch device lying down, the whole More menu is the popup; a test that clicks a HUD button goes through `GamePage.hud_action()`, which opens More when the button is hidden.
- 2026-09-19, #134: a Full screen control carries class `fs-only`, hidden when the browser has no Fullscreen API.
- 2026-09-19, #115: the title is modal until Start. `#title` hides the HUD while it is up, and a key or a HUD click before Start does nothing; `#onboard` sits inside `#obfold`, folded shut for a returning player.
- 2026-09-20, #139: `#mapcont` (the Continue card above the Roadmap), `#cont` (the same card on the title) and `#copysay` (the polite live region every copy writes to) are in `src/body.html`.
- 2026-09-20, #140: the zoom controls are `#zoom` with `#zoom-in`, `#zoom-out` and `#zoom-fit`; `#gfxlost` is the notice when the WebGL context is lost.

## The game state S

- 2026-09-18, #81: `S.interests` has three meanings: `null` is not answered (`CONFIG.interests` speaks), `[]` is everything, a list is the choice. Read it through `interestList()`, `interestsAll()` and `wantsShelf()` in `src/game/86-interests.js`, never directly.
- 2026-09-18, #101: `S.topics` is the terminal's list of topics done, carried through the game untouched.
- 2026-09-19, #112: `S.pet` is a pet id or `none`; empty means the camp's `[pet]` choice. `petId()` is the one reader.
- 2026-09-19, #113: `S.doneW` is the saved progress per island; `S.done` is only a runtime view of the current island's list and is never saved.
- 2026-09-20, #140: `S.settings.zoom` is the camera level from -1 (close follow) through 0 (the fitted island) to 1 (the archipelago), starting at `CAM.zoom.start`.

## The progress code

- 2026-09-18, #81: the code is version 2 and grows only by adding keys inside it; `interests` joined `mentors`, `artifactsBuilt`, `items`, `ach` and `wear` that way. A list merges as a set, so a code adds and never removes.
- 2026-09-18, #101: the key `topics` is added inside version 2 the same way.
- 2026-09-19, #112: the key `pet` is added inside version 2; an id the game has no pixels for is refused by name on both sides.
- 2026-09-20, #131: every id in a code is a plain identifier (`plainId()`: letters, digits, dot, dash, underscore, colon) and a `path` value is `deep` or `skip`; anything else is refused, naming the field. A test that builds a code keeps to that.
- 2026-09-21, #146: a code the game or the CLI cannot read is refused whole with a message, never half merged; an unknown version is refused by both sides (`vibe import` exits 1).

## Configuration keys

- 2026-09-17, #44: `config/camp.toml` is the journey configuration of a camp, and this checkout is a camp too; `docs/CONFIG.md` says which setting lives where.
- 2026-09-18, #81: `[learner] interests` is a list of shelf ids; an unknown id is refused. The build injects it as `CONFIG.interests`, next to `CONFIG.personaInterests`.
- 2026-09-18, #89: `[news] live` is the off switch for the live world feed, injected as `CONFIG.news.live`; in the game `liveNews()` decides, and every feed-driven element carries class `live-feed` or asks `liveNews()`.
- 2026-09-19, #112: `[pet] species` and `enabled` become `CONFIG.pet`, so a hosted build ships the camp's companion.
- 2026-09-19, #128: `[game] site_url` becomes `CONFIG.site`; a link to a page published beside the game goes through `siteDoc()`.
- 2026-09-19, #119: anything written into `config/camp.toml` or a theme file goes through `toml_str()`, and the file is named to the user through `config_label()`.

## CLI commands and exit codes

- 2026-09-18, #101: every check family exits 0 when every check passed and 1 when one did not: `vibe check <n>`, `--mentor`, `--artifact`, `--topic`, `--fork`.
- 2026-09-18, #81: `vibe interests set` with an unknown shelf exits 1 with "unknown shelf".
- 2026-09-19, #119: a command that writes configuration (`vibe name`, `persona`, `difficulty`, `provider`, `mode`, `interests`) exits 1 with "no camp at" outside a camp instead of inventing one.
- 2026-09-19, #121: a refused manifest raises `quests.Refused`, a `ValueError`, and prints its message alone.
- 2026-09-20, #138: `vibe check` refuses two of `--mentor`, `--artifact`, `--topic` and `--fork` at once (exit 1); `vibe news --limit` and `vibe explain --commits` below 1 exit 2 with click's message; `vibe scores` with no scores yet exits 0; `vibe start` without a terminal exits 1.
- 2026-09-20, #138: the progress grid has one language, `stop_marks()` in `vibemap/campaign.py` (`x` checked, `i` claimed, `>` next, `.` to do), and `stop_count()` replaces the literal 8.

## Test helpers

- 2026-09-17, #42: a browser test never sleeps; it waits for something the page produced, such as `window.__debug().frame`.
- 2026-09-18, #68: `game_desktop` is a Chromium page at 1440x900, next to `game` at 420x860; `GamePage.hud_action()` clicks a HUD button wherever the width put it.
- 2026-09-18, #100: `GamePage.still()` counts a sample only after a new paint, `GamePage.until()` waits for a condition the page makes true, and `GamePage.sheet_in_place()` waits for the sheet's spring to reach identity before anything measures it.
- 2026-09-19, #134: `PHONES` and `phone_options()` in `tests/conftest.py` are the two phone profiles; the fixtures `game_android` and `game_webkit_iphone` are built from them, and every name in `BROWSER_FIXTURES` marks a test as a browser test.
- 2026-09-21, #158: every page believes it is noon of today; `GamePage.set_clock()` picks another hour, `GamePage.toast_said()` asks the record of toasts instead of the screen, and `out_file()` refuses a write outside the test output folder.
- 2026-09-21, #152: a browser test file is claimed by name or pattern in the `browser-shard` matrix of `.github/workflows/ci.yml`; a file nothing claims runs in `smoke`, the default shard, and `tests/test_repo.py` fails on a file in two shards or a pattern that claims nothing.

## Generated files

- 2026-09-18, #105: generated outputs are never merged by hand. `.gitattributes` marks them `merge=binary`, and `just sync-main` takes a side and regenerates them in dependency order; `GENERATED` in `tools/sync_main.py` is the list.
- 2026-09-18, #105: a change is a fragment in `changelog.d/`, never an edit of `CHANGELOG.md`; CI refuses a change under `src/`, `vibemap/` or `tools/` without one.
- 2026-09-18, #63: `vibemap/data/fork_source/` mirrors `src/`, `tools/build.py` and `tools/generated/`, written by `tools/sync_fork_source.py`; run it after any change to what the build reads.
- 2026-09-18, #89: `tools/build.py` writes `game/vibe-map.html` and `game/news.json`, and `--check` covers both.
- 2026-09-19, #114: `tools/regen_tree.py` emits `NOTE_ALIAS` into `tools/generated/tree.js`; a note title in `vibemap/data/campaign.json` is the real topic title, and the game resolves it through `noteId()`.
- 2026-09-19, #128: `docs/site/syllabus.html` and the generated blocks of `docs/SYLLABUS.md` come from `tools/gen_syllabus.py` (`just syllabus`).
- 2026-09-20, #131: `tools/reviewed_sinks.json` is a register, not a generated file: on a conflict keep both sides' lines.

## Data shapes

- 2026-09-18, #89: `game/news.json` is format version 2 (`version`, `fetched_at`, `items`); the feeds are registered in `vibemap/data/sources.json`.
- 2026-09-18, #101: a topic is one TOML file in a pack under `vibemap/data/topics/`, read by `vibemap/topics.py` with unknown keys refused; `tools/new_topic.py` starts one.
- 2026-09-18, #101: a topic's hands-on names a check kind from `KINDS` in `vibemap/artifact_checks.py`, the same kinds an artifact uses, and `run_spec()` runs one spec for any folder; #106 added the kind `module`.
- 2026-09-19, #111: the wearables live in `vibemap/data/items.json` as `wearables`, named once for the game and the terminal.
- 2026-09-18, #62: an item or a seat in `vibemap/data/items.json` is positioned relative to a plot, an annex or the path (`at`), never in world coordinates.
- 2026-09-18, #67: the four islands share one scene, each at its origin in `ISLANDS` in `src/game/20-worlds.js`, with local coordinates per island.
- 2026-09-21, #166: a place is one TOML file under `vibemap/data/places/`, read by `vibemap/places.py`; a topic points at it through `[[origins]]`.

## Game helpers and test seams

- 2026-09-18, #61: every dashboard event goes through `track()`, exposed as `window.track`.
- 2026-09-19, #72: `mergeStatic()`, `win()`, `blobAdd()`, `blobFlush()` and `tintGeo()` in `src/game/10-scene.js` are the scene's shared builders; `CAM`, `EXPOSURE` and `SKY_RIG` in `src/config/00-config.js` hold the numbers. `window.__gfx()`, `window.__scene()` and `window.__minimap()` are the seams.
- 2026-09-19, #120: text that did not come from our own package data goes into HTML through `esc()` and into a link through `safeUrl()`, both in `src/game/00-state.js`.
- 2026-09-20, #131: every injected constant goes through `js_json()` in `tools/build.py`, and `just sinks-check` fails on a new raw value in an HTML template.
- 2026-09-19, #113: `bubble()` is the only way into the speech bubble; `stopCount()` and `finaleStop()` replace the literal 8 and 9; `window.__data()` carries `campaign`.
- 2026-09-19, #114: `vrender()` in `src/game/60-vault.js` is the one gate for opening a note; `window.__vault()` and `window.__finale()` are the seams.
- 2026-09-19, #112: `window.__pet()` reports the companion, and `PETS` is injected by the build from `vibemap/data/pets/`.
- 2026-09-20, #139: `copyText()` in `src/game/00-state.js` is the one copy helper, and `wrapCommands()` puts a copy row after every command block.
- 2026-09-20, #140: `discard()` in `src/game/10-scene.js` frees what a rebuild removes; a geometry, material or texture that outlives a scene is marked with `keep()`.

## The build

- 2026-09-21, #162: the build finds modules by file name, not by a list: two digits, an optional letter, a dash, lowercase words (`MODULE_NAME` in `tools/build.py`). A new module is a new file; a misnamed file stops the build.
- 2026-09-22, #178: `src/game/`, then src/galaxy/ when that folder exists (Galaxy, not on main yet), and boot (`src/game/90-boot.js`) after every folder, because its calls at load read constants the modules declare.

## Working together

- 2026-09-18, #99: `main` is protected with strict required checks, `lint, unit tests, generated files in sync` and `Playwright tests (Chromium and WebKit)`, and the rule binds administrators too. The aggregator job owns the second name, never a shard.
- 2026-09-21, #144: a task for an agent is a work order under `work/orders/`, checked by `tools/work.py`: `just work-check` is what done means, and a review by someone else lands with the code.
- 2026-09-21, #144: a session's report under an order starts with the line `order: <id>`, which is how the stop hook finds the order; a subagent is found by the edits the other hook saw.
- 2026-09-23, #95 comment: Team Claude and Team Codex share the repository. Every issue comment, pull request body and review note opens with a line naming model, effort and role; a team claims an order or issue on #95 before it starts and posts `LANDED` or `released` after; neither team touches the other's worktrees or branches; at most four heavy local jobs run across both teams at once.

## Changed since it was posted on #95

- 2026-09-21, #162: "a new module must be added to `GAME_ORDER` in `tools/build.py`" no longer holds; the list is gone and the file name is the order.
- 2026-09-20, #140: "set `userData.shared` on a geometry reused across rebuilds" became `keep()`.
- 2026-09-21, #146: "an imported stop is clamped to 1..8" became the island's own stop count, `CAMPAIGN[w].ws.length` in the game and `stop_count()` in the CLI.
- 2026-09-21, #152: "add a new browser test file to a shard in the same commit" no longer holds; a file no pattern claims runs in the default shard.
