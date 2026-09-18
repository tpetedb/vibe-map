---
title: "Apache Arrow"
date: 2026-09-18
tags: [tech, data]
generated: 4838973fc387
---
# Apache Arrow

Arrow is a columnar layout for data in memory, not a file format you store things in. Reach for it when two tools have to hand a table to each other, because Arrow is what lets DuckDB, Polars and pandas pass the same buffers around instead of each writing and parsing its own copy. Parquet is how a table rests on disk; Arrow is how it sits in RAM while something is working on it. The payoff is the copy that does not happen: the bytes one library allocated are the bytes the other one reads. And for an agent: when a pipeline feels slow for no reason, look for a conversion between two libraries that both already speak Arrow.

**History.** The columnar format specification calls itself "a language-agnostic in-memory data structure specification, metadata serialization, and a protocol for serialization and generic data transport". Its vocabulary is small: an array is "a sequence of values with known length all having the same type", a buffer is "a sequential virtual address space with a given length", and nullness lives apart from the values in a validity bitmap where "a 1 (set bit) for index j indicates that the value is not null". Layout is deliberate down to the address: the spec recommends "allocating memory on aligned addresses (multiple of 8- or 64-bytes)", the 64 matching the SIMD register width so a loop needs no conditional checks. Because the layout holds no pointers it is "relocatable without 'pointer swizzling', allowing for true zero-copy access in shared memory". Arrow's own introduction says why any of this exists: it "was born from the need for a set of standards around tabular data representation and interchange between systems", and adopting them "reduces computing costs of data serialization/deserialization and implementation costs across systems".

**Try in five minutes.** python3 -c "import polars as pl; pl.DataFrame({'a':[1,2]}).write_ipc('t.arrow')" then head -c 6 t.arrow and read ARROW1.

- Docs: [Apache Arrow, the columnar format specification](https://arrow.apache.org/docs/format/Columnar.html), [Apache Arrow, introduction to the columnar format](https://arrow.apache.org/docs/format/Intro.html), [PyArrow, data types and the in-memory data model](https://arrow.apache.org/docs/python/data.html), [Polars user guide, Polars and Apache Arrow](https://docs.pola.rs/user-guide/misc/arrow/)
- Unlocks: [[Polars]], [[DuckDB beyond the basics]]
- Shelf: Data · Depth: Deep

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #data
