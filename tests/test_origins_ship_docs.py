"""The ship, docs and knowledge shelves: where each of their topics happened.

The generic defects are `places.problems()`, and the schema's own rules are
tested in tests/test_places.py. What is specific to these three shelves is
here: the ten topics they hold, one primary origin each, and a primary line
that names the topic. On the map the primary origin's `what` is the only
sentence next to a topic, so a line that never says what it is about leaves a
dome with no label, which no schema rule can catch.
"""

from __future__ import annotations

import datetime as dt
import re

from vibemap import places, topics

SHELVES = ("ship", "docs", "knowledge")

# The word that stands for the topic in its primary origin's line. Where a
# title is a phrase, the word is the half the origin is about: `headless` is
# scheduled work, and `semver` is the specification by its full name.
NAMES = {
    "adr": "architecture decision",
    "changelog": "changelog",
    "cloud": "cloud",
    "docker": "docker",
    "headless": "schedul",
    "kubernetes": "kubernetes",
    "obsidian": "obsidian",
    "readme": "readme",
    "semver": "semantic versioning",
    "vault": "vault",
}

# A page below an edition's root in the TUHS tree is a path and the file's own
# bytes: a date at best, never a lab or a person. The edition's root page and
# the manual's title page are where Bell Laboratories is named.
TUHS_FILE_PAGE = re.compile(r"tuhs\.org/cgi-bin/utree\.pl\?file=[^/&]+/")


def _topics() -> list[topics.Topic]:
    return [t for t in topics.all_topics() if t.shelf in SHELVES]


def test_the_three_shelves_hold_the_topics_this_order_sourced() -> None:
    found = sorted(t.id for t in _topics())
    assert found == sorted(NAMES), (
        "a topic on the ship, docs or knowledge shelf needs an [[origins]] block"
        " and its word in NAMES, and one that left needs its word removed:"
        f" {sorted(set(found) ^ set(NAMES))}"
    )


def test_none_of_the_three_shelves_has_a_defect_left() -> None:
    assert places.problems(shelves=list(SHELVES)) == []


def test_every_topic_of_them_lives_at_one_place_that_exists() -> None:
    for topic in _topics():
        found = places.origins_of(topic)
        primary = [o for o in found if o.primary]
        assert len(primary) == 1, topic.id
        assert found[0] is primary[0], f"{topic.id}: the primary origin comes first"
        for origin in found:
            assert places.get(origin.place).id == origin.place
            assert origin.source.startswith("https://"), topic.id
            assert origin.what.strip() and "\n" not in origin.what, topic.id
            assert 1940 <= origin.year <= dt.date.today().year, topic.id


def test_the_primary_line_of_every_topic_names_the_topic() -> None:
    for topic in _topics():
        primary = places.origins_of(topic)[0]
        assert NAMES[topic.id] in primary.what.lower(), (
            f"{topic.pack}/{topic.id}.toml: the primary origin's line is the only"
            f" one the map shows, so it has to say {NAMES[topic.id]!r}:"
            f" {primary.what!r}"
        )


def test_no_topic_of_them_stands_twice_at_the_same_place() -> None:
    # Two origins of one topic at one place draw one dome and print the first
    # of them twice in `vibe places <id>`: an echo is somewhere else.
    for topic in _topics():
        used = [o.place for o in topic.origins]
        assert len(used) == len(set(used)), topic.id


def test_no_origin_of_them_stands_on_a_page_that_names_no_one() -> None:
    # The town may come from the place file, the actor may not: an origin's own
    # page has to say who, so a bare file out of an archive cannot carry one.
    for topic in _topics():
        for origin in places.origins_of(topic):
            assert not TUHS_FILE_PAGE.search(origin.source), (
                f"{topic.pack}/{topic.id}.toml: {origin.source} is a file in the"
                f" TUHS tree and names no lab and no person, so it cannot put"
                f" {topic.id!r} at {origin.place!r}; cite a page that says who"
            )


def test_the_game_is_given_the_origins_of_all_ten() -> None:
    given = places.payload()["origins"]
    assert isinstance(given, dict)
    for topic in _topics():
        assert given[topic.id][0]["primary"] is True, topic.id
        assert given[topic.id][0]["source"].startswith("https://"), topic.id
