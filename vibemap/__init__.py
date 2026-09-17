"""Vibe Code Camp: the terminal companion to Vibe Code Camp.

The package tracks the eight workstreams per evening, writes an Obsidian
vault as you go, reads the scores file with polars and DuckDB, and exchanges
a progress code with the game in game/vibe-map.html.
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

# One source for the version: pyproject.toml, through the installed metadata.
# A checkout that is not installed (a bare `python -c`) falls back to the pin.
try:
    __version__ = version("vibe-map")
except PackageNotFoundError:  # reason: running from source without an install
    __version__ = "0.5.0"
