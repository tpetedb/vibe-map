---
title: "TOML in practice: pyproject.toml"
date: 2026-09-16
tags: [tech, formats]
---
# TOML in practice: pyproject.toml

TOML is INI with types. [tables] group keys; key = "value" pairs are typed (strings, numbers, booleans, dates, arrays); `[[arrays.of.tables]]` repeat asection, one block per item. Python packaging chose it because it is unambiguous, has a small spec, and stays readable when hand-edited: pyproject.toml declares the package, its dependencies and the tool settings (ruff, pytest) in one file.

**History.** TOML was started by Tom Preston-Werner in 2013 and reached 1.0.0 in January 2021. PEP 518 (2016) introduced pyproject.toml for build requirements, PEP 621 (2020) added the [project] table, and tomllib joined the standard library with Python 3.11 in October 2022.

**Try in five minutes.** Read pyproject.toml in this repo and add a dependency, then uv sync.

- Docs: [TOML 1.0.0 spec](https://toml.io/en/v1.0.0), [Python packaging: writing your pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/), [tomllib](https://docs.python.org/3/library/tomllib.html), [Source: TOML v0.1.0 release (March 2013)](https://github.com/toml-lang/toml/releases/tag/v0.1.0), [Source: TOML 1.0.0 release (January 2021)](https://github.com/toml-lang/toml/releases/tag/1.0.0), [Source: PEP 518 (created May 2016)](https://peps.python.org/pep-0518/), [Source: PEP 621 (created June 2020)](https://peps.python.org/pep-0621/), [Source: Python 3.11.0 release (October 2022, PEP 680 tomllib)](https://www.python.org/downloads/release/python-3110/)
- Unlocks: [[Python libraries - what they are for]]
- Shelf: Config and formats · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #formats
