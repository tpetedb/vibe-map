# ADR 0003: Python dependencies are welcome, managed by uv

Status: Accepted, 2026-09-16

## Context

The first `AGENTS.md` said "Python: standard library first; add a dependency only when it removes real work", and the companion was one file, `grimoire/cli.py`, run with `python3`. That kept the template runnable on a bare Mac and taught nothing about packaging.

The companion grew: a CLI with twenty-one commands, a state file with a schema, tables and colour in the terminal, scores through a DataFrame and through SQL, an onboarding screen. With the standard library alone that is argparse, hand-rolled validation, ANSI codes and CSV loops: more code, worse code, and none of the tools a learner meets in a real Python repo. The syllabus wants the learner to read a `pyproject.toml` and understand it (the TOML node of the tech tree).

uv installs Python, creates the environment and locks dependencies in one tool, and `scripts/setup.sh` installs uv. The owner lifted the standard-library rule on 2026-09-16 (commit `2da5ae1`: "Python dependencies are welcome when they remove real work"); the toolchain landed the same day (commit `5e9007a`).

## Decision

We will declare the package in `pyproject.toml` and manage it with uv: `uv sync` to install, `uv run` to execute, never bare `pip`. Dependencies are welcome when they remove real work. Today: click (commands), rich (terminal output), pydantic (state and config with a schema), polars and duckdb (scores), python-dotenv (tokens), pyyaml (reading the CI workflow back), textual (onboarding). Dev: pytest, playwright, pillow, ruff, basedpyright.

We will commit `uv.lock` and pin `requires-python`. Each dependency line in `pyproject.toml` carries a comment saying what it is for, so the file teaches.

We will keep `python/scores.py` and the `sql/` queries runnable without the package, because workstream 3 uses them before the learner has met uv.

## Consequences

- `uv sync` is a prerequisite for the CLI and the tests. `uv run grimoire` is the entry point; `python3 grimoire/cli.py` is not. `README.md` still shows the old command in its quickstart and has to follow.
- The learner sees a real packaging setup: a `[project]` table, dependency groups, the tool tables for ruff, pyright and pytest, and a lock file.
- Every new dependency is a decision: it must remove real work, get its comment, and survive `uv sync` on a fresh clone.
- Playwright needs a browser download on top of `uv sync`; it is the heaviest thing in the toolchain and the one the browser tests cannot do without.
