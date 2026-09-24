---
title: "Schemas and schema evolution"
date: 2026-09-18
tags: [tech, data]
generated: de16e6624737
---
# Schemas and schema evolution

A schema is the contract a table keeps: the column names, their types, and whether a value may be missing. Reach for one the moment two programs share a file, because without it the reader guesses and the guess changes when the data does. Schema evolution is what happens next, when a column is added, dropped, renamed or widened while old files are still lying around. The formats that survive that name their columns rather than count them; the one drift nobody can repair automatically is a rename, because a new name and a dropped column look identical from the outside. And for an agent: pin the columns you depend on in writing, then fail loudly when they move, rather than quietly reading position three.

**History.** Avro resolves a writer's schema against a reader's schema, and the rules are worth knowing by heart: "If the reader's record schema has a field that contains a default value, and writer's schema does not have a field with the same name, then the reader should use the default value from its field", while "If the writer's record contains a field with a name not present in the reader's record, the writer's value for that field is ignored". A missing field with no default is not patched over: "an error is signalled". Records are matched "by name", not by position, which is the whole trick. Iceberg makes the same promise on a table: it "supports the following schema evolution changes: Add, Drop, Rename, Update, Reorder", "Iceberg schema updates are metadata changes, so no data files need to be rewritten", and the reason it is safe is that "Iceberg uses unique IDs to track each column in a table. When you add a column, it is assigned a new ID so existing data is never used by mistake". DuckDB gives the same problem a reader-side answer: by default it "reads the schema of the first file provided, and then unifies columns in subsequent files by column position", and `union_by_name = true` matches on names instead, where "any missing values are set to NULL".

**Try in five minutes.** duckdb -c "select * from read_parquet(['a.parquet','b.parquet'], union_by_name = true)" on two files with different columns and count the NULLs.

- Docs: [Source: Apache Incubator, Iceberg specification publication](https://incubator.apache.org/projects/iceberg.html), [Apache Avro specification, schema resolution](https://avro.apache.org/docs/1.12.0/specification/), [Apache Iceberg, evolution: schema, partition and sort order](https://iceberg.apache.org/docs/latest/evolution/), [DuckDB, combining schemas across files with union_by_name](https://duckdb.org/docs/stable/data/multiple_files/combining_schemas), [Source: Apache Iceberg, docs/docs/evolution.md in the project repository](https://github.com/apache/iceberg/blob/main/docs/docs/evolution.md)
- Unlocks: [[Apache Iceberg]], [[Data quality and contracts]], [[dlt, ingestion as code]]
- Shelf: Data · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #data
