---
title: "Semantic Versioning"
date: 2026-09-16
tags: [tech, castle]
---
# Semantic Versioning

A version number that makes a promise: MAJOR.MINOR.PATCH, where a MAJOR change breaks something, MINOR adds, PATCH fixes. Read one and you know whether an upgrade can hurt you; write one and you have to know what you changed. Before 1.0.0 anything may change, which is what this repo's 0.2.0 says out loud.

**History.** Tom Preston-Werner, cofounder of GitHub, wrote the spec. The 1.0.0 text dates from September 2011; 2.0.0, the version everyone links, was merged on 18 June 2013. It is written with the RFC 2119 keywords (MUST, SHOULD, MAY), so a version is something a tool can check, not a feeling.

**Try in five minutes.** uv run vibe --version, then open pyproject.toml and vibemap/__init__.py: the number lives in both. With the semver skill, decide what 0.3.0 would need.

- Docs: [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html), [Source: semver.org, About (authored by Tom Preston-Werner)](https://semver.org/), [Source: semver/semver, merge of release-2.0 (18 June 2013)](https://github.com/semver/semver/commit/7c834b3f3a4940d77ab593bc32583004d6a426a9), [Source: semver/semver, the commit tagged v1.0.0 (September 2011)](https://github.com/semver/semver/commit/ec80195ed310aab3ae1f1ce797b7ba88b4246d27)
- Unlocks: [[Changelogs (Keep a Changelog)]]
- Age: Castle Age · Level: Medior

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #castle
