"""The live world feed: real organisations, people and projects, by name only.

`vibe news` pulls every source in `vibemap/data/sources.json` (or the feeds a
camp lists in `config/camp.toml`), keeps the newest items, writes
`data/news.json` for the game and a dated `News` note in the vault. A daily
GitHub Action runs the same command, so a hosted game refreshes itself.

A summary is the feed's own description with the markup stripped and the tail
cut off. Nothing here is written by a model and nothing is attributed to a
person that they did not publish themselves: see
`docs/adr/0010-real-names-and-live-content.md`. Only the standard library:
RSS 2.0 and Atom are both small enough to parse by hand.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ATOM = "{http://www.w3.org/2005/Atom}"
USER_AGENT = "vibe-map (+https://github.com/tpetedb/vibe-map)"

# The registry and the file the game reads both carry a version: an unknown
# one is refused with the number in the message, never guessed at.
SOURCES_VERSION = 1
FEED_VERSION = 2
SOURCES_PATH = Path(__file__).resolve().parent / "data" / "sources.json"

SUMMARY_CHARS = 220
# A headline and a publisher name are one line each; a feed that sends more
# is cut here rather than in the card.
TITLE_CHARS = 160
NAME_CHARS = 80
KINDS = ("organisation", "person", "project")
ITEM_KINDS = ("release", "post", "talk")


@dataclass(frozen=True, slots=True)
class Source:
    """One feed in the registry: who publishes it and why it is trusted."""

    id: str
    kind: str  # organisation | person | project
    name: str
    url: str
    publisher: str
    trust: str
    building: str = ""
    tags: tuple[str, ...] = ()
    # A high volume feed would fill the card on its own; 0 means the run's cap.
    cap: int = 0

    @property
    def item_kind(self) -> str:
        """A releases feed yields releases; everything else yields posts."""
        return "release" if self.url.endswith("releases.atom") else "post"


@dataclass(frozen=True, slots=True)
class Item:
    id: str  # stable across runs: the link, hashed
    source: str  # the source id
    name: str  # the organisation or person, as it is shown
    kind: str  # release | post | talk
    title: str
    link: str
    date: str  # ISO 8601, UTC, or "" when the feed gave none
    summary: str = ""
    tags: tuple[str, ...] = ()


class SourcesError(ValueError):
    """The registry is unreadable or of a version this release does not know."""


def load_sources(path: Path = SOURCES_PATH) -> tuple[Source, ...]:
    """The registry, validated. A bad entry names itself and stops the run."""
    data = json.loads(path.read_text(encoding="utf-8"))
    version = data.get("version")
    if version != SOURCES_VERSION:
        raise SourcesError(
            f"{path.name}: version {version!r}, this release reads "
            f"{SOURCES_VERSION}. Upgrade vibe-map or check the file out again."
        )
    out: list[Source] = []
    seen: set[str] = set()
    for raw in data.get("sources", []):
        missing = [
            k
            for k in ("id", "kind", "name", "url", "publisher", "trust")
            if not raw.get(k)
        ]
        if missing:
            raise SourcesError(
                f"{path.name}: source {raw.get('id', '?')!r} is missing "
                + ", ".join(missing)
            )
        if raw["kind"] not in KINDS:
            raise SourcesError(
                f"{path.name}: source {raw['id']!r} has kind {raw['kind']!r}, "
                f"expected one of {', '.join(KINDS)}"
            )
        if not raw["url"].startswith("https://"):
            raise SourcesError(f"{path.name}: source {raw['id']!r} is not https")
        if raw["id"] in seen:
            raise SourcesError(f"{path.name}: source {raw['id']!r} appears twice")
        seen.add(raw["id"])
        out.append(
            Source(
                id=raw["id"],
                kind=raw["kind"],
                name=raw["name"],
                url=raw["url"],
                publisher=raw["publisher"],
                trust=raw["trust"],
                building=raw.get("building", ""),
                tags=tuple(raw.get("tags", ())),
                cap=int(raw.get("cap", 0)),
            )
        )
    if not out:
        raise SourcesError(f"{path.name}: no sources")
    return tuple(out)


def source_name(url: str) -> str:
    host = urlparse(url).netloc.removeprefix("www.")
    return host or url


def source_for_url(url: str) -> Source:
    """A camp's own feed from config/camp.toml, which carries no provenance."""
    host = source_name(url)
    return Source(
        id=host,
        kind="organisation",
        name=host,
        url=url,
        publisher=host,
        trust="Listed in config/camp.toml by the owner of this camp.",
    )


