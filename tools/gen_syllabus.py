"""Render the syllabus: the generated blocks of the Markdown, and the page.

Two outputs, one source of truth. The repetitive half of `docs/SYLLABUS.md`
(the course map, the mentors, the artifacts, the tech tree) is a function of
`vibemap/data/`, so it is written between markers in the Markdown instead of
typed; the prose around the markers is the teaching and stays hand-written.
`docs/site/syllabus.html` is then that whole Markdown as one self-contained
page, with the game's own palette and no third-party request, which
`.github/workflows/pages.yml` publishes next to the game as `syllabus.html`.

    uv run python tools/gen_syllabus.py           write both
    uv run python tools/gen_syllabus.py --check   exit 1 when either is stale
"""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from markdown_it import MarkdownIt  # noqa: E402

from vibemap import campaign, project, topics  # noqa: E402
from vibemap.config import Config  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "docs" / "SYLLABUS.md"
OUT = ROOT / "docs" / "site" / "syllabus.html"
CONFIG_JS = ROOT / "src" / "config" / "00-config.js"

# A generated region of the Markdown. The opening marker names the block and
# the command that rewrites it, so a reader who lands on it by accident knows
# what to run instead of typing.
OPEN = "<!-- generated:{name}. Do not edit inside; run `just syllabus`. -->"
CLOSE = "<!-- /generated:{name} -->"

TENS = ("", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy",
        "eighty", "ninety")  # fmt: skip
ONES = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen")  # fmt: skip


