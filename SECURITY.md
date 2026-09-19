# Security policy

## Supported versions

The latest release is the supported one. Fixes land on `main` and ship in the
next release; older tags are not patched.

| Version | Supported |
|---|---|
| The latest release (see [Releases](https://github.com/tpetedb/vibe-map/releases)) | yes |
| Anything older | no |

## Reporting a vulnerability

Report privately, not in a public issue. Open
[Security, Report a vulnerability](https://github.com/tpetedb/vibe-map/security/advisories/new)
on this repository: that form is a private advisory only the maintainer can
read, and it is the one channel for this. If the form is not available to you,
open an issue titled `security` that says a report is waiting and nothing else,
and you will be invited to the private advisory.

What helps: the version (`vibe --version`), what an attacker gains, and the
smallest way to see it happen. Expect an acknowledgement within a week and a
fix or a plan within a month. Please give the fix time to ship before writing
about it in public.

## What is in scope

This repository is a browser game, a terminal companion and a local HTTP
bridge. The parts worth looking at:

- **The chat bridge** (`vibemap/chat.py`): a loopback HTTP server the game's
  Ask panel talks to, with an Origin allowlist and a pairing code. The design
  and its limits are in [docs/adr/0009-local-chat-bridge.md](docs/adr/0009-local-chat-bridge.md).
- **The game as a page** (`src/`, built into `game/vibe-map.html`): anything
  that arrives from outside the build is content, never markup. That is the
  news feed, an answer from the bridge and an imported progress code.
- **The CLI** (`vibemap/`): what it reads and writes in a camp, and the
  commands it runs on the learner's behalf.

Out of scope: a vulnerability in a vendored third party (`src/vendor/`) that
upstream already knows about, and anything that needs an attacker who is
already running code on the learner's machine.

## What the product promises

- The game is one file with three.js embedded and no CDN. It makes no
  third-party request, and a test proves it on every pull request.
- No secrets in the repository. Tokens live in `.env` (gitignored) or the
  keychain.
- The bridge listens on loopback only and refuses a request whose Origin it
  does not know, including a request with no Origin at all.
