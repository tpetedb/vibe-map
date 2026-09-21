# Galaxy: a second way to travel the same course

Status: proposal, not built. The decision it rests on is [ADR 0015](adr/0015-experiences-share-one-core.md). Nothing here changes the island game; the two are meant to live next to each other.

The idea in one line: every topic sits where it happened, a lab, a company, a city, a year. Each place is a tiny planet carrying a small dome of the real thing, pinned where it is on Earth, and one line through the universe shows your whole journey. You fly between them in a ship, land, walk, learn the same lesson, and build.

## 1. What was asked

Method: one stakeholder brief (Tom, two spoken notes, 2026-09-21), read against the repository and the literature below. One participant, so this is a brief and its evidence, not user research. The quotes are his words, tidied only for spelling.

| Theme | In his words | What it means for the product |
|---|---|---|
| Place is generic today | "instead of the current quite generic items every topic is on an island or in a place where it actually happened in history" | A topic's position must come from its history, as data, with a source. |
| Abstract and diverse places | "this can be abstract and diverse, in the cloud, in California, in China, at different labs or companies at different points in time" | A place is not only a dot on Earth. It has a kind (lab, company, university, city, network, the cloud) and an era. |
| Travel is the fantasy | "teleporting you through a galaxy", "travel by spaceship like a crazy future Age of Empires" | Travel between places is a feature, not a loading screen. The ages of the tech tree already are the Age of Empires ladder. |
| It rhymes with the vault | "this also kind of works with the vault theme" | The star map and the vault graph are the same graph, laid out by place and time instead of by force. |
| Walk and build | "in a spaceship and can walk planets and build" | Landing leads to the walking the game already has, and a finished topic leaves something built. |
| Clean layers | "a good separation of concerns with config and underlying data and source code for the backend, frontend" | Data, configuration, the Python side and the browser side each own one thing, and the two experiences share everything below the view. |
| The whole journey at a glance | "it should be easy to also see the whole journey, in a cool sort of journey through the universe" | One zoomed-out view draws the entire course as a single line through the planets: done, next, still ahead. |
| Tiny planets, small domes | "tiny planets that look like small domes of the place where it happens on Earth, like a little Silicon Valley with actual Silicon Valley, and places in China or Europe" | A place is a miniature: a little planet with a glass-dome diorama of the real location on it. Recognisable, not generic. |
| Where on the globe | "just where on the globe it happens, but on a tiny globe; can also be a data centre globe" | The planet is a tiny Earth with the place at its true latitude and longitude. Abstract places get their own globe: a data centre, the cloud. |
| Both, side by side | "Do not ruin the current look of the game, it should be available alongside each other" | Islands stay the default and stay pixel-stable. Galaxy is a choice, switchable, with one shared progress. |

One phrase in the note did not survive transcription ("I don't understand Gwen design, so research that"). It is read here as **game design**, and section 3 is that research. If it meant something else, that section is the one to redo.

### Evidence in the repository

- 65 of 70 topics have a sourced `history` field; 48 name a year; the span is 1962 to 2026. The when exists. The where is prose today ("Postgres 1986 (Berkeley)") and has to become structure.
- All 70 topics declare `unlocks`. That is a route graph between topics, already reviewed and tested. Routes between places fall out of it.
- Progress is stored per stop and per topic in `S` (`done`, `doneW`, `topics`, `artifactsBuilt`), never per scene. A second view needs no new progress format.
- ADR 0010 already settles how real organisations and people appear: by name, as plain text, every claim a link to their own words. Places inherit that rule unchanged.
- ADR 0013 made topics data. ADR 0006 made configuration three levels. This proposal adds to both and breaks neither.

## 2. Does putting knowledge in places help anyone learn

Yes, moderately, and that is worth saying plainly because it is the reason to build this rather than a nicer menu.

