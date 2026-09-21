"""Topics as data: one TOML file per topic, grouped into packs.

vibemap/data/topics/ is the tech tree. `tree.toml` holds the ladder (ages),
the shelves and the depths; every other folder is a pack with a `pack.toml`
and one `<id>.toml` per topic. `vibemap/tech.py` turns what is loaded here
into the lists the roadmap, the vault and the game build have always read.

Nothing is guessed: an unknown shelf, an unknown depth, a duplicate id, a
link to a topic that does not exist and a pack that lists a file it does not
have are all refused with the file name in the message.

Where a topic happened is `[[origins]]` here and a registry of places in
`vibemap/places.py`, which is where an origin's place name is checked.
"""

from __future__ import annotations

import datetime as dt
import tomllib
from functools import cache
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, ValidationError

from vibemap import project

TOPICS_DIR = "topics"
TREE_FILE = "tree.toml"
PACK_FILE = "pack.toml"
# Where `vibe topic <id> --start` puts the hands-on, when the topic names no path.
WORK_DIR = "workspace/topics"


class Source(BaseModel):
    """One citation: what it is, where it is, and when it was last read."""

    model_config = ConfigDict(extra="forbid")

    label: str
    url: str
    checked: dt.date | None = None


class Origin(BaseModel):
    """Where a topic happened: a place, a year, one line, and a source.

    `place` is the id of a file in vibemap/data/places/ (vibemap/places.py
    holds that registry and checks the name). Exactly one origin of a topic
    is `primary`, the place the topic lives at; the others are echoes.
    """

    model_config = ConfigDict(extra="forbid")

    place: str
    year: int
    what: str
    source: str
    primary: bool = False


class HandsOn(BaseModel):
    """The smallest real exercise: a folder, a definition of done, one check."""

    model_config = ConfigDict(extra="forbid")

    title: str
    path: str = ""
    minutes: int = 20
    done: str
    check: dict[str, Any]

    def folder(self, topic_id: str) -> str:
        return self.path or f"{WORK_DIR}/{topic_id}"


class Topic(BaseModel):
    """One topic of the tech tree, as its file declares it."""

    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    age: str
    shelf: str
    depth: int
    # A topic whose prose lives in a handwritten vault note carries none here.
    covered_elsewhere: bool = False
    summary: str | None = None
    # The agent-facing half of the prose, kept apart so a topic can be read
    # without it; the tree joins the two into one paragraph.
    for_agents: str | None = None
    history: str | None = None
    try_it: str | None = None
    sources: list[Source] = []
    # Where this happened. Additive: a topic written before its pack was
    # migrated carries none, and `places.problems()` is what reports that.
    origins: list[Origin] = []
    unlocks: list[str] = []
    prerequisites: list[str] = []
    minutes: int | None = None
    checked: dt.date | None = None
    hands_on: HandsOn | None = None
    pack: str = ""

    @property
    def what(self) -> str | None:
        """The prose the tree carries: the summary and the agent-facing half."""
        if self.summary is None:
            return None
        return f"{self.summary} {self.for_agents}" if self.for_agents else self.summary


class Pack(BaseModel):
    """A folder of topics that is published, reviewed and versioned together."""

    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    blurb: str
    shelf: str
    maintainer: str = ""
    order: int = 100
    topics: list[str] = []


