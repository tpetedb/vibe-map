## Batch 4: Feedback, the companion and the frame loop

Owns `src/game/18-avatar.js`, `src/game/19b-pet.js`, `src/game/19-items.js`,
`src/game/00-state.js`, `src/game/90-boot.js`.

Proposals 7 (pause on `visibilitychange`), 10 (haptics), 20 (quiet mode and notifications log), 21
(pet cheer), 22 (contextual hints), and the `save()` tick from 24.

Prerequisites: filed bugs B2, B3.

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

## 10. A haptic tick on Android for a claim, an unlock and a find

**Gets you**: a short buzz when an OKR lights, a bridge opens or you pick up a collectible, so the
phone confirms the thing your thumb just did.

**Seen in**: Game Accessibility Guidelines, Motor (Basic), "Include toggle/slider for any haptics"
(https://gameaccessibilityguidelines.com/basic/). MDN, Vibration API: "Sticky user activation is
required. The user has to interact with the page or a UI element in order for this feature to work",
and MDN marks the feature "not Baseline because it does not work in some of the most widely-used
browsers" (https://developer.mozilla.org/en-US/docs/Web/API/Vibration_API). Support is Chrome for
Android since 32, with the note "Beginning in Chrome 60, this method requires a user gesture.
Otherwise it returns `false`"; Safari on iOS does not implement it at all. The owner plays on Android
Chrome, so this is a real win there and a silent no-op on iPhone.

**Here**: one helper next to `toast()` in `18-avatar.js`: `buzz(pattern)`, feature-detected, gated by
a Settings toggle that is visible only when `navigator.vibrate` exists. Call it from `claim()` in
`40-sheet.js`, from the bridge-open path in `22-archipelago.js` and from the collectible pickup in
`19-items.js`. Because it must ride a user gesture, it fires in the click handler, never from a frame.

**Effort**: S. **Risk**: low; the toggle has to default to on but be one tap away, and nothing may
depend on the return value. **State**: `S.settings.haptics`.

## 20. A quiet mode and a notifications log

**Gets you**: a switch that stops toasts interrupting a lesson, with everything they would have said
still readable in Stats.

**Seen in**: Xbox Accessibility Guideline 109: "Interruptions (like notifications or side quests)
that aren't directly related to the objective at hand can be postponed or suppressed by the player",
citing Gears 5's HUD notification toggle
(https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/109). Xbox
Accessibility Guideline 117, goal: "to ensure that players can pause or completely stop any content
that scrolls, blinks, auto-updates, or otherwise moves"
(https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/117).

**Here**: `toast()` in `18-avatar.js` is the single entry point. Give it a queue with a cap, a quiet
mode that suppresses the visual toast while still calling `track()`, and a list in `89-dashboard.js`
built from those events. Filed bugs B2 and B3 (the toast covering the HUD and stacking off the top)
are about placement and should land first; this proposal is the suppression and the log, not the
layout.

**Effort**: S. **Risk**: low. **State**: `S.settings.toasts` (all, important, quiet).

## 21. A cheer from the pet on a claim

**Gets you**: your companion reacts when you deliver a workstream, so the moment lands somewhere other
than a toast.

**Seen in**: Xbox Accessibility Guideline 103, goal: "to express visual and audio cues by using
multiple sensory methods", with the printed rule "Color alone should never be used to represent
information"
(https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/103). A second
visual channel for a claim is exactly that.

**Here**: `19b-pet.js` maps three states onto the packs' rows through `PET_STATE`, and a pack without
a row already falls back to idle. Add a one-shot `cheer` state that plays a pack's existing row
faster for a second and returns to idle, triggered from `claim()` in `40-sheet.js` through the same
`window.track` style seam the other modules use. No new pixels, no new licence, nothing to credit.

**Effort**: S. **Risk**: low; the sprite atlas is built once, so the state has to be one that exists
in every pack or fall back cleanly, which the module already does. **State**: none.

## 22. Contextual first-time hints that never repeat

**Gets you**: the first time you stand on a bridge, sit on a bench or open the vault, one short line
tells you what you can do, and never again.

**Seen in**: Game Accessibility Guidelines, "Include contextual in-game help / guidance / tips"
(Cognitive, Intermediate): "Gradually introducing concepts to the player during gameplay not only
gives greater context, but also avoids overburdening gamers"
(https://gameaccessibilityguidelines.com/include-contextual-in-game-helpguidancetips/).

**Here**: one helper, `hint(id, text)`, next to `toast()` in `18-avatar.js`, showing a line once per
id and recording the id in `S.hints`. Call it from the proximity checks in `30-input.js` and from
`openVault()`, `openTree()` and `openPack()`. Settings gets a "Show the hints again" button next to
"Back to the defaults".

**Effort**: S. **Risk**: low; the ids have to be stable strings, because a renamed id shows an old
hint again. **State**: `S.hints` array.

## 24. An autosave tick and an export reminder

**Gets you**: a quiet confirmation that progress is saved, and a warning before anything that would
clear it, because this game's save lives in one browser's localStorage.

**Seen in**: Game Accessibility Guidelines, "Provide an autosave feature" (General, Intermediate):
"Players often do not know that a section will be problematic for their particular impairment until
they come across it" (https://gameaccessibilityguidelines.com/provide-an-autosave-feature/). Xbox
Accessibility Guideline 108: "Ideally, both manual and auto-save options should be provided so that
players can continue after failure without significant loss of progress"
(https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/108).

**Here**: `save()` in `00-state.js` is the single write; have it flag a tiny "saved" mark in the HUD
that fades. In `80-sync.js`, if `S.doneW` has content and nothing has ever been exported, show a line
in the Roadmap's sync card offering the export, and show the same line in the confirm step of
`resetProgress()` in `85-settings.js`, which today keeps only the name and settings.

**Effort**: S to M. **Risk**: low; `save()` is called very often, so the mark must be throttled and
must not force a layout each time. **State**: `S.exportedAt` timestamp.

