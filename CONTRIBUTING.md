# Contributing

Thanks for looking. This is a course and a template: a single-file 3D browser
game, a terminal companion, a small data pipeline and an Obsidian vault. Keep
it small and readable. One file per concern; a dependency only when it removes
real work.

Agents that work here read [AGENTS.md](AGENTS.md). This page is the same rules
for a person, and the two must not drift: change one, change the other.

## Before you start

```bash
brew install just     # not required, but every task lives in the justfile
just setup            # uv, the Python env, Playwright browsers, the skills
just verify           # ruff, pytest with Playwright, the build check
```

`just` on its own lists every task. If `just verify` is green before you touch
anything, the machine is set up.

Open an issue before a big change, so nobody builds the same thing twice.
Small fixes can go straight to a pull request.

## The loop

1. Branch off `main`. Never commit to `main`; it only takes pull requests.
2. Write the test first where there is a behaviour to pin down. The game is
   tested through the built file with Playwright, in Chromium and WebKit;
   zero page errors is the bar.
3. While iterating, run the test closest to what you changed:
   `just test-one "tests/test_cli.py"` or `just smoke`.
4. `just verify` before every commit. All green or no pull request.
5. One changelog fragment per branch (see below).
6. Open a pull request against `main`. Both CI jobs green and the branch up to
   date with `main` before it can merge.

## Things this repository is strict about

- **Never hand-edit a generated file.** `game/vibe-map.html`,
  `tools/generated/`, `docs/ROADMAP.md`, `docs/RESOURCES.md`,
  `docs/OBSIDIAN.md`, `docs/COOKBOOK.md`, `vibemap/data/fork_source/`,
  `vibemap/data/template/_claude` and `_agents`, and the vault are written by
  a tool. Edit the source and run it: `just build` (the game), `just tree`
  (after a topic), `uv run python tools/sync_template.py`,
  `uv run python tools/sync_fork_source.py`, `uv run vibe vault build`. A test
  fails when one of them is out of date.
- **The game stays one file.** Three.js is embedded, there is no CDN and no
  build step beyond concatenation. Edit `src/`, run `just build`, test the
  built file. A test asserts the page never talks to anything but its own
  origin.
- **A changelog fragment, never `CHANGELOG.md`.** Add
  `changelog.d/<slug>.<type>.md`; the types are Keep a Changelog's `added`,
  `changed`, `deprecated`, `removed`, `fixed`, `security`. See
  [changelog.d/README.md](changelog.d/README.md). CI refuses a pull request
  that touches `src/`, `vibemap/` or `tools/` without one.
- **Scores are a system of record.** Never reset or rewrite
  `workspace/data/scores.csv` without asking.
- **No secrets.** Tokens go in `.env` (gitignored) or the keychain.

## House style

- No em dashes and no emoji, anywhere, including commit messages and pull
  request bodies. `uv run python tools/checks.py style` is the check.
- Python: `from __future__ import annotations`, frozen dataclasses or pydantic
  models, a `__main__` guard, `ruff format` at line length 88, basedpyright on
  basic, Python 3.12.
- SQL: lowercase keywords, one clause per line, a comment above the query
  saying which question it answers.
- HTML and JavaScript: no minification of our own code, comments where the
  logic is not obvious.
- Comments state constraints and why, in one or two lines. Never narrate a
  change ("replaced the old X"), never date a comment, never point at a line
  number in another file.
- State is data, the view is derived. Everything persisted lives in the game's
  `S` object or the CLI's `state.json`; the DOM, the 3D scene and the vault
  notes are rebuilt from it, never the other way round.
- Commit messages say what and why, in one line, in the imperative.

## Where things live

[docs/MAINTAINERS.md](docs/MAINTAINERS.md) is the map: the three zones (the
product, the template a camp starts from, the learner's workspace), how a
change travels between them, and what branch protection expects.
[docs/CONFIG.md](docs/CONFIG.md) is the table of which setting lives in which
of the three configuration levels. [AGENTS.md](AGENTS.md) has the file map.

## Reporting things

- A bug or an idea: open an issue; the forms ask for what a fix needs.
- A vulnerability: not in an issue. [SECURITY.md](SECURITY.md) has the private
  channel.
- Everyone here agrees to the [Code of Conduct](CODE_OF_CONDUCT.md).

By contributing you agree that your work is licensed under the
[MIT License](LICENSE), like the rest of the repository.
