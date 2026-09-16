#!/usr/bin/env python3
"""Grimoire CLI: the terminal companion to the game.

Tracks the eight workstreams, writes a vault note per finished workstream,
draws a Mermaid progress map, and exchanges a progress code with the game.
Standard library only. State lives in .grimoire/state.json.
"""

import argparse
import base64
import csv
import datetime as dt
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / ".grimoire" / "state.json"
VAULT = ROOT / "vault" / "Grimoire"

WS = [
    (
        "18:00",
        "Innovation Hub",
        "a playable single-file game",
        "https://code.claude.com/docs/en/quickstart",
    ),
    (
        "19:00",
        "Centre of Excellence",
        "AGENTS.md rules and a first skill",
        "https://agents.md",
    ),
    (
        "20:00",
        "Data Warehouse",
        "scores.csv, DuckDB queries, a Python chart",
        "https://duckdb.org/docs/",
    ),
    (
        "21:00",
        "Business Continuity",
        "git history, one rollback, one hook",
        "https://code.claude.com/docs/en/hooks-guide",
    ),
    (
        "21:30",
        "Stakeholder Bridge",
        "one MCP integration",
        "https://code.claude.com/docs/en/mcp",
    ),
    (
        "22:00",
        "Knowledge Tree",
        "a linked vault and its graph",
        "https://help.obsidian.md/plugins/graph",
    ),
    (
        "22:30",
        "Go-to-Market",
        "the game at a public URL",
        "https://docs.github.com/en/pages/quickstart",
    ),
    (
        "23:00",
        "Autonomous Operations",
        "headless Claude on a schedule",
        "https://code.claude.com/docs/en/headless",
    ),
]

CAMP = json.loads((ROOT / "grimoire" / "campaign.json").read_text())
EV = CAMP["evenings"]
MENTORS = {m["id"]: m for m in CAMP["mentors"]}
WORLD_NAMES = {
    "campus": "Innovation Campus",
    "winter": "Cold Storage Cluster",
    "desert": "Sandbox Environment",
    "prod": "Production Environment",
}


def load():
    s = {
        "name": "Lotte",
        "done": [],
        "doneW": {k: [] for k in EV},
        "path": {},
        "log": [],
    }
    if STATE.exists():
        s.update(json.loads(STATE.read_text()))
    s.setdefault("doneW", {k: [] for k in EV})
    s.setdefault("path", {})
    if s["done"] and not s["doneW"].get("campus"):
        s["doneW"]["campus"] = list(s["done"])
    s["done"] = s["doneW"].setdefault("campus", [])
    return s


def save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, indent=2))


def today():
    return dt.date.today().isoformat()


def cmd_init(a):
    s = load()
    save(s)
    VAULT.mkdir(parents=True, exist_ok=True)
    tonight = VAULT / "Tonight.md"
    if not tonight.exists():
        tonight.write_text(
            "# Tonight\n\nEvening 1 of four. Workstreams: "
            + ", ".join(f"[[{x['n']}]]" for x in EV["campus"]["ws"])
            + "\n\nThe campaign: "
            + " · ".join(f"[[{ev['title'].split(': ')[0]}]]" for ev in EV.values())
            + "\n\nMap: [[Map]] · Mentors: [[Your path]] · Resources: [[Resources]]\n\n#overview\n"
        )
    for w, ev in EV.items():
        p = VAULT / (ev["title"].split(": ")[0] + ".md")
        if not p.exists():
            rows = "\n".join(
                f"- {x['h']} {x['n']}: {x['d']}"
                + (
                    ""
                    if not x["src"]
                    else "  " + " · ".join(f"[{t}]({u})" for t, u in x["src"])
                )
                for x in ev["ws"]
            )
            p.write_text(
                f"# {ev['title']}\n\n{WORLD_NAMES[w]}.\n\n{rows}\n\nBack to [[Tonight]]\n\n#overview\n"
            )
    res = VAULT / "Resources.md"
    if not res.exists():
        res.write_text((ROOT / "docs" / "RESOURCES.md").read_text())
    cmd_map(a)
    print(f"vault ready at {VAULT}")


