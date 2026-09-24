# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
A branch never edits this file: it adds a fragment under `changelog.d/`, and
`uv run python tools/changelog.py release X.Y.Z` cuts them into a section here.

## [Unreleased]

Nothing here between releases: an entry lives in its own file under
[`changelog.d/`](changelog.d/) until a release assembles them.

## [0.12.0] - 2026-09-24

### Added

- Galaxy, a second way to travel the same course. Settings, Experience, switches between the islands and Galaxy, which follows the history of programming: every topic of the tech tree is a stop on one ordered journey across three globes (the Earth, the data centre and the cloud), each place where a topic happened is a tiny domed miniature, and the next stop is marked and readable from the overview (with Settings, Vault set to Grow and no topic done, the first lesson can stay locked until 0.12.1; Vault set to Full shows it). The islands stay the default, unchanged by the switch, both share one progress, and progress imported from the terminal or a code shows on the route at once. Travelling the world or importing progress keeps the experience you chose, and switching back puts the island camera where it was.
- In Galaxy you land in a place and walk it with the keyboard, the touch stick or a tap on the ground; buildings, water and the shore stop you, and walking up to a pavilion names its lesson, which Open nearby lesson or Enter opens. Where you are follows the lesson you reached, not the last place picked on the map. The whole journey is also a plain list next to the scene, for a keyboard, a screen reader, a short screen or a browser without WebGL, and its names, progress and Learn buttons follow the text size setting without running off a phone.
- Every one of the seventy topics says where it happened: 97 dated origins at 39 places, among them Codd's relational model at IBM San Jose in 1970, the web at CERN in 1990 and Kubernetes announced in San Francisco in 2014, each with the year, the actor, one plain line and a source that was opened and supports all of it. A topic sits at a town only when a dated first-party page puts it there; where no page names a place (a format, a specification, an open-source project, an online announcement) it sits at the internet or a standards body rather than at a guessed office, and the pages behind each origin are listed under the topic's sources so a learner can open the proof.
- `vibe places` lists the places by era with the topics that come from each, `vibe places <id>` shows one of them, and `vibe topic <id>` shows a topic's origins. The data is one file per place under `vibemap/data/places/` and `[[origins]]` on a topic; `vibemap/places.py` refuses what it cannot vouch for, such as an ambiguous year or a duplicate place, and the weekly link check opens the place sources too.
- Photo mode (the Photo button, or P): the HUD steps aside, the camera pulls back one step, and Take photo hands over the drawn frame as a PNG with a caption, to save, or to share where the browser can share files. Opening a panel ends it, and Done gives the focus back to the Photo button.
- The Roadmap's sync card says how many stops live only in this browser, or were delivered since the last export, and the line goes once a code is exported. Stops that arrived in an imported code count as carried. Reset to greenfield says the same before it clears anything.
- After about fifty minutes on screen in one sitting, Rolinda says once, between stops, that this is a good place to stop and where you are. Keep going, Escape or Stop reminding me closes it; a hidden tab, a gap of ten minutes or nobody at the keys earns nothing.
- Walk me there. A stop picked in the search palette (Cmd K, then Walk there or Shift and Enter), a plot tapped on the map or a row in the big map's list of stops sets the walker off for it, and the island says where it is going. The way goes round the hub, the lake and the bays, for a tap on the ground as much as for a stop; a walk that cannot get nearer, to the hub's roof or across a shut bridge, stops and says so, and leaving the island ends it. The Roadmap has no Walk there button yet, and a stop on another island is not walked to.
- The marker where you are walking to stays lit until you arrive, with dashes on the ground that follow the way round, light on dark so they show on grass, snow, sand and lava rock alike.
- An arrow at the edge of the screen points at the next stop with its distance, and at the bridge that has opened once the island is finished. It takes no press of its own, so a tap under it reaches the island, and it is off at the two hardest difficulties. Settings has no row for it yet, so the difficulty is the only switch.
- The map grows with its Bigger button, or a long press on a phone, and every stop is a labelled button under it for a keyboard or a screen reader.
- Hurrying: hold Shift, or push the stick to its rim, to move half again as fast, and "Tap to hurry" in Settings now does what it says. Shift with Tab does not hurry, and changing apps releases held movement keys.
- The island pauses when you look away: a hidden tab or a locked phone stops the ambient clock, so coming back is not an hour of boats, birds and weather in one jump. Battery saver also draws half the frames after a minute with nothing touched and no panel open, back to full rate at the next key, tap or stick; setting it to Keep running turns both off.
- A short buzz on a claim, an achievement and a collectible where the browser has one (Android Chrome; iOS has none), gated by the Buzz setting, silent under reduced motion and never asked for before you have touched the page.
- The Backpack has a Notifications tab: every message the island has shown, newest first, with its time, so what a toast said while you were reading can be read late. Quiet mode raises no toast and keeps the list, at most three cards are on screen at once, a first-time hint shows once, and a quiet "Saved" mark follows a save.

### Changed

- The first lesson no longer tells a beginner to answer yes to a permission prompt they do not understand. Its Definition of done, in the game and in the syllabus, says to pause, read what Claude wants to run or change, and ask Tom before saying yes, and a test checks the learner-facing text it scans for an unguarded instruction to approve a permission prompt.
- `vibe new`, a new camp's agent rules and the Codespaces path say plainly that the camp, the coding-agent subscription and any Codespace bill belong to the learner, and the Codespaces path starts from the learner's own repository.
- The Cycle 3 guide documents the dashboard, the avatar and the archipelago.
- The data-engineering lesson says that keeping Bronze data append-only is this camp's exercise policy; a medallion architecture can also apply change-data capture updates.
- For maintainers: the build reads the game's modules from `src/game/` and `src/galaxy/` by file name, with boot last, and ADR 0001 and `docs/CONFIG.md` say so; the islands sit behind the experience contract of ADR 0015, held by golden pictures in `tests/golden/`; `docs/CONTRACTS.md` lists what other agents depend on; every browser test takes its page from one fixture (a noon clock, a record of every toast, screenshots only under `tests/out`) and a wait that runs out names itself; CI shards stop when the battery cannot be collected and the browser cache follows the Playwright version; `tools/work.py` judges each order on its own branch; one tested command regenerates the whole played camp; and the daily news opens a pull request instead of pushing to main.

### Fixed

- An artifact's yellow ring is drawn at the radius the walk-up test uses, so "walk up to the yellow ring" is true everywhere: the fountain's ring is on the grass, not under the lake, the mountain's is clear of the mountain, and on a finished island a delivered stop's slab no longer cuts one in half.
- The market stall answers a path it does not have with 404 and a body it cannot read with 400, as its demo shows, so the code says which half was wrong.
- The vault links at the foot of an artifact sheet are links: the vault's colour and underline, the yellow focus ring every other control has, and Enter opens the note.
- A second demo button cancels what the first still owed instead of interleaving two transcripts; under reduced motion a demo prints its whole transcript at once and a screen reader hears one line at a time; a line too wide for the panel folds with a hanging indent, and a number such as "1 200 tokens" no longer breaks across two lines on a phone.
- The balloon demo charges the region it rents in: t3.small in `eu-west-1` is 0.0228 USD an hour, and a month of forgetting it is 16.42 USD. The mountain demo names `vibemap/cli.py`, the file the package has, and its columns line up again.
- The "Do it for real" walkthrough and the demo terminal are drawn with ligatures off, so a fork's typeface cannot join `->` or `--` in a line the learner is told to copy exactly.
- An open panel starts and scrolls below the HUD, so a lesson scrolled past the first screen no longer slides behind the bar, and the band it keeps clear grows with the bar on a touch screen.
- An achievement message hangs under the HUD instead of over Stats, Vault, Tree, World, More, the map or the panel's Close button, and moves nothing on its way. A batch of them stacks within the room between the bar and the bottom buttons, newest on top, each takes the whole row (half the lines on a phone) and carries its own surface, so it reads over a panel and over the island alike.
- The panel is announced as a named dialog, opening the More menu on a laptop no longer blanks the numbers beside it, and a group heading that wraps has room between its lines.
- A tech tree shelf outside your interests is set back with its surface rather than dimmed to a fifth of its contrast, so its description reads on a touch screen.
- Achievements earned on a slow-rendering device arrive promptly, and a hidden page and reduced motion are still respected.
- The generated Git and Python topic notes open in the game, and a duplicate note title stops the build and names every file that defines it.
- `vibe scores` treats an existing empty scores file as an empty scoreboard.

## [0.11.0] - 2026-09-21

### Added

- The island can be zoomed. The mouse wheel, a trackpad pinch, two fingers on a phone, the plus and minus keys and a small control on the right edge of the stage all move one camera between three framings: close on the walker, the whole island (the 0 key, or the middle button), and the archipelago with its bridges. A fresh browser now starts close, so the walker, the companion and the name plates read on a phone; the level is kept in Settings, survives a reload, and "Back to the defaults" resets it. Under reduced motion the zoom steps instead of easing, and while the title screen is up the control sits behind the panel and takes no tab stop. The numbers are in the `CAM` block of `src/config/00-config.js`.

- Messages in a bottle. Two bottles lie near the shore of every island; walking over one opens a note with a lesson that really happened while this game was being built (three red tests with one cause, a flaky test that was the birthday problem, a release that got jumped in the queue, a night lost to a spend limit), with a link to the tech tree topic it belongs to. The Backpack keeps the ones you have read. They are not collectibles: no count, badge or progress code knows them. The text lives in `vibemap/data/items.json` under `bottles`.

- In the game, the companion cheers when a stop is claimed, with the happy row every pack already carried. It is a third larger, its pixels are always a whole number of screen pixels so they stay crisp at every zoom, it keeps its colours at noon and takes the moonlight at night, and it no longer gets left behind a stretch of water or jumps onto the walker when a bridge is crossed.

- Every command block in the game has a Copy button: the lessons, the setup guide, an artifact's task and a stop a camp adds. It says "Copied" where you can see it and where a screen reader can hear it, and when the clipboard is missing or refused it selects the command and names the key to press. A command written with `<your_name>` copies with your name in it, shell safe, and says so when there is no name yet.

- A Continue card on the title screen and at the top of the Roadmap: the next open stop of the island you are on, its goal, the one command for it with a Copy button, and a button that opens it.

- The Roadmap says which island you are standing on, how much of it is delivered, and marks the one row to open next.

- The screen stays awake while a panel is open, where the browser has the Screen Wake Lock API. It is released when you close the panel or leave the tab, and taken again when you come back.

- Settings has a text size (Normal, Large, Larger) and a line spacing (Comfortable) with the numbers XAG 101 names: line 1.5, letter 0.12 and word 0.16 times the size. It grows the lesson, the vault note and the title screen and leaves the HUD, the stick and the minimap where your thumb left them. A command block keeps its own tracking, so monospace still lines up.

- A contrast setting: it follows the platform's own high contrast and forced colours by default, and can be insisted on or turned off. It raises the palette's token values only, so black is still the brand.

- A handedness setting: the stick, the jump button and the zoom column swap sides for a left hand or a one-handed grip.

- A quiet setting for the toasts. What a toast would have said is still recorded, so the achievements and the numbers are whole.

- Settings is grouped under five headings, and a row the browser cannot obey (the buzz, the screen wake lock) is not offered at all. Above Normal a row's value takes the whole width, and the control's own size is capped where its longest option still fits the narrowest phone: a select cannot wrap, so the value is either whole or lost.

- The syllabus is published from this repository: `tools/gen_syllabus.py` writes the repetitive blocks of `docs/SYLLABUS.md` (the course map, the mentors, the artifacts, the tech tree) from `vibemap/data/` and renders the whole file into `docs/site/syllabus.html`, which `pages.yml` deploys next to the game as `syllabus.html`. One file, the game's palette, system fonts, a sticky table of contents, print styles, light and dark, and no third-party request. `just syllabus` regenerates it and `--check` fails when it is stale.

- `config/camp.toml` gains `[game] site_url`, where the product is published. The game's Roadmap now resolves "the syllabus" through it, so the link is the neighbour on that site and the product's URL anywhere else. No link to a page in a personal claude.ai account is left, and a repo test keeps it that way.

- The README, the quickstart and a camp's own README say which browsers the game is supported in: Chrome on desktop and on Android is the one it is built and fixed for, an iPhone is best effort because every iPhone browser runs Apple's WebKit, and Firefox and desktop Safari should work without being tested beyond that.

- A link to the game now previews: the page has a description, a canonical address, Open Graph and Twitter card tags, a theme colour and a tab icon that travels inside the one file, so nothing is fetched and no request misses. The Pages workflow publishes the card image next to the game and serves a 404 page in the game's own look with a way home.

- `LICENSE` carries the MIT text in full, so GitHub reads the repository as MIT instead of "Other", and `src/vendor/` now keeps the three.js and Motion licence texts next to the bundles they cover.

