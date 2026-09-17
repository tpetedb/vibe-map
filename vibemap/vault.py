"""The Obsidian vault: built from state, linted for orphans and dead links.

Tonight.md is the index and the hot cache. Every other note is reachable
from it. Notes carry YAML frontmatter (title, date, tags), dated sections
newest first, wikilinks, and tags at the bottom, which is what the Obsidian
graph colour groups key on.
"""

from __future__ import annotations

import datetime as dt
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from vibemap import campaign, project
from vibemap.config import DIFFICULTIES, Config
from vibemap.palette import (
    BLUE,
    CATEGORY_COLOURS,
    GREEN,
    ORANGE,
    RED,
    YELLOW,
    hex_to_int,
)
from vibemap.personas import Persona
from vibemap.state import State

ROOT = project.root()
WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]")

# Colour groups for the graph, first match wins in Obsidian.
GRAPH_GROUPS: tuple[tuple[str, str], ...] = (
    ("tag:#workstream", GREEN),
    ("tag:#people", BLUE),
    *((f"tag:#{c}", colour) for c, colour in CATEGORY_COLOURS.items()),
    ("tag:#tech", YELLOW),
    ("tag:#decision", RED),
    ("tag:#concept", ORANGE),
    ("tag:#recipe", "#D1477D"),
    ("tag:#persona", "#22D3EE"),
    ("tag:#council", "#C084FC"),
    ("tag:#overview", "#CCCCCC"),
)

MERMAID_CLASSES = (
    "  classDef done fill:#00A86B,stroke:#00D084,color:#000000\n"
    "  classDef todo fill:#0067A5,stroke:#0088CC,color:#FFFFFF\n"
    "  classDef deep fill:#FFBF00,stroke:#FFD500,color:#000000\n"
    "  classDef skip fill:#D32F2F,stroke:#F04923,color:#FFFFFF\n"
)
MERMAID_LEGEND = (
    "```mermaid\n"
    "flowchart LR\n"
    '  a["Done · green"]:::done\n'
    '  b["To do · blue"]:::todo\n'
    '  c(["Mentor on your path · yellow"]):::deep\n'
    '  d(["Mentor skipped · red"]):::skip\n' + MERMAID_CLASSES + "```\n"
)


def today() -> str:
    return dt.date.today().isoformat()


def safe_title(title: str) -> str:
    """A note title Obsidian accepts as a file name (no / \\ : * ? " < > |)."""
    out = title.replace("/", "-").replace(":", " -").replace("|", "-")
    out = re.sub(r'[\\*?"<>]', "", out)
    return re.sub(r"\s+", " ", out).strip()


def frontmatter(title: str, tags: list[str], date: str | None = None) -> str:
    return (
        f"---\ntitle: {json.dumps(title)}\ndate: {date or today()}\n"
        f"tags: [{', '.join(tags)}]\n---\n"
    )


@dataclass
class LintReport:
    notes: int = 0
    orphans: list[str] = field(default_factory=list)
    dead_links: list[tuple[str, str]] = field(default_factory=list)
    no_frontmatter: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not (self.orphans or self.dead_links or self.no_frontmatter)

    def link_count(self) -> int:
        return self._links

    _links: int = 0


