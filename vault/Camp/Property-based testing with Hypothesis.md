---
title: "Property-based testing with Hypothesis"
date: 2026-09-24
tags: [tech, code]
generated: 58afa7d59121
---
# Property-based testing with Hypothesis

A property-based test states something that must hold for every input in a range, and a library picks the inputs, including edge cases you did not think of. Hypothesis is that library for Python, and its tests are still ordinary pytest or unittest functions. Reach for it when a function has a rule you can say in one line (decoding undoes encoding, sorting keeps every element) and a handful of hand-picked examples feels like luck. And for an agent: write the property, not the examples, and when Hypothesis reports a failing test case, read the input it prints before you touch the code.

**History.** The Hypothesis docs call it "the property-based testing library for Python": "you write tests which should pass for all inputs in whatever range you describe, and let Hypothesis randomly choose which of those inputs to check - including edge cases you might not have thought about." @given is the standard entrypoint, and it takes a strategy such as st.integers() that describes the inputs the test accepts. By default Hypothesis generates 100 random inputs, and the max_examples setting controls that. When the quickstart's test @given(st.integers(0, 200)) asserts n < 50, pytest reports the failing test case as n=50. The Hypothesis changelog records 0.0.1 on 2013-03-10 as "Initial release", and 1.0.0 on 2015-03-27.

**Try in five minutes.** Write test_props.py with encode (text to a list of (character, count) runs), decode (back again), and @given(st.text()) def test_decode_undoes_encode(text): assert decode(encode(text)) == text. Run uv run --with hypothesis --with pytest pytest -q test_props.py > props-out.txt. Then break encode on purpose and watch Hypothesis print the small input that fails.

- Docs: [Hypothesis documentation, Welcome to Hypothesis](https://hypothesis.readthedocs.io/en/latest/), [Hypothesis documentation, Quickstart](https://hypothesis.readthedocs.io/en/latest/quickstart.html), [Source: the Hypothesis changelog, 0.0.1 and 1.0.0](https://hypothesis.readthedocs.io/en/latest/changelog.html)
- Shelf: Languages and code · Depth: Deep

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #code
