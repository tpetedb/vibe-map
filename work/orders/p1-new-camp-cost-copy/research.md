# Issue 91 evidence

Checked against `origin/main` at `6514a4e`. The main README already says that the learner brings their own coding-agent subscription and pays for their own usage. The template README already says that the camp and its Codespace belong to the learner, identifies the free allowance and names a zero spending limit.

Two learner-facing entry points remain incomplete. The closing message at `vibemap/cli.py` only prints the next three commands after `camp ready`; it says nothing about repository ownership, subscriptions or billing. `vibemap/data/template/AGENTS.md` calls the camp the learner's workspace and forbids secrets in git, but it does not tell an agent that model and Codespaces usage belong to the learner's account. Focused tests belong in `tests/test_onboarding.py`, which already covers `vibe new` and the template it writes.

The researched GitHub pages do not establish that a repository generated from a template can itself be marked as a template. The copy must not promise that behavior. The ownership decision itself is recorded by the sibling docs order as ADR 0017 because 0011 and 0012 are permanently reserved.

The title-screen prerequisite and ownership line remains part of issue 92, where the provider matrix and free routes are implemented. The fully online choice and its configuration remain part of issue 82. This order must not edit the browser onboarding, providers or journey configuration.
