> Cut from the hunt's triage of 2026-09-19. The `Shot:` names refer to that hunt's screenshots, which were not kept: reproduce each finding from its steps on current main before you touch anything, and take your own screenshots into `tests/out/`. Line numbers are from that day and will have moved.

## Batch S: the Ask panel and the chat bridge

### S1 (17-1) The pairing code appears only after a question has failed - medium, game-ui
Repro: press C on a fresh game and look for the code `docs/CHAT.md` tells you to pair with.
Seen: heading, context chip, suggestions, input; no code and no mention of a bridge. The code is
inside the card headed "No bridge answered". Expected: the code is visible when the panel opens.
File: `src/game/88-chat.js:72-80`, `chatHelp` at `:64-69`. Shot: `17/p1-01-ask-empty.png`.
Status: present on main, unchanged.

### S2 (17-2) There is no way to type the bridge's pairing code into the panel - medium, game-ui
Repro: run `vibe chat serve` with no `--pair`; it says to type its code into the panel. Look.
Seen: the help card offers a Port box only; `c.code` is never set from the UI.
Expected: a box for the bridge's code, or the CLI and `docs/CHAT.md` stop promising one.
File: `src/game/88-chat.js:68` against `vibemap/cli.py:1994-1996`.
Shot: `17/p13-01-long-question-clip.png`. Status: present on main, unchanged.

### S3 (17-3) Every refusal from a running bridge is "No bridge answered on port 7717" - medium, game-ui
Repro: pair the bridge with the wrong code, ask anything; repeat with a 4001-character question.
Seen: both print the three-line "start a bridge" card; a 401, a 400 and a 409 are all reported as
an absent bridge. Expected: name what the bridge refused, as `docs/CHAT.md` has a row per case.
File: `src/game/88-chat.js:112-115` with `:64-69`. Shot: `17/p4-01-wrong-code.png`.
Status: present on main, unchanged.

### S4 (17-4) A second question asked while an answer streams is erased in silence - medium, game-ui
Repro: ask a slow question, then type another and press Ask.
Seen: the input empties, nothing is logged, the status line still says "Asking your claude...";
`docs/CHAT.md` promises "a question is already being answered".
Expected: queue it, or say it is busy and keep the text.
File: `src/game/88-chat.js:82-83` with `:87`. Shot: `17/p3-01-busy-swallowed.png`.
Status: present on main, unchanged.

### S5 (17-5) A provider error is a dead end and wipes the answer that had streamed - medium, game-ui
Repro: run the bridge with no provider on PATH and ask; then with `--timeout 2` and a slow provider.
Seen: the install command is buried in the log, the status line is cleared, no fallback search
runs, and the streamed pieces are replaced by the error. Expected: keep what streamed and fall
back to the notes search, as the comment above the fallback promises.
File: `src/game/88-chat.js:104-115` with `vibemap/chat.py:411-417`. Shot: `17/p5-missing.png`.
Status: present on main, unchanged.

### S6 (17-7) The pairing code changes on every reload until the first question - medium, game-ui
Repro: press C, note the code, reload, press C again.
Seen: a different code; `chatState()` makes it without `save()`, so localStorage holds none until
a question is pushed. Expected: the code is written when it is generated.
File: `src/game/88-chat.js:12`. Shot: `17/p9-01-code-after-reload.png`.
Status: present on main, unchanged.

### S7 (17-14, 30-4 chatq half) The Ask panel has no labels, no live region and no busy state - medium, game-ui
Repro: press C and inspect `#chatq`, `#chatmsg`, `#chatlog` and the Ask button while streaming.
Seen: no label and no aria-label on the input, no aria-live anywhere, the Ask button enabled
during a stream, and offline vault links are `span` with an onclick.
Expected: a labelled field, a polite live region, a busy state and focusable links.
File: `src/game/88-chat.js:72-80`, input at `:77`. Shot: `17/p1-01-ask-empty.png`, `30/10-ask.png`.
Status: present on main, unchanged.

### S8 (17-9) "Try again" adds a duplicate question instead of retrying - low, game-ui
Repro: ask with no bridge, then click "Try again".
Seen: the history grows by one identical question per click, in a log capped at 20.
Expected: the retry replaces the failed entry. File: `src/game/88-chat.js:71` with `:88`.
Shot: `17/p4-02-try-again.png`. Status: present on main, unchanged.

