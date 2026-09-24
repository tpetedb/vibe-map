---
title: "The medallion layering"
date: 2026-09-18
tags: [tech, data]
generated: a13eb13e4a43
---
# The medallion layering

Medallion is a naming convention for the stages data passes through: bronze holds it as it arrived, silver holds it cleaned, gold holds the answer somebody asked for. Reach for it when more than one person builds tables in the same place, because the value is that a table's name tells you how much you may trust it. In this camp, keep bronze append-only so you can rebuild the later layers when a cleaning rule turns out to be wrong. That is an exercise choice: Databricks also documents updates in Bronze to apply change-data capture (CDC). It is a convention rather than a rule, and Databricks, who named it, say so in as many words. And for an agent: in this exercise, keep bronze unchanged and clean in silver. The copy of the source you did not touch is the only thing that makes a mistake recoverable.

**History.** Databricks defines it in one sentence: "The medallion architecture describes a series of data layers that denote the quality of data stored in the lakehouse." Bronze is "Raw data ingestion", holding "Raw, unvalidated data", and it "Contains and maintains the raw state of the data source in its original formats". Silver is "Data cleaning and validation", where you "perform data cleansing, deduplication, and normalization". Gold is "Dimensional modeling and aggregation" and "Consists of aggregated data tailored for analytics and reporting". The caveat is theirs too: "Following the medallion architecture is a recommended best practice but not a requirement." The layers are a good fit for the rest of this pack, because dlt lands bronze, dbt builds silver and gold, tests guard the boundary between them, and a table format such as Iceberg is what lets bronze be rebuilt without anyone reading a half-written table.

**Try in five minutes.** Name the three tables you touched at work this week bronze, silver or gold. The one you cannot name is the one to look at.

- Docs: [Source: Databricks, data layers and modeling (2022)](https://www.databricks.com/blog/2022/06/24/data-warehousing-modeling-techniques-and-their-implementation-on-the-databricks-lakehouse-platform.html), [Databricks, what is a medallion architecture](https://docs.databricks.com/aws/en/lakehouse/medallion), [Databricks, the lakehouse architecture](https://docs.databricks.com/aws/en/lakehouse/), [dbt, how we structure our projects](https://docs.getdbt.com/best-practices/how-we-structure/1-guide-overview)
- Unlocks: [[Ingestion, transformation, orchestration]]
- Shelf: Data · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #data
