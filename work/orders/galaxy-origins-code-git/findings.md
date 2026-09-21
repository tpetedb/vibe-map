# What

For every topic of the shelves git, code, formats (15 topic files, listed in `owns`): add `[[origins]]` as `galaxy-places-schema` defined them. One primary origin, where the topic lives in the Galaxy experience; further origins as echoes when the history honestly has more than one place (the relational model at IBM in 1970, Postgres at Berkeley in 1986).

# How

- Start from the topic's own `history` field and its existing `[[sources]]`: many already cite the page you need.
- A place must already exist under `vibemap/data/places/`. If a topic needs one that does not, do NOT create it (another order may be creating the same file): name it in your report with its coordinates and a source, and use the nearest honest existing place or leave that origin out.
- The bar for a claim is ADR 0010 and the findings of `galaxy-places-schema`: open every link, primary sources, no guesses. Where something "happened" in no single place (a standard, a protocol), the abstract places exist for that.
- `just tree` after editing topic files, then the build and the two sync tools.
