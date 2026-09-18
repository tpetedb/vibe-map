---
title: "Data quality and contracts"
date: 2026-09-18
tags: [tech, data]
generated: 0a14889bead4
---
# Data quality and contracts

A data contract is the small set of promises a table makes: these columns exist, this one is unique, this one is never null, that one only ever holds these values. Reach for it the moment somebody downstream depends on your table, because the alternative is finding out at the dashboard. The mechanism is the same as in code: write the assertion next to the thing, run it on every build, and fail the build rather than publish. This pack uses dbt tests for the exercise because they run against the same DuckDB file with nothing extra to install; Great Expectations is the fuller framework and is worth knowing exists. And for an agent: a test that has never failed has never been proved. Break the data on purpose once and watch it go red.

**History.** dbt ships four generic tests, and they are the four promises most contracts are made of: unique, not_null, accepted_values and relationships, the last being "each customer_id in the orders model exists as an id in the customers table (also known as referential integrity)". They are declared in YAML under a data_tests key on a column. The other half is a singular test: "when you write a SQL query that returns failing rows, you can save that query in a .sql file within your test directory", and the rule is blunt, "If the data test returns zero failing rows, it passes, and your assertion has been validated". Running them is one command: "When you run dbt test, dbt will tell you if each test in your project passes or fails." Great Expectations names the same ideas differently: "An Expectation is a verifiable assertion about data", "An Expectation Suite is a collection of Expectations", and "A Checkpoint is the primary means for validating data in a production deployment of GX". Soda is the third option in this space, but its published soda-core package does not import on Python 3.12, which is what this camp runs, so it is named here and not used.

**Try in five minutes.** Add a not_null test to a column you know has a null in it, run dbt test, and read the failing row count.

- Docs: [dbt, data tests: generic and singular](https://docs.getdbt.com/docs/build/data-tests), [dbt, model contracts](https://docs.getdbt.com/docs/collaborate/govern/model-contracts), [Great Expectations, the overview of GX Core](https://docs.greatexpectations.io/docs/core/introduction/gx_overview), [Soda, the documentation](https://docs.soda.io/)
- Unlocks: [[The medallion layering]], [[Ingestion, transformation, orchestration]]
- Shelf: Data · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #data
