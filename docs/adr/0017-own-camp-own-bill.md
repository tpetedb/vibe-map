# ADR 0017: A camp and its bill belong to the learner

Status: Accepted, 2026-09-22

## Context

A camp contains a learner's notes, scores, settings and work. It may be public
or private, and the learner may want a history unrelated to the product's
history. A fork keeps a network relationship with its upstream repository and
a public fork cannot be made private, so it is the wrong default for personal
course work. Forks remain useful for contributing to the product and for the
course's in-game fork challenges.

The hosted game, checks and vault do not need a paid model. Features that ask a
model run a provider CLI on the learner's machine through the local bridge in
ADR 0009. Codespaces compute is charged to the account that owns the
codespace. Codespaces prebuilds and Git LFS bandwidth are different: other
people's use can consume resources charged to the repository owner. The
research and sources for these constraints are in
`docs/RESEARCH/2026-09-18-ownership-costs-providers.md`.

GitHub's documentation describes the files and history created from a template
but does not establish whether a generated repository can itself be marked as
a template. The course cannot promise behavior its source does not support.

## Decision

We will start a learner with `vibe new`, which creates a local camp and git
history, or with **Use this template**, which creates the learner's own
repository with an unrelated history and their visibility choice. We will not
start the learner in a Codespace on the product repository. A learner who wants
Codespaces creates their own repository first and opens the Codespace there.

The hosted game will make no paid provider call and carry no provider key. The
chat bridge will run only the learner's own provider CLI. Product and template
workflows will carry no model credential or paid model action. They will not
use `pull_request_target` or workflow secrets. The repository will use no Git
LFS. A static test will guard these checked-in constraints.

Codespaces prebuild configuration lives in the repository's remote settings,
outside the committed tree. This repository will keep that setting disabled.
The static test cannot prove it. A maintainer with admin access must verify
that **Settings, Codespaces, Prebuild configuration** lists no configuration
when this decision is reviewed or released.

The game, checks and vault are the free route. A coding agent uses the
learner's own subscription or free provider allowance. A Codespace uses the
learner's own account and its included allowance before any paid usage. Every
starting path will say who owns the repository and the bill and will point to
a zero product-level Codespaces budget. Where GitHub offers it, the learner
must select **Stop usage when budget limit is reached**. The budget must be
created before setup: GitHub excludes usage from before its creation during
the first billing cycle.

## Consequences

- A learner's notes, scores, visibility and history stay under their control.
- No normal learner action can spend this project's owner's model or
  Codespaces allowance.
- A learner has one extra step before Codespaces: create their own repository.
- Paid provider and Codespaces features remain available, but the learner
  chooses and pays for them on their own account.
- A future workflow that needs a secret, model action or Git LFS must first
  replace this decision and its regression test with an equally explicit cost
  boundary. A future prebuild requires the same decision change and a remote
  settings review.
- A learner may try marking their camp as a template in repository settings,
  but the course does not promise that GitHub supports it.
