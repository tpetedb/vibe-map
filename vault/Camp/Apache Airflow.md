---
title: "Apache Airflow"
date: 2026-09-18
tags: [tech, data]
generated: f3d91177c516
---
# Apache Airflow

Airflow is the scheduler: it holds the graph of what runs, in what order, on what schedule, and what to do when a step fails. Reach for it when the pipeline has more than one moving part and somebody has to be able to see, at eight in the morning, which run failed and where. It does not transform your data and it does not move it; it calls the things that do, which is why it sits next to dbt and dlt rather than replacing either. The hands-on here parses a DAG with the real library instead of starting a server, and the reason is measured below, not assumed. And for an agent: a DAG file is Python that is imported, not run, so anything slow at module level is paid on every parse.

**History.** The concepts page is short about what a DAG is: "A Dag is a model that encapsulates everything needed to execute a workflow", with a schedule, tasks, task dependencies and callbacks. "Tasks are discrete units of work that are run on workers", and they "come in the form of Operators, Sensors or TaskFlow". Dependencies are declared with operators: "The recommended one is to use the >> and << operators", or the explicit set_upstream and set_downstream. The schedule is one argument: "You define it via the schedule argument", with values such as "@daily" or a cron string. Running the whole thing locally is documented as one command, where "The airflow standalone command initializes the database, creates a user, and starts all components", served at localhost:8080. That is the part this topic declines to make the exercise: the check against Airflow 3.3.2 on a laptop was a 179 MB environment in which importing the SDK alone took about six seconds, and standalone adds a database migration plus an api-server, a scheduler and a triggerer left running. Parsing the DAG with the real library is the honest twenty-minute version; start standalone yourself when you have the afternoon.

**Try in five minutes.** uv run --with "apache-airflow==3.3.2" python -c "from airflow.sdk import DAG; print(DAG)" and note how long the import alone takes.

- Docs: [Source: Airbnb Engineering, Airflow announcement](https://medium.com/airbnb-engineering/airflow-a-workflow-management-platform-46318b977fd8?responsesOpen=true&sortBy=REVERSE_CHRON), [Airflow, core concepts: DAGs](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html), [Airflow, quick start and airflow standalone](https://airflow.apache.org/docs/apache-airflow/stable/start.html), [Airflow, the TaskFlow API](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/taskflow.html), [Airflow, installation](https://airflow.apache.org/docs/apache-airflow/stable/installation/index.html), [Source: Airbnb, About us, as archived on 2 June 2015 (based in San Francisco)](https://web.archive.org/web/20150602181934/https://www.airbnb.com/about/about-us)
- Unlocks: [[Dagster and Prefect]], [[Ingestion, transformation, orchestration]]
- Shelf: Data · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #data
