"""Where the data and net shelves happened.

`places.problems()` says whether an origin loads at all; the order checks that
separately. The data shelf also holds the data-engineering pack, which has an
order and a test file of its own, so this file reads the core pack only. What
is specific to these four topics is written here: each lives
at the place this table names, the line under it names the thing the topic is
about, a line at a real address names who is at that address, every line
spells the year it is dated to, no topic stands twice at one place, and no two
topics share a sentence. The relational model at IBM in 1970 with Postgres at
Berkeley in 1986 as its echo is the example docs/GALAXY.md gives, so it is
pinned.
"""

from __future__ import annotations

import re

from vibemap import places, topics

SHELVES = ("data", "net")
PACK = "core"

# Where each topic lives, and what its primary line has to name. On the map a
# planet carries its origin line and nothing else, so the line says what
# happened to the thing the topic is about, in the words the topic's own prose
# uses for it. One of the words has to appear, as a word and not inside one.
HOME: dict[str, tuple[str, tuple[str, ...]]] = {
    "data": ("ibm-san-jose", ("data",)),
    "sql": ("ibm-san-jose", ("sql",)),
    "http": ("cern", ("http",)),
    "apis": ("uc-irvine", ("rest", "api", "apis")),
}

# Who a line has to name when it stands at a real organisation, as its page
# spells it. An origin at an address is a statement about who is at that
# address. A place missing from this table is an abstract one, where no
# address is claimed.
ACTORS: dict[str, tuple[str, ...]] = {
    "amazon-seattle": ("amazon",),
    "apache-software-foundation": ("apache software foundation",),
    "cern": ("cern",),
    "cwi-amsterdam": ("cwi",),
    "google-mountain-view": ("google",),
    "ibm-san-jose": ("ibm",),
    "microsoft-redmond": ("microsoft",),
    "uc-berkeley": ("university of california at berkeley",),
    "uc-irvine": ("university of california, irvine", "uc irvine"),
}
ABSTRACT = {"a-standards-body", "ietf", "the-internet"}

YEAR = re.compile(r"\b(?:19|20)\d\d\b")


def _shelved() -> list[topics.Topic]:
    return [t for t in topics.all_topics() if t.shelf in SHELVES and t.pack == PACK]


def _names(what: str, words: tuple[str, ...]) -> bool:
    """Whether the line names one of the words, as a word of its own."""
    text = what.lower()
    return any(
        re.search(rf"(?<![a-z0-9]){re.escape(w)}(?![a-z0-9])", text) for w in words
    )


def _origins() -> list[tuple[topics.Topic, topics.Origin]]:
    return [(t, o) for t in _shelved() for o in places.origins_of(t)]


def test_the_table_covers_exactly_the_topics_of_these_shelves() -> None:
    # A topic added to one of these shelves without a line in the table would
    # otherwise be sourced by nobody: the table is the list of what is owed.
    assert set(HOME) == {t.id for t in _shelved()}


def test_every_topic_lives_where_the_table_says_and_its_line_names_it() -> None:
    for topic in _shelved():
        home, words = HOME[topic.id]
        primary = [o for o in topic.origins if o.primary]
        assert [o.place for o in primary] == [home], (
            f"{topic.pack}/{topic.id}.toml lives at {home}, and its primary"
            f" origins are: {[o.place for o in primary]}"
        )
        assert _names(primary[0].what, words), (
            f"{topic.id}: the line has to name one of {words},"
            f" and it says: {primary[0].what}"
        )


def test_a_line_at_an_address_names_who_is_at_that_address() -> None:
    for topic, origin in _origins():
        if origin.place in ABSTRACT:
            continue
        where = f"{topic.pack}/{topic.id}.toml at {origin.place}"
        assert origin.place in ACTORS, f"{where}: say who the line has to name"
        assert _names(origin.what, ACTORS[origin.place]), (
            f"{where}: the line has to name one of {ACTORS[origin.place]},"
            f" and it says: {origin.what}"
        )


def test_every_line_spells_the_year_it_is_dated_to_before_any_other() -> None:
    # The year is the one the page gives for what happened. A line with no
    # year cannot be checked against its origin, and a line that opens on
    # another year has been read off a different event than the one dated.
    for topic, origin in _origins():
        spelled = [int(y) for y in YEAR.findall(origin.what)]
        assert spelled and spelled[0] == origin.year, (
            f"{topic.pack}/{topic.id}.toml at {origin.place}: dated"
            f" {origin.year}, and the line says: {origin.what}"
        )


def test_a_line_is_one_plain_sentence_in_the_house_style() -> None:
    for topic, origin in _origins():
        where = f"{topic.pack}/{topic.id}.toml at {origin.place}"
        assert origin.what == origin.what.strip(), where
        assert origin.what.endswith("."), f"{where}: {origin.what}"
        assert "\u2014" not in origin.what, f"{where}: an em dash"
        assert "\u2013" not in origin.what, f"{where}: an en dash"
        assert len(origin.what) <= 200, f"{where}: {len(origin.what)} characters"


def test_no_topic_stands_twice_at_the_same_place() -> None:
    # Two origins of one topic at one place load, and `vibe places <id>` then
    # prints that topic twice under the same dome (issue 168). An echo is
    # somewhere else, or it is not an echo.
    for topic in _shelved():
        used = [o.place for o in topic.origins]
        assert len(used) == len(set(used)), f"{topic.id} stands twice at one place"


def test_no_two_origins_share_a_sentence() -> None:
    # Two topics may share a dome; each says what happened to itself there.
    lines = [o.what for _, o in _origins()]
    assert len(lines) == len(set(lines))


def test_every_place_used_exists_with_a_source_of_its_own() -> None:
    for topic, origin in _origins():
        where = f"{topic.pack}/{topic.id}.toml"
        assert places.get(origin.place).source.startswith("https://"), where
        assert origin.source.startswith("https://"), where


def test_the_relational_model_is_at_ibm_with_postgres_as_its_echo() -> None:
    # The example docs/GALAXY.md explains an echo with: one topic that belongs
    # to IBM in 1970 and to Berkeley in 1986.
    data = next(t for t in _shelved() if t.id == "data")
    found = {o.place: o for o in data.origins}
    assert found["ibm-san-jose"].year == 1970 and found["ibm-san-jose"].primary
    assert "codd" in found["ibm-san-jose"].what.lower()
    assert found["uc-berkeley"].year == 1986 and not found["uc-berkeley"].primary
    assert "postgres" in found["uc-berkeley"].what.lower()
