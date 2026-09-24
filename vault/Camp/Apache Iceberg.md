---
title: "Apache Iceberg"
date: 2026-09-18
tags: [tech, data]
generated: 017a6a15c140
---
# Apache Iceberg

Iceberg is a table format: a pile of Parquet files plus metadata that says which of them are the table right now. Reach for it when several writers share one dataset, when you need to read the table as it was last Tuesday, or when a column has to change without rewriting terabytes. The unit that makes it work is the snapshot, and a commit is an atomic swap of one metadata pointer for another, so a reader either sees the old table or the new one and never a half-written mixture. Delta Lake solves the same problem with the same ingredients (Parquet files plus a log, ACID transactions, time travel, schema enforcement) and the choice between them is usually made by which engines your employer already runs, not by the formats. And for an agent: Iceberg is the version control of tables, and "which snapshot" is the question to ask when two runs disagree.

**History.** The specification states the goal first: "Serializable isolation: Reads will be isolated from concurrent writes and always use a committed snapshot of a table's data. Writes will support removing and adding files in a single operation and are never partially visible. Readers will not acquire locks." The mechanism is one file: "All changes to table state create a new metadata file and replace the old metadata with an atomic swap. The table metadata file tracks the table schema, partitioning config, custom properties, and snapshots of the table contents. A snapshot represents the state of a table at some time". Under a snapshot sit manifests: "Data files in snapshots are tracked by one or more manifest files that contain a row for each data file in the table, the file's partition data, and its metrics", and "The manifests that make up a snapshot are stored in a manifest list file", whose stats "are used to avoid reading manifests that are not required for an operation". Concurrency is optimistic: a writer "commits by swapping the table's metadata file pointer from the base version to the new version". Evolution falls out of the same design, because "Iceberg schema updates are metadata changes, so no data files need to be rewritten" and "Iceberg uses unique IDs to track each column".

**Try in five minutes.** uv run --with "pyiceberg[sql-sqlite,pyarrow]" python -c "from pyiceberg.catalog.sql import SqlCatalog; print(SqlCatalog)" and you have a catalog with no server.

- Docs: [Source: Apache Incubator, Iceberg project status](https://incubator.apache.org/projects/iceberg.html), [Apache Iceberg, the table specification](https://iceberg.apache.org/spec/), [Apache Iceberg, evolution](https://iceberg.apache.org/docs/latest/evolution/), [PyIceberg, the Python implementation and its SQL catalog](https://py.iceberg.apache.org/), [Delta Lake, what it is](https://docs.delta.io/latest/delta-intro.html), [Source: Apache Iceberg, format/spec.md in the project repository](https://github.com/apache/iceberg/blob/main/format/spec.md)
- Unlocks: [[The medallion layering]], [[Data quality and contracts]]
- Shelf: Data · Depth: Deep

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #data
