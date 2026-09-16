---
title: "Data: files, schemas, warehouses"
date: 2026-09-16
tags: [tech, feudal]
---
# Data: files, schemas, warehouses

Data lives in files (CSV, Parquet), databases (Postgres, SQLite), and warehouses (Snowflake, BigQuery, DuckDB locally). A schema is the contract: column names and types. Most data pain is schema drift, which is why AGENTS.md pins the columns of scores.csv.

**History.** Relational databases: Codd 1970. Postgres 1986 (Berkeley). SQLite 2000, in every phone. Cloud warehouses (BigQuery 2011, Redshift 2012, Snowflake 2015) separated storage from compute. Parquet (2013, Twitter and Cloudera) is the file format they all read.

**Try in five minutes.** duckdb -c "copy 'data/scores.csv' to 'data/scores.parquet'" then query the parquet file. Same SQL, smaller file.

- Docs: [Parquet](https://parquet.apache.org/docs/), [SQLite](https://www.sqlite.org/docs.html), [Postgres tutorial](https://www.postgresql.org/docs/current/tutorial.html), [Source: IBM, The relational database (Codd, 1970)](https://www.ibm.com/history/relational-database), [Source: PostgreSQL docs, A Brief History of PostgreSQL](https://www.postgresql.org/docs/current/history.html), [Source: SQLite release history (2000-05-29)](https://www.sqlite.org/changes.html), [Source: SQLite, Most Widely Deployed Database](https://www.sqlite.org/mostdeployed.html), [Source: Google Cloud blog, Google BigQuery Service (November 2011)](https://cloudplatform.googleblog.com/2011/11/google-bigquery-service-big-data.html), [Source: AWS, Announcing Amazon Redshift (November 2012)](https://aws.amazon.com/about-aws/whats-new/2012/11/28/announcing-amazon-redshift/), [Source: Dageville et al., The Snowflake Elastic Data Warehouse (SIGMOD 2016)](https://info.snowflake.net/rs/252-RFO-227/images/Snowflake_SIGMOD.pdf), [Source: Twitter Engineering, Announcing Parquet 1.0 (2013)](https://blog.x.com/engineering/en_us/a/2013/announcing-parquet-10-columnar-storage-for-hadoop)
- Unlocks: [[Building and consuming APIs]], [[Tests and evals]]
- Age: Feudal Age · Level: Junior

<!-- generated from tools/tech.py; edit there -->

Back to [[Tech tree]]

#tech #feudal
