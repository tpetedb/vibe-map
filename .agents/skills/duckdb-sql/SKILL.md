---
name: duckdb-sql
description: Answers questions about the numbers in data/scores.csv with DuckDB SQL, straight from the CSV, no database server. Use for "top runs", "best score", "average per player", "how many runs", "who is winning", "longest streak", "query the scores", or when asked to write, explain or fix SQL or a file in sql/.
allowed-tools: Bash(duckdb *)
---
# DuckDB SQL

DuckDB reads a CSV as a table: `select * from 'data/scores.csv'`. Columns: `played_at, player, score, duration_s`. The file is a system of record: query it, never rewrite it. Docs: https://duckdb.org/docs/ . SQL basics: https://sqlbolt.com

Run (the `duckdb` CLI comes from `brew install duckdb`; the Python package is a project dependency):
- one-off: `duckdb -c "select count(*) from 'data/scores.csv'"`
- a saved query: `duckdb < sql/top_runs.sql`
- in Python: `uv run python -c "import duckdb; duckdb.sql(\"select * from 'data/scores.csv' limit 5\").show()"`
- the standard summary: `uv run grimoire scores`

Tested queries in `sql/`: `top_runs.sql` (five best runs), `per_player.sql` (runs, best, mean per player), `streaks.sql` (longest improving streak, with `lag()` over a window). Start from these.

Conventions:
- lowercase keywords, one clause per line, a comment above each query saying which question it answers
- reusable queries live in `sql/` with a descriptive file name
- window functions for streaks and rankings: `row_number() over (partition by player order by score desc)`
- dates: `played_at::timestamp`, `date_trunc('day', played_at::timestamp)`

Teach as you go: when you write a query for the user, add one comment explaining the one construct they have not seen before. Show the result as a small table, then the query.
