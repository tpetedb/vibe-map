"""The played-camp regenerator is local, reviewable and explicit about pushes."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from tools import regen_played
from vibemap import campaign
from vibemap.state import State

ROOT = Path(__file__).resolve().parents[1]


def _git(repo: Path, *args: str) -> str:
    out = subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    )
    return out.stdout.strip()


def _repo(
    tmp_path: Path, *, remote_name: str = "vibe-map-played.git"
) -> tuple[Path, Path]:
    remote = tmp_path / remote_name
    subprocess.run(["git", "init", "--bare", "-q", remote], check=True)
    camp = tmp_path / "played"
    camp.mkdir()
    _git(camp, "init", "-q")
    _git(camp, "switch", "-qc", "played")
    (camp / "config").mkdir()
    (camp / "config" / "camp.toml").write_text("[learner]\nname = 'Old'\n")
    (camp / "stale.txt").write_text("old\n")
    _git(camp, "add", "-A")
    _git(
        camp,
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "-qm",
        "old played camp",
    )
    _git(camp, "remote", "add", "origin", str(remote))
    _git(camp, "push", "-qu", "origin", "played")
    return camp, remote


def test_the_demo_state_is_complete_and_shows_the_avatar_rewards() -> None:
    state = regen_played.played_state(ROOT)
    items = json.loads((ROOT / "vibemap/data/items.json").read_text())

    assert state.total_done() == campaign.total_stops() == 32
    assert set(state.path) == {mentor["id"] for mentor in campaign.mentors()}
    assert set(state.artifacts) == set(state.artifacts_built)
    assert set(state.mentors) == set(state.path)
    assert set(state.items) == {item["id"] for item in items["items"]}
    assert set(state.wear) == {"beanie", "shades", "jacket", "backpack", "lanyard"}
    assert set(state.wear) <= {wear["id"] for wear in items["wearables"]}
    assert {"campaign", "collector", "builder", "mentored"} <= set(state.ach)


def test_the_stage_is_a_current_camp_with_every_scripted_part(tmp_path: Path) -> None:
    stage = tmp_path / "stage"

    regen_played.prepare_stage(stage, ROOT)

    state = State.load(stage / ".vibe" / "state.json")
    assert state.total_done() == 32
    assert (stage / "workspace/mentors/karpathy/notes.md").is_file()
    assert (stage / "workspace/artifacts/cafe/notes.md").is_file()
    assert (stage / "workspace/forks/vibe-map/fork.json").is_file()
    assert (stage / "game/vibe-map.html").is_file()
    assert (stage / "docs/media/backpack.png").is_file()


def test_install_preserves_branch_and_origin_and_does_not_push(
    tmp_path: Path,
) -> None:
    camp, remote = _repo(tmp_path)
    stage = tmp_path / "stage"
    (stage / "config").mkdir(parents=True)
    (stage / "config" / "camp.toml").write_text("[learner]\nname = 'Tom'\n")
    (stage / "README.md").write_text("# Played now\n")
    state = State(name="Tom")
    state.save(stage / ".vibe" / "state.json")
    before_remote = _git(remote, "rev-parse", "refs/heads/played")

    changed = regen_played.install(stage, camp)

    assert changed is True
    assert _git(camp, "branch", "--show-current") == "played"
    assert _git(camp, "remote", "get-url", "origin") == str(remote)
    assert not (camp / "stale.txt").exists()
    assert (camp / "README.md").read_text() == "# Played now\n"
    assert _git(camp, "ls-files", ".vibe/state.json") == ".vibe/state.json"
    assert _git(remote, "rev-parse", "refs/heads/played") == before_remote
    assert _git(camp, "status", "--porcelain") == ""


def test_push_flag_pushes_the_reviewed_commit_without_regenerating(
    tmp_path: Path, monkeypatch
) -> None:
    camp, remote = _repo(tmp_path)
    stage = tmp_path / "stage"
    (stage / "config").mkdir(parents=True)
    (stage / "config" / "camp.toml").write_text("[learner]\nname = 'Tom'\n")
    (stage / "README.md").write_text("# New played camp\n")

    regen_played.install(stage, camp)
    before_push = _git(remote, "rev-parse", "refs/heads/played")
    reviewed = _git(camp, "rev-parse", "HEAD")
    assert before_push != reviewed

    def fail_if_regenerated(*_args, **_kwargs) -> None:
        raise AssertionError("--push must not regenerate after review")

    monkeypatch.setattr(regen_played, "prepare_stage", fail_if_regenerated)
    result = regen_played.regenerate(camp, ROOT, dry_run=False, push=True)

    assert result == f"pushed reviewed commit: {camp.resolve()} on played"
    assert _git(camp, "rev-parse", "HEAD") == reviewed
    assert _git(remote, "rev-parse", "refs/heads/played") == reviewed


def test_failed_install_restores_the_clean_target(tmp_path: Path, monkeypatch) -> None:
    camp, _ = _repo(tmp_path)
    (camp / ".gitignore").write_text(".vibe/\n")
    _git(camp, "add", ".gitignore")
    _git(
        camp,
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "-qm",
        "ignore local state",
    )
    stage = tmp_path / "stage"
    (stage / "config").mkdir(parents=True)
    (stage / "config" / "camp.toml").write_text("[learner]\nname = 'Tom'\n")
    (stage / "README.md").write_text("# New played camp\n")
    before = _git(camp, "rev-parse", "HEAD")
    copytree = regen_played.shutil.copytree

    def fail_after_copy(*args, **kwargs) -> None:
        copytree(*args, **kwargs)
        raise OSError("injected copy failure")

    monkeypatch.setattr(regen_played.shutil, "copytree", fail_after_copy)
    with pytest.raises(OSError, match="injected copy failure"):
        regen_played.install(stage, camp)

    assert _git(camp, "rev-parse", "HEAD") == before
    assert _git(camp, "status", "--porcelain") == ""
    assert (camp / "stale.txt").read_text() == "old\n"
    assert (camp / "config" / "camp.toml").read_text() == "[learner]\nname = 'Old'\n"
    assert not (camp / ".vibe").exists()
    assert _git(camp, "status", "--porcelain", "--ignored") == ""


def test_missing_product_inputs_are_refused_before_regeneration(
    tmp_path: Path,
) -> None:
    camp, _ = _repo(tmp_path)
    product = tmp_path / "product"
    product.mkdir()

    with pytest.raises(
        regen_played.RegenerationError,
        match="game/vibe-map.html, docs/media/",
    ):
        regen_played.regenerate(camp, product, dry_run=True, push=False)

    assert _git(camp, "status", "--porcelain", "--ignored") == ""


def test_partial_media_is_refused_before_regeneration(tmp_path: Path) -> None:
    camp, _ = _repo(tmp_path)
    product = tmp_path / "product"
    (product / "game").mkdir(parents=True)
    (product / "game" / "vibe-map.html").write_text("game\n")
    (product / "docs" / "media").mkdir(parents=True)
    (product / "docs" / "media" / "README.md").write_text("media\n")

    with pytest.raises(
        regen_played.RegenerationError,
        match="docs/media/gameplay.gif, docs/media/hero.png",
    ):
        regen_played.regenerate(camp, product, dry_run=True, push=False)

    assert _git(camp, "status", "--porcelain", "--ignored") == ""


def test_install_refuses_to_replace_ignored_learner_data(tmp_path: Path) -> None:
    camp, _ = _repo(tmp_path)
    (camp / ".gitignore").write_text(".vibe/\n")
    _git(camp, "add", ".gitignore")
    _git(
        camp,
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "-qm",
        "ignore local state",
    )
    existing = camp / ".vibe" / "state.json"
    existing.parent.mkdir()
    existing.write_text('{"learner": "keep me"}\n')
    stage = tmp_path / "stage"
    state = State(name="Tom")
    state.save(stage / ".vibe" / "state.json")

    with pytest.raises(
        regen_played.RegenerationError,
        match="ignored data that regeneration would replace: .vibe/state.json",
    ):
        regen_played.install(stage, camp)

    assert existing.read_text() == '{"learner": "keep me"}\n'


def test_install_keeps_matching_ignored_data(tmp_path: Path) -> None:
    camp, _ = _repo(tmp_path)
    (camp / ".gitignore").write_text("private/\n")
    _git(camp, "add", ".gitignore")
    _git(
        camp,
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "-qm",
        "ignore private data",
    )
    private = camp / "private" / "same.txt"
    private.parent.mkdir()
    private.write_text("preserve me\n")
    inode = private.stat().st_ino
    stage = tmp_path / "stage"
    (stage / "private").mkdir(parents=True)
    (stage / "private" / "same.txt").write_text("preserve me\n")
    (stage / ".gitignore").write_text("private/\n")
    (stage / "README.md").write_text("# New played camp\n")

    assert regen_played.install(stage, camp) is True
    assert private.read_text() == "preserve me\n"
    assert private.stat().st_ino == inode
    assert _git(camp, "status", "--porcelain") == ""


def test_install_refuses_to_expose_ignored_learner_data(tmp_path: Path) -> None:
    camp, _ = _repo(tmp_path)
    (camp / ".gitignore").write_text("private/\n")
    _git(camp, "add", ".gitignore")
    _git(
        camp,
        "-c",
        "user.name=Test",
        "-c",
        "user.email=test@example.invalid",
        "commit",
        "-qm",
        "ignore private data",
    )
    private = camp / "private" / "token.txt"
    private.parent.mkdir()
    private.write_text("keep private\n")
    before = _git(camp, "rev-parse", "HEAD")
    stage = tmp_path / "stage"
    stage.mkdir()
    (stage / ".gitignore").write_text(".vibe/\n")

    with pytest.raises(
        regen_played.RegenerationError,
        match="expose ignored target data: private/token.txt",
    ):
        regen_played.install(stage, camp)

    assert _git(camp, "rev-parse", "HEAD") == before
    assert private.read_text() == "keep private\n"
    assert _git(camp, "ls-files", "private/token.txt") == ""
    assert "!! private/" in _git(camp, "status", "--porcelain", "--ignored")


def test_a_dirty_target_is_refused_before_any_file_changes(tmp_path: Path) -> None:
    camp, _ = _repo(tmp_path)
    marker = camp / "mine.txt"
    marker.write_text("unfinished\n")

    with pytest.raises(regen_played.RegenerationError, match="not clean"):
        regen_played.check_target(camp)

    assert marker.read_text() == "unfinished\n"


def test_a_clean_product_checkout_is_refused_before_replacement(tmp_path: Path) -> None:
    camp, remote = _repo(tmp_path, remote_name="vibe-map.git")
    before = _git(camp, "rev-parse", "HEAD")
    remote_before = _git(remote, "rev-parse", "refs/heads/played")

    with pytest.raises(
        regen_played.RegenerationError, match="not the tpetedb/vibe-map-played"
    ):
        regen_played.regenerate(camp, ROOT, dry_run=False, push=False)

    assert _git(camp, "rev-parse", "HEAD") == before
    assert _git(camp, "status", "--porcelain") == ""
    assert (camp / "stale.txt").read_text() == "old\n"
    assert _git(remote, "rev-parse", "refs/heads/played") == remote_before


def test_a_misdirected_push_url_is_refused(tmp_path: Path) -> None:
    camp, _ = _repo(tmp_path)
    other = tmp_path / "vibe-map.git"
    subprocess.run(["git", "init", "--bare", "-q", other], check=True)
    _git(camp, "remote", "set-url", "--push", "origin", str(other))

    with pytest.raises(
        regen_played.RegenerationError, match="not the tpetedb/vibe-map-played"
    ):
        regen_played.check_target(camp)


def test_repeating_the_same_product_keeps_the_reviewed_commit(tmp_path: Path) -> None:
    camp, remote = _repo(tmp_path)
    remote_before = _git(remote, "rev-parse", "refs/heads/played")

    first = regen_played.regenerate(camp, ROOT, dry_run=False, push=False)
    reviewed = _git(camp, "rev-parse", "HEAD")
    second = regen_played.regenerate(camp, ROOT, dry_run=False, push=False)

    assert first.startswith("regenerated:")
    assert second.startswith("already current:")
    assert _git(camp, "rev-parse", "HEAD") == reviewed
    assert _git(camp, "status", "--porcelain") == ""
    assert _git(remote, "rev-parse", "refs/heads/played") == remote_before
    assert _git(camp, "ls-files", str(regen_played.SOURCE_MARKER)) == str(
        regen_played.SOURCE_MARKER
    )
    mcp = json.loads((camp / "workspace/artifacts/bridge/mcp.json").read_text())
    assert mcp["mcpServers"]["camp-scores"]["args"][1] == str(camp)


def test_dry_run_only_reports_the_named_checkout(tmp_path: Path) -> None:
    camp, _ = _repo(tmp_path)
    before = _git(camp, "rev-parse", "HEAD")

    result = regen_played.regenerate(camp, ROOT, dry_run=True, push=False)

    assert result == f"would regenerate without pushing: {camp.resolve()} on played"
    assert _git(camp, "rev-parse", "HEAD") == before
