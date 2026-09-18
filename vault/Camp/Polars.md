---
title: "Polars"
date: 2026-09-18
tags: [tech, data]
generated: 36f9990cc623
---
# Polars

Polars is a DataFrame library whose best trick is that it does not run your query when you write it. Reach for it when the work is a transformation rather than a question: reshaping, joining and cleaning in Python, where SQL would need a temporary table for every step. Writing scan_csv instead of read_csv gives you a plan rather than a table, and Polars then rewrites that plan before it touches the file. It is the same pushdown idea as Parquet and DuckDB, applied to code you wrote in Python, and it is why the camp's own scores helper is written in Polars. And for an agent: build the whole chain first and collect once at the end; a collect in the middle throws the optimiser's work away.

**History.** The user guide draws the line in one sentence: "in the lazy API, the query is only evaluated once it is collected", against an eager mode where "the query is executed immediately". The optimisations it names are the two familiar ones. Predicate pushdown: "Apply filters as early as possible while reading the dataset, thus only reading rows with sepal length greater than 5." Projection pushdown: "Select only the columns that are needed while reading the dataset, thus removing the need to load additional columns." The payoff is stated in the same place: they "will significantly lower the load on memory & CPU thus allowing you to fit bigger datasets in memory and process them faster." The guide's own advice is not subtle: "the lazy API should be preferred unless you are either interested in the intermediate results or are doing exploratory work." Underneath it is Arrow, and Polars "can move data in and out of arrow zero copy".

**Try in five minutes.** uv run python -c "import polars as pl; print(pl.scan_csv('workspace/data/scores.csv').filter(pl.col('score') > 100).explain())" and read the plan.

- Docs: [Polars user guide, the lazy API](https://docs.pola.rs/user-guide/concepts/lazy-api/), [Polars user guide, query plan and optimisations](https://docs.pola.rs/user-guide/lazy/optimizations/), [Polars user guide, Polars and Apache Arrow](https://docs.pola.rs/user-guide/misc/arrow/), [Polars, the Python API reference](https://docs.pola.rs/api/python/stable/reference/index.html)
- Unlocks: [[dbt]], [[The medallion layering]]
- Shelf: Data · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #data
