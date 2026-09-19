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


def test_the_module_kind_runs_the_script_or_names_what_to_install(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A topic may lean on a library nobody here depends on; both ways answer."""
    from vibemap.artifact_checks import run_spec

    (tmp_path / "count.py").write_text("print('rows: 3')\n", encoding="utf-8")
    spec = {
        "kind": "module",
        "file": "count.py",
        "modules": ["json"],
        "prints": ["rows: 3"],
    }
    assert run_spec(tmp_path, spec) == (True, "count.py printed all 1 expected lines")

    absent = dict(spec, modules=["nothing_like_this"], install="uv add nothing")
    ok, detail = run_spec(tmp_path, absent)
    assert ok and "nothing_like_this is not installed" in detail
    assert "uv add nothing" in detail

    (tmp_path / "count.py").write_text("print('rows: 0')\n", encoding="utf-8")
    ok, detail = run_spec(tmp_path, spec)
    assert not ok and "rows: 3" in detail


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


def test_the_justfile_check_reads_it_with_just_or_by_line(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Both layers read the same file and must agree on what is in it."""
    here = _build(tmp_path, "switchboard", monkeypatch)
    detail = run_quest(artifact_quest("switchboard", GOD), GOD)[0].detail
    assert "3 documented recipes" in detail

    # A machine without just still gets a verdict, with the install command.
    monkeypatch.setattr("vibemap.artifact_checks._tool", lambda name: False)
    detail = run_quest(artifact_quest("switchboard", GOD), GOD)[0].detail
    assert "3 documented recipes" in detail and "brew install just" in detail

    # A recipe with no comment above it is the one thing --list cannot show.
    (here / "justfile").write_text(
        "# greet someone\ngreet name='camp':\n    @echo {{name}}\n\n"
        "count:\n    @ls | wc -l\n\n# both\nround: greet\n    @just count\n",
        encoding="utf-8",
    )
    detail = run_quest(artifact_quest("switchboard", GOD), GOD)[0].detail
    assert "no comment above: count" in detail


def test_the_justfile_check_wants_a_parameter_and_a_dependency(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    here = _build(tmp_path, "switchboard", monkeypatch)
    monkeypatch.setattr("vibemap.artifact_checks._tool", lambda name: False)
    (here / "justfile").write_text(
        "# one\na:\n    @echo a\n\n# two\nb:\n    @echo b\n\n"
        "# three\nc:\n    @echo c\n",
        encoding="utf-8",
    )
    detail = run_quest(artifact_quest("switchboard", GOD), GOD)[0].detail
    assert "no recipe takes a parameter" in detail

    (here / "justfile").write_text(
        "# one\na name='x':\n    @echo {{name}}\n\n# two\nb:\n    @echo b\n\n"
        "# three\nc:\n    @echo c\n",
        encoding="utf-8",
    )
    detail = run_quest(artifact_quest("switchboard", GOD), GOD)[0].detail
    assert "no recipe depends on another" in detail


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
    assert out.returncode == 1, out.stdout + out.stderr
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


# ---- the terminal route to the walkthrough -------------------------------------


def test_vibe_artifact_lists_the_twenty_and_refuses_an_unknown_id(
    tmp_path: Path,
) -> None:
    from click.testing import CliRunner

    from vibemap.cli import cli

    camp = tmp_path / "camp"
    assert CliRunner().invoke(cli, ["new", str(camp), "--name", "Tom"]).exit_code == 0
    out = _run(camp, "artifact")
    assert out.returncode == 0, out.stdout + out.stderr
    for a in campaign.artifacts():
        assert a["id"] in out.stdout
    assert "not yet" in out.stdout
    unknown = _run(camp, "artifact", "nowhere")
    assert unknown.returncode == 1 and "unknown artifact" in unknown.stdout


def test_vibe_artifact_prints_the_walkthrough_the_game_shows(tmp_path: Path) -> None:
    from click.testing import CliRunner

    from vibemap.cli import cli

    camp = tmp_path / "camp"
    assert CliRunner().invoke(cli, ["new", str(camp), "--name", "Tom"]).exit_code == 0
    out = _run(camp, "artifact", "cafe")
    assert out.returncode == 0, out.stdout + out.stderr
    real = get_artifact("cafe")["real"]
    assert real["title"] in out.stdout and real["doc"]["url"] in out.stdout
    assert real["done"] in out.stdout
    assert "vibe check --artifact cafe" in out.stdout
    for step in real["steps"]:
        # The table wraps, so the first words of every step are the evidence.
        assert " ".join(step.split()[:4]) in " ".join(out.stdout.split())


def test_vibe_artifact_start_scaffolds_honest_stubs(tmp_path: Path) -> None:
    from click.testing import CliRunner

    from vibemap.cli import cli

    camp = tmp_path / "camp"
    assert CliRunner().invoke(cli, ["new", str(camp), "--name", "Tom"]).exit_code == 0
    out = _run(camp, "artifact", "cafe", "--start")
    assert out.returncode == 0, out.stdout + out.stderr
    here = camp / "workspace" / "artifacts" / "cafe"
    assert (here / "cafe.py").exists() and (here / "notes.md").exists()
    assert "TODO" in (here / "cafe.py").read_text(encoding="utf-8")
    # A stub is a starting point, never a pass.
    assert _run(camp, "check", "--artifact", "cafe").returncode == 1
    # The learner's own work is never overwritten.
    (here / "cafe.py").write_text("mine\n", encoding="utf-8")
    again = _run(camp, "artifact", "cafe", "--start")
    assert "kept your" in again.stdout
    assert (here / "cafe.py").read_text(encoding="utf-8") == "mine\n"


def test_every_scaffolded_artifact_starts_red(tmp_path: Path, monkeypatch) -> None:
    from vibemap import artifact_checks
    from vibemap.cli import _scaffold_artifact
    from vibemap.quests import run_quest

    monkeypatch.setattr(artifact_checks, "ARTIFACTS_DIR", tmp_path)
    cfg = Config.model_validate({"learner": {"difficulty": "god"}})
    for aid in artifact_ids():
        _scaffold_artifact(get_artifact(aid))
        results = run_quest(artifact_quest(aid, cfg), cfg)
        assert not all(r.ok for r in results), aid


# ---- the findings of hunt wave 1 ------------------------------------------------


def test_a_failing_script_says_when_only_the_spacing_differs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`print("a -> ", x)` prints two spaces, and the message looked identical."""
    here = _build(tmp_path, "lighthouse", monkeypatch)
    spec = get_artifact("lighthouse")["real"]["check"]
    lines = "".join(f'print("{line} ")\n' for line in spec["prints"])
    (here / spec["file"]).write_text(lines, encoding="utf-8")
    ok, detail = KINDS[spec["kind"]](here, spec)
    assert ok, detail
    (here / spec["file"]).write_text(
        'print("localhost -> ", "127.0.0.1")\nprint("AF_INET")\n', encoding="utf-8"
    )
    ok, detail = KINDS[spec["kind"]](here, spec)
    assert not ok
    assert "not the spacing" in detail, detail


def test_a_lowercase_keyword_is_the_same_keyword(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The camp's own SQL skill writes lowercase; the check asked for capitals."""
    from vibemap.artifact_checks import _absent

    assert _absent("create index i on t(c);", ["CREATE INDEX"]) == []
    assert _absent("nothing here", ["CREATE INDEX"]) == ["CREATE INDEX"]
    # A name is not a keyword, so its case still counts.
    assert _absent("import Polars", ["polars"]) == ["polars"]


def test_a_syntax_directive_is_read_from_the_raw_text(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    here = _build(tmp_path, "dock", monkeypatch)
    spec = get_artifact("dock")["real"]["check"]
    (here / spec["file"]).write_text(
        '# syntax=docker/dockerfile:1\nFROM python:3.12-slim\nCMD ["python"]\n',
        encoding="utf-8",
    )
    ok, detail = KINDS[spec["kind"]](here, spec)
    assert ok, detail
    if "docker is not installed" in detail:
        assert "after a syntax directive" in detail, detail


def test_a_private_recipe_is_private_with_or_without_just(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from vibemap.artifact_checks import _just_dump, _just_parse

    text = (
        "# build it\nbuild:\n    @echo one\n\n"
        "# test it\ntest:\n    @echo two\n\n"
        "# helper\n[private]\nhelp:\n    @echo three\n"
    )
    here = _build(tmp_path, "switchboard", monkeypatch)
    (here / "justfile").write_text(text, encoding="utf-8")
    by_line = _just_parse(text)
    assert [r["name"] for r in by_line if not r["private"]] == ["build", "test"]
    by_just = _just_dump(here, "justfile")
    if by_just is not None:
        assert sorted(r["name"] for r in by_just if not r["private"]) == [
            "build",
            "test",
        ]


def test_the_walkthrough_states_the_note_at_the_difficulty_that_asks_for_it() -> None:
    from vibemap.artifact_checks import note_requirement

    a = get_artifact("cafe")
    easy = Config.model_validate({"learner": {"difficulty": "easy"}})
    assert note_requirement(a, easy) is None
    said = note_requirement(a, GOD)
    assert said and "notes.md" in said and ARTIFACT_SECTION in said