- The method of loci (tie each thing to a location you can walk through) works in virtual environments about as well as in familiar real ones: 142 participants, randomised, virtual and conventional palaces performed the same against an uninstructed control (Legge and others, 2012).
- A meta-analysis of 13 randomised trials found a medium effect (g = 0.65, 95 percent interval 0.45 to 0.85), stable after adjusting for publication bias, with the caution that the trials were mostly in university settings (Twomey and Kroneisen, 2021).
- So: a real place, a real year and a walk to get there is a legitimate memory aid. It is not magic, and the lesson text still does the teaching.

Design consequence: a place must be **distinct and stable**. Twelve planets that look alike teach nothing. This is why the small domes in the brief are the right call and not only a nice one: a miniature of the actual place, on a globe that shows where on Earth it is, gives each topic two honest hooks, what it looked like and where it was. A topic must always be found in the same spot.

## 3. Game design, the short version

The framework used here is MDA (Hunicke, LeBlanc, Zubek, 2004), because it separates exactly the things this project already separates.

- **Mechanics** are "the particular components of the game, at the level of data representation and algorithms". Here: topics, places, routes, the done list, the checks.
- **Dynamics** are "the run-time behavior of the mechanics acting on player inputs and each others' outputs over time". Here: which routes open as topics are done, how far you can fly, what gets built.
- **Aesthetics** are "the desirable emotional responses evoked in the player". The paper lists eight kinds of fun: sensation, fantasy, narrative, challenge, fellowship, discovery, expression, submission.

The paper's advice is to decide the aesthetics first and derive the rest. The two experiences aim at different ones, which is the honest reason to have two:

| | Islands (today) | Galaxy (proposed) |
|---|---|---|
| Leading kinds of fun | submission (a calm evening walk), challenge (the checks) | discovery (uncharted places), fantasy (a ship), narrative (history in order), expression (what you build) |
| Pace | one island, eight stops, linear | a map, many routes, your order |
| Best for | a first evening, a learner who wants to be led | a returning learner, someone who asks "where did this come from" |

The core loop of Galaxy, each step a thing that already exists or is cheap:

0. **Journey**: zoomed all the way out, one line threads every planet in course order: solid where you have been, glowing at the next stop, faint ahead. This is the whole course on one screen, and the way back to anywhere. (New view, old data: the campaign order and `S.done`.)
1. **Chart**: one step in, the star map shows places by era. Open routes glow. (New view, old data: `unlocks`.)
2. **Fly**: pick a destination; the ship flies itself. Short, skippable. (New, small.)
3. **Land and walk**: the ship sets down on a tiny planet. On approach you see the little globe with the place lit at its real spot on Earth; then the dome fills the view and you walk the miniature inside it. (The island builder, parametrised by the place, under a dome, on a sphere.)
4. **Learn**: the same sheet, the same lesson, the same `try_it`, the same check. (Unchanged.)
5. **Build**: a finished topic raises a structure on its site, as an annex does today. (The annex reveal, renamed.)
6. **Open routes**: the topic's `unlocks` light new lanes. Back to the chart.

The Age of Empires ladder stays what it is: dark, feudal, castle, imperial are the ages you advance through. In Galaxy they also decide how far the ship can jump, so advancing an age visibly opens a further arm of the map.

## 4. System design

### Requirements

Functional:
- Two experiences, `islands` and `galaxy`, selectable in the settings and in `config/camp.toml`, switchable at any time without losing anything.
- One progress. Done in one is done in the other. The progress code, `state.json`, the vault and the quests do not know which experience was used.
- Every topic has at least one origin: a place, a year, a one-line claim, a source link.
- The Python side can answer the same questions as the game: `vibe places`, `vibe topic <id>` shows the origin.

Non-functional:
- The game stays one file, no CDN (ADR 0001). Galaxy is procedural geometry, no textures or models. Budget: under 80 KB added to a 1.57 MB file.
- Islands render exactly as today. Guarded by golden screenshots taken before any refactor.
- Only the active experience builds a scene. Switching disposes the other through `discard()`.
- WCAG 2.2 AA for everything that is not the 3D canvas, and a complete non-3D path for everything the canvas does (section 6).

