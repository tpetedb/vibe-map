"""The world feed: the registry, the parse, the summaries, the files.

Every fixture under tests/fixtures/feeds/ is a snippet of the real feed it is
named after, cut to two items. The battery never touches the network: a live
check of every URL in the registry lives at the bottom, marked integration.
"""

from __future__ import annotations

import http.server
import json
import socket
import threading
import warnings
from collections.abc import Callable, Iterator
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


# ---- liveness: answering is not the same as having news today ----------------
# Every case here is served by a local server, so the check is tested on what a
# server answers without a single packet leaving the machine.

# A daily digest between announcements: a whole feed, no items. arXiv declares
# the gap itself with skipDays, which is why its empty weekend is not death.
QUIET = b"""<?xml version="1.0"?><rss version="2.0"><channel>
<title>cs.AI updates on arXiv.org</title><link>https://x.test/</link>
<description>Announcements Sunday to Thursday.</description>
<skipDays><day>Saturday</day><day>Sunday</day></skipDays>
</channel></rss>"""

# The same, in Atom, with the self and alternate links a real feed carries:
# repeated metadata is not a renamed entry element.
QUIET_ATOM = b"""<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom">
<title>a</title><id>urn:x</id><updated>2026-09-19T00:00:00Z</updated>
<link rel="self" href="https://x.test/atom"/>
<link rel="alternate" href="https://x.test/"/>
</feed>"""

# A full feed the parser no longer understands: the elements it reads were
# renamed. This is what a changed format looks like from the outside.
RENAMED = b"""<?xml version="1.0"?><rss version="2.0"><channel><title>t</title>
<item><headline>Second</headline><url>https://x.test/2</url></item>
<item><headline>First</headline><url>https://x.test/1</url></item>
</channel></rss>"""

# The other half of a changed format: the entry element itself is renamed, so
# the parser counts no entries at all and the feed looks quiet. Three
# spellings, because a rename can drop the name, move it into a namespace or
# swap the Atom one.
RENAMED_ENTRY = {
    "an rss item called article": b"""<?xml version="1.0"?>
<rss version="2.0"><channel><title>t</title><link>https://x.test/</link>
<article><title>Second</title><link>https://x.test/2</link></article>
<article><title>First</title><link>https://x.test/1</link></article>
</channel></rss>""",
    "an rss item moved into a namespace": b"""<?xml version="1.0"?>
<rss version="2.0" xmlns:n="https://n.test/"><channel><title>t</title>
<n:item><title>Second</title><link>https://x.test/2</link></n:item>
<n:item><title>First</title><link>https://x.test/1</link></n:item>
</channel></rss>""",
    "an atom entry called post": b"""<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom"><title>a</title><id>urn:x</id>
<link rel="self" href="https://x.test/atom"/>
<post><title>Second</title><link rel="alternate" href="https://x.test/2"/></post>
<post><title>First</title><link rel="alternate" href="https://x.test/1"/></post>
</feed>""",
}

A_PAGE = b"<!DOCTYPE html><html><body><h1>This feed has moved.</h1></body></html>"
NOT_XML = b"<html><p>410 gone & nothing here"


@pytest.fixture
def serve_feed() -> Iterator[Callable[..., str]]:
    """A local server answering with exactly the body each test registers."""
    routes: dict[str, tuple[int, bytes]] = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 (the base class names it)
            status, body = routes.get(self.path, (404, b"no such feed"))
            self.send_response(status)
            self.send_header("Content-Type", "application/xml")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: object) -> None:  # noqa: A002
            pass

    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    host = f"http://127.0.0.1:{httpd.server_address[1]}"

    def serve(path: str, body: bytes = b"", status: int = 200) -> str:
        routes[path] = (status, body)
        return host + path

    try:
        yield serve
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=5)


def source_at(url: str, sid: str = "feed-under-test", rests: str = "") -> news.Source:
    return news.Source(
        sid, "organisation", "Feed under test", url, "x.test", "test", rests=rests
    )


DIGEST = "Announces Sunday to Thursday and says so in skipDays."


@pytest.mark.parametrize("body", [QUIET, QUIET_ATOM], ids=["rss", "atom"])
def test_a_feed_with_nothing_new_today_is_alive(
    serve_feed: Callable[..., str], body: bytes
) -> None:
    """The weekend case: the digest answered, it just has nothing to announce."""
    url = serve_feed("/quiet.xml", body)
    verdict = news.check_one(source_at(url, rests=DIGEST))
    assert verdict.alive and not verdict.fresh
    assert verdict.entries == 0 and verdict.items == 0 and not verdict.fault
    assert "nothing published" in str(verdict)


def test_an_empty_feed_from_a_source_that_never_rests_is_dead(
    serve_feed: Callable[..., str],
) -> None:
    """Twenty of the twenty-one keep a back catalogue: empty is a fault there.

    Only a source the registry says rests may answer with nothing, so the
    failure line says where to write that down.
    """
    url = serve_feed("/empty.xml", QUIET)
    verdict = news.check_one(source_at(url, "busy-feed"))
    assert not verdict.alive and "no entries at all" in verdict.fault
    assert "rests" in verdict.fault and "sources.json" in verdict.fault


@pytest.mark.parametrize("spelling", sorted(RENAMED_ENTRY))
def test_a_renamed_entry_element_is_dead_even_for_a_resting_source(
    serve_feed: Callable[..., str], spelling: str
) -> None:
    """A full feed the parser reads as empty is a format change, not a quiet day.

    The entry element itself carries the new name, so counting items and
    entries sees nothing; a run of the same unread child is what tells the two
    apart. The source rests here, so nothing but that run can catch it.
    """
    url = serve_feed("/renamed.xml", RENAMED_ENTRY[spelling])
    verdict = news.check_one(source_at(url, "renamed-feed", rests=DIGEST))
    assert not verdict.alive and not verdict.fresh
    line = str(verdict)
    assert "format changed" in line and "renamed-feed" in line and url in line


