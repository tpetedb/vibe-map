- `work.py ci` judges each order a pull request carries by itself. A plan (an
  order with no builder whose files are untouched) rides in a train car next
  to built code without asking for a review, and an order's strays are
  measured on what its own branch changed, so a loose change in the same car
  is nobody's stray.
- `work.py plan` prints the groups it can form and then which orders are
  blocked by an order of another goal that has not landed; only orders that
  wait on each other are called a cycle.
- `work.py validate` warns when a criterion runs pytest over a file with
  integration tests without `-m 'not integration'`, since those may go online.
- A file whose name looks like git pathspec magic (`:(nope)x.js`,
  `:!src/x.js`) is judged like any other file instead of stopping the check or
  hiding a neighbouring stray.
- `touched.json` keeps agents in the order of their last edit, so a builder
  that keeps editing is never the one dropped.
- `tools/ci_shards.py` stops every shard when pytest cannot collect the
  browser battery, instead of leaving the broken file out of all of them, and
  refuses a `default` that is not a plain true or false.
- `work.py validate` fails a branch only for a collision its own order is part
  of. A clash between two orders in other worktrees is still printed, as
  "collision elsewhere", and a checkout that builds no order, such as `main`,
  still fails on any collision.
