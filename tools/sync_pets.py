"""Convert vendored pixel pet sprites into the packed format the CLI ships.

The sprites come from vscode-pets (MIT, Anthony Shaw). Only sets whose art was
authored for that repository, with no separate art licence, are vendored; the
sets that carry their own itch.io terms are skipped. See
vibemap/data/pets/CREDITS.md for who made what.

Pillow reads the GIFs here, at sync time only, so an installed `vibe` needs
nothing beyond the packed JSON.

    uv run python tools/sync_pets.py --source <vscode-pets checkout>
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
    palette: list[str] = [""]
    index: dict[str, int] = {}
    states = {
        state: [
            _pack(f.crop(box).resize(size, Image.NEAREST), palette, index)
            for f in frames
        ]
        for state, frames in raw.items()
    }
    return {
        "version": FORMAT_VERSION,
        "set": src.name,
        "width": size[0],
        "height": size[1],
        "fps": FPS,
        "palette": palette,
        "source": {
            "project": "vscode-pets",
            "url": f"{UPSTREAM}/tree/{commit}/media/{src.media}",
            "commit": commit,
            "author": src.author,
            "author_url": src.author_url,
            "licence": src.licence,
        },
        "states": states,
    }


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


def sync(source: Path, *, check: bool) -> int:
    media = source / "media"
    if not media.is_dir():
        raise SystemExit(f"{source} does not look like a vscode-pets checkout")
    commit = _commit(source)
    stale = 0
    for src in SOURCES:
        target = OUT / src.name / "frames.json"
        text = _dump(build(src, media, commit))
        if check:
            if not target.exists() or target.read_text() != text:
                print(f"stale: {target.relative_to(ROOT)}")
                stale += 1
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
        print(f"{target.relative_to(ROOT)}  {len(text) // 1024} KB")
    return stale


def verify() -> int:
    """The vendored data on its own: it decodes, and every set is credited."""
    problems = 0
    credits = (OUT / "CREDITS.md").read_text()
    for src in SOURCES:
        folder = OUT / src.name
        data = json.loads((folder / "frames.json").read_text())
        if data["version"] != FORMAT_VERSION:
            print(f"{src.name}: format version {data['version']}")
            problems += 1
        if not (folder / "LICENSE").exists():
            print(f"{src.name}: no LICENSE next to the sprites")
            problems += 1
        if data["source"]["author"] not in credits or src.name not in credits:
            print(f"{src.name}: missing from CREDITS.md")
            problems += 1
        top = data["palette"]
        for state, frames in data["states"].items():
            for n, rows in enumerate(frames):
                if len(rows) != data["height"]:
                    print(f"{src.name}/{state}[{n}]: {len(rows)} rows")
                    problems += 1
                for row in rows:
                    if sum(count for count, _ in row) != data["width"]:
                        print(f"{src.name}/{state}[{n}]: short row")
                        problems += 1
                    if any(i >= len(top) for _, i in row):
                        print(f"{src.name}/{state}[{n}]: palette index out of range")
                        problems += 1
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", type=Path, help="a vscode-pets checkout")
    ap.add_argument("--check", action="store_true", help="verify, write nothing")
    args = ap.parse_args()
    problems = verify() if args.check else 0
    if args.source:
        problems += sync(args.source, check=args.check)
    elif not args.check:
        ap.error("--source is required unless you only --check")
    if problems:
        print(f"{problems} problem(s); run tools/sync_pets.py --source <checkout>")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
