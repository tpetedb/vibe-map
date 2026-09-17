"""Artifacts as tasks: the Do it for real walkthroughs and their checks.

Every artifact gets a fixture that is a plausible finished piece of work, built
the way its own walkthrough says; the fixtures live in tools/script_camp.py so
the played instance is scripted with the same files these tests check. The
check then has to pass on it. A check that needs a tool this machine may not
have says so in its detail instead of failing, and the test reads that sentence
rather than guessing.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from tools.script_camp import FIXTURES, FOUNTAIN, NOTE
from vibemap import campaign
from vibemap.artifact_checks import (
    ARTIFACT_SECTION,
    KINDS,
    artifact_ids,
    artifact_quest,
    get_artifact,
)
from vibemap.config import Config
from vibemap.quests import run_quest
from vibemap.state import State, decode_code

GOD = Config.model_validate({"learner": {"difficulty": "god"}})


def _build(tmp_path: Path, artifact_id: str, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Write the fixture into a workspace of its own and point the checks at it."""
    here = tmp_path / "workspace" / "artifacts" / artifact_id
    here.mkdir(parents=True)
    for name, body in FIXTURES[artifact_id].items():
        (here / name).write_text(body, encoding="utf-8")
    (here / "notes.md").write_text(NOTE, encoding="utf-8")
    monkeypatch.setattr(
        "vibemap.artifact_checks.ARTIFACTS_DIR", tmp_path / "workspace" / "artifacts"
    )
    return here


# ---- the data ------------------------------------------------------------------


def test_every_artifact_has_a_sourced_walkthrough_under_twenty_minutes() -> None:
    for a in campaign.artifacts():
        real = a["real"]
        assert real["dir"] == f"workspace/artifacts/{a['id']}", a["id"]
        assert 0 < real["minutes"] <= 20, a["id"]
        assert real["doc"]["url"].startswith("https://"), a["id"]
        assert real["doc"]["title"] and real["done"], a["id"]
        assert 3 <= len(real["steps"]) <= 5, a["id"]
        assert real["commands"], a["id"]
        assert real["check"]["kind"] in KINDS, a["id"]


def test_the_walkthroughs_keep_the_house_style() -> None:
    dashes = (chr(0x2014), chr(0x2013))  # spelled by code point: the gate bans them
    for a in campaign.artifacts():
        text = json.dumps(a["real"], ensure_ascii=False)
        assert not any(d in text for d in dashes), a["id"]


def test_every_artifact_quest_has_two_checks_with_hints() -> None:
    for artifact_id in artifact_ids():
        quest = artifact_quest(artifact_id, GOD)
        assert len(quest.checks) == 2, artifact_id
        assert all(c.hint for c in quest.checks), artifact_id


def test_an_unknown_artifact_id_is_refused() -> None:
    with pytest.raises(ValueError, match="unknown artifact"):
        get_artifact("nothing-like-that")


# ---- the checks ----------------------------------------------------------------


