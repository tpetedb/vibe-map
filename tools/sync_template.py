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
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "vibemap" / "data" / "template"

# The product's own loops: a camp has no engine to develop, no orders to run
# and no board room or shared memory of this repository's teams.
PRODUCT_ONLY_SKILLS = {"develop-camp", "work-order", "shared-memory"}

# Hooks that call these are the product's own harness (work orders, the board
# room); a camp has no tools/ folder, so a camp's settings are this repository's
# minus those.
PRODUCT_ONLY_HOOKS = ("tools/work.py", "tools/board.py")
SETTINGS = ROOT / ".claude" / "settings.json"
CAMP_SETTINGS = TEMPLATE / "_claude" / "settings.json"

PAIRS: list[tuple[Path, Path]] = [
    (ROOT / "env.example", TEMPLATE / "env.example"),
    (
        ROOT / ".claude" / "agents" / "scorekeeper.md",
        TEMPLATE / "_claude" / "agents" / "scorekeeper.md",
    ),
]


def camp_settings() -> str:
    """This repository's Claude Code settings as a camp gets them."""
    settings = json.loads(SETTINGS.read_text(encoding="utf-8"))
    hooks = {}
    for event, groups in settings.get("hooks", {}).items():
        kept = []
        for group in groups:
            ours = [
                h
                for h in group["hooks"]
                if not any(t in h.get("command", "") for t in PRODUCT_ONLY_HOOKS)
            ]
            if ours:
                kept.append({**group, "hooks": ours})
        if kept:
            hooks[event] = kept
    return json.dumps({**settings, "hooks": hooks}, indent=2) + "\n"


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
    if not CAMP_SETTINGS.exists() or CAMP_SETTINGS.read_text() != camp_settings():
        bad.append(CAMP_SETTINGS)
    return bad


def sync() -> None:
    for src, dst in pairs():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    CAMP_SETTINGS.write_text(camp_settings(), encoding="utf-8")
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
