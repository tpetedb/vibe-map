"""Exercise the publisher against real local Git remotes and a fake GitHub CLI."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PUBLISH = ROOT / "tools/publish_news.py"
FILES = ("data/news.json", "game/news.json", "vault/Camp/News.md", "game/vibe-map.html")
BRANCH = "automation/daily-news"


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=repo, text=True).strip()


@pytest.fixture
def checkout(tmp_path: Path, monkeypatch):
    remote = tmp_path / "remote.git"
    git(tmp_path, "init", "--bare", str(remote))
    repo = tmp_path / "checkout"
    git(tmp_path, "init", "-b", "main", str(repo))
    git(repo, "config", "user.name", "Test")
    git(repo, "config", "user.email", "test@example.invalid")
    for name in FILES:
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("original\n")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "initial")
    git(repo, "remote", "add", "origin", str(remote))
    git(repo, "push", "origin", "main")
    binary = tmp_path / "bin"
    binary.mkdir()
    gh = binary / "gh"
    gh.write_text(
        "#!/usr/bin/env python3\n"
        "import json, os, sys\n"
        "from pathlib import Path\n"
        "with Path(os.environ['GH_LOG']).open('a') as f:\n"
        "    f.write(json.dumps(sys.argv[1:]) + '\\n')\n"
        "if sys.argv[1:3] == ['pr', 'list']:\n"
        "    print(os.environ.get('GH_PENDING', '[]'))\n"
        "elif os.environ.get('GH_DENIED'):\n"
        "    print('GitHub Actions may not create pull requests', file=sys.stderr)\n"
        "    sys.exit(1)\n"
        "else:\n"
        "    print('https://github.com/example/repo/pull/1')\n"
    )
    gh.chmod(0o755)
    monkeypatch.setenv("PATH", f"{binary}:{os.environ['PATH']}")
    monkeypatch.setenv("GH_LOG", str(tmp_path / "gh.log"))
    monkeypatch.setenv("GITHUB_STEP_SUMMARY", str(tmp_path / "summary.md"))
    return repo, remote, tmp_path


def publish(repo: Path):
    return subprocess.run(
        [sys.executable, str(PUBLISH)], cwd=repo, capture_output=True, text=True
    )


def change(repo: Path):
    for name in FILES:
        (repo / name).write_text("updated\n")


def test_changes_go_to_pr_branch_only(checkout):
    repo, remote, tmp = checkout
    original = git(remote, "rev-parse", "main")
    change(repo)
    result = publish(repo)
    assert result.returncode == 0, result.stderr
    assert git(remote, "rev-parse", "main") == original
    assert git(remote, "show", f"{BRANCH}:data/news.json") == "updated"
    assert set(git(remote, "diff", "--name-only", "main", BRANCH).splitlines()) == set(
        FILES
    )
    calls = (tmp / "gh.log").read_text()
    assert '"create"' in calls and '"--base", "main"' in calls
    assert "Approve workflows to run" in (tmp / "summary.md").read_text()


def test_no_change_does_not_publish(checkout):
    repo, remote, tmp = checkout
    assert publish(repo).returncode == 0
    assert not (tmp / "gh.log").exists()
    assert git(remote, "branch", "--list", BRANCH) == ""


def test_pending_pr_is_not_duplicated_or_overwritten(checkout, monkeypatch):
    repo, remote, tmp = checkout
    change(repo)
    assert publish(repo).returncode == 0
    head = git(remote, "rev-parse", BRANCH)
    git(repo, "switch", "main")
    change(repo)
    monkeypatch.setenv("GH_PENDING", '[{"url":"https://example.test/pull/1"}]')
    result = publish(repo)
    assert result.returncode == 0
    assert git(remote, "rev-parse", BRANCH) == head
    assert (tmp / "gh.log").read_text().count('"create"') == 1


def test_denied_pr_preserves_branch_and_handoff(checkout, monkeypatch):
    repo, remote, tmp = checkout
    monkeypatch.setenv("GH_DENIED", "1")
    change(repo)
    result = publish(repo)
    assert result.returncode == 1
    assert git(remote, "show", f"{BRANCH}:data/news.json") == "updated"
    summary = (tmp / "summary.md").read_text()
    assert "gh pr create" in summary
    assert "Allow GitHub Actions to create and approve pull requests" in summary


def test_existing_branch_without_pr_is_never_overwritten(checkout):
    repo, remote, tmp = checkout
    git(repo, "push", "origin", f"HEAD:refs/heads/{BRANCH}")
    original = git(remote, "rev-parse", BRANCH)
    change(repo)
    result = publish(repo)
    assert result.returncode == 1
    assert git(remote, "rev-parse", BRANCH) == original
    assert '"create"' not in (tmp / "gh.log").read_text()
    assert "preserved" in (tmp / "summary.md").read_text()


def test_unrelated_staged_file_is_not_committed(checkout):
    repo, remote, _ = checkout
    (repo / "unrelated.txt").write_text("keep me")
    git(repo, "add", "unrelated.txt")
    change(repo)
    assert publish(repo).returncode == 1
    assert git(remote, "branch", "--list", BRANCH) == ""
    assert git(repo, "diff", "--cached", "--name-only") == "unrelated.txt"


def test_workflow_preserves_snapshot_before_publishing():
    import yaml

    flow = yaml.safe_load((ROOT / ".github/workflows/news.yml").read_text())
    assert flow["permissions"] == {"contents": "write", "pull-requests": "write"}
    assert flow["concurrency"]["cancel-in-progress"] is False
    steps = flow["jobs"]["pull"]["steps"]
    assert steps[0]["with"]["ref"] == "main"
    snapshot = next(
        s for s in steps if s.get("uses", "").startswith("actions/upload-artifact@")
    )
    publisher = next(s for s in steps if "tools/publish_news.py" in s.get("run", ""))
    assert steps.index(snapshot) < steps.index(publisher)
    assert set(snapshot["with"]["path"].splitlines()) == set(FILES)
    assert publisher["env"]["GH_TOKEN"] == "${{ github.token }}"
    assert all("git push" not in s.get("run", "") for s in steps)
