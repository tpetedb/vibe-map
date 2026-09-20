# work/

How more than one agent works here at once without stepping on each other, and how anyone can tell that a task is done. The skill `work-order` is the how-to; `docs/adr/0016-work-orders.md` is the why.

| Path | What it is |
|---|---|
| `teams.toml` | The teams by theme and the paths each answers for. A path belongs to the first team that covers it. |
| `goals/<goal>.toml` | A goal: the sentence, what it leaves out, its orders. `just work-plan <goal>` turns it into launch groups. |
| `orders/<id>/order.toml` | One task: team, branch, the files it owns, criteria that are commands (`check`) or rulings (`judge`). |
| `orders/<id>/review.toml` | The ruling of someone who did not build it, tied to the commit they read. |
| `orders/<id>/signoff-<team>.toml` | Another team agreeing to a change in its files. |
| `orders/<id>/result.json` | What the last check measured. Not committed; good only for the exact tree it saw. |
| `templates/` | Start from these. `just work-new <id> <team> "<title>"` writes an order. |

An order is active while its branch is checked out in some worktree, and landed once its review is on `main`. Both are derived, nothing stores a status.

The checks, all in `tools/work.py`:

- `just work-validate`: every order is readable and no two active orders own the same file.
- `just work-check <id>`: nothing outside `owns` changed (generated files and the changelog fragment belong to anyone), then every criterion's command.
- `just work-accept <id>`: the checks, an accepted and still current review, every cross team's sign-off.
- In Claude Code, a hook refuses an edit outside the order on the current branch, and an agent whose report starts with `order: <id>` cannot stop while that order fails. Both let go on anything they cannot read, so they cannot trap a session.
- CI runs `work.py ci` on every pull request: an order that ships code ships its accepted review.

Orders that have landed are removed when a release is cut, like changelog fragments.
