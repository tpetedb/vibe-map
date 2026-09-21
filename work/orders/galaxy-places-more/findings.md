# Source

Issue 168 lists what the review of `galaxy-places-schema` left. Read it with `just work-thread galaxy-places-more`. This order takes the places half.

# What

- **Places the histories still need.** Topic histories name Heroku, Twitter, Cloudera, Snowflake, Cursor and Dagster, and no place exists for them. Read every topic's `history` field across both packs once more and add what is missing, each with its own source and coordinates. The five origin research orders own no place file and may not add one, so this order is where a missing place gets made.
- **Places the origin orders wished for.** Each origin order names on issue 168 the places it could not honestly do without (`just work-thread galaxy-places-more` lists them, signed by the builder that asked). The first: `nuenen`, Nuenen NL, 51.47, 5.55, for Dijkstra's EWD 447, signed "30th August 1974, Burroughs, Plataanstraat 5, NUENEN" (https://www.cs.utexas.edu/~EWD/transcriptions/EWD04xx/EWD447.html): the town, never the house, because the page prints a private address. When it exists, `concerns` takes EWD 447 as its primary origin and Parnas at Carnegie Mellon becomes the echo; that edit to the topic file is a follow-up for the content team, not this order's.
- **Landmarks.** Fifteen of 42 place files name a landmark their own source does not carry; two (`research-annex`, `city-office`) stand on no page and no map; an address is not a landmark. For each: find a source that carries it, or choose a plainer landmark that the place's page does carry (a lawn, a hill, a harbour, a tower block), or leave the landmark generic. Nothing that is an organisation's mark, a product, or a likeness of a named real building: ADR 0010 says no logo, no trade dress, no product imagery, no building modelled on a real one.
- **Comments in place files** that claim what their own source does not carry (eight are listed in the review): make them true or remove them. The next researcher copies them.
- **`docs/TOPICS.md`** says which reading of the rule is meant: an origin's page has to carry the year, the actor and what happened; the town may come from the place file's own source. It also stops telling a topic writer to add a place when none fits: name the place you need on the issue instead.
- **`vibemap/places.py`**: two origins of one topic at the same place are refused (today they load, and `vibe places <id>` prints the first twice); `problems(shelves=[])` and `problems(packs=[])` mean none, not all; a year given as a string is refused, not coerced; a place file's TOML error names `places/<file>`; the docstring of `payload()` stops promising a `--json` that does not exist.
- **`tools/checks.py`**: the weekly link check also reads the sources under `vibemap/data/places/`, with a declared user agent (one source answers 403 to the default one).
- **`AGENTS.md`**: the file map names `vibemap/places.py` and `vibemap/data/places/`.

The bar for a claim is unchanged: open every link, primary sources, a gap is honest and a guess is not.
