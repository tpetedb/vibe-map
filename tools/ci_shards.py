"""The browser battery's shards: who owns which files, and the receipt check.

The split is written down once, in the `browser-shard` matrix of
`.github/workflows/ci.yml`, and read back from there by the test that guards
it, by the shard jobs themselves and by the aggregator.

A shard claims files by pattern (`tests/test_game_qol*.py`), and one shard is
the default: a browser test file no pattern claims runs there. So a new browser
test file is run by CI the moment it exists, without an edit to the workflow,
and the guard still refuses a file that is in two shards or a pattern that
claims nothing.

The aggregator asks two questions, because a required check that can report
success while a shard did not run is worse than no check at all: the aggregate
result GitHub gives for the matrix job, and a receipt from every shard the
matrix defines.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from collections.abc import Collection
from dataclasses import dataclass
from fnmatch import fnmatchcase
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CI = ROOT / ".github" / "workflows" / "ci.yml"


class Unreadable(Exception):
    """The split cannot be known: a matrix that does not say what it has to, or
    a battery pytest cannot collect. Always a sentence a human can act on."""


def matches(file: str, pattern: str) -> bool:
    """Whether a shard's pattern claims a file. Case counts, as it does on the
    Linux runners the shards run on."""
    return fnmatchcase(file, pattern)


@dataclass(frozen=True, slots=True)
class Shard:
    """One leg of the browser matrix: a name, the patterns it claims, and
    whether it takes the files no other pattern claims."""

    name: str
    patterns: tuple[str, ...]
    default: bool = False

    def claims(self, file: str) -> bool:
        return any(matches(file, p) for p in self.patterns)


def shards(workflow: Path = CI) -> tuple[Shard, ...]:
    flow = yaml.safe_load(workflow.read_text(encoding="utf-8"))
    include = flow["jobs"]["browser-shard"]["strategy"]["matrix"]["include"]
    for e in include:
        # A quoted "false" is a string, and every non-empty string is true.
        if not isinstance(e.get("default", False), bool):
            raise Unreadable(
                f"{workflow.name}: shard {e['shard']}: default is true or false, "
                f"not {e['default']!r}"
            )
    return tuple(
        Shard(e["shard"], tuple(str(e["files"]).split()), e.get("default", False))
        for e in include
    )


def browser_test_files(root: Path = ROOT) -> set[str]:
    """The files pytest itself puts in the browser battery, asked of pytest. A
    file that cannot be collected would drop out of every shard in silence, so
    a collection that fails is refused (5 is pytest's "nothing collected")."""
    ran = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-m",
            "browser and not integration",
            "--collect-only",
            "--no-header",
        ],
        cwd=root,
        capture_output=True,
        text=True,
    )
    out = ran.stdout
    if ran.returncode not in (0, 5):
        tail = "\n".join((out + ran.stderr).strip().splitlines()[-15:])
        raise Unreadable(
            f"pytest could not collect the browser battery (exit {ran.returncode}), "
            f"so no shard can say which files it runs:\n{tail}"
        )
    # The quiet collect prints one "tests/test_x.py: 4" line per file.
    return set(re.findall(r"^(tests/\S+\.py)(?=[:\s])", out, re.MULTILINE))


def assign(files: Collection[str], workflow: Path = CI) -> dict[str, tuple[str, ...]]:
    """Which shard runs which file: every shard whose pattern claims it, and
    the default shard for a file no pattern claims. A file claimed twice is
    listed twice, so the guard can see it rather than silently pick one."""
    legs = shards(workflow)
    split: dict[str, list[str]] = {s.name: [] for s in legs}
    for file in sorted(files):
        claimed = [s for s in legs if s.claims(file)]
        for shard in claimed or [s for s in legs if s.default]:
            split[shard.name].append(file)
    return {name: tuple(owned) for name, owned in split.items()}


def problems(files: Collection[str], workflow: Path = CI) -> list[str]:
    """Everything wrong with the split, as lines a human can act on."""
    legs = shards(workflow)
    split = assign(files, workflow)
    found: list[str] = []
    default = [s.name for s in legs if s.default]
    if len(default) != 1:
        found.append(
            "exactly one shard carries `default: true`, or a file no pattern "
            f"claims runs nowhere; today: {', '.join(default) or 'none does'}"
        )
    for file in sorted(files):
        homes = [name for name, owned in split.items() if file in owned]
        if not homes:
            found.append(f"in no shard, so it would never run: {file}")
        elif len(homes) > 1:
            found.append(f"in more than one shard ({', '.join(homes)}): {file}")
    for shard in legs:
        for pattern in shard.patterns:
            if not any(matches(file, pattern) for file in files):
                found.append(f"{shard.name}: {pattern} claims no browser test file")
    return found


def split_lines(files: Collection[str], workflow: Path = CI) -> list[str]:
    """The split as it stands, one line a shard: what CI runs where. This is
    what a rebalance reads, next to the `--durations` each shard prints."""
    default = {s.name for s in shards(workflow) if s.default}
    return [
        f"{name}{' (default)' if name in default else ''}: "
        f"{len(owned)} file{'' if len(owned) == 1 else 's'}, "
        f"{' '.join(owned) or 'none'}"
        for name, owned in assign(files, workflow).items()
    ]


def verify(receipts: Path, result: str) -> list[str]:
    """Everything wrong with this run, as lines a human can act on."""
    found = []
    if result != "success":
        found.append(f"the shards reported {result or 'nothing'}, not success")
    missing = [s.name for s in shards() if not (receipts / s.name).is_file()]
    if missing:
        found.append("no receipt from: " + ", ".join(missing))
    return found


def _files_of(name: str) -> tuple[int, str]:
    """The one line of file paths the named shard hands to pytest."""
    names = [s.name for s in shards()]
    if name not in names:
        return 1, f"no shard named {name}; the matrix has: {', '.join(names)}"
    files = browser_test_files()
    # A split this runner cannot trust is a hard stop, because a shard that
    # quietly runs a subset of its files would report a pass it did not earn.
    if found := problems(files):
        return 1, "\n".join(found)
    owned = assign(files)[name]
    if not owned:
        # pytest with no file argument runs the whole battery, so an empty
        # shard has to be a failure rather than a very long green run.
        return 1, f"{name} claims no browser test file"
    return 0, " ".join(owned)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verify",
        action="store_true",
        help="fail unless every shard left a receipt and the matrix is green",
    )
    parser.add_argument(
        "--files",
        metavar="SHARD",
        help="print the files this shard runs, one line, for pytest",
    )
    parser.add_argument("--receipts", default="receipts", type=Path)
    args = parser.parse_args()
    try:
        return _main(args)
    except Unreadable as e:
        print(e, file=sys.stderr)
        return 1


def _main(args: argparse.Namespace) -> int:
    if args.files:
        code, line = _files_of(args.files)
        print(line, file=sys.stderr if code else sys.stdout)
        return code
    if not args.verify:
        for line in split_lines(browser_test_files()):
            print(line)
        return 0
    found = verify(args.receipts, os.environ.get("SHARDS_RESULT", ""))
    for line in found:
        print(line, file=sys.stderr)
    if found:
        return 1
    print(f"all {len(shards())} shards passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
