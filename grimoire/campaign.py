"""The campaign data: four evenings, twelve mentors, the tech tree.

src/data/campaign.json is the one source the game and the CLI share; the
tech tree comes from tools/tech.py so the notes, the roadmap and the quests
can never disagree.
"""

from __future__ import annotations

import importlib.util
import json
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CAMPAIGN_PATH = ROOT / "src" / "data" / "campaign.json"
TECH_PATH = ROOT / "tools" / "tech.py"

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


@cache
def raw() -> dict[str, Any]:
    return json.loads(CAMPAIGN_PATH.read_text(encoding="utf-8"))


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
def tech_nodes() -> list[TechNode]:
    return [
        TechNode(
            id=t[0], age=t[1], name=t[2], what=t[3], history=t[4], try_it=t[5],
            docs=tuple((d[0], d[1]) for d in t[6]), unlocks=tuple(t[7]),
        )
        for t in _tech_module().T
    ]  # fmt: skip


def _tech_module() -> Any:
    spec = importlib.util.spec_from_file_location("grimoire_tech", TECH_PATH)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(f"cannot load {TECH_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