Constraints: three.js r128 as vendored, no build step beyond concatenation, phones are first-class, agents build it in parallel so the layers must be separable files.

### The layers

```
  DATA            vibemap/data/topics/**.toml      topics, now with [[origins]]
  (what is true)  vibemap/data/places/<id>.toml    one place: kind, era, region, look
                  vibemap/data/campaign.json       evenings, mentors (unchanged)
                          |
                          |  pydantic loaders, fail loudly with the file name
                          v
  BACKEND         vibemap/topics.py, places.py     schema and loading
  (Python)        vibemap/cli.py                   vibe places, vibe topic
                  tools/build.py                   injects TECH, PLACES, CONFIG
                          |
                          |  one JSON blob per concept, written through js_json()
                          v
  CONFIG          config/camp.toml                 journey: experience = "islands"
  (three levels,  src/config/00-config.js          source: island numbers
   ADR 0006)      src/config/10-galaxy.js          source: galaxy numbers
                          |
                          v
  CORE            src/core/   state S, save/load, progress code, sheet, vault,
  (frontend,                  search, settings, chat, dashboard, sync
   no scene)                  knows topics and stops, never meshes
                          |
                          |  the experience contract (below)
                          v
  EXPERIENCE      src/game/    islands  (today's modules, registered, unchanged)
  (frontend,      src/galaxy/  galaxy   (star map, ship, planet surface)
   a view)        shared:      10-scene.js helpers: mat, keep, discard, release
```

The rule that keeps it honest: an arrow only points down. Core never imports an experience; an experience never writes progress except through core's `claim()`; data never knows a view exists.

### The experience contract

One object per experience, registered by id. Everything core needs from a view, and nothing more:

```js
EXPERIENCES.galaxy = {
  name: "Galaxy",
  build(),            // make the scene from S and the data; idempotent
  dispose(),          // discard() everything it added
  tick(dt, t),        // per frame; must honour reducedMotion()
  goTo(target),       // {stop} or {topic}: bring the player there ("walk me there")
  where(),            // {stop|topic|null}: what the player is at, for the sheet
  listing(),          // the same places as plain data, for the non-3D path
}
```

Islands implements the same seven. Most already exist under other names (`buildWorld`, the animate loop, `openCh`). The first engineering step is to give them these names and change nothing else.

### Data model

A topic gains origins. Additive: a topic that has none still loads, because the packs are sourced one research order at a time, and `places.problems(shelves=..., packs=...)` returns one sentence per topic that is still without one. What cannot be half right fails the loader by file name: an unknown place, a missing or non-https source, two primary origins or none.

```toml
# vibemap/data/topics/core/data.toml
[[origins]]
place = "ibm-san-jose"
year = 1970
what = "Codd publishes the relational model"
source = "https://www.ibm.com/history/relational-database"
primary = true          # where the topic lives; the others are echoes

[[origins]]
place = "uc-berkeley"
year = 1986
what = "Postgres begins"
source = "https://www.postgresql.org/docs/current/history.html"
```

