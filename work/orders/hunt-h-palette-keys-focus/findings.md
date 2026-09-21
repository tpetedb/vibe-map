> Cut from the hunt's triage of 2026-09-19. The `Shot:` names refer to that hunt's screenshots, which were not kept: reproduce each finding from its steps on current main before you touch anything, and take your own screenshots into `tests/out/`. Line numbers are from that day and will have moved.

## Batch H: palette, keys, focus

### H1 (02-5) The palette claims a locked stop, bypassing the dependency gate - medium, game-ui
Repro: fresh game, Cmd K, type "Business", open "21:00, Business Continuity Tower", press
"Mark as done". Seen: `done` goes from `[]` to `[4]` although the Roadmap renders the same stop
disabled with "(blocked by dependency)". Expected: the palette respects the same lock.
File: `src/game/41-search.js:10`. Shot: `02/a5-after-out-of-order-claim.png`.
Status: present on main, unchanged.

### H2 (14-3) C opens the Ask panel underneath the open palette - medium, game-ui
Repro: Cmd K, one Tab (focus on a result row, not an input), press c, then Escape once.
Seen: `{pal:'on', sheet:'on', screen:'s-chat'}` and Escape reveals the Ask panel.
Expected: with the palette open, c does nothing.
File: `src/game/88-chat.js:117` (the tagName test at `:118` does not fire on a button).
Shot: `14/repro-c-inside-palette.png`. Status: present on main, unchanged.

### H3 (14-5) Focus escapes the palette although it is aria-modal - medium, game-ui
Repro: Cmd K, then three Shift+Tabs.
Seen: focus walks to Inspect, More and World while `#pal` still has class `on`.
Expected: a dialog with aria-modal holds focus and restores it on close.
File: `src/body.html:60` with `src/game/41-search.js`. Shot: `14/pal-shift-tab-escape.png`.
Status: present on main, unchanged.

### H4 (14-4) Settings is unreachable by forward Tab from More - medium, game-ui
Repro: focus More, press Enter to open the menu, press Tab four times.
Seen: focus goes to `#enterbtn`, then out of the HUD; Settings is only reachable backwards.
Expected: a button with aria-expanded puts its menu items next in the tab order.
File: `src/body.html:13` (DOM order). Shot: `14/more-open-1440.png`. Status: present on main.

### H5 (14-8) Palette rows badge a single stop with the plural counter - low, content
Repro: Cmd K and read the kind badge on each row.
Seen: every stop row reads "STOPS" while other kinds are singular (Note, Topic, Mentor).
Expected: a singular noun for one result.
File: `src/game/41-search.js:9` (`CONFIG.theme.stopLabel`, plural in `vibemap/themes.py`).
Shot: `14/pal-open.png`. Status: present on main, unchanged.

### H6 (14-9) Palette arrow selection is invisible to assistive tech - low, game-ui
Repro: Cmd K, press ArrowDown three times, then Escape.
Seen: the highlight moves and aria-selected flips, but focus stays on `#pal-q`, the input has
no combobox role and no aria-activedescendant, rows have empty ids; focus is not restored.
Expected: combobox with aria-activedescendant, and focus restored on close.
File: `src/game/41-search.js:35`. Shot: `14/pal-open.png`. Status: present on main.

### H7 (14-10) The desktop hint offers the on-screen stick, which desktop hides - low, content
Repro: start at 1440, 1100 or 800 on a mouse machine and read the hint bar.
Seen: "use the stick" while `#joy` and `#jump` are `display:none` at every width tested.
Expected: the stick clause sits behind the same media query that shows the stick.
File: `src/body.html:24` with `src/style.css:325`. Shot: `14/hud-1440.png`.
Status: present on main, unchanged.

---
