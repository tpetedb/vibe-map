# Security model

What the game and the CLI trust, what they do not, and the one helper each kind of value goes through. Read it before adding anything that draws text on the page or writes data into the build. Why there is no Content-Security-Policy behind all this: [ADR 0014](adr/0014-no-decorative-csp.md).

## The shape of the risk

The game is one HTML file built from strings: most panels are a template literal assigned to `innerHTML`, with inline `onclick` handlers. That is fast to write and it means a value that reaches such a template unescaped is markup. A hosted camp is a public page, and some of what it shows was written by strangers.

## Trusted: written by us, fixed at build time

Package data (`vibemap/data/`: the campaign, mentors, artifacts, items, pets, the tech tree and its notes), the modules in `src/`, and the theme and persona presets. These may carry HTML on purpose (`ws.html` in the campaign is a lesson). They reach the page raw, and every such use is counted in `tools/reviewed_sinks.json`.

A camp's own `config/camp.toml` and its own topic packs are trusted the way a person trusts their own typing: not hostile, but free text. So they must not be able to break the build or the page by accident, which is what `js_json()` and the template literal escaping are for.

## Not trusted: anything that arrives from somewhere else

| Source | How it arrives | Held by |
|---|---|---|
| A feed item (title, name, summary, link, date) | `vibe news` from public RSS and Atom, committed daily as `data/news.json`, baked into the game and fetched again as `./news.json` | the writer: `plain()` leaves no angle bracket, `safe_link()` keeps http and https with a host and encodes what would end a Markdown link or an attribute. The build: `js_json()`. The page: `esc()` and `safeUrl()` in `newsRow` |
| A progress code | pasted by the player from a mail or a chat | `progressFault()` in `80-sync.js`: every id is a `plainId()`, a path is `deep` or `skip`, and a code that fails is refused whole and by name before anything is merged |
| An answer from the chat bridge | streamed from a model over the loopback bridge | `esc()` in `renderChatLog`; the bridge itself takes questions only |
| The state in `localStorage` | written by an older build, by hand, or by an import before it learnt to refuse | the sinks escape on their own; `chatState()` re-checks the port and the pairing code |
| The player's name | typed, or imported | `textContent`, a canvas sprite, `esc()` in the note graph, `shq()` then `esc()` in the setup commands |
| A request to the bridge | any page in the browser can try | loopback bind, an Origin allowlist that refuses a missing Origin, a pairing code compared in constant time with a lockout after ten misses, a 16 KB body cap, a length that must be a plain number, JSON answers marked `nosniff` |

## One helper per sink

| The value goes into | Use | Never |
|---|---|---|
| HTML text or a double or single quoted attribute | `esc(value)` from `00-state.js` | a local replace, or a second escaper |
| An `href`, `window.open`, anything the browser will follow | `safeUrl(value)`, then `esc()` on the result; an empty answer means draw it without a link. The camp's repository goes through `repoUrl()` | a scheme check with `startsWith` |
| A text node | `textContent` | `innerHTML` with one value in it |
| An inline handler argument | an id that passed `plainId()`, or put the value in a `data-` attribute with `esc()` and read it from `this.dataset` | a value inside the handler's JavaScript string |
| A shell command shown to the player | `shq(value)`, then `esc()` | the bare value |
| The script element, at build time | `js_json(data)` in `tools/build.py` | `json.dumps` alone: it leaves a closing script tag and a comment opener as they are, and the HTML parser reads those before JavaScript does |
| A note as a JavaScript template literal | `_template_literal()` in `tools/regen_tree.py` | escaping the backtick only: a backslash and a dollar brace mean something too |
| HTML the CLI writes (the dashboard report) | `_esc()` in `vibemap/dashboard.py` | an f-string with the bare value |

Cut a string before you escape it, never after: a cut can land inside `&amp;`.

## The guards

- `uv run python tools/checks.py sinks` (also `just sinks-check`, and `tests/test_repo.py` runs it): every interpolation inside an HTML template in `src/game/` that is not wrapped in `esc()` or `icon()`, and every `innerHTML` or `insertAdjacentHTML`, is counted per module in `tools/reviewed_sinks.json`. A new one fails. Escape it; if it really is build-time data of ours, run the check with `--write` and say in the pull request why it is ours. `eval`, `new Function`, `document.write`, `outerHTML`, `srcdoc` and a timer given a string fail always.
- `tools/build.py` refuses to write a game whose script could end or swallow its own element.
- `tests/test_game_security.py` drives the hostile feed, the hostile bridge, the hostile progress code and a poisoned state through the real buttons, and records that the page talks to its own origin only.

## Known and accepted

- A page that is opened from `file://` sends the Origin `null`, and so does any sandboxed frame on any site, so the bridge's Origin check alone does not tell them apart. The pairing code is what does; a hostile page can spend the ten wrong guesses and lock the bridge until it is restarted, which is a nuisance and not a leak.
- Every project page of one GitHub account shares an origin, so they share `localStorage`. Another game under the same account can read and write this one's progress.
- The vault's Markdown renderer (`vrender` in `60-vault.js`) writes note text as HTML on purpose. Notes are package data. If notes ever come from a learner's vault at runtime, that renderer needs `esc()` on every line first.
