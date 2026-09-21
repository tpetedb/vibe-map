"""Where the git, code and formats shelves happened.

`places.problems()` says whether an origin loads at all; that is the generic
half and the order checks it separately. What is specific to these fifteen
topics is written here: each one sits at one place, the line under it names
the thing the topic is about, and no topic stands twice at the same place,
because the map draws one dome per place and would print the same topic twice.
"""

from __future__ import annotations

import datetime as dt
import re

from vibemap import places, topics

SHELVES = ("git", "code", "formats")

# What the primary origin's line has to name. On the map a planet carries its
# origin line and nothing else: there is no history paragraph beside it, so
# the line says what happened to the thing the topic is about. One of the
# words here has to appear in it, as a word and not inside another one.
NAMES: dict[str, tuple[str, ...]] = {
    "ci": ("ci/cd", "actions"),
    "git": ("git",),
    "githooks": ("hooks",),
    "github": ("github",),
    "concerns": ("modules",),
    "languages": ("c", "go", "rust", "typescript"),
    "pylibs": ("numpy", "libraries"),
    "python": ("python",),
    "tests": ("test", "py.test", "evals"),
    "web": ("web", "html", "javascript", "css"),
    "config": ("json", "yaml", "toml", "markdown"),
    "env": (".env",),
    "markdown": ("markdown",),
    "toml": ("toml",),
    "yaml": ("yaml",),
}


def _shelved() -> list[topics.Topic]:
    return [t for t in topics.all_topics() if t.shelf in SHELVES]


def _names(what: str, words: tuple[str, ...]) -> bool:
    """Whether the line names one of the words, as a word of its own."""
    text = what.lower()
    return any(
        re.search(rf"(?<![a-z0-9]){re.escape(w)}(?![a-z0-9])", text) for w in words
    )


def test_the_table_covers_exactly_the_topics_of_these_shelves() -> None:
    # A topic added to one of these shelves without a line in the table would
    # otherwise be sourced by nobody: the table is the list of what is owed.
    assert set(NAMES) == {t.id for t in _shelved()}
    assert len(NAMES) == 15


def test_every_topic_has_one_primary_origin_whose_line_names_it() -> None:
    for topic in _shelved():
        found = places.origins_of(topic)
        assert found, f"{topic.pack}/{topic.id}.toml has no origin"
        assert len([o for o in found if o.primary]) == 1, topic.id
        first = found[0]
        assert first.primary, f"{topic.id}: the primary origin comes first"
        assert _names(first.what, NAMES[topic.id]), (
            f"{topic.id}: the line has to name one of {NAMES[topic.id]},"
            f" and it says: {first.what}"
        )


def test_every_origin_stands_on_a_place_that_exists_and_an_opened_source() -> None:
    this_year = dt.date.today().year
    for topic in _shelved():
        for origin in places.origins_of(topic):
            where = f"{topic.pack}/{topic.id}.toml"
            assert places.get(origin.place).source.startswith("https://"), where
            assert origin.source.startswith("https://"), where
            assert 1940 <= origin.year <= this_year, f"{where}: {origin.year}"
            assert origin.what.strip() == origin.what.strip().splitlines()[0], where
            assert origin.what.endswith("."), f"{where}: {origin.what}"


def test_no_topic_stands_twice_at_the_same_place() -> None:
    # Two origins of one topic at one place load, and `vibe places <id>` then
    # prints that topic twice under the same dome (issue 168). An echo is
    # somewhere else, or it is not an echo.
    for topic in _shelved():
        used = [o.place for o in topic.origins]
        assert len(used) == len(set(used)), f"{topic.id} stands twice at one place"
