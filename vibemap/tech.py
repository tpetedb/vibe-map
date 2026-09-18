"""The tech tree, read from vibemap/data/topics/ (see vibemap/topics.py).

This module is the shape the rest of the repository has always used: AGES,
T, CATEGORIES, DEPTHS, CATEGORY and category(). The content moved into one
TOML file per topic (ADR 0013); the lists below are built from it at import
so the roadmap, the vault notes and the game build never disagree.
"""

from __future__ import annotations

from vibemap import topics

_TREE = topics.tree()
_TOPICS = topics.all_topics()

# id, name, rank, blurb: the XP ladder the player climbs.
AGES: list[tuple[str, str, str, str]] = [
    (a.id, a.name, a.rank, a.blurb) for a in _TREE.ages
]
# id, age, name, what, history, try, docs(list of (label,url)), unlocks(list ids)
T: list[tuple] = [
    (
        t.id,
        t.age,
        t.title,
        t.what,
        t.history,
        t.try_it,
        [(s.label, s.url) for s in t.sources],
        list(t.unlocks),
    )
    for t in _TOPICS
]
# The tree is grouped by category, not by age: every topic has a depth of its
# own (1 basics, 2 working knowledge, 3 deep), and a category is a shelf you
# come back to. AGES stay as the player's XP ladder only.
CATEGORIES: list[tuple[str, str, str]] = [
    (s.id, s.name, s.blurb) for s in _TREE.shelves
]
DEPTHS: dict[int, str] = dict(_TREE.depths)
CATEGORY: dict[str, tuple[str, int]] = {t.id: (t.shelf, t.depth) for t in _TOPICS}


def category(node_id: str) -> tuple[str, int]:
    """(category id, depth) for a node; unknown nodes land in agents, depth 2."""
    return CATEGORY.get(node_id, ("agents", 2))
