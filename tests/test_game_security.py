"""What the page does with content it did not write, and who it talks to.

Two rules the game has to keep. Nothing that arrives from outside the build
(the news feed, an answer from the chat bridge, an imported progress code) may
reach the page as markup or as a link the browser will run. And the page talks
to its own origin only: it is one file with no CDN, so a fresh boot, the
Roadmap, a lesson sheet and the dashboard must need nothing else.

The hostile payloads here are served by the test, never fetched: nothing in
this file talks to the open internet.
"""

from __future__ import annotations

import json
import threading
from collections.abc import Iterator
from typing import Any

import pytest
from playwright.sync_api import Route

from tests.conftest import GamePage, encode_progress
from vibemap import chat
from vibemap.config import Config

# One item with every field hostile: a title that runs script through an image,
# a name with markup in it, a summary carrying a script element, and a link the
# browser would execute if it became an anchor.
TITLE = '<img src=x onerror="window.__pwned=1">Title'
NAME = "Odd & <b>bold</b> name"
SUMMARY = "<script>window.__pwned=1</script>Summary"
HOSTILE = {
    "version": 2,
    "fetched_at": "2026-09-18T06:00:00Z",
    "items": [
        {
            "id": "ffffffffffff",
            "source": "hostile",
            "name": NAME,
            "kind": "post",
            "title": TITLE,
            "link": "javascript:window.__jsurl=1",
            "date": "2026-09-18T05:00:00Z",
            "summary": SUMMARY,
            "tags": [],
        },
        {
            "id": "eeeeeeeeeeee",
            "source": "hostile",
            "name": "Plain name",
            "kind": "release",
            "title": "An item with a link that is fine",
            "link": "https://example.com/post",
            "date": "2026-09-18T04:00:00Z",
            "summary": "",
            "tags": [],
        },
    ],
}

CODE = "ABCD2345"
# The bridge is the player's own subscription, and a model answers with
# whatever it likes: the panel owes them text either way.
ANSWER = '<img src=x onerror="window.__pwned=1">The answer.'


def _feed(payload: dict[str, Any]) -> Any:
    def handler(route: Route) -> None:
        route.fulfill(
            status=200, content_type="application/json", body=json.dumps(payload)
        )

    return handler


def hostile_runner(provider_id: str, prompt: str, timeout: int) -> Iterator[str]:
    """A provider that answers with markup instead of words."""
    yield ANSWER


@pytest.fixture
def hostile_bridge() -> Iterator[int]:
    bridge = chat.Bridge(Config.load(), code=CODE, runner=hostile_runner)
    server = chat.serve(bridge, port=0)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield int(server.server_address[1])
    server.shutdown()
    server.server_close()


def test_a_hostile_feed_is_shown_as_text_and_never_runs(game: GamePage) -> None:
    game.page.route("**/news.json*", _feed(HOSTILE))
    game.goto()
    game.start("Lotte")
    game.open_roadmap()
    game.until(
        "(document.getElementById('newslist').textContent || '')"
        ".includes('Odd & <b>bold</b> name')"
    )
    # Nothing ran, and nothing became an element.
    assert game.page.evaluate("() => window.__pwned") is None
    assert game.page.evaluate("() => window.__jsurl") is None
    assert (
        game.page.locator("#newslist img, #newslist b, #newslist script").count() == 0
    )
    assert game.page.locator("#newslist a[href^='javascript:']").count() == 0
    # The item whose link is unusable keeps its title, as words.
    text = game.page.text_content("#newslist") or ""
    assert TITLE in text
    assert "<script>" in text and "Summary" in text
    # The item with an http link keeps its anchor, with both rel tokens.
    links = game.page.locator("#newslist a")
    assert links.count() == 1
    assert links.first.get_attribute("href") == "https://example.com/post"
    assert links.first.get_attribute("rel") == "noopener noreferrer"
    game.page.locator("#newscard").scroll_into_view_if_needed()
    game.screenshot("news_hostile")
    game.assert_clean()


