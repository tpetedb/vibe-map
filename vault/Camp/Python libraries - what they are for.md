---
title: "Python libraries: what they are for"
date: 2026-09-16
tags: [tech, feudal]
---
# Python libraries: what they are for

pandas (tables), numpy (numbers), matplotlib/plotly (charts), requests/httpx (talk to APIs), duckdb (SQL on files), pydantic (validate data), fastapi (build an API), typer/click (build a CLI), playwright (drive a browser), pytest (tests). Install with uv; import only what removes real work.

**History.** NumPy 2005 (1.0 in 2006), pandas 2008 (Wes McKinney, at a hedge fund), requests 2011, pytest 2004 lineage, FastAPI 2018, pydantic 2017, Playwright 2020, DuckDB 2019 (started at CWI in 2018). The stack is young; most of it postdates the iPhone.

**Try in five minutes.** uv pip install pandas, then python3 -c "import pandas as pd; print(pd.read_csv('data/scores.csv').describe())".

- Docs: [pandas 10 minutes](https://pandas.pydata.org/docs/user_guide/10min.html), [Requests](https://requests.readthedocs.io), [pytest](https://docs.pytest.org), [FastAPI](https://fastapi.tiangolo.com), [Source: numpy.org, About NumPy](https://numpy.org/about/), [Source: pandas.pydata.org, About pandas](https://pandas.pydata.org/about/), [Source: requests release history on PyPI (February 2011)](https://pypi.org/project/requests/#history), [Source: pytest history](https://docs.pytest.org/en/stable/history.html), [Source: FastAPI release history on PyPI (December 2018)](https://pypi.org/project/fastapi/#history), [Source: pydantic v0.1 release (June 2017)](https://github.com/pydantic/pydantic/releases/tag/v0.1), [Source: Playwright v1.0.0 release (May 2020)](https://github.com/microsoft/playwright/releases/tag/v1.0.0), [Source: DuckDB v0.1.0 release (June 2019)](https://github.com/duckdb/duckdb/releases/tag/v0.1.0)
- Unlocks: [[Building and consuming APIs]], [[Tests and evals]]
- Age: Feudal Age · Level: Junior

<!-- generated from tools/tech.py; edit there -->

Back to [[Tech tree]]

#tech #feudal
