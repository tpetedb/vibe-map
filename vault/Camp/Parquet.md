---
title: "Parquet"
date: 2026-09-18
tags: [tech, data]
generated: 72035d5715f0
---
# Parquet

Parquet is a binary columnar file format: the rows are cut into row groups, each row group holds one chunk per column, and a footer at the end records where every chunk is and what is in it. Reach for it the moment a CSV stops being something a human opens: it is smaller, it is typed, and a query that wants two of forty columns reads two. The footer is what makes it fast, because a reader can look up the minimum and maximum of a column in a row group and skip the whole group without decompressing it. That skipping is what predicate pushdown means, and it is why the same query is faster on Parquet than on CSV even though Parquet is harder to read by hand. And for an agent: write Parquet when the next step is a query and CSV when the next step is a human.

**History.** The Parquet file layout is documented as a magic number PAR1, then the column chunks, then the file metadata, then a four-byte little-endian metadata length, then PAR1 again. The metadata sits at the end on purpose: "File metadata is written after the data to allow for single pass writing", and a reader works backwards, because "Readers are expected to first read the file metadata to find all the column chunks they are interested in". Splitting metadata from data is also deliberate: it "allows splitting columns into multiple files, as well as having a single metadata file reference multiple parquet files". DuckDB documents what it does with that footer: "When you apply a filter to a column that is scanned from a Parquet file, the filter will be pushed down into the scan", and only "the columns required for the query are read". Size matters to the same reader: DuckDB "works best on Parquet files with row groups of 100K-1M rows each", because it "can only parallelize over row groups", and it measures TPC-H queries running "approximately 1.1-5.0x slower on Parquet files than on a DuckDB database".

**Try in five minutes.** duckdb -c "copy (from 'workspace/data/scores.csv') to 'scores.parquet' (format parquet)" then duckdb -c "select * from parquet_metadata('scores.parquet')" and read the footer.

- Docs: [Apache Parquet, the file format](https://parquet.apache.org/docs/file-format/), [DuckDB, reading and writing Parquet files](https://duckdb.org/docs/stable/data/parquet/overview), [DuckDB performance guide, file formats and row group sizes](https://duckdb.org/docs/stable/guides/performance/file_formats), [PyArrow, reading and writing the Parquet format](https://arrow.apache.org/docs/python/parquet.html)
- Unlocks: [[Apache Arrow]], [[DuckDB beyond the basics]], [[Apache Iceberg]]
- Shelf: Data · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #data
