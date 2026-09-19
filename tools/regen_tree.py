"""Regenerate the tech tree outputs from vibemap/tech.py.

Writes docs/ROADMAP.md, docs/RESOURCES.md, docs/OBSIDIAN.md and
tools/generated/{notes,tree}.js;
tools/build.py
embeds the JS into the game. Never hand-edit those outputs.

    uv run python tools/regen_tree.py           write the three outputs
    uv run python tools/regen_tree.py --check   exit 1 if any output is stale
"""

from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from vibemap.obsidian import doc_markdown  # noqa: E402
from vibemap.project import data_text  # noqa: E402
from vibemap.tech import CATEGORIES, DEPTHS, T, category  # noqa: E402

GENERATED = ROOT / "tools" / "generated"
ROADMAP = ROOT / "docs" / "ROADMAP.md"
RESOURCES = ROOT / "docs" / "RESOURCES.md"
OBSIDIAN = ROOT / "docs" / "OBSIDIAN.md"

# Topics that already have a handwritten vault note under this title.
EXIST = {
    "agentsmd": "AGENTS.md",
    "skills": "Agent Skills standard",
    "hooks": "Hook",
    "mcp": "MCP",
    "vault": "Claude and Obsidian",
}
OVERVIEW_INTRO = (
    "The whole map, shelf by shelf. Every topic has a depth (basics, working "
    "knowledge, deep) and says what it is, real history, a five-minute try, "
    "docs, and what it unlocks. Read a shelf top to bottom, or jump."
)


def _note_title(tech_id: str, name: str) -> str:
    return EXIST.get(tech_id, name)


def render() -> tuple[dict[str, dict[str, str]], str, str]:
    """Return (vault notes, tree JS, roadmap Markdown)."""
    name = {i: _note_title(i, n) for i, a, n, *_ in T}
    catname = {c: n for c, n, _ in CATEGORIES}
    notes: dict[str, dict[str, str]] = {}
    for i, _a, n, what, hist, tr, docs, unl in T:
        if i in EXIST:
            continue
        cat, depth = category(i)
        md = f"# {n}\n{what}\n**History.** {hist}\n**Try in five minutes.** {tr}\n"
        if docs:
            md += "- Docs: " + ", ".join(f"[{lb}]({u})" for lb, u in docs) + "\n"
        if unl:
            md += "- Unlocks: " + ", ".join(f"[[{name[u]}]]" for u in unl) + "\n"
        md += f"- Shelf: {catname[cat]} · Depth: {DEPTHS[depth]}\n#tech #{cat}"
        notes[n] = {"t": cat, "md": md}
    overview = f"# Tech tree\n{OVERVIEW_INTRO}\n" + "".join(
        f"**{cn}.** {d} "
        + ", ".join(
            f"[[{name[i]}]]"
            for i, *_ in sorted(T, key=lambda t: category(t[0])[1])
            if category(i)[0] == c
        )
        + "\n"
        for c, cn, d in CATEGORIES
    )
    overview += "- See also: [[Resources]], [[Template repo]], [[Tonight]]\n#overview"
    notes["Tech tree"] = {"t": "future", "md": overview}

    # A few topics are covered by a note written by hand under a shorter name.
    # The data names the topic, so the game needs the same map to find the note.
    alias = {n: EXIST[i] for i, _a, n, *_ in T if i in EXIST}
    tree_js = (
        "const NOTE_ALIAS="
        + json.dumps(alias)
        + ";const CATS="
        + json.dumps([[c, cn, d] for c, cn, d in CATEGORIES])
        + ";const DEPTHS="
        + json.dumps({str(k): v for k, v in DEPTHS.items()})
        + ";const TREE="
        + json.dumps(
            {
                c: [
                    {"id": i, "n": name[i], "d": category(i)[1]}
                    for i, *_ in sorted(T, key=lambda t: category(t[0])[1])
                    if category(i)[0] == c
                ]
                for c, *_ in CATEGORIES
            }
        )
        + ";"
    )

    md = (
        "# Roadmap: the map, shelf by shelf\n\n"
        "Every topic has a depth: basics, working knowledge, deep. Each one: "
        "what it is, real history, a five-minute try, docs, and what it unlocks.\n\n"
    )
    for c, cn, d in CATEGORIES:
        md += f"## {cn}\n\n{d}\n\n"
        for i, _aa, n, what, hist, tr, docs, unl in sorted(
            T, key=lambda t: category(t[0])[1]
        ):
            if category(i)[0] != c:
                continue
            md += f"*{DEPTHS[category(i)[1]]}.* "
            if i in EXIST:
                md += (
                    f"### {n}\n\nCovered in the workstreams; see "
                    "`docs/RESOURCES.md` and the vault note.\n\n"
                )
                continue
            md += f"### {n}\n\n{what}\n\n**History.** {hist}\n\n"
            md += f"**Try in five minutes.** {tr}\n\n"
            if docs:
                md += "Docs: " + " · ".join(f"[{lb}]({u})" for lb, u in docs) + "\n\n"
            if unl:
                md += "Unlocks: " + ", ".join(name[u] for u in unl) + "\n\n"
    return notes, tree_js, md


def _notes_js(notes: dict[str, dict[str, str]]) -> str:
    return ",\n".join(
        f"{json.dumps(k)}:{{t:{json.dumps(v['t'])},md:`{v['md'].replace('`', '\\`')}`}}"
        for k, v in notes.items()
    )


def main() -> None:
    notes, tree_js, md = render()
    outputs = {
        GENERATED / "notes.js": _notes_js(notes),
        GENERATED / "tree.js": tree_js,
        ROADMAP: md,
        RESOURCES: data_text("resources.md"),
        OBSIDIAN: doc_markdown(),
    }
    if "--check" in sys.argv:
        stale = [
            p.relative_to(ROOT).as_posix()
            for p, text in outputs.items()
            if not p.exists() or p.read_text(encoding="utf-8") != text
        ]
        if stale:
            print("stale tech tree outputs: " + ", ".join(stale) + "; run: just tree")
            sys.exit(1)
        print("tree OK: outputs match vibemap/tech.py")
        return
    GENERATED.mkdir(exist_ok=True)
    for p, text in outputs.items():
        p.write_text(text, encoding="utf-8")
    print(f"wrote {len(notes)} notes, the tree and docs/ROADMAP.md; run: just build")


if __name__ == "__main__":
    main()
