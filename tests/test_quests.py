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


# ---- the findings of hunt wave 2 ------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
A_TEST = "def test_one():\n    assert 1 + 1 == 2\n"


def _git(camp: Path, *args: str) -> None:
    env = dict(os.environ, GIT_AUTHOR_NAME="T", GIT_AUTHOR_EMAIL="t@example.test")
    env.update(GIT_COMMITTER_NAME="T", GIT_COMMITTER_EMAIL="t@example.test")
    subprocess.run(["git", *args], cwd=camp, env=env, check=True, capture_output=True)


def test_the_learners_tests_run_with_the_learners_own_pytest(tmp_path: Path) -> None:
    """Desert 3 runs the tests that are there, and says so when they fail."""
    camp = _camp(tmp_path)
    _write(camp / "workspace" / "python" / "test_scores.py", A_TEST)
    out = _flat(_vibe(camp, "check", "--no-claim", "-w", "desert", "3"))
    assert "1 passed" in out, out
    _write(
        camp / "workspace" / "python" / "test_scores.py",
        "def test_one():\n    assert False\n",
    )
    out = _flat(_vibe(camp, "check", "--no-claim", "-w", "desert", "3"))
    assert "1 failed" in out, out


def test_a_machine_without_pytest_is_told_which_command_installs_one(
    tmp_path: Path, monkeypatch
) -> None:
    """The documented install has no pytest; the stop says how to get one."""
    from vibemap import quests
    from vibemap.config import Config

    camp = _camp(tmp_path)
    _write(camp / "workspace" / "python" / "test_scores.py", A_TEST)
    monkeypatch.setattr(quests, "ROOT", camp)
    monkeypatch.setattr(quests, "_pytest_runner", lambda: None)
    ok, detail = quests._d3_tests(Config())
    assert ok, detail
    assert quests.PYTEST_INSTALL in detail, detail
    # A file with no test in it is still not a test.
    _write(camp / "workspace" / "python" / "test_scores.py", "x = 1\n")
    ok, detail = quests._d3_tests(Config())
    assert not ok
    assert "none with a test in it" in detail, detail


def test_both_test_checks_run_through_the_same_runner(
    tmp_path: Path, monkeypatch
) -> None:
    """One helper and one interpreter: the god gate and desert 3 agree."""
    from vibemap import quests
    from vibemap.config import Config

    camp = _camp(tmp_path)
    _write(camp / "workspace" / "python" / "test_scores.py", A_TEST)
    seen: list[list[Path]] = []
    monkeypatch.setattr(quests, "ROOT", camp)
    monkeypatch.setattr(
        quests, "_run_pytest", lambda paths: (seen.append(paths), (True, "ran"))[1]
    )
    quests._d3_tests(Config())
    quests._extra_tests(Config())
    assert len(seen) == 2 and seen[0] == seen[1], seen


