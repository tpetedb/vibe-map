> Cut from the hunt's triage of 2026-09-19. The `Shot:` names refer to that hunt's screenshots, which were not kept: reproduce each finding from its steps on current main before you touch anything, and take your own screenshots into `tests/out/`. Line numbers are from that day and will have moved.

## Batch K: lesson copy and island wording

### K1 (02-6) The stop 2 playbook the learner writes is never saved - medium, game-ui
Repro: open campus stop 2, type into "Your first playbook", reload, resume, reopen stop 2.
Seen: the textarea is back to the shipped default and the text never reaches `__S()`, while the
stop 1 pitch box does persist. Expected: persist it like `S.pitch`, or stop calling it the
standing procedure. File: `src/body.html:184` against `src/game/70-minigames.js:10`.
Shot: `02/a9-playbook-after-reload.png`. Status: present on main, unchanged.

### K2 (03-5) Workstream 6 promises a draggable graph above an inert one - medium, content
Repro: open workstream 6 and try to drag or tap a node in the SVG under the card.
Seen: "Drag nodes, tap one to read it" above an SVG with zero pointer handlers.
Expected: the copy points at the real graph one button away.
File: `src/body.html:408` with `src/game/70-minigames.js:87`. Shot: `03/11-ws6-graph.png`.
Status: present on main. The verifier calls it largely a known gap; fix the sentence, not the SVG.

### K3 (03-11) A raw wikilink `[[Git]]` is printed in workstream 7 - low, content
Repro: open workstream 7 and read the Concept paragraph.
Seen: "a copy of your [[Git]] history"; the sheet does not render wikilinks, and Obsidian is
only introduced in workstream 6. Expected: a plain word or a real link.
File: `src/body.html:444`. Shot: `03/14-ws7-top.png`. Status: present on main.

### K4 (03-13) Workstream 7 still refers to the Roquefort after the theme rewrote the pairing - low, content
Repro: on the default studio theme open workstream 7 and compare the pairing block with the
paragraph. Seen: "COFFEE, 22:30 / Sparkling water" above "... including the Roquefort"; the
same pattern at `src/body.html:514` ("Rolinda is available for wine").
Expected: wine prose moves into the block the theme rewrites.
File: `src/body.html:443`. Shot: `03/14-ws7-top.png`. Status: present on main.

### K5 (02-8) The stop 2 lesson teaches a SKILL.md without a name - medium, content
Repro: open campus stop 2, read "Concept 3: skills", then run `vibe check 2`.
Seen: the pasted frontmatter is `description:` only, while the card says a skill has "name,
description, instructions" and `_c2_skill` requires both keys.
Expected: the lesson's skill carries `name:` and lives where the check looks.
File: `src/body.html:223` against `vibemap/quests.py:192`. Shot: `02/32-sheet-2-top.png`.
Status: present on main, unchanged.

### K6 (02-9) The stop 4 hook example backs up a file that does not exist - low, content
Repro: open campus stop 4, copy the hook block, follow step 4 and look in `backups/`.
Seen: `cp scores.csv backups/...` while every other place uses `workspace/data/scores.csv`, and
the copy promises "A copy appeared". Expected: the path the template hook uses.
File: `src/body.html:332`. Shot: `02/d-desktop-stop4-scrolled.png`. Status: present on main.

### K7 (02-15) The stop 2 definition of done does not match its check - low, content
Repro: read the "Definition of done" callout in campus stop 2, then `quest_for('campus', 2)`.
Seen: the callout never mentions AGENTS.md, which the first check requires.
Expected: the definition of done names what the check verifies. Note: the reported stop 4 half
did not reproduce. File: `src/body.html:238` against `vibemap/quests.py:599`.
Shot: `02/d-desktop-stop4-scrolled.png`. Status: present on main.

### K8 (04-12, 05-9, 06-11) Panels say "Back to the campus" on every island - low, content
Repro: on winter, the desert or prod open the Roadmap, Settings and the Vault, read the last
button of each. Seen: "Back to the campus" and "Back to campus" while the stop screens on the
same island say "Back to the island". Expected: neutral wording.
File: `src/body.html` (11 occurrences, including `:54` and `:87`) and
`src/game/85-settings.js:36`. Shot: `06/50-roadmap-prod.png`. Status: present on main.

---

### Handed on from batch P (pull request 142)
- Desert stop 3 still opens with `uv pip install pytest ruff`, which needs something a camp lacks.
- `src/body.html` claims the template ships `scores.csv`, three SQL files and a Python script.
