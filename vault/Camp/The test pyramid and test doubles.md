---
title: "The test pyramid and test doubles"
date: 2026-09-24
tags: [tech, code]
generated: 1d8463c4fe63
---
# The test pyramid and test doubles

The test pyramid is a picture of how many tests of each kind a codebase should have: many small, fast unit tests at the bottom, fewer coarse-grained tests in the middle, and very few end-to-end tests on top. A test double is whatever stands in for a real thing during a test: a dummy, a fake, a stub, a spy or a mock. Reach for this topic when a test is slow, flaky or needs the network, and you want to replace the slow part without losing what the test proves. And for an agent: patch a name where the code under test looks it up, not where it is defined, and assert on the calls you care about with assert_called_once_with rather than on how the code is built inside.

**History.** Ham Vocke's The Practical Test Pyramid, published on martinfowler.com on 26 February 2018, credits Mike Cohn with the test pyramid in his book Succeeding with Agile, with unit tests, service tests and user interface tests from bottom to top, and sums it up as: "Write lots of small and fast unit tests. Write some more coarse-grained tests and very few high-level tests that test your application from end to end." Martin Fowler's TestDouble note of 17 January 2006 records Gerard Meszaros's term "test double", "a generic term for any case where you replace a production object for testing purposes". It names five kinds: dummies are passed around but never used, fakes have working implementations that take a shortcut, stubs "provide canned answers to calls made during the test", spies are stubs that also record how they were called, and mocks "are pre-programmed with expectations". Python's standard library has carried unittest.mock since version 3.3, which lets you "replace parts of your system under test with mock objects and make assertions about how they have been used". Its docs give the rule that trips most people: "you patch where an object is looked up, which is not necessarily the same place as where it is defined."

**Try in five minutes.** Write test_notify.py: a function notify(user, send) that calls send(user, "welcome"), and a unittest test that passes a Mock() as send and calls send.assert_called_once_with("ada", "welcome"). End the file with unittest.main() and run python3 test_notify.py. Then change "welcome" in notify and watch the test fail with the call it expected.

- Docs: [Ham Vocke on martinfowler.com, The Practical Test Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html), [Martin Fowler, TestDouble](https://martinfowler.com/bliki/TestDouble.html), [Python documentation, unittest.mock, mock object library](https://docs.python.org/3/library/unittest.mock.html), [Source: python.org, Python 3.3.0 release page](https://www.python.org/downloads/release/python-330/)
- Unlocks: [[pytest fixtures and parametrize]], [[Refactoring and code smells]]
- Shelf: Languages and code · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #code