def test_a_model_family_is_named_and_not_spelled_inside_ollama(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    p = camp / "workspace" / "winter" / "local-model.md"
    _write(p, "# Local\nI ran ollama.\n" + "It was quick.\n" * 8)
    out = _flat(_vibe(camp, "check", "--no-claim", "-w", "winter", "6"))
    assert "names none of" in out, out
    _write(
        p,
        "# Local\nI ran ollama run llama3.2 and asked it three things.\n"
        + "It was quick.\n" * 8,
    )
    out = _flat(_vibe(camp, "check", "--no-claim", "-w", "winter", "6"))
    assert "names none of" not in out, out


def test_a_mermaid_block_has_to_close_around_a_diagram(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    p = camp / "workspace" / "winter" / "transformer.md"
    _write(p, "# T\ntoken and attention\n```mermaid\n" + "x\n" * 8)
    out = _flat(_vibe(camp, "check", "--no-claim", "-w", "winter", "3"))
    assert "no ```mermaid block that closes" in out, out
    _write(
        p,
        "# T\ntoken and attention\n```mermaid\nflowchart LR\n"
        "  A[token] --> B[attention]\n```\n" + "Attention mixes the tokens.\n" * 6,
    )
    out = _flat(_vibe(camp, "check", "--no-claim", "-w", "winter", "3"))
    assert "no ```mermaid" not in out, out


def test_an_empty_runner_scores_no_eval_cases(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    _write(
        camp / "workspace" / "evals" / "cases.csv", "prompt,expected\n" + "q,yes\n" * 6
    )
    _write(camp / "workspace" / "evals" / "run.py", "")
    out = _flat(_vibe(camp, "check", "--no-claim", "-w", "desert", "8"))
    assert "run.py is empty" in out, out


def test_a_hook_that_only_echoes_is_not_a_gate(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    settings = camp / ".claude" / "settings.json"
    data = json.loads(settings.read_text(encoding="utf-8"))
    data["hooks"] = {
        "Stop": [{"hooks": [{"type": "command", "command": "echo goodbye"}]}]
    }
    _write(settings, json.dumps(data, indent=2))
    out = _flat(_vibe(camp, "check", "--no-claim", "-w", "desert", "4"))
    assert "none of them runs" in out, out
    data["hooks"]["Stop"][0]["hooks"][0]["command"] = "pytest -q"
    _write(settings, json.dumps(data, indent=2))
    out = _flat(_vibe(camp, "check", "--no-claim", "-w", "desert", "4"))
    assert "gates: Stop" in out, out


def test_a_spec_is_told_which_half_it_is_missing(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    p = camp / "workspace" / "specs" / "nickname.md"
    _write(p, "# Nicknames\n" + "\n".join(f"## S{i}\nline\n" for i in range(4)))
    out = _flat(_vibe(camp, "check", "--no-claim", "-w", "desert", "5"))
    assert "nickname.md needs 12 lines" in out, out
    _write(p, "# Nicknames\n" + "a line\n" * 14)
    out = _flat(_vibe(camp, "check", "--no-claim", "-w", "desert", "5"))
    assert "nickname.md needs ## sections" in out, out


def test_a_commit_message_is_not_a_rewrite_of_history(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    _git(camp, "init", "-q")
    _git(camp, "add", "-A")
    _git(camp, "commit", "-qm", "reset the headline of the readme", "--allow-empty")
    out = _flat(_vibe(camp, "check", "--no-claim", "-w", "prod", "4"))
    assert "no rebase, revert, cherry-pick or reset" in out, out
    _git(camp, "reset", "--soft", "HEAD")
    out = _flat(_vibe(camp, "check", "--no-claim", "-w", "prod", "4"))
    assert "the reflog remembers: reset" in out, out


def test_a_branch_nobody_pushed_is_not_on_github(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    _git(camp, "init", "-q")
    _git(camp, "add", "-A")
    _git(camp, "commit", "-qm", "the camp", "--allow-empty")
    _git(camp, "remote", "add", "origin", "https://github.com/learner/nope.git")
    _git(camp, "branch", "feature/nickname")
    out = _flat(_vibe(camp, "check", "--no-claim", "-w", "prod", "3"))
    assert "none on the remote" in out, out
    _git(camp, "update-ref", "refs/remotes/origin/main", "HEAD")
    out = _flat(_vibe(camp, "check", "--no-claim", "-w", "prod", "3"))
    assert "pushed: origin/main" in out, out


def test_the_dotfiles_repository_leaves_git_add_working(tmp_path: Path) -> None:
    """A repository inside the camp with no commit stops `git add -A` dead."""
    camp = _camp(tmp_path)
    _git(camp, "init", "-q")
    dots = camp / "workspace" / "dotfiles"
    _write(dots / "README.md", "# mine\n")
    _write(dots / "install.sh", "#!/usr/bin/env bash\nln -sf a b\n")
    _git(dots, "init", "-q")
    out = _flat(_vibe(camp, "check", "--no-claim", "-w", "prod", "8"))
    assert "has no commit yet" in out, out
    _git(dots, "add", "-A")
    _git(dots, "commit", "-qm", "mine")
    out = _flat(_vibe(camp, "check", "--no-claim", "-w", "prod", "8"))
    assert "does not ignore workspace/dotfiles" in out, out
    ignore = camp / ".gitignore"
    _write(ignore, ignore.read_text(encoding="utf-8") + "workspace/dotfiles/\n")
    out = _flat(_vibe(camp, "check", "--no-claim", "-w", "prod", "8"))
    assert "a git repo with install.sh and a README" in out, out
    # The camp can still stage everything, which its own AGENTS.md asks for.
    _git(camp, "add", "-A")


def test_a_fork_manifest_of_another_version_is_refused_not_crashed(
    tmp_path: Path,
) -> None:
    camp = _camp(tmp_path)
    fork = camp / "workspace" / "forks" / "vibe-map"
    (fork / "src" / "config").mkdir(parents=True)
    _write(fork / "fork.json", json.dumps({"version": 2}))
    out = _flat(_vibe(camp, "check", "--no-claim", "--fork", "exists"))
    assert "check crashed" not in out, out
    assert "fork.json version 2 is not 1" in out, out
    _write(fork / "fork.json", "{not json")
    out = _flat(_vibe(camp, "check", "--no-claim", "--fork", "exists"))
    assert "check crashed" not in out, out
    assert "fork.json is not valid JSON" in out, out


def test_a_scaffolded_exercise_is_never_part_of_a_pass(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    assert "labels.csv" in _vibe(camp, "mentor", "li", "--start")
    rows = "\n".join(f"thing{i},keep" for i in range(10))
    labels = camp / "workspace" / "mentors" / "li" / "labels.csv"
    labels.write_text(
        labels.read_text(encoding="utf-8") + f"item,label\n{rows}\n", encoding="utf-8"
    )
    out = _flat(_vibe(camp, "check", "--no-claim", "--mentor", "li"))
    assert "still holds the stub" in out, out
    labels.write_text(f"item,label\n{rows}\n", encoding="utf-8")
    out = _flat(_vibe(camp, "check", "--no-claim", "--mentor", "li"))
    assert "still holds the stub" not in out, out
    assert "holds what the exercise asks for" in out, out


def test_the_game_check_names_the_floor_it_measures(tmp_path: Path) -> None:
    from vibemap.quests import GAME_BYTES

    camp = _camp(tmp_path)
    _write(camp / "workspace" / "game" / "index.html", "<canvas></canvas>" * 20)
    out = _flat(_vibe(camp, "check", "--no-claim", "1"))
    assert "exists fail" not in out, out
    assert f"(needs {GAME_BYTES})" in out, out
    assert str(GAME_BYTES) in out, out


def test_the_collector_badge_reads_the_same_in_the_cli_and_the_game() -> None:
    from vibemap.quests import BADGES

    text = (ROOT / "src" / "game" / "18-avatar.js").read_text(encoding="utf-8")
    m = re.search(r'id:"collector".*?what:"([^"]+)"', text)
    assert m, "no collector achievement in the game"
    assert BADGES["collector"].lower().endswith(m.group(1).rstrip(".").lower())
