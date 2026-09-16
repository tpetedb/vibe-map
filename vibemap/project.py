"""Where the learner's camp lives: the project root and the package's own data.

The CLI can be installed globally (`uv tool install vibe-map`) and run from
any folder, so nothing may assume the package sits inside the repo. The
project root is the nearest ancestor of the working directory that holds a
`vibe.toml` (or `VIBE_HOME` when set); package data ships inside `vibemap/data`.
"""

from __future__ import annotations

import os
from functools import cache
from importlib import resources
from pathlib import Path

MARKERS = ("vibe.toml", "game/vibe-map.html")


@cache
def root() -> Path:
    """The camp folder: VIBE_HOME, else the nearest ancestor with a vibe.toml.

    Falls back to the working directory so `vibe init` and `vibe toolbelt`
    work anywhere; commands that need a camp check for the markers themselves.
    """
    env = os.environ.get("VIBE_HOME")
    if env:
        return Path(env).expanduser().resolve()
    here = Path.cwd().resolve()
    for candidate in (here, *here.parents):
        if any((candidate / m).exists() for m in MARKERS):
            return candidate
    return here


def is_camp(path: Path | None = None) -> bool:
    p = path or root()
    return any((p / m).exists() for m in MARKERS)


def data_path(name: str) -> Path:
    """A file shipped inside the package (campaign.json, resources.md)."""
    with resources.as_file(resources.files("vibemap").joinpath("data", name)) as p:
        return Path(p)


def data_text(name: str) -> str:
    return resources.files("vibemap").joinpath("data", name).read_text(encoding="utf-8")
