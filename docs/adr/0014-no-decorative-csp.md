# ADR 0014: No Content-Security-Policy until it can block an injected script

Status: Accepted, 2026-09-19

## Context

Feed content reached `innerHTML` raw and ran script in every player's browser (fixed in #120; the second look found the same through a pasted progress code and through the build). A Content-Security-Policy is the usual second line behind escaping, so we asked whether the built game should carry one in a `<meta http-equiv>` tag, which is the only place a single file opened from `file://` or served by GitHub Pages can put it.

What a policy has to allow for this game to keep working:

- Five inline `<script>` elements (the error trap, three.js, Motion, d3-force, the game). `tools/build.py` could hash each one and write `script-src 'sha256-...'`, so this part is solvable.
- 105 inline event handlers (`onclick="openCh(3)"`) in `src/body.html` and in the HTML the modules render. Hashes and nonces do not apply to event handlers. The only way to keep them is `'unsafe-hashes'` with one hash per distinct handler text, and the handlers are generated with values in them (`claim(${n})`, `openMentor('${m.id}')`), or `'unsafe-inline'`. Source: MDN, script-src, "Hashes apply to inline scripts and styles, but not event handlers" (https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/script-src).
- 45 inline `style=""` attributes, which need `style-src 'unsafe-inline'` the same way.

With `'unsafe-inline'` in `script-src`, the payload that started all this, `<img src=x onerror=...>`, still runs. What is left of the policy is an egress limit (`connect-src 'self' http://127.0.0.1:*`, `img-src 'self' data: blob:`, `form-action 'none'`, `base-uri 'none'`), and a script that already runs gets round that by navigating the page, which no directive a browser ships can forbid.

## Decision

The game ships no Content-Security-Policy for now. A policy that cannot stop an injected script is decoration, and a header people read as protection is worse than none.

The defences that do hold are the ones in `docs/SECURITY-MODEL.md`: one escaper at every sink, `safeUrl()` for every link, `js_json()` for everything the build writes into the script element, a progress code that is validated before it is merged, and the register in `tools/reviewed_sinks.json` that fails the battery when a new raw value reaches HTML. The promise that the page talks to its own origin only is kept by a browser test (`tests/test_game_security.py`), not by a header.

## Consequences

- Escaping stays the only line of defence in the page, so the sink guard is not optional and a register update is a review, not a formality.
- The way to a policy that matters is known and can be walked in steps: replace the inline handlers with one delegated listener reading `data-act` attributes, move the inline styles into classes, then let `tools/build.py` hash the five script elements and write `default-src 'none'; script-src 'sha256-...'; style-src 'sha256-...'; img-src 'self' data: blob:; connect-src 'self' http://127.0.0.1:* http://localhost:*; base-uri 'none'; form-action 'none'` into `src/head.html`. At that point this record is superseded.
- Two things to check when that day comes: the browser test helper `STILL` in `tests/conftest.py` uses `new Function`, which a policy without `'unsafe-eval'` refuses, and WebKit on `file://` has to be tried with `'self'`, since a file has an opaque origin.
