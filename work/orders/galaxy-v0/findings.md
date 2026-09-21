# What (phase 3 of docs/GALAXY.md)

`concept.html` in this folder is the look Tom approved on 2026-09-21: open it in a browser. It is a sketch with sample data and a CDN script; the product uses the vendored three.js, the real `PLACES` and `TECH`, the game's helpers (`mat()`, `keep()`, `discard()`, `esc()`), and the palette.

- The list twins first (journey, places), from `listing()`. Then the journey line and the chart drawn from the same data, tiny globes with each place lit at its coordinates, domes whose miniature comes from a small kit plus one landmark per place, neighbours in one region fanned out on a shared planet.
- Travel is a cut in version zero. The ship is phase 4.
- Landing opens the unchanged lesson sheet. One progress: done in one experience is done in the other.
- Behind the preference: `experience` in `config/camp.toml`, a row in Settings, `?experience=galaxy` for tests. Islands stay the default. Boot builds only the active experience; switching disposes the other through `discard()`.
- Every place gets a `look` and a `landmark` checked against a photograph of the real place before it ships.

# Learned since this order was written

- A landmark is a shape of the real place, checked against a photograph and against the place's own source, and it has to stand AT that place. The first concept gave Bell Labs at Murray Hill a horn antenna; the horn antenna stands on Crawford Hill in Holmdel, another town. The reviewer of `galaxy-places-schema` caught it; `concept.html` here is corrected.
- A landmark is never an organisation's mark: no feather, no snakes, no puffer fish, no helm. ADR 0010 says no logo, no wordmark, no trade dress, and that holds for a dome.
- Boot stays the last module. `galaxy-places-schema` makes the build place every module folder before `90-boot.js`, because boot runs at load and a Galaxy module's top-level bindings would not exist yet otherwise.

# Not in this order

The ship and its flight, building on a finished site, era arms, echoes as jumps, playing together. Each is a later phase with its own order.
