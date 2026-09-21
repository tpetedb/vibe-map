> Cut from the hunt's triage of 2026-09-19. The `Shot:` names refer to that hunt's screenshots, which were not kept: reproduce each finding from its steps on current main before you touch anything, and take your own screenshots into `tests/out/`. Line numbers are from that day and will have moved.

## Batch Q: docs and generators

### Q1 (10-7, 11-7, 13-9) BRIEF and CHANGELOG count twenty artifacts - low, docs
Repro: read `docs/BRIEF.md:11` and `:78`, `CHANGELOG.md:29`, then count `__artifacts()` (21).
Seen: "twenty artifacts" in the present tense against `docs/SYLLABUS.md:468` ("twenty-one"),
the game and `vibe status` ("0/21 artifacts"). Expected: one number everywhere.
File: `docs/BRIEF.md:11`, `:78`; `CHANGELOG.md:29`. Shot: `11/11-switchboard-sheet.png`.
Status: present on main, unchanged.

### Q2 (15-6) `docs/ROADMAP.md` renders no headings - medium, docs
Repro: `grep -c '^### ' docs/ROADMAP.md`.
Seen: 0. Line 9 is `*Basics.* ### Unix and the terminal`, line 121 `*Basics.* ### Git`; the
depth label is written with no trailing newline before the heading.
Expected: each topic is its own `### <name>` heading.
File: `tools/regen_tree.py:108`. Shot: none. Status: present on main and still 0 headings
after the topics-as-data move.

### Q3 (15-1) Tree topics Git and Python open a stub note - medium, content
Repro: open the Vault, Tech tree, click Git, then Python.
Seen: a 300-odd character concept stub, because the generated `"Git":{t:"git"}` at
`game/vibe-map.html:2679` is overwritten by `"Git":{t:"c"}` at `:3334` from
`src/game/50-notes.js`; same for Python. Expected: the tree opens the topic note.
File: `tools/regen_tree.py:30` (`EXIST` lists only agentsmd, skills, hooks, mcp, vault).
Shot: `15/08-tree.png`. Status: present on main; both duplicate keys are still in the built
game after #101.

### Q4 (02-14) `scores.py` tells you to run it from a path that does not exist - low, docs
Repro: open `workspace/python/scores.py` and read the docstring.
Seen: "Run: python3 python/scores.py"; every other reference uses `workspace/python/scores.py`.
Expected: the working path. File: `workspace/python/scores.py:5`. Shot: none.
Status: present on main, unchanged.

# Note
`CHANGELOG.md` is never edited on a branch. The wrong count in the 0.10.0 section is fixed by the release that follows; say so in the pull request and leave the file alone.
