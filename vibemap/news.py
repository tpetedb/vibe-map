"""AI news from a handful of feeds, so the game stays current after launch.

`vibe news` pulls the feeds listed in vibe.toml ([news] feeds), keeps the
newest items, writes `data/news.json` for the game's News card and a dated
`News` note in the vault. A weekly GitHub Action runs the same command and
commits the result, so a hosted game refreshes itself. Only the standard
library: RSS 2.0 and Atom are both small enough to parse by hand.
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ATOM = "{http://www.w3.org/2005/Atom}"
USER_AGENT = "vibe-map (+https://github.com/tpetedb/vibe-map)"

# Verified on 2026-09-17: each answers with RSS or Atom. Anthropic publishes no feed.
DEFAULT_FEEDS: tuple[tuple[str, str], ...] = (
    ("OpenAI news", "https://openai.com/news/rss.xml"),
    ("Hugging Face blog", "https://huggingface.co/blog/feed.xml"),
    ("Simon Willison", "https://simonwillison.net/atom/everything/"),
    ("Claude Code releases", "https://github.com/anthropics/claude-code/releases.atom"),
    ("GitHub changelog", "https://github.blog/changelog/feed/"),
    ("arXiv cs.AI", "https://rss.arxiv.org/rss/cs.AI"),
)


@dataclass(frozen=True, slots=True)
class Item:
    source: str
    title: str
    link: str
    date: str  # ISO 8601, UTC, or "" when the feed gave none


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


def parse(xml: bytes | str, source: str, *, limit: int = 8) -> list[Item]:
    """Items from an RSS 2.0 or Atom document; unknown shapes give nothing."""
    root = ET.fromstring(xml)
    items: list[Item] = []
    for it in root.iter("item"):
        title, link = _text(it.find("title")), _text(it.find("link"))
        if title and link:
            items.append(Item(source, title, link, _date(_text(it.find("pubDate")))))
    if not items:
        for en in root.iter(f"{ATOM}entry"):
            title = _text(en.find(f"{ATOM}title"))
            link_el = en.find(f"{ATOM}link[@rel='alternate']")
            if link_el is None:
                link_el = en.find(f"{ATOM}link")
            link = (link_el.get("href") or "").strip() if link_el is not None else ""
            when = _text(en.find(f"{ATOM}published")) or _text(
                en.find(f"{ATOM}updated")
            )
            if title and link:
                items.append(Item(source, title, link, _date(when)))
    return items[:limit]


def fetch_one(name: str, url: str, *, limit: int = 8, timeout: int = 20) -> list[Item]:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as r:  # noqa: S310 (feeds are config)
        return parse(r.read(), name, limit=limit)


def fetch(
    feeds: tuple[tuple[str, str], ...] = DEFAULT_FEEDS, *, per_feed: int = 8
) -> tuple[list[Item], list[str]]:
    """All feeds, newest first, deduplicated by link; failures reported, not raised."""
    out: list[Item] = []
    problems: list[str] = []
    for name, url in feeds:
        try:
            out += fetch_one(name, url, limit=per_feed)
        except Exception as e:  # reason: one dead feed must not stop the rest
            problems.append(f"{name}: {type(e).__name__}: {str(e)[:80]}")
    seen: set[str] = set()
    unique = []
    for it in sorted(out, key=lambda i: i.date, reverse=True):
        if it.link not in seen:
            seen.add(it.link)
            unique.append(it)
    return unique, problems


def source_name(url: str) -> str:
    host = urlparse(url).netloc.removeprefix("www.")
    return host or url


def write_json(items: list[Item], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "fetched_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "items": [asdict(i) for i in items],
    }
    path.write_text(
        json.dumps(payload, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def note_body(items: list[Item], problems: list[str]) -> str:
    """The vault note: newest first, grouped by day, one line per item."""
    lines = [
        "What happened in AI lately, pulled from the feeds in `vibe.toml` by "
        "`vibe news`. A weekly action does the same on GitHub, so the hosted "
        "game and this note keep up without you.",
        "",
    ]
    day = None
    for it in items:
        d = it.date[:10] or "undated"
        if d != day:
            lines += [f"## {d}", ""]
            day = d
        lines.append(f"- [{it.title}]({it.link}) ({it.source})")
    if problems:
        lines += ["", "## Feeds that did not answer", ""] + [f"- {p}" for p in problems]
    lines += ["", "Back to [[Tonight]] · [[Resources]]", "", "#concept"]
    return "\n".join(lines)
