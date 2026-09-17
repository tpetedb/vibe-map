"""The news feed: RSS and Atom parse, dates normalise, files and note are written."""

from __future__ import annotations

import json
from pathlib import Path

from vibemap import news

RSS = b"""<?xml version="1.0"?><rss version="2.0"><channel><title>t</title>
<item><title>Second</title><link>https://x.test/2</link>
<pubDate>Tue, 16 Sep 2026 10:00:00 GMT</pubDate></item>
<item><title>First</title><link>https://x.test/1</link>
<pubDate>Mon, 15 Sep 2026 10:00:00 +0200</pubDate></item>
</channel></rss>"""

ATOM = b"""<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom"><title>a</title>
<entry><title>Release v2.1.274</title><link rel="alternate" href="https://y.test/r"/><updated>2026-09-17T01:02:03Z</updated></entry>
<entry><title>No link</title></entry>
</feed>"""


def test_rss_and_atom_parse_with_utc_dates() -> None:
    rss = news.parse(RSS, "x")
    assert [i.title for i in rss] == ["Second", "First"]
    assert rss[0].date == "2026-09-16T10:00:00Z"
    assert rss[1].date == "2026-09-15T08:00:00Z"
    atom = news.parse(ATOM, "y")
    assert len(atom) == 1 and atom[0].link == "https://y.test/r"
    assert atom[0].date == "2026-09-17T01:02:03Z"


def test_fetch_merges_sorts_and_reports_dead_feeds(tmp_path: Path) -> None:
    a, b = tmp_path / "a.xml", tmp_path / "b.xml"
    a.write_bytes(RSS)
    b.write_bytes(ATOM)
    feeds = (
        ("A", a.as_uri()),
        ("B", b.as_uri()),
        ("Dead", (tmp_path / "no.xml").as_uri()),
    )
    items, problems = news.fetch(feeds)
    assert [i.title for i in items] == ["Release v2.1.274", "Second", "First"]
    assert len(problems) == 1 and problems[0].startswith("Dead:")


def test_json_and_note_are_written(tmp_path: Path) -> None:
    items = news.parse(RSS, "x")
    news.write_json(items, tmp_path / "data" / "news.json")
    data = json.loads((tmp_path / "data" / "news.json").read_text())
    assert data["items"][0]["title"] == "Second" and data["fetched_at"].endswith("Z")
    body = news.note_body(items, ["Dead: boom"])
    assert "## 2026-09-16" in body and "[Second](https://x.test/2) (x)" in body
    assert "Feeds that did not answer" in body and "[[Tonight]]" in body
