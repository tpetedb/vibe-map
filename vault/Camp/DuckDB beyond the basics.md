---
title: "DuckDB beyond the basics"
date: 2026-09-18
tags: [tech, data]
generated: 120ad7734d16
---
# DuckDB beyond the basics

The core topic on SQL and DuckDB gets you selecting from a CSV; this one is the rest of the tool. Reach for it when the query is the program: a persistent .duckdb file instead of a re-read of the files, views that name a step, window functions that answer per-group questions, and the friendly syntax that removes the boilerplate. The two habits that change the most are QUALIFY, which filters on a window function without a wrapping subquery, and GROUP BY ALL, which stops you restating the grouping columns. Keep reading the files directly while you explore, and load them into a database file once the same data is queried again and again. And for an agent: a .duckdb file is a whole analytics database you can commit to a scratch folder and delete, with no server to start.

**History.** DuckDB documents a list it calls Friendly SQL, and most of it exists to delete typing. FROM-first: "DuckDB allows queries in the form of FROM tbl which selects all columns". GROUP BY ALL lets you "omit the group-by columns by inferring them from the list of attributes", and ORDER BY ALL is "shorthand to order on all columns (e.g., to ensure deterministic results)". SELECT * EXCLUDE "allows excluding specific columns from the * expression" and SELECT * REPLACE "allows replacing specific columns with different expressions". Column aliases are usable in WHERE, GROUP BY and HAVING, which no other dialect lets you do. When to stop reading files and load them is a documented answer too: "If you have the storage space available, and have a join-heavy workload and/or plan to run many queries on the same dataset, load the Parquet files into the database first", because a DuckDB database carries "hyperloglog statistics that Parquet files do not have".

**Try in five minutes.** duckdb camp.duckdb -c "create table runs as from read_csv('workspace/data/scores.csv'); from runs limit 3" and note that the file persists.

- Docs: [Source: DuckDB Foundation, the co-creators](https://duckdb.foundation/), [DuckDB, Friendly SQL](https://duckdb.org/docs/stable/sql/dialect/friendly_sql), [DuckDB, the QUALIFY clause](https://duckdb.org/docs/stable/sql/query_syntax/qualify), [DuckDB, window functions](https://duckdb.org/docs/stable/sql/functions/window_functions), [DuckDB performance guide, file formats and when to load](https://duckdb.org/docs/stable/guides/performance/file_formats)
- Unlocks: [[dbt]], [[The medallion layering]]
- Shelf: Data · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #data
