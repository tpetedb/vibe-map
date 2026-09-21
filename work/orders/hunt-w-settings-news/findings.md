> Cut from the hunt's triage of 2026-09-19. The `Shot:` names refer to that hunt's screenshots, which were not kept: reproduce each finding from its steps on current main before you touch anything, and take your own screenshots into `tests/out/`. Line numbers are from that day and will have moved.

## Batch W: settings, interests, collectibles and the news feed

### W1 (18-4, 20-2) After Live world is off once, turning it back on never refetches - medium, game-ui
Repro: Settings, Live world, Off; open the Roadmap; Live world, On; open the Roadmap again.
Seen: `./news.json` is never requested in that session; the card keeps the items baked in at build
time ("Pulled 2026-09-18") even when the server serves a fresher file. `loadNews()` sets
`newsLoaded=true` before `refreshNews()` returns early on the off branch.
Expected: the refresh runs when the switch goes on, which `tests/test_game_news.py:120` says in a
comment and never asserts. File: `src/game/40-sheet.js:30` with the guard at `:25`.
Shot: `18/07-live-on-roadmap.png`, `20/21-live-on-after-off.png`. Status: present on main.

### W2 (20-4) The empty news card gives a camp two commands it does not have - medium, content
Repro: open the Roadmap in a camp or a forked build whose feed is empty.
Seen: "Run uv run vibe news, then just build"; a camp has no `build` recipe and calls the CLI as
bare `vibe`. Expected: instructions that work where the card is read.
File: `src/game/40-sheet.js:18` against `vibemap/data/template/justfile`. Shot: `20/22-empty-feed.png`.
Status: present on main, unchanged.

### W3 (20-6) A forked game's news card is empty and cannot be filled - medium, cli
Repro: `vibe fork`, `python3 tools/build.py` in the fork, open the Roadmap.
Seen: `game/news.json` is `{"version": 0, "items": []}` and the card tells the owner to run a
command the fork has no data for; `vibemap/data/fork_source/` ships no `data/news.json`.
Expected: the fork builds with a feed, or the card says something a fork owner can act on.
File: `tools/sync_fork_source.py`, `tools/build.py:144-155`,
`vibemap/data/template/_github/workflows/pages.yml:36-44`. Shot: `20/50-fork-empty-news.png`.
Status: present on main; `tools/build.py` changed in #111 but not this fallback.

### W4 (20-5) Collectibles never get the interest dot the docs promise - medium, game-ui
Repro: choose Data and Agents on the title screen, open the Backpack, Inventory, count `.idot`.
Seen: zero; the dot appears on 11 artifacts and 9 mentors and on no item, although every item
carries a `topic` in `items.json`. Expected: `docs/SYLLABUS.md:991` and
`src/game/86-interests.js:8-9` both promise a dot on a collectible.
File: `src/game/18-avatar.js:173`. Shot: `20/32-roadmap-card-chosen.png`.
Status: present on main; `18-avatar.js` changed in #112 for the pet, not here.

### W5 (21-6) The phone hint says "x to sit" and a phone has no way to sit - medium, game-ui
Repro: enter the island at 393x852 with touch, read the hint bar, try to sit on a bench.
Seen: "arrows / WASD - space to jump - x to sit"; three of four name keys a phone has not, and
sitting is bound to a keydown only, while the first sit gates the Field cap.
Expected: a touch path to sit, or a hint that matches the pointer.
File: `src/game/18-avatar.js:194-196`, `:204`, with `src/body.html:24`. Shot: `21/07-joystick.png`.
Status: present on main, unchanged.

### W6 (18-5) An unknown stored setting value is kept silently - low, game-ui
Repro: seed `settings {map:"huge",difficulty:"lunatic",speed:"sprint"}` and open Settings.
Seen: no refusal; `#stage` gets `map-huge` and falls back to the big height while the panel reads
"Compact", `body.dataset.difficulty` is "lunatic" and folds every command while the panel reads
"normal". Expected: an unrecognised value falls back to the default and the panel shows what is in
force (AGENTS.md: versioned formats fail loudly). File: `src/game/85-settings.js:16` and `:35`.
Shot: `18/17-unknown-setting-values.png`. Status: present on main (line 34 to 35).

