"""Regression proof for ten audited historical origin locations.

The sources date online publications and standards registrations. They do not
locate those events at the organisations' current offices, so the map uses the
network or a standards body and drops online echoes that would duplicate a
topic's existing online origin.
"""

from __future__ import annotations

from vibemap import places, topics

EXPECTED_PLACES = {
    "ci": ("the-internet",),
    "dotfiles": ("the-internet",),
    "github": ("the-internet", "microsoft-redmond"),
    "languages": ("bell-labs", "the-internet"),
    "tests": ("the-internet",),
    "interfaces": ("parc", "the-internet"),
    "unix": ("bell-labs", "a-standards-body"),
    "yaml": ("the-internet",),
    "zsh": ("the-internet",),
    "config": ("a-standards-body",),
}
YAML_ACTIONS_SOURCE = (
    "https://github.blog/news-insights/product-news/github-actions-now-supports-ci-cd/"
)


def test_audited_origins_do_not_infer_current_office_locations() -> None:
    found = {topic.id: topic for topic in topics.all_topics()}

    for topic_id, expected in EXPECTED_PLACES.items():
        origins = places.origins_of(found[topic_id])
        assert tuple(origin.place for origin in origins) == expected, topic_id
        assert len({origin.place for origin in origins}) == len(origins), topic_id
        assert sum(origin.primary for origin in origins) == 1, topic_id


def test_config_cites_the_dated_first_edition_of_ecma_404() -> None:
    config = next(topic for topic in topics.all_topics() if topic.id == "config")
    (origin,) = places.origins_of(config)

    assert origin.year == 2013
    assert origin.source.endswith("ECMA-404_1st_edition_october_2013.pdf")


def test_yaml_retains_the_exact_actions_announcement_as_history() -> None:
    yaml = next(topic for topic in topics.all_topics() if topic.id == "yaml")

    assert YAML_ACTIONS_SOURCE in {source.url for source in yaml.sources}
