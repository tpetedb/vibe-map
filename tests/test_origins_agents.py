"""Agent milestones must cover the shelf and remain attributable on their own."""

from __future__ import annotations

import re

from tests.test_internet_origins import MOVES, placed_as_planned
from vibemap import places, topics

TOPICS = {
    "agenthooks",
    "agentsmd",
    "context",
    "cost",
    "harness",
    "hooks",
    "llm",
    "mcp",
    "meta",
    "prompting",
    "promptstructure",
    "security",
    "skills",
    "subagents",
    "symbols",
    "future",
}
ACTORS = {topic: ("Anthropic",) for topic in TOPICS} | {
    "agentsmd": ("OpenAI",),
    "security": ("MIT",),
    "meta": ("SRI",),
    "llm": ("Google", "Alibaba"),
    "symbols": ("John Gruber",),
}
# Historical sites with contemporary evidence. A publication stands at a
# company's address only where a dated first-party page places it in that town
# (MOVES); an office address alone proves nothing, so the rest stay online.
HISTORICAL_SITES = {"security": "mit", "meta": "sri-menlo-park"}


def selected() -> list[topics.Topic]:
    return [t for t in topics.all_topics() if t.shelf in {"agents", "future"}]


def test_every_agent_and_future_topic_is_accounted_for() -> None:
    assert {t.id for t in selected()} == TOPICS
    for topic in selected():
        origins = places.origins_of(topic)
        assert len([o for o in origins if o.primary]) == 1, topic.id
        assert len({o.place for o in origins}) == len(origins), topic.id


def test_milestones_name_the_actor_and_use_dated_sources() -> None:
    for topic in selected():
        assert topic.origins, topic.id
        for origin in topic.origins:
            assert any(actor in origin.what for actor in ACTORS[topic.id]), topic.id
            assert origin.source.startswith("https://"), topic.id
            assert origin.what.endswith("."), topic.id
            assert "\n" not in origin.what, topic.id
            years = re.findall(r"\b(?:19|20)\d{2}\b", origin.what)
            assert not years or str(origin.year) in years, topic.id


def test_cli_prints_a_named_origin_for_an_agent_topic() -> None:
    from click.testing import CliRunner

    from vibemap.cli import cli

    result = CliRunner().invoke(cli, ["topic", "mcp"])
    assert result.exit_code == 0, result.output
    assert "2024" in result.output
    assert "Anthropic" in result.output
    assert "Model Context Protocol" in result.output


def test_a_company_address_needs_a_dated_page_that_places_the_event() -> None:
    for topic in selected():
        primary = next(origin for origin in topic.origins if origin.primary)
        if topic.id in HISTORICAL_SITES:
            assert primary.place == HISTORICAL_SITES[topic.id], topic.id
        elif topic.id in MOVES:
            assert primary.place == MOVES[topic.id][0], topic.id
            assert placed_as_planned(topic.id), topic.id
        else:
            assert primary.place == "the-internet", topic.id
            assert "online" in primary.what.lower(), topic.id
