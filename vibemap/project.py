"""Where the learner's camp lives: the project root and the package's own data.

The CLI can be installed globally (`uv tool install vibe-map`) and run from
any folder, so nothing may assume the package sits inside the repo. The
project root is the nearest ancestor of the working directory that holds a
camp marker (or `VIBE_HOME` when set); package data ships inside `vibemap/data`.

Journey configuration lives in `config/camp.toml`. The retired `vibe.toml` at
the camp root is still accepted as a marker and still read, for one release.
"""

from __future__ import annotations

import os
from functools import cache
from importlib import resources
from pathlib import Path

CAMP_CONFIG = Path("config") / "camp.toml"
LEGACY_CONFIG = Path("vibe.toml")
MARKERS = (CAMP_CONFIG, LEGACY_CONFIG, Path("game") / "vibe-map.html")


@cache
def root() -> Path:
    """The camp folder: VIBE_HOME, else the nearest ancestor with a camp marker.

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


def config_path(base: Path | None = None) -> Path:
    """The journey configuration: config/camp.toml, else the retired vibe.toml.

    A camp that has neither gets the new path, so the first write lands there.
    """
    b = base or root()
    camp = b / CAMP_CONFIG
    if camp.exists():
        return camp
    legacy = b / LEGACY_CONFIG
    return legacy if legacy.exists() else camp


def nearest_config(start: Path) -> Path:
    """The journey configuration for START: its own, else an ancestor camp's.

    A fork under `workspace/forks/` has no camp.toml, so its build takes the
    camp it sits in; only its `src/config/` differs from the product build.
    """
    s = start.resolve()
    for candidate in (s, *s.parents):
        for name in (CAMP_CONFIG, LEGACY_CONFIG):
            if (candidate / name).exists():
                return candidate / name
    return s / CAMP_CONFIG


def legacy_config_in_use(base: Path | None = None) -> Path | None:
    """The vibe.toml being read instead of config/camp.toml, if any."""
    b = base or root()
    legacy = b / LEGACY_CONFIG
    return legacy if legacy.exists() and not (b / CAMP_CONFIG).exists() else None


def data_path(name: str) -> Path:
    """A file shipped inside the package (campaign.json, resources.md)."""
    with resources.as_file(resources.files("vibemap").joinpath("data", name)) as p:
        return Path(p)


def data_dir(name: str):
    """A folder shipped inside the package, as a context manager (see data_path)."""
    return resources.as_file(resources.files("vibemap").joinpath("data", name))


def data_text(name: str) -> str:
    return resources.files("vibemap").joinpath("data", name).read_text(encoding="utf-8")
