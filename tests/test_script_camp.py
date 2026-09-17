"""The scripted camp: what tools/script_camp.py writes is what the checks want.

The mentor exercises are the part with no other test, so they get one here: a
fresh camp, scripted, must pass `vibe check --mentor <id>` for all twelve. The
camp is built once for the module and each mentor is its own case, so a failure
names the mentor instead of the whole set.

The other half is the tool running against a camp that is already a real
repository, which is what the nightly regeneration does: it must keep the
remote, the branch and the uncommitted work it finds.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

from tools.script_camp import CAMP_MARKER, script_fork, script_mentors, script_stops
from vibemap import campaign
from vibemap.cli import cli

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "script_camp.py"
MENTOR_IDS = [m["id"] for m in campaign.mentors()]


@pytest.fixture(scope="module")
def scripted_camp(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """One camp, made the way a learner makes one, with the exercises done."""
    camp = tmp_path_factory.mktemp("scripted") / "camp"
    made = CliRunner().invoke(cli, ["new", str(camp), "--name", "Lotte"])
    assert made.exit_code == 0, made.output
    # God difficulty so the strict note check runs too, not only the exercise.
    toml = camp / CAMP_MARKER
    toml.write_text(
        toml.read_text(encoding="utf-8").replace(
            'difficulty = "normal"', 'difficulty = "god"'
        ),
        encoding="utf-8",
    )
    script_mentors(camp)
    return camp


def _vibe(camp: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "vibemap.cli", *args],
        cwd=camp,
        env=dict(os.environ, VIBE_HOME=str(camp), NO_COLOR="1", COLUMNS="200"),
        capture_output=True,
        text=True,
    )


@pytest.mark.parametrize("mentor_id", MENTOR_IDS)
def test_a_scripted_mentor_encounter_passes_its_checks(
    scripted_camp: Path, mentor_id: str
) -> None:
    out = _vibe(scripted_camp, "check", "--mentor", mentor_id)
    assert out.returncode == 0, out.stdout + out.stderr
    assert "not yet." not in out.stdout, out.stdout


def test_the_command_line_refuses_a_folder_that_is_not_a_camp(tmp_path: Path) -> None:
    out = subprocess.run(
        [sys.executable, str(TOOL), "--camp", str(tmp_path), "--only", "mentors"],
        capture_output=True,
        text=True,
    )
    assert out.returncode != 0
    assert "is not a camp" in out.stderr and CAMP_MARKER in out.stderr
    assert not (tmp_path / "workspace").exists()


REAL_REMOTE = "https://github.com/tpetedb/vibe-map-played.git"
WORLDS = ("winter", "desert", "prod")


def _git(repo: Path, *args: str) -> str:
    out = subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, check=True
    )
    return out.stdout.strip()


def _origin(camp: Path) -> str:
    """The stored URL. `remote get-url` applies any insteadOf rule the machine
    has, so it is not what this test is about."""
    return _git(camp, "config", "--get", "remote.origin.url")


def _islands_are_green(camp: Path) -> None:
    for world in WORLDS:
        out = _vibe(camp, "check", "--all", "--no-claim", "-w", world)
        assert out.stdout.count("all checks pass") == 8, (world, out.stdout)


def test_scripting_a_camp_that_is_already_a_real_repository_disturbs_nothing(
    tmp_path: Path,
) -> None:
    """The played instance has an origin, a branch and work in the tree, and the
    nightly regeneration runs the tool against it twice over its life."""
    camp = tmp_path / "camp"
    assert CliRunner().invoke(cli, ["new", str(camp), "--name", "Tom"]).exit_code == 0
    _git(camp, "remote", "add", "origin", REAL_REMOTE)
    _git(
        camp,
        "-c",
        "user.email=t@e.st",
        "-c",
        "user.name=T",
        "commit",
        "-q",
        "--allow-empty",
        "-m",
        "mine",
    )
    _git(camp, "switch", "-qc", "played")
    # Work in the tree that nobody has committed: nothing here may throw it away.
    mine = camp / "workspace" / "scratch" / "half-finished.md"
    mine.parent.mkdir(parents=True, exist_ok=True)
    mine.write_text("# my own words, not committed\n", encoding="utf-8")

    said = script_stops(camp)
    script_fork(camp, ROOT)

    assert _origin(camp) == REAL_REMOTE
    assert "kept the origin it already had" in said
    assert _git(camp, "rev-parse", "--abbrev-ref", "HEAD") == "played"
    assert mine.read_text(encoding="utf-8") == "# my own words, not committed\n"
    _islands_are_green(camp)

    # A second run adds nothing and still leaves the camp where it found it.
    again = script_stops(camp)
    assert "0 deliverables" in again and "0 notes" in again
    assert "left as the learner had them" in again
    assert _git(camp, "rev-parse", "--abbrev-ref", "HEAD") == "played"
    assert _origin(camp) == REAL_REMOTE
    assert "kept the" in script_fork(camp, ROOT)
    _islands_are_green(camp)
