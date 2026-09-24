---
title: "dlt, ingestion as code"
date: 2026-09-18
tags: [tech, data]
generated: d9c332b2db0e
---
# dlt, ingestion as code

dlt is a Python library that takes whatever a source hands you and lands it in a destination as a proper table. Reach for it when the shape of the incoming data is not your decision: an API that nests three levels deep, a paginated endpoint, a vendor export whose columns move. You write a function that yields records and name a destination; dlt works out the schema, flattens the nesting into columns, creates the tables and loads them. The part that saves the most work is the second run, because a primary key and a merge write disposition turn "load it again" into "update what changed" instead of doubling the table. And for an agent: dlt is the piece that lets you point at a messy source without writing the CREATE TABLE by hand first.

**History.** The project describes itself plainly: "dlt is an open-source Python library that loads data from various, often messy data sources into well-structured datasets". The work it removes is named in the same place: it "infers schemas and data types, normalizes the data, and handles nested data structures", and it "automates pipeline maintenance with incremental loading, schema evolution, and schema and data contracts". Installing it is one line, pip install dlt, and a pipeline is three arguments plus a run: dlt.pipeline(pipeline_name=..., destination="duckdb", dataset_name=...) then pipeline.run(source). The version read for this topic was 1.30.0, and it is the version the hands-on was run against. Because the destination is DuckDB, none of this needs a warehouse, an account or a network.

**Try in five minutes.** uv run --with "dlt[duckdb]" python -c "import dlt; p = dlt.pipeline(destination='duckdb'); print(p.pipeline_name)" and you have a pipeline.

- Docs: [Source: dltHub, version 1.0.0 announcement](https://dlthub.com/blog/dlt-v1), [dlt, the introduction](https://dlthub.com/docs/intro), [dlt, creating a pipeline](https://dlthub.com/docs/walkthroughs/create-a-pipeline), [dlt, incremental loading and write dispositions](https://dlthub.com/docs/general-usage/incremental-loading), [DuckDB, the destination this hands-on uses](https://duckdb.org/docs/stable/)
- Unlocks: [[dbt]], [[The medallion layering]], [[Data quality and contracts]]
- Shelf: Data · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #data
