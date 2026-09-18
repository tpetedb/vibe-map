---
title: "Ingestion, transformation, orchestration"
date: 2026-09-18
tags: [tech, data]
generated: 5772609e07ae
---
# Ingestion, transformation, orchestration

Every data tool you will be handed does one of three things, and the fastest way to read a job advert or an architecture diagram is to sort the names into those three piles. Ingestion moves bytes and changes nothing: dlt, Kafka, a vendor export. Transformation changes meaning and moves nothing: dbt, Polars, SQL in DuckDB. Orchestration runs neither, and owns only the order, the schedule and what happens when a step fails: Airflow, Dagster, Prefect. Read this topic first if the pack looks like a list of sixteen unrelated products, and last if you want the summary. And for an agent: when you are asked to add a tool, say which of the three it is before you install it. Two tools in the same pile is usually a mistake you are about to make.

**History.** Each pile has a definition its own documentation gives it. Ingestion, from dlt: it "loads data from various, often messy data sources into well-structured datasets", and it "infers schemas and data types, normalizes the data, and handles nested data structures". Transformation, from dbt: "When you execute dbt run, you are running a model that will transform your data without that data ever leaving your warehouse", which is the whole point, because the data does not move. Orchestration, from Airflow: "A Dag is a model that encapsulates everything needed to execute a workflow", where "Tasks are discrete units of work that are run on workers" and the schedule is one argument. Dagster puts the same job in different words, calling itself "a data orchestrator built for data engineers, with integrated lineage, observability, a declarative programming model". Nothing here is a hierarchy: a working pipeline needs all three, and most of the arguments you will hear are about which pile a particular tool belongs in.

**Try in five minutes.** Write the three words on a page and put every data tool your employer pays for under one of them. The ones you cannot place are the ones to ask about.

- Docs: [dlt, the introduction: what ingestion is for](https://dlthub.com/docs/intro), [dbt, building models: transformation where the data is](https://docs.getdbt.com/docs/build/models), [Airflow, core concepts: DAGs, tasks and schedules](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html), [Dagster, the documentation home](https://docs.dagster.io/)
- Shelf: Data · Depth: Basics

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #data
