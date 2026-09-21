## Batch 2: Wayfinding and movement

Owns `src/game/30-input.js`, `src/game/31-animate.js`, `src/game/32-minimap.js`,
`src/game/41-search.js`, `src/game/22-archipelago.js`.

Proposals 2 (walk me there, and the `walkTo()` seam the Roadmap calls), 3 (edge arrow), 6 (path
preview), 12 (remappable keys), 13 (gamepad), 14 (hold to run), 15 (fast travel), 16 (tappable map),
and the idle half-rate half of proposal 7.

Prerequisites: filed bugs D1, E1, E3, V4.

## 2. Walk me there, from the Roadmap and the search palette

**Gets you**: pick a stop in the Roadmap or in Cmd K and your walker starts walking to it instead of
you hunting for the signpost.

**Seen in**: Xbox Accessibility Guideline 109, whose goal is "to ensure that players always know what
goals or objectives they're supposed to be working toward"; it cites Fable III, where "the player is
guided to the next objective by a clear visual path on the ground", and The Outer Worlds, where "the
waypoint marker gives further guidance to players regarding which direction they should move"
(https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/109).

**Here**: `30-input.js` holds `target`, `hasTarget` and `marker`; expose one seam,
`window.walkTo(plotIndex)`, that sets them from `PLOT_POS` and clears any joystick input.
`41-search.js` `palGo()` gets a second action on a stop row ("Walk there") next to the existing
"Open", and `40-sheet.js` `renderMap()` gets the same button per row. If the stop is on another
island, chain `startFlight()` in `22-archipelago.js` first and walk after it lands.

**Effort**: M. **Risk**: low to medium; the walker must not be sent across water or onto a shut
bridge, so `walkTo` refuses a target on another island until the flight has landed. **State**: none.

## 3. An edge arrow to the next stop and to the open bridge

**Gets you**: a small chevron at the edge of the screen always points at the next open stop, with its
distance, so you never circle the island looking for it.

