---
title: "Dagster and Prefect"
date: 2026-09-18
tags: [tech, data]
generated: 148d620fec73
---
# Dagster and Prefect

Dagster and Prefect are the two orchestrators people reach for when Airflow feels like too much ceremony, and they disagree with it in different directions. Dagster changes the unit: you declare the table you want to exist rather than the step that makes it, and the graph is the lineage of your data. Prefect keeps the unit a function: a decorator turns ordinary Python into a flow, and the flow runs locally the moment you call it. Read this topic when you already know what a DAG is and want to know what the alternatives thought was wrong with it. And for an agent: ask what the nodes of the graph are named after. Tasks name the work; assets name the result, and only one of those is what a stakeholder asks about.

**History.** Dagster puts the asset first: "An asset represents a logical unit of data such as a table, dataset, or machine learning model", and "Assets can have dependencies on other assets, forming the data lineage for your pipelines". It calls assets "the core abstraction in Dagster", and a definition written with the @dg.asset decorator "is automatically added to a top-level Definitions object". The project describes itself as "a data orchestrator built for data engineers, with integrated lineage, observability, a declarative programming model, and best-in-class testability". Prefect states its aim differently: it "is an open-source orchestration engine that turns your Python functions into production-grade data pipelines with minimal friction", built on "simple Python decorators for tasks and flows", and its quickstart runs a flow with plain python 01_getting_started.py, with a server needed only for scheduled remote deployments. Airflow's own answer to the same question is the TaskFlow API, so the three have converged on decorators while still disagreeing about what a node is.

**Try in five minutes.** uv run --with dagster python -c "import dagster as dg; print(dg.__version__)" then compare it with uv run --with prefect prefect version.

- Docs: [Source: Dagster, version 1.0 announcement](https://dagster.io/blog/dagster-1-0-hello), [Dagster, getting started concepts: assets](https://docs.dagster.io/getting-started/concepts), [Dagster, the documentation home](https://docs.dagster.io/), [Prefect, the quickstart with flows and tasks](https://docs.prefect.io/v3/get-started/quickstart), [Prefect, what Prefect is](https://docs.prefect.io/v3/get-started/index)
- Unlocks: [[Ingestion, transformation, orchestration]]
- Shelf: Data · Depth: Deep

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #data
