"""Keep the packaged fork source in sync with the game's own source.

`vibe fork` copies the game's source into a camp. A camp from `vibe new` has
no engine, so an installed `vibe` has to carry that source itself: it lives in
vibemap/data/fork_source and is a mirror of src/, tools/build.py and the
generated inputs the build reads. Nothing here is edited by hand; the product's
own files are the original and this is the copy that travels in the wheel.

    uv run python tools/sync_fork_source.py          # write
    uv run python tools/sync_fork_source.py --check  # exit 1 when out of date
"""

from __future__ import annotations

import filecmp
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGED = ROOT / "vibemap" / "data" / "fork_source"

# The build reads these two generated files; campaign.json comes from the
# package itself, so the fork never needs a checkout for it.
GENERATED = ("notes.js", "tree.js")


def pairs() -> list[tuple[Path, Path]]:
    """(source in the product, destination in the package) for every file."""
    out: list[tuple[Path, Path]] = [
        (ROOT / "tools" / "build.py", PACKAGED / "tools" / "build.py")
    ]
    for name in GENERATED:
        out.append(
            (
                ROOT / "tools" / "generated" / name,
                PACKAGED / "tools" / "generated" / name,
            )
        )
    for f in sorted((ROOT / "src").rglob("*")):
        if f.is_file():
            out.append((f, PACKAGED / f.relative_to(ROOT)))
    return out


def stale() -> list[Path]:
    wanted = {dst for _, dst in pairs()}
    bad = [
        dst
        for src, dst in pairs()
        if not dst.exists() or not filecmp.cmp(src, dst, shallow=False)
    ]
    if PACKAGED.exists():
        bad += [p for p in PACKAGED.rglob("*") if p.is_file() and p not in wanted]
    return bad


def sync() -> None:
    for src, dst in pairs():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    wanted = {dst for _, dst in pairs()}
    for extra in list(PACKAGED.rglob("*")):
        if extra.is_file() and extra not in wanted:
            extra.unlink()


def main() -> int:
    if "--check" in sys.argv[1:]:
        bad = stale()
        for p in bad:
            print("stale:", p.relative_to(ROOT))
        return 1 if bad else 0
    sync()
    print(f"fork source synced: {len(pairs())} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
