- `vibe check --world desert 3` is passable on the documented install. One
  runner now stands behind every stop that runs tests: the camp's own `uv run
  pytest` when the camp declares pytest, else the interpreter running `vibe`,
  else a `pytest` on PATH. A machine with none is told which command installs
  one instead of being marked wrong, and pytest stays out of the product's
  runtime dependencies. A file with no test in it is not a test.
- The stops stopped passing on filler. A model family has to be named and not
  spelled inside `ollama`, a `mermaid` block has to close around a diagram,
  `workspace/evals/run.py` has to have a body, a hook counts as a gate only
  when it runs ruff, a formatter or the tests, the reflog has to remember a
  rewrite as its operation and not in a commit subject, and a branch has to
  have reached the remote.
- The dotfiles stop no longer breaks `git add -A` in the camp: it asks for a
  commit inside `workspace/dotfiles` and for the camp to ignore that folder,
  so nothing hides in a gitlink.
- A check says which half failed: the spec names the sections or the lines it
  still needs, the strict note check names the missing link, the game check
  names the byte floor it measures and no longer says "exists" about a file
  that exists, and the words a note needs are counted inside its dated
  section.
- A fork manifest of an unknown version, or one that will not parse, is
  refused with that sentence instead of "check crashed", and a scaffolded
  mentor exercise can never be part of a pass.
- A claimed stop's note loses the line saying the stop is not done, even when
  the learner wrote their own words into that same dated section.
- An artifact check reads the frontmatter block a Markdown file opens with, so
  a brief that starts with a horizontal rule is still a brief, and a correct
  Dockerfile passes when docker is installed but no daemon answers.
- The vault graph keys on the palette: the cyan, violet and pink
  `docs/DESIGN.md` bans by name are gone, and the Collector badge reads the
  same in the terminal as in the game.
