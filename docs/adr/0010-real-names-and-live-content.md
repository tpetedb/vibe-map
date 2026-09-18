# ADR 0010: Real organisations and people appear by name as plain text, and everything they say is a link to their own words

Status: Accepted, 2026-09-18

## Context

The course is about the world the learner is walking into, and that world has names in it: Apple, Microsoft, the Linux kernel, the Python Software Foundation, DuckDB, three.js, Markus Winand. A campus of invented companies teaches nothing that transfers. Tom asked for the opposite: organisations, releases and opinions from notable people appearing in the game while it is played, from an RSS reader or another trustworthy source, with an off switch.

That request puts three risks in one feature.

The first is trade dress. A logo, a wordmark, an app icon, a product photograph or a recognisable building shape is somebody's property, and a game that ships one has taken it. The second is attribution. A sentence next to a real person's name is read as that person's sentence, and a model that writes one has put words in their mouth; the mentor encounters already ran into this and answered it (ADR 0008). The third is the feed itself. Anything pulled at runtime is content we did not review arriving in a page that carries our name, and a browser that fetches a third-party feed leaks every player to that third party.

The alternatives were all worse. Invented stand-ins ("Appel", "Mikrosoft") are the joke that ages badly and still teaches nothing. A hand-written snapshot of the industry is stale within a month and is our opinion rather than theirs. No live content at all was the state before this, and it is why the game's news card said "what happened in AI lately" about a file last touched at build time.

## Decision

Real names are used, and the three risks are answered separately.

- **Plain text only.** A real organisation, project or person appears by name, set in the game's own type, on original low-poly architecture. No logo, no wordmark, no product imagery, no app icon, no trade dress, no colour scheme copied from a brand, no building modelled on a real one.
- **A plaque on every one of them.** Each building and each person carries the same three facts: unofficial, not affiliated, and the sources it draws on, linked.
- **Every sentence is theirs, with the link next to it.** A line attributed to a person or an organisation is a headline they published or a paraphrase of their own published words, and the link is in the same element. Never an invented quote, never an invented opinion, never a summary a model wrote. `vibemap/news.py` takes the summary from the feed's own description, strips the markup and cuts the tail; there is no generation step in the path and there is not going to be one.
- **A registry with provenance, not a list of URLs.** `vibemap/data/sources.json` carries, per source, an id, a kind (organisation, person, project), the display name, the feed URL, the publisher, the reason it is trusted, the building it belongs to and the shelf tags from the tech tree. A source is first-party (their own blog, release feed or repository) or a recognised outlet in its field, and the reason is written down in the file rather than known by whoever added it. Every URL was opened and parsed before it was committed, a schema test keeps the registry honest offline, and a nightly job checks that every feed still answers.
- **The browser only ever talks to its own origin.** The feed is pulled by `vibe news` in a GitHub Action, baked into the game at build time and published as `news.json` next to the page. The hosted game refreshes from `./news.json` with a cache-buster and nothing else. A `file://` game does not even try. A failed refresh is silent and leaves the baked copy: a quiet feed is not an error a player should have to read.
- **A version travels with the file.** `news.json` carries a format version, and a game built against another one refuses it and keeps what it was built with, rather than reading half of it.
- **An off switch that is real.** `config/camp.toml` `[news] live` sets the default and the Settings dropdown Live world overrides it. Off means one class on `body`, one CSS rule hiding everything marked `live-feed`, and no fetch at all. A new feed-driven element obeys the switch by carrying the class, so the switch cannot rot as the world grows.

## Consequences

- The game can name the industry it is teaching, and a learner reading about uv or DuckDB sees what those projects shipped this week. That is the whole point of the feature.
- We never host anyone's mark and never speak for anyone. The worst case a plaque and a link cannot answer is a takedown request for a name, which is one line in `sources.json`.
- The summaries read like feeds, because they are feeds: an arXiv abstract begins like an arXiv abstract. Making them read better would mean writing them, which is the thing this record forbids.
- Adding a source is more work than adding a URL: someone has to say who publishes it and why it is trusted, and open it first. That is the intended cost.
- The feed is only as fresh as the last daily action, and a camp that never runs `vibe news` sees the copy it was built with. That is acceptable: the card says when it was pulled.
- A player who turns the live world off gets a smaller game, and every later feature that leans on the feed (the notification feed, the headquarters district) has to work with it off. The class and the helper are there so that stays cheap.