A place is one file of its own, because many topics share one, its look is decided once, and several research orders add origins at the same time without ever owning the same file (ADR 0013's reason for topics, and the amendment on ADR 0015):

```toml
# vibemap/data/places/bell-labs.toml
id = "bell-labs"
name = "Bell Labs, Murray Hill"
kind = "lab"            # lab, company, university, city, network, cloud,
                        # orbit, standards, foundation
region = "us-east"      # a coarse region from vibemap/places.py
era = "mainframe"       # the arm of the galaxy it sits in
globe = "earth"         # earth, datacentre, cloud: which tiny globe carries it
lat = 40.684            # where the dome sits on the tiny globe; refused for
lon = -74.402           # a place that is not on Earth (the cloud, the lanes)
look = "campus"         # which diorama builder and palette family
landmark = "mountain-avenue-plaque"   # one silhouette that stands there, and
                        # never a logo, a wordmark or a mascot (ADR 0010)
source = "https://ethw.org/Milestones:Bell_Telephone_Laboratories,_Inc.,_1925-1983"
```

Eras are the arms of the map, in `vibemap/places.py` next to the loader rather than in the tech tree's `tree.toml`, because an era places a place and not a topic: mainframes and Unix (1960 to 1979), personal computers and the web (1980 to 1999), open source and the cloud (2000 to 2011), data and deep learning (2012 to 2021), agents (2022 on). Abstract places are first-class and get a globe of their own: `datacentre` is a little world of racks and cooling towers, "the cloud" is a nebula you fly into, "the internet" is the lanes themselves, a standard body is a station. On an `earth` globe the continents are a simple outline in one palette hue, enough to say "China", "Europe", "California" at a glance, with the place's dome standing at its true coordinates. Several places in one region (Silicon Valley has many) share a planet and stand as neighbouring domes on it, which is itself a true thing to learn.

An **echo** is a secondary origin. It appears at its place as a marker that offers a jump to the primary site. That is the teleport in the brief, and it is how one topic can honestly belong to IBM in 1970 and Berkeley in 1986.

### State

One new field, a preference, not progress: `S.experience`. It stays out of the progress code, because a code describes what you have done, not how you like to look at it. `config/camp.toml` sets the starting value; the settings panel changes it. No version bump: the field has a default and the loader already fills defaults, and no existing field changes meaning.

### Trade-offs

| Decision | Chosen | Instead of | Why | Cost |
|---|---|---|---|---|
| Where Galaxy lives | Same file, same page, a registered experience | A second HTML file | One progress, one build, one vault, no sync problem | A larger file; bounded by the 80 KB budget |
| Planet surfaces | A tiny globe seen from the ship, and inside its dome a flat miniature built by the island builder | Walking around a true sphere | The brief asks for tiny globes with small domes, and a dome is exactly a flat scene on a sphere: the globe gives the where, the dome gives the walkable what. Walking, collision, plots, annexes, camera and tests keep working | Two scales to build (globe and diorama) and a transition between them, which reduced motion turns into a cut |
| Dioramas | Procedural miniatures from a small kit (buildings, racks, antenna, harbour, campus lawn, hills) plus one landmark per place | Photo textures or downloaded models | One file, no CDN, no licences to clear for real buildings, and the low-poly look matches the islands | A landmark is a suggestion, not a likeness; each one is reviewed against a photo of the real place before it ships |
| Flight | Autopilot to a chosen destination | Free six-axis flight | Motion sickness, phones, keyboards, and it is a course, not a flight sim | Less "pilot" fantasy; a later free-flight toggle stays possible |
| Place data | Structured `[[origins]]` with a source each | Parse the `history` prose | A parsed guess about a real company is a false statement waiting to ship (ADR 0010) | 70 topics to source by hand, in packs, reviewable |
| Refactor | Name the seam first, move files later | Move everything into `src/core` at once | Golden screenshots can prove a rename changed nothing; a big move cannot be reviewed | Two steps instead of one |
| Default | Islands | Galaxy | The brief: do not ruin the current look | Galaxy has to earn the switch |

What to revisit as it grows: the file-size budget once there are more than twenty places; whether eras should be per pack; whether the star map should replace the vault graph view rather than sit next to it.

## 5. Critique of this proposal

Stage: exploration, before any pixels. Severity in words: critical, moderate, minor.

**Overall.** The strongest part is that almost nothing is new below the view: data, state, sheet, checks and vault are reused, and the route graph already exists. The biggest risk is the opposite of the one the brief names: not that islands get ruined, but that Galaxy becomes a second game to maintain.

| Finding | Severity | Recommendation |
|---|---|---|
| The journey view has to read in two seconds or it is wallpaper. | critical | One line, three states (been, next, ahead), one label only: the next stop. Everything else appears on focus or hover. Tapping any planet on the line goes there. |
| Tiny globes with continent outlines can turn to noise at phone size. | moderate | At journey scale a planet is a dot with its dome's colour; the globe and its outline appear only from the chart inward. The pin is a light, not a label. |
| A star map of 70 topics across 20 places is a wall of dots on a phone. | critical | The map shows places, never topics. A place shows a count ("3 of 5"). Topics appear only after landing. Era arms collapse to one at a time on narrow screens. |
| "Where am I going and why" can get lost between chart, flight and surface. | critical | One persistent line, the same in both experiences: the Continue card from the quality-of-life batch ("Next: Git, at Helsinki, 1991"). It is the spine; the ship is decoration around it. |
| Flight that cannot be skipped becomes a tax by the third trip. | moderate | First flight to a place plays in full (about four seconds). Later ones are a one-second cut unless the player holds to watch. Reduced motion always cuts. |
| Places that look alike defeat the memory argument in section 2. | moderate | Each place: one silhouette landmark, one colour family from the palette, one sound-free motion cue. Review them side by side in one screenshot before building more than five. |
| Real places invite real mistakes (wrong year, wrong city, a company that objects). | moderate | ADR 0010 applies in full. A place without a source link does not load. Claims are one line, dated, linked, never paraphrased opinion. |
| Two experiences double the screenshots, the tests and the bug surface. | moderate | The contract has seven functions; the smoke test runs the same script against both by id. What cannot be tested through the contract does not belong in an experience. |
| "Build" is vague. | minor | Version one: the structure is chosen by the topic's shelf and grows with depth. Player-placed building is a later phase, behind its own decision. |
| The palette is OLED black plus five hues; a galaxy tempts purple nebulae. | minor | Stay in the palette. Space is `#000000` already. Eras take the five hues. The banned violet stays banned. |

What works well: islands stay the default and untouched; the abstract places (cloud, internet) turn a weakness of a map into its most memorable parts; echoes give teleporting a meaning instead of a gimmick; the ages finally do something visible.

## 6. Accessibility requirements

Standard: WCAG 2.2 AA, plus the Game Accessibility Guidelines where WCAG is silent about games. This is a review of a design, so every finding is a requirement to build against, not a defect to fix. Each becomes a test.

**Perceivable**

| # | Requirement | Criterion | Severity if missed |
|---|---|---|---|
| P0 | The journey view has the same twin as the map: an ordered list of every stop with its place, year and state (done, next, ahead). It is the accessible form of "see the whole journey", and it is built first. | 1.1.1, 1.3.1 | critical |
| P1 | The star map has a non-3D twin: a real list of eras, places and counts, from `listing()`, that does everything the canvas does. A canvas is one opaque image to a screen reader. | 1.1.1, 1.3.1 | critical |
| P2 | Place labels on a starfield sit on a plate (the existing name-plate helper), never bare on stars; 4.5:1 for text, 3:1 for the lane and marker graphics against `#000000`. | 1.4.3, 1.4.11 | major |
| P3 | Era is never colour alone: arm position, a label and a glyph carry it as well. Same for open, locked and done routes (solid, dashed, ticked). | 1.4.1 | major |
| P4 | Text size follows the existing setting, including map labels; the layout holds at 200 percent. | 1.4.4, 1.4.10 | major |

**Operable**

| # | Requirement | Criterion | Severity if missed |
|---|---|---|---|
| O1 | Everything by keyboard: arrows move between places along lanes, Enter travels, Escape returns to the chart. No flight input is ever required. | 2.1.1 | critical |
| O2 | Flight is autopilot. No holding a key to fly, no timing, no aiming. (GAG basic: "Ensure controls are as simple as possible, or provide a simpler alternative"; intermediate: "Avoid / provide alternatives to requiring buttons to be held down".) | 2.1.1, 2.5.1 | critical |
| O3 | With reduced motion, from the system or the game's own setting, travel is a cut: no warp, no star streaks, no camera sweep, no parallax. WCAG names parallax as a vestibular trigger. | 2.3.3 (AAA, adopted) | critical |
| O4 | No flash above three per second, anywhere, including warp and arrival. | 2.3.1 | critical |
| O5 | Any motion that lasts over five seconds (drifting stars, orbiting planets) can be paused from the settings. | 2.2.2 | major |
| O5b | Zooming between journey, chart, globe and dome is a camera move over a large distance, the exact trigger WCAG warns about. With reduced motion each level change is a cut, and the four levels are also plain buttons, never only a pinch or a wheel. | 2.3.3, 2.5.1 | critical |
| O6 | The camera never rolls, never shakes, and moves only when the player asked for travel. Field of view keeps the island default. (GAG: set an appropriate default FOV; avoid a difference between controller movement and camera movement.) | GAG | major |
| O7 | Touch targets for places and for the travel button are at least 44 by 44 CSS pixels; the map pans with one finger and never needs a two-finger gesture for anything essential. | 2.5.8, 2.5.1, 2.5.7 | major |
| O8 | Focus is visible on the list twin and mirrored on the canvas by a ring on the focused place. | 2.4.7, 2.4.11 | major |

**Understandable and robust**

| # | Requirement | Criterion | Severity if missed |
|---|---|---|---|
| U1 | Switching experience never moves focus unexpectedly and never loses the open sheet; it announces "Galaxy view" or "Island view" through the existing live region. | 3.2.2, 4.1.3 | major |
| U2 | A locked route says why and what opens it ("Finish Git to open this lane"), in text. | 3.3.1 | minor |
| U3 | The list twin uses real elements: a list, buttons with names, `aria-current` on where you are. | 4.1.2 | major |

Keyboard plan:

| Where | Tab | Enter or Space | Escape | Arrows |
|---|---|---|---|---|
| Star map | through the list twin, in era then route order | travel to the focused place | back to the last surface | along lanes between places |
| In flight | skip button only | skip | skip | none |
| On a surface | as on an island today | as today | open the chart | walk, as today |

What cannot be checked on paper: VoiceOver and NVDA on the list twin, and whether autopilot flight still makes anyone queasy. Both need a person, once version zero exists.

## 7. How it gets built

Each phase is one pull request that can ship alone, and islands must be pixel-stable after every one.

| Phase | What | Proves |
|---|---|---|
| 0 | This document and ADR 0015. | The decision, in writing, before code. |
| 1 | Data: `vibemap/data/places/`, `[[origins]]`, `vibemap/places.py`, `vibe places`, `vibe topic` shows origins, `PLACES` in the build. Every place seeded, the shell shelf sourced as the worked example, every claim checked against its link. No game change. | The where and when are real and loadable. |
| 2 | The seam: golden screenshots of the four islands, then the experience contract with islands registered under it. No file moves. | A refactor that changes no pixel. |
| 3 | Galaxy version zero: the list twins first (journey and chart), then the journey line and the star map drawn from them, travel as a cut, tiny globes with the place pinned at its coordinates, landing in a dome whose miniature is built by the island builder with the place's look, the unchanged sheet. Three places only, chosen to be as different as possible (a California campus, a Chinese city, a data centre globe), reviewed side by side. Behind the setting. | The loop works end to end with no flight at all, and the miniatures are recognisable. |
| 4 | The ship: autopilot flight, skip, reduced-motion cut, the ages as jump range, echoes as jumps. | The fantasy, within the accessibility rules. |
| 5 | Build: structures on finished sites, by shelf and depth. The remaining packs sourced. | Expression, and a full map. |
| 6 | Review: the section 5 and 6 tables re-run against the real thing, agents play both experiences, a person tries a screen reader. Then, and only then, a decision on whether Galaxy is offered on the title screen. | It earned its place. |

## 8. Playing together, prepared for and not yet built

Asked after the first draft: "prepare it so people can play together", on the players' own GitHub resources or some other sync, without saying how. This is the how, and what to keep open now so it stays cheap later.

The constraint that decides it is the one from P1: your repo, your bill. Nothing may run on Tom's account, and a camp must keep working alone and offline.

| Option | How it works | Cost and who pays | Verdict |
|---|---|---|---|
| **A crew over GitHub, not live** | Each player's own camp repo publishes one small file, `crew/me.json` (name, where they are, what is done, what they built, when). A crew is a list of repo addresses in `config/camp.toml`. The game fetches each file and draws the others: their ships on the journey line, their structures as ghosts on the planets, "Sam finished Git at Helsinki yesterday". | Nothing new. Public repos and Pages are free, and both answer browsers from any origin (checked: `access-control-allow-origin: *` on `raw.githubusercontent.com` and on `github.io`, cached 5 to 10 minutes). | **Do this first.** It is the vault idea between people: files in git, no server, works for a class or two friends. |
| Live, browser to browser | WebRTC data channels. Needs a way for two browsers to find each other: either paste a code to each other (no server, clumsy) or a public signalling service (a third party the game would depend on). | Free, but a dependency outside the repo, against the no-CDN habit. | Later, and only as an optional layer on top of the crew file, for seeing each other move. |
| A hosted game server | The usual way. | Somebody's bill and somebody's uptime. | No. |

Why not live first: a course is played over evenings, not at the same minute. What people want from "together" here is to see where friends are, what they built and who is ahead, and that is all in a file that changes a few times a night. Ten minutes of cache delay does not matter for that.

What it needs, all small, and where each part lives in the layers of section 4:

- **Backend**: `vibe crew publish` writes `crew/me.json` from `state.json` and commits it; the player pushes with their own git. `vibe crew add <repo>` edits `config/camp.toml`. Opt-in, and the file holds a display name and progress only: no email, no paths, no scores file.
- **Core**: one module, `presence`, with one function, `crew()`, returning a list of `{name, where, done, built, at}`. It is the only place that fetches. An experience reads the list and draws it; it never fetches.
- **Experience**: `listing()` includes the crew, so the non-3D twin says who is where before any ship is drawn.
- **Security**: a crew file is someone else's text. It goes through `esc()` and `safeUrl()` like the news feed, it is size-limited and schema-checked with a version that fails loudly, and a repo address must match `owner/name`. `docs/SECURITY-MODEL.md` gets a row for it.
- **Versioned format**: `crew/me.json` carries `v: 1`. An unknown version is skipped with a message, never guessed at.

What to keep open now so this stays cheap: the experience contract takes a list of other players from core from the first version (empty for now), and a structure on a planet records who built it rather than assuming "me". Both are one field each in phase 3 and 5, and neither costs anything if multiplayer never ships.

Limits to be honest about: a private repo cannot be read this way, so a crew needs public repos or Pages; there is no cheating protection, and none is needed for a course; and rate limits on raw files are generous but real, so the game fetches a crew at most once per ten minutes, matching the cache.

## Sources

- Hunicke, LeBlanc, Zubek, "MDA: A Formal Approach to Game Design and Game Research" (2004): https://users.cs.northwestern.edu/~hunicke/MDA.pdf
- Twomey and Kroneisen, "The effectiveness of the loci method as a mnemonic device: Meta-analysis" (2021): https://journals.sagepub.com/doi/abs/10.1177/1747021821993457
- Legge, Madan, Ng, Caplan, "Building a memory palace in minutes" (2012): https://pubmed.ncbi.nlm.nih.gov/23098905/
- Virtual memory palaces and recall, feasibility study (2022): https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9540171/
- WCAG 2.2, Understanding 2.3.3 Animation from Interactions: https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html
- Game Accessibility Guidelines, full list: https://gameaccessibilityguidelines.com/full-list/
