"""Convert vendored pixel pet sprites into the packed format the CLI ships.

Two upstreams. The crab, duck, turtle and snail come from vscode-pets (MIT,
Anthony Shaw): only sets whose art was authored for that repository, with no
separate art licence, are vendored. The cat and the dog come from two CC0
packs by Shepardskin on OpenGameArt, unzipped side by side in one folder. See
vibemap/data/pets/CREDITS.md for who made what.

Pillow reads the GIFs here, at sync time only, so an installed `vibe` needs
nothing beyond the packed JSON.

    uv run python tools/sync_pets.py --source <vscode-pets checkout>
    uv run python tools/sync_pets.py --packs <folder of unzipped OGA packs>
    uv run python tools/sync_pets.py --check     the vendored data is sound
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "vibemap" / "data" / "pets"
FORMAT_VERSION = 1
# The panel is about twenty cells wide and one cell holds two pixels, so a
# sprite fits in twenty by sixteen pixels: at most eight rows of half blocks.
BOX = (20, 16)
FPS = 8
UPSTREAM = "https://github.com/tonybaloney/vscode-pets"


@dataclass(frozen=True, slots=True)
class Source:
    """One sprite set upstream, with the licence it is vendored under."""

    name: str
    media: str
    colour: str
    author: str
    author_url: str
    licence: str
    # Our state to the upstream file stem; a missing state falls back to idle.
    states: tuple[tuple[str, str], ...] = (
        ("idle", "idle"),
        ("walk", "walk"),
        ("happy", "swipe"),
        ("sleep", "lie"),
    )


SOURCES = (
    Source(
        "crab", "crab", "red", "Marc Duiker", "https://github.com/marcduiker", "MIT"
    ),
    Source(
        "duck",
        "rubber-duck",
        "yellow",
        "Marc Duiker",
        "https://github.com/marcduiker",
        "MIT",
    ),
    Source(
        "turtle",
        "turtle",
        "green",
        "enkeefe",
        "https://www.pixilart.com/draw",
        "MIT",
    ),
    Source(
        "snail", "snail", "brown", "Kennet Shin", "https://github.com/WoofWoof0", "MIT"
    ),
)


@dataclass(frozen=True, slots=True)
class Clip:
    """Where one state's frames sit inside a downloaded pack.

    Either a GIF of its own, or a run of cells in one row of a sprite sheet
    whose sprites stand on a flat background colour; an empty `cells` takes
    the whole row.
    """

    file: str
    row: int = -1
    cells: tuple[int, ...] = ()


@dataclass(frozen=True, slots=True)
class Pack:
    """A public-domain pack from OpenGameArt, and the folder it unzips to."""

    name: str
    folder: str
    project: str
    url: str
    author: str
    author_url: str
    licence: str
    states: tuple[tuple[str, Clip], ...]


SHEPARDSKIN = "https://opengameart.org/users/shepardskin"
PACKS = (
    # The cat ships one sheet: standing poses, then a walk cycle, then a run.
    # The two standing frames differ only in the tail, so idling flicks it.
    Pack(
        "cat",
        "cat sprite",
        "Cat Sprites",
        "https://opengameart.org/content/cat-sprites",
        "Shepardskin",
        SHEPARDSKIN,
        "CC0-1.0",
        (
            ("idle", Clip("catspritesoriginal.gif", 0, (0, 2))),
            ("walk", Clip("catspritesoriginal.gif", 1)),
            ("happy", Clip("catspritesoriginal.gif", 2)),
            ("sleep", Clip("catspritesoriginal.gif", 0, (3,))),
        ),
    ),
    # The dog ships one GIF per animation at three sizes; x1 is the original.
    Pack(
        "dog",
        "dog",
        "Dog Sprites",
        "https://opengameart.org/content/dog-sprites",
        "Shepardskin",
        SHEPARDSKIN,
        "CC0-1.0",
        (
            ("idle", Clip("dog_stand_lookx1.gif")),
            ("walk", Clip("dog_walkx1.gif")),
            ("happy", Clip("dog_stand_barkx1.gif")),
            ("sleep", Clip("dog_sitx1.gif")),
        ),
    ),
)


def _open_frames(path: Path):
    from PIL import Image, ImageSequence

    with Image.open(path) as im:
        return [f.convert("RGBA") for f in ImageSequence.Iterator(im)]


def _bbox(frames) -> tuple[int, int, int, int]:
    """The box that holds every non-transparent pixel of the whole set."""
    boxes = [f.getbbox() for f in frames]
    live = [b for b in boxes if b]
    if not live:
        raise SystemExit("a sprite set decoded to nothing but transparency")
    return (
        min(b[0] for b in live),
        min(b[1] for b in live),
        max(b[2] for b in live),
        max(b[3] for b in live),
    )


def _target(width: int, height: int) -> tuple[int, int]:
    """Fit inside BOX, keep the aspect, and keep the height even for pairing."""
    scale = min(BOX[0] / width, BOX[1] / height)
    w = max(1, min(BOX[0], round(width * scale)))
    h = max(2, min(BOX[1], round(height * scale)))
    return w, h + (h % 2)


def _pack(frame, palette: list[str], index: dict[str, int]) -> list[list[list[int]]]:
    """A frame as run-length rows of palette indices; 0 is transparent."""
    w, h = frame.size
    px = frame.load()
    rows: list[list[list[int]]] = []
    for y in range(h):
        row: list[list[int]] = []
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 128:
                idx = 0
            else:
                key = f"#{r:02x}{g:02x}{b:02x}"
                if key not in index:
                    index[key] = len(palette)
                    palette.append(key)
                idx = index[key]
            if row and row[-1][1] == idx:
                row[-1][0] += 1
            else:
                row.append([1, idx])
        rows.append(row)
    return rows


def _packed(name: str, states: dict[str, list], size: tuple[int, int], source: dict):
    """The shared tail: one palette for the set, run-length rows per frame."""
    palette: list[str] = [""]
    index: dict[str, int] = {}
    return {
        "version": FORMAT_VERSION,
        "set": name,
        "width": size[0],
        "height": size[1],
        "fps": FPS,
        "palette": palette,
        "source": source,
        "states": {
            state: [_pack(f, palette, index) for f in frames]
            for state, frames in states.items()
        },
    }


def build(src: Source, media: Path, commit: str) -> dict:
    from PIL import Image

    raw: dict[str, list] = {}
    for state, stem in src.states:
        path = media / src.media / f"{src.colour}_{stem}_8fps.gif"
        if path.exists():
            raw[state] = _open_frames(path)
    if "idle" not in raw:
        raise SystemExit(f"{src.name}: no idle animation in {media / src.media}")
    for state, _ in src.states:
        raw.setdefault(state, raw["idle"])
    box = _bbox([f for frames in raw.values() for f in frames])
    size = _target(box[2] - box[0], box[3] - box[1])
    states = {
        state: [f.crop(box).resize(size, Image.NEAREST) for f in frames]
        for state, frames in raw.items()
    }
    return _packed(
        src.name,
        states,
        size,
        {
            "project": "vscode-pets",
            "url": f"{UPSTREAM}/tree/{commit}/media/{src.media}",
            "commit": commit,
            "author": src.author,
            "author_url": src.author_url,
            "licence": src.licence,
        },
    )


def _keyed(im, background):
    """A sheet's flat background turned into transparency, pixel for pixel."""
    from PIL import Image

    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    src, dst = im.convert("RGB").load(), out.load()
    for y in range(im.height):
        for x in range(im.width):
            if src[x, y] != background:
                dst[x, y] = (*src[x, y], 255)
    return out


