"""Every data-engineering lesson has a dated, sourced event for the map."""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest
from click.testing import CliRunner

from vibemap import places, topics
from vibemap.cli import cli

TOPICS = {
    "airflow",
    "arrow",
    "csv",
    "dagster",
    "datamap",
    "dataquality",
    "dbt",
    "dlt",
    "duckdblab",
    "iceberg",
    "jsonl",
    "kafka",
    "medallion",
    "parquet",
    "polars",
    "schemas",
}


def test_pack_coverage_is_explicit() -> None:
    assert {t.id for t in topics.all_topics() if t.pack == "data-engineering"} == TOPICS


@pytest.mark.parametrize("topic_id", sorted(TOPICS))
def test_each_lesson_has_a_complete_origin(topic_id: str) -> None:
    topic = topics.get(topic_id)
    origins = topic.origins
    assert origins, f"{topic_id}: no dated event"
    assert sum(o.primary for o in origins) == 1
    assert len({o.place for o in origins}) == len(origins)
    for origin in origins:
        assert places.get(origin.place)
        assert origin.source.startswith("https://")
        assert str(origin.year) in re.findall(r"\b(?:19|20)\d{2}\b", origin.what)
        assert origin.what.endswith(".")
        assert "\n" not in origin.what
        assert origin.source in {s.url for s in topic.sources}


def test_pack_passes_the_place_validator() -> None:
    assert places.problems(packs=["data-engineering"]) == []


# A planet carries a single event line: it must name the lesson's concrete
# subject, even when the lesson title describes a broader practice.
SUBJECTS = {
    "airflow": "airflow",
    "arrow": "arrow",
    "csv": "csv",
    "dagster": "dagster",
    "datamap": "airflow",
    "dataquality": "tests",
    "dbt": "dbt",
    "dlt": "dlt",
    "duckdblab": "duckdb",
    "iceberg": "iceberg",
    "jsonl": "json lines",
    "kafka": "kafka",
    "medallion": "bronze",
    "parquet": "parquet",
    "polars": "polars",
    "schemas": "specification",
}


@pytest.mark.parametrize("topic_id", sorted(TOPICS))
def test_primary_event_names_the_subject(topic_id: str) -> None:
    primary = [o for o in topics.get(topic_id).origins if o.primary]
    assert len(primary) == 1
    assert re.search(
        rf"(?<![a-z0-9]){re.escape(SUBJECTS[topic_id])}(?![a-z0-9])",
        primary[0].what.lower(),
    )


def test_cli_exposes_the_same_dated_duckdb_origin_as_the_game() -> None:
    root = Path(__file__).resolve().parents[1]
    result = CliRunner(env=dict(os.environ, VIBE_HOME=str(root), COLUMNS="240")).invoke(
        cli, ["topic", "duckdblab"]
    )
    assert result.exit_code == 0, result.output
    output = " ".join(re.sub(r"\x1b\[[0-9;]*m", "", result.output).split())
    origin = places.payload()["origins"]["duckdblab"][0]
    assert "CWI, Amsterdam Science Park" in output
    assert "2018" in output
    assert origin["what"] in output
    assert origin["source"] in output


def test_publications_do_not_borrow_current_office_locations() -> None:
    for topic_id in ("airflow", "datamap", "dbt", "dataquality", "medallion"):
        primary = next(o for o in topics.get(topic_id).origins if o.primary)
        assert primary.place == "the-internet", topic_id
    kafka = next(o for o in topics.get("kafka").origins if o.primary)
    assert kafka.place == "linkedin-mountain-view"
    assert "scheduled for 27 July 2011" in kafka.what
    assert "11 January" not in kafka.what
    duckdb = next(o for o in topics.get("duckdblab").origins if o.primary)
    assert (duckdb.place, duckdb.year) == ("cwi-amsterdam", 2018)