def item_id(link: str) -> str:
    """Stable across runs and across sources, so the game can remember one."""
    return hashlib.sha1(link.encode("utf-8"), usedforsecurity=False).hexdigest()[:12]


# A tag opens with a letter, a slash, a bang or a question mark; "a < b" is
# arithmetic. What is left of either bracket after the strip goes too.
_TAGS = re.compile(r"<[A-Za-z/!?][^<>]*>")
_BRACKETS = re.compile(r"[<>]")
_SPACE = re.compile(r"\s+")


def plain(raw: str, *, limit: int = SUMMARY_CHARS) -> str:
    """A feed's own words as text: entities resolved, markup out, tail cut.

    Never generated. A feed is somebody else's machine, so nothing it sends
    may reach the page as markup: the entities are resolved first, so an
    escaped tag cannot survive the strip, and the strip runs until nothing is
    left to remove. A tag the feed never closed, or a comment opener, is
    markup to whatever reads the text next (the script element the build
    writes it into, the vault note Obsidian renders), so no angle bracket is
    left at all. A cut lands on a word boundary so the sentence reads as an
    opening rather than as a broken word.
    """
    text = html.unescape(raw or "")
    while True:
        stripped = _TAGS.sub(" ", text)
        if stripped == text:
            break
        text = stripped
    text = _BRACKETS.sub(" ", text)
    text = _SPACE.sub(" ", text).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0].rstrip(" ,;:.")
    return (cut or text[:limit].rstrip()) + "..."


_LINK_UNSAFE = frozenset("<>()[]\"'`\\")


def safe_link(url: str) -> str:
    """The item's link, or "" when it is not an absolute http or https URL.

    A card renders a link as an anchor, so a `javascript:` or `data:` link in
    a feed is script injection. An item without a usable link is dropped.
    """
    link = (url or "").strip()
    parts = urlparse(link)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        return ""
    # The link is written into a Markdown link and an href. The characters
    # that end either one are encoded, which a URL allows and no server minds.
    return "".join(
        f"%{ord(c):02X}" if c in _LINK_UNSAFE or c <= " " or c == "\x7f" else c
        for c in link
    )


def _text(el: ET.Element | None) -> str:
    return (el.text or "").strip() if el is not None else ""


def _date(raw: str) -> str:
    raw = raw.strip()
    if not raw:
        return ""
    try:
        dt = parsedate_to_datetime(raw)
    except (TypeError, ValueError):
        try:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _item(src: Source, title: str, link: str, when: str, body: str) -> Item:
    """One item, sanitised: the game is handed text and a checked link."""
    return Item(
        id=item_id(link),
        source=src.id,
        name=plain(src.name, limit=NAME_CHARS),
        kind=src.item_kind,
        title=plain(title, limit=TITLE_CHARS),
        link=safe_link(link),
        date=_date(when),
        summary=plain(body),
        tags=src.tags,
    )


def parse(xml: bytes | str, src: Source | str, *, limit: int = 8) -> list[Item]:
    """Items from an RSS 2.0 or Atom document; unknown shapes give nothing."""
    if isinstance(src, str):
        src = Source(src, "organisation", src, "", src, "ad hoc")
    root = ET.fromstring(xml)
    items: list[Item] = []
    for it in root.iter("item"):
        title, link = _text(it.find("title")), safe_link(_text(it.find("link")))
        if title and link:
            items.append(
                _item(
                    src,
                    title,
                    link,
                    _text(it.find("pubDate")),
                    _text(it.find("description")),
                )
            )
    if not items:
        for en in root.iter(f"{ATOM}entry"):
            title = _text(en.find(f"{ATOM}title"))
            link_el = en.find(f"{ATOM}link[@rel='alternate']")
            if link_el is None:
                link_el = en.find(f"{ATOM}link")
            link = safe_link(link_el.get("href") or "") if link_el is not None else ""
            when = _text(en.find(f"{ATOM}published")) or _text(
                en.find(f"{ATOM}updated")
            )
            body = _text(en.find(f"{ATOM}summary")) or _text(en.find(f"{ATOM}content"))
            if title and link:
                items.append(_item(src, title, link, when, body))
    return items[:limit]


