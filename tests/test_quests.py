"""A check reads what the learner built, not what the camp shipped.

Every test here runs the real command in a camp made the way a learner gets
one, so a check that passes on the scaffolding fails the test.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

from click.testing import CliRunner

from vibemap.cli import cli

ANSI = re.compile(r"\x1b\[[0-9;]*m")


def _flat(text: str) -> str:
    """The output as one line: a table cell wraps wherever the terminal ends."""
    return re.sub(r"\s+", " ", ANSI.sub("", text)).strip()


def _camp(tmp_path: Path) -> Path:
    camp = tmp_path / "camp"
    out = CliRunner().invoke(cli, ["new", str(camp), "--name", "T"])
    assert out.exit_code == 0, out.output
    return camp


def _vibe(camp: Path, *args: str, home: Path | None = None) -> str:
    env = dict(os.environ, VIBE_HOME=str(camp))
    if home is not None:
        env["HOME"] = str(home)
    out = subprocess.run(
        [sys.executable, "-m", "vibemap.cli", *args],
        cwd=camp,
        env=env,
        capture_output=True,
        text=True,
    )
    return out.stdout + out.stderr


def _write(p: Path, text: str) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def test_a_fresh_camp_passes_no_campus_stop(tmp_path: Path) -> None:
    """The template ships AGENTS.md, skills, a vault and a Pages workflow."""
    camp = _camp(tmp_path)
    for n in (2, 6, 7):
        out = _vibe(camp, "check", "--no-claim", str(n))
        assert "fail" in out, out
        assert "pass" not in out, out


def test_a_skill_and_an_agents_md_of_your_own_pass_stop_2(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    _write(
        camp / "AGENTS.md",
        "# My rules\n\n## Commands\n\n- just test runs the tests\n" + "- a rule\n" * 8,
    )
    _write(
        camp / ".claude" / "skills" / "mine" / "SKILL.md",
        "---\nname: mine\ndescription: my own skill\n---\n\nDo the thing.\n",
    )
    out = _vibe(camp, "check", "--no-claim", "2")
    assert "fail" not in out, out
    assert "1 skill(s) of your own: mine" in _flat(out), out


def test_an_mcp_server_in_the_default_scope_passes_stop_5(tmp_path: Path) -> None:
    """`claude mcp add` with no scope writes the local scope, not .mcp.json."""
    camp = _camp(tmp_path)
    home = tmp_path / "home"
    _write(
        home / ".claude.json",
        json.dumps(
            {"projects": {str(camp.resolve()): {"mcpServers": {"weather": {}}}}}
        ),
    )
    out = _vibe(camp, "check", "--no-claim", "5", home=home)
    assert "weather" in _flat(out), out
    assert "fail" not in out, out


def test_a_launchd_agent_counts_as_a_schedule(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    home = tmp_path / "home"
    _write(
        home / "Library" / "LaunchAgents" / "camp.scorekeeper.plist",
        "<plist><dict><key>ProgramArguments</key>"
        "<array><string>claude</string></array></dict></plist>",
    )
    out = _vibe(camp, "check", "--no-claim", "8", home=home)
    assert "launchd agent" in _flat(out), out


def test_a_workflow_that_runs_nothing_is_not_ci(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    wf = camp / ".github" / "workflows" / "aspirational.yml"
    _write(wf, "name: pytest and ruff, one day\non: push\njobs: {}\n")
    out = _vibe(camp, "check", "--no-claim", "-w", "desert", "6")
    assert "fail" in out, out
    _write(
        wf,
        "name: checks\non: push\njobs:\n  test:\n    runs-on: ubuntu-latest\n"
        "    steps:\n      - run: pytest -q\n",
    )
    out = _vibe(camp, "check", "--no-claim", "-w", "desert", "6")
    assert "job test runs pytest" in _flat(out), out


def test_a_list_of_bare_dot_names_is_not_an_explanation(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    p = camp / "workspace" / "desert" / "dotfiles.md"
    _write(p, ".zshrc .gitconfig .vimrc .ssh .config .claude\n")
    out = _vibe(camp, "check", "--no-claim", "-w", "desert", "2")
    assert "1 dot entries with a line explaining them" in _flat(out), out
    _write(
        p,
        "\n".join(
            f"- `{name}` holds the settings for {name[1:]} on this machine"
            for name in (
                ".zshrc",
                ".gitconfig",
                ".vimrc",
                ".ssh",
                ".config",
                ".claude",
            )
        )
        + "\n",
    )
    out = _vibe(camp, "check", "--no-claim", "-w", "desert", "2")
    assert "6 dot entries with a line explaining them" in _flat(out), out


def test_an_empty_script_is_not_a_job(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    _write(camp / "workspace" / "jobs" / "job.sh", "")
    _write(camp / "workspace" / "jobs" / "log.csv", "started,ended\n1,2\n3,4\n")
    out = _vibe(camp, "check", "--no-claim", "-w", "desert", "7")
    assert "none with a job in it" in _flat(out), out


def test_a_missing_folder_reads_as_a_missing_folder(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    out = _vibe(camp, "check", "--no-claim", "-w", "winter", "8")
    assert "workspace/winter/makemore/ does not exist" in _flat(out), out


def test_the_repair_check_reads_the_history_of_the_camp_around_the_fork(
    tmp_path: Path,
) -> None:
    """A `vibe fork` fork has no .git of its own; the camp is its repository."""
    camp = _camp(tmp_path)
    (camp / "workspace" / "forks" / "vibe-map").mkdir(parents=True)
    env = dict(os.environ, GIT_AUTHOR_NAME="T", GIT_AUTHOR_EMAIL="t@example.test")
    env.update(GIT_COMMITTER_NAME="T", GIT_COMMITTER_EMAIL="t@example.test")
    for args in (
        ["init", "-q"],
        ["add", "-A"],
        ["commit", "-qm", "break the build on purpose", "--allow-empty"],
        ["commit", "-qm", "fix the build, green again", "--allow-empty"],
    ):
        subprocess.run(["git", *args], cwd=camp, env=env, check=True)
    out = _vibe(camp, "check", "--no-claim", "--fork", "repair")
    assert "no git history" not in _flat(out), out
    assert "breaks the build and then repairs it" in _flat(out), out
