"""Grow mode: the vault starts nearly empty and fills up as you play.

Every note still exists, in ``vault/_library/`` (excluded from Obsidian's
graph and search). A note moves into the camp folder when the campaign
unlocks it: the hubs from the start, a workstream note and its one-hop links
when the stop is done, a mentor when you go deep with them, an artifact's
notes when you inspect it, the Obsidian feature notes when the vault stop is
done, a tech note when the roadmap marks it done, or anything by hand with
``vibe vault unlock``. Notes you wrote yourself are never moved: only titles
listed in ``_library/.index`` belong to the library.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from vibemap import campaign

if TYPE_CHECKING:
    from vibemap.vault import Vault

WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]")
ALWAYS = (
    "Tonight",
    "Map",
    "Your field",
    "Your path",
    "Artifacts",
    "Tech tree",
    "Resources",
    "Workstreams",
    "Template repo",
    "Terminal companion",
    "Tom",
    "Rolinda",
    "Rolinda's questions",
)
VAULT_STOP = 6  # the campus workstream that builds the vault


def library_dir(vault: Vault) -> Path:
    return vault.dir.parent / "_library"


def _index_path(vault: Vault) -> Path:
    return library_dir(vault) / ".index"


def read_index(vault: Vault) -> set[str]:
    p = _index_path(vault)
    if not p.exists():
        return set()
    return {line for line in p.read_text(encoding="utf-8").splitlines() if line}


def write_index(vault: Vault, titles: set[str]) -> None:
    library_dir(vault).mkdir(parents=True, exist_ok=True)
    _index_path(vault).write_text("\n".join(sorted(titles)) + "\n", encoding="utf-8")


def _links_of(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    prose = re.sub(r"```.*?```", "", text, flags=re.S)
    prose = re.sub(r"`[^`\n]*`", "", prose)
    return {m.strip() for m in WIKILINK.findall(prose) if m.strip()}


def unlocked_titles(vault: Vault, lookup: dict[str, Path]) -> set[str]:
    """Which titles the campaign has unlocked, given every note's path."""
    st = vault.state
    out: set[str] = set(ALWAYS) | {st.name}
    evs = campaign.evenings()
    for ev in evs.values():
        out.add(ev.short)
    for world, ev in evs.items():
        for ws in ev.workstreams:
            if st.is_done(world, ws.n):
                out.add(ws.name)
                p = lookup.get(ws.name)
                if p:
                    out |= _links_of(p)
    for m in campaign.mentors():
        if st.path.get(m["id"]) == "deep":
            out.add(m["name"])
    for a in campaign.artifacts():
        if a["id"] in st.artifacts:
            out |= set(a["links"])
    ids = {n.id: n.name for n in campaign.tech_nodes()}
    out |= {ids[t] for t in st.roadmap_done if t in ids}
    if st.is_done("campus", VAULT_STOP):
        out |= {t for t in lookup if t.startswith("Obsidian - ")}
        out.add("Obsidian features")
    out |= set(st.unlocked)
    return out


def sync(vault: Vault) -> tuple[int, int]:
    """Move locked library notes out of the camp and unlocked ones back in.

    Returns:
        (notes in the camp, notes waiting in the library).
    """
    lib = library_dir(vault)
    lib.mkdir(parents=True, exist_ok=True)
    camp_notes = {
        p.stem: p for p in vault.dir.rglob("*.md") if "_templates" not in p.parts
    }
    lib_notes = {p.stem: p for p in lib.glob("*.md")}
    index = read_index(vault)
    if not index:
        # First run: everything the camp holds now is the library's.
        index = set(camp_notes)
    index |= set(lib_notes)
    lookup = {**lib_notes, **camp_notes}
    unlocked = unlocked_titles(vault, lookup)
    for title, p in camp_notes.items():
        if title in index and title not in unlocked:
            shutil.move(str(p), str(lib / p.name))
    for title, p in lib_notes.items():
        if title not in unlocked:
            continue
        target = vault.dir / p.name
        if not target.exists():
            shutil.move(str(p), str(target))
        elif target.read_bytes() == p.read_bytes():
            p.unlink()
        # A camp note that differs is the learner's: it stays, and the library
        # copy waits rather than overwriting their words.
    write_index(vault, index)
    camp_count = len(
        [p for p in vault.dir.rglob("*.md") if "_templates" not in p.parts]
    )
    return camp_count, len(list(lib.glob("*.md")))


def restore_all(vault: Vault) -> int:
    """Full mode again: every library note back into the camp."""
    lib = library_dir(vault)
    moved = 0
    if lib.exists():
        for p in sorted(lib.glob("*.md")):
            target = vault.dir / p.name
            if not target.exists():
                shutil.move(str(p), str(target))
                moved += 1
            elif target.read_bytes() == p.read_bytes():
                p.unlink()
            elif p.stat().st_mtime > target.stat().st_mtime:
                # Both sides have a version: the newer one comes back and the
                # other keeps its place in the library. Nothing is deleted.
                _swap(p, target)
                moved += 1
        idx = _index_path(vault)
        if idx.exists():
            idx.unlink()
        if not any(lib.iterdir()):
            lib.rmdir()
    return moved


def _swap(library: Path, camp: Path) -> None:
    """Exchange a library note and the camp note of the same name."""
    holding = library.with_name(library.name + ".swap")
    library.rename(holding)
    camp.rename(library)
    holding.rename(camp)


def unlock(vault: Vault, title: str) -> Path | None:
    """Unlock one note by hand; returns its new path, or None if unknown."""
    lib = library_dir(vault)
    src = lib / f"{title}.md"
    if not src.exists():
        return vault.path(title) if vault.exists(title) else None
    if title not in vault.state.unlocked:
        vault.state.unlocked.append(title)
    target = vault.dir / src.name
    shutil.move(str(src), str(target))
    return target


def next_hint(vault: Vault) -> str:
    """One sentence on what unlocks the next notes."""
    st = vault.state
    evs = campaign.evenings()
    for ws in evs["campus"].workstreams:
        if not st.is_done("campus", ws.n):
            return f"Finish {ws.hour} {ws.name} to unlock its notes."
    found = len(st.artifacts)
    total = len(campaign.artifacts())
    if found < total:
        return f"Inspect an artifact on the island ({found} of {total} found)."
    return "Go deep with a mentor, or unlock a note by hand with vibe vault unlock."
