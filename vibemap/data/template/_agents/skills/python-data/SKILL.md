---
name: python-data
description: Writes small, readable Python for reading workspace/data/scores.csv, computing summaries and drawing a chart, run with uv. Use when asked for a script, a chart or plot, "automate this", "do it in Python", polars or pandas, or when SQL is not the right tool.
---
# Python for data

Reference: https://docs.python.org/3/tutorial/ . Exercises: https://exercism.org/tracks/python . Run everything with `uv run python <file>`; never bare `pip`.

Rules:
- Standard library first (`csv`, `statistics`, `datetime`, `pathlib`, `argparse`). `polars` and `duckdb` are already project dependencies; add anything else with `uv add <package>` only when it removes real work, and say why.
- One file, `from __future__ import annotations`, a `main()` function, `if __name__ == "__main__": main()`.
- Read `workspace/data/scores.csv` with `csv.DictReader` (or `polars.read_csv`). Never mutate it.
- Print a small table to the terminal; write charts to `python/out/` (gitignored).
- Explain one new concept per script in the module docstring at the top.
- Format with `just fmt` (ruff). If the Python grows beyond one file, add tests in `tests/` and run `uv run pytest`.

Starting point: `workspace/python/scores.py` (`uv run python workspace/python/scores.py`).
