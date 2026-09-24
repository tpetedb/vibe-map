# Source

Issue #87 (Z5 Topic pack: software craft and delivery; it also absorbs the CI/CD and DevOps scope of #80): `gh issue view 87` and `gh issue view 80`. docs/TOPICS.md is how to write a topic and an origin; tools/new_topic.py scaffolds the pack; vibemap/data/topics/linux/ (from #190) and core/unix.toml are worked examples.

# What

A pack `craft`: testing in depth (the pyramid, pytest fixtures and parametrize, property-based testing with Hypothesis, test doubles), code review as a practice, refactoring and code smells, API design (HTTP RFCs, OpenAPI, versioning), authentication basics (OAuth 2.0 and OIDC from the RFCs), containers in depth (images, layers, multi-stage builds, compose), Kubernetes concepts only, Terraform or OpenTofu concepts with a local provider if the docs support one, observability with OpenTelemetry, licences and open source etiquette (choosealicense.com, SPDX), security basics for builders (OWASP Top 10, secrets, dependency updates). Existing topics (core: semver, changelog, docker, kubernetes, ci) are linked, not duplicated.

Content rule: written from each project's own official documentation fetched at writing time, every factual sentence traceable to a cited URL, versions and commands exactly as the docs give them, a date of check per topic, nothing from memory. Each topic: what it is and when to reach for it, the five-sentence model, the smallest real hands-on (offline, laptop, no cloud account, no paid service), a deterministic offline check, three to six sources, one primary origin at a place where the actor was at that date (docs/TOPICS.md rule; the-internet only when the event truly happened online, at most a quarter of primary origins). A wished-for place goes to issue #168 as a wish.