def fetch_one(src: Source, *, limit: int = 8, timeout: int = 20) -> list[Item]:
    req = Request(src.url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as r:  # noqa: S310 (feeds are config)
        return parse(r.read(), src, limit=limit)


# ---- is the feed still there --------------------------------------------------
# Two facts a liveness check must not confuse: a feed that answers and still
# parses is alive, and a feed with items today is fresh. A digest rests between
# announcements (arXiv announces Sunday to Thursday and declares the gap in its
# own skipDays), so only the first is a fault.

FEED_ROOTS = ("rss", f"{ATOM}feed")


@dataclass(frozen=True, slots=True)
class Liveness:
    """What one source answered, and what was wrong when it did not."""

    source: str  # the source id
    url: str
    alive: bool
    entries: int = 0  # item or entry elements in the document
    items: int = 0  # how many of them this parser understood
    fault: str = ""  # why it is not alive; empty when it is

    @property
    def fresh(self) -> bool:
        """It had something to say today. Quiet is weather, not death."""
        return self.items > 0

    def __str__(self) -> str:
        """The line a failing check prints: the feed, the URL, what was wrong."""
        head = f"{self.source} ({self.url})"
        if not self.alive:
            return f"{head}: {self.fault}"
        if not self.fresh:
            return f"{head}: alive, nothing published yet today"
        return f"{head}: alive, {self.items} of {self.entries} entries read"


def liveness(src: Source, body: bytes | str) -> Liveness:
    """Read what a feed answered: is this still a feed this parser knows?

    Dead is a body that is not XML, XML that is not a feed, or a feed whose
    entries none of the parser's fields fit, which is how a changed format
    looks from out here. An empty feed is not dead: it has nothing to announce
    today, and a digest between announcements looks exactly like this.
    """
    try:
        root = ET.fromstring(body)
    except ET.ParseError as e:
        return Liveness(src.id, src.url, False, fault=f"not XML: {str(e)[:100]}")
    if root.tag not in FEED_ROOTS:
        return Liveness(
            src.id,
            src.url,
            False,
            fault=f"not a feed: the root element is {root.tag!r}",
        )
    entries = sum(1 for _ in root.iter("item"))
    entries += sum(1 for _ in root.iter(f"{ATOM}entry"))
    items = len(parse(body, src, limit=entries))
    if entries and not items:
        return Liveness(
            src.id,
            src.url,
            False,
            entries,
            0,
            fault=(
                f"format changed: {entries} entries, none of them with a "
                "title and a link this parser could read"
            ),
        )
    return Liveness(src.id, src.url, True, entries, items)


def check_one(src: Source, *, timeout: int = 20) -> Liveness:
    """Ask one feed whether it is still there; one step of the nightly check."""
    req = Request(src.url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(req, timeout=timeout) as r:  # noqa: S310 (feeds are config)
            body = r.read()
    except Exception as e:  # reason: a feed that will not answer is the answer
        return Liveness(
            src.id, src.url, False, fault=f"{type(e).__name__}: {str(e)[:120]}"
        )
    return liveness(src, body)


def fetch(
    sources: tuple[Source, ...] | None = None, *, per_feed: int = 8
) -> tuple[list[Item], list[str]]:
    """Every source, newest first, deduplicated by link; failures are reported.

    One dead feed must not stop the rest: the world keeps turning without it
    and the note says which one was quiet.
    """
    if sources is None:
        sources = load_sources()
    out: list[Item] = []
    problems: list[str] = []
    for src in sources:
        try:
            out += fetch_one(src, limit=src.cap or per_feed)
        except Exception as e:  # reason: one dead feed must not stop the rest
            problems.append(f"{src.name}: {type(e).__name__}: {str(e)[:80]}")
    seen: set[str] = set()
    unique = []
    for it in sorted(out, key=lambda i: i.date, reverse=True):
        if it.link not in seen:
            seen.add(it.link)
            unique.append(it)
    return unique, problems


def payload(items: list[Item]) -> dict[str, object]:
    """What both the file and the baked constant carry, in one shape."""
    return {
        "version": FEED_VERSION,
        "fetched_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "items": [{**asdict(i), "tags": list(i.tags)} for i in items],
    }


def write_json(items: list[Item], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload(items), indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def note_body(items: list[Item], problems: list[str]) -> str:
    """The vault note: newest first, grouped by day, one line per item."""
    lines = [
        "What the organisations, projects and people in "
        "`vibemap/data/sources.json` published lately, pulled by `vibe news`. "
        "A daily action does the same on GitHub, so the hosted game and this "
        "note keep up without you. Every summary is the feed's own wording, "
        "cut short; nothing here is written for them.",
        "",
    ]
    day = None
    for it in items:
        d = it.date[:10] or "undated"
        if d != day:
            lines += [f"## {d}", ""]
            day = d
        lines.append(f"- [{it.title}]({it.link}) ({it.name})")
        if it.summary:
            lines.append(f"  - {it.summary}")
    if problems:
        lines += ["", "## Feeds that did not answer", ""] + [f"- {p}" for p in problems]
    lines += ["", "Back to [[Tonight]] · [[Resources]]", "", "#concept"]
    return "\n".join(lines)
