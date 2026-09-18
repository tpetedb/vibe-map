---
title: "CSV done properly"
date: 2026-09-18
tags: [tech, data]
generated: 9a5104e7c6aa
---
# CSV done properly

CSV is a text file of records separated by line breaks and fields separated by commas, and it is the format every tool can read and no tool reads the same way. Reach for it when a human has to open the file, when the other side is a spreadsheet, or when the data is small enough that nobody cares about speed. RFC 4180 writes the rules down, but it is an Informational document that "does not specify an Internet standard of any kind", so it describes common practice rather than commanding it. The three fields that break naive code are a field with a comma in it, a field with a quote in it, and a field with a line break in it; all three are legal and all three need quoting. And for an agent: never split a CSV line on commas. Use a real reader, because the line you are splitting may not be a whole record.

**History.** RFC 4180 gives the grammar as file = [header CRLF] record *(CRLF record) [CRLF], so a record is a line and the line break is CRLF. It says "Fields containing line breaks (CRLF), double quotes, and commas should be enclosed in double-quotes", which is why a quoted field may contain a newline and still be one field. A double quote inside a quoted field is escaped by doubling it: "a double-quote appearing inside a field must be escaped by preceding it with another double quote". The MIME type it registers is text/csv, with the optional parameters charset and header, whose "Valid values are 'present' or 'absent'". Python's own csv documentation puts the reason for all of this plainly: "CSV format was used for many years prior to attempts to describe the format in a standardized way in RFC 4180. The lack of a well-defined standard means that subtle differences often exist in the data produced and consumed by different applications."

**Try in five minutes.** python3 -c "import csv,io;print(list(csv.reader(io.StringIO('a,\"b,c\",d'))))" and watch three fields come back, not four.

- Docs: [RFC 4180, Common Format and MIME Type for CSV Files](https://www.rfc-editor.org/rfc/rfc4180), [Python, the csv module: dialects, Sniffer and the newline rule](https://docs.python.org/3/library/csv.html), [DuckDB, reading CSV files and the CSV sniffer](https://duckdb.org/docs/stable/data/csv/overview)
- Unlocks: [[JSON Lines]], [[Parquet]], [[Schemas and schema evolution]]
- Shelf: Data · Depth: Basics

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #data