- `SECURITY.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, issue forms and a pull request template: how to report something privately, and the house rules an outsider needs before the first pull request.

- The camp `vibe new` writes carries an MIT `LICENSE` with the year filled in and the name filled in when you gave one.

- Work orders for agents: a task under `work/orders/` names the files it may touch and its acceptance as commands, a different agent rules on it in `review.toml`, another team's files need that team's sign-off, and `tools/work.py` checks all of it from the `work-*` recipes, from Claude Code hooks and in CI. Teams by theme live in `work/teams.toml`, goals become launch groups with `just work-plan`, and an order's GitHub issue carries one status comment and a thread agents read only from people who can push. The hooks stay out of a learner's camp.

### Changed

- The documents an agent or a newcomer reads first now match the product. `HANDOVER.md` is gone: it was dated, named the retired `vibe.toml`, sent readers to `vibemap/tech.py` and asked for setup that shipped long ago, and everything in it that still held is in `AGENTS.md`, `docs/MAINTAINERS.md`, `docs/BRIEF.md` and the `develop-camp` skill. The README leads with the live game, a quickstart that was run as written, and what you have to bring yourself: your own machine, your own repository and your own coding-agent subscription. `docs/SKILLS.md` lists every skill that ships (`council` and `justfile` were missing), `docs/DESIGN.md` quotes the tokens that really are in `src/style.css`, and both are now guarded by a test. The camp-facing skills stop naming files only a product checkout has: `install-camp`, `python-data`, `duckdb-sql`, `council` and `camp-progress` describe what a camp can actually run.

- The finale offers slots ("Friday evening", "Saturday afternoon") instead of five 2026 dates and a note to the maintainer, so a camp's configuration and the published game never read as out of date. A camp still writes its own evenings over them.

- A browser shard in CI claims its test files by name or by pattern (`tests/test_game_qol*.py`), and one shard is the default: a browser test file no pattern claims runs there. A new browser test is run from the moment it exists, without an edit to `.github/workflows/ci.yml`, which is what made two branches that each added one collide. `tools/ci_shards.py` expands the matrix the same way for the shard jobs and for the guard, and the guard still refuses a file in no shard or in two, now also a pattern that claims nothing, and prints the whole split when it fails.

- Every picture under `docs/media` is rendered from the product again by `just media` and `just tui-media`, and seven of them are new: the archipelago, the Ask panel, the Stats panel, the Backpack, the Settings rows, the More menu on a phone and a message in a bottle on its shore. A shot whose subject is laid out against the window is taken in a window of that size, so the social card carries the whole title card and the More menu all seven of its rows; the gameplay GIF walks to the 18:00 signpost through the controls a player uses, in a window where the zoom control is not drawn over the minimap; and the `just start` Welcome screen and campaign map come from the app instead of being kept by hand.

### Removed

- The published site no longer serves the learner's untouched `workspace/game/index.html` at `/your-game.html`.

- `interestAnswered()` is gone from the game: nothing called it.

### Fixed

- When the browser takes the WebGL context away (a phone short of memory, a tab that slept), the stage says so and the Roadmap opens, instead of a flat blue stage with a HUD that carried on. The island comes back by itself when the context returns.

- Leaving an island gives its memory back. Every crossing and every fast travel used to leave the old island's geometries, plate textures and shadow map on the GPU, about 170 geometries and a shadow map per switch; so did every mote of dust behind the walker and every change of look.

- Browser zoom and a move to a screen with another pixel ratio resize the drawing buffer, so the island is no longer drawn at half resolution until a reload.

- Reduced motion, from the system or from Settings, now stills the 3D view as well: clouds, birds, boats, planes, the windmill, confetti, dust and every pulse stop, and so does Rolinda's typewriter. The walk, the follow camera and the companion's frames stay.

- Arrow keys and space typed into a text field move the caret and no longer steer the walker.

- Name plates are legible from the whole-island view (they hold a minimum size on screen), a long name gets a wider plate instead of a smaller font, overlapping plates give way to the nearest one instead of being drawn on top of each other, and the signpost of a built stop no longer shows its plate again.

- The plates over Tom and Rolinda carry the roles of the theme, the same ones the speech bubble shows.

- A mentor's plaque now grows into view in the session that imports the code, instead of staying invisible until the island is rebuilt, and it keeps its distance from the mentor at every world scale.

- The sea's highlight no longer shows the mesh as a checkerboard, and the sea reaches past the haze from the farthest zoom.

- A bridge opens the moment the stop that opens it is claimed, and the Difficulty setting gates the bridges wherever it was chosen. A shut bridge carries a sign saying why, and its barrier is taller.

- A bridge deck now meets the shore of the island rather than starting several metres inland, a far deck spans the whole gap instead of half of it, and the bench on the rest platform can be sat on like every other bench.

- Production's lava river, lake and flows read as lava rather than white, and the volcano's glowing crater is the one that is kept.

- The winter island's aurora is in frame at night, and the snowman's carrot nose points forward.

- A look changed mid-stride keeps the walker walking instead of stopping dead.

- The More menu on a phone is one opaque sheet on the bottom edge: no row over another, none off screen, every row at least 44px, the island dimmed behind it, and a tap beside it or Escape closes it.

- The HUD on a narrow window keeps its two rows the same width, collapses the secondary buttons into More below 820px instead of 480px, keeps a long name on one line and stops stretching the name pill across an ultrawide screen.

- The stage is never taller than the window, so the page does not scroll and the speech bubble stays on screen, in landscape and with Map size Tall.

- The movement hint shows the finger half on a touch device and the keyboard half on a mouse, and no longer sits under the stick or the jump button.

- The phone chrome honours the notch and the home bar, gives every control a 44px target, keeps fields at 16px so iOS does not zoom, drops hover styles where nothing hovers, and hides Full screen where the browser has no Fullscreen API.

- The Map button on a phone says whether the map is open.

- Blocked roadmap rows, the vault note reader and the settings options are readable again: AA contrast from the palette surfaces, and no value cut off mid-word.

- The disclosure chevron on a command block keeps its space before the word on a phone, where the summary is laid out as a flex row and the trailing space in the marker collapsed: "vCommands" read as one word.

- The title screen is modal until Start: the HUD, the walk hint and the speech bubble no longer sit half readable under the panel, they take no tab stop and no click, and `c`, `Cmd K` and `Escape` no longer open a panel over the form or claim a stop before the game has begun.

- The name field and Start stay on screen while the setup guide is open, and the sticky row no longer prints over the first line of the text below it.

- Resume is offered only when there is a name to resume with; a saved look on its own used to offer a button that then turned you down.

- Enter in the name field starts the game, "Your own name" keeps a name that was already typed, and a returning player can open the five steps again under "Change your setup", so the play mode can still be changed later.

- The in-game setup guide sends you to Roadmap, Sync for the progress code, which is where Sync is, not to World. It stops offering a clone it never gives, and its `--github` line sits in a command block like every other command, so the flag can no longer break across a line and be retyped as two words.

- A progress code is now checked whole before anything is merged, in the game and in the terminal alike: an island neither side has, a field of the wrong shape, a version that is not a number and a companion with no pixels are each refused by name, and a refused code leaves the camp exactly as it was. `vibe import` answers with that one sentence instead of a Python traceback.

- A saved record in the browser is checked field by field before it becomes state: an island the game does not build, stops that are not numbers and a record that is not an object each cost that field and never the evening. The player is told which part started fresh.

- How many stops an island or an evening has is the campaign's to say everywhere: in a progress code, in `vibe status`, which used to read an `8` typed into the command, and in the progress line of the onboarding menu, which counted a hard-coded 32. A camp that adds a ninth stop can send it, and a code cannot invent one.

- The XP inside a code is no longer added on top of the XP an import awards. XP derives from the log, which is what `vibe undo` hands back.

- A code from a camp nobody named no longer names the player `<your_name>`.

- A code from a newer `vibe` now says the game is the old side and how to rebuild it, instead of asking for another export.

- Importing a progress code names what it merged, so a code carrying only mentors or only artifacts no longer reports "0/8 workstreams", and a code can no longer dress the walker in a wearable the Backpack calls locked.

- Export selects the code in the box, so a browser that refuses the clipboard still leaves one keystroke that works, and the box has an accessible name. The Sync panel names the command a camp really has: `vibe import <code>`.

- The stats panel and the `vibe dashboard` report count the same things: XP follows the difficulty multiplier the terminal uses, inspecting an artifact pays nothing, and a day streak is a day something was delivered in both places.

- Time per stop counts every island instead of the campus alone, and a row is coloured by that island's own stops.

- The panel's feed names screens, islands and shelves instead of printing internal ids, and says "1 event recorded".

- A chosen shelf with nothing on it shows 0 of 0, and a shelf name is no longer cut mid-word.

- Every sparkline states its reading, on the panel and in the report.

- The report survives an empty `workspace/data/scores.csv`, plots stops on its stops sparkline, gives a verified mentor or a built artifact the time its check recorded or no time at all, and names a badge the way `vibe status` names it.

- Every winter and desert stop now names the file or folder its own check opens, so a learner who follows a lesson literally lands where `vibe check` looks instead of going red on work that was really done.

- The production island's stops 1, 2, 7 and 8 now name the paths their checks read. They told you to run `brew bundle dump`, to write "your own ghostty config", to put a comparison "in the vault" and to `mkdir ~/dotfiles`, while the checks looked in `workspace/dotfiles/Brewfile`, `workspace/dotfiles/ghostty/config`, `workspace/dotfiles/zshrc`, `workspace/agents/comparison.md` and `workspace/dotfiles/`, so the work was done and the stop still went red. Stop 7 also asks for two agents other than Claude Code, which is what its check counts.

- The desert's vibe dial sends you to Chris Olah, the mentor who is on that island, and says where Karpathy and Cherny are instead of promising both of them on the sand.

- The desert's deterministic-checks stop points at the script you wrote into `workspace/python/` on Evening 1; a fresh camp never shipped `workspace/python/scores.py`.

- The lighthouse walkthrough asks for `family.name`: `AddressFamily` is an `IntEnum`, so since Python 3.11 printing the member itself gives the bare number and the check's `AF_INET` never appeared.

- The school and market stall walkthroughs run `uv init .` before `uv add`, which needs a `pyproject.toml` a camp does not have.

- The production island's first stop no longer promises DevTools in a stop that does not mention them, and its fork challenge names `gh repo fork tpetedb/vibe-map`: with no argument `gh` forks the camp.

- `docs/SYLLABUS.md` repeats the steps the game shows, word for word, and a test now holds the two together.

- `vibe check --world desert 3` is passable on the documented install. One runner now stands behind every stop that runs tests: the camp's own `uv run pytest` when the camp declares pytest, else the interpreter running `vibe`, else a `pytest` on PATH. A machine with none is told which command installs one instead of being marked wrong, and pytest stays out of the product's runtime dependencies. A file with no test in it is not a test.

- The stops stopped passing on filler. A model family has to be named and not spelled inside `ollama`, a `mermaid` block has to close around a diagram, `workspace/evals/run.py` has to have a body, a hook counts as a gate only when it runs ruff, a formatter or the tests, the reflog has to remember a rewrite as its operation and not in a commit subject, and a branch has to have reached the remote.

- The dotfiles stop no longer breaks `git add -A` in the camp: it asks for a commit inside `workspace/dotfiles` and for the camp to ignore that folder, so nothing hides in a gitlink.

- A check says which half failed: the spec names the sections or the lines it still needs, the strict note check names the missing link, the game check names the byte floor it measures and no longer says "exists" about a file that exists, and the words a note needs are counted inside its dated section.

- A fork manifest of an unknown version, or one that will not parse, is refused with that sentence instead of "check crashed", and a scaffolded mentor exercise can never be part of a pass.

- A claimed stop's note loses the line saying the stop is not done, even when the learner wrote their own words into that same dated section.

- An artifact check reads the frontmatter block a Markdown file opens with, so a brief that starts with a horizontal rule is still a brief, and a correct Dockerfile passes when docker is installed but no daemon answers.

- The vault graph keys on the palette: the cyan, violet and pink `docs/DESIGN.md` bans by name are gone, and the Collector badge reads the same in the terminal as in the game.

- `vibe status` draws the same four marks as the campaign map in `vibe start` (`x` checked, `i` claimed but not verified, `>` next, `.` to do) and prints the legend whenever the grid is drawn, so a forced claim no longer shows an unexplained `i`.

- `vibe check` refuses two named targets (`--mentor`, `--artifact`, `--topic`) instead of running the first and exiting 0, and an empty one of them is refused the way an unknown id is rather than quietly checking campus stop 1.

- `vibe check --fork all` claims the forking stop when the four challenges pass, as the source always promised; one challenge says what it proved and claims nothing, instead of telling everyone their fork builds.

- Raising the difficulty no longer pays out again for a stop a check already verified. A stop claimed in the game or with `--force` is still topped up.

- A hint at beginner and easy is the whole hint; at normal and hard it stops after the first sentence, which is the difference the difficulty table promises.

- `vibe fork --force` says what it is about to delete and asks first.

- `vibe toolbelt --install <unknown>` is one red line, not a traceback, and `--install missing` on a complete tier says so instead of printing nothing.

- `vibe council` convenes the mentors of the island you are on, says who did not fit at the four-seat table, and refuses an empty question before it spends a provider call.

- `vibe explain` escapes what the provider wrote, so an answer containing square brackets no longer dies with a markup error; it diffs from the first commit and says so when the history is shorter than `-n`, and `-n 0` blames the argument rather than the repository.

- `vibe news --limit 0` no longer empties `News.md` and `news.json`, and `--limit -1` is refused instead of being read as a Python slice. `vibe news` rebuilds Tonight, so the note it writes is never an orphan.

- The nightly check "every registered feed answers and parses" stopped calling a quiet feed a dead one. It separates the two facts it used to confuse: a feed is alive when it answers and is still a feed the parser reads, and fresh when it has items today. arXiv announces Sunday to Thursday, so its cs.AI feed is legitimately empty every weekend, and made the night, and the `v0.10.0` tag, red for no product reason.

- Empty stays a fault for every source that does not say it rests. The one digest that rests says so in `vibemap/data/sources.json` with a new optional `rests` that carries the reason and the link, the way `trust` carries provenance; the other twenty keep a back catalogue in the feed, so nothing at all from them is an outage or a format this parser lost. The registry version is unchanged, because the key is optional and an older release reads the same file.

- That check still fails, by name, for a feed that is really dead: a 404 or any other answer the request does not survive, a body that is not XML, XML that is not a feed, a full feed whose entries no longer carry a title and a link this parser can read, and a full feed whose entry element itself was renamed, which counts as no entries at all and used to pass for a quiet day. Every failure line names the feed, the URL and what was wrong, and a feed that is alive with nothing new warns, so a green night still names it.

- `vibe scores` in a camp that has not played yet exits 0 with one line, so `just scores` stops reporting day one as a failed recipe.

- `vibe play`, `vibe dashboard` and the play launcher print the path when the machine has no opener, instead of raising `FileNotFoundError`, and `vibe play --offline` reports a network it cannot reach instead of a urllib traceback.

- `vibe start` says it needs a terminal instead of hanging when stdin is a pipe.

- `vibe pet --all` refuses to be combined with a write, rather than printing the gallery and dropping `--species` on the floor.

- `vibe import` writes the companion chosen in the game into `config/camp.toml`, the way `vibe pet` carries it the other way.

- `vibe new --name` writes your name through a real TOML serialiser and reads the file back, so a quote, a backslash, an accent or a newline no longer leaves a camp whose `config/camp.toml` refuses to parse.

- A very long `--name` is cut to a folder name the filesystem accepts instead of ending in an `OSError`.

- `vibe new --github` says the GitHub CLI is missing before it builds half a camp, instead of raising `FileNotFoundError`.

- `vibe name` refuses an empty name, prints a name that looks like markup without crashing, and says `config/camp.toml` the same way `vibe interests` does.

- A command that writes the configuration refuses when there is no camp at `VIBE_HOME`, instead of scattering a config, a state file and a vault at a typo.

- `vibe config --help` promises only what it has.

- The persona recipes name `workspace/data/examples/`, the folder `vibe persona` actually writes to.

- In a camp, `just done n "note" --force` forwards the flag its own error advises, and `just break` refuses to carry uncommitted work onto the play branch.

- The retired `vibe.toml` is gone from the theme file header, the `vibe start` welcome and `env.example`.

- The onboarding terminal fits a small window: the launcher list scrolls and keeps the focused button in view, the toolbelt keeps its rows at 80x24, and a launcher hint wraps instead of running off the side.

- The welcome screen refuses an empty name instead of storing the placeholder, Enter in the name field is Continue, and a theme of your own stays selected and stays in `config/camp.toml` when you press Continue.

- The Terminal setup rows say "installed" as soon as a module is installed, the campaign map speaks the same grid language as `vibe status`, the Campaign status launcher runs the CLI directly instead of `uv run --no-sync`, and the Obsidian launcher opens the vault folder that `[vault] path` names.

- A tool version in the toolbelt arrives without escape codes, so btop no longer prints `^[[1m1.4.7^[[0m` into the table or under `NO_COLOR`.

- In the terminal, the companion keeps its hat on every idle frame, and `vibe pet` on a terminal without truecolor says why forced pixels look flat and how to get the art.

- `vibemap.__version__` now reads `pyproject.toml` when the package is not installed, instead of a pin that was four releases behind and read as a real release. When neither is there it reports `0+unknown`, which cannot be mistaken for one. An installed copy still reads its metadata, so there is one source for the number and nothing to keep in agreement. The `semver` skill says so too: the old "the number lives in two places" rule would have reintroduced the drift it describes.

- `docs/ROADMAP.md` has its headings back. Every topic was written as `*Basics.* ### Unix and the terminal`, one line, so Markdown rendered the whole thing as a paragraph and the seventy topics of the tree had no headings, no anchors and no way to be linked to. The depth label now opens the body underneath the heading.

- `workspace/python/scores.py` says how to run it from the camp root (`python3 workspace/python/scores.py`), the path every other page uses; the one it printed does not exist anywhere.

- The MCP artifact's sample configuration names the camp's real path instead of one from another machine.

- Work orders: a change that is only staged is a stray like any other, a `git diff` the verdict rests on is an error when it cannot run instead of reading as nothing changed, every list of file names is read with `-z` so a name with a quote or an accent in it arrives whole, and `touched.json` keeps the newest thirty-two agents instead of growing without end.

### Security

- A pasted progress code can no longer put markup on the page. Shelf ids and mentor choices in a code went raw into the Roadmap, Settings and the title screen, so a code from a stranger ran script on import and again on every load. The game now checks every id in a code before it merges anything and refuses a code that fails, naming the field; the panels escape those values on their own as well, along with the dashboard feed and the setup commands.

- The build writes data into the game through one helper, `js_json()`, so a value in `config/camp.toml` that contains a closing script tag is a string again instead of running, and a feed headline containing a comment opener can no longer leave the built game dead. `tools/build.py` also refuses any script that could end its own element.

- `vibe news` leaves no angle bracket in a title, a name or a summary (a tag the feed never closed used to survive), requires a host in a link and encodes the characters that would end a Markdown link or an attribute.

- Notes reach the game character for character: a backslash or `${` in a topic is text. Two CSV notes were showing `\n` as a line break and had lost the backslashes of a quoted command.

- The chat bridge refuses a `Content-Length` that is not a plain number (a negative one held a thread until the peer hung up) and marks its JSON answers `nosniff`.

- New: `docs/SECURITY-MODEL.md`, ADR 0014 on why the game ships no Content-Security-Policy yet, and `just sinks-check`, which fails when a new value reaches HTML without `esc()` (`tools/reviewed_sinks.json` is the register of the ones that were looked at).

## [0.10.0] - 2026-09-19

### Added

- An analytics dashboard, in the game and in the terminal, on one event shape: `{ts, kind, id, world}` with `v` for a number of seconds. The game records into `S.events` through one helper, `track(kind, id, v)` (`src/game/00-state.js`), from the places where something happens: a session start, a stop opened and delivered, an artifact inspected, a mentor met, a mentor verified or an artifact built on import, the time a screen stayed open, and a minute tick while the island is on screen. The log is capped at 600 events and compacts a day of ticks into one before it drops anything, it stays in the browser, and the progress code still carries no events, so an import merges none. The Stats button on the HUD opens the panel (`src/game/89-dashboard.js`): six KPI tiles with sparklines, a ring per island, XP over time, a day-by-hour heatmap, bars for the time per stop, the path you took and a feed of recent events, all inline SVG, all derived from the state, working from 393px up.

- The avatar can do things. The walker sits down on the x key, on a bench or a chair where one is in reach and on the spot where it is not, and an original low-poly clamshell laptop in aluminium grey with a lit screen opens on the lap while the hands type; walking, jumping or pressing x again stands the walker back up. The twelve mentors work at their spot on their own chair, Rolinda serves, and Tom and the walker cheer when a stop is claimed. Forty collectibles, ten to an island, sit along the paths and on the annexes that appear: walking over one picks it up with a small burst and a line that explains one concept in a sentence and links to its topic in the tech tree. Twelve achievements, six of them the badges `vibe status` hands out, unlock with a toast and open six wearables (two hats, glasses, a jacket, a backpack and a lanyard) that show on the walker, in the look picker on the title screen and in the terminal. A Backpack panel in the HUD holds the inventory, the achievements and the wardrobe. Seats and collectibles come from `vibemap/data/items.json`, positioned against a plot, an annex or the path of their island rather than as world coordinates, so a new island layout carries them along; the new `src/game/18-avatar.js` and `src/game/19-items.js` hold the logic and the island builder, the frame loop and the character builder only call into them. The progress code carries `items`, `ach` and `wear` additively inside version 2, so an older game or an older `vibe` ignores the keys and keeps working.

- A cat and a dog, and a gallery of every pet option. Both are real pixel sprites with all four states, vendored from two CC0 packs by [Shepardskin](https://opengameart.org/users/shepardskin) on OpenGameArt ([Cat Sprites](https://opengameart.org/content/cat-sprites), [Dog Sprites](https://opengameart.org/content/dog-sprites)) whose pages state the licence; the CC0 legal code sits next to the frames and `vibemap/data/pets/CREDITS.md` quotes the terms with the author, the URL and the date. vscode-pets' own cat (its author asked it not be redistributed) and dog (CC BY-ND, and packing frames makes a derivative) stay out. `tools/sync_pets.py --packs <folder>` reads the packs, keys out the flat background colour they paint instead of transparency, cuts the cat's sheet into its rows and stands every frame on the bottom edge of one canvas; `--check` covers the new sets too. The dog joins the species list as a choice, never a roll, with ASCII art of its own, so `vibe pet --species dog` works in any terminal and `[pet] species` in `config/camp.toml` now lists twenty. A claimed stop makes the creature cheer: `vibe check` and `vibe done` play the happy state through once. `tools/tui_media.py --pets` renders `docs/media/pets/<species>.png` and `.gif` for all six pixel species and the contact sheet `docs/media/pets.png` from real terminal output, and README.md and `docs/ABOUT.md` have a Pets section with the images and the credits.

- The changelog is assembled, not edited. A change adds one small file under `changelog.d/` named `<slug>.<type>.md`, with the type one of the six Keep a Changelog headings, and `CHANGELOG.md` is written only by a release: `just changelog` prints the Unreleased view, `just release X.Y.Z` cuts the dated section, moves the compare links and deletes the fragments. `tools/changelog.py check --base origin/main` runs in CI's lint job and refuses a pull request that changes `src/`, `vibemap/` or `tools/` without an entry, or that edits `CHANGELOG.md` outside a release. Two branches can no longer conflict over the same three lines, which is what they did on every merge.

- `just sync-main` catches a branch up with `main` in one command: it merges `origin/main`, resolves a conflict in a generated output by taking either side and running the generators in dependency order (tree, cookbook, template, build, fork mirror, pets check, vault), stops and names the file when a real source conflict is left, and then runs the fast gates. A new `.gitattributes` marks the same outputs `merge=binary`, so a built game never gets conflict markers written through it, and `linguist-generated=true`, so a review reads the source change instead of the output. Both are things git and GitHub do in a fresh clone; a custom merge driver would need `git config` in every clone and is deliberately not used. `docs/MAINTAINERS.md` has the policy, and the finding that a merge queue is not available for a repository owned by a personal account.

- **Choose what you want to learn.** The eleven shelves of the tech tree are now a choice. The title screen asks after the difficulty ("What do you want to learn?") with a chip per shelf, an Everything chip and the preset your persona would pick (the data engineer: data, terminal and shell, git, agents; the teacher educator: agents, docs, knowledge); Settings changes it later, and `vibe interests`, `vibe interests set data,shell,agents` and `vibe interests all` do the same in the terminal. The choice lives in `config/camp.toml` under `[learner] interests`, is refused loudly when it names a shelf that does not exist, and travels in the progress code additively inside version 2, where it is a set: a code adds a shelf and never removes one. Nothing is hidden or locked by a choice and the thirty-two stops stay the spine for everyone; what changes is the order things are offered in. The tree and the command palette put chosen shelves first and dim the rest, the Roadmap gains a "What you want to learn" card with where to start, grow mode opens the basics of chosen shelves from the first evening, an artifact, a mentor or a collectible on a chosen shelf gets a small coloured dot, the dashboard counts what was found per chosen shelf, and `vibe status` prints the shelves and the next suggested topic (`vibemap/interests.py`, `src/game/86-interests.js`).

- `.github/CODEOWNERS` in the product, naming the generated folders so a review request that points at one means a generator was skipped, and a commented teaching example in the camp template.

- A command palette over everything the game holds. **Cmd K** or **Ctrl K**, and the Search button in the HUD, open one box that searches the stops of the island you are on, every vault note, every tech-tree topic, the twelve mentors, the twenty-one artifacts and the forty collectibles; the arrow keys move, Enter opens the stop, the note, the topic, the mentor or the artifact, Escape closes. The index is derived from the same data the panels render, so a new note or a new artifact is in it without a second list to maintain (`src/game/41-search.js`).

- **The data engineering pack**, sixteen topics in `vibemap/data/topics/data-engineering/`, written from each project's own documentation and read as one path: the formats data arrives in (CSV to RFC 4180, JSON Lines, Parquet, Arrow, schemas and schema evolution), the engines and table formats it rests in (DuckDB beyond the basics, Iceberg with Delta Lake alongside it), ingestion (dlt, Kafka concepts), transformation (Polars, dbt), orchestration (Airflow, Dagster and Prefect), quality (data contracts and dbt tests), and the two maps that tie it together (the medallion layering, and ingestion versus transformation versus orchestration). Every hands-on runs on a laptop with uv, with no account and no paid service, and every one was run before it landed: the folder built, the commands run, the check confirmed green on the result and red on an empty folder. Where a tool was too heavy for twenty minutes the topic says so with the measurement instead of pretending, so Airflow's exercise parses a DAG with the real library rather than starting `airflow standalone`, and Kafka is concepts only because both its and Redpanda's documented local runs need Docker and gigabytes.

- What GitHub Pro pays for, in the repository and in every camp. `.devcontainer/devcontainer.json` opens this checkout in Codespaces or any dev container: the `mcr.microsoft.com/devcontainers/python:1-3.12-bookworm` image, the `github-cli` dev container feature, and `.devcontainer/setup.sh` for uv, just, duckdb, `uv sync` and the Playwright browsers. The camp template carries its own under `_devcontainer/` (the underscore becomes a dot, like `_github`): the same four tools and the installed `vibe`, with no browsers, because a camp has no test battery. Both install from official installers rather than Homebrew, and both do the slow work in `onCreateCommand`, which is what a Codespaces prebuild replays. Port 8000 is labelled for the game and 7717 for the chat bridge. `docs/QUICKSTART.md` has it as Path D.

- An installed `vibe` carries the game's source, so `vibe fork` works in a camp from `vibe new` with no clone and no network. `vibemap/data/fork_source/` mirrors `src/`, `tools/build.py` and the generated inputs the build reads; `tools/sync_fork_source.py` writes it and `--check` fails when it drifts, the way the camp template already works, and a test holds the line. `--from` still takes a checkout, and a product checkout still forks from its own working tree. `tools/build.py` in a fork hands the run to the interpreter behind the `vibe` on PATH when the package is missing, so `just build` and `just record` work in a camp built by a plain `python3`. The fresh-camp end-to-end run forks and checks it, where a missing file in the wheel is the only way it can fail.

- In-game chat, answered by the learner's own Claude, Codex, Gemini, Copilot or OpenCode subscription. The **Ask** button in the HUD and the **C** key open a panel with a context chip (the island, the stop whose sheet is open, the mentor or artifact in view), suggested questions for that context, a streamed answer and a history kept in the saved state. `vibe chat serve --pair <code>` runs the bridge that answers it: `127.0.0.1` only, one `POST /ask` endpoint that takes a question and never a command, the pairing code the panel shows as the shared secret, an Origin allowlist, a 16 KiB body cap, a queue of one and a timeout that kills the provider process. The prompt is built on the Python side from the course data, so the page sends identifiers rather than text to run, and the question is an argument, never a shell string. `vibe chat ask "..."` asks the same question with the same prompt in the terminal. With no bridge the panel explains how to start one in three lines, with the exact command and code in it, and answers by searching the notes and stops embedded in the game file. `docs/CHAT.md` and `docs/adr/0009-local-chat-bridge.md`.

- A `justfile` skill in `.agents/skills/justfile/`, synced into the camp template: when a recipe earns its place, how to name it, that the doc comment is the interface, that a secret never goes in a justfile, and the contract with an agent.

- A module on justfiles, written from the [just manual](https://just.systems/man/en/) with every claim cited. A roadmap topic, **Justfiles and task running** (the shell shelf, working knowledge), covers what a recipe is and why a command runner is not a build system, the default recipe, doc comments and `just --list`, parameters with defaults and variadic `+` and `*`, dependencies, variables, `export` and `set dotenv-load`, shebang recipes, the `[group]`, `[private]`, `[confirm]` and `[no-cd]` attributes, `import` and `mod`, `just --choose` with fzf, `just --fmt --check`, `just --dump --dump-format json`, `just -n` and `just --completions`. The second half is the agent half: why a justfile is the narrowest useful contract between a person and a coding agent, with `AGENTS.md` listing recipes instead of incantations, the hook and the CI job calling the same recipe, `[confirm]` on the destructive ones, and the single allow rule `Bash(just *)` in Claude Code, whose wildcard-after-the-program shape comes from the [permissions page](https://code.claude.com/docs/en/permissions). This repository's own `justfile` and `agents.just` are the worked example.

- A live world feed: real organisations, projects and people, by name. `vibemap/data/sources.json` is a registry of twenty-one verified feeds, each with a kind (organisation, person, project), the display name, the feed URL, the publisher, the reason it is trusted, the building it belongs to and shelf tags from the tech tree: Apple Developer News, the Microsoft developer blogs, kernel.org and LWN, Python Insider and CPython releases, Markus Winand on modern-sql.com and Use The Index, Luke!, DuckDB, the GitHub changelog, and release feeds for just, uv, ruff, three.js, Claude Code and Codex alongside the AI feeds the news card already carried. `vibemap/news.py` reads the registry, gives every item a stable id, its source, the name shown, a kind (release or post), shelf tags and a one-sentence summary taken from the feed's own description with the markup stripped, then dedupes, caps per source and sorts newest first. Nothing is generated: every line is a headline or the publisher's own words with the link next to it, and `docs/adr/0010-real-names-and-live-content.md` records the guardrails. The news action runs daily instead of weekly, and a nightly job checks that every registered feed still answers.

- An off switch for all of it: `config/camp.toml` `[news] live` sets the default and a **Live world** dropdown in Settings (on, off, or from the config) overrides it. Off hides every element marked `live-feed`, the News card first, and stops the fetch.

- A `module` check kind in `vibemap/artifact_checks.py`: `script` for an exercise whose library is nobody's dependency. It names the imports it needs and the command that installs them, runs the script when they are there, and says what to install when they are not, so a learner without `dbt` on this machine is told rather than marked wrong. The floor still reads the file either way. Topics and artifacts share it, as they share every other kind.

- The hosted game refreshes its feed at runtime. `tools/build.py` writes `game/news.json` next to the built game and the Pages workflow publishes it beside the page, so the game fetches `./news.json` from its own origin with a cache-buster and never a third party. `news.json` carries a format version, and a file of a shape the build does not know is refused rather than half read. From a `file://` game nothing is fetched at all and the baked copy is the feed; a refusal or a failure is silent and leaves the baked copy in place.

- One archipelago. The four islands now stand in the same scene, on the corners of a square, joined by long plank bridges with railings, lamps and a rest platform with a bench at the middle. Every coordinate in `WORLDS` stays local to its island and only the island origins move (`ISLANDS` and `BRIDGE_CHAIN` in `src/game/20-worlds.js`, `ISLAND_GAP`, `BRIDGE_W` and `BRIDGE_REST_R` in `src/config/00-config.js`), so the active island is still built at the origin and the camera, `onLandW`, the items, the artifacts and the mentors carry on unchanged. A bridge deck is ground: it is walkable, tap to walk aims at it, and walking past its middle switches the active island with no reload, the walker carried into the new island's coordinates while the HUD, the roadmap, the sky mood, the items, the mentors and the plaques rebuild for the new world and the island behind drops to a silhouette. A bridge opens when the island before it has its first stop done, and always on beginner; a shut one shows a barrier and does not carry you. The World button stays fast travel and flies the camera over the water before it builds (a cut under reduced motion). A minimap under the HUD (`src/game/32-minimap.js`) draws the four islands, the bridges open or shut, the walker and the next stop; on a phone it waits behind a Map button.

- `docs/RESEARCH/2026-09-18-ownership-costs-providers.md`: who pays for what, template versus fork, and what each of the five coding harnesses can do. Every claim carries the sentence from the first-party page it came from, with the URL and the date. It answers four questions the course needs settled: which GitHub products can put a cost on the repository owner (Actions is free on public repositories, a codespace is billed to the account that owns it, prebuilds and Git LFS bandwidth are the two that bill the owner, Pages overage throttles rather than bills) and how each one is closed; why the template beats a fork for a camp (a fork of a public repository cannot be made private, and a camp holds the learner's own notes); a capability matrix of Claude Code, Codex CLI, Gemini CLI, Copilot CLI and OpenCode against the chat bridge, `explain`, `council`, skills, hooks, subagents, MCP and scheduled headless runs, as a table and as JSON `vibemap/providers.py` could load; and the free route for a learner with no subscription (the game, the checks, the vault, Gemini CLI on a personal Google account, Copilot Free, or OpenCode against a local Ollama model). Where a vendor's documentation is silent the report says so rather than filling the gap.

- A real pixel pet in the terminal. The crab, the duck, the turtle and the snail are animated sprites, painted two pixels to a cell with half blocks (U+2580, foreground over background) so a transparent pixel shows the terminal's own background: eight frames a second in the `just start` launch screen and under `vibe pet --watch`, a still frame next to `vibe status`, and four states (idle, walk, happy, sleep) with the walk chosen by the stroll rather than stored. The frames are vendored from [vscode-pets](https://github.com/tonybaloney/vscode-pets) (MIT, Anthony Shaw), drawn by Marc Duiker, enkeefe and Kennet Shin; only art that project licenses as MIT was taken, the sets with their own itch.io terms were left behind, and the licence, the author, the source URL and the commit travel with the pixels in `vibemap/data/pets/`. `tools/sync_pets.py` packs the GIFs into a palette with run-length rows and has a `--check` mode a test runs, so Pillow stays a dev dependency and an installed `vibe` needs nothing new. Every other species keeps the claude-buddy ASCII art, and so does any terminal without truecolor or with `NO_COLOR` set; `[pet] style` in `config/camp.toml` (`auto`, `pixel`, `ascii`, also `vibe pet --style`) decides for good. `tools/tui_media.py` renders `docs/media/tui-pet.png` and `tui-pet.gif` from the real onboarding screens.

- A pixel companion in the browser game, the hosted one included. The six vendored sets the terminal paints (cat, crab, dog, duck, snail, turtle) are injected into the game by the build, so there is one source of pixels and nothing is redrawn: a billboard sprite with nearest-neighbour filtering follows the walker across the islands and over the bridges, idles, walks and sits down when he does, keeps to the land, never takes a click, and costs two draw calls against a phone budget of 300. Pick one in the onboarding or under Settings, Companion, with a preview that walks while you choose; the artists and licences are named there exactly as `vibemap/data/pets/CREDITS.md` names them. The choice is `S.pet`, it travels in the progress code both ways (version 2 stays 2, an id this game has no pixels for is refused by name), and `config/camp.toml` `[pet]` decides what a published build ships with. Reduced motion keeps the companion and takes the bobbing away.

- **The switchboard**, a twenty-first artifact, on the campus beside the fourth plot with a prop of its own (`src/game/17b-switchboard.js`, so the shared builders stay untouched). Five terminal demos: reading the labels with `just --list`, a parameter with a default, a dependency that runs first, handing the board to an agent with one allow rule, and a `[confirm]` guard on the switch that cuts the power. Its Do it for real task is a `workspace/artifacts/switchboard/justfile` with three recipes, every one documented, one with a parameter and one with a dependency. The new `justfile` check kind in `vibemap/artifact_checks.py` reads it as data with `just --dump --dump-format json` when just is on PATH, and with a tolerant line parser when it is not, saying which layer answered and how to install just.

- **The tech tree is data.** Every topic is its own file, `vibemap/data/topics/<pack>/<id>.toml`, inside a pack with a `pack.toml` that gives it a title, a blurb, the shelf it mostly lives on, maintainer notes and the reading order; `tree.toml` holds the ages, the eleven shelves and the three depths. `vibemap/topics.py` is the schema (pydantic: id, title, age, shelf, depth, summary, an optional agent-facing half, history, try it, sources with a url and a date of check, unlocks, prerequisites, minutes, and a hands-on with a workspace folder and a check spec that reuses the kinds in `vibemap/artifact_checks.py`) and the loader, which refuses a duplicate id, an unknown shelf, age or depth, a link to a topic that does not exist, a file whose name is not its id and any key it does not know, always naming the file. `vibemap/tech.py` keeps the shape the generators read, so `tools/regen_tree.py` writes byte-identical output before and after the move; that was the acceptance test. TOML over JSON because a topic is long prose full of quotes and backticks and a literal string needs no escaping, and `tomllib` reads it with no new dependency (`docs/adr/0013-topics-as-data.md`).
- `vibe topics` lists the packs and what is in them, `vibe topic <id>` prints one the way the vault note reads it, `vibe topic <id> --start` scaffolds its hands-on folder, and `vibe check --topic <id>` runs that hands-on with the same exit-code contract as the other checks: 0 when it passes, 1 when it does not. A pass records the topic, and the progress code carries the topics that are done as `topics`, added inside version 2 and merged as a set, so a topic read on one machine is news on the other and never a correction.
- `tools/new_topic.py` scaffolds a topic file, or a whole pack, with the keys in the right order, today as the date of check and TODO markers where the author has to read the official documentation and write; it adds the new id to the pack's reading order. `docs/TOPICS.md` is how to write one, the content rule and the review checklist, and `tests/test_topics.py` holds every rule an author can break by hand.

- `vibe artifact`: the artifact walkthroughs in the terminal, with the parity the mentors already had. `vibe artifact` lists the twenty-one with their island, their task and whether they were built for real; `vibe artifact <id>` prints what the artifact sheet in the game prints (the concept, the documentation page it was written from, the numbered steps, the commands, the definition of done and the check that verifies it); `vibe artifact <id> --start` scaffolds `workspace/artifacts/<id>/` with an honest TODO stub for the file the task names and a `notes.md`, never overwriting work that is already there. A task whose files come from its own commands (`uv init`, `git`) gets no stub and says so.

- `vibe dashboard` writes `workspace/dashboard.html` from `.vibe/state.json`, the vault and `workspace/data/scores.csv` and opens it (`--no-open` to skip, `--out` to place it elsewhere, `--json` to print the numbers instead). It is one self-contained file with no script and no network, in the same design as the game panel: the tokens come from `vibemap/palette.py` (`css_tokens()`), and a test keeps them equal to the game's `:root` in `src/style.css`.

- `vibe new --github OWNER/NAME --private` creates the camp's repository private instead of public. The camp README, the Pages workflow and `docs/MAINTAINERS.md` say what a private repository costs: Pages, protected branches and code owners need GitHub Pro or above, and on GitHub Free the repository has to be public.

### Changed

- Resizing the window reframes the island at once instead of gliding. The camera's distance comes from the viewport's aspect ratio, and easing that meant a second of drift after the window had already stopped changing; a new fit is a new window, not movement in the world, so only the walk is eased now. The same holds for going full screen, changing the map size and arriving on a wider island. It also takes the browser test off a wait for forty drawn frames per viewport, which on a throttled runner is the difference between twenty seconds and two.

- CI runs on Linux, and the browser battery runs in four shards. Both required job names are unchanged. `browser-shard` is a matrix of `smoke`, `ui`, `bridges`, `panels` and `webkit`, cut along measured per-file durations; the required context `Playwright tests (Chromium and WebKit)` is a separate aggregator that needs it, runs under `if: always()` so a skipped job can never leave the check pending, and goes green only when the matrix result is success and every shard left a receipt (`tools/ci_shards.py`, which reads the split back out of the workflow so the matrix is the one place it is written down). A test fails when a browser test file is in no shard or in two. Both required jobs moved from `macos-latest` to `ubuntu-latest`, keeping their names, and the nightly play-through moved with them. A Pro account may run forty concurrent standard jobs but only five on macOS, so two macOS jobs per push filled that pool after three pushes and pull requests waited on a queue rather than on tests. A `concurrency` group per ref now cancels a superseded pull-request run and never cancels `main` or a tag, `push` is limited to `main` and to tags so a commit is not tested twice, `astral-sh/setup-uv` caches the environment and `actions/cache` keeps the Playwright browsers under the resolved Playwright version. macOS is still tested where it matters: a `macos-smoke` job on release tags installs the wheel and runs `vibe new` and the fresh-camp end-to-end, plus anything marked `macos`.

- The HUD has a hierarchy and an overflow menu. Roadmap and Search stay in the pill; Backpack, Ask, Stats, Vault, Tree and World are the secondary row, which sits in the pill on a wide screen and drops into the **More** menu on a phone; Settings is tertiary and lives in the menu at every width. It is one set of buttons in one place in the markup, so a new button is one more line in `#hud-sec` and needs no layout work. The KPI row is the HUD's own last line instead of a hand-measured offset, so it follows however the pills wrap. The HUD stays above the sheet, which is what keeps Ask and Search working while a stop is open, and the name pill and the stop dots step aside while it is.

- A stop imported from the game is honest about what it is: `vibe import` still awards half the XP and now says so in plain words and names the `vibe check` that pays the rest, `vibe status` marks it `i` instead of `x`, and the first passing check tops it up to full, the same way it tops up a `--force` claim. ADR 0004 records the decision.

- The island is framed, lit and shaded. The camera no longer sits at a fixed distance: it derives one from the island's radius and the viewport's aspect ratio (`camFitDist` in `src/game/21-world-build.js`, the numbers in `CAM` in `src/config/00-config.js`), so the diorama fits the frame on a wide desktop window, a square one and a phone instead of being cropped on all three, and the follow is eased in time rather than per frame, capped so the island never leaves the frame, and runs a little ahead of the walk. The renderer tone maps with ACES and writes sRGB at a tuned exposure. The sky is a dome with a vertical ramp from the world's horizon colour to the stage's zenith, with the sun or the moon riding the same stage, and the whole light rig moves with it: the bearing, height, colour and intensity of the key light, the hemisphere pair and the ambient, one row per stage in `SKY_RIG`. A night is lit like a night now, carried by the path lamps, the lit windows of the finished buildings, the inn, the lighthouse and the laptop screen on a sitting walker's face. The sea is one mesh animated on the GPU, with a shallow band and a foam line at the coast and a scrolling highlight, which also takes the old per-frame vertex loop off the main thread. Land blobs carry vertex colours for a darker cliff band, everything that stands on the ground gets an instanced contact-shadow decal that survives the shadows setting being off, name plates are drawn at twice the resolution with a dark stroke and only near the walker, the production island's lava is emissive and pulses, and a ring under the walker says which of the three figures is yours.

- The `linked` badge counts only wikilinks the learner wrote. The generated vault satisfied it from day one, so it fired on whatever the learner happened to do next. Every note vibe generates whole now carries the hash of the body it was given, and the lint report counts own links separately.

- Static island props are merged. Trees, rocks, cacti and ice floes are collected while the island is built and flushed into one instanced mesh per shape and colour (`batchAdd` and `batchFlush` in `src/game/10-scene.js`), which pays for the archipelago and leaves the phone with more room than before: on the WebKit iPhone profile a fresh campus went from 282 draw calls to 271 and a fresh winter from 286 to 260, with the three silhouettes and the bridges already in the scene. The fog and the camera reach across the water so a neighbouring island reads as a silhouette in the haze rather than a wall of sky.

- Everything static on an island is baked into one mesh. The land and its satellites, a finished building and its windows, an annex with its causeway, the props, the clouds and the walkers themselves are merged at build time into a single geometry that carries the colours as vertex colours (`mergeStatic` in `src/game/10-scene.js`); only what the animation loop holds, a sprite, a light or an instanced mesh keeps its own node, and the fourteen path lamps became two instanced meshes. On the WebKit iPhone profile a finished campus went from 333 draw calls to 208 and a finished winter from 325 to 227, a fresh campus from 282 to 179, so an island with all eight stops built is inside the budget of 300 for the first time. `tests/test_game_graphics.py` holds that line, along with the framing at four aspect ratios, the colour pipeline and the light rig.

- The scene and the speech bubble fill the window: the stage takes the height the talk band does not, so the black letterbox under the island at 1440x900 is gone. The hint line carries its own backing pill instead of light grey on bright grass, and the joystick and the jump button are hidden on a fine pointer, where the ground, the arrow keys and WASD already do the work.

- The in-game Settings screen names `config/camp.toml`, which is the file a camp really has, and no longer tells a slim camp to run `just build`; the same stale reference is gone from the news line, the setup guide, the vault and the finale.

- The sheet is a real overlay: one panel, its own scroll container, the page behind it never moves, and the row that closes a lesson (Mark as done, and the way back) sticks to the bottom of that container. The reading column is framed rather than floating on black, and the Close button sits with the text instead of eight hundred pixels away from it.

- On the title screen the name field travels with the Start button in the sticky row, so the field the copy points at cannot be below the fold while the button that needs it is on screen.

- The vault graph labels the hubs first and drops a label that would land on one already drawn, so a dense patch reads instead of turning into a smear.

- `vibe check` exits 1 when any check failed and 0 when they all passed, for workstreams, mentors, artifacts and the fork challenges; `--no-claim` changes what is recorded, never the exit code. The course's own gate can now be a step in a hook or a workflow, which is what it teaches.

- Workstream 2's demo asks both change requests of the same card, which is what makes them comparable: the precise one changes the badge it named and nothing else, the vague one changes everything it was not told to leave alone.

### Fixed

- The artifact sheet says what its number counts ("3 of 21 artifacts found") instead of reading as an index.

- `main` is protected on GitHub: pull requests only, both CI jobs green and up to date, no force pushes or deletion, enforced for admins; release tags are immutable; merged branches are deleted automatically; secret scanning with push protection and Dependabot security updates are on. `docs/MAINTAINERS.md` and `AGENTS.md` say so.

- The browser tests no longer measure a panel while it is still moving. The sheet opens with a spring that lifts it in from 16px below, and the stillness helper sampled on a timer alone, so on a loaded runner, where the spring advances only when a frame is drawn, five samples of the same stale number read as settled and the sticky action bar was measured 16px below the window. `sheet_in_place()` now waits for the sheet's transform to reach identity, which is the page's own end of the spring, before anything samples geometry; stillness only counts a sample once the page has painted again; and `GamePage.until()` waits for a condition rather than a sampled value, so the sticky bar test waits for the bar's bottom edge to be the window's and the dashboard test waits for the focus move instead of reading it right after the open. No product change: the sheet is `position:fixed;inset:0`, so the bar cannot really sit below the window.

- `vibe check` no longer passes a workstream on the files the camp shipped.
  Stop 2 wants an `AGENTS.md` and a skill you wrote, stop 6 counts the notes
  and wikilinks you added rather than the whole vault, and stop 7 wants a
  Pages workflow of your own or a site that answers.
- Stop 5 accepts an MCP server added in the default local scope, which is
  where `claude mcp add` writes it, and stop 8 accepts a launchd agent, the
  route the lesson teaches.
- The desert gates stopped taking an empty deliverable: a CI workflow counts
  when a step runs the checks, a job when the script has a job in it, and a
  dot entry when a line explains it. Winter 8 reports a missing folder as a
  missing folder.
- `vibe check --fork repair` reads the history of the camp around the fork,
  which is where the fork's commits live, and `vibe check --fork ""` is
  refused the way an unknown challenge is.
- A fork's `just build` refuses to write JavaScript the browser cannot read,
  and it runs on an older `python3` again instead of stopping on `tomllib`.
- An imported stop's vault note says it was imported instead of still saying
  it is not done; a stub names the command that checks its own stop; and a
  `links:` line you wrote counts as yours.
- `vibe status` names a wearable the way the game does, the three mentor
  surfaces use one word per state, and `vibe mentor <id> <choice> --start`
  scaffolds as well as records.
- The artifact checks match a keyword in any case, say when only the spacing
  of an expected line differs, treat a `[private]` recipe as private with or
  without `just` on PATH, and the walkthrough states the note that hard asks
  for before you build.

- The Copy buttons say what happened. A refused or missing clipboard now selects the text and says "Selected, press Cmd C" instead of failing silently, in the workstream 1 prompt and in the finale message.

- Committing an empty release note in workstream 4 answers with a reason instead of doing nothing.

- The export message names the camp, not the repo, and no longer cuts the command with an ellipsis; it says the code is on the clipboard when it is.

- A reload restores exactly the islands you played: the saved record no longer
  carries the active island's stops under a second name, so the campus stops
  being handed another island's progress.
- A stop a camp adds to an island opens and can be claimed, instead of the
  island reporting itself complete at the ninth stop.
- A delivered stop shows one way back, and its primary button is never a
  second copy of the secondary's label.
- The end of an island is written for that island: the campus ends at the hub,
  production ends the campaign.
- The bubble takes both speakers' roles from the theme, cancels the line that
  was typing before it writes a new one, and is replaced when you change island.
- The Roadmap says met for a mentor you have talked to, whatever you chose.
- At a strict difficulty the mentor card also promises the note that
  `vibe check --mentor` checks there.
- Enter opens the stop you are standing on, as the copy has always said.
- The proximity button says "Talk to the OpenCode team" rather than
  "Talk to team", a locked signpost says what opens it, the inn's terrace
  offers the finale at eight of eight, and the Streak tile counts the stops
  done today instead of a percentage.

- The minimap test waits for a painted map rather than for three frames. The map is drawn on its own throttle, so a fast frame loop could pass the wait with the canvas still blank; opening the map now also paints it on the next frame instead of waiting the throttle out.

- The go-live pairing block is a sentence. The items carry commas of their own, so they are separated by semicolons with an "and" before the last, instead of being joined into an unparseable list.

- The thirty-two "Open" buttons in the Roadmap and the "Go" buttons under the campaign carry an `aria-label` naming their row, so a screen reader hears the mentor or the artifact rather than "Open" thirty-two times.

- Strict checks no longer print a Python exception at the learner. The workstream 1 game check, the workstream 2 `AGENTS.md` check, the DuckDB `top_runs.sql` check and the strict vault-note check all guard their reads and answer with the same plain sentence as the lenient row above them.

- The sitting test waits for a toast that was raised, not for one that is still on screen. A toast removes itself after a few seconds, so looking for the element raced with the machine being slow; the toast stack counts what it has raised and the test waits on that.

- The vault opens the note a link names. An artifact's "In the vault" links
  pointed at eight titles no note carried, which threw and landed you on
  Tonight; a title the vault does not know now says so instead of throwing.
- Grow mode unlocks every campus stop. Stops 4 to 8 carry the theme's own
  names, so claiming them unlocked nothing.
- One lock rule for the whole vault: a locked note shows the same card from a
  wikilink, the graph or the tech tree, and the tech tree no longer renders a
  locked note in full.
- Wikilinks are links: focusable, and Enter or Space opens them. The graph
  canvas carries a label.
- The graph settles where it settles and the view is fitted to it, so a large
  vault no longer piles into a row along the top and bottom edge. Labels are
  drawn at a readable size whatever the zoom, and one that cannot be placed is
  dropped.
- A two-tag line renders as tags, a mentor's role as emphasis, and the vault
  header says what is on screen after you switch to the tech tree.
- The finale takes a date with an apostrophe or a tag in it: config text is
  data, not code. The start time is added only to an entry that is a date, the
  closing follows the camp's pairing instead of always talking about wine, and
  one release reads as one release.

- The vault graph does not play its settling animation when the machine asks
  for reduced motion. The layout is already final when the vault opens, so the
  drift was animation for its own sake.

- Sitting down with `x` sticks. Typing your name schedules a rebuild of the walker a moment after the last keystroke, so that it carries the finished name on its plate; on a fast machine that rebuild landed after the game had started and after you had sat down, and the new body came up standing with the laptop gone, because the rebuild carried only the position and the rotation over. The pose is state, so the new body takes it over, and its limbs are put where the pose says in the same tick. The same rule also decided standing up from the speed the frame started with, so `x` pressed with the speed of the last step still in the legs, which is how you sit down on a bench you just walked to, unlocked the achievement and left you standing. It reads the speed the frame ends with, and a sit sets that to zero.

### Security

- The news card shows a feed item as text: a title, a name or a summary
  carrying markup is read literally instead of becoming elements, and a link
  that is not an absolute http or https URL is shown without an anchor. Feed
  content travels from public RSS sources into the hosted game, so this was
  stored script injection for every player of a published camp.
- `vibe news` writes plain text: titles, names and summaries are unescaped,
  stripped of markup and capped, and an item whose link is not http or https
  is dropped. The daily workflow therefore cannot put markup in `news.json`.
- Answers from the chat bridge, an imported progress code's player name and
  the release notes of workstream 4 go through the same one escaper, which
  now also escapes quotes, so a value cannot break out of an attribute.
- The game asks nothing of a third party: the Google Fonts stylesheet is gone
  and the type is the system stack the device already has, so "no CDN, works
  offline" is true of the page and of every report the CLI generates.

## [0.9.0] - 2026-09-17

### Added

- Three configuration levels, nested, each flat inside, with `docs/CONFIG.md` as the table of "to change X, edit Y" for both a camp and the product. The repository level stays where the tools demand it; the source level is `src/config/` for the game (world scale, island radius, palette) and `vibemap/data/` for the CLI; the journey level moves from `vibe.toml` to `config/camp.toml` (name, persona, difficulty, provider, theme, vault mode, finale dates). `vibe new` writes `config/camp.toml`, and this checkout has one too so it stays a valid camp.

- `vibe fork` copies `src/`, its vendor files, `tools/build.py` and the generated inputs into `workspace/forks/vibe-map/`, with a `justfile`, a `README.md` with the challenges and a versioned `fork.json`; `just build` there produces the learner's own game file. `vibe check --fork` verifies that the fork exists, that its `src/config/` is no longer the product's and that it builds. A fork is the learner's copy to break and repair; the course keeps living in the product.

- A deterministic check on every stop of winter, desert and production where a deliverable exists, with the note check as the floor underneath all of them. The check reads what is on disk and every hint names the exact path: a backprop reproduction in `workspace/winter/backprop/`, a mermaid transformer in `workspace/winter/transformer.md`, a recorded local model run in `workspace/winter/local-model.md`, makemore and its samples in `workspace/winter/makemore/`, both ends of the vibe dial in `AGENTS.md`, six dot entries explained in `workspace/desert/dotfiles.md`, the learner's own pytest green under `workspace/`, a hook in `.claude/settings.json` that gates rather than bookkeeps, a spec with sections in `workspace/specs/`, a workflow under `.github/workflows/` that parses and runs ruff or pytest, a job with two recorded runs in `workspace/jobs/`, five eval cases in `workspace/evals/`, a Brewfile, a ghostty config and a zshrc in `workspace/dotfiles/`, a GitHub remote with a second branch, a reflog that remembers a rebase or a revert, a permissions allow list, two agents compared in `workspace/agents/comparison.md`, and `workspace/dotfiles/` as a git repository with `install.sh` and a README. The four winter stops that are genuinely reading only say so in the check name.

- A new production stop, Fork the game, with four challenges checked one at a time by `vibe check --fork <challenge>`: `exists` (the fork is there and was made by `vibe fork`), `config` (its `src/config/` differs from the product's and it still builds), `topic` (a stop or a tree node of the learner's own in the fork's generated data) and `repair` (a build that failed and then passed, from `repair.json` that `just record` writes in the fork, or from the fork's git history). The challenges print and claim under that stop's heading rather than a production 0, and the fork now carries `tools/record_build.py` and a `just record` task.

- Mentor encounters. Each of the twelve mentors now has a dialogue of three or four exchanges in the game, walked one question at a time, where every line is a paraphrase of something that person is on record saying, with the link it came from next to it. Each encounter sets one exercise of under fifteen minutes in `workspace/mentors/<id>/` and `vibe check --mentor <id>` (or `--all`) verifies it without a network: Karpathy's bigram model must print the likeliest character after "a", Torvalds's script must produce the same blob hash as `git hash-object`, Hinton's twenty steps of gradient descent must land on the target, Sutton's brute-force search must beat the rule you invented, and the note-shaped exercises (Cherny's CLAUDE.md rule with the command that proves it, Wu's spec-plan-todo, LeCun's what mattered against what you could throw away, Li's ten labelled rows, Amodei's falsifiable forecast, Olah's mermaid circuit, Hashimoto's one readable config file, opencode's one prompt across two providers) must hold the sections the exercise asks for. A verified encounter is worth half a workstream in XP, turns the mentor's ring green and raises a plaque on their spot with their one line on it, writes the encounter and the exercise into their vault note, and earns the `mentored` badge when all twelve are done. The progress code carries the verified mentors inside version 2, so an older game or an older `vibe` ignores the key and keeps working.

- Artifacts became tasks. Each of the twenty artifacts on the islands keeps its demo and gains a "Do it for real" section written from the official documentation of the thing it stands for, with the page it came from linked on the sheet: `http.server` for the cafe, `functools.lru_cache` for the fountain, `sqlite3` for the well, `socket` for the lighthouse, the Docker "Writing a Dockerfile" page for the dock, the GitHub Actions events reference for the windmill, the AWS On-Demand Instances page for the balloon, `platform` for the mountain, FastAPI's First Steps for the market stall, the MCP build-a-server quickstart for the bridge, the DuckDB Python API for the factory, `queue` for the post office, uv's Working on projects for the shop, the git `gitignore` reference for the bank, `concurrent.futures` for the data centre, the Claude API rate limits page for the energy grid, `collections.Counter` for the library, the Claude Code subagents page for the office, `csv` for the households and scikit-learn's `train_test_split` for the school. Every task is under twenty minutes, lives in `workspace/artifacts/<id>/`, and the commands it gives are the ones its documentation gives, behind the same Commands disclosure the lessons use.

- `vibe check --artifact <id>` (or `--all`) verifies what was actually built, deterministically and offline: a Dockerfile whose instructions all parse and, when Docker is installed, an image that builds; a DuckDB pipeline whose gold table has rows; a FastAPI app its own test client gets 200 from; a workflow file that parses and carries a schedule trigger and a job with steps; an MCP config that lists a server with a command; a SQLite file with an indexed table that holds rows; a queue script whose output shows two deliveries, one retry and one dead letter in that order; a subagent file with valid frontmatter; and eleven more. A check that wants a tool this machine does not have says so, with the install command, instead of failing. The checks live in `vibemap/artifact_checks.py`, one function per kind, named from the `real` block in `vibemap/data/campaign.json`.

- The progress code carries an `artifactsBuilt` list, added inside version 2 so an older game or an older `vibe` ignores the key and keeps working. An artifact built for real is worth half a workstream in XP, reads "built for real" on the sheet and in the Artifacts vault note, and earns the new `builder` badge when all twenty are done.

- A fresh-camp end-to-end run: `tools/fresh_camp.py` installs nothing, starts the `vibe` process a learner installs, makes a camp with `vibe new`, proves that workstream 1, workstream 3 and a winter note check all refuse on an empty camp, scripts the two campus deliverables, proves the checks then pass, exports the progress code and imports it into a second camp. It runs nightly against `uv tool install .`, and `tests/test_fresh_camp.py` runs the same journey against the checkout.

- A `nightly` workflow for everything marked `integration`: the fresh-camp run and the full play-through, on a nightly schedule, on every `v*` tag and on demand. `ci` keeps the pull-request loop fast.

- A `browser` marker, applied automatically to any test that takes a browser fixture, so CI can split the battery without anyone labelling a new test by hand. Tests that read the workflows back assert the split holds.

- Three architecture decision records for the cycle: `0006-config-levels.md` (three nested levels, why `config/camp.toml` replaced `vibe.toml` and why the product checkout is also a camp), `0007-artifacts-as-tasks.md` (why a demo alone earns no XP, why every walkthrough is written from the official documentation of the thing, why the check is deterministic and offline) and `0008-mentor-encounters.md` (why a paraphrase with its source and never an invented quote, why an exercise is under fifteen minutes, why a verified encounter is worth half a workstream). All three explain why the progress code stayed at version 2 and gained keys inside it.

- `tools/script_camp.py`, one home for the deliverables a learner would have built: the stop deliverables of winter, desert and production, the twenty artifact fixtures, the twelve mentor exercises and the four fork challenges. `tests/test_stops.py` and `tests/test_artifact_tasks.py` read their scripted set from it instead of carrying their own, and the nightly regeneration of the played instance uses it to script a camp before it plays. It is safe to run in a camp that already has history and a remote: it adds nothing that is there, overwrites nothing the learner wrote, and leaves the repository on the branch it found it on.

- `vibe mentor` lists the twelve mentors with their island and whether the encounter is verified, `vibe mentor <id>` prints the exercise, its steps and the check that reads it, and `vibe mentor <id> --start` scaffolds `workspace/mentors/<id>/` with a stub of the file and a `notes.md`. The scaffold never makes the check pass, and an existing file is kept, not overwritten.

- The camp's Pages workflow publishes the learner's fork at `/fork/` when they have built and committed one.

### Changed

- The title screen puts the form first. The four steps, the name box and the Go row sit directly under the title and the campaign stats; the framing paragraph, the roles and the full brief moved below the Go button, and step 3 carries an honest prerequisites line (a terminal, about fifteen minutes, a GitHub account, a paid plan for Claude, Codex or Gemini). The Go and Resume buttons, the word for a stop in the HUD, the four KPI labels and the second line of the tagline are theme strings now: the studio preset says Start, Stops, Progress, Streak, Connections and Found, and the wine-night preset keeps Kick off the engagement, OKRs, Velocity and Synergy. A theme in `themes/<name>.toml` needs the five new keys, and an old file is refused with the missing names.

- The mini-games were audited against what they teach; the decision and the reasoning are in `docs/adr/0005-mini-games.md`. The mascot generator and the roll ledger are gone, along with `S.mascot` and `S.rolls`. Workstream 1 now builds the prompt you paste into Claude Code from your three sentences, workstream 2 runs a vague and a precise change request against the same component without a mascot in sight, and workstream 3 renames a column and shows the binder error DuckDB really prints. The release ledger, the connectors and the note graph are kept; opening workstream 6 now draws the graph, which only the playthrough tool used to do.

- The production island's stop 6 is Fork the game; Claude in Chrome, which was a two-click install with nothing to check, is folded into stop 5 (Claude Code, the power settings) as the browser surface, with its sources. The island still lays out eight plots, so nothing in the game, the progress code or the badges had to learn a ninth. Every stop on the three later islands gained a "Checked by" line in `docs/SYLLABUS.md` saying what the check reads.

- `tools/build.py` concatenates `src/config/*.js` before the game modules and resolves every input relative to the folder that holds it, or to `--root DIR`, so a fork builds on its own. `WORLD_SCALE`, the island radius and the palette moved out of the game modules into `src/config/00-config.js`.

- CI runs the whole battery. It used to run three unit files and three browser files, which left ten test files (artifacts, reset, grow, onboarding, notes, obsidian, pet, project, news, dotfiles) running nowhere but a maintainer's laptop. The WebKit file is now its own step with one rerun of what failed, which tells a lost WebGL context apart from a real defect, and the pytest command no longer passes a second `-q` that was swallowing the summary of failures.

- `vibe status` counts the encounters next to the artifacts (`K/12 mentors met`), and `status --json` carries `mentors`, `artifacts` and `artifacts_built` for the scripts that read it. The onboarding terminal shows the same three numbers, and the grow-mode hint follows the state: after every artifact is found it asks for one built for real, then for a mentor's exercise.

- The mentor screen in the game says each thing once. The summary list of ideas was a second telling of the dialogue, which now carries every idea with the link it was paraphrased from; the list stays in the mentor's vault note.

- The docs are finalised against the merged layout: `docs/CONFIG.md` gained the fork challenges, `repair.json` and the mentor workspace; `docs/MAINTAINERS.md` says how an artifact check and a mentor encounter travel to a learner; `docs/QUICKSTART.md` and `docs/LONG-GAME.md` carry the three new checks and the fork; `docs/SYLLABUS.md` describes an encounter and a Do it for real task; `docs/BRIEF.md` maps the professionalize cycle to the pull requests that delivered it and rewrites its gaps honestly; and the camp README tells a learner what the island asks them to build. A fork is a learner feature and never our development workflow: work on the product happens in the product.

### Deprecated

- `vibe.toml` at a camp root is still read, and still marks a camp, for one release. Every command says so in one line and points at `config/camp.toml`.

### Removed

- `tools/split_game.py`, the one-shot that cut the 2026-09-16 monolith into `src/` by line number. `src/` has been the source since, and the script read a file that no longer has those lines.

### Fixed

- The browser tests wait for signals the page produces instead of for a wall clock: the walker's own frame counter (a new read-only seam next to `window.__debug()`), the demo scripts behind the artifact terminal (`window.__demos()`), a settle helper for a spring or a smooth scroll, and the state, note or message a click actually produces. Every `wait_for_timeout` is gone from `tests/` and from `tools/play.py`. The fixed waits were hiding a failure: the game falls back to the roadmap list when the 3D scene will not start, and a test that waited 600 ms carried on regardless. It now fails loudly, which is how a seeded record with an out-of-range stop number was found.

## [0.8.0] - 2026-09-17

### Changed

- The docs separate a camp from the product repository. `docs/LONG-GAME.md` and `docs/QUICKSTART.md` no longer promise `just setup --check`, a `.venv`, Playwright browsers, `just verify` or `just build` to a learner in a camp, the "Where things end up" table labels every row camp or product, and the troubleshooting tables say what a camp does instead. The camp README leads with the next command and what you get, then a zones table written for the learner (your work in `workspace/`, notes in `vault/`, the rest is settings), says `just` needs `brew install just` and that every recipe also runs as `vibe <thing>`, moves `just scores` out of the day-one list, and tells the learner that the regenerated `vault/Camp` notes belong in git; the camp AGENTS.md says the same. Every code block now installs with `uv tool install git+https://github.com/tpetedb/vibe-map`, with the PyPI form as a footnote. Two dead sources are fixed: the Git 2.9.0 release notes (`.adoc`) and the dotfiles placeholder, now the GitHub dotfiles guide.

### Fixed

- A play-through of the browser game in Chromium and on an iPhone-sized WebKit turned up nineteen defects; all of them are fixed. A signpost now wins over an artifact when both are in range, and the mountain's detection radius no longer reaches over the Business Continuity plot, so stop 4 can be entered by walking. An empty name is refused at the title screen instead of starting the evening as `<your_name>`: the placeholder is never written to the saved state, and the HUD and the walker's label show the chosen character until a name is typed. The walker's label is rebuilt when the name changes and shrinks to fit its plate. A name with a quote or an accent is handled: the setup guide single-quotes it for the shell, and the camp directory folds accents (`Jorg` and the accented spelling get the same folder). `?reset` in the URL now runs after the saved record is read, so it no longer loses the name, the look, the play mode and the settings. Full screen is asked for on the document rather than on the stage, so the sheet and the vault stay visible. Escape closes the sheet and the vault, and opening either focuses its close button. A theme that does not pair wine gets its own pairing line from the theme data, and a theme with no pairings loses the blocks altogether. On a phone the title box is opaque, covers the HUD and keeps its primary button in view; the full-experience guide renders below that button. Resume is offered to anyone who has been here before, not only after a stop is done. The vault graph keeps its labels on the canvas and drops the labels of small nodes when zoomed out; the tech tree says it scrolls sideways and has buttons for it; "Open in Obsidian" becomes "Vault on GitHub" when the game is not served from a file. Workstreams 7 and 8 have real command blocks that fold with the difficulty. A progress code whose version is not 2 is refused with a clear message. Stale paths and counts: `workspace/python/scores.py`, `workspace/data/scores.csv`, `vault/Camp/Scores.md`, eight workstreams rather than six, and workstream 3 now teaches the schema the check reads (`played_at,player,score,duration_s`) at the path it reads it from.
- A stop on winter, desert or production is green only when the learner wrote the note: the check ignores everything vibe writes into it (the stub, the claim bullets, the campaign sources) and asks for a dated section of their own, forty of their own words and two links beyond the generated ones; the strict check asks for a source they added. A claim now replaces the stub section instead of contradicting it, and a second entry on the same day joins that heading. `vibe undo <n>` un-claims a stop, hands the XP back and drops the claim from the note, and `vibe done --force` on a finished stop says so and changes nothing. `vibe scores` says there are no scores yet instead of raising, in both forms. Generated vault notes carry a hash of what vibe wrote, so a rebuild, a switch to grow mode and back never overwrite a note the learner edited, and the library never overwrites a camp note. One name: the state follows `vibe.toml` while it holds the placeholder, and `vibe name` writes both and rebuilds the vault. Skills are counted once in workstream 2, the hint keeps its `[[links]]` and names the file as it is spelled on disk, `vibe vault build` counts the folder, `vibe status` congratulates a finished campaign and points at the next island, expert and god run pytest without colour, `vibe theme` and the docs separate the camp from the product, `vibe news --help` names both files, the toolbelt reads Obsidian as installed, and two dead links (git RelNotes, the dotfiles placeholder) are real links again. In the onboarding terminal, Play goes through the same path as `vibe play`, the news button runs `vibe news` only, and the tests button is greyed in a camp with one line saying why.
- The game no longer crashes on the Roadmap, a stop or the inn prompt when WebGL failed before the island set a world; a progress reset keeps the chosen character and play mode; the setup guide escapes the name. Expert and god difficulty work in a camp: expert runs the learner's `workspace/**/test_*.py`, god adds the vault lint (the product keeps its own gates). `vibe news` in a camp writes `.vibe/news.json` instead of a fourth top-level folder. `vibe new --name` also sets the learner's name in `vibe.toml`. `vibe new` reports when git could not commit (and refuses `--github` without a commit), survives a package without the skills tree, prints the real path, and copies the template inside the package-resources context. Remaining `data/`, `sql/` and `python/` mentions moved to `workspace/` in AGENTS.md, CLAUDE.md, two skills, the personas, the cookbook, two game notes and the vault; `env.example` names `VIBE_NAME` and is synced into the template.

## [0.7.0] - 2026-09-17

### Changed

- Three zones, separated: the learner's own work now lives in `workspace/` (`workspace/game/index.html`, `workspace/data/scores.csv`, `workspace/sql/`, `workspace/python/`), the checks, the scorekeeper, the backup hook, the Pages workflow, the lessons and the skills follow; `vibe new` writes a slim camp from a template shipped inside the package (README, AGENTS.md, CLAUDE.md, vibe.toml, justfile, the learner skills, the hook and subagent, a Pages workflow, an empty workspace), builds the vault and makes the first commit, instead of cloning the whole engine; `vibe play` opens the hosted game outside the product repository, `--offline` caches a copy. `docs/MAINTAINERS.md` explains the layout and how a change travels; `tools/sync_template.py` keeps the template's skills, hook and subagent equal to the product's, with a test.
- `<your_name>` is the default name everywhere Lotte used to be one: the state file, vibe.toml, the game's title screen and the terminal onboarding show the placeholder and say to type your name plainly, without the angle brackets. Lotte remains a character you can pick.

### Added

- Two roadmap topics with sources: Separation of concerns (Dijkstra's EWD 447, Parnas 1972, Conway 1968, Ousterhout, Twelve-Factor config, Team Topologies) and Building the builder (Engelbart's bootstrapping, Brooks's No Silver Bullet, Grove's leverage, AGENTS.md, Claude Code memory), both pointing at the camp's own layout as the worked example.

## [0.6.0] - 2026-09-17

### Added

- A much bigger map. One constant, `WORLD_SCALE` (1.6), is applied once at load to every coordinate the game uses (land, plots, path, river, lake, bridge, prop positions, mentors, artifacts), while buildings and walkers keep their size; walking speed, the camera, the fog and the sky distances scale with it so the feel stays the same, and the inn stays at the origin. Every stop now has its own path: a spur leaves the ring at the plot and runs outward over a causeway to an annex, a small land blob with a flag that carries the stop's hour. An annex is hidden until its stop is done and pops in with the building's confetti when the stop is claimed (or imported), so the level grows as you play; annexes of done stops are there on load. Two new pictures, `docs/media/island-campus-start.png` and `island-campus-expanded.png`, come from `tools/campus_shots.py`.
- Onboarding in the game: the title screen is a four-step form on a first visit. Who you are (Lotte, Frank, Max, Rolinda, or your own name; each preset is a different walker), how hard (beginner to god, changeable later under Settings), how you want to play (just the game, or the full experience: a setup guide with the exact commands for the terminal, the camp folder and Obsidian, plus the export and import loop that keeps the two in sync), go. Returning players get the resume button first.
- Commands fold by difficulty: every command block in a lesson is a `Commands` disclosure, open at beginner, easy and normal, folded at hard, expert and god, always one click away. The setup guide's commands are always open.
- Setup guide screen from the Roadmap, and `vibe name` to set your name in the terminal.
- A naming convention for local camps, `vibe-map-<name>-<YYYY-MM-DD>`: `vibe new` without a directory uses it (`--name` picks the person part, else the login), and the setup guide suggests it with your name and today's date.
- Three roadmap topics on the agents shelf: Prompting (task, goal, hard constraints, context, definition of done), Structure (XML tags for the model, Markdown blocks for the reader, fenced code for anything copied) and The symbols (what `/`, `!`, `@`, `#`, `[[ ]]`, `---` and backticks mean to Claude Code, CLAUDE.md, Markdown and Obsidian), all sourced to the Anthropic and Claude Code docs.
- Reset progress: a two-click button on the Roadmap and in Settings takes the game back to the start of the roadmap (every stop undone, artifacts and mentor choices cleared, name and settings kept), and `?reset` on the URL does the same for the hosted game: https://tpetedb.github.io/vibe-map/?reset

## [0.5.0] - 2026-09-17

### Added

- Ten more artifacts, spread over the four islands, each with its own small procedural building (`src/game/17-artifact-props.js`) that the walker goes round: the factory (a data pipeline: raw, bronze, silver, gold; a failed run that reruns cleanly; batch versus stream) and the post office (queues and pub/sub: a letter delivered later, at-least-once delivery, a dead-letter shelf) on the campus; the shop (a package registry: `uv add` as buying, the lockfile as the receipt, a yanked version) and the bank (secrets and auth: a token is a key, `.env` is the safe, a leaked key revoked and rotated) in the sandbox; the data centre (an inference request's path, latency by region, a cold start, batch versus interactive), the energy grid (tokens as watts, a rate limit as a fuse, autoscaling, a budget alarm) and the library (RAG: a question becomes a vector, the nearest shelves, a citation, a stale index) in cold storage; the office (planner, worker, reviewer, `AGENTS.md` as the handbook, a review gate that rejects, subagents as departments), the households (users and privacy: data minimisation, anonymisation, a GDPR request) and the school (train and test split, overfitting caught by the test, a benchmark) in production. The roadmap card, the README and the tests count twenty; the play-through inspects the artifacts of every island.
- Settings in the game (the HUD's Settings button): map size (compact, big, the whole window), a full-screen button, vault mode, pairings, shadows, motion, walking speed; persisted with the progress, applied at once. The map is bigger by default (84 percent of the window).
- `vibe news`: six AI feeds (OpenAI news, Hugging Face blog, Simon Willison, Claude Code releases, the GitHub changelog, arXiv cs.AI; `[news] feeds` in `vibe.toml`) into `data/news.json` and the vault note News; the news is embedded into the game at build time and shown on the Roadmap; a weekly `news` GitHub Action pulls, rebuilds and commits so a forked repo and its hosted game stay current. Standard library only.
- `docs/LONG-GAME.md`: the command-by-command setup for playing over weeks with the terminal, the game and Obsidian side by side, and `just camp` to open all three.
- Grow mode for the vault: `vibe vault mode grow` keeps every note in `vault/_library` (excluded from Obsidian's graph and search) and unlocks notes into the camp as the campaign earns them (a stop's notes and their links, an artifact's notes, a mentor, the Obsidian feature notes when the vault stop is done, `vibe vault unlock` by hand). Tonight reports what is here and what is waiting; the in-game vault applies the same rules (`?vault=grow` previews it) so the graph grows as you play; `vibe vault mode full` restores everything; a Vault choice on the onboarding screen; `vibemap/grow.py`, three tests and a Playwright test.
- `docs/ECOSYSTEM.md` lists claude-obsidian (AgriciDaniel, MIT), the Claude Code skill set for wiki-style vaults, with `just obsidian-plugin` to fetch it and the one-line `claude --plugin-dir` to use it on this vault.

## [0.4.1] - 2026-09-17

### Fixed

- `vibe --version` reported 0.3.0 after the 0.4.0 release: the version string was pinned in `vibemap/__init__.py`. It now comes from the installed package metadata, with a test that it matches `pyproject.toml`.

## [0.4.0] - 2026-09-17

### Changed

- The tech tree is grouped by shelf (terminal and shell; version control and GitHub; config and formats; languages and code; data; web, networks and APIs; ship and run; agents and the harness; docs and versioning; knowledge and Obsidian; what is coming), each topic with a depth (basics, working knowledge, deep), instead of ages with career ranks. The game's tree view, the vault's Tech tree note, the generated topic notes (tag per shelf), the Obsidian graph groups (one colour per shelf) and `docs/ROADMAP.md` follow. The ages remain only as the player's XP ladder (Intern to Expert).

### Added

- Ten artifacts on the campus island, each a prop you walk up to and inspect: the cafe (client, server, protocol: 200, 404, 429, 503), the fountain (a cache), the well (a database: scan, index, transaction), the lighthouse (DNS), the dock (containers: build, push, run), the windmill (cron and hooks), the balloon (the cloud and its meter), the mountain (the stack in six layers), the market stall (an API and its docs) and the bridge (MCP). Each prints a terminal-style demo per button, ends with a question from Rolinda and links the vault notes. Found artifacts turn green, count in the HUD, travel in the progress code (`artifacts`), appear in the vault note Artifacts and earn the Collector badge; the play-through visits all ten.
- Terminal setup modules from Tom's toolbox (MIT): `vibe dotfiles` lists, shows and installs zsh (completion dropdown, history suggestions, palette highlighting, fzf, a tmux picker), tmux (the bottom bar, j/k/i/l panes), Ghostty (the R2-D2 high-contrast theme), Starship (the prompt), AeroSpace (tiling) and the R2-D2 Obsidian theme into the vault; backups for anything that differs, one source line in `~/.zshrc`, `--dry-run`, `--brew`; a Terminal setup screen in `just start`.
- Three tech nodes: Git hooks (pre-commit to pre-push, `core.hooksPath`, pre-commit and lefthook), Agent hooks (Claude Code's events, scopes, matchers and exit codes, with this repo's own hook as the example) and Interfaces (GUI, TUI, CLI, API, MCP and ACP, with sourced history from Unix to ACP).
- Obsidian feature modules: `vibe vault feature <id>` and `--all` bootstrap one note per feature the official help documents (thirty-five: links, backlinks, graph view, tags, properties, callouts, embeds, templates, daily notes, unique notes, bookmarks, search, quick switcher, command palette, hotkeys, slash commands, workspaces, outline, note composer, slides, canvas, bases, web viewer, Obsidian URI, Obsidian CLI, community plugins, CSS snippets, Sync, Publish, Web Clipper, Obsidian Flavored Markdown, file recovery, page preview, random note, footnotes) with the exact commands, the syntax and a five-minute try, plus working example files (a JSON Canvas, a base, a template, a deck, a CSS snippet, a daily template). The facts live in `vibemap/data/obsidian.json`, extracted from obsidianmd/obsidian-help; `docs/OBSIDIAN.md` is generated from it by `just tree`.

## [0.3.0] - 2026-09-17

### Added

- The `vibe` package: a click CLI (`uv run vibe`) with status, check, done, map, vault, export, import, scores, council, explain, init, play, start, persona, theme, toolbelt, provider, difficulty, mode and mentor, and rich output in the house palette.
- Quests that verify real work: `vibe check N` inspects the repo and awards XP, `vibe done --force` claims at half XP, levels mirror the ages of the tech tree, badges (ADR 0004).
- Versioned pydantic state, migrated on load, and config in `vibe.toml` with unknown keys refused; personas, themes, a toolbelt report, model providers, the council of mentors, and a Textual onboarding screen (`just start`).
- The vault builder with lint, a committed vault baseline of 96 notes, and the Obsidian vault pre-configured: graph colour groups by tag, a dark base in the house palette, note templates, `docs/VAULT.md`.
- The Python toolchain: a uv project with `pyproject.toml`, a `justfile` with agent recipes, style and link checks in `tools/checks.py` (ADR 0003).
- Browser tests with Playwright: seven Chromium smoke tests and a WebKit iPhone battery (tap, joystick, sheet scroll, HUD width, WebGL draw budget); pytest tests for the CLI (state migration, the progress code version gate, quests, vault build and lint, scores through polars and DuckDB).
- `src/`: the game split into source files with a concatenating build, `tools/build.py --check` to catch hand edits, and `vibemap/data/campaign.json` as the one source for game and CLI (ADR 0001).
- The tech tree fact-checked: every history claim cited to a primary source (137 sources), new nodes for .env, zsh, YAML and TOML, and now Semantic Versioning, changelogs, ADRs and the README.
- Docs: `docs/AOE-STUDY.md` (ADR 0002), `docs/DESIGN.md`, `docs/ECOSYSTEM.md`, `docs/SKILLS.md`, `docs/COOKBOOK.md` generated from the personas, `docs/adr/` with four decision records, and this changelog.
- Skills: `council` for agents; `semver`, `changelog`, `adr` and `readme-quickstart` for the documentation habits; vendored `webapp-testing` (Apache-2.0) and `verification-before-completion` (MIT).
- An installable CLI: `uv tool install vibe-map` puts `vibe` on the PATH; it finds the camp from any subfolder (`vibe.toml`, or `VIBE_HOME`), ships the campaign, the tech tree and the resources as package data (`vibemap/data/`, `vibemap/tech.py`), and `vibe new [dir] [--github OWNER/NAME]` clones the template or creates a repo from it.
- Lucide icons (ISC) on the HUD, the enter pill, the sheet, the roadmap rows and the vault toolbar (`src/game/05-icons.js`, `iconize()` for static markup).
- The vault graph runs on d3-force (ISC): a simulation that cools and stops, pan by dragging, zoom with the wheel, labels only on hubs and the selection, an Open in Obsidian button that deep-links to the real vault (`obsidian://open`) or to the vault folder on GitHub when hosted.
- A terminal pet: `vibe pet` (show, animate, configure, gallery), a strolling companion on the launch screen of `just start`, a `[pet]` table in `vibe.toml`. Sprites and the deterministic roll ported from claude-buddy (MIT), plus a crab of our own.
- `docs/QUICKSTART.md` (three paths in, numbered, with what you should see) and `docs/ABOUT.md` (why it looks like this, whose toolbelt it is); a fourth onboarding screen with the campaign map; the version and theme stamped on the title screen.
- The template pieces: CI and Pages workflows, `env.example`, `scripts/setup.sh` with `--check` and `--yolo`, zsh helpers, `just break`, `just rescue`, `just council`, `just explain`, and a Claude model fallback for print mode.

### Changed

- The product is Vibe Code Camp everywhere: the Python package is `vibemap`, the command is `vibe`, the config is `vibe.toml`, state lives in `.vibe/`, the vault folder is `vault/Camp/`, the game is `game/vibe-map.html`, the skills are `develop-camp`, `install-camp` and `camp-progress`. The game reads progress from the new `vibemap1` key and, once, from the old `grimoire3` key, so nobody loses an evening.
- The title screen: the island renders and orbits behind the panel from the first frame, the brief folds away, a stats row and a monospace kicker replace the wall of text, and the call to action sits above the fold on a phone. Every leftover cyan, violet and pink (callouts, the vault reader, the path rows, the world picker) maps to the five hues; no gradients anywhere.
- The default theme is `studio`: professional, plain, coffee, with Rolinda's questions intact. `wine-night` keeps the original jargon and pairings as an optional mode (`vibe theme wine-night`).
- `AGENTS.md` adopts the file map, comment and test-loop conventions studied in sokrypton/aoe, ideas only (ADR 0002), and the standard-library-only rule for Python is lifted (ADR 0003).
- The seven house skills rewritten for the `src/` layout and the uv CLI.
- The existing Python formatted with ruff; regenerated outputs stay byte-identical.
- The onboarding test runs on injectable paths instead of the real config.

### Removed

- The fantasy layer: the Grimoire codename, the summoned creature with strength and wisdom, the dice, the spell and the dragon. In their place: a project mascot with speed, insight and charm, logged runs, releases and a coffee scoreboard. The satire of corporate language stays.

### Fixed

- Walking on every browser: the collision check called `onLand`, which did not exist (the helper is `onLandW`), so moving Lotte threw a ReferenceError.
- The phone HUD: the name pill takes its own row and the KPIs sit below the buttons.
- The backup hook in `.claude/settings.json`.

## [0.1.0] - 2026-09-16

The initial package on `main`: the course as one folder, no dependencies beyond Python 3.

### Added

- The single-file 3D game `game/vibe-map.html` and the placeholder `game/index.html` for workstream 1.
- `vibemap/cli.py`, a standard-library terminal companion (`uv run vibe status`), with `vibemap/campaign.json`.
- `AGENTS.md`, `CLAUDE.md`, `HANDOVER.md`, seven house skills in `.agents/skills/`, the `scorekeeper` subagent and the backup hook.
- `data/scores.csv`, three DuckDB queries in `sql/`, and `python/scores.py`.
- The Obsidian vault seed in `vault/Camp/`, `README.md`, `docs/SYLLABUS.md`, `docs/RESOURCES.md` and `docs/ROADMAP.md`.
- The tech tree source `tools/tech.py` with its generator `tools/regen_tree.py`.

[Unreleased]: https://github.com/tpetedb/vibe-map/compare/v0.12.0...HEAD
[0.12.0]: https://github.com/tpetedb/vibe-map/compare/v0.11.0...v0.12.0
[0.11.0]: https://github.com/tpetedb/vibe-map/compare/v0.10.0...v0.11.0
[0.10.0]: https://github.com/tpetedb/vibe-map/compare/v0.9.0...v0.10.0
[0.9.0]: https://github.com/tpetedb/vibe-map/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/tpetedb/vibe-map/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/tpetedb/vibe-map/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/tpetedb/vibe-map/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/tpetedb/vibe-map/compare/v0.4.1...v0.5.0
[0.4.1]: https://github.com/tpetedb/vibe-map/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/tpetedb/vibe-map/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/tpetedb/vibe-map/compare/v0.1.0...v0.3.0
[0.1.0]: https://github.com/tpetedb/vibe-map/releases/tag/v0.1.0
