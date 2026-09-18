# changelog.d

One file per change, so two branches never conflict over `CHANGELOG.md`.

- Name it `<slug>.<type>.md`. The type is one of `added`, `changed`,
  `deprecated`, `removed`, `fixed`, `security` (Keep a Changelog 1.1.0).
- The content is one or more Markdown bullets, written for the person using
  this repository: what they can now do, what they must change.
- Add it in the same commit as the change. CI refuses a pull request that
  touches `src/`, `vibemap/` or `tools/` without one.
- Never edit `CHANGELOG.md` on a branch; a release writes it.

```
uv run python tools/changelog.py draft          # the Unreleased view
uv run python tools/changelog.py release 1.0.0  # cut it, delete these files
```
