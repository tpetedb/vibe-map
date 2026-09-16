---
name: changelog
description: Writes and updates CHANGELOG.md in Keep a Changelog 1.1.0 form (Unreleased on top, Added, Changed, Deprecated, Removed, Fixed, Security, ISO dates, compare links). Use when the user says "update the changelog", "add a changelog entry", "what changed since", "release notes", "cut a release", "move Unreleased to a version", or asks whether a change is Added, Changed or Fixed.
allowed-tools: Read Bash(git log *) Bash(git diff *)
---
# Changelog

A changelog tells a person what changed for them between two versions. It is not the git log. Guide: https://keepachangelog.com/en/1.1.0/

Rules:
- One `CHANGELOG.md` at the repo root, newest version first, `## [Unreleased]` at the top. Why: readers look in one place and see what is coming.
- Six headings only: Added, Changed, Deprecated, Removed, Fixed, Security. Leave out the empty ones. Why: the same kind of change is always in the same place.
- Write for the person using the repo, not the person who wrote the commit: what they can now do, what they must change. Never paste `git log`. Why: merge commits, typos and refactors are noise to them.
- Every released version gets `## [0.2.0] - 2026-09-16`, the date in ISO 8601. Why: 03/04 is a different day in Rotterdam and in Boston.
- Breaking changes, deprecations and removals are named as such in the entry. Why: the person upgrading must not learn it from a traceback.
- A pulled release stays in the file with `[YANKED]` after the date. Why: the people who installed it need to know.
- Every version heading is a link: compare URLs at the bottom of the file. Why: the diff is one click away.
- Add the Unreleased line in the same commit as the change. Why: now it takes a minute; in a month it takes an afternoon of git archaeology.
- Never rewrite a released section; correct it with a new entry. Say in the header that the project follows SemVer (the `semver` skill).
- Conventional Commits can generate this file from commit titles; this repo's commits are "what and why, one line" (AGENTS.md), so write the entry by hand and keep it human.

Template, the whole file:

```
# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- The thing a person can now do, in one line.

## [0.1.0] - 2026-09-16

### Added

- The first release.

[Unreleased]: https://github.com/tpetedb/vibe-map/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/tpetedb/vibe-map/releases/tag/v0.1.0
```

Cutting a release: rename `[Unreleased]` to the version and date, add an empty `## [Unreleased]` above it, and update the links (Unreleased compares from the new tag, the version compares from the previous one). `CHANGELOG.md` in this repo is the live example.

Sources:
- Keep a Changelog 1.1.0, Olivier Lacan: https://keepachangelog.com/en/1.1.0/
- Semantic Versioning 2.0.0: https://semver.org/spec/v2.0.0.html
- Tom's doc-doc ships the same discipline as a packaged skill (private repo): https://github.com/tpetedb/doc-doc
