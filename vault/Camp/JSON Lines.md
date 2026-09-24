---
title: "JSON Lines"
date: 2026-09-18
tags: [tech, data]
generated: 7ef7a0390435
---
# JSON Lines

JSON Lines is one JSON value per line in a UTF-8 text file, extension .jsonl. Reach for it when records arrive one at a time and the file has to stay appendable: logs, event streams, an API paged into a file, anything you want to tail. It is the format that makes a large JSON document readable a record at a time, because a whole-file JSON array has to be parsed before you see the first record. Every line stands alone, so two files concatenate into one valid file and a crash halfway through costs you one line, not the file. And for an agent: a .jsonl file is the cheapest append-only log you can write from a tool, and the easiest one to diff.

**History.** The specification has three requirements, and the first is UTF-8: "a byte order mark (U+FEFF) must NOT be included". The second is that each line is a valid JSON value, where "The most common values will be objects or arrays, but any JSON value is permitted. e.g. null is a valid value but a blank line is not". The third is the line terminator: "Line Terminator is '\n'", and "'\r\n' is also supported because surrounding white space is implicitly ignored when parsing JSON values". The spec explains why the terminator comes after the last record too: "Including a line terminator after every JSON value makes generating and concatenating JSON Lines files easier", while after the last value it is "strongly recommended but not required". The suggested extension is .jsonl, and compressed variants such as .jsonl.gz are named as the way to save space.

**Try in five minutes.** printf '{"a":1}\n{"a":2}\n' > two.jsonl then duckdb -c "select sum(a) from read_json('two.jsonl')" and read 3.

- Docs: [Source: Ian Ward, JSON Lines specification commit](https://github.com/wardi/jsonlines/commit/92c32d4496d1f0b789cc4840e6cd65e11ef51e94), [JSON Lines, the specification](https://jsonlines.org/), [Python, the json module](https://docs.python.org/3/library/json.html), [DuckDB, reading JSON and newline-delimited JSON](https://duckdb.org/docs/stable/data/json/overview)
- Unlocks: [[Schemas and schema evolution]], [[dlt, ingestion as code]]
- Shelf: Data · Depth: Basics

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #data
