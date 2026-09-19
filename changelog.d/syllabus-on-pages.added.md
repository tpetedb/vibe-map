- The syllabus is published from this repository: `tools/gen_syllabus.py` writes
  the repetitive blocks of `docs/SYLLABUS.md` (the course map, the mentors, the
  artifacts, the tech tree) from `vibemap/data/` and renders the whole file into
  `docs/site/syllabus.html`, which `pages.yml` deploys next to the game as
  `syllabus.html`. One file, the game's palette, system fonts, a sticky table of
  contents, print styles, light and dark, and no third-party request. `just
  syllabus` regenerates it and `--check` fails when it is stale.
- `config/camp.toml` gains `[game] site_url`, where the product is published.
  The game's Roadmap now resolves "the syllabus" through it, so the link is the
  neighbour on that site and the product's URL anywhere else. No link to a page
  in a personal claude.ai account is left, and a repo test keeps it that way.
