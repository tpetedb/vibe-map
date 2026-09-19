"""Vibe Code Camp: the terminal companion to Vibe Code Camp.

The package tracks the eight workstreams per evening, writes an Obsidian
vault as you go, reads the scores file with polars and DuckDB, and exchanges
a progress code with the game in game/vibe-map.html.
"""

from __future__ import annotations

import tomllib
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

UNKNOWN_VERSION = "0.0.0+unknown"


def _version() -> str:
    """The version, from one source: pyproject.toml.

    An installed package reads it from the metadata built out of that file. A
    bare checkout has no metadata, so it reads the file itself rather than a
    pin that would drift every release.
    """
    try:
        return version("vibe-map")
    except PackageNotFoundError:  # reason: running from source without an install
        pass
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    try:
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        return str(data["project"]["version"])
    except (OSError, KeyError, tomllib.TOMLDecodeError):
        return UNKNOWN_VERSION


__version__ = _version()
