"""Obsidian feature modules: one note per feature, bootstrapped into the vault.

The facts come from the official help (obsidianmd/obsidian-help, the source
of https://help.obsidian.md), extracted into ``vibemap/data/obsidian.json``:
what the feature is, the exact commands and syntax, a five-minute try and
the page URL. ``bootstrap()`` writes a note per feature into the vault and, where the
feature is a file format, a working example next to it (a canvas, a base,
a template, a deck, a CSS snippet).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from vibemap import project


@dataclass(frozen=True, slots=True)
class Feature:
    """One Obsidian feature as the help describes it.

    Attributes:
        id: Lowercase-dashes identifier used on the command line.
        name: The help page title.
        kind: core plugin, editing, linking, extending, service or format.
        what: One or two sentences grounded in the page.
        facts: Short concrete facts: commands, syntax, settings, defaults.
        syntax: A verbatim example from the page, or empty.
        try_it: A five-minute exercise in the vault.
        url: The help page.
    """

    id: str
    name: str
    kind: str
    what: str
    facts: tuple[str, ...]
    syntax: str
    try_it: str
    url: str

    @property
    def title(self) -> str:
        return f"Obsidian - {self.name}"


@cache
def features() -> dict[str, Feature]:
    raw = json.loads(project.data_text("obsidian.json"))
    out: dict[str, Feature] = {}
    for f in raw:
        out[f["id"]] = Feature(
            f["id"],
            f["name"],
            f["kind"],
            f["what"],
            tuple(f["facts"]),
            f.get("syntax", ""),
            f["try"],
            f["url"],
        )
    return out


def get_feature(feature_id: str) -> Feature:
    """Return a feature or raise ValueError naming the valid ids."""
    try:
        return features()[feature_id]
    except KeyError:
        raise ValueError(
            f"unknown feature {feature_id!r}; one of: {', '.join(features())}"
        ) from None


WIKILINK = re.compile(r"(!?\[\[[^\]]+\]\])")


def _quote_links(text: str) -> str:
    """Wikilinks quoted from the help are syntax, not links: show them as code.

    A fence mentioned in prose would unbalance the note's own fences, so it
    is spelled out.
    """
    return WIKILINK.sub(r"`\1`", text.replace("```", "three backticks"))


def _fence(f: Feature) -> str:
    """Tildes when the example itself contains a backtick fence (nesting)."""
    return "~~~" if "```" in f.syntax else "```"


def note_body(f: Feature) -> str:
    """The Markdown body of a feature note (no H1; the vault adds it)."""
    lines = [_quote_links(f.what), "", "## Facts", ""]
    lines += [f"- {_quote_links(fact)}" for fact in f.facts]
    if f.syntax:
        lines += [
            "",
            "## Syntax",
            "",
            _fence(f) + ("yaml" if f.id == "bases" else ""),
            f.syntax.rstrip(),
            _fence(f),
        ]
    lines += ["", "## Try in five minutes", "", _quote_links(f.try_it)]
    extra = EXTRAS.get(f.id)
    if extra:
        lines += ["", "## In this vault", "", extra.note_line]
    lines += [
        "",
        "## Source",
        "",
        f"- [{f.name}, Obsidian Help]({f.url})",
        "",
        f"Back to [[Obsidian features]]. Kind: {f.kind}.",
    ]
    return "\n".join(lines)


def hub_body(done: set[str] | None = None) -> str:
    """The hub note listing every feature, grouped by kind."""
    done = done or set()
    kinds = ("linking", "editing", "core plugin", "format", "extending", "service")
    lines = [
        "Every feature of Obsidian the help documents, one note each, with the "
        "exact commands and a five-minute try. Bootstrap them with "
        "`vibe vault feature --all` or one at a time.",
        "",
    ]
    for kind in kinds:
        group = [f for f in features().values() if f.kind == kind]
        if not group:
            continue
        lines += [f"## {kind.capitalize()}", ""]
        for f in group:
            mark = " (done)" if f.id in done else ""
            lines.append(f"- [[{f.title}]]{mark}: {f.what.split('. ')[0]}.")
        lines.append("")
    lines += [
        "## Source",
        "",
        "- [Obsidian Help](https://help.obsidian.md/), the official documentation.",
        "",
        "See also [[Markdown and Obsidian]], [[Memory - the vault as long-term memory]], [[Tonight]].",
    ]
    return "\n".join(lines)


@dataclass(frozen=True, slots=True)
class Extra:
    """A working example file a feature note points at."""

    path: str
    body: str
    note_line: str


CANVAS = json.dumps(
    {
        "nodes": [
            {"id": "a1", "type": "file", "file": "Camp/Obsidian - Canvas.md", "x": -300, "y": -80, "width": 360, "height": 200},
            {"id": "a2", "type": "text", "text": "A text card. Drag notes, images and web pages in; draw lines between them.", "x": 140, "y": -80, "width": 320, "height": 140},
            {"id": "a3", "type": "file", "file": "Camp/Tonight.md", "x": -80, "y": 220, "width": 360, "height": 200},
        ],
        "edges": [
            {"id": "e1", "fromNode": "a1", "toNode": "a2", "label": "explains"},
            {"id": "e2", "fromNode": "a2", "toNode": "a3", "label": "lands in"},
        ],
    },
    indent=2,
)  # fmt: skip

BASE = """filters:
  and:
    - file.hasTag("tech")
