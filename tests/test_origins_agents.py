"""Agent milestones must cover the shelf and remain attributable on their own."""

from __future__ import annotations

import re

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
ACTORS = {topic: "Anthropic" for topic in TOPICS} | {
    "agentsmd": "OpenAI",
    "security": "MIT",
    "meta": "SRI",
    "llm": "Google",
    "symbols": "John Gruber",
}
# Only these two milestones have contemporary evidence for an Earth location.
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
            assert ACTORS[topic.id] in origin.what, topic.id
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


def test_online_publications_do_not_borrow_a_current_company_address() -> None:
    for topic in selected():
        primary = next(origin for origin in topic.origins if origin.primary)
        if topic.id in HISTORICAL_SITES:
            assert primary.place == HISTORICAL_SITES[topic.id], topic.id
        else:
            assert primary.place == "the-internet", topic.id
            assert "online" in primary.what.lower(), topic.id