def test_repeated_metadata_is_not_read_as_entries_under_another_name(
    serve_feed: Callable[..., str],
) -> None:
    """The guard on the rule above: real feeds repeat links and categories.

    Every Atom release feed in the registry carries a self link and an
    alternate one, and Blogger lists every category of the blog in the
    channel, so a run of those must not read as a renamed entry element.
    """
    channel = b"""<?xml version="1.0"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>
<title>t</title><link>https://x.test/</link>
<category>a</category><category>b</category>
<atom:link rel="self" href="https://x.test/f"/>
<atom:link rel="hub" href="https://hub.test/"/>
</channel></rss>"""
    url = serve_feed("/busy-metadata.xml", channel)
    verdict = news.check_one(source_at(url, "quiet-feed", rests=DIGEST))
    assert verdict.alive and not verdict.fresh and not verdict.fault


def test_the_registry_says_which_source_rests_and_why() -> None:
    """A rest is data with its reason, like trust, and the digest is the one."""
    rests = {s.id: s.rests for s in news.load_sources() if s.rests}
    assert "arxiv-cs-ai" in rests
    for sid, why in rests.items():
        assert len(why) > 40, sid
    # A source that says nothing rests never: that is what keeps empty a fault.
    assert all(not s.rests for s in news.load_sources() if s.id != "arxiv-cs-ai")


def test_a_feed_with_items_is_alive_and_fresh(serve_feed: Callable[..., str]) -> None:
    url = serve_feed("/rss.xml", RSS)
    verdict = news.check_one(source_at(url))
    assert verdict.alive and verdict.fresh
    assert verdict.entries == 2 and verdict.items == 2 and not verdict.fault


@pytest.mark.parametrize(
    ("body", "status", "says"),
    [
        (b"", 404, "HTTPError"),  # the feed is gone
        (NOT_XML, 200, "not XML"),  # a server answering with anything
        (A_PAGE, 200, "not a feed"),  # a redirect landing on a page
        (RENAMED, 200, "format changed"),  # a full feed the parser lost
    ],
)
def test_a_feed_that_is_really_dead_says_what_was_wrong(
    serve_feed: Callable[..., str], body: bytes, status: int, says: str
) -> None:
    url = serve_feed("/dead.xml", body, status)
    verdict = news.check_one(source_at(url, "gone-feed"))
    assert not verdict.alive and not verdict.fresh
    assert says in verdict.fault
    # The failure message names the feed, the URL and what was wrong.
    line = str(verdict)
    assert "gone-feed" in line and url in line and says in line


def test_a_feed_nobody_answers_for_is_dead() -> None:
    """A name that does not resolve and a closed port arrive as the same URLError."""
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    verdict = news.check_one(source_at(f"http://127.0.0.1:{port}/feed.xml"), timeout=5)
    assert not verdict.alive and "URLError" in verdict.fault


def test_a_registered_source_is_checked_by_id_and_url(
    serve_feed: Callable[..., str],
) -> None:
    """A run over several sources reports each one, dead or quiet, by name."""
    live = source_at(serve_feed("/live.xml", RSS), "live-feed")
    quiet = source_at(serve_feed("/quiet.xml", QUIET), "quiet-feed", rests=DIGEST)
    dead = source_at(serve_feed("/missing.xml", b"", 404), "dead-feed")
    checks = [news.check_one(s, timeout=5) for s in (live, quiet, dead)]
    assert [c.alive for c in checks] == [True, True, False]
    assert [c.fresh for c in checks] == [True, False, False]
    assert [c.source for c in checks] == ["live-feed", "quiet-feed", "dead-feed"]


# ---- the live check, nightly only ---------------------------------------------


class QuietFeed(UserWarning):
    """A feed that answered with nothing new: a warning, so a green night says so."""


def report_liveness(checks: list[news.Liveness]) -> None:
    """The nightly's verdict: a dead feed fails, a quiet one warns.

    A warning is what survives a passing run. pytest captures a print and
    shows it only with `-rP` or `-s`, neither of which the nightly passes, so
    a feed that goes quiet for good would leave no trace on a green night.
    """
    for c in checks:
        if c.alive and not c.fresh:
            warnings.warn(f"alive with nothing new today: {c}", QuietFeed, stacklevel=2)
    dead = [str(c) for c in checks if not c.alive]
    assert not dead, "\n".join(dead)


def test_a_quiet_feed_is_warned_about_so_a_green_night_still_names_it() -> None:
    quiet = news.Liveness("quiet-feed", "https://x.test/q.xml", True)
    with pytest.warns(QuietFeed, match="quiet-feed"):
        report_liveness([quiet, news.Liveness("live", "https://x.test/l", True, 2, 2)])


def test_a_dead_feed_fails_the_nightly_and_a_live_one_warns_about_nothing() -> None:
    dead = news.Liveness("gone", "https://x.test/g.xml", False, fault="HTTPError: 404")
    with warnings.catch_warnings():
        warnings.simplefilter("error", QuietFeed)
        with pytest.raises(AssertionError, match="gone"):
            report_liveness(
                [news.Liveness("live", "https://x.test/l", True, 2, 2), dead]
            )


@pytest.mark.integration
def test_every_registered_feed_is_alive() -> None:
    """The nightly liveness check. Not in the default battery: it needs network.

    Alive is the fact this job is for: the feed answered and is still a feed
    this parser reads. Whether it published today is the weather, so a digest
    resting over the weekend warns and does not fail.
    """
    report_liveness([news.check_one(src) for src in news.load_sources()])


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