def spell(n: int) -> str:
    """A count as a word, because the prose around it is written out too."""
    if n < 20:
        return ONES[n]
    if n < 100:
        rest = f"-{ONES[n % 10]}" if n % 10 else ""
        return TENS[n // 10] + rest
    return str(n)


def link(label: str, url: str) -> str:
    return f"[{label}]({url})"


def sources(pairs: list[tuple[str, str]] | tuple[tuple[str, str], ...]) -> str:
    return " · ".join(link(label, url) for label, url in pairs)


# --- the generated blocks ----------------------------------------------------


def course_map() -> str:
    """Every stop of every evening, in one table per island."""
    evenings = campaign.evenings()
    stops = sum(len(e.workstreams) for e in evenings.values())
    lines = [
        f"{spell(len(evenings)).capitalize()} evenings, {spell(stops)} stops, one "
        "island each. Every stop has a definition of done the terminal companion "
        "can check, so the parts a night does not reach can be done alone later.",
        "",
    ]
    blurbs = campaign.raw()["evenings"]
    for world, evening in evenings.items():
        lines += [
            f"**{evening.title}** on the {campaign.WORLD_NAMES[world]}. "
            f"{blurbs[world]['blurb']}",
            "",
            "| Stop | What | You leave with | Sources |",
            "|---|---|---|---|",
        ]
        for ws in evening.workstreams:
            lines.append(
                f"| {ws.hour} | {ws.name} | {ws.outcome} | {sources(ws.sources)} |"
            )
        lines.append("")
    return "\n".join(lines).rstrip()


def mentors() -> str:
    """The twelve encounters: who, where, why them, and the record behind it."""
    people = campaign.mentors()
    lines = [
        f"{spell(len(people)).capitalize()} real people from the field stand on the "
        "islands. Every line a mentor speaks is a paraphrase of something that "
        "person is on record saying, with the link it came from, never an invented "
        "quote. `vibe check --mentor <id>` verifies the exercise.",
        "",
    ]
    for m in people:
        lines += [
            f"**{m['name']}**, {m['role']} ({campaign.WORLD_NAMES[m['world']]}). "
            f"{m['bio']}",
            "",
            f"Ask them: *{m['ask']}* Sources: {sources(m['src'])}",
            "",
        ]
    return "\n".join(lines).rstrip()


def artifacts() -> str:
    """The collectible lessons, with the documentation each real task reads."""
    items = campaign.artifacts()
    lines = [
        f"{spell(len(items)).capitalize()} artifacts stand on the four islands. "
        "Walk into the yellow ring and press **Inspect**: the sheet explains one "
        "concept, a small terminal demonstrates it, and **Do it for real** sets a "
        "task of under twenty minutes written from the official documentation of "
        "the thing the artifact stands for. The work goes in "
        "`workspace/artifacts/<id>/` and `vibe check --artifact <id>` runs it.",
        "",
        "| Artifact | Island | The concept | Do it for real | The documentation |",
        "|---|---|---|---|---|",
    ]
    for a in items:
        real = a["real"]
        doc = real["doc"]
        lines.append(
            f"| {a['name']} | {campaign.WORLD_NAMES[a['world']]} | {a['concept']} "
            f"| {real['title']} ({real['minutes']} min) "
            f"| {link(doc['title'], doc['url'])} |"
        )
    return "\n".join(lines).rstrip()


def tech_tree() -> str:
    """The packs, the shelves and every topic, with its age and its depth."""
    tree = topics.tree()
    packs = topics.packs()
    all_topics = topics.all_topics()
    by_shelf: dict[str, list[object]] = {}
    for t in all_topics:
        by_shelf.setdefault(t.shelf, []).append(t)
    lines = [
        f"{spell(len(all_topics)).capitalize()} topics on "
        f"{spell(len(tree.shelves))} shelves, in "
        f"{spell(len(tree.ages))} ages from intern to expert. A topic carries its "
        "own depth, so a shelf is something to come back to rather than a rank to "
        "pass. `vibe topics` lists them, `vibe topic <id>` opens one, "
        "`vibe check --topic <id>` marks it done, and "
        "[ROADMAP.md](ROADMAP.md) is the same tree in full.",
        "",
        "| Age | Level | What it covers |",
        "|---|---|---|",
    ]
    for age in tree.ages:
        lines.append(f"| {age.name} | {age.rank} | {age.blurb} |")
    lines += ["", f"### The packs ({spell(len(packs))})", ""]
    for p in packs:
        lines += [
            f"**{p.title}** ({spell(len(p.topics))} topics, first shelf "
            f"{p.shelf}). {p.blurb}",
            "",
        ]
    lines += ["", "### The shelves", ""]
    for shelf in tree.shelves:
        mine = by_shelf.get(shelf.id, [])
        if not mine:
            continue
        names = ", ".join(
            f"{t.title} ({tree.depths[t.depth]})"  # type: ignore[attr-defined]
            for t in mine
        )
        lines += [f"**{shelf.name}.** {shelf.blurb} {names}.", ""]
    return "\n".join(lines).rstrip()


BLOCKS = {
    "course-map": course_map,
    "mentors": mentors,
    "artifacts": artifacts,
    "tech-tree": tech_tree,
}


def sync(text: str) -> str:
    """Rewrite every generated region of the Markdown in place.

    Raises:
        SystemExit: when a marker the generator owns is missing from the file.
    """
    for name, render in BLOCKS.items():
        start, end = OPEN.format(name=name), CLOSE.format(name=name)
        if start not in text or end not in text:
            raise SystemExit(f"docs/SYLLABUS.md has no {name} block; expected {start}")
        head, _, rest = text.partition(start)
        _, _, tail = rest.partition(end)
        text = f"{head}{start}\n\n{render()}\n\n{end}{tail}"
    return text


# --- the page ----------------------------------------------------------------


def palette() -> dict[str, str]:
    """The game's own hues, read from src/config so they are defined once."""
    body = re.search(r"const PALETTE=\{(.*?)\};", CONFIG_JS.read_text("utf-8"), re.S)
    if not body:
        raise SystemExit("src/config/00-config.js has no PALETTE")
    return dict(re.findall(r'(\w+):"(#[0-9A-Fa-f]{6})"', body.group(1)))


def slug(text: str, seen: set[str]) -> str:
    """A stable anchor for a heading; a repeat gets a numbered suffix."""
    base = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "section"
    candidate, n = base, 1
    while candidate in seen:
        n += 1
        candidate = f"{base}-{n}"
    seen.add(candidate)
    return candidate


def _text_of(token: object) -> str:
    children = getattr(token, "children", None) or []
    return "".join(c.content for c in children if c.type in ("text", "code_inline"))


def render(md_text: str) -> tuple[str, list[tuple[int, str, str]]]:
    """The Markdown as HTML, plus the (level, id, title) rows for the contents."""
    md = MarkdownIt("commonmark").enable("table")
    tokens = md.parse(md_text)
    seen: set[str] = set()
    toc: list[tuple[int, str, str]] = []
    for i, token in enumerate(tokens):
        if token.type != "heading_open":
            continue
        title = _text_of(tokens[i + 1])
        anchor = slug(title, seen)
        token.attrSet("id", anchor)
        level = int(token.tag[1])
        if 2 <= level <= 3:
            toc.append((level, anchor, title))
    return md.renderer.render(tokens, md.options, {}), toc


def css(p: dict[str, str]) -> str:
    """One stylesheet: paper by day, the game's black by night, and print."""
    return f"""
:root{{
  --blue:{p["blue"]};--blue-bright:{p["blueBright"]};--green:{p["green"]};
  --orange:{p["orange"]};--yellow:{p["yellow"]};--red:{p["red"]};
  --paper:#FDFDFB;--ink:#16181D;--muted:#5C6472;--rule:#E3E4E8;
  --card:#F6F6F3;--code:#F1F1EE;
  --font-body:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",sans-serif;
  --font-mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
  --measure:38rem;
}}
@media (prefers-color-scheme:dark){{
  :root{{--paper:{p["black"]};--ink:{p["text"]};--muted:{p["muted"]};
    --rule:#23252C;--card:{p["surface"]};--code:#111218;--blue:{p["blueBright"]};}}
}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth;scroll-padding-top:1.5rem}}
body{{margin:0;background:var(--paper);color:var(--ink);
  font-family:var(--font-body);font-size:17px;line-height:1.65;
  -webkit-text-size-adjust:100%}}
.wrap{{max-width:68rem;margin:0 auto;padding:0 16px 6rem;
  display:grid;grid-template-columns:1fr;gap:0 2.5rem}}
header.top{{grid-column:1/-1;padding:3.5rem 0 1.5rem;
  border-bottom:1px solid var(--rule)}}
header.top .kicker{{font-family:var(--font-mono);font-size:12px;letter-spacing:.14em;
  text-transform:uppercase;color:var(--muted);margin:0 0 .6rem}}
header.top h1{{font-size:clamp(30px,5vw,44px);line-height:1.1;letter-spacing:-.02em;
  margin:0 0 .5rem}}
header.top p{{max-width:var(--measure);color:var(--muted);margin:0}}
nav.toc{{display:none}}
/* Prose keeps a readable line; a table and a code block may use the column. */
main{{min-width:0;padding-top:2rem}}
main>p,main>ul,main>ol,main>blockquote,main>h1,main>h2,main>h3,main>h4{{
  max-width:var(--measure)}}
main>h2:first-of-type{{margin-top:1.2rem}}
h2{{font-size:1.6rem;line-height:1.2;letter-spacing:-.015em;
  margin:3.2rem 0 .8rem;padding-top:.6rem;border-top:2px solid var(--blue)}}
h3{{font-size:1.15rem;margin:2.2rem 0 .6rem;letter-spacing:-.01em}}
h4{{font-size:.82rem;text-transform:uppercase;letter-spacing:.1em;
  color:var(--muted);margin:1.8rem 0 .4rem}}
p,ul,ol{{margin:0 0 1rem}}
li{{margin:.25rem 0}}
a{{color:var(--blue);text-underline-offset:2px}}
a:hover{{color:var(--orange)}}
strong{{font-weight:650}}
code{{font-family:var(--font-mono);font-size:.86em;background:var(--code);
  border-radius:5px;padding:.12em .35em;word-break:break-word}}
pre{{background:var(--card);border:1px solid var(--rule);border-radius:10px;
  padding:14px 16px;overflow-x:auto;margin:0 0 1.2rem}}
pre code{{background:none;padding:0;font-size:.85em;line-height:1.5}}
blockquote{{margin:0 0 1rem;padding-left:1rem;border-left:3px solid var(--yellow);
  color:var(--muted)}}
hr{{border:0;border-top:1px solid var(--rule);margin:2.5rem 0}}
.tablewrap{{overflow-x:auto;margin:0 0 1.4rem;max-width:100%}}
table{{border-collapse:collapse;font-size:.88rem;min-width:100%}}
th,td{{text-align:left;vertical-align:top;padding:.5rem .7rem;
  border-bottom:1px solid var(--rule)}}
th{{font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;
  color:var(--muted);font-weight:650;white-space:nowrap}}
td:first-child{{white-space:nowrap;color:var(--muted)}}
footer{{grid-column:1/-1;margin-top:4rem;padding-top:1.2rem;
  border-top:1px solid var(--rule);color:var(--muted);font-size:.85rem}}
@media (min-width:60rem){{
  .wrap{{grid-template-columns:15.5rem minmax(0,1fr)}}
  nav.toc{{display:block;position:sticky;top:0;align-self:start;
    max-height:100vh;overflow-y:auto;padding:2rem 0 3rem;font-size:.86rem}}
  nav.toc h2{{font-size:.72rem;text-transform:uppercase;letter-spacing:.1em;
    color:var(--muted);border:0;margin:0 0 .6rem;padding:0}}
  nav.toc ol{{list-style:none;margin:0;padding:0}}
  nav.toc li{{margin:0}}
  nav.toc a{{display:block;padding:.2rem 0 .2rem .6rem;color:var(--ink);
    text-decoration:none;border-left:2px solid var(--rule)}}
  nav.toc a:hover{{color:var(--blue);border-left-color:var(--blue)}}
  nav.toc .lvl3 a{{padding-left:1.4rem;color:var(--muted);font-size:.95em}}
}}
@media print{{
  :root{{--paper:#FFFFFF;--ink:#000000;--muted:#444444;--rule:#BBBBBB;
    --card:#FFFFFF;--code:#FFFFFF;--blue:#000000;--measure:100%}}
  nav.toc{{display:none}}
  .wrap{{display:block;max-width:none;padding:0}}
  main{{max-width:none;padding-top:0}}
  body{{font-size:10.5pt}}
  h2{{border-top-width:1px;page-break-after:avoid}}
  h3,h4{{page-break-after:avoid}}
  pre,table,blockquote{{page-break-inside:avoid}}
  a{{text-decoration:none}}
  main a[href^="http"]::after{{content:" (" attr(href) ")";font-size:.82em;
    word-break:break-all;color:#444444}}
}}
"""


# The markers are scaffolding for the Markdown, not content: the page renders
# with raw HTML off, so they would otherwise print as escaped text.
MARKER = re.compile(r"^<!-- /?generated:.*-->\n?", re.M)


# A relative link in the Markdown points at a neighbour in docs/. The page is
# published alone at the root of the site, where that neighbour does not
# exist, so every one of them becomes the file on GitHub instead of a 404.
RELATIVE = re.compile(r'href="(?!https?:|#|mailto:)([^"]+)"')


def page(md_text: str, site: str, repo: str) -> str:
    """The whole syllabus as one file: no script, no request off this origin."""
    body, toc = render(MARKER.sub("", md_text))
    blob = repo.rstrip("/") + "/blob/main/docs/"
    body = RELATIVE.sub(lambda m: f'href="{blob}{m.group(1)}"', body)
    body = body.replace("<table>", '<div class="tablewrap"><table>')
    body = body.replace("</table>", "</table></div>")
    # The first heading and the paragraph under it become the masthead, so the
    # page opens like a course sheet rather than like a rendered README.
    first = re.search(r"<h1[^>]*>(.*?)</h1>\s*<p>(.*?)</p>", body, re.S)
    title = re.sub("<[^>]+>", "", first.group(1)).strip() if first else "Syllabus"
    standfirst = first.group(2).strip() if first else ""
    body = body[first.end() :] if first else body
    items = "\n".join(
        f'<li class="lvl{level}"><a href="#{anchor}">{html.escape(text)}</a></li>'
        for level, anchor, text in toc
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="The written version of Vibe Code Camp: \
every evening, every stop, every command.">
<link rel="canonical" href="{html.escape(site)}syllabus.html">
<style>{css(palette())}</style>
</head>
<body>
<div class="wrap">
<header class="top">
<p class="kicker">Vibe Code Camp</p>
<h1>{html.escape(title)}</h1>
<p>{standfirst}</p>
</header>
<nav class="toc" aria-label="Contents">
<h2>Contents</h2>
<ol>
{items}
</ol>
</nav>
<main>
{body}
</main>
<footer>
<p>Generated from <code>docs/SYLLABUS.md</code> and <code>vibemap/data/</code> by
<code>tools/gen_syllabus.py</code>. Never hand-edited.
<a href="{html.escape(site)}">Play the game</a>.</p>
</footer>
</div>
</body>
</html>
"""


def outputs() -> tuple[str, str]:
    """What both files should hold right now."""
    md_text = sync(MD.read_text(encoding="utf-8"))
    cfg = Config.load(project.nearest_config(ROOT)).game
    site = cfg.site_url if cfg.site_url.endswith("/") else cfg.site_url + "/"
    return md_text, page(md_text, site, cfg.repo_url)


def main() -> None:
    md_text, html_text = outputs()
    if "--check" in sys.argv:
        stale = [
            path.relative_to(ROOT)
            for path, want in ((MD, md_text), (OUT, html_text))
            if not path.exists() or path.read_text(encoding="utf-8") != want
        ]
        if stale:
            names = ", ".join(str(p) for p in stale)
            print(f"{names} is stale; run: just syllabus")
            sys.exit(1)
        print("syllabus OK")
        return
    MD.write_text(md_text, encoding="utf-8")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html_text, encoding="utf-8")
    print(f"wrote {MD.relative_to(ROOT)} and {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