def _runs(flags: list[bool]) -> list[tuple[int, int]]:
    """The stretches where `flags` is False, as half-open spans."""
    out: list[tuple[int, int]] = []
    start: int | None = None
    for i, empty in enumerate(flags):
        if not empty and start is None:
            start = i
        elif empty and start is not None:
            out.append((start, i))
            start = None
    if start is not None:
        out.append((start, len(flags)))
    return out


def _rows(sheet) -> list[list]:
    """A sprite sheet split on its empty rows and columns, row by row."""
    px = sheet.load()
    w, h = sheet.size
    bands = _runs([all(px[x, y][3] == 0 for x in range(w)) for y in range(h)])
    out: list[list] = []
    for top, bottom in bands:
        gaps = _runs(
            [all(px[x, y][3] == 0 for y in range(top, bottom)) for x in range(w)]
        )
        out.append([sheet.crop((a, top, b, bottom)) for a, b in gaps])
    return out


def _clip(folder: Path, clip: Clip) -> list:
    """The frames of one state, from a GIF of its own or from a sheet row.

    These packs paint the background as a flat colour rather than leaving it
    transparent, so the colour in the top left corner is keyed out first.
    """
    frames = _open_frames(folder / clip.file)
    background = frames[0].convert("RGB").load()[0, 0]
    frames = [_keyed(f, background) for f in frames]
    if clip.row < 0:
        return frames
    rows = _rows(frames[0])
    if clip.row >= len(rows):
        raise SystemExit(f"{clip.file}: no row {clip.row}")
    cells = rows[clip.row]
    return [cells[i] for i in clip.cells] if clip.cells else cells