### W7 (18-6) "Back to the defaults" leaves the shelves it sits under untouched - low, game-ui
Repro: pick the Data chip, set Walking speed to Hurry, click "Back to the defaults".
Seen: every dropdown resets and `S.interests` stays `["data"]`, with the chip lit two rows above
the button. Expected: it clears the shelves too, or says it is about the dropdowns only.
File: `src/game/85-settings.js:45`, panel at `:36`. Shot: `18/16-back-to-defaults.png`.
Status: present on main (44 to 45).

### W8 (18-7) The Full screen button never says it is a toggle - low, game-ui
Repro: click "Full screen", then read the button's label and attributes.
Seen: the label stays "Full screen" and `aria-pressed`, `aria-label` and `title` are all null,
although a second click does exit and it is the only in-page way out.
Expected: the label or `aria-pressed` reports the state.
File: `src/game/85-settings.js:37` and `:43`, second copy at `src/body.html:72`.
Shot: `18/12-fullscreen-settings.png`. Status: present on main (36/42 to 37/43).

### W9 (18-9) Reset progress wipes the Stats history and the verified topics - low, game-ui
Repro: play a little, set a verified topic, then Reset progress twice.
Seen: `{topics:["git-basics"],events:6}` becomes `{topics:[],events:[]}`, while the button says
only "your name and settings stay". The event log is everything the Stats screen draws.
Expected: the copy names what else goes, or the reset keeps the terminal's topics.
File: `src/game/85-settings.js:52-53` (the keep list). Shot: `18/09-reset-armed.png`.
Status: present on main; #112 added `pet` to the keep list, `topics` and `events` still go.

### W10 (18-2) The map size percentages in the dropdown are wrong - low, content
Repro: measure `#stage` for each Map size at 1440x1200 and at 1280x820.
Seen: "Compact (56% of the window)" gives 43 percent and "Big (84%)" gives 91 percent, because
compact is `min(56vh,520px)` and big is the window minus the 104 px talk band.
Expected: labels that match, or labels without a percentage.
File: `src/game/85-settings.js:7` against `src/style.css:36-37`. Shot: `18/02-settings-default.png`.
Status: present on main, unchanged.

### W11 (20-7) Choosing all eleven shelves is not treated as Everything - low, game-ui
Repro: click every shelf chip in Settings.
Seen: the Everything chip stays off, the summary says "The rest stays open, just dimmed" over four
lines although there is no rest, and all 31 mentors and artifacts carry a dot.
Expected: eleven of eleven collapses to Everything, as an empty list does.
File: `src/game/86-interests.js:12`, `:38-43`. Shot: `20/60-all-eleven.png`.
Status: present on main, unchanged.

### W12 (20-8) HTML entities from the feeds reach the vault note as literal text - low, cli
Repro: `vibe news` in a camp, then read `vault/Camp/News.md`.
Seen: "What&#8217;s new" and "release,&#8230;"; `summarise()` strips tags but never unescapes, and
double-encoded feeds survive XML parsing. Expected: the publisher's words, readable.
File: `vibemap/news.py:163`. Shot: none. Status: present on main, unchanged.

### W13 (28-15) A camp is shown package-internal paths and promised an action it has not - low, cli
Repro: in a camp: `vibe news`, read `vault/Camp/News.md`, then `ls .github/workflows`.
Seen: the note names `vibemap/data/sources.json` and promises "A daily action does the same on
GitHub", which only the product repository has. Expected: text a camp reads names paths a camp has.
File: `vibemap/news.py:287-292`. Shot: none. Status: present on main. The two `--help` strings
(`vibe news`, `vibe pet`) that repeat the package path belong to batch Y; fix the note here.

---
