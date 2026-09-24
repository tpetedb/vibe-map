# Issue 91 evidence

Checked against `origin/main` at `6514a4e`. PR 98 supplied the ownership and cost research, PR 97 added the current Codespaces setup, and PR 130 added the README's first-screen wording.

The repository already says that the learner brings their own subscription and pays for their own usage in `README.md`, and the camp template README explains that a Codespace belongs to the learner's account, names a zero spending limit and says no prebuild is configured. ADR 0009 already fixes the chat architecture: the browser carries no provider key and the bridge runs the learner's own CLI.

The remaining contract is incomplete. There is no ownership ADR, LONG-GAME does not state who owns the repository and bill, and QUICKSTART still gives `gh codespace create --repo tpetedb/vibe-map`. `tests/test_repo.py` has no regression guard for Git LFS, paid model workflows, workflow secrets or `pull_request_target`. The current tree has none of those hazards, so the new test protects an existing safe state.

Review on 2026-09-22 corrected the prebuild boundary. GitHub's current
[prebuild configuration documentation](https://docs.github.com/en/codespaces/prebuilding-your-codespaces/configuring-prebuilds)
says a created configuration appears on the Codespaces page in repository
settings. It is remote state, not a committed workflow declaration, so a
static repository test cannot prove that prebuilds are disabled. The reviewer
must inspect **Settings, Codespaces, Prebuild configuration** with repository
admin access. The static test remains responsible only for committed workflows
and Git LFS attributes.

GitHub's current [workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
documents both named secret expressions and `secrets: inherit`, which passes
all secrets available to a calling workflow. The guard therefore walks YAML
keys and expressions, including `toJSON(secrets)`, while checking paid provider
names only in `uses:` action references. Provider names in workflow prose are
not automation and must remain valid.

GitHub's current [budget setup documentation](https://docs.github.com/en/billing/how-tos/set-up-budgets)
uses the option name **Stop usage when budget limit is reached** and says
personal user-level budgets always enforce a hard stop. It also names
Codespaces as a product-level budget choice. The related
[budgets and alerts documentation](https://docs.github.com/en/billing/concepts/budgets-and-alerts)
adds that a new budget counts usage only from its creation date. Usage from
earlier in the first billing cycle is excluded, so the course must tell a
learner to create the zero budget before Codespaces setup rather than promise a
retroactive cap.

ADR 0011 is no longer available: `docs/adr/README.md` reserves 0011 and 0012 permanently and names 0017 as the next number. This order therefore records the decision as ADR 0017. GitHub's researched documentation does not establish that a repository generated from a template can itself be marked as a template, so the docs must not promise that behavior.

The title-screen prerequisite and ownership line remains part of issue 92, where provider capabilities and free routes become data. The fully online choice and its persisted local/Codespaces mode remain part of issue 82. This order must not edit onboarding or configuration for either dependency.

## Remote setting check

On 2026-09-22 an administrator opened **Settings, Codespaces, Prebuild
configuration** for `tpetedb/vibe-map`. GitHub displayed **There are no
prebuilds configured for this repository** and only the **Set up prebuild**
action. This is the external evidence for criterion c4; it cannot be inferred
from a checkout.
