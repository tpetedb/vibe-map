"""Places as data: where a topic happened, one TOML file per place.

vibemap/data/places/ is the map. Every file is one place (`<id>.toml`) with
its kind, the arm of the galaxy it sits in, where it is on Earth when it is on
Earth, the look a diorama builder takes from it, and a source link for the
place itself. A topic points at a place through `[[origins]]` (see
vibemap/topics.py); this module is the registry those origins are checked
against. ADR 0015 is the decision, docs/GALAXY.md the design.

Nothing is guessed: an unknown kind, era, region, globe or look, coordinates
on a place that is not on Earth, a missing source and an origin that names a
place no file declares are all refused with the file name in the message.
`problems()` is the other half: it reports, one sentence per defect, instead
of stopping at the first, so a research order can see all its work at once.
"""

from __future__ import annotations

import re
import tomllib
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError

from vibemap import project, topics
from vibemap.topics import Origin, Topic

PLACES_DIR = "places"


@dataclass(frozen=True, slots=True)
class Era:
    """One arm of the map: the stretch of the story a place belongs to.

    The eras live here and not in the tech tree's `tree.toml`, because an era
    places a place, not a topic: a lab sits in one arm for its whole life
    while the topics made there span decades.
    """

    id: str
    name: str
    first: int
    last: int | None


ERAS: tuple[Era, ...] = (
    Era("mainframe", "Mainframes and Unix", 1960, 1979),
    Era("personal", "Personal computers and the web", 1980, 1999),
    Era("open-source", "Open source and the cloud", 2000, 2011),
    Era("data", "Data and deep learning", 2012, 2021),
    Era("agents", "Agents", 2022, None),
)

# What a place is. The kind decides the diorama kit and the palette family:
# a campus is not a station and a nebula is neither.
KINDS = (
    "lab",
    "company",
    "university",
    "city",
    "network",
    "cloud",
    "orbit",
    "standards",
    "foundation",
)
# Which tiny globe carries the place. Only `earth` has coordinates: the cloud
# and a data centre are real, but they are not anywhere in particular.
GLOBES = ("earth", "datacentre", "cloud")
# The diorama builder and palette family the place is drawn with.
LOOKS = (
    "campus",
    "tower",
    "lab",
    "hall",
    "racks",
    "nebula",
    "lanes",
    "station",
    "house",
    "harbour",
)
# Coarse enough that a new place never needs a new region, fine enough to
# group the domes that share a planet.
REGIONS = (
    "us-west",
    "us-east",
    "us-central",
    "canada",
    "latin-america",
    "europe-west",
    "europe-north",
    "europe-central",
    "europe-south",
    "africa",
    "middle-east",
    "asia-east",
    "asia-south",
    "asia-southeast",
    "oceania",
    "orbit",
    "everywhere",
)
# A landmark names one silhouette the diorama builder draws, so it is a slug
# and not prose. It is a thing that stands at the place, never an
# organisation's logo, wordmark or mascot. `generic-marker` makes no physical
# landmark claim. ADR 0010 gives a real organisation
# its name as plain text and nothing else, and a place inherits that rule.
LANDMARK = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")


class Place(BaseModel):
    """One place of the map, as its file declares it."""

    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    kind: str
    region: str
    era: str
    globe: str = "earth"
    # Where the dome stands on the tiny globe. Omitted off the earth globe.
    lat: float | None = None
    lon: float | None = None
    look: str
    landmark: str
    source: str

    @property
    def on_earth(self) -> bool:
        return self.globe == "earth"

    @property
    def where(self) -> str:
        """One short line for a table: the coordinates, else the globe."""
        if self.lat is None or self.lon is None:
            return self.globe
        return f"{self.lat:.3f}, {self.lon:.3f}"


def _read(path: Path) -> dict[str, Any]:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as e:
        raise ValueError(f"places/{path.name} is not valid TOML: {e}") from e


def _fail(where: str, msg: str) -> None:
    raise ValueError(f"{where}: {msg}")


def _one_of(where: str, field: str, value: str, allowed: Sequence[str]) -> None:
    if value not in allowed:
        _fail(where, f"unknown {field} {value!r}; one of: {', '.join(allowed)}")


def _check(place: Place, where: str) -> None:
    """Everything about one place that a person can get wrong by hand."""
    _one_of(where, "kind", place.kind, KINDS)
    _one_of(where, "region", place.region, REGIONS)
    _one_of(where, "era", place.era, tuple(e.id for e in ERAS))
    _one_of(where, "globe", place.globe, GLOBES)
    _one_of(where, "look", place.look, LOOKS)
    if not LANDMARK.fullmatch(place.landmark):
        _fail(where, "landmark names one shape to draw, as a slug (great-dome)")
    if not place.source.startswith("https://"):
        _fail(where, "source is an https link to a page about the place itself")
    has_coords = place.lat is not None and place.lon is not None
    if place.on_earth and not has_coords:
        _fail(where, "a place on the earth globe needs lat and lon")
    if not place.on_earth and (place.lat is not None or place.lon is not None):
        _fail(where, f"a place on the {place.globe} globe is nowhere on Earth")
    if (place.lat is None) != (place.lon is None):
        _fail(where, "lat and lon come together or not at all")
    if has_coords and not (-90 <= float(place.lat or 0) <= 90):
        _fail(where, f"lat {place.lat} is not a latitude")
    if has_coords and not (-180 <= float(place.lon or 0) <= 180):
        _fail(where, f"lon {place.lon} is not a longitude")