views:
  - type: table
    name: Tech notes
    order:
      - file.name
      - date
      - tags
"""

TEMPLATE = """---
title: {{title}}
date: {{date:YYYY-MM-DD}}
tags: [feature]
---

# {{title}}

Created {{date}} at {{time}}.

> [!tip] What to write
> One idea, one link out, one link back.
"""

SLIDES = """One evening, one island, eight workstreams.

---

## Done is

A green check and one sentence you can explain to Rolinda.

---

## The vault

Everything you learned, linked. Open the [[Tonight]] note.
"""

SNIPPET = """/* Obsidian features demo: a coloured left rule on notes tagged #feature.
   Enable it under Settings, Appearance, CSS snippets. */
.markdown-preview-view .tag[href="#feature"] { color: #FFBF00; }
"""

EXTRAS: dict[str, Extra] = {
    "canvas": Extra(
        "Camp map.canvas",
        CANVAS,
        "`Camp map.canvas` next to this note is a JSON Canvas with two notes and a text card; open it and drag the cards.",
    ),
    "bases": Extra(
        "Tech notes.base",
        BASE,
        "`Tech notes.base` next to this note is a base: a table of every note tagged #tech, with its date and tags.",
    ),
    "templates": Extra(
        "_templates/obsidian/Feature note.md",
        TEMPLATE,
        "`_templates/obsidian/Feature note.md` is a template with {{title}}, {{date}} and {{time}}; point Settings, Templates at `_templates`.",
    ),
    "slides": Extra(
        "note:Camp deck",
        SLIDES,
        "[[Camp deck]] next to this note has three slides separated by `---`; run Slides: Start presentation on it.",
    ),
    "css-snippets": Extra(
        ".obsidian/snippets/feature-demo.css",
        SNIPPET,
        "`.obsidian/snippets/feature-demo.css` colours the #feature tag yellow once enabled under Settings, Appearance, CSS snippets.",
    ),
    "daily-notes": Extra(
        "_templates/obsidian/Daily.md",
        "---\ndate: {{date:YYYY-MM-DD}}\ntags: [daily]\n---\n\n# {{date:dddd D MMMM}}\n\n## Today\n\n- \n\n## Learned\n\n- \n",
        "`_templates/obsidian/Daily.md` is a daily note template; set it as the Daily notes template and the folder to `Daily`.",
    ),
}


def bootstrap(vault_dir: Path, feature_ids: list[str], *, write) -> list[str]:
    """Write the notes (through ``write``) and the example files; return titles.

    Args:
        vault_dir: The vault's note folder (``vault/Camp``); a canvas or base
            lands there, templates and snippets in the vault root, and a
            ``note:`` extra goes through ``write`` like any note.
        feature_ids: Which features to bootstrap.
        write: ``Vault.write(title, body, tags=...)``, injected so this module
            stays free of the vault's frontmatter rules.
    """
    titles: list[str] = []
    for fid in feature_ids:
        f = get_feature(fid)
        write(f.title, note_body(f), tags=["tech", "obsidian"])
        titles.append(f.title)
        extra = EXTRAS.get(fid)
        if extra and extra.path.startswith("note:"):
            write(extra.path[5:], extra.body, tags=["obsidian"])
        elif extra:
            root = vault_dir if "/" not in extra.path else vault_dir.parent
            target = root / extra.path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(extra.body, encoding="utf-8")
    write("Obsidian features", hub_body(set(feature_ids)), tags=["tech", "overview"])
    return titles


def doc_markdown() -> str:
    """docs/OBSIDIAN.md: the same table for readers outside the vault."""
    lines = [
        "# Obsidian, feature by feature",
        "",
        "Every feature the official help documents, in one table, with the exact "
        "commands and a five-minute try. `uv run vibe vault feature <id>` writes "
        "the matching note (and, for canvases, bases, templates, slides and "
        "snippets, a working example file) into the vault; `--all` writes them all. "
        "Source: [Obsidian Help](https://help.obsidian.md/).",
        "",
        "| id | Feature | Kind | What | Try |",
        "|---|---|---|---|---|",
    ]
    for f in features().values():
        lines.append(
            f"| `{f.id}` | [{f.name}]({f.url}) | {f.kind} | {f.what} | {f.try_it} |"
        )
    lines += ["", "## Syntax cheatsheet", ""]
    for f in features().values():
        if f.syntax:
            lines += [
                f"### {f.name}",
                "",
                _fence(f) + ("yaml" if f.id == "bases" else ""),
                f.syntax.rstrip(),
                _fence(f),
                "",
            ]
    return "\n".join(lines).rstrip() + "\n"
