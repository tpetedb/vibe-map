> Cut from the hunt's triage of 2026-09-19. The `Shot:` names refer to that hunt's screenshots, which were not kept: reproduce each finding from its steps on current main before you touch anything, and take your own screenshots into `tests/out/`. Line numbers are from that day and will have moved.

## Batch F: artifacts

### F1 (09-2, 10-5) A second demo click interleaves both transcripts - medium, game-ui
Repro: open the cafe, press "Order a coffee", press "Ask for unicorn milk" 200ms later.
Seen: one merged transcript, "GET /flat-white?milk=unicorn ... 200 OK ... 404 Not Found";
reproduced on the well and the factory too. Expected: a new demo cancels the pending lines.
File: `src/game/16-artifacts.js:155` (`runDemo` clears the element but not its timeouts).
Shot: `09/50-cafe-two-presses.png`. Status: present on main, unchanged.

### F2 (09-3) Ligatures render "->" as an arrow in a print-it-exactly step - medium, game-ui
Repro: open the cafe sheet, read step 4 of "Do it for real", copy what is on screen.
Seen: the DOM text is ASCII but Inter draws "GET /coffee -> 200" as an arrow, so a literal copy
fails the check. Expected: no ligature substitution in text meant to be reproduced.
File: `src/game/16-artifacts.js:138` with `src/style.css:32`. Shot: `09v/f3-cafe-step4.png`.
Status: present on main, unchanged.

### F3 (09-8) The demo terminal ignores reduced motion and is silent to readers - low, game-ui
Repro: run with `prefers-reduced-motion: reduce`, press a demo button, read straight away.
Seen: empty at 60ms, full about 1.5s later, while `typeOut` is already complete; `#art-term`
has no aria-live. Expected: print at once under reduced motion, and announce the result.
File: `src/game/16-artifacts.js:155`, `:147` against `src/game/00-state.js:91`.
Shot: `09/42-reduced-motion-demo.png`. Status: present on main, unchanged.

### F4 (09-6) The fountain has no visible ring: it is inside the lake disc - medium, game-world
Repro: walk west on the campus until "Inspect the fountain" appears and look at it.
Seen: no yellow ring; the fountain has no `ART_PROPS` model so the ring falls to r 1.2 at
y 0.05, inside the lake cylinder at the same centre. Expected: the ring is visible.
File: `src/game/16-artifacts.js:127` with `src/game/21-world-build.js:38`.
Shot: `09/43-fountain-ring-zoom.png`. Status: present on main, unchanged.

### F5 (09-11, 10-3) The Inspect zone is up to three times the drawn ring - medium, game-world
Repro: walk at the fountain, then at the mountain, and note where the prompt lights up.
Seen: fountain trigger r 3.68 and mountain r 4.64 after `WORLD_SCALE`, against a drawn ring of
1.2; on the mountain the ring is buried in the obstacle. Expected: the ring is the zone, since
the copy says "walk up to the yellow ring".
File: `src/game/16-artifacts.js:127` against `:130`. Shot: `10/mountain-00-near.png`.
Status: present on main, unchanged.

### F6 (10-2) Artifact-sheet wikilinks look like text and no keyboard reaches them - medium, game-ui
Repro: open any artifact sheet, look at the "In the vault:" line, try to Tab to it.
Seen: colour rgb(139,147,167) identical to the muted parent, cursor auto, no underline, SPAN
with tabIndex -1 and no role; the same class in the vault is blue and clickable.
Expected: the vault's affordance and a focusable control.
File: `src/game/16-artifacts.js:150` with `src/style.css:300`. Shot: `10/mountain-03-links.png`.
Status: present on main, unchanged.

### F7 (09-7) The balloon demo charges the us-east-1 rate for eu-west-1 - low, content
Repro: open the balloon sheet and press "Rent a balloon".
Seen: "--region eu-west-1" then "meter: 0.0208 USD per hour"; t3.small is 0.0208 in us-east-1
and 0.0228 in eu-west-1. Expected: the region and the rate agree, in the demo about regions.
File: `src/game/16-artifacts.js:40`. Shot: `09/11-balloon-demo1.png`.
Status: present on main, unchanged.

---

### P9, handed on from batch P (pull request 142)
See the pull request's body: the finding lives in `src/game/16-artifacts.js` and was left for this batch.
