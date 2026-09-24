# Docs team review: galaxy-places-more

Reviewed on 2026-09-22 by `codex-places-docs-manager`, independently of the builder. Scope: `docs/TOPICS.md` and the related `AGENTS.md` registry description. This is preliminary cross-team evidence, not a signed approval or the work-order acceptance ruling.

## Resolved finding

**Resolved, previously medium: current city association does not establish a historical event location.** The initially reviewed origin-source rule in `docs/TOPICS.md` permits the town to come from a place file's own source, but its warning about current addresses only excludes the building or exact address. The review checklist repeats the permissive town rule. A company can move between cities. A current mailing address or job listing cannot establish where an earlier release, invention or research event occurred.

The surrounding contract remains explicitly historical: `docs/GALAXY.md` says that a topic must sit where it actually happened in history; `vibemap/places.py`, the build's `PLACES` data and `vibe places` retain the same meaning. The independent `source-review.md` correctly says that modern mailing addresses and job listings support only city association, not an earlier technology's development site. Allowing those associations to locate historical events would contradict that limitation.

Proposed replacement for the new source paragraph:

> The source is https, it was opened while writing, and the page says what the line says: the year, the actor and what happened. A separate place source may establish the town only when it supports that actor's location for the relevant historical event or period. A current contact address or job listing does not establish the town, building or exact address of an earlier event. Naming an organisation as the actor does not by itself establish a physical event location. If the sources do not support that historical attribution, record the gap or use an appropriate abstract place.

Proposed checklist wording:

> Exactly one origin is primary, its place exists, and every origin's source was opened and says the year, actor and event it claims. Any physical town attribution is supported for the relevant historical event or period by that page or the place file's own source.

The builder should also assess existing origin references to current-location-only place records against this distinction. That follow-up is outside this docs-only review; this report makes no finding about any particular topic's final origin.

The requirement was posted through `just work-say galaxy-places-more manager:docs` on issue #168. The orchestrator agreed that the historical town distinction must be explicit. The clarification was independently reread in the working tree on 2026-09-22 and resolves the docs finding. Both the rule and checklist now require support at the relevant historical date. The rule explicitly excludes inferring an earlier event's town, building or exact address from a current contact address, and permits an abstract place only when the event source supports it. No unresolved docs wording finding remains.

This correction does not certify the historical locations assigned by the topic origins. That content audit remains separate and outstanding. The docs sign-off file still waits for a committed checkpoint and completed content evidence; no sign-off or full acceptance is issued here.

## Verified without findings

- The added strict integer year and duplicate-place documentation matches `Origin.year: StrictInt` and `_check_origins()` in `vibemap/topics.py`. Missing origins remain allowed during migration; the existing primary-origin validation applies when origins are present.
- The registry description matches one TOML file per place, referenced by topic origin ids, loaded by `vibemap/places.py` and serialized through the build's `PLACES` payload. `AGENTS.md` remains subject to the harness manager's own sign-off.
- `generic-marker` clearly makes no physical landmark claim. Fictional `look` kits are distinguished from evidence. The ban on copying buildings, organisation marks or products matches ADR 0010.
- The work-order ownership instructions prevent topic builders from editing unowned registry files. The order correctly declares `cross = ["cli", "docs", "harness"]`.
- Existing regeneration instructions still distinguish editable topic/place data from generated files. This order does not replace them with instructions to hand-edit generated output.
- `git diff --check -- docs/TOPICS.md AGENTS.md` passed. No browser or full-suite execution was performed for this docs review.

## Snapshot

Working-tree review based on HEAD `25f0994a5537775e33e21c755721e15f2a0e2c75`, before an implementation commit. Exact file hashes after the correction review:

- `docs/TOPICS.md`: SHA-256 `18f451cba7ebd51b3e3dde001ce508b32c6a2cf328065fea71097f1918a896f5`.
- `AGENTS.md`: SHA-256 `dadb7f257a2ed4ea0359390be5cb24fb45901d4a33ffcccaddb38afbcd786aeb`.
