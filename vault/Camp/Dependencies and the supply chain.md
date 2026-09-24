---
title: "Dependencies and the supply chain"
date: 2026-09-24
tags: [tech, ship]
generated: 184b734da793
---
# Dependencies and the supply chain

Your software is also everything it depends on and everything that builds it: packages, base images and the actions in your CI. Keeping that supply chain safe means updating dependencies on a schedule instead of never, and pinning what your pipeline runs so it cannot change under you. Reach for this topic when you add a dependency, when you write a workflow that uses someone else's action, and when you set up a repository that will live longer than a weekend. And for an agent: pin a third-party action to a full-length commit SHA, and let Dependabot open the pull requests that move it, so every update goes through review and CI.

**History.** A Dependabot configuration lives in a dependabot.yml file that starts with version: 2 and lists, under updates, one entry per package-ecosystem, each with the directory of its manifest and a schedule.interval of daily, weekly, monthly, quarterly, semiannually, yearly or cron. Dependabot's supported ecosystems include github-actions, and uv with uv v0.11. GitHub's secure use reference says "pinning an action to a full-length commit SHA is currently the only way to use an action as an immutable release." Supply-chain Levels for Software Artifacts, SLSA, pronounced "salsa", "is a set of incrementally adoptable guidelines for supply chain security, established by industry consensus", useful to producers who follow it and to consumers deciding whether to trust a package. The Open Source Security Foundation, OpenSSF, was formed by the Linux Foundation on 3 August 2020 to improve the security of open source software, bringing together efforts that included GitHub's Open Source Security Coalition.

**Try in five minutes.** Write dependabot.yml with version: 2 and two updates entries: package-ecosystem "uv" and package-ecosystem "github-actions", both with directory "/" and schedule interval "weekly". In a real repository it goes at .github/dependabot.yml.

- Docs: [GitHub Docs, Dependabot options reference](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file), [GitHub Docs, Dependabot supported ecosystems and repositories](https://docs.github.com/en/code-security/dependabot/ecosystems-supported-by-dependabot/supported-ecosystems-and-repositories), [GitHub Docs, Secure use reference: pin actions to a full-length commit SHA](https://docs.github.com/en/actions/reference/security/secure-use), [SLSA v1.2, About SLSA](https://slsa.dev/spec/v1.2/about), [Source: OpenSSF, Technology and Enterprise Leaders Combine Efforts to Improve Open Source Security](https://openssf.org/press-release/2020/08/03/technology-and-enterprise-leaders-combine-efforts-to-improve-open-source-security/)
- Shelf: Ship and run · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #ship
