"""The world feed: the registry, the parse, the summaries, the files.

Every fixture under tests/fixtures/feeds/ is a snippet of the real feed it is
named after, cut to two items. The battery never touches the network: a live
check of every URL in the registry lives at the bottom, marked integration.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from vibemap import news

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "feeds"

RSS = b"""<?xml version="1.0"?><rss version="2.0"><channel><title>t</title>
<item><title>Second</title><link>https://x.test/2</link>
<description>&lt;p&gt;Second body.&lt;/p&gt;</description>
<pubDate>Tue, 16 Sep 2026 10:00:00 GMT</pubDate></item>
<item><title>First</title><link>https://x.test/1</link>
<pubDate>Mon, 15 Sep 2026 10:00:00 +0200</pubDate></item>
</channel></rss>"""

ATOM = b"""<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom"><title>a</title>
<entry><title>Release v2.1.274</title><link rel="alternate" href="https://y.test/r"/><updated>2026-09-17T01:02:03Z</updated></entry>
<entry><title>No link</title></entry>
</feed>"""

APPLE = news.Source(
    id="apple-developer-news",
    kind="organisation",
    name="Apple Developer News",
    url="https://developer.apple.com/news/rss/news.rss",
    publisher="Apple Inc.",
    trust="First-party.",
    building="apple",
    tags=("code",),
)
UV = news.Source(
    id="uv-releases",
    kind="project",
    name="uv releases",
    url="https://github.com/astral-sh/uv/releases.atom",
    publisher="Astral Software Inc.",
    trust="First-party.",
    building="toolshed",
    tags=("code",),
)


def fixture(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


# ---- the registry -------------------------------------------------------------


def test_registry_loads_and_every_source_carries_its_provenance() -> None:
    sources = news.load_sources()
    assert len(sources) >= 20
    assert len({s.id for s in sources}) == len(sources)
    for s in sources:
        assert s.kind in news.KINDS, s.id
        assert s.url.startswith("https://"), s.id
        assert s.publisher and s.trust, s.id
        assert s.building, s.id
        assert s.tags, s.id
    # The people and organisations the course names have to be in here by name.
    names = " ".join(s.name for s in sources)
    for who in ("Apple", "Microsoft", "Python", "Markus Winand", "DuckDB"):
        assert who in names


def test_registry_shelf_tags_are_tech_tree_categories() -> None:
    from vibemap.tech import CATEGORIES

    shelves = {c[0] for c in CATEGORIES}
    for s in news.load_sources():
        assert set(s.tags) <= shelves, (s.id, s.tags)


def test_a_registry_of_an_unknown_version_is_refused(tmp_path: Path) -> None:
    p = tmp_path / "sources.json"
    p.write_text(json.dumps({"version": 99, "sources": []}))
    with pytest.raises(news.SourcesError) as e:
        news.load_sources(p)
    assert "99" in str(e.value)


@pytest.mark.parametrize(
    ("broken", "says"),
    [
        ({"id": "x", "kind": "organisation", "name": "X", "url": "https://x/f"}, "x"),
        (
            {
                "id": "y",
                "kind": "robot",
                "name": "Y",
                "url": "https://y/f",
                "publisher": "Y",
                "trust": "t",
            },
            "robot",
        ),
        (
            {
                "id": "z",
                "kind": "person",
                "name": "Z",
                "url": "http://z/f",
                "publisher": "Z",
                "trust": "t",
            },
            "https",
        ),
    ],
)
def test_a_broken_source_names_itself(
    tmp_path: Path, broken: dict[str, str], says: str
) -> None:
    p = tmp_path / "sources.json"
    p.write_text(json.dumps({"version": 1, "sources": [broken]}))
    with pytest.raises(news.SourcesError) as e:
        news.load_sources(p)
    assert says in str(e.value)


# ---- parsing ------------------------------------------------------------------


def test_rss_and_atom_parse_with_utc_dates() -> None:
    rss = news.parse(RSS, "x")
    assert [i.title for i in rss] == ["Second", "First"]
    assert rss[0].date == "2026-09-16T10:00:00Z"
    assert rss[1].date == "2026-09-15T08:00:00Z"
    atom = news.parse(ATOM, "y")
    assert len(atom) == 1 and atom[0].link == "https://y.test/r"
    assert atom[0].date == "2026-09-17T01:02:03Z"


def test_an_item_carries_its_source_kind_and_shelf_tags() -> None:
    post = news.parse(fixture("apple-developer-news.xml"), APPLE)[0]
    assert post.source == "apple-developer-news"
    assert post.name == "Apple Developer News"
    assert post.kind == "post" and post.tags == ("code",)
    assert post.title and post.link.startswith("https://developer.apple.com/")
    release = news.parse(fixture("uv-releases.atom"), UV)[0]
    assert release.kind == "release" and release.source == "uv-releases"


def test_an_item_id_is_stable_and_follows_the_link() -> None:
    one = news.parse(fixture("lwn-headlines.xml"), APPLE)
    two = news.parse(fixture("lwn-headlines.xml"), UV)
    assert [i.id for i in one] == [i.id for i in two]
    assert one[0].id == news.item_id(one[0].link)


def test_a_summary_is_the_feeds_own_words_without_markup() -> None:
    apple = news.parse(fixture("apple-developer-news.xml"), APPLE)[0]
    assert apple.summary and "<" not in apple.summary
    assert "  " not in apple.summary
    assert len(apple.summary) <= news.SUMMARY_CHARS + 3
    # A body longer than the cap ends in an ellipsis on a word boundary.
    lwn = news.parse(fixture("lwn-headlines.xml"), APPLE)[0]
    assert lwn.summary.startswith("Version 5.6 of the Systemtap")
    long = news.plain("<p>" + "word " * 200 + "</p>")
    assert long.endswith("...") and " wor..." not in long


def test_a_summary_of_a_short_body_is_left_whole() -> None:
    assert news.plain("<b>Short.</b> Two sentences.") == "Short. Two sentences."
    assert news.plain("") == ""


# ---- what a hostile feed cannot do -------------------------------------------
# The feeds are other people's machines and the card renders what they send,
# so the writer hands the game plain text and a link a browser may follow.


def test_markup_never_survives_a_field() -> None:
    assert news.plain('<img src=x onerror="alert(1)">Title') == "Title"
    # Escaped markup is unescaped first, so an escaped tag is stripped too and
    # what it wrapped stays behind as the words it always was.
    assert news.plain("&lt;script&gt;alert(1)&lt;/script&gt;Hi") == "alert(1) Hi"
    # A tag nested inside a tag is stripped until no angle bracket is left,
    # so a strip that opens a new tag cannot leave one behind.
    assert "<" not in news.plain("<<b>b>bold</<b>b>")
    assert "&" in news.plain("Odd &amp; even")


def test_a_title_and_a_name_are_stripped_and_capped() -> None:
    src = news.Source(
        "hostile",
        "organisation",
        "Odd & <b>bold</b> name",
        "https://x.test/f.xml",
        "x.test",
        "test",
    )
    xml = (
        "<rss><channel><item>"
        '<title>&lt;img src=x onerror="window.pwned=1"&gt;' + "T" * 300 + "</title>"
        "<link>https://x.test/p</link>"
        "<description>&lt;b&gt;Body&lt;/b&gt;</description>"
        "</item></channel></rss>"
    )
    item = news.parse(xml, src)[0]
    assert "<" not in item.title and "onerror" not in item.title
    assert len(item.title) <= news.TITLE_CHARS + 3
    assert item.name == "Odd & bold name"
    assert item.summary == "Body"


def test_a_link_that_is_not_http_drops_the_item() -> None:
    assert news.safe_link("javascript:alert(1)") == ""
    assert news.safe_link("data:text/html,<script>") == ""
    assert news.safe_link("/relative/path") == ""
    assert news.safe_link(" https://x.test/p ") == "https://x.test/p"
    xml = (
        "<rss><channel>"
        "<item><title>Bad</title><link>javascript:alert(1)</link></item>"
        "<item><title>Good</title><link>https://x.test/p</link></item>"
        "</channel></rss>"
    )
    items = news.parse(xml, APPLE)
    assert [i.title for i in items] == ["Good"]


def test_every_fixture_parses_into_items() -> None:
    for f in sorted(FIXTURES.iterdir()):
        items = news.parse(f.read_bytes(), APPLE)
        assert items, f.name
        assert all(i.title and i.link for i in items), f.name


# ---- fetching, writing --------------------------------------------------------


def test_fetch_merges_sorts_caps_and_reports_dead_feeds(tmp_path: Path) -> None:
    a, b = tmp_path / "a.xml", tmp_path / "b.xml"
    a.write_bytes(RSS)
    b.write_bytes(ATOM)
    sources = (
        news.Source("a", "organisation", "A", a.as_uri(), "A", "test"),
        news.Source("b", "project", "B", b.as_uri(), "B", "test"),
        news.Source("dead", "person", "Dead", (tmp_path / "no.xml").as_uri(), "D", "t"),
    )
    items, problems = news.fetch(sources)
    assert [i.title for i in items] == ["Release v2.1.274", "Second", "First"]
    assert len(problems) == 1 and problems[0].startswith("Dead:")
    # The same link from two sources is one item.
    twice = news.fetch((sources[0], sources[0]))[0]
    assert len(twice) == 2
    # A source with its own cap keeps to it.
    capped = news.Source("a", "organisation", "A", a.as_uri(), "A", "test", cap=1)
    assert len(news.fetch((capped,))[0]) == 1


def test_json_carries_a_version_and_the_new_fields(tmp_path: Path) -> None:
    items = news.parse(fixture("apple-developer-news.xml"), APPLE)
    news.write_json(items, tmp_path / "data" / "news.json")
    data = json.loads((tmp_path / "data" / "news.json").read_text())
    assert data["version"] == news.FEED_VERSION and data["fetched_at"].endswith("Z")
    first = data["items"][0]
    assert {"id", "source", "name", "kind", "title", "link", "date", "summary"} <= set(
        first
    )
    assert first["tags"] == ["code"]


def test_note_body_names_the_publisher_and_the_quiet_feeds() -> None:
    items = news.parse(RSS, "x")
    body = news.note_body(items, ["Dead: boom"])
    assert "## 2026-09-16" in body and "[Second](https://x.test/2) (x)" in body
    assert "Second body." in body
    assert "Feeds that did not answer" in body and "[[Tonight]]" in body


def test_a_camp_feed_from_camp_toml_becomes_a_source() -> None:
    src = news.source_for_url("https://www.example.test/feed")
    assert src.id == "example.test" and src.kind == "organisation"
    assert "camp.toml" in src.trust


# ---- the live check, nightly only ---------------------------------------------


@pytest.mark.integration
def test_every_registered_feed_answers_and_parses() -> None:
    """The weekly liveness check. Not in the default battery: it needs network."""
    dead = []
    for src in news.load_sources():
        try:
            if not news.fetch_one(src, limit=1):
                dead.append(f"{src.id}: parsed, no items")
        except Exception as e:  # reason: report every dead feed, not the first
            dead.append(f"{src.id}: {type(e).__name__}: {str(e)[:120]}")
    assert not dead, "\n".join(dead)


@pytest.mark.parametrize(
    "raw",
    [
        "Notes <!-- <script x",
        "Half a tag <img src=x onerror=alert(1) ",
        "&lt;!--&lt;script ",
        "<<b>script>alert(1)<</b>/script>",
        "a < b and b > c",
    ],
)
def test_no_angle_bracket_survives_the_writer(raw: str) -> None:
    """A tag the feed never closes is still a tag to the browser that reads it."""
    out = news.plain(raw)
    assert "<" not in out and ">" not in out, out


def test_the_words_around_markup_survive() -> None:
    assert news.plain("a < b and b > c") == "a b and b c"
    assert news.plain("R&amp;D <b>ships</b> v2") == "R&D ships v2"
    # Escaped twice at the source: one level comes off, as text.
    assert news.plain("&amp;lt;b&amp;gt; tags") == "&lt;b&gt; tags"


def test_a_link_cannot_end_the_markdown_or_the_attribute_it_lands_in() -> None:
    link = news.safe_link('https://example.com/a_(b)?q="x"&r=<y> z')
    assert link == "https://example.com/a_%28b%29?q=%22x%22&r=%3Cy%3E%20z"
    assert news.safe_link("https:///no-host") == ""
    assert news.safe_link("HTTPS://Example.com/ok") == "HTTPS://Example.com/ok"
    for bad in [
        "javascript:alert(1)",
        " JaVaScRiPt:alert(1)",
        "data:text/html,x",
        "vbscript:x",
        "//example.com/x",
        "/relative",
        "java\\tscript:x",
    ]:
        assert news.safe_link(bad) == "", bad
