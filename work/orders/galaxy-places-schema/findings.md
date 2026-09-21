# Decision

Tom accepted ADR 0015 on 2026-09-21 ("all approved, build it"). This order sets its status to Accepted and records one amendment: places are one file each under `vibemap/data/places/`, not one `places.toml`, for the reason ADR 0013 gave for topics, and so that several research orders can add origins at once without owning the same file.

# What this order builds (phase 1 of docs/GALAXY.md, the data half)

- `vibemap/data/places/<id>.toml`: id, name, kind (lab, company, university, city, network, cloud, orbit), region, era, `lat` and `lon` when the place is on Earth, `globe` (earth, datacentre, cloud), `look`, `landmark`, and a `source` link for the place itself.
- `[[origins]]` on a topic: `place`, `year`, `what` (one line), `source` (https), and `primary = true` on exactly one.
- `vibemap/places.py`: the loader and the schema, written the way `vibemap/topics.py` is. `problems(shelves=None)` returns one sentence per defect, naming the file; the criterion above calls it.
- Seed EVERY place the two packs will need, so the research orders that follow only reference places and never create them. Read each topic's `history` field for the candidates (Bell Labs, IBM San Jose, Xerox PARC, UC Berkeley, CERN, the University of Helsinki, MIT, Google, GitHub, Docker, OpenAI, Anthropic and so on), and add the abstract ones the design names: the cloud, the internet, a data centre, a standards body.
- Source the origins of the shell shelf's topics as the worked example.
- `vibe places`, origins in `vibe topic <id>`, `PLACES` injected by `tools/build.py` through `js_json()`, `tools/new_topic.py` scaffolds an origin, `docs/TOPICS.md` says how to write one.

# The bar for a claim (ADR 0010)

A real organisation or person appears by name, as plain text, and everything said about them links to their own words or to a primary source. Open every link you cite. Prefer the organisation's own history page, the original paper or announcement, a standards document. No paraphrased opinion, no "widely considered". If you cannot find a primary source for where something happened, say so in the pull request and leave that origin out rather than guess.

# Which places are seeded, and what is still missing (round 2)

Seeded after the first review, each read before it was written: `openai-sf`
(OpenAI, Inc.'s IRS Form 990, EIN 81-0861541, gives 3180 18th Street, San
Francisco), `amazon-seattle` (Amazon.com, Inc.'s EDGAR record gives 410 Terry
Avenue North, Seattle), `uc-santa-barbara` (where GNU's Bulletin of June 1989
puts Brian Fox), `ecma-international` (its own site gives Rue du Rhone 114,
Geneva; ECMA-262 and ECMA-404 are published there).

Still not seeded, with the reason as it was measured on 2026-09-21, not as it
was assumed: `iso.org` and `ansi.org` answer 403 to every client tried, and
openai.com does too, which is why OpenAI is sourced from its filings instead.
Mozilla, Meta and the W3C's contact pages answer 200 but carry no address in
their text at all. Where an organisation has no single address, the answer is
not a guess: `docs/TOPICS.md` says an open-source project sits at
`the-internet`, a hosted service at `the-cloud` and a specification at
`a-standards-body`, and it says how a research order adds a place when it
finds a source for one.