def cmd_status(a):
    s = load()
    for w, ev in EV.items():
        d = s["doneW"].get(w, [])
        print(f"{ev['title']}  ({WORLD_NAMES[w]})  {len(d)}/8")
        for i, x in enumerate(ev["ws"], 1):
            print(f"   [{'x' if i in d else ' '}] {i}. {x['h']} {x['n']}")
    met = [m for m in MENTORS.values() if s["path"].get(m["id"])]
    print(
        f"Mentors: {len([m for m in met if s['path'][m['id']] == 'deep'])} on your path, {len([m for m in met if s['path'][m['id']] == 'skip'])} skipped, {len(MENTORS) - len(met)} not met"
    )


def cmd_done(a):
    s = load()
    n = a.n
    w = a.world
    if w not in EV:
        sys.exit("world is one of: " + ", ".join(EV))
    if not 1 <= n <= 8:
        sys.exit("workstream is 1-8")
    x = EV[w]["ws"][n - 1]
    h, name, out, url = x["h"], x["n"], x["d"], x["src"][0][1] if x["src"] else ""
    if n not in s["doneW"].setdefault(w, []):
        s["doneW"][w].append(n)
    s["log"].append(
        {
            "n": n,
            "at": dt.datetime.now().isoformat(timespec="minutes"),
            "note": a.note or "",
        }
    )
    save(s)
    VAULT.mkdir(parents=True, exist_ok=True)
    p = VAULT / f"{name}.md"
    head = f"# {name}\n\n{h}. Outcome: {out}.\n\n" if not p.exists() else p.read_text()
    entry = f"## {today()}\n- done at {dt.datetime.now():%H:%M}\n- {a.note or 'built it'}\n- links: [[Tonight]], [[Map]], [[{EV[w]['title'].split(': ')[0]}]]\n\n"
    if not p.exists():
        head += entry + f"## Sources\n- {url}\n\n#workstream\n"
        p.write_text(head)
    else:
        # insert after the title paragraph
        parts = head.split("\n## ", 1)
        p.write_text(
            parts[0].rstrip("\n")
            + "\n\n"
            + entry
            + ("## " + parts[1] if len(parts) > 1 else "")
        )
    cmd_map(a)
    print(f"[x] {n}. {name}: note written to {p.relative_to(ROOT)}")


def cmd_map(a):
    s = load()
    lines = ["flowchart TD"]
    total = 0
    done_all = 0
    for wi, (w, ev) in enumerate(EV.items()):
        done = set(s["doneW"].get(w, []))
        done_all += len(done)
        total += 8
        lines.append(f'  subgraph E{wi}["{ev["title"]}"]')
        ids = [f"{w[0]}{i}" for i in range(8)]
        for i, x in enumerate(ev["ws"]):
            lines.append(f'    {ids[i]}["{x["h"]} {x["n"]}"]')
        lines.append("    " + " --> ".join(ids))
        lines.append("  end")
        d = [ids[i] for i in range(8) if i + 1 in done]
        t = [ids[i] for i in range(8) if i + 1 not in done]
        if d:
            lines.append("  class " + ",".join(d) + " done")
        if t:
            lines.append("  class " + ",".join(t) + " todo")
    for wi in range(len(EV) - 1):
        lines.append(f"  E{wi} --> E{wi + 1}")
    for m in MENTORS.values():
        st = s["path"].get(m["id"])
        if st:
            lines.append(
                f'  M_{m["id"]}(["{m["name"]}"]):::{"deep" if st == "deep" else "skip"} --- {m["world"][0]}0'
            )
    lines += [
        "  classDef done fill:#34D399,color:#0b2b1c,stroke:#10B981",
        "  classDef todo fill:#1e1e1e,color:#ddd,stroke:#555",
        "  classDef deep fill:#22D3EE,color:#062a33",
        "  classDef skip fill:#FB7185,color:#3b0a12",
    ]
    mer = "\n".join(lines)
    VAULT.mkdir(parents=True, exist_ok=True)
    (VAULT / "Map.md").write_text(
        f"# Map\n\n{done_all}/{total} stops across four evenings. Updated {today()}.\n\n```mermaid\n{mer}\n```\n\nBack to [[Tonight]] · [[Your path]].\n\n#overview\n"
    )
    write_path(s)
    if getattr(a, "cmd", "") == "map":
        print(mer)
        print("\nwritten to vault/Grimoire/Map.md")


