---
title: "dbt"
date: 2026-09-18
tags: [tech, data]
generated: a29672c021b8
---
# dbt

dbt turns a folder of SELECT statements into a build system: each file is a model, each model is a table or a view, and one function call says which model depends on which. Reach for it when the transformations have outgrown a single script and somebody other than you has to understand the order they run in. The whole idea rests on ref, because writing ref('runs') instead of the table name is what lets dbt work out the graph and build the pieces in the right order. It is transformation only, and it runs where the data already is: no rows leave the warehouse, which on a laptop means the warehouse is a DuckDB file. And for an agent: never hardcode a table name a model already produces; ref is the edge of the graph, and a hardcoded name is an edge nobody can see.

**History.** The documentation keeps the definition small: "Models are primarily written as a select statement and saved as a .sql file", and "A project is a directory of a .yml file (the project configuration) and either .sql or .py files (the models)". A model is "a single file containing a final select statement, and a project can have multiple models, and models can even reference each other". The execution model is the second half: "When you execute dbt run, you are running a model that will transform your data without that data ever leaving your warehouse." The DuckDB adapter is configured with a profile, and the documented local target is four lines: type: duckdb, path: './my_project.duckdb', schema: main and threads. What installs on a laptop today is the open-source dbt Core plus that adapter, which this topic was checked against at dbt Core 1.12.5 with dbt-duckdb 1.11.0; the documentation site also now describes a dbt v2 in which the DuckDB adapter is bundled, so read the install page before you pin anything.

**Try in five minutes.** uv run --with dbt-duckdb dbt --version and read which adapter you got, then dbt init to see the folder it wants.

- Docs: [dbt, building models](https://docs.getdbt.com/docs/build/models), [dbt, the DuckDB connection profile](https://docs.getdbt.com/docs/core/connect-data-platform/duckdb-setup), [dbt, installation overview](https://docs.getdbt.com/docs/core/installation-overview), [dbt, the ref function](https://docs.getdbt.com/reference/dbt-jinja-functions/ref)
- Unlocks: [[Data quality and contracts]], [[The medallion layering]], [[Apache Airflow]]
- Shelf: Data · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #data
