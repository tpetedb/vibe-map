"""Catch up with main in one command: merge, regenerate, gate.

Most conflicts on this repository are not disagreements. They are two branches
that both ran a generator, so the built game, the tree notes or the camp
template differ in every line. The content of those files is a function of
their sources, so either side will do: take one, run the generators in
dependency order, and the result is what both branches meant. What is left
after that is a real disagreement, and a person resolves it.

    uv run python tools/sync_main.py           # just sync-main
    uv run python tools/sync_main.py --push

Exit codes: 0 merged and green, 1 a gate failed, 2 a real source conflict is
waiting for you (the merge is left in progress, `git merge --abort` undoes it).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Outputs, never hand-edited: a conflict here is resolved by regenerating.
# AGENTS.md lists the same set, and docs/MAINTAINERS.md says which tool owns
# which output.
GENERATED = (
    "game/vibe-map.html",
    "game/news.json",
    "tools/generated/",
    "docs/ROADMAP.md",
    "docs/RESOURCES.md",
    "docs/OBSIDIAN.md",
    "docs/COOKBOOK.md",
    "docs/site/syllabus.html",
    "vibemap/data/fork_source/",
    "vibemap/data/template/_agents/",
    "vibemap/data/template/_claude/",
    "vault/",
)

# Dependency order: the tree feeds the notes and the roadmap, the build reads
# both, the fork mirror copies what the build read, the vault reads the rest.
REGENERATE = (
    ("python", "tools/regen_tree.py"),
    ("python", "tools/gen_cookbook.py"),
    ("python", "tools/gen_syllabus.py"),
    ("python", "tools/sync_template.py"),
    ("python", "tools/build.py"),
    ("python", "tools/sync_fork_source.py"),
    ("python", "tools/sync_pets.py", "--check"),
    ("vibe", "vault", "build"),
)

# The fast gates: everything CI's lint job runs that needs no browser.
GATES = (
    ("ruff", "check", "."),
    ("ruff", "format", "--check", "."),
    ("python", "tools/checks.py", "style"),
    ("python", "tools/regen_tree.py", "--check"),
    ("python", "tools/gen_cookbook.py", "--check"),
    ("python", "tools/gen_syllabus.py", "--check"),
    ("python", "tools/sync_template.py", "--check"),
    ("python", "tools/build.py", "--check"),
    ("python", "tools/sync_fork_source.py", "--check"),
    ("vibe", "vault", "lint"),
)


def classify(paths: list[str]) -> tuple[list[str], list[str]]:
    """Split conflicted paths into the generated ones and the real ones."""
    generated = [p for p in paths if p.startswith(GENERATED)]
    return generated, [p for p in paths if p not in generated]


def run(args: tuple[str, ...] | list[str], **kw: object) -> subprocess.CompletedProcess:
    return subprocess.run(list(args), cwd=ROOT, text=True, **kw)  # type: ignore[arg-type]


def uv(args: tuple[str, ...]) -> int:
    """Run one repository command through uv and echo what it is doing."""
    print(f"  {' '.join(args)}")
    return run(("uv", "run", *args), capture_output=True).returncode


def conflicts() -> list[str]:
    out = run(
        ("git", "diff", "--name-only", "--diff-filter=U"), capture_output=True
    ).stdout
    return [line for line in out.splitlines() if line]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", default="origin/main", help="what to merge")
    parser.add_argument("--push", action="store_true", help="push when green")
    parser.add_argument("--no-fetch", action="store_true", help="skip git fetch")
    args = parser.parse_args(argv)

    remote, _, branch = args.ref.partition("/")
    if not args.no_fetch:
        run(("git", "fetch", remote, branch or "main"))
    if run(("git", "merge", "--no-edit", args.ref)).returncode != 0:
        generated, real = classify(conflicts())
        if real:
            print("Real source conflicts, resolve these by hand and commit:")
            for path in real:
                print(f"  {path}")
            return 2
        if generated:
            print(f"{len(generated)} generated file(s) conflicted; regenerating")
            # Either side is as good as the other: the generators overwrite both.
            run(("git", "checkout", "--ours", "--", *generated))
            run(("git", "add", "--", *generated))
        else:
            # Nothing is conflicted, so the merge was already in progress: this
            # is the second run, after a real conflict was resolved by hand.
            print("nothing conflicted; finishing the merge that was in progress")

    print("regenerating")
    for cmd in REGENERATE:
        if uv(cmd) != 0:
            print(f"FAILED: {' '.join(cmd)}")
            return 1
    left = conflicts()
    if left:
        print("still conflicted after regenerating: " + ", ".join(left))
        return 2
    run(("git", "add", "-A"))
    if run(("git", "diff", "--cached", "--quiet")).returncode != 0:
        merging = (
            run(
                ("git", "rev-parse", "-q", "--verify", "MERGE_HEAD"),
                capture_output=True,
            ).returncode
            == 0
        )
        message = ("--no-edit",) if merging else ("-m", f"Regenerate after {args.ref}")
        run(("git", "commit", *message))

    print("gates")
    failed = [cmd for cmd in GATES if uv(cmd) != 0]
    if failed:
        print("FAILED: " + ", ".join(" ".join(cmd) for cmd in failed))
        return 1
    if args.push:
        run(("git", "push"))
    print("sync-main OK: merged, regenerated, gates green")
    return 0


if __name__ == "__main__":
    sys.exit(main())
