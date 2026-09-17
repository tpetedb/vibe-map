"""The campaign data: four evenings, twelve mentors, the tech tree.

vibemap/data/campaign.json is the one source the game and the CLI share; the
tech tree comes from vibemap/tech.py so the notes, the roadmap and the quests
can never disagree.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from typing import Any

from vibemap import project, tech

WORLD_NAMES = {
    "campus": "Innovation Campus",
    "winter": "Cold Storage Cluster",
    "desert": "Sandbox Environment",
    "prod": "Production Environment",
}


@dataclass(frozen=True, slots=True)
class Workstream:
    world: str
    n: int
    hour: str
    name: str
    outcome: str
    sources: tuple[tuple[str, str], ...]


@dataclass(frozen=True, slots=True)
class Evening:
    world: str
    title: str
    short: str
    workstreams: tuple[Workstream, ...]

    @property
    def island(self) -> str:
        return WORLD_NAMES.get(self.world, self.world)


@dataclass(frozen=True, slots=True)
class TechNode:
    id: str
    age: str
    name: str
    what: str
    history: str
    try_it: str
    docs: tuple[tuple[str, str], ...]
    unlocks: tuple[str, ...]
    category: str = "agents"
    depth: int = 2


@cache
def raw() -> dict[str, Any]:
    return json.loads(project.data_text("campaign.json"))


@cache
def evenings() -> dict[str, Evening]:
    out: dict[str, Evening] = {}
    for world, ev in raw()["evenings"].items():
        ws = tuple(
            Workstream(
                world=world,
                n=i,
                hour=x["h"],
                name=x["n"],
                outcome=x["d"],
                sources=tuple((s[0], s[1]) for s in x.get("src", [])),
            )
            for i, x in enumerate(ev["ws"], 1)
        )
        out[world] = Evening(
            world=world,
            title=ev["title"],
            short=ev["title"].split(": ")[0],
            workstreams=ws,
        )
    return out


@cache
def artifacts() -> list[dict[str, Any]]:
    """The props on the island that teach one concept each."""
    return list(raw().get("artifacts", []))


def mentors() -> list[dict[str, Any]]:
    return list(raw()["mentors"])


def mentor(mentor_id: str) -> dict[str, Any]:
    for m in mentors():
        if m["id"] == mentor_id:
            return m
    raise ValueError(
        f"unknown mentor {mentor_id!r}; one of: {', '.join(m['id'] for m in mentors())}"
    )


@cache
def ages() -> list[tuple[str, str, str, str]]:
    return [tuple(a) for a in _tech_module().AGES]


@cache
def categories() -> list[tuple[str, str, str]]:
    """(id, name, blurb) for every shelf of the tree, in display order."""
    return [tuple(c) for c in _tech_module().CATEGORIES]


def depth_label(depth: int) -> str:
    return _tech_module().DEPTHS.get(depth, str(depth))


@cache
def tech_nodes() -> list[TechNode]:
    mod = _tech_module()
    return [
        TechNode(
            id=t[0], age=t[1], name=t[2], what=t[3], history=t[4], try_it=t[5],
            docs=tuple((d[0], d[1]) for d in t[6]), unlocks=tuple(t[7]),
            category=mod.category(t[0])[0], depth=mod.category(t[0])[1],
        )
        for t in mod.T
    ]  # fmt: skip


def _tech_module() -> Any:
    return tech