### S9 (17-10) An invalid port is ignored in silence and the box keeps the bad number - low, game-ui
Repro: type 0, 99999, abc and -5 into the Port box, committing each.
Seen: `S.chat.port` stays 7717, the box keeps the bad value, nothing is said, and an accepted port
never updates the card's heading. Expected: a refusal says why; an accepted port re-renders.
File: `src/game/88-chat.js:70`. Shot: `17/p4-03-port-box.png`. Status: present on main.

### S10 (17-13) The panel says "your claude" where every other surface says "Claude Code" - low, content
Repro: pair the bridge and ask; read the status line and the provenance tag.
Seen: "Asking your claude..." and the tag "YOUR CLAUDE", the raw provider id, although `/health`
returns `"label": "Claude Code"`. Expected: the panel uses the label the bridge sends.
File: `src/game/88-chat.js:91` and `:61`, `vibemap/chat.py:406`. Shot: `17/p2-03-answered.png`.
Status: present on main, unchanged.

### S11 (17-15) The panel's own first suggestion cannot be answered offline - low, content
Repro: with no bridge, press C and click "What is this game for?".
Seen: three unrelated note passages; the word-overlap search has no note that answers it.
Expected: offer questions the embedded notes can answer, or say it cannot answer this one.
File: `src/game/88-chat.js:36` with `:43-55`. Shot: `17/p8-02-mentor-offline.png`.
Status: present on main, unchanged.

### S12 (17-6) A long question scrolls the chat log sideways instead of wrapping - medium, game-ui
Repro: paste 600 z's into the question box and press Enter.
Seen: `chatlog.scrollWidth` 4320 against `clientWidth` 634; every answer under it is pushed into a
horizontal scroll. Expected: the question wraps; neither line has `overflow-wrap:anywhere`.
File: `src/style.css:361` (`.chatlog .you`) and `:362` (`.chatlog .them`).
Shot: `17/p13-01-long-question-clip.png`. Status: present on main; the rules moved 353 to 361.

### S13 (17-11) The Port box is an unstyled white browser default - low, game-ui
Repro: press C, ask anything, look at the Port control on the dark card.
Seen: a white rectangle with black text; the stylesheet styles `input[type=text],textarea` only
and the port box is `input[type=number]`. Expected: it matches the question box.
File: `src/style.css:64` against `src/game/88-chat.js:68`. Shot: `17/p13-03-crop-help.png`.
Status: present on main, unchanged.

### S14 (22-7) The Ask panel clips its own input placeholder - low, game-ui
Repro: at 393x852 open More, Ask, and read the input beside the button.
Seen: 227 px of content box against 228 px of placeholder text, so the last letter is sliced.
Expected: the placeholder fits, or the row wraps at phone width.
File: `src/game/88-chat.js:77` (the inline `flex:1;min-width:160px`). Shot: `22/21-chat.png`.
Status: present on main, unchanged.

### S15 (17-8) An over-cap body is never drained, poisoning the connection - medium, cli
Repro: on one keep-alive socket send a 20000-byte POST to /ask, then a normal one.
Seen: 413, then "400 Bad request syntax" because the undelivered body was parsed as the next
request line. Every later question on that connection fails.
Expected: set `close_connection` or drain the socket after refusing.
File: `vibemap/chat.py:386-390` with `:305`. Shot: none. Status: present on main, unchanged.

### S16 (17-12) The answer is written for "Player: <your_name>" - medium, cli
Repro: `vibe new <dir>` with no `--name`, then `vibe chat ask "hello" --stop 1`.
Seen: the prompt's second line is "Player: <your_name>."; the name typed on the title screen never
reaches the bridge. Expected: leave the player unnamed while the camp holds the placeholder.
File: `vibemap/chat.py:191` with `vibemap/data/template/config/camp.toml:7`. Shot: none.
Status: present on main, unchanged.

### S17 (17-16, 28-12) `vibe chat ask` drops context arguments it cannot resolve - low, cli
Repro: `vibe chat ask "hi" --stop 99`, `--mentor Karpathy`, `--artifact bogus`.
Seen: each answers with the plain campus context line and no mention that the argument was
dropped, while `--world mars` is refused properly. Expected: refuse an unknown id, as
`vibe mentor Karpathy` already does. File: `vibemap/chat.py:121-138` and `:141-155`, reached from
`vibemap/cli.py:2023-2036`. Shot: none. Status: present on main, unchanged.

---
