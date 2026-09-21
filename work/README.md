# work/

How more than one agent works here at once without stepping on each other, and how anyone can tell that a task is done. The skill `work-order` is the how-to; `docs/adr/0016-work-orders.md` is the why.

| Path | What it is |
|---|---|
| `teams.toml` | The teams by theme and the paths each answers for. A path belongs to the first team that covers it. |
| `goals/<goal>.toml` | A goal: the sentence, what it leaves out, its orders. `just work-plan <goal>` turns it into launch groups. |
| `orders/<id>/order.toml` | One task: team, branch, the files it owns, criteria that are commands (`check`) or rulings (`judge`). |
| `orders/<id>/review.toml` | The ruling of someone who did not build it, tied to the commit they read. |
| `orders/<id>/signoff-<team>.toml` | Another team agreeing to a change in its files. |
| `orders/<id>/result.json` | What the last check measured. Not committed; good only for the exact tree it saw, and a convenience for the builder: `work-accept` measures again for itself. |
| `orders/<id>/touched.json` | Which agents edited under this order, written by the hook. Not committed. |
| `templates/` | Start from these. `just work-new <id> <team> "<title>"` writes an order. |

An order is active while its branch is checked out in some worktree, and landed once its accepting review is on `main`. One order, one branch, one pull request: `work-validate` names two orders that share a branch. Both are derived, nothing stores a status. `just work-new` writes a draft: it loads, and starts guarding, once `owns`, `builder` and a criterion are filled in. Someone else's draft in another worktree is named by `work-validate` and never fails it.

The checks, all in `tools/work.py`:

- `just work-validate`: every order is readable and no two active orders own the same file.
- `just work-check <id>`: nothing outside `owns` changed (generated files and the changelog fragment belong to anyone), then every criterion's command.
- `just work-accept <id>`: the checks, an accepted and still current review, every cross team's sign-off.
- In Claude Code, a hook refuses an edit outside the orders on the current branch. It lets go on anything it cannot read, so a broken or half-written order stays repairable; `work-check` refuses that order later anyway. The edit hook also notes which subagent worked on which order (`touched.json`, not committed, and not an agent's to write), and sends that subagent back once if it stops while the order fails: a builder to the checks, someone who only wrote into the order's folder to a readable review. A session is sent back only when its report's first line is `order: <id>`, because Stop fires at the end of every turn. This is a reminder for a cooperative agent, not the gate: an edit made through a shell is never seen by a hook. What decides whether work lands is `work-check`, `work-accept` and CI, and those fail closed.
- CI runs `work.py ci` on every pull request, after the tests so it can never hide a failing one. The orders a pull request carries are those whose folder it touches and those written for its branch. One that ships code ships its accepted review and every sign-off, so until the review lands that one step is red and everything else is green.

Orders that have landed are removed when a release is cut, like changelog fragments.
