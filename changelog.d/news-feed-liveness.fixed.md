- The nightly check "every registered feed answers and parses" stopped calling
  a quiet feed a dead one. It now separates the two facts it used to confuse: a
  feed is alive when it answers and is still a feed the parser reads, and fresh
  when it has items today. arXiv announces Sunday to Thursday, so its cs.AI
  feed is legitimately empty every weekend and made the night, and the `v0.10.0`
  tag, red for no product reason.
- The check still fails, by name, for a feed that is really dead: a 404 or any
  other answer the request does not survive, a body that is not XML, XML that is
  not a feed, and a full feed whose entries no longer carry a title and a link
  this parser can read, which is what a changed format looks like from outside.
  Every failure line names the feed, the URL and what was wrong, and a feed that
  is alive with nothing new is printed rather than failed.
- `vibe news` and the game's News card are unchanged.
