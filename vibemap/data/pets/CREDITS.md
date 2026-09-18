# Pixel pet sprites: where they come from and under what licence

Two upstreams, both checked on the page that states the terms.

The crab, duck, turtle and snail are vendored from
[vscode-pets](https://github.com/tonybaloney/vscode-pets) by Anthony Shaw,
MIT licensed. Copied from commit `2c91214beb922288cca1938cddb607abc5f806b7`
(7 August 2026). `LICENSE` in those set folders is that project's MIT licence
text, unchanged.

The cat and the dog are two CC0 packs by **Shepardskin** on OpenGameArt,
downloaded on 18 September 2026. Both pages state the licence as "CC0
(Creative Commons Zero)" and add, under Copyright/Attribution Instructions:
"No attribution necessary, unless you want to. Just credit Shepardskin and/or
a link to my twitter." Credit is given here and in `vibe pet` anyway. `LICENSE`
in those two set folders is the CC0 1.0 Universal legal code.

The GIFs are not shipped. `tools/sync_pets.py` reads them from a checkout or
from the unzipped packs and writes `frames.json`: a palette, run-length rows
and four states, downscaled with nearest neighbour to the size the terminal
panel uses. The OpenGameArt packs paint their background as a flat colour
rather than leaving it transparent, so that one colour is keyed out and each
frame is stood on the bottom edge of a shared canvas. Nothing else is changed:
the pixels are the authors' pixels, recoloured nowhere and redrawn nowhere.

| Set | Species | Author | Source | Licence |
|---|---|---|---|---|
| `crab` | crab | [Marc Duiker](https://github.com/marcduiker), on a concept by [Karen Rustad Tolva](https://www.aldeka.net) | [vscode-pets `media/crab`](https://github.com/tonybaloney/vscode-pets/tree/main/media/crab) | MIT |
| `duck` | duck | [Marc Duiker](https://github.com/marcduiker) | [vscode-pets `media/rubber-duck`](https://github.com/tonybaloney/vscode-pets/tree/main/media/rubber-duck) | MIT |
| `turtle` | turtle | enkeefe, drawn with [Pixilart](https://www.pixilart.com/draw) | [vscode-pets `media/turtle`](https://github.com/tonybaloney/vscode-pets/tree/main/media/turtle) | MIT |
| `snail` | snail | [Kennet Shin](https://github.com/WoofWoof0) | [vscode-pets `media/snail`](https://github.com/tonybaloney/vscode-pets/tree/main/media/snail) | MIT |
| `cat` | cat | [Shepardskin](https://opengameart.org/users/shepardskin) | [Cat Sprites](https://opengameart.org/content/cat-sprites) | CC0-1.0 |
| `dog` | dog | [Shepardskin](https://opengameart.org/users/shepardskin) | [Dog Sprites](https://opengameart.org/content/dog-sprites) | CC0-1.0 |

Which frames became which state:

| Set | idle | walk | happy | sleep |
|---|---|---|---|---|
| `cat` | the two standing poses of the sheet, so idling flicks the tail | the walk row | the run row | the sitting pose |
| `dog` | `dog_stand_lookx1` | `dog_walkx1` | `dog_stand_barkx1` | `dog_sitx1` |

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
  freely distributed. Not in the upstream repository, and not here. The cat in
  this folder is the CC0 one from OpenGameArt instead.
- **dog**: `media/dog/license.txt` is CC BY-ND 4.0. No derivatives, and packing
  the frames makes one, so that dog stays out. The dog in this folder is the
  CC0 one from OpenGameArt instead.
- **fox** (Elthen), **horse** (Onfe), **squirrel** (Azdner), **skeleton**
  (MonoPixelArt), **frog** (seethingswarm): adapted from itch.io packs whose own
  terms are not restated in the repository. Unclear, therefore skipped.
- **clippy, rocky, zappy, mod, deno, totoro, monkey, panda, raccoon, rat,
  chicken, cockatiel, snake, morph**: clearly licensed in several cases, but no
  species in this camp maps to them. Nothing to gain by copying them.

Every other species keeps the ASCII art from
[claude-buddy](https://github.com/btcromesh/claude-buddy) (MIT, Romesh
Niriella), and the ASCII crab is ours.
