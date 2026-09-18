# Pixel pet sprites: where they come from and under what licence

The animated sprites in this folder are vendored from
[vscode-pets](https://github.com/tonybaloney/vscode-pets) by Anthony Shaw,
MIT licensed. Copied from commit `2c91214beb922288cca1938cddb607abc5f806b7`
(7 August 2026). `LICENSE` here and in every set folder is that project's MIT
licence text, unchanged.

The GIFs are not shipped. `tools/sync_pets.py` reads them from a checkout and
writes `frames.json`: a palette, run-length rows and four states, downscaled
with nearest neighbour to the size the terminal panel uses. The pixels are the
authors' pixels; nothing is recoloured or redrawn.

| Set | Species | Author | Source | Licence |
|---|---|---|---|---|
| `crab` | crab | [Marc Duiker](https://github.com/marcduiker), on a concept by [Karen Rustad Tolva](https://www.aldeka.net) | [vscode-pets `media/crab`](https://github.com/tonybaloney/vscode-pets/tree/main/media/crab) | MIT |
| `duck` | duck | [Marc Duiker](https://github.com/marcduiker) | [vscode-pets `media/rubber-duck`](https://github.com/tonybaloney/vscode-pets/tree/main/media/rubber-duck) | MIT |
| `turtle` | turtle | enkeefe, drawn with [Pixilart](https://www.pixilart.com/draw) | [vscode-pets `media/turtle`](https://github.com/tonybaloney/vscode-pets/tree/main/media/turtle) | MIT |
| `snail` | snail | [Kennet Shin](https://github.com/WoofWoof0) | [vscode-pets `media/snail`](https://github.com/tonybaloney/vscode-pets/tree/main/media/snail) | MIT |

## What was checked, and what was left behind

vscode-pets is MIT as a whole. Its
[credits](https://github.com/tonybaloney/vscode-pets/blob/main/docs/credits.md)
name a separate artist for several sets, and some of that art came from itch.io
under its own terms. Only sets drawn for vscode-pets itself by a contributor to
that repository, with no separate licence file next to the art, are vendored
here: those are covered by the project's MIT licence, which allows
redistribution and modification with the copyright notice kept.

Skipped, deliberately:

- **cat**: `media/README.md` says the author asked that the cat assets not be
  freely distributed. Not in the upstream repository, and not here.
- **dog**: `media/dog/license.txt` is CC BY-ND 4.0. No derivatives, and packing
  the frames makes one, so the dog stays out.
- **fox** (Elthen), **horse** (Onfe), **squirrel** (Azdner), **skeleton**
  (MonoPixelArt), **frog** (seethingswarm): adapted from itch.io packs whose own
  terms are not restated in the repository. Unclear, therefore skipped.
- **clippy, rocky, zappy, mod, deno, totoro, monkey, panda, raccoon, rat,
  chicken, cockatiel, snake, morph**: clearly licensed in several cases, but no
  species in this camp maps to them. Nothing to gain by copying them.

Every other species keeps the ASCII art from
[claude-buddy](https://github.com/btcromesh/claude-buddy) (MIT, Romesh
Niriella), and the ASCII crab is ours.
