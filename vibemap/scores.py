"""Scores: the same CSV through polars, DuckDB and the workspace/sql/ folder.

workspace/data/scores.csv is a system of record; nothing here writes to it.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import duckdb
import polars as pl
from rich.table import Table

from vibemap import project

ROOT = project.root()
SCORES = ROOT / "workspace" / "data" / "scores.csv"
SQL_DIR = ROOT / "workspace" / "sql"
COLUMNS = ("played_at", "player", "score", "duration_s")


def read_scores(path: Path = SCORES) -> pl.DataFrame:
    """Load the scores file, validating the column contract."""
    df = pl.read_csv(path, try_parse_dates=True)
    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"{path.name} is missing columns: {', '.join(missing)}")
    return df


def summary(df: pl.DataFrame) -> dict[str, Any]:
    """Runs, best, mean and a per-player breakdown."""
    if df.is_empty():
        return {"runs": 0, "best": 0, "best_by": "", "mean": 0.0, "players": []}
    best_row = df.sort("score", descending=True).row(0, named=True)
    per_player = (
        df.group_by("player")
        .agg(
            pl.len().alias("runs"),
            pl.col("score").max().alias("best"),
            pl.col("score").mean().round(1).alias("mean"),
            pl.col("duration_s").sum().alias("seconds"),
        )
        .sort("best", descending=True)
    )
    return {
        "runs": df.height,
        "best": int(best_row["score"]),
        "best_by": str(best_row["player"]),
        "mean": round(float(df["score"].mean() or 0), 1),
        "players": per_player.to_dicts(),
    }


def run_sql(name: str, *, cwd: Path = ROOT) -> pl.DataFrame:
    """Run one of the queries in workspace/sql/ with DuckDB, run from the camp root."""
    path = SQL_DIR / (name if name.endswith(".sql") else f"{name}.sql")
    if not path.exists():
        options = ", ".join(p.stem for p in sorted(SQL_DIR.glob("*.sql")))
        raise FileNotFoundError(f"no {path.name} in workspace/sql/; options: {options}")
    con = duckdb.connect()
    con.execute(f"set file_search_path = '{cwd.as_posix()}'")
    cur = con.execute(path.read_text(encoding="utf-8"))
    columns = [d[0] for d in cur.description or []]
    # Rows to polars by hand: DuckDB's .pl() needs pyarrow, one dependency
    # fewer for a tiny result set.
    return pl.DataFrame(cur.fetchall(), schema=columns, orient="row")


def scores_table(data: dict[str, Any]) -> Table:
    t = Table(title="Scores", title_style="title", header_style="path")
    t.add_column("player")
    t.add_column("runs", justify="right")
    t.add_column("best", justify="right", style="ok")
    t.add_column("mean", justify="right")
    t.add_column("chart")
    top = max((p["best"] for p in data["players"]), default=1) or 1
    for p in data["players"]:
        bar = "#" * int(30 * p["best"] / top)
        t.add_row(str(p["player"]), str(p["runs"]), str(p["best"]), str(p["mean"]), bar)
    t.caption = (
        f"{data['runs']} runs, best {data['best']} by {data['best_by']}, "
        f"mean {data['mean']}"
    )
    return t


def frame_table(df: pl.DataFrame, title: str) -> Table:
    t = Table(title=title, title_style="title", header_style="path")
    for c in df.columns:
        t.add_column(c, justify="right" if df[c].dtype.is_numeric() else "left")
    for row in df.iter_rows():
        t.add_row(*[str(v) for v in row])
    return t
