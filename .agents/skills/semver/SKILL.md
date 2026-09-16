---
name: semver
description: Picks the next version number with Semantic Versioning 2.0.0 (MAJOR.MINOR.PATCH) and bumps it in pyproject.toml, grimoire/__init__.py and a git tag. Use when the user says "bump the version", "what version is this", "is this a breaking change", "cut a release", "release 0.3.0", "tag it", or asks what major, minor, patch, 0.x or a pre-release like 1.0.0-rc.1 means.
allowed-tools: Read Bash(uv run grimoire --version) Bash(git tag -l *)
---
# Semantic Versioning

A version number is a promise about compatibility and nothing else. Spec: https://semver.org/spec/v2.0.0.html

Rules:
- MAJOR.MINOR.PATCH. Bump MAJOR for a change that breaks what people rely on, MINOR for a backward-compatible addition, PATCH for a backward-compatible fix. Why: the number alone tells a reader whether an upgrade can hurt.
- Reset the lower parts on a bump: 0.2.3 plus a feature is 0.3.0, not 0.3.3. Why: the number is a statement, not a counter.
- Decide the bump from the effect on the user, not the size of the diff. A one-line change to the CLI's output breaks every script that parses it.
- Before 1.0.0 anything may change (spec, rule 4). This repo is 0.2.0: features bump MINOR, fixes bump PATCH, nobody promises stability yet. Why: honest about what early means.
- A pre-release is `1.0.0-rc.1` and sorts before `1.0.0`; build metadata is `1.0.0+abc123` and is ignored for ordering.
- A released version is final. Found a mistake? Release the next number. Why: one number names exactly one thing, forever.
- The number lives in two places here, `pyproject.toml` and `grimoire/__init__.py`, and they must agree. Tag the commit `v0.3.0` so git and `CHANGELOG.md` say the same thing.
- Conventional Commits (`feat:`, `fix:`, `feat!:`) can compute the bump from commit titles, but this repo's rule is "what and why, one line" (AGENTS.md, Git), so read the Unreleased section of `CHANGELOG.md` to decide. Either works; do not mix them in one repo.
- The changelog entry comes first, the bump second (the `changelog` skill). Why: you cannot pick the number before you know what changed.

Template, the release checklist:

```
1. uv run grimoire --version                       what we have now
2. Read CHANGELOG.md, section [Unreleased]:
     Removed, or a Changed that breaks something  -> MAJOR (MINOR while 0.y.z)
     Added                                         -> MINOR
     only Fixed                                    -> PATCH
3. Set the number in pyproject.toml and grimoire/__init__.py
4. Rename [Unreleased] to [0.3.0] - YYYY-MM-DD and fix the links at the bottom
5. uv run grimoire --version prints 0.3.0; commit "Release 0.3.0: <why>"
6. git tag -a v0.3.0 -m "0.3.0"; push the tag with the commit
```

Sources:
- Semantic Versioning 2.0.0, Tom Preston-Werner: https://semver.org/spec/v2.0.0.html
- Keep a Changelog 1.1.0 (the changelog names the SemVer promise): https://keepachangelog.com/en/1.1.0/
- The commit rule: `AGENTS.md`, section Git, in this repo
