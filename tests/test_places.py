"""Places as data: the schema, the origins, and what an author may not get wrong.

Every rule here is one a research order can break by hand while sourcing a
pack, so each one fails with the file name in the message rather than putting
a topic on a planet that is not there. The build is tested here too, because
PLACES is the one thing the game is given about all of this.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import pytest
from click.testing import CliRunner

from tests.conftest import ROOT
from tools import build
from vibemap import places, topics
from vibemap.cli import cli
from vibemap.places import load_from
from vibemap.topics import load_from as load_topics_from

PLACES_DIR = ROOT / "vibemap" / "data" / "places"
TOPICS_DIR = ROOT / "vibemap" / "data" / "topics"
GAME = ROOT / "game" / "vibe-map.html"
SHELL = "shell"


# ---- the files -----------------------------------------------------------------


def test_every_place_is_one_file_named_after_its_id() -> None:
    files = sorted(p.stem for p in PLACES_DIR.glob("*.toml"))
    assert files == sorted(p.id for p in places.all_places())
    assert len(files) >= 30, "the packs need their places seeded before they land"


def test_the_design_s_abstract_places_exist() -> None:
    # docs/GALAXY.md names these four by hand: a topic that happened nowhere in
    # particular still has somewhere to sit.
    for place_id in ("the-cloud", "the-internet", "a-data-centre", "a-standards-body"):
        assert places.get(place_id).globe in ("cloud", "datacentre")


# ---- the schema on the real data ------------------------------------------------


def test_every_place_is_sourced_and_placed() -> None:
    eras = {e.id for e in places.ERAS}
    for place in places.all_places():
        assert place.source.startswith("https://"), place.id
        assert place.kind in places.KINDS and place.era in eras, place.id
        assert place.look in places.LOOKS and place.region in places.REGIONS, place.id
        assert re.fullmatch(r"[a-z0-9-]+", place.landmark), place.id
        if place.on_earth:
            assert place.lat is not None and place.lon is not None, place.id
            assert -90 <= place.lat <= 90 and -180 <= place.lon <= 180, place.id
        else:
            assert place.lat is None and place.lon is None, place.id


def test_the_eras_are_an_unbroken_ladder() -> None:
    years = [(e.first, e.last) for e in places.ERAS]
    assert years[0][0] == 1960 and years[-1][1] is None
    for (_, last), (first, _) in zip(years, years[1:], strict=False):
        assert last is not None and first == last + 1


# ---- the loader refuses ---------------------------------------------------------


PLACE = (
    'id = "{i}"\nname = "A place"\nkind = "lab"\nregion = "us-east"\n'
    'era = "mainframe"\nglobe = "{g}"\n{c}look = "campus"\n'
    'landmark = "horn-antenna"\nsource = "{s}"\n'
)
EARTH = {"g": "earth", "c": "lat = 40.0\nlon = -74.0\n", "s": "https://example.org/"}


def _places(tmp_path: Path, files: dict[str, str]) -> Path:
    here = tmp_path / "places"
    here.mkdir(parents=True)
    for name, text in files.items():
        (here / name).write_text(text, encoding="utf-8")
    return here


def test_a_good_folder_loads(tmp_path: Path) -> None:
    root = _places(tmp_path, {"one.toml": PLACE.format(i="one", **EARTH)})
    assert [p.id for p in load_from(root)] == ["one"]


def test_a_file_that_does_not_match_its_id_fails_loudly(tmp_path: Path) -> None:
    root = _places(tmp_path, {"one.toml": PLACE.format(i="two", **EARTH)})
    with pytest.raises(ValueError, match="places/one.toml.*named <id>.toml"):
        load_from(root)


def test_an_unknown_kind_fails_loudly(tmp_path: Path) -> None:
    text = PLACE.format(i="one", **EARTH).replace('kind = "lab"', 'kind = "castle"')
    root = _places(tmp_path, {"one.toml": text})
    with pytest.raises(ValueError, match="unknown kind 'castle'"):
        load_from(root)


def test_a_place_on_earth_needs_coordinates(tmp_path: Path) -> None:
    root = _places(tmp_path, {"one.toml": PLACE.format(i="one", **{**EARTH, "c": ""})})
    with pytest.raises(ValueError, match="needs lat and lon"):
        load_from(root)


def test_a_place_that_is_not_on_earth_may_not_have_coordinates(
    tmp_path: Path,
) -> None:
    root = _places(
        tmp_path, {"one.toml": PLACE.format(i="one", **{**EARTH, "g": "cloud"})}
    )
    with pytest.raises(ValueError, match="nowhere on Earth"):
        load_from(root)


def test_a_place_without_an_https_source_fails_loudly(tmp_path: Path) -> None:
    root = _places(
        tmp_path,
        {"one.toml": PLACE.format(i="one", **{**EARTH, "s": "http://example.org/"})},
    )
    with pytest.raises(ValueError, match="source is an https link"):
        load_from(root)


def test_an_unknown_key_in_a_place_file_fails_loudly(tmp_path: Path) -> None:
    text = PLACE.format(i="one", **EARTH) + 'colour = "red"\n'
    root = _places(tmp_path, {"one.toml": text})
    with pytest.raises(ValueError, match="Place schema"):
        load_from(root)


# ---- origins: the topic's half --------------------------------------------------


PACK = 'id = "demo"\ntitle = "Demo"\nblurb = "b"\nshelf = "shell"\ntopics = []\n'
TOPIC = (
    'id = "one"\ntitle = "One"\nage = "dark"\nshelf = "shell"\ndepth = 1\n'
    'summary = "s"\nhistory = "h"\ntry_it = "t"\n'
)
ORIGIN = '[[origins]]\nplace = "{p}"\nyear = {y}\nwhat = "w"\nsource = "{s}"\n{m}'
GOOD = {
    "p": "bell-labs",
    "y": 1969,
    "s": "https://example.org/",
    "m": "primary = true\n",
}


def _topics(tmp_path: Path, origins: str) -> Path:
    here = tmp_path / "topics"
    (here / "demo").mkdir(parents=True)
    (here / "tree.toml").write_text(
        (TOPICS_DIR / "tree.toml").read_text(encoding="utf-8"), encoding="utf-8"
    )
    (here / "demo" / "pack.toml").write_text(PACK, encoding="utf-8")
    (here / "demo" / "one.toml").write_text(TOPIC + origins, encoding="utf-8")
    return here


def test_a_topic_with_no_origins_still_loads(tmp_path: Path) -> None:
    # Additive: a pack that has not been migrated yet is not broken, it is
    # unfinished, and places.problems() is what says so.
    tree = load_topics_from(_topics(tmp_path, ""))
    assert tree[2][0].origins == []


def test_one_sound_origin_loads(tmp_path: Path) -> None:
    tree = load_topics_from(_topics(tmp_path, ORIGIN.format(**GOOD)))
    assert tree[2][0].origins[0].place == "bell-labs"


def test_two_primary_origins_fail_loudly(tmp_path: Path) -> None:
    text = ORIGIN.format(**GOOD) + ORIGIN.format(**{**GOOD, "p": "mit", "y": 1965})
    with pytest.raises(ValueError, match="demo/one.toml: has 2 primary origins"):
        load_topics_from(_topics(tmp_path, text))


def test_an_origin_with_no_primary_fails_loudly(tmp_path: Path) -> None:
    text = ORIGIN.format(**{**GOOD, "m": ""})
    with pytest.raises(ValueError, match="has 0 primary origins"):
        load_topics_from(_topics(tmp_path, text))


def test_an_origin_without_an_https_source_fails_loudly(tmp_path: Path) -> None:
    text = ORIGIN.format(**{**GOOD, "s": "http://example.org/"})
    with pytest.raises(ValueError, match="needs an https source"):
        load_topics_from(_topics(tmp_path, text))


def test_an_origin_with_an_impossible_year_fails_loudly(tmp_path: Path) -> None:
    text = ORIGIN.format(**{**GOOD, "y": 1869})
    with pytest.raises(ValueError, match="has the year 1869"):
        load_topics_from(_topics(tmp_path, text))


def test_an_origin_missing_its_source_fails_loudly(tmp_path: Path) -> None:
    text = '[[origins]]\nplace = "bell-labs"\nyear = 1969\nwhat = "w"\nprimary = true\n'
    with pytest.raises(ValueError, match="Topic schema"):
        load_topics_from(_topics(tmp_path, text))


def test_an_unknown_place_is_refused_with_the_topic_s_file_name(
    tmp_path: Path,
) -> None:
    tree = load_topics_from(
        _topics(tmp_path, ORIGIN.format(**{**GOOD, "p": "atlantis"}))
    )
    with pytest.raises(ValueError, match="demo/one.toml: names the place 'atlantis'"):
        places.origins_of(tree[2][0])


# ---- what problems() reports ----------------------------------------------------


def test_the_shell_shelf_is_sourced_and_every_origin_resolves() -> None:
    assert places.problems(shelves=[SHELL]) == []
    shell = [t for t in topics.all_topics() if t.shelf == SHELL]
    assert len(shell) >= 9
    for topic in shell:
        found = places.origins_of(topic)
        assert found and found[0].primary, topic.id
        assert len([o for o in found if o.primary]) == 1, topic.id
        for origin in found:
            assert origin.source.startswith("https://") and origin.what.strip()
            assert places.get(origin.place)


def test_problems_names_the_file_of_every_topic_that_has_no_origin() -> None:
    # The research orders that follow read this list: one sentence per defect,
    # each naming a file, narrowed by shelf or by pack.
    by_pack = places.problems(packs=["data-engineering"])
    assert by_pack, "the data pack is not sourced yet, so it has to be reported"
    for line in by_pack:
        assert line.startswith("data-engineering/") and line.endswith(".")
    assert places.problems(shelves=[SHELL], packs=["core"]) == []
    assert len(places.problems()) == len(places.problems(packs=None))


def test_problems_reports_an_unknown_place_rather_than_raising(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    made = load_topics_from(
        _topics(tmp_path, ORIGIN.format(**{**GOOD, "p": "atlantis"}))
    )
    monkeypatch.setattr(topics, "all_topics", lambda: made[2])
    found = places.problems()
    assert found == [
        "demo/one.toml names the place 'atlantis', and no file in"
        " vibemap/data/places/ declares it."
    ]


# ---- the blob the game is given -------------------------------------------------


def test_the_payload_carries_the_places_the_eras_and_the_origins() -> None:
    payload = places.payload()
    assert [e["id"] for e in payload["eras"]] == [e.id for e in places.ERAS]
    assert len(payload["places"]) == len(places.all_places())
    bell = next(p for p in payload["places"] if p["id"] == "bell-labs")
    assert bell["lat"] and "source" in bell
    cloud = next(p for p in payload["places"] if p["id"] == "the-cloud")
    assert "lat" not in cloud, "a place that is nowhere carries no coordinates"
    assert payload["origins"]["unix"][0]["primary"] is True
    assert set(payload["origins"]) <= {t.id for t in topics.all_topics()}


def test_the_built_game_carries_places_as_one_json_blob() -> None:
    text = GAME.read_text(encoding="utf-8")
    assert "const PLACES=" in text
    blob = text.split("const PLACES=", 1)[1].split(";\n", 1)[0]
    payload = json.loads(blob.replace("\\u003c", "<").replace("\\u0026", "&"))
    assert payload == json.loads(json.dumps(places.payload()))
    assert "</script" not in blob and "<!--" not in blob


def test_the_places_are_injected_before_the_first_module_that_could_read_them() -> None:
    # PLACES is written in front of src/game/00-state.js, so every module of
    # every folder has it, and nothing in the game reads it yet.
    assert "places" in build.INJECT_BEFORE["game/00-state.js"]
    script = GAME.read_text(encoding="utf-8")
    first = (ROOT / "src" / "game" / "00-state.js").read_text(encoding="utf-8")
    assert script.index("const PLACES=") < script.index(first[:120])


# ---- the commands ---------------------------------------------------------------


ANSI = re.compile(r"\x1b\[[0-9;]*m")


def _run(args: list[str]) -> str:
    """The command's output with the colour taken out, so a style is never
    what an assertion is really reading."""
    env = dict(os.environ, VIBE_HOME=str(ROOT), COLUMNS="200")
    out = CliRunner(env=env).invoke(cli, args)
    plain = ANSI.sub("", out.output)
    assert out.exit_code == 0, plain
    return plain


def test_vibe_places_lists_the_places_by_era() -> None:
    out = _run(["places"])
    assert "Mainframes and Unix" in out and "bell-labs" in out
    assert "Bell Labs, Murray Hill" in out
    # The topics that come from a place are listed with it.
    assert "unix, files" in out


def test_vibe_places_shows_one_place_with_its_topics() -> None:
    out = _run(["places", "bell-labs"])
    assert "40.684" in out and "ethw.org" in out
    assert "unix 1969 (where it lives)" in out
    assert "files 1965 (echo)" in out
    env = dict(os.environ, VIBE_HOME=str(ROOT), COLUMNS="200")
    unknown = CliRunner(env=env).invoke(cli, ["places", "nothing-like-this"])
    assert unknown.exit_code == 1 and "unknown place" in ANSI.sub("", unknown.output)


def test_vibe_topic_shows_the_same_origins_the_game_is_given() -> None:
    out = " ".join(_run(["topic", "ssh"]).split())
    assert "Helsinki University of Technology" in out
    assert "1995" in out and "draft-ylonen-ssh-protocol-00" in out
    assert "Echo." in out and "OpenBSD" in out
    origin = places.payload()["origins"]["ssh"][0]
    assert " ".join(origin["what"].split()) in out
    assert origin["source"] in out
