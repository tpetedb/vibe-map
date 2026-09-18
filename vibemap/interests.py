"""Interests: which shelves of the tech tree the learner wants first.

The course has eleven shelves now, and nobody wants all of them at once. An
interest is a shelf id from `vibemap/tech.py`; an empty list means everything,
which is the default and stays the default.

Nothing is ever hidden or locked by a choice. Interests change the order in
which things are offered: the tree and the search put the chosen shelves first
and dim the rest, the roadmap suggests the next topic from them, grow mode
gives their basics a head start, and the dashboard counts per shelf. The
thirty-two stops are the spine for everyone, whatever is chosen.
"""

from __future__ import annotations

from dataclasses import dataclass

from vibemap import campaign


def shelves() -> list[tuple[str, str, str]]:
    """(id, name, blurb) for every shelf, in the tree's display order."""
    return campaign.categories()


def shelf_ids() -> list[str]:
    return [c[0] for c in shelves()]


def label(shelf_id: str) -> str:
    for c, name, _ in shelves():
        if c == shelf_id:
            return name
    return shelf_id


def normalise(names: list[str] | tuple[str, ...]) -> list[str]:
    """Clean a list of shelf ids: lowercase, no repeats, tree order.

    Raises:
        ValueError: naming the unknown shelf and the ones that exist.
    """
    wanted = [str(n).strip().lower() for n in names if str(n).strip()]
    known = shelf_ids()
    unknown = [n for n in wanted if n not in known]
    if unknown:
        raise ValueError(
            f"unknown shelf {', '.join(unknown)}; one of: {', '.join(known)}"
        )
    return [c for c in known if c in wanted]


def parse(value: str) -> list[str]:
    """`all`, `everything` or a comma-separated list, as the CLI takes it."""
    if value.strip().lower() in {"all", "everything", "-"}:
        return []
    return normalise(value.replace(" ", ",").split(","))


def wants(chosen: list[str], shelf_id: str) -> bool:
    """True when this shelf is chosen, and true for every shelf when none is."""
    return not chosen or shelf_id in chosen


@dataclass(frozen=True, slots=True)
class Suggestion:
    """One next topic to read, with the shelf it sits on."""

    id: str
    name: str
    shelf: str
    depth: int


def suggestions(chosen: list[str], done: list[str], limit: int = 3) -> list[Suggestion]:
    """The next topics to read: chosen shelves first, shallowest first."""
    todo = [n for n in campaign.tech_nodes() if n.id not in done]
    mine = [n for n in todo if wants(chosen, n.category)]
    # A learner who finished their shelves is offered the rest rather than
    # nothing: an interest orders the course, it never ends it.
    pool = mine or todo
    pool.sort(key=lambda n: n.depth)
    return [Suggestion(n.id, n.name, n.category, n.depth) for n in pool[:limit]]
