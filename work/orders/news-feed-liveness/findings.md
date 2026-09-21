# What happened

The nightly workflow's job "every registered feed answers and parses" has failed on every weekend run, including the run on the `v0.10.0` tag (runs 35430110848, 35460712205, 35498923691), with:

```
AssertionError: arxiv-cs-ai: parsed, no items
```

It passed on Friday 18 September and passes on a Monday. arXiv announces new submissions Sunday to Thursday evening (US Eastern) and nothing on Friday or Saturday, and its feeds are rebuilt at midnight Eastern, so the cs.AI feed is legitimately empty through Saturday and Sunday. Sources: https://info.arxiv.org/help/availability.html and https://info.arxiv.org/help/rss.html

`tests/test_news.py::test_every_registered_feed_answers_and_parses` treats "parsed, no items" as dead. A nightly job that is red two days out of seven hides the day a feed really dies, and it made the 0.10.0 tag's run red for no product reason.

# What to do

- Separate the two facts the check confuses: the feed answered and is a feed (alive), and the feed has items today (fresh). Only the first is a liveness failure.
- Decide where that knowledge lives. A source that is a daily digest may say so in `vibemap/data/sources.json` (the registry is versioned: `SOURCES_VERSION`; a new optional key must not break an older file, and a new required one needs the version bumped and refused loudly, as AGENTS.md demands). Or the check may simply accept a well-formed empty feed for every source. Pick the simpler one that still catches a feed whose format changed so that the parser finds nothing in a full feed, and say why in the pull request.
- Make the failure message name the feed, the URL and what was wrong.
- Tests run offline: serve fixtures from a local server or feed the parser strings. The one test that touches the network stays `integration`.
- Do not change which feeds are registered.