def _aligned(frames: list) -> list:
    """Every frame on one canvas, feet on the floor and centred.

    Each animation in these packs is drawn on its own canvas, so a shared
    bounding box would slide the creature around between states; standing it
    on the bottom edge keeps it in one place.
    """
    from PIL import Image

    boxes = [f.getbbox() for f in frames]
    if not all(boxes):
        raise SystemExit("a sprite frame decoded to nothing but transparency")
    tight = [f.crop(b) for f, b in zip(frames, boxes, strict=True)]
    w = max(t.width for t in tight)
    h = max(t.height for t in tight)
    out = []
    for t in tight:
        canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        canvas.paste(t, ((w - t.width) // 2, h - t.height))
        out.append(canvas)
    return out


def build_pack(pack: Pack, packs: Path) -> dict:
    from PIL import Image

    folder = packs / pack.folder
    if not folder.is_dir():
        raise SystemExit(f"{folder} is missing; unzip the {pack.project} pack there")
    raw = {state: _clip(folder, clip) for state, clip in pack.states}
    counts = [len(raw[state]) for state, _ in pack.states]
    flat = _aligned([f for state, _ in pack.states for f in raw[state]])
    size = _target(flat[0].width, flat[0].height)
    states: dict[str, list] = {}
    at = 0
    for (state, _), count in zip(pack.states, counts, strict=True):
        states[state] = [f.resize(size, Image.NEAREST) for f in flat[at : at + count]]
        at += count
    return _packed(
        pack.name,
        states,
        size,
        {
            "project": pack.project,
            "url": pack.url,
            "author": pack.author,
            "author_url": pack.author_url,
            "licence": pack.licence,
        },
    )


def _commit(source: Path) -> str:
    out = subprocess.run(
        ["git", "-C", str(source), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return out.stdout.strip()


def _dump(data: dict) -> str:
    return json.dumps(data, separators=(",", ":"), sort_keys=False) + "\n"


def _write(name: str, data: dict, *, check: bool) -> int:
    """Write one packed set, or say whether the vendored copy still matches."""
    target = OUT / name / "frames.json"
    text = _dump(data)
    if check:
        if not target.exists() or target.read_text() != text:
            print(f"stale: {target.relative_to(ROOT)}")
            return 1
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text)
    print(f"{target.relative_to(ROOT)}  {len(text) // 1024} KB")
    return 0


def sync(source: Path, *, check: bool) -> int:
    media = source / "media"
    if not media.is_dir():
        raise SystemExit(f"{source} does not look like a vscode-pets checkout")
    commit = _commit(source)
    return sum(
        _write(src.name, build(src, media, commit), check=check) for src in SOURCES
    )


def sync_packs(packs: Path, *, check: bool) -> int:
    if not packs.is_dir():
        raise SystemExit(f"{packs} is not a folder of unzipped OpenGameArt packs")
    return sum(
        _write(pack.name, build_pack(pack, packs), check=check) for pack in PACKS
    )


# Every vendored set: its name, who to credit and how the LICENSE next to the
# frames must open, so a set can never arrive without its terms.
VENDORED = tuple(
    [(s.name, s.author, "MIT License") for s in SOURCES]
    + [(p.name, p.author, "Creative Commons Legal Code") for p in PACKS]
)


def verify() -> int:
    """The vendored data on its own: it decodes, and every set is credited."""
    problems = 0
    credits = (OUT / "CREDITS.md").read_text()
    for name, author, licence_head in VENDORED:
        folder = OUT / name
        data = json.loads((folder / "frames.json").read_text())
        if data["version"] != FORMAT_VERSION:
            print(f"{name}: format version {data['version']}")
            problems += 1
        licence = folder / "LICENSE"
        if not licence.exists():
            print(f"{name}: no LICENSE next to the sprites")
            problems += 1
        elif not licence.read_text().startswith(licence_head):
            print(f"{name}: LICENSE is not the {licence_head} text")
            problems += 1
        if author not in credits or name not in credits:
            print(f"{name}: missing from CREDITS.md")
            problems += 1
        if data["source"]["author"] != author:
            print(f"{name}: frames.json credits {data['source']['author']}")
            problems += 1
        top = data["palette"]
        for state in ("idle", "walk", "happy", "sleep"):
            if not data["states"].get(state):
                print(f"{name}: no {state} frames")
                problems += 1
        for state, frames in data["states"].items():
            for n, rows in enumerate(frames):
                if len(rows) != data["height"]:
                    print(f"{name}/{state}[{n}]: {len(rows)} rows")
                    problems += 1
                for row in rows:
                    if sum(count for count, _ in row) != data["width"]:
                        print(f"{name}/{state}[{n}]: short row")
                        problems += 1
                    if any(i >= len(top) for _, i in row):
                        print(f"{name}/{state}[{n}]: palette index out of range")
                        problems += 1
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", type=Path, help="a vscode-pets checkout")
    ap.add_argument("--packs", type=Path, help="a folder of unzipped OpenGameArt packs")
    ap.add_argument("--check", action="store_true", help="verify, write nothing")
    args = ap.parse_args()
    problems = verify() if args.check else 0
    if args.source:
        problems += sync(args.source, check=args.check)
    if args.packs:
        problems += sync_packs(args.packs, check=args.check)
    if not args.source and not args.packs and not args.check:
        ap.error("--source or --packs is required unless you only --check")
    if problems:
        print(f"{problems} problem(s); re-run tools/sync_pets.py with its sources")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
