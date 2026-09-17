---
title: "SQL and DuckDB"
date: 2026-09-16
tags: [tech, data]
---
# SQL and DuckDB

SQL asks questions of tables: select what, from where, filter, group, order. DuckDB runs it on CSV and Parquet files with no server, which is why the data hour uses it. Window functions (lag, row_number) are the step from junior to medior.

**History.** SQL was designed at IBM in 1974 (as SEQUEL, by Chamberlin and Boyce) and standardised by ANSI in 1986 and ISO in 1987. It has outlived every technology that promised to replace it. DuckDB (started at CWI Amsterdam in 2018, first release 2019) brought analytics SQL to a single file.

**Try in five minutes.** duckdb < workspace/sql/streaks.sql, then change limit 3 to limit 10 and read the lag() comment.

- Docs: [DuckDB docs](https://duckdb.org/docs/), [SQLBolt](https://sqlbolt.com), [Mode SQL tutorial](https://mode.com/sql-tutorial/), [Source: Chamberlin and Boyce, SEQUEL (1974), university copy](https://course.khoury.northeastern.edu/cs3200f20s2/ssl/readings/boyce.pdf), [Source: The Open Group, SQL: The Standard and the Language](http://archive.opengroup.org/public/tech/datam/sql.htm), [Source: DuckDB Foundation](https://duckdb.foundation/), [Source: DuckDB v0.1.0 release (June 2019)](https://github.com/duckdb/duckdb/releases/tag/v0.1.0)
- Unlocks: [[Data - files, schemas, warehouses]], [[Building and consuming APIs]]
- Shelf: Data · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #data
