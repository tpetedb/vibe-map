"""`vibe new` and the commands that write config/camp.toml.

Every one of these goes through the real command, because the defect they
guard against is a file written by one command and read back by the next.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tomllib
from datetime import date
from pathlib import Path

import pytest
from click.testing import CliRunner

from vibemap.cli import SLUG_MAX, camp_dir_name, cli
from vibemap.config import Config, toml_str

# A name that has every escape TOML basic strings know about, plus letters no
# ASCII fold keeps. No emoji: the repository refuses them.
AWKWARD_NAMES = [
    'He said "hi"',
    "C:\\Users\\Tom",
    "Jörg Müller",
    "Bjørn Østergård",
    "Анна Каренина",
    "line one\nline two",
    "tab\there",
    'back\\slash and "quote" and \nnewline',
]


def _run(camp: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "vibemap.cli", *args],
        cwd=camp,
        env=dict(os.environ, VIBE_HOME=str(camp), COLUMNS="200"),
        capture_output=True,
        text=True,
    )


# ---- the serialiser ------------------------------------------------------------


@pytest.mark.parametrize("value", AWKWARD_NAMES)
def test_a_toml_string_survives_the_round_trip(value: str) -> None:
    assert tomllib.loads(f"name = {toml_str(value)}")["name"] == value


def test_a_control_character_is_escaped_not_written_raw() -> None:
    assert toml_str("bell\x07") == '"bell\\u0007"'


@pytest.mark.parametrize("value", AWKWARD_NAMES)
def test_the_whole_config_round_trips_through_the_file(
    tmp_path: Path, value: str
) -> None:
    cfg = Config()
    cfg.learner.name = value
    cfg.theme.preset = value
    path = tmp_path / "camp.toml"
    cfg.save(path)
    back = Config.load(path)
    assert back.learner.name == value
    assert back.theme.preset == value


# ---- vibe new ------------------------------------------------------------------


@pytest.mark.parametrize("value", ['He said "hi"', "C:\\Users\\Tom", "Bjørn Østergård"])
def test_vibe_new_writes_a_name_every_command_can_read_back(
    tmp_path: Path, value: str
) -> None:
    camp = tmp_path / "camp"
    out = CliRunner().invoke(cli, ["new", str(camp), "--name", value])
    assert out.exit_code == 0, out.output
    assert Config.load(camp / "config" / "camp.toml").learner.name == value
    status = _run(camp, "status", "--json")
    assert status.returncode == 0, status.stdout + status.stderr
    assert json.loads(status.stdout)["name"] == value


def test_a_pasted_name_does_not_make_a_folder_the_disk_refuses(tmp_path: Path) -> None:
    long = "Ludwig" * 40
    assert len(camp_dir_name(long)) < 100
    assert camp_dir_name(long).startswith("vibe-map-" + "ludwig" * 2)
    assert camp_dir_name(long).endswith(date.today().isoformat())
    assert len(camp_dir_name(long)) == len("vibe-map--") + SLUG_MAX + len("2026-09-19")
    out = CliRunner().invoke(cli, ["new", str(tmp_path / "c"), "--name", long])
    assert out.exit_code == 0, out.output
    assert Config.load(tmp_path / "c" / "config" / "camp.toml").learner.name == long


def test_github_without_gh_says_so_instead_of_a_traceback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("PATH", str(tmp_path / "empty"))
    camp = tmp_path / "camp"
    out = CliRunner().invoke(cli, ["new", str(camp), "--github", "me/camp"])
    assert out.exit_code == 1, out.output
    assert "gh" in out.output
    assert "Traceback" not in out.output
    # It refuses before building half a camp on disk.
    assert not camp.exists()


# ---- the commands that write the file -------------------------------------------


def _camp(tmp_path: Path) -> Path:
    camp = tmp_path / "camp"
    out = CliRunner().invoke(cli, ["new", str(camp), "--name", "Tom"])
    assert out.exit_code == 0, out.output
    return camp


def test_a_name_with_rich_markup_completes_everywhere(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    out = _run(camp, "name", "[/x]Bad")
    assert out.returncode == 0, out.stdout + out.stderr
    assert "MarkupError" not in out.stderr
    assert Config.load(camp / "config" / "camp.toml").learner.name == "[/x]Bad"
    assert json.loads(_run(camp, "status", "--json").stdout)["name"] == "[/x]Bad"
    shown = _run(camp, "name")
    assert shown.returncode == 0, shown.stdout + shown.stderr
    assert "[/x]Bad" in shown.stdout


def test_an_empty_name_is_refused(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    out = _run(camp, "name", "   ")
    assert out.returncode == 1, out.stdout
    assert Config.load(camp / "config" / "camp.toml").learner.name == "Tom"


def test_a_mistyped_vibe_home_is_named_instead_of_becoming_a_camp(
    tmp_path: Path,
) -> None:
    nowhere = tmp_path / "no-such-camp"
    out = subprocess.run(
        [sys.executable, "-m", "vibemap.cli", "name", "Zed"],
        cwd=tmp_path,
        env=dict(os.environ, VIBE_HOME=str(nowhere), COLUMNS="200"),
        capture_output=True,
        text=True,
    )
    assert out.returncode == 1, out.stdout
    assert "vibe new" in out.stdout
    assert not nowhere.exists()


def test_the_config_file_is_spelled_one_way(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    for args in (("interests", "set", "data"), ("interests", "all"), ("name", "Ann")):
        out = _run(camp, *args)
        assert out.returncode == 0, out.stdout + out.stderr
        assert "config/camp.toml" in out.stdout, args
        assert "(camp.toml)" not in out.stdout, args


def test_vibe_config_help_promises_only_what_it_has(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    out = _run(camp, "config", "--help")
    assert out.returncode == 0, out.stdout
    assert "Show config/camp.toml" in out.stdout
    assert "Show or change" not in out.stdout


# ---- the camp template ----------------------------------------------------------

TEMPLATE = Path(__file__).resolve().parents[1] / "vibemap" / "data" / "template"


def test_the_done_recipe_forwards_the_flag_its_error_advises() -> None:
    assert "done n note *args:" in (TEMPLATE / "justfile").read_text()
    assert "{{args}}" in (TEMPLATE / "justfile").read_text()


def test_break_refuses_to_carry_uncommitted_work_onto_the_play_branch() -> None:
    body = (TEMPLATE / "justfile").read_text().split("break name:")[1]
    assert "git status --porcelain" in body.split("rescue:")[0]


def test_the_retired_config_name_is_gone_from_what_a_learner_reads() -> None:
    from vibemap.themes import THEMES

    assert "vibe.toml" not in THEMES["studio"].to_toml()
    assert "config/camp.toml" in THEMES["studio"].to_toml()
    for f in (TEMPLATE / "env.example", TEMPLATE / "README.md"):
        assert "vibe.toml" not in f.read_text(), f
    tui = (Path(__file__).resolve().parents[1] / "vibemap" / "tui.py").read_text()
    assert "lives in config/camp.toml" in tui


def test_the_persona_recipes_name_the_folder_the_dataset_lands_in() -> None:
    from vibemap.personas import PERSONAS

    for p in PERSONAS.values():
        for r in p.recipes:
            assert f"workspace/data/{p.dataset.filename}" not in r.prompt, p.id


def test_the_camp_readme_says_which_recipes_need_just() -> None:
    readme = (TEMPLATE / "README.md").read_text()
    assert "Every recipe in this camp is one line that calls" not in readme
    assert "no `vibe` equivalent" in readme
