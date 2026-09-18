"""The terminal setup modules: complete, safe, idempotent."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from vibemap import dotfiles
from vibemap.cli import cli


def test_every_module_ships_its_files() -> None:
    for m in dotfiles.MODULES.values():
        for rel, target in m.files:
            text = dotfiles.source_text(rel)
            assert text.strip(), (m.id, rel)
            assert target.startswith(("~/", "vault:")), (m.id, target)
        assert m.what and m.docs.startswith("https://"), m.id
    assert "Tom's Toolbox" in dotfiles.source_text("zsh/vibe.zsh")


def test_install_writes_backs_up_and_appends_once(tmp_path: Path) -> None:
    home, vault = tmp_path / "home", tmp_path / "vault"
    home.mkdir()
    (home / ".zshrc").write_text("export EDITOR=zed\n", encoding="utf-8")
    m = dotfiles.get_module("zsh")
    assert not dotfiles.is_installed(m, home=home, vault=vault)
    p = dotfiles.install(m, home=home, vault=vault)
    assert [x[0].name for x in p.writes] == ["vibe.zsh"] and p.appends
    rc = (home / ".zshrc").read_text(encoding="utf-8")
    assert rc.startswith("export EDITOR=zed\n") and rc.count(dotfiles.ZSH_LINE) == 1
    assert dotfiles.is_installed(m, home=home, vault=vault)
    # a second install changes nothing and appends nothing
    again = dotfiles.install(m, home=home, vault=vault)
    assert not again.writes and not again.appends and again.skipped
    assert (home / ".zshrc").read_text(encoding="utf-8").count(dotfiles.ZSH_LINE) == 1
    # a differing existing file is backed up, not lost
    target = home / ".config" / "vibe" / "vibe.zsh"
    target.write_text("# mine\n", encoding="utf-8")
    p3 = dotfiles.install(m, home=home, vault=vault)
    assert p3.writes[0][1] is True
    backups = list(target.parent.glob("vibe.zsh.bak-*"))
    assert len(backups) == 1 and backups[0].read_text() == "# mine\n"


def test_vault_targets_land_in_the_vault(tmp_path: Path) -> None:
    home, vault = tmp_path / "home", tmp_path / "vault"
    m = dotfiles.get_module("obsidian-theme")
    dotfiles.install(m, home=home, vault=vault)
    assert (vault / ".obsidian" / "themes" / "R2-D2" / "manifest.json").exists()
    assert dotfiles.is_installed(m, home=home, vault=vault)


def test_dry_run_touches_nothing(tmp_path: Path) -> None:
    home, vault = tmp_path / "home", tmp_path / "vault"
    p = dotfiles.install(
        dotfiles.get_module("tmux"), home=home, vault=vault, dry_run=True
    )
    assert p.writes and not (home / ".config").exists()


def test_unknown_module_is_refused() -> None:
    with pytest.raises(ValueError, match="unknown module"):
        dotfiles.get_module("emacs")


def test_cli_lists_and_dry_runs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("VIBE_HOME_DIR", str(tmp_path))
    runner = CliRunner()
    out = runner.invoke(cli, ["dotfiles"])
    assert (
        out.exit_code == 0
        and "ghostty" in out.output
        and "obsidian-theme" in out.output
    )
    # A printed path is wrapped at the console's width, which is 80 on a CI
    # runner and wider in a terminal, so the width is fixed like everywhere else.
    dry = runner.invoke(
        cli, ["dotfiles", "install", "tmux", "--dry-run"], env={"COLUMNS": "200"}
    )
    assert dry.exit_code == 0, dry.output
    assert "tmux.conf" in dry.output and not (tmp_path / ".config").exists()
