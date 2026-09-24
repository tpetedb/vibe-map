"""Publish generated news to a review branch without changing protected main."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

BRANCH = "automation/daily-news"
FILES = ("data/news.json", "game/news.json", "vault/Camp/News.md", "game/vibe-map.html")
TITLE = "News: daily pull of the world feed"
HANDOFF = (
    f"The branch `{BRANCH}` is preserved. Inspect its changes and open a PR with "
    f"`gh pr create --base main --head {BRANCH} --title '{TITLE}' --body "
    "'Generated daily news; review and run required checks before merging.'`. "
    "If Actions cannot create PRs, a repository administrator can enable "
    "Settings > Actions > General > Workflow permissions > "
    "Allow GitHub Actions to create and approve pull requests, or a maintainer "
    "can open this PR manually. No additional secret is needed. "
    "For a bot-created PR, select **Approve workflows to run** in the PR "
    "merge box, then review and wait for required checks. After merging, "
    "delete the branch only after confirming all its work was integrated. "
    "An existing branch is never replaced, including a branch left after a merge."
)


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True).strip()


def report(message: str) -> None:
    print(message)
    if summary := os.environ.get("GITHUB_STEP_SUMMARY"):
        with Path(summary).open("a") as stream:
            stream.write(message + "\n\n")


def main() -> int:
    try:
        staged = set(run("git", "diff", "--cached", "--name-only").splitlines())
        if staged - set(FILES):
            report("Refusing to publish: unrelated files are staged.")
            return 1
        if not run("git", "status", "--porcelain", "--", *FILES):
            report("No news changes to publish.")
            return 0
        pending = json.loads(
            run(
                "gh",
                "pr",
                "list",
                "--state",
                "open",
                "--base",
                "main",
                "--head",
                BRANCH,
                "--json",
                "url",
            )
        )
        if pending:
            report(
                f"News update already awaits review: {pending[0]['url']}. " + HANDOFF
            )
            return 0
        if run("git", "ls-remote", "--heads", "origin", f"refs/heads/{BRANCH}"):
            report("News branch exists without an open PR. " + HANDOFF)
            return 1
        run("git", "switch", "-c", BRANCH)
        run("git", "add", "--", *FILES)
        run(
            "git",
            "-c",
            "user.name=vibe news",
            "-c",
            "user.email=actions@users.noreply.github.com",
            "commit",
            "-m",
            TITLE,
        )
        run("git", "push", "origin", f"HEAD:refs/heads/{BRANCH}")
        # The branch is durable before GitHub's optional PR permission is used.
        report(HANDOFF)
        with tempfile.TemporaryDirectory() as directory:
            body = Path(directory) / "body.md"
            body.write_text(
                "Refresh the generated news and embedded game.\n\n" + HANDOFF
            )
            url = run(
                "gh",
                "pr",
                "create",
                "--base",
                "main",
                "--head",
                BRANCH,
                "--title",
                TITLE,
                "--body-file",
                str(body),
            )
        report(f"News pull request: {url}")
        return 0
    except (subprocess.CalledProcessError, OSError, ValueError) as error:
        report(
            f"News publication needs attention: {error}. "
            "Generated files are retained in this run's news-snapshot artifact. "
            "Check whether the remote news branch exists before retrying."
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
