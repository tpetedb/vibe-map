## Batch 5: Continuity, photo mode and install

Owns `src/game/80-sync.js`, `src/game/89-dashboard.js`, a new `src/game/33-photo.js`,
`tools/build.py`, `.github/workflows/pages.yml`.

Proposals 24 (export reminder), 25 (break card), 26 (forgiving streak), 27 (photo mode and share), 28
(install and offline).

Prerequisites: filed bugs D7, R10, R13.

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

## 25. A session timer and a gentle break card

**Gets you**: after about fifty minutes the game says, once, that this is a good place to stop, and
shows where you are; it never blocks anything.

**Seen in**: Game Accessibility Guidelines, "Do not make precise timing essential to gameplay, offer
alternatives, actions that can be carried out while paused, or a skip mechanism" (Motor, Advanced):
"There are gamers who find any kind of timing difficult or impossible"
(https://gameaccessibilityguidelines.com/do-not-make-precise-timing-essential-to-gameplay-offer-alternatives-actions-that-can-be-carried-out-while-paused-or-a-skip-mechanism/).
Xbox Accessibility Guideline 109 asks that interruptions be suppressible by the player
(https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/109).

**Here**: `89-dashboard.js` already derives time from the `play` ticks in `00-state.js`, so the timer
is a read, not a new store. Show a dismissible card between stops, never during one, and give it an
off switch. It has to be built on top of proposal 7, or a phone left in a pocket will "earn" the
break.

**Effort**: S. **Risk**: low; the tone has to stay Rolinda's, plain, never a nag. **State**:
`S.settings.breaks` (on, off).

## 26. A streak that a missed evening cannot break

**Gets you**: a day streak that survives a skipped evening, so a four-evening course does not punish
you for having a life.

**Seen in**: Duolingo's own blog on the streak, quoting Osman Mansur: "Your streak is a tangible,
measurable number that holds you accountable to practicing every single day", and, on the freeze:
"Offering Streak Freezes keeps learners dedicated to learning even when they need to skip a day or
two of practice" (https://blog.duolingo.com/how-duolingo-streak-builds-habit/).

**Here**: the streak is derived from the `play` and `claim` events in `00-state.js`, so this is
arithmetic in `89-dashboard.js` plus the matching rule in the CLI so the two agree. Allow one rest day
per week without breaking the run, and say so in the tile's caption. Filed bugs D7 ("The KPI labelled
Streak is the completion percentage") and R10 ("Day streak counts different things in the game and in
the terminal") both have to land first, or this is built on sand.

**Effort**: S to M. **Risk**: low technically, coupled to the CLI socially; `vibemap/dashboard.py`
has to use the same rule. **State**: none, derived.

## 27. Photo mode, with the HUD hidden and a share image

**Gets you**: a clean picture of your finished island at night, saved or shared straight from the
phone.

**Seen in**: MDN, `HTMLCanvasElement.toBlob`, "creates a `Blob` object representing the image
contained in the canvas", supported in Chrome for Android since 50 and Safari since 11
(https://developer.mozilla.org/en-US/docs/Web/API/HTMLCanvasElement/toBlob). MDN, Web Share API:
"This method must be called on a button click or other user activation (requires transient
activation)" (https://developer.mozilla.org/en-US/docs/Web/API/Web_Share_API); `navigator.share` is
supported in Chrome for Android since 61 and Safari since 12.1, and sharing files since Chrome for
Android 76 and Safari 14, with `navigator.canShare()` to test first.

**Here**: a new module, `33-photo.js`, adding a HUD entry that hides `.ui`, pulls the camera back a
little and takes the frame. The canvas is created without `preserveDrawingBuffer`, and MDN describes
that attribute as meaning "the buffers will not be cleared and will preserve their values until
cleared or overwritten by the author"
(https://developer.mozilla.org/en-US/docs/Web/API/HTMLCanvasElement/getContext), so the capture must
happen inside the same animation frame, right after `renderer.render`, or the context has to be
created with the attribute set. Then `canvas.toBlob`, then `navigator.canShare({files})` and
`navigator.share`, falling back to a download link.

**Effort**: M to L. **Risk**: medium; turning on `preserveDrawingBuffer` costs performance on every
frame, so the same-frame capture is the right answer and needs a test that waits for
`window.__debug().frame` rather than a timer. **State**: none.

## 28. Install as an app, and work offline

**Gets you**: the hosted game can be added to the Android home screen and opens without a browser bar
and without a network.

**Seen in**: MDN, Making PWAs installable: "While not a requirement for a PWA to be installable, many
PWAs use service workers to provide an offline experience", with the Chromium install requirements
being a manifest with a name, 192 px and 512 px icons, a `start_url`, a `display`, and HTTPS
(https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Making_PWAs_installable).
Chrome's own post: "we have removed the requirement to have a service worker that implements the
fetch() method for installation from the menu, since version 108 on mobile and 112 on Desktop"
(https://developer.chrome.com/blog/update-install-criteria).

**Here**: `.github/workflows/pages.yml` already copies extra files next to the page (`news.json`,
`your-game.html`), so it can copy a `manifest.webmanifest` and a tiny `sw.js` that caches the one
HTML file. The single-file build stays exactly what it is: the manifest link is added only when the
build is for Pages, so `just game` from a `file://` path is unchanged and the "one file, no CDN,
works offline" stamp in `body.html` stays true. Note for the same pass: MDN records that the standard
Fullscreen API on iOS is "Only available on iPad, not on iPhone"
(https://developer.mozilla.org/en-US/docs/Web/API/Fullscreen_API), so the Full screen button and the
install prompt should not both be offered on an iPhone.

**Effort**: M. **Risk**: medium; a service worker that caches the game will happily serve a stale
build after a push, so it has to be a network-first worker keyed on the build version that
`tools/build.py` already injects. **State**: none.

---

