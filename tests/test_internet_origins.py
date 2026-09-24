"""Origins leave the-internet only where a dated first-party page places them.

The board's plan for issue #168 moved nineteen origins to the town a dated
first-party page names, and left at the-internet every origin no such page
places. The page that gives the town is either the origin's own source, the
place file's source, or a page listed under the topic's [[sources]]
(docs/TOPICS.md), so each move here names that page and the test asks that a
learner can open it from the topic.
"""

from __future__ import annotations

import pytest

from vibemap import places, topics

VEND = "https://www.anthropic.com/research/project-vend-1"
AIRBNB_2015 = (
    "https://web.archive.org/web/20150602181934/https://www.airbnb.com/about/about-us"
)

# topic -> (place, year, the dated first-party page that puts it in that town)
MOVES: dict[str, tuple[str, int, str]] = {
    "agenthooks": ("anthropic-sf", 2025, VEND),
    "apis": (
        "google-mountain-view",
        2015,
        "https://www.sec.gov/Archives/edgar/data/0001288776/"
        "000128877615000021/googq12015exhibit991.htm",
    ),
    "ci": (
        "github-sf",
        2019,
        "https://github.blog/2019-08-01-why-you-need-to-be-at-github-universe-2019/",
    ),
    "cloud": (
        "amazon-seattle",
        2006,
        "https://press.aboutamazon.com/2006/3/amazon-web-services-launches",
    ),
    "cost": ("anthropic-sf", 2025, VEND),
    "docker": ("santa-clara", 2013, "https://us.pycon.org/2013/"),
    "github": (
        "github-sf",
        2008,
        "https://tom.preston-werner.com/2008/10/18/how-i-turned-down-300k.html",
    ),
    "data": (
        "google-mountain-view",
        2011,
        "https://www.sec.gov/Archives/edgar/data/1288776/"
        "000119312512025336/d260164d10k.htm",
    ),
    "headless": (
        "anthropic-sf",
        2025,
        "https://www.anthropic.com/news/Introducing-code-with-claude",
    ),
    "hooks": ("anthropic-sf", 2025, VEND),
    "kubernetes": (
        "san-francisco",
        2014,
        "https://www.docker.com/blog/dockercon-2022-community-powered-developer-obsessed/",
    ),
    "languages": (
        "google-mountain-view",
        2007,
        "https://commandcenter.blogspot.com/2017/09/go-ten-years-and-climbing.html",
    ),
    "skills": ("anthropic-sf", 2025, VEND),
    "pylibs": (
        "byu-provo",
        2005,
        "https://science.byu.edu/college-events/lecture-travis-oliphant-2025-11-05",
    ),
    "zsh": (
        "apple-cupertino",
        2019,
        "https://www.apple.com/newsroom/2019/10/apple-reports-fourth-quarter-results/",
    ),
    "airflow": ("airbnb-sf", 2015, AIRBNB_2015),
    "datamap": ("airbnb-sf", 2015, AIRBNB_2015),
    "dagster": (
        "dagster-sf",
        2022,
        "https://www.einpresswire.com/article/584322636/dagster-1-0-and-dagster-"
        "cloud-bring-full-cycle-development-best-practices-to-data-orchestration",
    ),
    "medallion": (
        "databricks-sf",
        2022,
        "https://www.databricks.com/company/newsroom/press-releases/databricks-"
        "releases-final-keynote-lineup-and-industry-programming-for-2022-data-ai-summit",
    ),
}

# Refuted by a checker: they wait at the-internet for the page named in the plan.
# future joined them in review: its only town page was a letter on a private
# mailbox letterhead (PMB), which places mail, not an event, as for harness.
OPEN = {
    "future",
    "harness",
    "subagents",
    "interfaces",
    "mcp",
    "prompting",
    "promptstructure",
    "dbt",
    "dataquality",
}

# No single address: an open project, a specification or a distributed release.
STAYS = {
    "adr",
    "agentsmd",
    "changelog",
    "context",
    "git",
    "githooks",
    "env",
    "dotfiles",
    "justfile",
    "llm",
    "markdown",
    "semver",
    "symbols",
    "tests",
    "toml",
    "yaml",
    "jsonl",
    "dlt",
    "polars",
    "netshell",
    "packages",
    "systemd",
}

