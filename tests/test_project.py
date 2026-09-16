"""Camp discovery: the installed CLI must find the camp from any folder."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from vibemap import project


@pytest.fixture(autouse=True)
def _fresh_root(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("VIBE_HOME", raising=False)
    project.root.cache_clear()
    yield
    project.root.cache_clear()


def test_root_walks_up_to_the_nearest_vibe_toml(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    camp = tmp_path / "camp"
    deep = camp / "vault" / "Camp"
    deep.mkdir(parents=True)
    (camp / "vibe.toml").write_text("[player]\n", encoding="utf-8")
    monkeypatch.chdir(deep)
    assert project.root() == camp.resolve()
    assert project.is_camp()


def test_root_prefers_vibe_home(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    home = tmp_path / "elsewhere"
    home.mkdir()
    (home / "vibe.toml").write_text("", encoding="utf-8")
    monkeypatch.setenv("VIBE_HOME", str(home))
    monkeypatch.chdir(tmp_path)
    assert project.root() == home.resolve()


def test_root_falls_back_to_cwd_outside_a_camp(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    lonely = tmp_path / "no-camp-here"
    lonely.mkdir()
    monkeypatch.chdir(lonely)
    assert project.root() == lonely.resolve()
    assert not project.is_camp()
    assert os.environ.get("VIBE_HOME") is None


def test_package_data_ships_with_the_wheel() -> None:
    assert project.data_path("campaign.json").exists()
    assert "evenings" in project.data_text("campaign.json")
    assert project.data_text("resources.md").startswith("#")