def write_path(s):
    VAULT.mkdir(parents=True, exist_ok=True)
    body = [
        "# Your path",
        "",
        "The mentors you met and what you chose. Change it in the game; re-import to update.",
        "",
    ]
    for m in MENTORS.values():
        st = s["path"].get(m["id"])
        body.append(
            f"- [[{m['name']}]] ({WORLD_NAMES[m['world']]}): "
            + {"deep": "on your path", "skip": "skipped for now"}.get(st, "not met yet")
        )
        if st == "deep":
            p = VAULT / f"{m['name']}.md"
            if not p.exists():
                srcs = "\n".join(f"- [{t}]({u})" for t, u in m["src"])
                ideas = "\n".join("- " + i for i in m["ideas"])
                p.write_text(
                    f"# {m['name']}\n*{m['role']}*\n\n{m['bio']}\n\n**What they would tell you**\n{ideas}\n\n**Going deeper**\n{m['deep']}\n\n**Rolinda asks:** {m['ask']}\n\n**Sources**\n{srcs}\n\nBack to [[Your path]]\n\n#people\n"
                )
    body += ["", "#people", ""]
    (VAULT / "Your path.md").write_text("\n".join(body))


def cmd_export(a):
    s = load()
    code = (
        base64.urlsafe_b64encode(
            json.dumps(
                {
                    "name": s["name"],
                    "done": s["doneW"].get("campus", []),
                    "doneW": s["doneW"],
                    "path": s["path"],
                }
            ).encode()
        )
        .decode()
        .rstrip("=")
    )
    print(code)


def cmd_import(a):
    s = load()
    raw = a.code + "=" * (-len(a.code) % 4)
    d = json.loads(base64.urlsafe_b64decode(raw))
    s["name"] = d.get("name", s["name"])
    dw = d.get("doneW") or {"campus": d.get("done", [])}
    for w, lst in dw.items():
        for n in lst:
            if int(n) not in s["doneW"].setdefault(w, []):
                s["doneW"][w].append(int(n))
    s["path"].update(d.get("path", {}))
    save(s)
    cmd_map(a)
    cmd_status(a)


def cmd_scores(a):
    p = ROOT / "data" / "scores.csv"
    rows = list(csv.DictReader(p.open()))
    if not rows:
        print("no scores")
        return
    best = max(rows, key=lambda r: int(r["score"]))
    mean = sum(int(r["score"]) for r in rows) / len(rows)
    print(
        f"{len(rows)} runs, best {best['score']} by {best['player']}, mean {mean:.1f}"
    )


def main():
    ap = argparse.ArgumentParser(prog="grimoire")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    sub.add_parser("status")
    sub.add_parser("map")
    sub.add_parser("export")
    sub.add_parser("scores")
    d = sub.add_parser("done")
    d.add_argument("n", type=int)
    d.add_argument("note", nargs="?")
    d.add_argument(
        "--world", "-w", default="campus", help="campus | winter | desert | prod"
    )
    mp = sub.add_parser("mentor")
    mp.add_argument("id")
    mp.add_argument("choice", choices=["deep", "skip"])
    i = sub.add_parser("import")
    i.add_argument("code")
    a = ap.parse_args()
    if a.cmd == "mentor":
        s = load()
        s["path"][a.id] = a.choice
        save(s)
        write_path(s)
        print(f"{MENTORS[a.id]['name']}: {a.choice}")
        return
    {
        "init": cmd_init,
        "status": cmd_status,
        "done": cmd_done,
        "map": cmd_map,
        "export": cmd_export,
        "import": cmd_import,
        "scores": cmd_scores,
    }[a.cmd](a)


if __name__ == "__main__":
    main()