class Age(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    rank: str
    blurb: str


class Shelf(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    name: str
    blurb: str


class Tree(BaseModel):
    """Everything a topic is placed on: the ladder, the shelves, the depths."""

    model_config = ConfigDict(extra="forbid")

    ages: list[Age]
    shelves: list[Shelf]
    depths: dict[int, str]


def _read(path: Path) -> dict[str, Any]:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as e:
        raise ValueError(f"{path.name} is not valid TOML: {e}") from e


def _model(cls, raw: dict[str, Any], where: str):
    try:
        return cls.model_validate(raw)
    except ValidationError as e:
        raise ValueError(
            f"{where} does not match the {cls.__name__} schema:\n{e}"
        ) from e


def _fail(where: str, msg: str) -> None:
    raise ValueError(f"{where}: {msg}")


# Nothing in this tree is older than the first stored-program computers, so a
# year outside this window is a typo, not history.
FIRST_YEAR = 1940


def _check_origins(topic: Topic, where: str) -> None:
    """A topic either has no origin yet, or has a sound set of them.

    The place name itself is checked in vibemap/places.py, which is the
    registry; everything that can be judged from this file alone is judged here.
    """
    if not topic.origins:
        return
    primary = [o for o in topic.origins if o.primary]
    if len(primary) != 1:
        _fail(
            where,
            f"has {len(primary)} primary origins; exactly one origin carries"
            " primary = true, and it is where the topic lives",
        )
    for origin in topic.origins:
        at = f"the origin at {origin.place!r}"
        if not origin.source.startswith("https://"):
            _fail(where, f"{at} needs an https source that says what it claims")
        if not (FIRST_YEAR <= origin.year <= dt.date.today().year):
            _fail(
                where, f"{at} has the year {origin.year}, outside {FIRST_YEAR} to now"
            )
        if not origin.what.strip():
            _fail(where, f"{at} says nothing; `what` is one line about what happened")
        if "\n" in origin.what.strip():
            _fail(where, f"{at} runs over several lines; `what` is one line")


def _pack_topics(folder: Path, pack: Pack) -> list[Topic]:
    """Every topic of one pack, in the pack's own order.

    A file the pack does not list still loads, after the listed ones and by id,
    so a topic dropped into the folder by hand is never silently ignored.
    """
    files = {p.stem: p for p in sorted(folder.glob("*.toml")) if p.name != PACK_FILE}
    missing = [t for t in pack.topics if t not in files]
    if missing:
        _fail(
            f"{pack.id}/{PACK_FILE}",
            f"lists {', '.join(missing)} but the folder has no such file",
        )
    order = pack.topics + sorted(t for t in files if t not in pack.topics)
    out: list[Topic] = []
    for tid in order:
        path = files[tid]
        where = f"{pack.id}/{path.name}"
        topic = _model(Topic, _read(path), where)
        if topic.id != tid:
            _fail(where, f"declares id {topic.id!r}; a topic file is named <id>.toml")
        if topic.pack:
            _fail(where, "pack is the folder the file sits in, never a key")
        if topic.covered_elsewhere and topic.summary is not None:
            _fail(where, "covered_elsewhere means the prose lives in a vault note")
        if not topic.covered_elsewhere and not (
            topic.summary and topic.history and topic.try_it
        ):
            _fail(where, "needs summary, history and try_it")
        _check_origins(topic, where)
        out.append(topic.model_copy(update={"pack": pack.id}))
    return out


def load_from(root: Path) -> tuple[Tree, tuple[Pack, ...], tuple[Topic, ...]]:
    """Read one topics folder: the tree, its packs and their topics, validated.

    Separate from load() so a test can hand it a folder of its own and watch
    a bad pack fail.
    """
    tree = _model(Tree, _read(root / TREE_FILE), TREE_FILE)
    packs: list[Pack] = []
    by_folder: dict[str, Path] = {}
    for folder in sorted(p for p in root.iterdir() if p.is_dir()):
        manifest = folder / PACK_FILE
        if not manifest.exists():
            _fail(f"topics/{folder.name}", f"a pack needs a {PACK_FILE}")
        pack = _model(Pack, _read(manifest), f"{folder.name}/{PACK_FILE}")
        if pack.id != folder.name:
            _fail(f"{folder.name}/{PACK_FILE}", f"declares id {pack.id!r}")
        packs.append(pack)
        by_folder[pack.id] = folder
    packs.sort(key=lambda p: (p.order, p.id))
    shelves = {s.id for s in tree.shelves}
    ages = {a.id for a in tree.ages}
    topics: list[Topic] = []
    seen: dict[str, str] = {}
    for pack in packs:
        if pack.shelf not in shelves:
            _fail(f"{pack.id}/{PACK_FILE}", f"unknown shelf {pack.shelf!r}")
        for topic in _pack_topics(by_folder[pack.id], pack):
            where = f"{pack.id}/{topic.id}.toml"
            if topic.id in seen:
                _fail(where, f"id already used by the {seen[topic.id]} pack")
            seen[topic.id] = pack.id
            if topic.shelf not in shelves:
                _fail(where, f"unknown shelf {topic.shelf!r}")
            if topic.age not in ages:
                _fail(where, f"unknown age {topic.age!r}")
            if topic.depth not in tree.depths:
                _fail(where, f"unknown depth {topic.depth}")
            topics.append(topic)
    known = set(seen)
    for topic in topics:
        for other in (*topic.unlocks, *topic.prerequisites):
            if other not in known:
                _fail(f"{topic.pack}/{topic.id}.toml", f"links to unknown {other!r}")
    return tree, tuple(packs), tuple(topics)


@cache
def load() -> tuple[Tree, tuple[Pack, ...], tuple[Topic, ...]]:
    """The packaged tree, read once per process."""
    with project.data_dir(TOPICS_DIR) as base:
        return load_from(Path(base))


def tree() -> Tree:
    return load()[0]


def packs() -> tuple[Pack, ...]:
    return load()[1]


def all_topics() -> tuple[Topic, ...]:
    return load()[2]


def by_id() -> dict[str, Topic]:
    return {t.id: t for t in all_topics()}


def get(topic_id: str) -> Topic:
    """One topic, or a ValueError naming a few of the ids that do exist."""
    found = by_id().get(topic_id)
    if found is None:
        near = sorted(t for t in by_id() if topic_id in t) or sorted(by_id())[:8]
        raise ValueError(
            f"unknown topic {topic_id!r}; try one of: {', '.join(near[:8])}"
        )
    return found


def in_pack(pack_id: str) -> list[Topic]:
    return [t for t in all_topics() if t.pack == pack_id]
