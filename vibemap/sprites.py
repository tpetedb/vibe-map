"""Pixel sprites in the terminal, two pixels per cell.

One cell holds an upper half block (U+2580): the foreground paints the top
pixel, the background the bottom one. A transparent pixel leaves that half
unset, so the terminal's own background shows through.

The frames are vendored, packed and credited in `data/pets/`; see
`data/pets/CREDITS.md`. `tools/sync_pets.py` writes them, Pillow is a dev
dependency only and nothing here decodes an image at runtime.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from rich.style import Style
from rich.text import Text

PETS = Path(__file__).parent / "data" / "pets"
FORMAT_VERSION = 1
UPPER, LOWER = "▀", "▄"
STATES = ("idle", "walk", "happy", "sleep")

# A row of pixels: a colour per column, None where the sprite is transparent.
Row = list[str | None]
Frame = list[Row]


@dataclass(frozen=True, slots=True)
class Sheet:
    """One vendored set: its frames per state, and who to credit for them."""

    name: str
    width: int
    height: int
    fps: int
    states: dict[str, list[Frame]]
    author: str
    licence: str
    project: str
    url: str

    @property
    def credit(self) -> str:
        return f"{self.name} pixels by {self.author}, {self.project} ({self.licence})"

    def frames(self, state: str) -> list[Frame]:
        """The frames of a state; an unknown state idles rather than fails."""
        return self.states.get(state) or self.states["idle"]

    def frame(self, state: str, tick: int) -> Frame:
        frames = self.frames(state)
        return frames[tick % len(frames)]


def _unpack(rows: list[list[list[int]]], palette: list[str]) -> Frame:
    out: Frame = []
    for row in rows:
        line: Row = []
        for count, index in row:
            line.extend([palette[index] or None] * count)
        out.append(line)
    return out


@cache
def sheet(name: str) -> Sheet:
    """A vendored set by name.

    Raises:
        ValueError: when the packed file carries a version this release does
            not know how to read.
        FileNotFoundError: when no set of that name is vendored.
    """
    data = json.loads((PETS / name / "frames.json").read_text())
    version = data.get("version")
    if version != FORMAT_VERSION:
        raise ValueError(
            f"pet sprites {name}: format version {version!r}, this vibe reads "
            f"{FORMAT_VERSION}. Reinstall vibe-map or re-run tools/sync_pets.py."
        )
    palette = data["palette"]
    source = data["source"]
    return Sheet(
        name=data["set"],
        width=data["width"],
        height=data["height"],
        fps=data["fps"],
        states={
            state: [_unpack(f, palette) for f in frames]
            for state, frames in data["states"].items()
        },
        author=source["author"],
        licence=source["licence"],
        project=source["project"],
        url=source["url"],
    )


@cache
def available() -> tuple[str, ...]:
    """Every vendored set, in name order."""
    if not PETS.is_dir():
        return ()
    return tuple(sorted(p.name for p in PETS.iterdir() if (p / "frames.json").exists()))


def half_blocks(frame: Frame, *, offset: int = 0) -> Text:
    """A frame as half-block rows; each cell is the top pixel over the bottom.

    An odd last row pairs with transparency, so the sprite never loses a line.
    """
    pad = " " * offset
    out = Text()
    for y in range(0, len(frame), 2):
        top = frame[y]
        bottom = frame[y + 1] if y + 1 < len(frame) else [None] * len(top)
        out.append(pad)
        for x in range(len(top)):
            over, under = top[x], bottom[x] if x < len(bottom) else None
            if over is None and under is None:
                out.append(" ")
            elif over is None:
                out.append(LOWER, style=Style(color=under))
            else:
                out.append(UPPER, style=Style(color=over, bgcolor=under))
        out.append("\n")
    return out


def truecolor(env: dict[str, str] | None = None) -> bool:
    """Whether this terminal can paint 24-bit colour, the honest way."""
    e = os.environ if env is None else env
    if e.get("NO_COLOR"):
        return False
    term = e.get("TERM", "")
    if term in ("", "dumb"):
        return False
    if e.get("COLORTERM", "").lower() in ("truecolor", "24bit"):
        return True
    return "truecolor" in term or "direct" in term


def style_for(
    configured: str, species: str, *, env: dict[str, str] | None = None
) -> str:
    """Which renderer a species gets: the config wins, the terminal decides.

    `pixel` is honoured even without truecolor, because a forced setting is a
    choice; `auto` falls back to ASCII when the terminal cannot show it or the
    species has no vendored set.
    """
    if configured == "ascii":
        return "ascii"
    if species not in available():
        return "ascii"
    if configured == "pixel":
        return "pixel"
    return "pixel" if truecolor(env) else "ascii"
