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
- Add the entry in the same commit as the change. Why: now it takes a minute; in a month it takes an afternoon of git archaeology.
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

Cutting a release by hand: rename `[Unreleased]` to the version and date, add an empty `## [Unreleased]` above it, and update the links (Unreleased compares from the new tag, the version compares from the previous one).

## Fragments, when several branches are open at once

Two branches that both add a line under `## [Unreleased]` conflict on the same three lines every time, and the conflict is never interesting: both sides want to be kept. So a repository with parallel work writes the entry to its own file instead, and assembles the section at release time. With one branch at a time, as in your camp, editing `CHANGELOG.md` directly is fine and this section is what to reach for when that stops being true. The vibe-map repository does it like this:

- A branch adds `changelog.d/<slug>.<type>.md`, where the type is one of the six headings in lower case, and the content is the bullets that would have gone into that heading. It never edits `CHANGELOG.md`.
- `uv run python tools/changelog.py draft` prints what Unreleased would say today (`just changelog`).
- `uv run python tools/changelog.py release X.Y.Z` writes the dated section, moves the compare links and deletes the fragments (`just release X.Y.Z`). That is the one commit that edits `CHANGELOG.md`.
- `uv run python tools/changelog.py check --base origin/main` exits 1 when a diff changes `src/`, `vibemap/` or `tools/` without a fragment. CI runs it on every pull request.

`CHANGELOG.md` stays the published file in Keep a Changelog form; the fragments are only how the next section is written. The same idea packaged as a tool is towncrier, which is worth knowing about but is not what this repository uses: its release notes are assembled at a `start_string` marker and it has no notion of the compare-link block at the bottom of a Keep a Changelog file, so following its conventions would mean templating the format back by hand for a file we can write in one screen of Python.

Sources for the fragment idea:
- towncrier configuration (`start_string`, `title_format`, custom types): https://towncrier.readthedocs.io/en/stable/configuration.html

Sources:
- Keep a Changelog 1.1.0, Olivier Lacan: https://keepachangelog.com/en/1.1.0/
- Semantic Versioning 2.0.0: https://semver.org/spec/v2.0.0.html
- Tom's doc-doc ships the same discipline as a packaged skill (private repo): https://github.com/tpetedb/doc-doc
