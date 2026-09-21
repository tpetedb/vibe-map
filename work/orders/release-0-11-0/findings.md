# Decision

Tom delegated the decision to publish on 2026-09-21. It is taken: 0.11.0 goes out. Main is green, everything on it since 0.10.0 was reviewed or carried through a tested train car, and the product jobs of the nightly suite (the play-through, the camp from nothing, the installed command on a Mac) pass. The one red nightly job was a calendar artefact (order `news-feed-liveness`).

Minor, not patch: eight fragments are `added`. Not 1.0.0: the course is still changing shape.

# What this order does

1. `just release 0.11.0` (it runs `tools/changelog.py release` and sweeps landed work orders). Read the result as a reader would and edit the section until criterion c5 holds; fragments are raw material.
2. `pyproject.toml` to 0.11.0, `uv lock`, rebuild, the fork mirror and the template in sync.
3. In the released 0.10.0 section, the artifact count: twenty-one, as the data has it (`docs/BRIEF.md` was already right). Nothing else in a released section changes.
4. `uv run python tools/media.py`: every screenshot and the GIF, from the built game. Look at each one. Issue 59 lists shots the tool never took (the archipelago, the Ask panel, the dashboard, the backpack): add them to `tools/media.py` if each is a few lines, and say which you left out. `docs/media/README.md` stays true.
5. `work/goals/release-0-11-0.toml`: the goal in two sentences, what it leaves out, the two orders.

# What this order does not do

The tag, the GitHub release and the repository's social preview image are the orchestrator's and the owner's, after this lands. Do not tag, do not run `gh release`.

# Careful

- Land order matters: a branch that lands before this one adds a fragment that this release did not assemble. If main gained fragments when you sync, run the release step again on top (the tool refuses a section that exists: remove yours first, then rerun) so that c2 holds.
- `tests/test_changelog.py` pins things about the latest section; the last release had to touch it. Change what a new version legitimately changes and nothing else.
- Media files are large and binary. Commit only pictures that actually changed.
