---
title: "pytest fixtures and parametrize"
date: 2026-09-24
tags: [tech, code]
generated: bf97c3f1c1f2
---
# pytest fixtures and parametrize

A pytest fixture is a function that prepares something a test needs, and a test asks for it by naming it as an argument. @pytest.mark.parametrize runs one test function once per row of inputs, so a table of cases replaces a pile of copied tests. Reach for them when your tests repeat the same setup, or when the same assertion should hold for many inputs. And for an agent: put cleanup after the yield in a yield fixture instead of in the test, and write one parametrized test with a case per row rather than one test per case.

**History.** In the pytest docs, "when pytest goes to run a test, it looks at the parameters in that test function's signature, and then searches for fixtures that have the same names as those parameters." A fixture is declared with the @pytest.fixture decorator, and a yield fixture runs its setup, passes an object back with yield, and runs any teardown code placed after the yield. A fixture's scope is one of function (the default), class, module, package or session. The parametrize docs show @pytest.mark.parametrize("test_input,expected", [("3+5", 8), ("2+4", 6), ("6*9", 42)]) and explain that the test_eval function "will run three times using them in turn". In the pytest changelog, 2.2.0 (2011-11-18) adds "a @pytest.mark.parametrize helper", and 2.3.0 (2012-10-19) introduces "@pytest.fixture which allows direct scoping and parametrization of funcarg factories".

**Try in five minutes.** Write test_cart.py with a yield fixture cart that yields an empty list and clears it after the yield, one test that asks for cart, and one test parametrized over three (price, qty, total) rows. Run uv run --with pytest pytest -o addopts="" --junitxml=report.xml test_cart.py and read the last line: 4 passed. The -o addopts="" keeps any pytest settings of the folder around it out of the run, and report.xml is the same count written for a machine, the way CI reads it. The first run downloads pytest into uv's cache; after that it runs offline.

- Docs: [pytest documentation, How to use fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html), [pytest documentation, How to parametrize fixtures and test functions](https://docs.pytest.org/en/stable/how-to/parametrize.html), [Source: the pytest changelog, entries 2.2.0 and 2.3.0](https://docs.pytest.org/en/stable/changelog.html)
- Unlocks: [[Property-based testing with Hypothesis]]
- Shelf: Languages and code · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #code