class Vault:
    """Read and write the vault folder for one learner."""

    def __init__(self, cfg: Config, state: State) -> None:
        self.cfg = cfg
        self.state = state
        self.dir = cfg.vault_dir()

    # ---- primitives -------------------------------------------------------

    def path(self, title: str) -> Path:
        return self.dir / f"{safe_title(title)}.md"

    def exists(self, title: str) -> bool:
        return self.path(title).exists()

    def write(self, title: str, body: str, *, tags: list[str]) -> Path:
        """Write a whole note (frontmatter, H1, body). Overwrites.

        The frontmatter date is the day the note was first written and is
        kept on rewrite, so a rebuild changes only notes whose content moved
        instead of stamping a hundred files with today.
        """
        self.dir.mkdir(parents=True, exist_ok=True)
        p = self.path(title)
        date = _existing_date(p)
        p.write_text(
            frontmatter(title, tags, date) + f"# {title}\n\n{body.rstrip()}\n",
            encoding="utf-8",
        )
        return p

    def upsert_dated(
        self,
        title: str,
        *,
        summary: str,
        bullets: list[str],
        tags: list[str],
        sources: list[str] | None = None,
    ) -> Path:
        """Create the note or insert a dated section after its summary."""
        entry = f"## {today()}\n" + "\n".join(f"- {b}" for b in bullets) + "\n\n"
        p = self.path(title)
        if not p.exists():
            body = f"{summary}\n\n{entry}"
            if sources:
                body += "## Sources\n" + "\n".join(f"- {s}" for s in sources) + "\n\n"
            body += " ".join(f"#{t}" for t in tags)
            return self.write(title, body, tags=tags)
        text = p.read_text(encoding="utf-8")
        head, sep, rest = text.partition("\n## ")
        p.write_text(head.rstrip("\n") + "\n\n" + entry + (sep + rest if sep else ""))
        return p

    def notes(self) -> list[Path]:
        return sorted(p for p in self.dir.rglob("*.md") if "_templates" not in p.parts)

    # ---- build --------------------------------------------------------------

    def build(self, persona: Persona) -> list[Path]:
        """Write every generated note; return the paths touched."""
        self.dir.mkdir(parents=True, exist_ok=True)
        written = [
            self._write_evenings(),
            self._write_map(),
            self._write_path(),
            self._write_artifacts(),
            self._write_field(persona),
            self._write_cookbook(persona),
            self._write_tech_tree(),
            self._write_resources(),
            self._write_done_workstreams(),
            self._write_tonight(persona),
        ]
        self._write_graph_config()
        if self.cfg.vault.mode == "grow":
            from vibemap import grow  # local import: grow imports this module's types

            grow.sync(self)
            self._write_tonight(persona)
            grow.sync(self)
        return [p for group in written for p in group]

    def _write_tonight(self, persona: Persona) -> list[Path]:
        evs = campaign.evenings()
        diff = DIFFICULTIES[self.cfg.learner.difficulty]
        from vibemap.quests import level_for  # local import: quests imports vault

        age, label, nxt = level_for(self.state.xp)
        p = self.path("Tonight")
        build_log = _section(p, "Build log") if p.exists() else ""
        lines = [
            f"{self.state.name}, {persona.label}, on {diff.label}. "
            f"Level {label} ({age}) with {self.state.xp} XP"
            + (f", {nxt - self.state.xp} to the next level." if nxt else ".")
            + f" {self.state.total_done()} of 32 stops done.",
            "",
            "## Workstreams",
        ]
        for ws in evs["campus"].workstreams:
            mark = "done" if self.state.is_done("campus", ws.n) else "to do"
            lines.append(
                f"- {ws.hour} [[{safe_title(ws.name)}]]: {ws.outcome} ({mark})"
            )
        lines += ["", "## The campaign"]
        for w, ev in evs.items():
            lines.append(
                f"- [[{ev.short}]] {ev.title.split(': ', 1)[1]}: "
                f"{len(self.state.done_w.get(w, []))}/8 on the {ev.island}"
            )
        if self.cfg.vault.mode == "grow":
            from vibemap import grow

            lib = grow.library_dir(self)
            waiting = len(list(lib.glob("*.md"))) if lib.exists() else 0
            here = len(self.notes())
            lines += [
                "",
                "## The vault grows as you play",
                f"{here} notes here, {waiting} waiting in `_library`. "
                + grow.next_hint(self),
            ]
        lines += ["", "## Hot cache"]
        recent = self.state.log[-5:][::-1]
        if recent:
            for e in recent:
                ws = evs[e.world].workstreams[e.n - 1]
                lines.append(
                    f"- {e.at[:16]} [[{safe_title(ws.name)}]] +{e.xp} XP: "
                    f"{e.note or 'done'}"
                )
        else:
            lines.append("- Nothing yet. Walk to the 18:00 signpost.")
        hubs = "Resources: [[Resources]] · Tree: [[Tech tree]]"
        # Bootstrapped hubs (features, methods) stay reachable across rebuilds.
        if self.path("Obsidian features").exists():
            hubs += " · Obsidian: [[Obsidian features]]"
        lines += [
            "",
            "Map: [[Map]] · Mentors: [[Your path]] · Artifacts: [[Artifacts]] · "
            "Your field: [[Your field]] · " + hubs,
            "",
            "## Build log",
            build_log.strip() or "- (the agent adds one line per session here)",
            "",
            "#overview",
        ]
        return [self.write("Tonight", "\n".join(lines), tags=["overview"])]

    def _write_evenings(self) -> list[Path]:
        out = []
        for w, ev in campaign.evenings().items():
            rows = []
            for ws in ev.workstreams:
                src = " · ".join(f"[{t}]({u})" for t, u in ws.sources)
                mark = "x" if self.state.is_done(w, ws.n) else " "
                rows.append(
                    f"- [{mark}] {ws.hour} [[{safe_title(ws.name)}]]: {ws.outcome}"
                    + (f"  {src}" if src else "")
                )
            body = (
                f"{ev.island}.\n\n"
                + "\n".join(rows)
                + "\n\nBack to [[Tonight]] · [[Map]]\n\n#overview"
            )
            out.append(self.write(ev.short, body, tags=["overview"]))
        return out

    def _write_map(self) -> list[Path]:
        evs = campaign.evenings()
        lines = ["flowchart TD"]
        for wi, (w, ev) in enumerate(evs.items()):
            lines.append(f'  subgraph E{wi}["{ev.title}"]')
            ids = [f"{w[0]}{i}" for i in range(8)]
            for i, ws in enumerate(ev.workstreams):
                lines.append(f'    {ids[i]}["{ws.hour} {ws.name}"]')
            lines.append("    " + " --> ".join(ids))
            lines.append("  end")
        for wi in range(len(evs) - 1):
            lines.append(f"  E{wi} --> E{wi + 1}")
        for w in evs:
            done = [f"{w[0]}{i}" for i in range(8) if self.state.is_done(w, i + 1)]
            todo = [f"{w[0]}{i}" for i in range(8) if not self.state.is_done(w, i + 1)]
            if done:
                lines.append("  class " + ",".join(done) + " done")
            if todo:
                lines.append("  class " + ",".join(todo) + " todo")
        for m in campaign.mentors():
            st = self.state.path.get(m["id"])
            if st:
                lines.append(f'  M_{m["id"]}(["{m["name"]}"])')
                lines.append(f"  M_{m['id']} --- {m['world'][0]}0")
                lines.append(
                    f"  class M_{m['id']} {'deep' if st == 'deep' else 'skip'}"
                )
        lines.append(MERMAID_CLASSES.rstrip("\n"))
        mer = "\n".join(lines)
        body = (
            f"{self.state.total_done()}/32 stops across four evenings. "
            f"Updated {today()}.\n\n"
            f"```mermaid\n{mer}\n```\n\n### Legend\n\n{MERMAID_LEGEND}\n"
            "Back to [[Tonight]] · [[Your path]]\n\n#overview"
        )
        return [self.write("Map", body, tags=["overview"])]

    def _write_artifacts(self) -> list[Path]:
        """One note listing the island artifacts and what each teaches."""
        found = set(self.state.artifacts)
        body = [
            "Things on the island that explain one idea each. Walk up to the "
            "yellow ring and press Inspect; a found one turns green. The CLI "
            "learns about them through the progress code.",
            "",
        ]
        for a in campaign.artifacts():
            mark = "found" if a["id"] in found else "not yet"
            links = ", ".join(f"[[{t}]]" for t in a["links"])
            body.append(
                f"- {mark}: **{a['name']}** ({a['prop']}): {a['concept']}. "
                f"{a['what']} See {links}."
            )
        body += ["", "Back to [[Tonight]]", "", "#concept"]
        return [self.write("Artifacts", "\n".join(body), tags=["concept"])]

    def _write_path(self) -> list[Path]:
        out = []
        body = [
            "The mentors you met and what you chose. "
            "Change it in the game; re-import to update.",
            "",
        ]
        for m in campaign.mentors():
            st = self.state.path.get(m["id"])
            label = {"deep": "on your path", "skip": "skipped for now"}.get(
                st, "not met yet"
            )
            body.append(
                f"- [[{m['name']}]] ({campaign.WORLD_NAMES[m['world']]}): {label}"
            )
            out.append(self._write_mentor(m))
        body += ["", "Back to [[Tonight]] · [[Map]]", "", "#people"]
        out.append(self.write("Your path", "\n".join(body), tags=["people"]))
        return out

    def _write_mentor(self, m: dict) -> Path:
        srcs = "\n".join(f"- [{t}]({u})" for t, u in m["src"])
        ideas = "\n".join("- " + i for i in m["ideas"])
        body = (
            f"*{m['role']}*\n\n{m['bio']}\n\n**What they would tell you**\n{ideas}\n\n"
            f"**Going deeper**\n{m['deep']}\n\n**Rolinda asks:** {m['ask']}\n\n"
            f"## Sources\n{srcs}\n\nBack to [[Your path]]\n\n#people"
        )
        return self.write(m["name"], body, tags=["people"])

    def _write_field(self, persona: Persona) -> list[Path]:
        ds = persona.dataset
        recipes = "\n".join(
            f"- **{r.title}** (workstream {r.workstream}): {r.goal} See [[Cookbook]]."
            for r in persona.recipes
        )
        body = (
            f"{persona.label}: {persona.field}.\n\n"
            f"**Your game (workstream 1).** {persona.game_idea}\n\n"
            f"**Your dataset (workstream 3).** `data/examples/{ds.filename}` "
            "with columns "
            f"{', '.join(ds.columns)}. The question to answer: {ds.question}\n\n"
            f"**Rolinda asks.** {persona.rolinda}\n\n"
            f"## Recipes\n{recipes}\n\nBack to [[Tonight]]\n\n#persona"
        )
        return [self.write("Your field", body, tags=["persona"])]

    def _write_tech_tree(self) -> list[Path]:
        out = []
        by_name = {n.id: safe_title(n.name) for n in campaign.tech_nodes()}
        cat_name = {c: n for c, n, _ in campaign.categories()}
        overview = [
            "The whole map, shelf by shelf. Every topic has a depth: basics, "
            "working knowledge, deep.",
            "",
        ]
        for cat_id, name, blurb in campaign.categories():
            names = sorted(
                (n for n in campaign.tech_nodes() if n.category == cat_id),
                key=lambda n: n.depth,
            )
            overview.append(
                f"**{name}.** {blurb} "
                + ", ".join(f"[[{safe_title(n.name)}]]" for n in names)
            )
        overview += ["", "Back to [[Tonight]] · [[Resources]]", "", "#overview"]
        out.append(self.write("Tech tree", "\n".join(overview), tags=["overview"]))
        for n in campaign.tech_nodes():
            if self.exists(n.name) and not _is_generated(self.path(n.name)):
                continue
            shelf = cat_name[n.category]
            docs = ", ".join(f"[{t}]({u})" for t, u in n.docs)
            unlocks = ", ".join(f"[[{by_name[u]}]]" for u in n.unlocks if u in by_name)
            done = n.id in self.state.roadmap_done
            body = (
                f"{n.what}\n\n**History.** {n.history}\n\n"
                f"**Try in five minutes.** {n.try_it}\n\n"
                + (f"- Docs: {docs}\n" if docs else "")
                + (f"- Unlocks: {unlocks}\n" if unlocks else "")
                + f"- Shelf: {shelf} · Depth: {campaign.depth_label(n.depth)}"
                + (" · done" if done else "")
                + "\n\n<!-- generated from vibemap/tech.py; edit there -->\n\n"
                f"Back to [[Tech tree]]\n\n#tech #{n.category}"
            )
            out.append(self.write(n.name, body, tags=["tech", n.category]))
        return out

    def _write_resources(self) -> list[Path]:
        src = project.data_text("resources.md")
        body = src.split("\n", 1)[1].strip() + "\n\nBack to [[Tonight]]\n\n#overview"
        return [self.write("Resources", body, tags=["overview"])]

    def _write_cookbook(self, persona: Persona) -> list[Path]:
        parts = [
            f"Recipes for a {persona.label}. Each one is a prompt you paste into "
            "your provider, a definition of done, and the workstream it belongs to. "
            "Every persona has its own set; switch with `vibe persona <id>`.",
            "",
        ]
        for r in persona.recipes:
            parts += [
                f"## {r.title}",
                f"Workstream {r.workstream}. {r.goal}",
                "",
                "```text",
                r.prompt,
                "```",
                "",
                f"**Done when:** {r.done}",
                "",
            ]
        parts += ["Back to [[Your field]] · [[Tonight]]", "", "#recipe"]
        return [self.write("Cookbook", "\n".join(parts), tags=["recipe"])]

    def _write_done_workstreams(self) -> list[Path]:
        """One note per workstream: a stub until it is done, then dated entries."""
        out = []
        evs = campaign.evenings()
        logged = {(e.world, e.n): e for e in self.state.log}
        for world, ev in evs.items():
            for ws in ev.workstreams:
                if self.exists(ws.name):
                    continue
                e = logged.get((world, ws.n))
                if e:
                    bullets = [f"done at {e.at[11:16]}", e.note or "built it"]
                elif self.state.is_done(world, ws.n):
                    bullets = ["done in the game, imported with `vibe import`"]
                else:
                    bullets = ["not done yet; run `vibe check` when it is"]
                out.append(
                    self.upsert_dated(
                        ws.name,
                        summary=f"{ws.hour}, [[{ev.short}]]. Outcome: {ws.outcome}.",
                        bullets=bullets + ["links: [[Tonight]], [[Map]]"],
                        tags=["workstream"],
                        sources=[u for _, u in ws.sources],
                    )
                )
        return out

    def _write_ignore_filters(self, cfg_dir: Path) -> None:
        """Grow mode hides the library from the graph, search and completion."""
        app = cfg_dir / "app.json"
        if not app.exists():
            return
        conf = json.loads(app.read_text(encoding="utf-8"))
        filters = [f for f in conf.get("userIgnoreFilters", []) if f != "_library/"]
        if self.cfg.vault.mode == "grow":
            filters.append("_library/")
        conf["userIgnoreFilters"] = filters
        app.write_text(json.dumps(conf, indent=2) + "\n", encoding="utf-8")

    def _write_graph_config(self) -> None:
        cfg_dir = ROOT / self.cfg.vault.path / ".obsidian"
        self._write_ignore_filters(cfg_dir)
        p = cfg_dir / "graph.json"
        if not p.exists():
            return
        data = json.loads(p.read_text(encoding="utf-8"))
        data["colorGroups"] = [
            {"query": q, "color": {"a": 1, "rgb": hex_to_int(c)}}
            for q, c in GRAPH_GROUPS
        ]
        p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def add_build_log(self, line: str) -> None:
        """Append one bullet to Tonight's Build log (creates Tonight if needed)."""
        p = self.path("Tonight")
        if not p.exists():
            self.write(
                "Tonight",
                f"## Build log\n- {today()} {line}\n\n#overview",
                tags=["overview"],
            )
            return
        text = p.read_text(encoding="utf-8")
        marker = "## Build log\n"
        if marker not in text:
            text = text.rstrip("\n") + f"\n\n{marker}- {today()} {line}\n"
        else:
            head, _, tail = text.partition(marker)
            tail = tail.replace("- (the agent adds one line per session here)\n", "")
            text = head + marker + f"- {today()} {line}\n" + tail
        p.write_text(text, encoding="utf-8")

    # ---- lint ---------------------------------------------------------------

    def lint(self) -> LintReport:
        notes = self.notes()
        titles = {p.stem for p in notes}
        # In grow mode a link into the library is a note not yet unlocked,
        # not a dead one.
        library = self.dir.parent / "_library"
        if library.exists():
            titles |= {p.stem for p in library.glob("*.md")}
        inbound: dict[str, int] = {t: 0 for t in titles}
        report = LintReport(notes=len(notes))
        links = 0
        for p in notes:
            text = p.read_text(encoding="utf-8")
            if not text.startswith("---\n"):
                report.no_frontmatter.append(p.stem)
            # Links inside code are examples, not links (Obsidian agrees).
            prose = re.sub(r"```.*?```", "", text, flags=re.S)
            prose = re.sub(r"`[^`\n]*`", "", prose)
            for target in WIKILINK.findall(prose):
                target = target.strip()
                if not target:
                    continue
                links += 1
                if target in titles:
                    if target != p.stem:
                        inbound[target] += 1
                else:
                    report.dead_links.append((p.stem, target))
        report._links = links
        report.orphans = sorted(
            t for t, n in inbound.items() if n == 0 and t != "Tonight"
        )
        return report


def _existing_date(p: Path) -> str | None:
    """The `date:` of a note's frontmatter, if the note exists and has one."""
    if not p.exists():
        return None
    with p.open(encoding="utf-8") as fh:
        head = [next(fh, "") for _ in range(6)]
    if not head or head[0].strip() != "---":
        return None
    for line in head[1:]:
        if line.startswith("date:"):
            value = line.split(":", 1)[1].strip()
            return value if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) else None
    return None


def _section(p: Path, heading: str) -> str:
    text = p.read_text(encoding="utf-8")
    marker = f"## {heading}\n"
    if marker not in text:
        return ""
    body = text.split(marker, 1)[1]
    body = body.split("\n## ", 1)[0]
    return body.replace("#overview", "").strip()


def _is_generated(p: Path) -> bool:
    text = p.read_text(encoding="utf-8")
    # Notes written before the package move carry the old path.
    return "generated from vibemap/tech.py" in text or (
        "generated from tools/tech.py" in text
    )
