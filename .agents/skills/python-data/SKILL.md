---
name: python-data
description: Writes small, readable Python for reading workspace/data/scores.csv, computing summaries and drawing a chart, run with uv. Use when asked for a script, a chart or plot, "automate this", "do it in Python", polars or pandas, or when SQL is not the right tool.
---
# Python for data

Reference: https://docs.python.org/3/tutorial/ . Exercises: https://exercism.org/tracks/python . Run everything with `uv run python <file>`; never bare `pip`.

Rules:
- Standard library first (`csv`, `statistics`, `datetime`, `pathlib`, `argparse`). A camp has no Python project of its own, so reach for a package only when it removes real work, and run it without installing anything: `uv run --with polars python <file>`.
- One file, `from __future__ import annotations`, a `main()` function, `if __name__ == "__main__": main()`.
- Read `workspace/data/scores.csv` with `csv.DictReader` (or `polars.read_csv`). You write that file yourself in workstream 3, from real rounds of your own game; once it exists it is a system of record, so never mutate it.
- Print a small table to the terminal; write charts to `workspace/python/out/` (gitignored).
- Explain one new concept per script in the module docstring at the top.
- Format with `uv run --with ruff ruff format <file>` and check it with `ruff check`, at 88 columns. If the Python grows beyond one file, put a test next to it and run it with `uv run --with pytest pytest`.

Starting point: write `workspace/python/scores.py` and run it with `uv run python workspace/python/scores.py`. `vibe scores` prints the standard summary of the same file, and workstream 3's check looks for at least one script in `workspace/python/`.
