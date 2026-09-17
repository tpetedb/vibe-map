"""The three configuration levels, and the fork that owns the source level.

Journey configuration lives in config/camp.toml; the retired vibe.toml is
still read for one release and says so. Source configuration for the game
lives in src/config/, which is what a learner's fork changes.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

from tests.conftest import ROOT
from vibemap import project, quests
from vibemap.cli import cli
from vibemap.config import Config, deprecation_note

CAMP_TOML = """[learner]
name = "Lotte"
difficulty = "hard"
"""


def _run(camp: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "vibemap.cli", *args],
        cwd=camp,
        env=dict(os.environ, VIBE_HOME=str(camp), COLUMNS="200"),
        capture_output=True,
        text=True,
    )


# ---- the journey level ---------------------------------------------------------


def test_config_loads_from_either_location(tmp_path: Path) -> None:
    new = tmp_path / "new"
    (new / "config").mkdir(parents=True)
    (new / "config" / "camp.toml").write_text(CAMP_TOML, encoding="utf-8")
    old = tmp_path / "old"
    old.mkdir()
    (old / "vibe.toml").write_text(CAMP_TOML, encoding="utf-8")
    for base in (new, old):
        cfg = Config.load(project.config_path(base))
        assert cfg.learner.name == "Lotte" and cfg.learner.difficulty == "hard"


def test_camp_toml_wins_over_the_retired_vibe_toml(tmp_path: Path) -> None:
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "camp.toml").write_text(CAMP_TOML, encoding="utf-8")
    (tmp_path / "vibe.toml").write_text('[learner]\nname = "Stale"\n', encoding="utf-8")
    assert project.config_path(tmp_path).name == "camp.toml"
    assert project.legacy_config_in_use(tmp_path) is None
    assert Config.load(project.config_path(tmp_path)).learner.name == "Lotte"


def test_a_camp_without_either_file_writes_the_new_one(tmp_path: Path) -> None:
    p = project.config_path(tmp_path)
    assert p == tmp_path / "config" / "camp.toml"
    Config().save(p)
    assert p.exists() and "journey configuration" in p.read_text(encoding="utf-8")


def test_the_retired_name_is_read_and_deprecated(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "vibe.toml").write_text(CAMP_TOML, encoding="utf-8")
    monkeypatch.setattr("vibemap.config.ROOT", tmp_path)
    note = deprecation_note()
    assert note is not None and "config/camp.toml" in note
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "camp.toml").write_text(CAMP_TOML, encoding="utf-8")
    assert deprecation_note() is None


def test_both_names_mark_a_camp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for name in ("config/camp.toml", "vibe.toml"):
        camp = tmp_path / name.replace("/", "-")
        (camp / Path(name)).parent.mkdir(parents=True)
        (camp / name).write_text("", encoding="utf-8")
        deep = camp / "workspace" / "forks"
        deep.mkdir(parents=True)
        monkeypatch.chdir(deep)
        project.root.cache_clear()
        assert project.is_camp(camp)
        assert project.nearest_config(deep) == camp / name
    project.root.cache_clear()


def test_the_template_ships_the_new_name() -> None:
    template = ROOT / "vibemap" / "data" / "template"
    assert (template / "config" / "camp.toml").exists()
    assert not (template / "vibe.toml").exists()
    assert Config.load(template / "config" / "camp.toml").learner.name.startswith("<")


# ---- the source level and the fork ---------------------------------------------


def test_the_build_reads_src_config() -> None:
    config_js = (ROOT / "src" / "config" / "00-config.js").read_text(encoding="utf-8")
    assert "WORLD_SCALE" in config_js and "PALETTE" in config_js
    game = (ROOT / "game" / "vibe-map.html").read_text(encoding="utf-8")
    assert "const WORLD_SCALE=" in game
    # The configuration is in scope before the modules that use it.
    assert game.index("const WORLD_SCALE=") < game.index("const P=(x,z)=>")


@pytest.mark.integration
def test_vibe_fork_builds_and_is_checked_end_to_end(tmp_path: Path) -> None:
    camp = tmp_path / "camp"
    out = CliRunner().invoke(cli, ["new", str(camp), "--name", "Lotte"])
    assert out.exit_code == 0, out.output

    made = _run(camp, "fork", "--from", str(ROOT))
    assert made.returncode == 0, made.stdout + made.stderr
    fork = camp / quests.FORK_DIR
    for rel in (
        "src/config/00-config.js",
        "src/vendor/three.min.js",
        "tools/build.py",
        "tools/generated/tree.js",
        "tools/generated/campaign.json",
        "justfile",
    ):
        assert (fork / rel).exists(), rel
    manifest = json.loads((fork / quests.FORK_MANIFEST).read_text(encoding="utf-8"))
    assert manifest["version"] == quests.FORK_VERSION

    # An untouched fork is not yet the learner's: it builds, but nothing differs.
    first = _run(camp, "check", "--fork")
    assert "src/config is still the product's" in first.stdout, first.stdout
    assert first.returncode == 0

    cfg_js = fork / "src" / "config" / "00-config.js"
    cfg_js.write_text(
        cfg_js.read_text(encoding="utf-8").replace(
            "const WORLD_SCALE=1.6;", "const WORLD_SCALE=2.4;"
        ),
        encoding="utf-8",
    )
    second = _run(camp, "check", "--fork")
    assert "your fork builds and is yours" in second.stdout, second.stdout
    built = (fork / "game" / "vibe-map.html").read_text(encoding="utf-8")
    assert "const WORLD_SCALE=2.4;" in built
    assert built != (ROOT / "game" / "vibe-map.html").read_text(encoding="utf-8")


@pytest.mark.integration
def test_the_fork_refuses_a_second_one_without_force(tmp_path: Path) -> None:
    camp = tmp_path / "camp"
    assert CliRunner().invoke(cli, ["new", str(camp), "--name", "Lotte"]).exit_code == 0
    assert _run(camp, "fork", "--from", str(ROOT)).returncode == 0
    again = _run(camp, "fork", "--from", str(ROOT))
    assert again.returncode != 0 and "--force" in again.stdout
    assert _run(camp, "fork", "--from", str(ROOT), "--force").returncode == 0


def test_fork_needs_a_product_checkout(tmp_path: Path) -> None:
    camp = tmp_path / "camp"
    assert CliRunner().invoke(cli, ["new", str(camp), "--name", "Lotte"]).exit_code == 0
    out = _run(camp, "fork", "--from", str(tmp_path))
    assert out.returncode != 0 and "not a product checkout" in out.stdout
