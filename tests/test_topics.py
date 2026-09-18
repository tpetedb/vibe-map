"""Topics as data: the schema, the packs, and what an author may not get wrong.

Every rule here is one a content pack can break by hand, so each one fails with
the file name in the message rather than producing a quietly wrong tree.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

from tests.conftest import ROOT
from vibemap import tech, topics
from vibemap.artifact_checks import KINDS
from vibemap.cli import cli
from vibemap.state import State, decode_code
from vibemap.topics import load_from
from vibemap.vault import safe_title

TOPICS_DIR = ROOT / "vibemap" / "data" / "topics"
CORE = TOPICS_DIR / "core"
URL = re.compile(r"^https?://[^\s\"'<>]+$")
# A scaffolded topic carries these until its author reads the docs and writes.
TODO = "TODO"


def _files(folder: Path) -> list[Path]:
    return sorted(p for p in folder.glob("*.toml") if p.name != "pack.toml")


# ---- the files -----------------------------------------------------------------


def test_every_topic_is_one_file_in_a_pack() -> None:
    assert (TOPICS_DIR / "tree.toml").exists()
    assert len(_files(CORE)) == len(topics.in_pack("core")) >= 54
    assert {t.pack for t in topics.all_topics()} == {p.id for p in topics.packs()}
    for topic in topics.all_topics():
        assert (TOPICS_DIR / topic.pack / f"{topic.id}.toml").exists()


def test_a_pack_declares_itself_and_its_reading_order() -> None:
    core = next(p for p in topics.packs() if p.id == "core")
    assert core.title and core.blurb and core.maintainer
    assert core.shelf in {s.id for s in topics.tree().shelves}
    assert [t.id for t in topics.in_pack("core")][: len(core.topics)] == core.topics


def test_no_topic_file_still_carries_a_scaffold_marker() -> None:
    for pack in topics.packs():
        for path in _files(TOPICS_DIR / pack.id):
            assert TODO not in path.read_text(encoding="utf-8"), path.name


# ---- the schema ----------------------------------------------------------------


def test_every_topic_is_placed_on_a_real_shelf_age_and_depth() -> None:
    tree = topics.tree()
    shelves, ages = {s.id for s in tree.shelves}, {a.id for a in tree.ages}
    for topic in topics.all_topics():
        assert topic.shelf in shelves and topic.age in ages
        assert topic.depth in tree.depths


def test_a_topic_title_survives_the_vault_s_file_name_rules() -> None:
    # The vault writes one note per topic and links it by title. A title the
    # file system cannot take is rewritten by safe_title(), so a handwritten
    # [[wikilink]] to it dies; a new topic has to be named so it never happens.
    titles = [safe_title(t.title) for t in topics.all_topics()]
    assert len(set(titles)) == len(titles)
    for topic in topics.all_topics():
        assert safe_title(topic.title), topic.id
        # The core pack has two titles with a colon or a slash in them, from
        # before the rule; a topic written since is named so nothing rewrites it.
        if topic.checked:
            assert safe_title(topic.title) == topic.title, topic.id


def test_every_source_is_a_url_and_a_written_topic_cites_three() -> None:
    for topic in topics.all_topics():
        for source in topic.sources:
            assert URL.match(source.url), f"{topic.id}: {source.url}"
            assert source.label.strip()
            # The content rule is https and a date; one archived page in the
            # core pack predates it and is the only http left.
            if topic.checked:
                assert source.url.startswith("https://"), topic.id
        # A topic written under the content rule records the day it was checked
        # and stands on at least three sources.
        assert len(topic.sources) >= (3 if topic.checked else 1), topic.id


def test_a_hands_on_names_a_check_kind_that_exists() -> None:
    for topic in topics.all_topics():
        if topic.hands_on is None:
            continue
        assert topic.hands_on.check.get("kind") in KINDS, topic.id
        assert topic.hands_on.folder(topic.id).startswith("workspace/")
        assert topic.hands_on.done and topic.hands_on.title


def test_the_prose_of_a_covered_topic_lives_in_its_vault_note() -> None:
    from tools.regen_tree import EXIST

    covered = {t.id for t in topics.all_topics() if t.covered_elsewhere}
    assert covered == set(EXIST)
    for topic in topics.all_topics():
        assert (topic.what is None) is topic.covered_elsewhere


# ---- the loader refuses ---------------------------------------------------------


def _camp(tmp_path: Path, files: dict[str, str]) -> Path:
    here = tmp_path / "topics"
    (here / "demo").mkdir(parents=True)
    (here / "tree.toml").write_text(
        (TOPICS_DIR / "tree.toml").read_text(encoding="utf-8"), encoding="utf-8"
    )
    for name, text in files.items():
        (here / name).write_text(text, encoding="utf-8")
    return here


PACK = 'id = "demo"\ntitle = "Demo"\nblurb = "b"\nshelf = "shell"\ntopics = []\n'
TOPIC = (
    'id = "{i}"\ntitle = "{i}"\nage = "dark"\nshelf = "shell"\ndepth = 1\n'
    'summary = "s"\nhistory = "h"\ntry_it = "t"\nunlocks = {u}\n'
)


def test_a_link_to_an_unknown_topic_fails_loudly(tmp_path: Path) -> None:
    root = _camp(
        tmp_path,
        {
            "demo/pack.toml": PACK,
            "demo/one.toml": TOPIC.format(i="one", u='["nowhere"]'),
        },
    )
    with pytest.raises(ValueError, match="links to unknown 'nowhere'"):
        load_from(root)


def test_a_pack_that_lists_a_missing_file_fails_loudly(tmp_path: Path) -> None:
    root = _camp(tmp_path, {"demo/pack.toml": PACK.replace("[]", '["gone"]')})
    with pytest.raises(ValueError, match="no such file"):
        load_from(root)


def test_an_unknown_shelf_fails_loudly(tmp_path: Path) -> None:
    root = _camp(
        tmp_path,
        {
            "demo/pack.toml": PACK,
            "demo/one.toml": TOPIC.format(i="one", u="[]").replace(
                'shelf = "shell"', 'shelf = "gardening"'
            ),
        },
    )
    with pytest.raises(ValueError, match="unknown shelf 'gardening'"):
        load_from(root)


def test_a_file_that_does_not_match_its_id_fails_loudly(tmp_path: Path) -> None:
    root = _camp(
        tmp_path,
        {"demo/pack.toml": PACK, "demo/one.toml": TOPIC.format(i="two", u="[]")},
    )
    with pytest.raises(ValueError, match="named <id>.toml"):
        load_from(root)


def test_a_topic_without_prose_has_to_say_it_is_covered_elsewhere(
    tmp_path: Path,
) -> None:
    thin = 'id = "one"\ntitle = "One"\nage = "dark"\nshelf = "shell"\ndepth = 1\n'
    root = _camp(tmp_path, {"demo/pack.toml": PACK, "demo/one.toml": thin})
    with pytest.raises(ValueError, match="needs summary, history and try_it"):
        load_from(root)


def test_an_unknown_key_in_a_topic_file_fails_loudly(tmp_path: Path) -> None:
    extra = TOPIC.format(i="one", u="[]") + 'colour = "red"\n'
    root = _camp(tmp_path, {"demo/pack.toml": PACK, "demo/one.toml": extra})
    with pytest.raises(ValueError, match="schema"):
        load_from(root)


# ---- the tree the rest of the repo reads ----------------------------------------


def test_tech_keeps_the_shape_every_generator_reads() -> None:
    assert len(tech.T) == len(topics.all_topics())
    assert all(len(row) == 8 for row in tech.T)
    assert [row[0] for row in tech.T] == [t.id for t in topics.all_topics()]
    assert tech.CATEGORY["unix"] == ("shell", 1)
    assert tech.category("nothing-like-this") == ("agents", 2)
    ladder = ["dark", "feudal", "castle", "imperial", "future"]
    assert [a[0] for a in tech.AGES] == ladder
    assert set(tech.DEPTHS) == {1, 2, 3}


def test_the_agent_facing_half_joins_back_into_one_paragraph() -> None:
    justfile = topics.get("justfile")
    assert justfile.for_agents and justfile.for_agents.startswith("And for an agent:")
    assert justfile.what == f"{justfile.summary} {justfile.for_agents}"


def test_the_generated_tree_is_in_step_with_the_data() -> None:
    out = subprocess.run(
        [sys.executable, "tools/regen_tree.py", "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert out.returncode == 0, out.stdout + out.stderr


# ---- the commands ---------------------------------------------------------------


def test_vibe_topics_lists_the_packs_and_vibe_topic_prints_one(
    tmp_path: Path,
) -> None:
    env = dict(os.environ, VIBE_HOME=str(ROOT), COLUMNS="200")
    listed = CliRunner(env=env).invoke(cli, ["topics"])
    assert listed.exit_code == 0, listed.output
    assert "The core map" in listed.output and "unix" in listed.output
    one = CliRunner(env=env).invoke(cli, ["topic", "unix"])
    assert one.exit_code == 0 and "Unix and the terminal" in one.output
    unknown = CliRunner(env=env).invoke(cli, ["topic", "nothing-like-this"])
    assert unknown.exit_code == 1 and "unknown topic" in unknown.output


def test_checking_a_topic_without_a_hands_on_says_so(tmp_path: Path) -> None:
    env = dict(os.environ, VIBE_HOME=str(tmp_path), COLUMNS="200")
    out = CliRunner(env=env).invoke(cli, ["check", "--topic", "unix"])
    assert out.exit_code == 1 and "no hands-on" in out.output


def test_the_progress_code_carries_the_topics_that_are_done() -> None:
    state = State(name="Tom", roadmap_done=["unix", "git"])
    assert decode_code(state.to_code())["topics"] == ["unix", "git"]
    other = State(name="Tom", roadmap_done=["bash"])
    other.merge_code(state.to_code())
    # A code adds a topic and never takes one away.
    assert other.roadmap_done == ["bash", "unix", "git"]
