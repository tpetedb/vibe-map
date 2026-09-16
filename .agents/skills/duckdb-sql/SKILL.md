---
name: duckdb-sql
description: Query CSV and Parquet files with DuckDB SQL directly, no database server. Use for any question about the numbers in data/, for "top", "average", "per player", "streak", or when asked to write or fix SQL.
---
# DuckDB SQL

DuckDB reads CSV files as tables: `select * from 'data/scores.csv'`. Docs: https://duckdb.org/docs/ . SQL basics: https://sqlbolt.com

Run:
- one-off: `duckdb -c "select count(*) from 'data/scores.csv'"`
- a file: `duckdb < sql/top_runs.sql`
- in Python: `import duckdb; duckdb.sql("select ...").show()`

Conventions:
- lowercase keywords, one clause per line, a comment above each query saying which question it answers
- reusable queries live in `sql/` with a descriptive file name
- window functions for streaks and rankings: `row_number() over (partition by player order by score desc)`
- dates: `played_at::timestamp`, `date_trunc('day', played_at)`

Teach as you go: when you write a query for the user, add one comment explaining the one construct they have not seen before.
