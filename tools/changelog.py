"""Changelog fragments: one small file per change, assembled on demand.

Two branches that both edit CHANGELOG.md conflict on the same three lines every
time, and the conflict is never interesting: both sides want to be kept. So a
branch writes a fragment instead, `changelog.d/<slug>.<type>.md`, and nothing
touches CHANGELOG.md until a release assembles them. Keep a Changelog 1.1.0 is
still the published form: https://keepachangelog.com/en/1.1.0/

    uv run python tools/changelog.py draft
    uv run python tools/changelog.py release 1.0.0 [--date 2026-09-18]
    uv run python tools/changelog.py check --base origin/main

`check` is what CI runs on a pull request: a diff that changes the product
without a fragment is a diff whose reader will never learn what changed.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRAGMENTS = ROOT / "changelog.d"
CHANGELOG = ROOT / "CHANGELOG.md"

# The six headings of Keep a Changelog 1.1.0, in the order the file prints them.
TYPES = ("added", "changed", "deprecated", "removed", "fixed", "security")
NAME = re.compile(r"^(?P<slug>[a-z0-9][a-z0-9-]*)\.(?P<type>[a-z]+)\.md$")
UNRELEASED = "## [Unreleased]"
# What the empty Unreleased section says instead of holding entries.
POINTER = (
    "Nothing here between releases: an entry lives in its own file under\n"
    "[`changelog.d/`](changelog.d/) until a release assembles them.\n"
)
VERSION = re.compile(r"^\d+\.\d+\.\d+$")
# A change under one of these needs an entry; the rest of the repository
# (tests, docs, workflows, the vault) does not.
WATCHED = ("src/", "vibemap/", "tools/")
# Generated mirrors: their content is a copy of something else that already
# carries the entry, so regenerating them is never a change of its own.
EXEMPT = (
    "tools/generated/",
    "vibemap/data/fork_source/",
    "vibemap/data/template/",
)


@dataclass(frozen=True, slots=True)
class Fragment:
    """One file under changelog.d: a slug, one of the six types, its bullets."""

    slug: str
    type: str
    body: str

    @property
    def path(self) -> Path:
        return FRAGMENTS / f"{self.slug}.{self.type}.md"


def read_fragments(folder: Path = FRAGMENTS) -> list[Fragment]:
    """Every fragment, sorted by type then slug. A misnamed file fails loudly."""
    out: list[Fragment] = []
    if not folder.is_dir():
        return out
    for path in sorted(folder.iterdir()):
        if not path.is_file() or path.name in {"README.md", ".gitkeep"}:
            continue
        m = NAME.match(path.name)
        if not m:
            raise SystemExit(
                f"{path.name}: a fragment is named <slug>.<type>.md, "
                f"type one of {', '.join(TYPES)}"
            )
        if m["type"] not in TYPES:
            raise SystemExit(
                f"{path.name}: {m['type']} is not a change type; "
                f"use one of {', '.join(TYPES)}"
            )
        body = path.read_text().strip("\n")
        if not body:
            raise SystemExit(f"{path.name}: empty; write the entry or delete the file")
        if not body.lstrip().startswith("-"):
            raise SystemExit(f"{path.name}: an entry is a bullet list, starting with -")
        out.append(Fragment(m["slug"], m["type"], body))
    return sorted(out, key=lambda f: (TYPES.index(f.type), f.slug))


def render(fragments: list[Fragment]) -> str:
    """The body of a section: the six headings, in order, without the empty ones."""
    parts: list[str] = []
    for kind in TYPES:
        bodies = [f.body for f in fragments if f.type == kind]
        if not bodies:
            continue
        parts.append(f"### {kind.title()}\n\n" + "\n\n".join(bodies) + "\n")
    return "\n".join(parts)


def _split(text: str) -> tuple[str, str, str]:
    """The file around its Unreleased section: head, the section, the rest."""
    start = text.find(UNRELEASED)
    if start < 0:
        raise SystemExit(f"{CHANGELOG.name}: no {UNRELEASED} heading")
    after = text.find("\n## ", start + 1)
    if after < 0:
        raise SystemExit(f"{CHANGELOG.name}: no released section under {UNRELEASED}")
    return text[:start], text[start:after], text[after + 1 :]


def draft(fragments: list[Fragment]) -> str:
    """What the Unreleased section would say today."""
    body = render(fragments)
    return f"{UNRELEASED}\n\n" + (body if body else POINTER)


def _links(text: str, version: str) -> str:
    """Point Unreleased at the new tag and give the new version its own compare."""
    m = re.search(
        r"^\[Unreleased\]: (?P<base>\S+)/compare/(?P<prev>v[^.]\S*)\.\.\.HEAD$",
        text,
        re.M,
    )
    if not m:
        raise SystemExit(f"{CHANGELOG.name}: no [Unreleased] compare link to update")
    base, prev = m["base"], m["prev"]
    new = (
        f"[Unreleased]: {base}/compare/v{version}...HEAD\n"
        f"[{version}]: {base}/compare/{prev}...v{version}"
    )
    return text[: m.start()] + new + text[m.end() :]


def release(version: str, date: str, fragments: list[Fragment]) -> str:
    """CHANGELOG.md with the fragments cut into a dated section under the top."""
    if not VERSION.match(version):
        raise SystemExit(f"{version}: a version is MAJOR.MINOR.PATCH, digits only")
    if not fragments:
        raise SystemExit("changelog.d is empty: nothing to release")
    text = CHANGELOG.read_text()
    if f"## [{version}]" in text:
        raise SystemExit(f"{CHANGELOG.name} already has a section for {version}")
    head, _, rest = _split(text)
    section = f"## [{version}] - {date}\n\n{render(fragments)}"
    return _links(f"{head}{UNRELEASED}\n\n{POINTER}\n{section}\n{rest}", version)


def _diff(base: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "diff", "--name-only", f"{base}...HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def changed_files(base: str) -> list[str] | None:
    """The paths this branch changes against base, or None when git cannot say.

    A shallow clone (what CI checks out) can be missing the merge base, so
    deepen once before giving up. Giving up means this check stays quiet: a
    history it cannot read is not evidence that an entry is missing.
    """
    out = _diff(base)
    if out.returncode != 0:
        subprocess.run(
            ["git", "fetch", "--deepen=200"], cwd=ROOT, capture_output=True, text=True
        )
        out = _diff(base)
    if out.returncode != 0:
        return None
    return [line for line in out.stdout.splitlines() if line]


def needs_fragment(paths: list[str]) -> list[str]:
    """The changed product files that make an entry mandatory."""
    return [
        p
        for p in paths
        if p.startswith(WATCHED) and not p.startswith(EXEMPT) and "/tests/" not in p
    ]


def check(paths: list[str]) -> tuple[int, str]:
    """Exit code and message for a diff: 0 when the entry is where it belongs."""
    product = needs_fragment(paths)
    fragments = [p for p in paths if p.startswith("changelog.d/") and "README" not in p]
    if "CHANGELOG.md" in paths and not fragments:
        return 1, (
            "CHANGELOG.md is written by a release, not by a branch. "
            "Move the entry to changelog.d/<slug>.<type>.md."
        )
    if product and not fragments:
        shown = ", ".join(product[:5]) + ("..." if len(product) > 5 else "")
        return 1, (
            f"no changelog fragment for a change under {shown}. "
            f"Add changelog.d/<slug>.<type>.md, type one of {', '.join(TYPES)}."
        )
    if not product:
        return 0, "no product change: no fragment needed"
    return 0, f"{len(fragments)} fragment(s) for {len(product)} changed product file(s)"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("draft", help="print the Unreleased view of the fragments")
    rel = sub.add_parser("release", help="cut the fragments into a dated section")
    rel.add_argument("version", help="MAJOR.MINOR.PATCH, without the v")
    rel.add_argument("--date", default=dt.date.today().isoformat(), help="ISO 8601")
    rel.add_argument("--dry-run", action="store_true", help="print, write nothing")
    chk = sub.add_parser("check", help="a product diff carries a fragment")
    chk.add_argument("--base", default="origin/main", help="what to diff against")
    args = parser.parse_args(argv)

    if args.cmd == "draft":
        print(draft(read_fragments()))
        return 0
    if args.cmd == "release":
        fragments = read_fragments()
        text = release(args.version, args.date, fragments)
        if args.dry_run:
            print(text)
            return 0
        CHANGELOG.write_text(text)
        for fragment in fragments:
            fragment.path.unlink()
        print(f"{CHANGELOG.name}: {args.version} written, {len(fragments)} cut")
        return 0
    paths = changed_files(args.base)
    if paths is None:
        print(f"no merge base with {args.base} in this clone: nothing checked")
        return 0
    code, message = check(paths)
    print(message)
    return code


if __name__ == "__main__":
    sys.exit(main())