NEW_PLACES = {
    "san-francisco": ("San Francisco, California", "city", "hall"),
    "byu-provo": ("Brigham Young University, Provo", "university", "campus"),
}

DOTFILES_REPO = "https://api.github.com/repos/dotfiles/dotfiles.github.com"
GITHUB_LAUNCH = "https://github.blog/2008-04-10-we-launched/"


# A letterhead with a private mailbox is a mailing address, never a town page.
MAILBOX_LETTERS = {
    "https://cdn.sanity.io/files/4zrzovbb/website/"
    "6a3b14a98a781a6b69b9a3c5b65da26a44ecddc6.pdf",
}


def test_the_plan_moves_nineteen_and_keeps_thirty_one() -> None:
    assert len(MOVES) == 19
    assert len(OPEN) == 9
    assert len(STAYS) == 22
    assert not (set(MOVES) & (OPEN | STAYS))


def pages_that_place(topic: topics.Topic, origin: places.Origin) -> set[str]:
    """The pages a learner can open from the topic that may give the town."""
    return (
        {s.url for s in topic.sources}
        | {origin.source}
        | {places.get(origin.place).source}
    )


def placed_as_planned(topic_id: str) -> bool:
    """Whether the moved origin stands in its town with its town page listed."""
    place_id, year, town_page = MOVES[topic_id]
    topic = topics.get(topic_id)
    origin = places.origin_at(topic, place_id)
    return origin.year == year and town_page in pages_that_place(topic, origin)


@pytest.mark.parametrize("topic_id", sorted(MOVES))
def test_each_move_stands_in_its_town_with_the_page_that_says_so(
    topic_id: str,
) -> None:
    place_id, year, town_page = MOVES[topic_id]
    topic = topics.get(topic_id)
    origin = places.origin_at(topic, place_id)
    assert origin.year == year, topic_id
    assert all(o.place != "the-internet" for o in topic.origins), topic_id
    readable = pages_that_place(topic, origin)
    assert town_page in readable, f"{topic_id}: {town_page} is not on the topic"


def test_moved_primaries_stay_primary_and_echoes_stay_echoes() -> None:
    echoes = {"apis", "data", "headless", "languages"}
    for topic_id, (place_id, _, _) in MOVES.items():
        origin = places.origin_at(topics.get(topic_id), place_id)
        assert origin.primary is (topic_id not in echoes), topic_id


def test_the_new_places_load_on_earth() -> None:
    for place_id, (name, kind, look) in NEW_PLACES.items():
        place = places.get(place_id)
        assert (place.name, place.kind, place.look) == (name, kind, look)
        assert place.on_earth
        assert place.source.startswith("https://")


def test_only_the_planned_topics_are_left_at_the_internet() -> None:
    left = {
        t.id
        for t in topics.all_topics()
        if any(o.place == "the-internet" for o in t.origins)
    }
    assert left <= OPEN | STAYS, sorted(left - (OPEN | STAYS))
    present = {t.id for t in topics.all_topics()}
    # Every planned topic that is loaded still waits there; interfaces keeps
    # its primary at PARC and only its echo online.
    assert left == (OPEN | STAYS) & present, sorted(((OPEN | STAYS) & present) - left)
    primaries = {
        t.id
        for t in topics.all_topics()
        for o in t.origins
        if o.place == "the-internet" and o.primary
    }
    assert primaries == left - {"interfaces"}


def test_a_mailbox_letterhead_moves_no_origin() -> None:
    for topic in topics.all_topics():
        cited = {s.url for s in topic.sources} | {o.source for o in topic.origins}
        assert not cited & MAILBOX_LETTERS, topic.id


def test_dotfiles_names_its_own_guide_and_not_the_github_launch() -> None:
    dotfiles = topics.get("dotfiles")
    (origin,) = dotfiles.origins
    assert (origin.place, origin.year, origin.source) == (
        "the-internet",
        2012,
        DOTFILES_REPO,
    )
    assert GITHUB_LAUNCH not in {s.url for s in dotfiles.sources}


def test_the_rule_names_the_listed_page() -> None:
    from tests.conftest import ROOT

    rule = (ROOT / "docs" / "TOPICS.md").read_text(encoding="utf-8")
    assert "listed under `[[sources]]`" in rule
