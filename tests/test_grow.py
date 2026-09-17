"""Grow mode: the vault starts small, unlocks with progress, never loses a note."""

from __future__ import annotations

from pathlib import Path

from vibemap import grow
from vibemap.config import Config
from vibemap.personas import get_persona
from vibemap.state import LogEntry, State
from vibemap.vault import Vault


def _vault(tmp_path: Path, state: State) -> Vault:
    cfg = Config()
    cfg.vault.path = str(tmp_path / "vault")
    cfg.vault.mode = "grow"
    v = Vault(cfg, state)
    (v.dir.parent / ".obsidian").mkdir(parents=True)
    (v.dir.parent / ".obsidian" / "app.json").write_text(
        '{"userIgnoreFilters": []}', encoding="utf-8"
    )
    return v


def test_grow_starts_small_and_unlocks_with_progress(tmp_path: Path) -> None:
    st = State(name="Tom")
    v = _vault(tmp_path, st)
    v.build(get_persona("data-engineer"))
    camp = {p.stem for p in v.notes()}
    lib = grow.library_dir(v)
    waiting = {p.stem for p in lib.glob("*.md")}
    assert "Tonight" in camp and "Map" in camp and "Your field" in camp
    assert "Innovation Hub" not in camp and "Innovation Hub" in waiting
    assert "Docker and containers" in waiting
    assert not v.lint().dead_links
    assert "_library/" in (v.dir.parent / ".obsidian" / "app.json").read_text()
    assert "waiting in `_library`" in v.path("Tonight").read_text(encoding="utf-8")
    # finish the first stop, inspect the dock, go deep with a mentor
    st.done_w["campus"].append(1)
    st.log.append(LogEntry(world="campus", n=1, at="2026-09-17T18:40", note="shipped"))
    st.artifacts.append("dock")
    st.path["cherny"] = "deep"
    v.build(get_persona("data-engineer"))
    camp = {p.stem for p in v.notes()}
    assert "Innovation Hub" in camp
    assert "Docker and containers" in camp and "CI-CD and automation" in camp
    assert "Boris Cherny" in camp
    assert "Kubernetes and platforms" not in camp
    assert not v.lint().dead_links


def test_unlock_by_hand_and_restore_all(tmp_path: Path) -> None:
    st = State(name="Tom")
    v = _vault(tmp_path, st)
    v.build(get_persona("data-engineer"))
    p = grow.unlock(v, "Git")
    assert p is not None and p.exists() and "Git" in st.unlocked
    assert grow.unlock(v, "No such note") is None
    # a rebuild keeps the hand-unlocked note in the camp
    v.build(get_persona("data-engineer"))
    assert v.exists("Git")
    # a note the learner wrote is never moved
    v.write("My own note", "Mine. Back to [[Tonight]].", tags=["concept"])
    v.build(get_persona("data-engineer"))
    assert v.exists("My own note")
    moved = grow.restore_all(v)
    assert moved > 50 and not grow.library_dir(v).exists()
    assert v.exists("Kubernetes and platforms")


def test_full_mode_never_touches_the_library(tmp_path: Path) -> None:
    st = State(name="Tom")
    cfg = Config()
    cfg.vault.path = str(tmp_path / "vault")
    v = Vault(cfg, st)
    v.build(get_persona("data-engineer"))
    assert not grow.library_dir(v).exists()
    assert v.exists("Kubernetes and platforms")
