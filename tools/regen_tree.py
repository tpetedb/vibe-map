"""Regenerate docs/ROADMAP.md and the tech-note JS from tools/tech.py.
Usage: python3 tools/regen_tree.py   (prints where to paste the JS; the game embeds it in NOTES/AGES/TREE)"""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from tech import AGES, T

EXIST = {
    "agentsmd": "AGENTS.md",
    "skills": "Agent Skills standard",
    "hooks": "Hook",
    "mcp": "MCP",
    "vault": "Claude and Obsidian",
}
name = {i: (EXIST.get(i, n)) for i, a, n, *_ in T}
agename = {a: (n, l) for a, n, l, d in AGES}
notes = {}
for i, a, n, what, hist, tr, docs, unl in T:
    if i in EXIST:
        continue
    an, lv = agename[a]
    md = f"# {n}\n{what}\n**History.** {hist}\n**Try in five minutes.** {tr}\n"
    if docs:
        md += "- Docs: " + ", ".join(f"[{l}]({u})" for l, u in docs) + "\n"
    if unl:
        md += "- Unlocks: " + ", ".join(f"[[{name[u]}]]" for u in unl) + "\n"
    md += f"- Age: {an} · Level: {lv}\n#tech #{a}"
    notes[n] = {"t": a, "md": md}
ov = (
    "# Tech tree\nThe roadmap from intern to expert, Age of Empires style.\n"
    + "".join(
        f"**{an} ({lv}).** {d} "
        + ", ".join(f"[[{name[i]}]]" for i, aa, *_ in T if aa == a)
        + "\n"
        for a, an, lv, d in AGES
    )
    + "- See also: [[Resources]], [[Template repo]], [[Tonight]]\n#overview"
)
notes["Tech tree"] = {"t": "future", "md": ov}
out = pathlib.Path(__file__).parent / "generated"
out.mkdir(exist_ok=True)
(out / "notes.js").write_text(
    ",\n".join(
        f"{json.dumps(k)}:{{t:{json.dumps(v['t'])},md:`{v['md'].replace('`', '\\`')}`}}"
        for k, v in notes.items()
    )
)
(out / "tree.js").write_text(
    "const AGES="
    + json.dumps([[a, an, lv, d] for a, an, lv, d in AGES])
    + ";const TREE="
    + json.dumps(
        {a: [{"id": i, "n": name[i]} for i, aa, *_ in T if aa == a] for a, *_ in AGES}
    )
    + ";"
)
md = "# Roadmap: from intern to expert, in ages\n\nAn Age of Empires style tech tree. Each technology: what it is, real history, a five-minute try, docs, and what it unlocks.\n\n"
for a, an, lv, d in AGES:
    md += f"## {an} ({lv})\n\n{d}\n\n"
    for i, aa, n, what, hist, tr, docs, unl in T:
        if aa != a:
            continue
        if i in EXIST:
            md += f"### {n}\n\nCovered in the workstreams; see `docs/RESOURCES.md` and the vault note.\n\n"
            continue
        md += f"### {n}\n\n{what}\n\n**History.** {hist}\n\n**Try in five minutes.** {tr}\n\n"
        if docs:
            md += "Docs: " + " · ".join(f"[{l}]({u})" for l, u in docs) + "\n\n"
        if unl:
            md += "Unlocks: " + ", ".join(name[u] for u in unl) + "\n\n"
(pathlib.Path(__file__).parent.parent / "docs" / "ROADMAP.md").write_text(md)
print(
    "wrote docs/ROADMAP.md and tools/generated/{notes,tree}.js; paste the JS into game/grimoire.html NOTES / AGES+TREE"
)
