---
name: python-data
description: Small, readable Python for reading CSV, computing summaries, and drawing a chart. Use when asked for a script, a chart, "automate this", or when SQL is not the right tool.
---
# Python for data

Reference: https://docs.python.org/3/tutorial/ . Exercises: https://exercism.org/tracks/python

Rules:
- Standard library first (`csv`, `statistics`, `datetime`, `pathlib`, `argparse`). Add `duckdb`, `pandas` or `matplotlib` only when they remove real work; install with `uv pip install`.
- One file, a `main()` function, `if __name__ == "__main__": main()`.
- Read `data/scores.csv` with `csv.DictReader`. Never mutate it.
- Print a small table to the terminal; write charts to `python/out/`.
- Explain one new concept per script in a comment at the top.

Starting point: `python/scores.py`.
