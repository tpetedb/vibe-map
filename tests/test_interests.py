"""What you want to learn: the shelves as a choice, in the CLI and the game.

The rule every assertion here defends is that an interest orders the course and
never shortens it. A chosen shelf comes first; an unchosen one is still there.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

from tests.conftest import GamePage
from vibemap import campaign, interests
from vibemap.cli import cli
from vibemap.config import Config
from vibemap.personas import PERSONAS
from vibemap.state import State


def _run(camp: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "vibemap.cli", *args],
        cwd=camp,
        env=dict(os.environ, VIBE_HOME=str(camp), COLUMNS="200"),
        capture_output=True,
        text=True,
    )


@pytest.fixture
def camp(tmp_path: Path) -> Path:
    here = tmp_path / "camp"
    made = CliRunner().invoke(cli, ["new", str(here), "--name", "Tom"])
    assert made.exit_code == 0, made.output
    return here


# ---- the model -----------------------------------------------------------------


def test_the_shelves_are_the_tree_s_own_and_an_unknown_one_is_refused() -> None:
    ids = interests.shelf_ids()
    assert len(ids) == 11 and "data" in ids and "agents" in ids
    assert interests.normalise(["agents", "data"]) == ["data", "agents"]  # tree order
    with pytest.raises(ValueError, match="unknown shelf"):
        interests.normalise(["gardening"])


def test_parse_takes_a_list_or_the_word_all() -> None:
    assert interests.parse("data, shell,agents") == ["shell", "data", "agents"]
    assert interests.parse("all") == []
    assert interests.parse("everything") == []


def test_nothing_chosen_means_every_shelf_is_wanted() -> None:
    for shelf in interests.shelf_ids():
        assert interests.wants([], shelf)
    assert interests.wants(["data"], "data")
    assert not interests.wants(["data"], "shell")


def test_a_suggestion_prefers_a_chosen_shelf_and_never_runs_out() -> None:
    picked = interests.suggestions(["data"], [], limit=3)
    assert picked and all(s.shelf == "data" for s in picked)
    assert picked[0].depth <= picked[-1].depth

    # Every topic on the shelf read: the rest of the tree is offered instead
    # of nothing, because an interest orders the course, it does not end it.
    nodes = campaign.tech_nodes()
    done = [n.id for n in nodes]
    data_done = [n.id for n in nodes if n.category == "data"]
    assert interests.suggestions(["data"], data_done, limit=1)[0].shelf != "data"
    assert interests.suggestions(["data"], done, limit=1) == []


def test_every_persona_preset_names_real_shelves() -> None:
    for p in PERSONAS.values():
        assert p.interests, p.id
        assert interests.normalise(list(p.interests))
    assert set(PERSONAS["data-engineer"].interests) == {
        "data",
        "shell",
        "git",
        "agents",
    }
    assert set(PERSONAS["pabo-teacher"].interests) == {"agents", "docs", "knowledge"}


# ---- the config and the state ---------------------------------------------------


def test_the_config_refuses_a_shelf_that_does_not_exist() -> None:
    assert Config().learner.interests == []
    ok = Config.model_validate({"learner": {"interests": ["agents", "data"]}})
    assert ok.learner.interests == ["data", "agents"]
    with pytest.raises(ValueError, match="unknown shelf"):
        Config.model_validate({"learner": {"interests": ["nope"]}})


def test_the_dumped_config_round_trips_the_choice(tmp_path: Path) -> None:
    cfg = Config.model_validate({"learner": {"interests": ["data", "agents"]}})
    p = tmp_path / "camp.toml"
    cfg.save(p)
    assert "interests" in p.read_text(encoding="utf-8")
    assert Config.load(p).learner.interests == ["data", "agents"]


def test_the_progress_code_carries_the_shelves_and_only_adds() -> None:
    s = State(name="Lotte", interests=["data"])
    assert json.loads(_decode(s.to_code()))["interests"] == ["data"]

    back = State(interests=["agents"])
    back.merge_code(s.to_code())
    assert back.interests == ["agents", "data"]

    # A code written before this release carries no key, and the reader keeps
    # what it had rather than losing the choice.
    older = State(name="Lotte")
    code = older.to_code()
    payload = json.loads(_decode(code))
    del payload["interests"]
    import base64

    trimmed = (
        base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    )
    keeper = State(interests=["docs"])
    keeper.merge_code(trimmed)
    assert keeper.interests == ["docs"]


def _decode(code: str) -> str:
    import base64

    return base64.urlsafe_b64decode(code + "=" * (-len(code) % 4)).decode()


# ---- the command ----------------------------------------------------------------


def test_vibe_interests_lists_sets_and_resets(camp: Path) -> None:
    out = _run(camp, "interests")
    assert out.returncode == 0, out.stdout + out.stderr
    assert "Everything" in out.stdout and "Next topic:" in out.stdout

    out = _run(camp, "interests", "set", "data,shell")
    assert out.returncode == 0, out.stdout + out.stderr
    assert Config.load(camp / "config" / "camp.toml").learner.interests == [
        "shell",
        "data",
    ]
    assert json.loads((camp / ".vibe" / "state.json").read_text())["interests"] == [
        "shell",
        "data",
    ]

    out = _run(camp, "interests", "all")
    assert out.returncode == 0
    assert Config.load(camp / "config" / "camp.toml").learner.interests == []


def test_an_unknown_shelf_on_the_command_line_is_refused(camp: Path) -> None:
    out = _run(camp, "interests", "set", "gardening")
    assert out.returncode == 1 and "unknown shelf" in out.stdout


def test_status_prints_the_shelves_and_the_next_topic(camp: Path) -> None:
    assert _run(camp, "interests", "set", "data").returncode == 0
    out = _run(camp, "status")
    assert out.returncode == 0, out.stdout + out.stderr
    assert "Learning: Data" in " ".join(out.stdout.split())
    assert "Next topic:" in out.stdout
    payload = json.loads(_run(camp, "status", "--json").stdout)
    assert payload["interests"] == ["data"]


# ---- the game -------------------------------------------------------------------


def test_the_title_asks_what_you_want_to_learn(game: GamePage) -> None:
    page = game.goto().page
    steps = page.locator("#onboard .step")
    assert steps.count() == 5
    assert "What do you want to learn?" in (page.text_content("#onboard") or "")
    page.click("#onboard .shelves button.choice:has-text('Data')")
    assert game.state()["interests"] == ["data"]
    # Everything is one click away again, and it is a real answer, not a gap.
    page.click("#onboard .shelves button.choice:has-text('Everything')")
    assert game.state()["interests"] == []
    assert game.errors == []


def test_a_chosen_shelf_orders_the_tree_and_hides_nothing(game: GamePage) -> None:
    game.goto(state={"name": "Lotte", "look": "own", "interests": ["data"]})
    game.resume()
    page = game.page
    page.evaluate("openTree()")
    page.wait_for_selector("#vtree.on", state="attached")
    shelves = page.evaluate(
        """() => [...document.querySelectorAll('#vtree .age')].map(
             e => [e.querySelector('h4').textContent, e.classList.contains('faded')])"""
    )
    assert len(shelves) == 11, shelves
    assert shelves[0] == ["Data", False]
    assert all(faded for _, faded in shelves[1:])
    assert game.errors == []


def test_the_progress_code_from_the_game_carries_the_shelves(game: GamePage) -> None:
    game.goto(state={"name": "Lotte", "look": "own", "interests": ["docs"]})
    game.resume()
    code = game.page.evaluate(
        """() => {openSheet('s-map'); exportProgress();
                  return document.getElementById('impcode').value}"""
    )
    st = State()
    st.merge_code(code)
    assert st.interests == ["docs"]
    assert game.errors == []
