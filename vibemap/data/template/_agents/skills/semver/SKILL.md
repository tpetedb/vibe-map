---
name: semver
description: Picks the next version number with Semantic Versioning 2.0.0 (MAJOR.MINOR.PATCH) and bumps it in pyproject.toml and a git tag. Use when the user says "bump the version", "what version is this", "is this a breaking change", "cut a release", "release 0.3.0", "tag it", or asks what major, minor, patch, 0.x or a pre-release like 1.0.0-rc.1 means.
allowed-tools: Read Bash(uv run vibe --version) Bash(git tag -l *)
---
# Semantic Versioning

A version number is a promise about compatibility and nothing else. Spec: https://semver.org/spec/v2.0.0.html

Rules:
- MAJOR.MINOR.PATCH. Bump MAJOR for a change that breaks what people rely on, MINOR for a backward-compatible addition, PATCH for a backward-compatible fix. Why: the number alone tells a reader whether an upgrade can hurt.
- Reset the lower parts on a bump: 0.2.3 plus a feature is 0.3.0, not 0.3.3. Why: the number is a statement, not a counter.
- Decide the bump from the effect on the user, not the size of the diff. A one-line change to the CLI's output breaks every script that parses it.
- Before 1.0.0 anything may change (spec, rule 4). This repo is still on 0.y.z: features bump MINOR, fixes bump PATCH, nobody promises stability yet. Why: honest about what early means. `uv run vibe --version` prints the number it is on now; never quote one from memory.
- A pre-release is `1.0.0-rc.1` and sorts before `1.0.0`; build metadata is `1.0.0+abc123` and is ignored for ordering.
- A released version is final. Found a mistake? Release the next number. Why: one number names exactly one thing, forever.
- One source: `pyproject.toml`. `vibemap/__init__.py` reads the installed metadata (`importlib.metadata.version`) and only its uninstalled fallback pin is written by hand, so there is nothing to keep in agreement. Tag the commit `vX.Y.Z` so git and `CHANGELOG.md` say the same thing.
- Conventional Commits (`feat:`, `fix:`, `feat!:`) can compute the bump from commit titles, but this repo's rule is "what and why, one line" (AGENTS.md, Git), so read the Unreleased section of `CHANGELOG.md` to decide. Either works; do not mix them in one repo.
- The changelog entry comes first, the bump second (the `changelog` skill). Why: you cannot pick the number before you know what changed. In this repository a branch adds a fragment to `changelog.d/` and the release assembles them; `CHANGELOG.md` is never edited by hand.

Template, the release checklist:

```
1. uv run vibe --version                       what we have now
2. Read the pending fragments (just changelog, or changelog.d/):
     Removed, or a Changed that breaks something  -> MAJOR (MINOR while 0.y.z)
     Added                                         -> MINOR
     only Fixed                                    -> PATCH
3. Set the number in pyproject.toml, and the fallback pin in vibemap/__init__.py
4. just release X.Y.Z                          writes the dated section and the links
5. uv run vibe --version prints X.Y.Z; commit "Release X.Y.Z: <why>"
6. git tag -a vX.Y.Z -m "X.Y.Z"; push the tag with the commit
```

Sources:
- Semantic Versioning 2.0.0, Tom Preston-Werner: https://semver.org/spec/v2.0.0.html
- Keep a Changelog 1.1.0 (the changelog names the SemVer promise): https://keepachangelog.com/en/1.1.0/
- The commit rule: `AGENTS.md`, section Git, in this repo
