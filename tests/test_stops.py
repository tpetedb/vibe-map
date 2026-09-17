"""Every stop on winter, desert and production is checked against a deliverable.

A fresh camp is red everywhere. The same camp, with the files each stop asks
for written into it, is green everywhere. The scripted set lives in
tools/script_camp.py, so the nightly regeneration writes exactly what these
tests prove. The fork challenges of the new production stop get their own
scripted fork, and the game shows that stop on the production island.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from click.testing import CliRunner

from tests.conftest import encode_progress
from tools.script_camp import script_fork, script_stops
from vibemap import quests
from vibemap.cli import cli

ROOT = Path(__file__).resolve().parents[1]
WORLDS = ("winter", "desert", "prod")


def _camp(tmp_path: Path) -> Path:
    camp = tmp_path / "camp"
    out = CliRunner().invoke(cli, ["new", str(camp), "--name", "T"])
    assert out.exit_code == 0, out.output
    return camp


def _vibe(camp: Path, *args: str) -> str:
    env = dict(os.environ, VIBE_HOME=str(camp))
    out = subprocess.run(
        [sys.executable, "-m", "vibemap.cli", *args],
        cwd=camp,
        env=env,
        capture_output=True,
        text=True,
    )
    return out.stdout + out.stderr


def _island(camp: Path, world: str) -> str:
    return _vibe(camp, "check", "--all", "--no-claim", "-w", world)


def test_a_fresh_camp_fails_every_stop(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    for world in WORLDS:
        output = _island(camp, world)
        assert "all checks pass" not in output, output
        assert output.count("not yet.") == 8, output


def test_scripted_deliverables_pass_every_stop(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    script_stops(camp)
    script_fork(camp, ROOT)
    for world in WORLDS:
        output = _island(camp, world)
        assert output.count("all checks pass") == 8, output
        assert "not yet." not in output, output


def test_each_fork_challenge_is_checked_on_its_own(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    for challenge in quests.FORK_CHALLENGES:
        assert "not yet." in _vibe(camp, "check", "--fork", challenge), challenge
    script_fork(camp, ROOT)
    for challenge in quests.FORK_CHALLENGES:
        output = _vibe(camp, "check", "--fork", challenge)
        assert "your fork builds and is yours" in output, (challenge, output)
    unknown = _vibe(camp, "check", "--fork", "sideways")
    assert "unknown fork challenge" in unknown, unknown


def test_reading_only_stops_say_so_and_still_need_the_note() -> None:
    from vibemap.config import Config

    cfg = Config()
    for world, n in sorted(quests.READING_ONLY):
        quest = quests.quest_for(world, n, cfg)
        assert quest.checks[0].name.startswith("reading only:"), quest.checks[0].name
        assert (world, n) not in quests.STOP_CHECKS
    for world in WORLDS:
        for n in range(1, 9):
            has_deliverable = (world, n) in quests.STOP_CHECKS
            assert has_deliverable is ((world, n) not in quests.READING_ONLY), (
                world,
                n,
            )


def test_the_production_island_shows_the_forking_stop(game) -> None:
    """The prod island still lays out eight plots; the sixth is the fork now."""
    game.goto()
    game.start("Lotte")
    game.import_code(encode_progress(done_w={"campus": [], "prod": [1, 2, 3, 4, 5]}))
    game.page.evaluate("setWorld('prod')")
    game.page.wait_for_function("() => window.__S().world === 'prod'")
    game.open_roadmap()
    buttons = game.workstream_buttons()
    assert len(buttons) == 8
    assert "Fork the game" in (buttons[5].text_content() or "")
    buttons[5].click()
    game.page.wait_for_selector("#sheet .screen.on", state="attached")
    text = game.page.text_content("#sheet .screen.on") or ""
    for word in ("vibe fork", "src/config/00-config.js", "vibe check --fork"):
        assert word in text, word
    game.screenshot("stops_prod_fork", clip_height=860)
    game.assert_clean()
