- The nightly check "every registered feed answers and parses" stopped calling
  a quiet feed a dead one. It now separates the two facts it used to confuse: a
  feed is alive when it answers and is still a feed the parser reads, and fresh
  when it has items today. arXiv announces Sunday to Thursday, so its cs.AI
  feed is legitimately empty every weekend and made the night, and the `v0.10.0`
  tag, red for no product reason.
- Empty stays a fault for every source that does not say it rests. The one
  digest says so in `vibemap/data/sources.json` with a new optional `rests`
  that carries the reason and the link, the way `trust` carries provenance; the
  other twenty keep a back catalogue in the feed, so nothing at all from them is
  an outage or a format this parser lost. The registry version is unchanged: the
  key is optional, so an older release reads the same file.
- The check still fails, by name, for a feed that is really dead: a 404 or any
  other answer the request does not survive, a body that is not XML, XML that is
  not a feed, a full feed whose entries no longer carry a title and a link this
  parser can read, and a full feed whose entry element itself was renamed, which
  counts as no entries at all and used to pass for a quiet day. Every failure
  line names the feed, the URL and what was wrong, and a feed that is alive with
  nothing new warns, so a green night still names it.
- `vibe news` and the game's News card are unchanged.
