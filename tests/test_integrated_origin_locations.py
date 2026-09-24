"""Regression proof for ten audited historical origin locations.

A current office address proves nothing about where an event happened, so an
origin stands in a town only where a dated first-party page places it there
(issue #168, tests/test_internet_origins.py); the rest stay on the network or
at a standards body, and no topic keeps two origins at one place.
"""

from __future__ import annotations

from tests.test_internet_origins import MOVES, placed_as_planned
from vibemap import places, topics

EXPECTED_PLACES = {
    "ci": ("github-sf",),
    "dotfiles": ("the-internet",),
    "github": ("github-sf", "microsoft-redmond"),
    "languages": ("bell-labs", "google-mountain-view"),
    "tests": ("the-internet",),
    "interfaces": ("parc", "the-internet"),
    "unix": ("bell-labs", "a-standards-body"),
    "yaml": ("the-internet",),
    "zsh": ("apple-cupertino",),
    "config": ("a-standards-body",),
}
YAML_ACTIONS_SOURCE = (
    "https://github.blog/news-insights/product-news/github-actions-now-supports-ci-cd/"
)


def test_audited_origins_stand_in_a_town_only_where_a_dated_page_says_so() -> None:
    found = {topic.id: topic for topic in topics.all_topics()}

    for topic_id, expected in EXPECTED_PLACES.items():
        origins = places.origins_of(found[topic_id])
        assert tuple(origin.place for origin in origins) == expected, topic_id
        assert len({origin.place for origin in origins}) == len(origins), topic_id
        assert sum(origin.primary for origin in origins) == 1, topic_id
        if topic_id in MOVES:
            assert placed_as_planned(topic_id), topic_id


def test_config_cites_the_dated_first_edition_of_ecma_404() -> None:
    config = next(topic for topic in topics.all_topics() if topic.id == "config")
    (origin,) = places.origins_of(config)

    assert origin.year == 2013
    assert origin.source.endswith("ECMA-404_1st_edition_october_2013.pdf")


def test_yaml_retains_the_exact_actions_announcement_as_history() -> None:
    yaml = next(topic for topic in topics.all_topics() if topic.id == "yaml")

    assert YAML_ACTIONS_SOURCE in {source.url for source in yaml.sources}
