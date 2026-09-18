"""The browser battery's shards: who owns which files, and the receipt check.

The split is written down once, in the `browser-shard` matrix of
`.github/workflows/ci.yml`, and read back from there by both the test that
guards it and the aggregator job that reports the required status check.

The aggregator asks two questions, because a required check that can report
success while a shard did not run is worse than no check at all: the aggregate
result GitHub gives for the matrix job, and a receipt from every shard the
matrix defines.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CI = ROOT / ".github" / "workflows" / "ci.yml"


@dataclass(frozen=True, slots=True)
class Shard:
    """One leg of the browser matrix: a name and the test files it runs."""

    name: str
    files: tuple[str, ...]


def shards(workflow: Path = CI) -> tuple[Shard, ...]:
    flow = yaml.safe_load(workflow.read_text(encoding="utf-8"))
    include = flow["jobs"]["browser-shard"]["strategy"]["matrix"]["include"]
    return tuple(Shard(e["shard"], tuple(str(e["files"]).split())) for e in include)


def verify(receipts: Path, result: str) -> list[str]:
    """Everything wrong with this run, as lines a human can act on."""
    problems = []
    if result != "success":
        problems.append(f"the shards reported {result or 'nothing'}, not success")
    missing = [s.name for s in shards() if not (receipts / s.name).is_file()]
    if missing:
        problems.append("no receipt from: " + ", ".join(missing))
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verify",
        action="store_true",
        help="fail unless every shard left a receipt and the matrix is green",
    )
    parser.add_argument("--receipts", default="receipts", type=Path)
    args = parser.parse_args()
    if not args.verify:
        for s in shards():
            print(f"{s.name}: {' '.join(s.files)}")
        return 0
    problems = verify(args.receipts, os.environ.get("SHARDS_RESULT", ""))
    for line in problems:
        print(line, file=sys.stderr)
    if problems:
        return 1
    print(f"all {len(shards())} shards passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