def test_a_bridge_answer_with_markup_is_shown_as_text(
    game: GamePage, hostile_bridge: int
) -> None:
    game.goto(state={"name": "Lotte", "chat": {"code": CODE, "port": hostile_bridge}})
    game.resume()
    game.hud_action("#hud button:has-text('Ask')")
    game.page.wait_for_selector("#chatq", state="attached")
    game.sheet_in_place()
    game.page.fill("#chatq", "What is a stop?")
    game.page.click("#s-chat button.primary")
    game.until(
        "(document.getElementById('chatlog').textContent || '').includes('The answer.')"
    )
    assert game.page.evaluate("() => window.__pwned") is None
    assert game.page.locator("#chatlog img, #chatlog script").count() == 0
    assert ANSWER in (game.page.text_content("#chatlog") or "")
    game.screenshot("chat_hostile")
    game.assert_clean()


def test_an_imported_name_with_markup_stays_text(game: GamePage) -> None:
    """A progress code comes from another machine, its name field included."""
    hostile = '<img src=x onerror="window.__pwned=1">Lotte'
    game.goto(state={"name": "Lotte", "doneW": {"campus": [1, 2, 3, 4, 5]}})
    game.resume()
    game.import_code(encode_progress(name=hostile, done_w={"campus": [1]}))
    # Workstream 6 draws the note graph, the one screen that writes the name
    # into markup rather than into a text node.
    game.open_workstream(6)
    game.until("document.querySelectorAll('#web text').length > 0")
    assert game.page.evaluate("() => window.__pwned") is None
    assert game.page.locator("#web img").count() == 0
    labels = game.page.locator("#web text").all_text_contents()
    assert hostile in labels
    game.assert_clean()


ALLOWED_SCHEMES = ("data:", "blob:", "about:")


def _foreign(urls: list[str], origin: str) -> list[str]:
    """Every request that left our own origin, in the order it was made."""
    return [
        u
        for u in urls
        if not u.startswith(origin) and not u.startswith(ALLOWED_SCHEMES)
    ]


def test_the_page_only_ever_talks_to_its_own_origin(
    game_desktop: GamePage, server: str
) -> None:
    """No CDN: a boot, the Roadmap, a lesson and the dashboard stay home.

    The tab icon is part of this. A page with no icon makes the browser ask
    for /favicon.ico, which is a request the one-file game cannot answer.
    """
    asked: list[str] = []
    missing: list[str] = []
    game_desktop.page.on("request", lambda r: asked.append(r.url))
    game_desktop.page.on(
        "response", lambda r: missing.append(r.url) if r.status >= 400 else None
    )
    game_desktop.goto()
    game_desktop.screenshot("fonts_title")
    game_desktop.start("Lotte")
    game_desktop.screenshot("fonts_hud")
    game_desktop.open_workstream(1)
    game_desktop.screenshot("fonts_sheet")
    game_desktop.page.keyboard.press("Escape")
    game_desktop.hud_action("#hud button:has-text('Stats')")
    game_desktop.page.wait_for_selector("#s-dash .tile", state="attached")
    game_desktop.sheet_in_place()
    game_desktop.screenshot("fonts_dashboard")
    assert asked, "no requests recorded at all"
    assert _foreign(asked, server) == []
    assert missing == [], f"the page asked for something that is not there: {missing}"
    # The icon travels inside the page, so no favicon is ever fetched.
    icon = game_desktop.page.get_attribute("link[rel=icon]", "href")
    assert icon and icon.startswith("data:image/svg+xml,")
    assert not [u for u in asked if "favicon" in u]
    game_desktop.assert_clean()


def test_the_iphone_profile_stays_home_and_still_fits(
    game_webkit_iphone: GamePage, server: str
) -> None:
    """The same on WebKit at iPhone metrics, where the fallback font differs."""
    game = game_webkit_iphone
    asked: list[str] = []
    game.page.on("request", lambda r: asked.append(r.url))
    game.goto()
    game.screenshot("fonts_iphone_title")
    game.start("Lotte")
    game.open_roadmap()
    game.screenshot("fonts_iphone_roadmap")
    # The Roadmap is the densest screen: no font metric may push it sideways.
    overflow = game.page.evaluate(
        "() => document.documentElement.scrollWidth - "
        "document.documentElement.clientWidth"
    )
    assert overflow <= 0, f"the page scrolls sideways by {overflow} px"
    assert _foreign(asked, server) == []
    game.assert_clean()