**Seen in**: Game Accessibility Guidelines, "Indicate / allow reminder of current objectives during
gameplay" (Cognitive, Intermediate): "A reminder can help greatly. Either permanently displayed, on
player request, or triggered automatically"
(https://gameaccessibilityguidelines.com/indicate-allow-reminder-of-current-objectives-during-gameplay/).
Xbox Accessibility Guideline 109 asks for "options to enable waypoint or path markers, hints, or
other reminders and directional cues"
(https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/109).

**Here**: `32-minimap.js` already computes the next stop and the state of every bridge each frame, so
it owns the data; it can draw a second, tiny canvas or position a DOM chevron rather than a third
source of truth. A second chevron in the bridge's colour appears only when the island is finished and
a bridge has opened. Off by default at expert and god, and a Settings row turns it off anywhere.

**Effort**: M. **Risk**: low; it is another fixed-position element, so it has to respect the HUD
stacking that `mmLayout()` already measures. **State**: `S.settings.guide` (on, next only, off).

## 6. A path preview on tap, and a marker that stays until you arrive

**Gets you**: tapping the ground shows a dotted line to where you are going, and the marker stays
until you get there instead of fading after a second.

**Seen in**: Xbox Accessibility Guideline 109 cites Fable III: "the player is guided to the next
objective by a clear visual path on the ground", adjustable from low brightness to very bright or off
(https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/109).

**Here**: `30-input.js` sets `marker.material.opacity=1` on a tap and `31-animate.js` decays it with
`marker.material.opacity*=.985`, so the destination disappears while the walker is still on the way.
Hold the opacity while `hasTarget` is true and drop it on arrival, and draw a thin dashed line from
the walker to the marker with the same material family `mat()` already provides. It reuses the
existing marker mesh, so it costs no new draw call beyond the line.

**Effort**: S. **Risk**: low. **State**: none, unless the line gets its own Settings row, in which
case `S.settings.guide` from proposal 3 covers it.

## 12. Remappable keys

**Gets you**: the movement, jump, Enter and panel keys can be changed, so a non-QWERTY layout or a
one-handed grip works.

**Seen in**: Game Accessibility Guidelines, Motor (Basic), "Allow controls to be remapped /
reconfigured": "Remappable controls are one of the best value accessibility features"
(https://gameaccessibilityguidelines.com/allow-controls-to-be-remapped-reconfigured/). Xbox
Accessibility Guideline 107: "Players should be given the option to remap all of the controls within
the game itself"
(https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/107). Unpacking
is widely reported to ship fully remappable controls
(https://caniplaythat.com/2021/11/01/unpacking-accessibility-review-can-i-play-that-pc/).

**Here**: `30-input.js` reads raw key names in two places (`keys.arrowup||keys.w` in `31-animate.js`,
and the `keydown` handler). Introduce one map, `KEYMAP`, defaulted from the current keys and
overridden by `S.settings.keys`, and read it in both. The Settings row is a press-a-key capture,
refusing a key already bound and offering "Back to the defaults" alongside the existing button.

**Effort**: M. **Risk**: medium; the global keys are shared with the palette and the Ask panel, and
filed bug V4 ("Arrow keys never reach a text field once the game has started") shows that surface is
already fragile. **State**: `S.settings.keys`.

## 13. Gamepad support

**Gets you**: a controller paired to the laptop or the phone drives the walker, opens a stop and
scrolls a lesson.

**Seen in**: MDN, Gamepad API, "well established and works across many devices and browser versions.
It's been available across browsers since March 2017"
(https://developer.mozilla.org/en-US/docs/Web/API/Gamepad_API). Bruno Simon's three.js portfolio
publishes gamepad controls next to its keyboard and touch controls, with joystick steering and
button-mapped actions (https://bruno-simon.com/).

**Here**: poll `navigator.getGamepads()` once per frame from `31-animate.js` through a reader in
`30-input.js`, mapping the left stick onto the same `joy` object the touch stick fills, the south
button onto `enterNear()` and the east button onto `closeSheet()`. Nothing else changes, because the
whole movement path already runs off `joy`. Show the controller hint line only once a `gamepadconnected`
event has fired.

**Effort**: M. **Risk**: low; polling a disconnected pad returns nulls, so the reader has to tolerate
holes in the array. **State**: none.

## 14. Hold to run, with a toggle for anyone who cannot hold

**Gets you**: press and hold to move faster across a big island, or flip one setting and make it a
toggle instead.

**Seen in**: Game Accessibility Guidelines, "Avoid / provide alternatives to requiring buttons to be
held down" (Motor, Intermediate): "Holding requires much greater motor ability than pressing,
particularly on buttons that require more strength to operate"
(https://gameaccessibilityguidelines.com/avoid-provide-alternatives-to-requiring-buttons-to-be-held-down/).

**Here**: `85-settings.js` already has `speedMult()` returning 0.7, 1 and 1.5. Add a transient
multiplier that `30-input.js` sets while Shift is down, or while the on-screen stick is pushed past
90 percent of its radius, and a Settings row `run` with values hold and toggle. `31-animate.js` reads
`speedMult()` in one place, so the change is one multiplication.

**Effort**: S. **Risk**: low; at 1.5 times the walking speed the existing edge and obstacle handling
already holds, but the collision slide should be checked on the winter island's narrow paths.
**State**: `S.settings.run`.

## 15. Fast travel to a visited island and a finished stop

**Gets you**: jump straight back to a stop you have already done, instead of walking the whole island
to re-read its lesson.

**Seen in**: Bruno Simon's three.js portfolio ships a respawn that "teleports you to the closest
respawn" when you get stuck (https://bruno-simon.com/). Game Accessibility Guidelines, "Offer a means
to bypass gameplay elements that aren't part of the core mechanic, via settings or in-game skip
option" (Intermediate)
(https://gameaccessibilityguidelines.com/offer-a-means-to-bypass-gameplay-elements-that-arent-part-of-the-core-mechanic-via-settings-or-in-game-skip-option/).

**Here**: `22-archipelago.js` already has the camera flight and `21-world-build.js` already rebuilds
an island and places the walker. Reuse both: a destination list of visited islands and delivered
stops, and on pick, fly, rebuild if the island changes, and set the walker at that plot. Lock it to
stops already in `S.doneW`, so it never skips the dependency gate that filed bug H1 already covers
for the palette.

**Effort**: M. **Risk**: medium; the island rebuild path is where filed bugs D1 and E1 live, so this
has to wait for them. **State**: none.

## 16. The minimap becomes a tappable map

**Gets you**: tap a plot on the open map to walk there, and a long press opens the map full screen.

**Seen in**: Xbox Accessibility Guideline 109 cites Ori and the Will of the Wisps, where "players can
access their map and view current objectives at any point" and the map "indicates where key quest
locations are"
(https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/109). Xbox
Accessibility Guideline 102 makes the point that a mini-map carrying critical information has to be
readable too
(https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/102).

**Here**: `32-minimap.js` already maps world coordinates to canvas pixels in `px(x,z)`; invert it for
a pointer event and hit-test the plots it already draws, then call `walkTo()` from proposal 2. The
full-screen mode is the same canvas at `MM_PHONE` size with the plots labelled. The module already
holds the only piece of state it needs (`mmOpen`).

**Effort**: M. **Risk**: medium; it is a canvas, so every tappable plot needs a parallel list of
buttons or an `aria` description for anyone not using a pointer. Filed bug E14 ("The map button never
reports its state") is the same element. **State**: none.

## 7. Pause and battery saver when the page is hidden or idle

**Gets you**: switching tabs or locking the phone stops the clock and the work, so the battery lasts
and the Stats panel does not credit you with an hour spent in another app.

**Seen in**: MDN, Page Visibility API, widely available since July 2015, exposing `visibilitychange`
and `document.visibilityState` so pages can "save resources and improve performance"
(https://developer.mozilla.org/en-US/docs/Web/API/Page_Visibility_API). MDN on
`requestAnimationFrame`: "requestAnimationFrame() calls are paused in most browsers when running in
background tabs or hidden `<iframe>`s, in order to improve performance and battery life"
(https://developer.mozilla.org/en-US/docs/Web/API/Window/requestAnimationFrame). Xbox Accessibility
Guideline 108 asks that "Single player, local multiplayer, and local split-screen games should be
pausable at any time"
(https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/108).

**Here**: the frame loop already stops itself when the tab is hidden, but the `play` tick in
`00-state.js` and the sky clock do not know it, so time in another app is counted as time on the
island. Add one `visibilitychange` listener in `90-boot.js` that pauses the tick and the elapsed
clock and resumes both on return. Separately, in `31-animate.js`, after sixty seconds with no input
and no open panel, render every second frame; any key, tap or stick event restores full rate.

**Effort**: S. **Risk**: low; the idle halving must be off while a demo is typing in the artifact
sheet, and the clock resume must not produce a giant `dt`, which `Math.min(.05, ...)` already caps.
**State**: `S.settings.saver` (auto, off).

