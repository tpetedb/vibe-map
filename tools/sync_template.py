"""Keep the camp template in sync with the product's own agent configuration.

The template `vibe new` copies lives in vibemap/data/template so an installed
`vibe` carries it. The skills, the backup hook and the scorekeeper subagent are
the same files the product repository uses, so they are copied from there, not
maintained twice. Dot-folders are stored with a leading underscore (`_agents`,
`_claude`, `_github`, `_gitignore`) so packaging never skips them; `vibe new`
puts the dots back.

    uv run python tools/sync_template.py          # write
    uv run python tools/sync_template.py --check  # exit 1 when out of date
"""

from __future__ import annotations

import filecmp
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "vibemap" / "data" / "template"

# The develop-camp skill is the product's own loop; a camp has no engine to develop.
PRODUCT_ONLY_SKILLS = {"develop-camp"}

PAIRS: list[tuple[Path, Path]] = [
    (ROOT / "env.example", TEMPLATE / "env.example"),
    (ROOT / ".claude" / "settings.json", TEMPLATE / "_claude" / "settings.json"),
    (
        ROOT / ".claude" / "agents" / "scorekeeper.md",
        TEMPLATE / "_claude" / "agents" / "scorekeeper.md",
    ),
]


def pairs() -> list[tuple[Path, Path]]:
    out = list(PAIRS)
    for skill in sorted((ROOT / ".agents" / "skills").iterdir()):
        if not skill.is_dir() or skill.name in PRODUCT_ONLY_SKILLS:
            continue
        for f in sorted(skill.rglob("*")):
            if f.is_file():
                out.append(
                    (f, TEMPLATE / "_agents" / "skills" / f.relative_to(skill.parent))
                )
    return out


def stale() -> list[Path]:
    wanted = {dst for _, dst in pairs()}
    bad = [
        dst
        for src, dst in pairs()
        if not dst.exists() or not filecmp.cmp(src, dst, shallow=False)
    ]
    for extra in (TEMPLATE / "_agents" / "skills").rglob("*"):
        if extra.is_file() and extra not in wanted:
            bad.append(extra)
    return bad


def sync() -> None:
    for src, dst in pairs():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    wanted = {dst for _, dst in pairs()}
    for extra in list((TEMPLATE / "_agents" / "skills").rglob("*")):
        if extra.is_file() and extra not in wanted:
            extra.unlink()


def main() -> int:
    if "--check" in sys.argv[1:]:
        bad = stale()
        for p in bad:
            print("stale:", p.relative_to(ROOT))
        return 1 if bad else 0
    sync()
    print(f"template synced: {len(pairs())} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
