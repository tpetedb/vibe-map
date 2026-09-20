---
name: duckdb-sql
description: Answers questions about the numbers in workspace/data/scores.csv with DuckDB SQL, straight from the CSV, no database server. Use for "top runs", "best score", "average per player", "how many runs", "who is winning", "longest streak", "query the scores", or when asked to write, explain or fix SQL or a file in sql/.
allowed-tools: Bash(duckdb *)
---
# DuckDB SQL

DuckDB reads a CSV as a table: `select * from 'workspace/data/scores.csv'`. Columns: `played_at, player, score, duration_s`. The file is a system of record: query it, never rewrite it. Docs: https://duckdb.org/docs/ . SQL basics: https://sqlbolt.com

Run (the `duckdb` CLI comes from `brew install duckdb`; for the Python package a camp needs no install, `uv run --with duckdb` fetches it for the one command):
- one-off: `duckdb -c "select count(*) from 'workspace/data/scores.csv'"`
- a saved query: `duckdb < workspace/sql/top_runs.sql`
- in Python: `uv run --with duckdb python -c "import duckdb; duckdb.sql(\"select * from 'workspace/data/scores.csv' limit 5\").show()"`
- the standard summary: `uv run vibe scores`

`workspace/sql/` is yours to fill in workstream 3, one file per question. Three that are worth writing first, because the checks and `vibe scores` read them by name: `top_runs.sql` (the five best runs, and the one workstream 3 insists on), `per_player.sql` (runs, best and mean per player) and `streaks.sql` (the longest improving streak, with `lag()` over a window).

Conventions:
- lowercase keywords, one clause per line, a comment above each query saying which question it answers
- reusable queries live in `workspace/sql/` with a descriptive file name
- window functions for streaks and rankings: `row_number() over (partition by player order by score desc)`
- dates: `played_at::timestamp`, `date_trunc('day', played_at::timestamp)`

Teach as you go: when you write a query for the user, add one comment explaining the one construct they have not seen before. Show the result as a small table, then the query.
