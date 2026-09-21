> Cut from the hunt's triage of 2026-09-19. The `Shot:` names refer to that hunt's screenshots, which were not kept: reproduce each finding from its steps on current main before you touch anything, and take your own screenshots into `tests/out/`. Line numbers are from that day and will have moved.

## Batch B: panel chrome, toasts, overlap

### B1 (02-3, 07-5, 08-8) Sheet text scrolls under the HUD pill - medium, game-ui
Repro: open a stop or a mentor, scroll the sheet body about 260px, at 1440x900 and 420x860.
Seen: paragraphs intersect the `#hud-bar` rect; the pill is opaque rgb(20,20,20) over the text
and the Close button. Expected: content stops above the HUD or passes behind an opaque bar.
File: `src/style.css:82`, `:86` and `:148` (`#sheet .inner` has no top guard).
Shot: `02/d-desktop-stop4-scrolled.png`, `08/20-torvalds-bottom.png`.
Status: present on main, unchanged.

### B2 (03-12, 06-10, 08-7, 13-3) The toast covers the right HUD buttons - medium, game-ui
Repro: claim a stop that fires an achievement at 1440x900 and watch the top right for 5s.
Seen: toast box x1086 to 1426, y14 to 94 over Stats, Vault, Tree, World and More at y19 to 47;
on a phone it covers the open sheet header. Expected: the toast sits clear of the HUD.
File: `src/style.css:380` (`#toast` top:14 right:14 z-index:60) against `#hud` z-index 40.
Shot: `13v/f3-desktop-toast-over-hud.png`. Status: present on main, unchanged.

### B3 (13-2) A batch unlock stacks toasts off the top of the viewport - medium, game-ui
Repro: import a full progress code at 1440x900; nine achievements unlock in one pass.
Seen: the stack measures top 14 to bottom 724 with `max-height:none`, covering the minimap and
the HUD. Expected: a bounded stack or one summary line.
File: `src/game/18-avatar.js:142` (no cap) with `src/style.css:380`.
Shot: `13/52-after-full-import.png`. Status: present on main; `18-avatar.js` changed only for
the seated walker (#108).

### B4 (02-13, 14-7) The sheet dialog has no accessible name and no aria-modal - low, game-ui
Repro: open any panel or stop and read `#sheet` attributes.
Seen: `{role:'dialog', aria-modal:null, aria-label:null, aria-labelledby:null}` for every
panel, while `#pal` and `#vault` both carry names. Expected: aria-modal and a name per panel.
File: `src/body.html:67`. Shot: `14/panel-stats.png`. Status: present on main, unchanged.

### B5 (14-6) Opening More blanks the KPI row at desktop widths - low, game-ui
Repro: start at 1440x900 (also 800), click More, close it.
Seen: `#kpis` visibility goes visible, hidden, visible although the open menu (x1245 to 1415)
does not overlap the pills (x12 to 381). Expected: hide only inside the 480px block.
File: `src/style.css:109`. Shot: `14/more-open-800.png`. Status: present on main, unchanged.

### B6 (11-6) A wrapped "Do it for real" heading has colliding lines - low, game-ui
Repro: at 1440x900 inspect the switchboard artifact and read the h3.
Seen: font-size 12px with line-height 13.2px, so two lines of caps nearly touch.
Expected: normal leading on a wrapped h3.
File: `src/style.css:51` and `:53`. Shot: `11/22-switchboard-cmds-hard.png`.
Status: present on main, unchanged.

### B7 (11-5) Demo terminal output wraps mid-column and mid-number on a phone - low, game-ui
Repro: at 393x852 inspect the data centre and press "Send one request".
Seen: "you (Amsterdam) -> POST /v1/messages 1" then a flush-left "200 tokens in"; the energy
grid breaks "312 000 tokens" the same way. Expected: horizontal scroll or a hanging indent.
File: `src/style.css:224`. Shot: `11/40-data-centre-phone-demo.png`.
Status: present on main, unchanged.

### B8 (15-12) Dimmed shelves cannot be undimmed on a touch screen - low, game-ui
Repro: pick one interest, open the Vault and the tech tree at 420 wide, tap a dimmed shelf.
Seen: ten shelves at opacity .45 with 11px description text; the only restore rules are
`:hover` and `:focus-within`. Expected: a tap restores it, or the dimming is lighter.
File: `src/style.css:288-289` with `:281`. Shot: `15/26-phone-tree.png`.
Status: present on main, unchanged.

---