@pytest.mark.parametrize("artifact_id", artifact_ids())
def test_a_finished_artifact_passes_its_own_check(
    artifact_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _build(tmp_path, artifact_id, monkeypatch)
    results = run_quest(artifact_quest(artifact_id, GOD), GOD)
    assert all(r.ok for r in results), [(r.name, r.detail) for r in results]


@pytest.mark.parametrize("artifact_id", artifact_ids())
def test_an_empty_workspace_fails_every_artifact_check(
    artifact_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "vibemap.artifact_checks.ARTIFACTS_DIR", tmp_path / "workspace" / "artifacts"
    )
    results = run_quest(artifact_quest(artifact_id, GOD), GOD)
    assert not any(r.ok for r in results), [(r.name, r.detail) for r in results]
    assert "does not exist" in results[0].detail


def test_a_missing_tool_is_reported_rather_than_failed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Docker and scikit-learn are optional; the check says which layer answered."""
    _build(tmp_path, "dock", monkeypatch)
    monkeypatch.setattr("vibemap.artifact_checks._tool", lambda name: False)
    detail = run_quest(artifact_quest("dock", GOD), GOD)[0].detail
    assert "docker is not installed" in detail and "parse" in detail

    _build(tmp_path, "school", monkeypatch)
    monkeypatch.setattr("vibemap.artifact_checks.find_spec", lambda name: None)
    detail = run_quest(artifact_quest("school", GOD), GOD)[0].detail
    assert "scikit-learn is not installed" in detail


def test_a_half_finished_artifact_says_what_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    here = _build(tmp_path, "post-office", monkeypatch)
    (here / "postoffice.py").write_text(
        "import queue\nq = queue.Queue()\nq.put(1)\nq.task_done()\n"
        "print('delivered 1')\n",
        encoding="utf-8",
    )
    detail = run_quest(artifact_quest("post-office", GOD), GOD)[0].detail
    assert "delivered 2" in detail

    (here / "notes.md").write_text(
        f"{ARTIFACT_SECTION}\n\nnot much\n", encoding="utf-8"
    )
    note = run_quest(artifact_quest("post-office", GOD), GOD)[1]
    assert not note.ok and "needs 25" in note.detail


def test_a_broken_file_fails_its_kind(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    here = _build(tmp_path, "windmill", monkeypatch)
    (here / "nightly.yml").write_text(
        "# cron goes here one day\non:\n  push:\njobs: {}\n", encoding="utf-8"
    )
    detail = run_quest(artifact_quest("windmill", GOD), GOD)[0].detail
    assert "at least one job" in detail

    here = _build(tmp_path, "bridge", monkeypatch)
    (here / "mcp.json").write_text('{"mcpServers": {}}\n', encoding="utf-8")
    assert "no mcpServers" in run_quest(artifact_quest("bridge", GOD), GOD)[0].detail

    here = _build(tmp_path, "office", monkeypatch)
    (here / "reviewer.md").write_text(
        "---\nname: Camp Reviewer\ndescription: x\ntools: Read\n---\n\nbody\n",
        encoding="utf-8",
    )
    assert "hyphens" in run_quest(artifact_quest("office", GOD), GOD)[0].detail


def test_a_secret_in_the_example_file_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    here = _build(tmp_path, "bank", monkeypatch)
    (here / "env.example").write_text(
        "ANTHROPIC_API_KEY=sk-ant-looks-real\n", encoding="utf-8"
    )
    detail = run_quest(artifact_quest("bank", GOD), GOD)[0].detail
    assert "must not contain" in detail


# ---- the CLI and the progress code ---------------------------------------------


def _run(camp: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "vibemap.cli", *args],
        cwd=camp,
        env=dict(os.environ, VIBE_HOME=str(camp), COLUMNS="200"),
        capture_output=True,
        text=True,
    )


def test_vibe_check_artifact_claims_and_reaches_the_vault(tmp_path: Path) -> None:
    from click.testing import CliRunner

    from vibemap.cli import cli

    camp = tmp_path / "camp"
    made = CliRunner().invoke(cli, ["new", str(camp), "--name", "Tom"])
    assert made.exit_code == 0, made.output

    out = _run(camp, "check", "--artifact", "fountain")
    assert out.returncode == 0, out.stdout + out.stderr
    assert "does not exist" in out.stdout

    here = camp / "workspace" / "artifacts" / "fountain"
    here.mkdir(parents=True)
    (here / "fountain.py").write_text(FOUNTAIN, encoding="utf-8")
    (here / "notes.md").write_text(NOTE, encoding="utf-8")

    out = _run(camp, "check", "--artifact", "fountain")
    assert out.returncode == 0, out.stdout + out.stderr
    assert "built for real" in out.stdout and "+" in out.stdout
    state = json.loads((camp / ".vibe" / "state.json").read_text())
    assert state["artifactsBuilt"] == ["fountain"]
    assert state["artifacts"] == ["fountain"] and state["xp"] > 0
    note = (camp / "vault" / "Camp" / "Artifacts.md").read_text()
    assert "built for real: **The fountain**" in note
    assert "vibe check --artifact fountain" in note

    # A second run does not pay twice.
    xp = state["xp"]
    _run(camp, "check", "--artifact", "fountain")
    assert json.loads((camp / ".vibe" / "state.json").read_text())["xp"] == xp


def test_an_unknown_artifact_on_the_command_line_is_refused(tmp_path: Path) -> None:
    from click.testing import CliRunner

    from vibemap.cli import cli

    camp = tmp_path / "camp"
    assert CliRunner().invoke(cli, ["new", str(camp), "--name", "Tom"]).exit_code == 0
    out = _run(camp, "check", "--artifact", "nowhere")
    assert out.returncode == 1 and "unknown artifact" in out.stdout


def test_the_progress_code_carries_what_was_built_for_real() -> None:
    s = State(name="Lotte")
    s.artifacts.append("cafe")
    s.artifacts_built.append("cafe")
    payload = decode_code(s.to_code())
    assert payload["v"] == 2 and payload["artifactsBuilt"] == ["cafe"]

    back = State()
    back.merge_code(s.to_code())
    assert back.artifacts_built == ["cafe"] and back.artifacts == ["cafe"]

    # A code from before this release is still a valid version 2 code, and a
    # reader of it simply learns nothing about what was built.
    older = json.dumps(
        {"v": 2, "name": "Lotte", "doneW": {"campus": [1]}, "artifacts": ["well"]}
    )
    import base64

    code = base64.urlsafe_b64encode(older.encode()).decode().rstrip("=")
    old = State()
    old.merge_code(code)
    assert old.artifacts == ["well"] and old.artifacts_built == []