def load_from(root: Path) -> tuple[Place, ...]:
    """Read one places folder, validated. Separate from load() so a test can
    hand it a folder of its own and watch a bad file fail."""
    found: list[Place] = []
    for path in sorted(root.glob("*.toml")):
        where = f"places/{path.name}"
        try:
            place = Place.model_validate(_read(path))
        except ValidationError as e:
            raise ValueError(f"{where} does not match the Place schema:\n{e}") from e
        if place.id != path.stem:
            _fail(where, f"declares id {place.id!r}; a place file is named <id>.toml")
        _check(place, where)
        found.append(place)
    return tuple(sorted(found, key=lambda p: p.id))


@cache
def all_places() -> tuple[Place, ...]:
    """The packaged places, read once per process."""
    with project.data_dir(PLACES_DIR) as base:
        return load_from(Path(base))


def by_id() -> dict[str, Place]:
    return {p.id: p for p in all_places()}


def get(place_id: str) -> Place:
    """One place, or a ValueError naming a few of the ids that do exist."""
    found = by_id().get(place_id)
    if found is None:
        near = sorted(p for p in by_id() if place_id in p) or sorted(by_id())[:8]
        raise ValueError(
            f"unknown place {place_id!r}; try one of: {', '.join(near[:8])}"
        )
    return found


def era(era_id: str) -> Era:
    for e in ERAS:
        if e.id == era_id:
            return e
    raise ValueError(f"unknown era {era_id!r}")


def sort_key(origin: Origin) -> tuple[int, int, str]:
    """The primary origin first, then by year: where the topic lives, then its
    echoes."""
    return (0 if origin.primary else 1, origin.year, origin.place)


def origins_of(topic: Topic, known: Iterable[Place] | None = None) -> list[Origin]:
    """One topic's origins, primary first, every place resolved.

    A place no file declares is refused here, with the topic's file name, so
    the fault is reported where it was written and not where it is drawn.
    """
    ids = {p.id for p in (all_places() if known is None else known)}
    where = f"{topic.pack}/{topic.id}.toml"
    for origin in topic.origins:
        if origin.place not in ids:
            _fail(
                where,
                f"names the place {origin.place!r}, and no file in"
                " vibemap/data/places/ declares it",
            )
    return sorted(topic.origins, key=sort_key)


def origin_at(topic: Topic, place_id: str) -> Origin:
    """What this topic says happened at one place."""
    found = next((o for o in topic.origins if o.place == place_id), None)
    if found is None:
        raise ValueError(f"{topic.id} has no origin at {place_id!r}")
    return found


def topics_by_place() -> dict[str, list[Topic]]:
    """Every place's topics, primary first within the place, in tree order."""
    out: dict[str, list[Topic]] = {p.id: [] for p in all_places()}
    for topic in topics.all_topics():
        for origin in origins_of(topic):
            out[origin.place].append(topic)
    return out


def _selected(
    shelves: Sequence[str] | None, packs: Sequence[str] | None
) -> list[Topic]:
    """The topics a selection names, refusing a name the tree does not have.

    A misspelt shelf would otherwise select nothing, and nothing has no
    defects: the order asking would pass with nothing checked.
    """
    chosen = topics.all_topics()
    for one, many, asked, known in (
        ("shelf", "shelves", shelves, {t.shelf for t in chosen}),
        ("pack", "packs", packs, {t.pack for t in chosen}),
    ):
        for name in asked or ():
            if name not in known:
                raise ValueError(
                    f"unknown {one} {name!r}; the {many} are:"
                    f" {', '.join(sorted(known))}."
                )
    if shelves is not None:
        chosen = tuple(t for t in chosen if t.shelf in shelves)
    if packs is not None:
        chosen = tuple(t for t in chosen if t.pack in packs)
    return list(chosen)


def problems(
    shelves: Sequence[str] | None = None, packs: Sequence[str] | None = None
) -> list[str]:
    """One sentence per defect, each naming the file, for the topics selected.

    `shelves` and `packs` narrow the selection the way a research order is cut:
    one shelf of the tree, or a whole pack. With neither, every topic is read.
    A shelf or a pack the tree does not have is itself the first defect, so a
    typo in an order's command fails it instead of checking nothing. An empty
    list means nothing is wrong with what was asked about.
    """
    try:
        known = {p.id for p in all_places()}
        chosen = _selected(shelves, packs)
    except ValueError as e:  # a file that cannot be loaded is the first defect
        return [str(e)]
    out: list[str] = []
    for topic in chosen:
        where = f"{topic.pack}/{topic.id}.toml"
        if not topic.origins:
            out.append(
                f"{where} has no origin: a topic needs a place, a year, one line"
                " and an https source that says so."
            )
            continue
        for origin in topic.origins:
            if origin.place not in known:
                out.append(
                    f"{where} names the place {origin.place!r}, and no file in"
                    " vibemap/data/places/ declares it."
                )
    return out


def payload() -> dict[str, object]:
    """The places and the origins as one blob, for the build.

    The same facts `vibe places` and `vibe topic` print, so the game and the
    terminal can never disagree about where a topic happened.
    """
    return {
        "eras": [
            {"id": e.id, "name": e.name, "first": e.first, "last": e.last} for e in ERAS
        ],
        "places": [p.model_dump(exclude_none=True) for p in all_places()],
        "origins": {
            t.id: [o.model_dump() for o in origins_of(t)]
            for t in topics.all_topics()
            if t.origins
        },
    }
