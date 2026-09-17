"""Obsidian feature modules: grounded in the help, lint-clean in a fresh vault."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from vibemap import obsidian, project
from vibemap.cli import cli
from vibemap.config import Config
from vibemap.personas import get_persona
from vibemap.state import State
from vibemap.vault import Vault

EM_DASH = chr(0x2014)


def test_every_feature_is_grounded_and_clean() -> None:
    feats = obsidian.features()
    assert len(feats) >= 30
    for f in feats.values():
        assert f.url.startswith("https://help.obsidian.md/"), f.id
        assert 3 <= len(f.facts) <= 6, f.id
        assert f.what and f.try_it, f.id
        assert EM_DASH not in f.what + f.try_it + " ".join(f.facts), f.id
    for fid in obsidian.EXTRAS:
        assert fid in feats, fid


def test_package_data_is_valid_json() -> None:
    data = json.loads(project.data_text("obsidian.json"))
    ids = [d["id"] for d in data]
    assert len(ids) == len(set(ids))


def test_bootstrap_all_is_lint_clean(tmp_path: Path) -> None:
    cfg = Config()
    cfg.vault.path = str(tmp_path / "vault")
    st = State(name="Tom")
    v = Vault(cfg, st)
    v.build(get_persona(cfg.learner.persona))
    titles = obsidian.bootstrap(v.dir, list(obsidian.features()), write=v.write)
    assert len(titles) == len(obsidian.features())
    assert (v.dir / "Camp map.canvas").exists()
    assert (v.dir.parent / "_templates" / "obsidian" / "Feature note.md").exists()
    canvas = json.loads((v.dir / "Camp map.canvas").read_text())
    assert {n["id"] for n in canvas["nodes"]} == {"a1", "a2", "a3"}
    report = v.lint()
    assert not report.dead_links, report.dead_links
    assert not report.orphans, report.orphans


def test_vault_feature_lists_and_refuses_unknown() -> None:
    runner = CliRunner()
    out = runner.invoke(cli, ["vault", "feature"])
    assert out.exit_code == 0 and "canvas" in out.output
    bad = runner.invoke(cli, ["vault", "feature", "telepathy"])
    assert bad.exit_code != 0 and "unknown feature" in bad.output
