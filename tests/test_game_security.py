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

import base64
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


# One payload for every field of a progress code and of the stored state: it
# closes a single and a double quoted attribute first, so a value that lands
# inside an attribute is caught as well as one that lands between tags.
BREAKOUT = '\'"><img src=x onerror="window.__pwned=1">'
NO_MARKUP = "() => document.querySelectorAll('img[src=\"x\"]').length"


def _code(payload: dict[str, Any]) -> str:
    """A progress code with any payload, the way another machine would send it."""
    raw = json.dumps(payload).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


@pytest.mark.parametrize(
    "field",
    ["interests", "path", "artifacts", "mentors", "items", "topics", "doneW"],
)
def test_a_pasted_progress_code_cannot_carry_markup(game: GamePage, field: str) -> None:
    """A code is pasted from a chat or a mail, so every id in it is outside data."""
    values: dict[str, Any] = {
        "interests": [BREAKOUT],
        "path": {"karpathy": BREAKOUT},
        "doneW": {BREAKOUT: [1]},
    }
    payload = {"v": 2, "name": "Lotte", "doneW": {"campus": [1]}}
    payload[field] = values.get(field, [BREAKOUT])
    game.goto()
    game.start("Lotte")
    before = game.state()
    message = game.import_code(_code(payload))
    # The Roadmap is on screen and has just been redrawn from the state.
    assert game.page.evaluate("() => window.__pwned") is None
    assert game.page.evaluate(NO_MARKUP) == 0
    # Refused whole, by name: nothing of a code that fails is merged.
    assert "cannot read" in message and field in message, message
    after = game.state()
    assert after["doneW"] == before["doneW"]
    assert after.get("interests") == before.get("interests")
    assert after["path"] == before["path"]
    # Settings and the title screen draw the same state again after a reload.
    game.page.keyboard.press("Escape")
    game.hud_action("#hud button:has-text('Settings')")
    game.page.wait_for_selector("#s-settings .setting", state="attached")
    assert game.page.evaluate(NO_MARKUP) == 0
    game.page.reload()
    game.page.wait_for_function("typeof window.__S === 'function'")
    assert game.page.evaluate("() => window.__pwned") is None
    assert game.page.evaluate(NO_MARKUP) == 0
    game.assert_clean()


def test_a_pasted_code_is_refused_on_the_iphone_profile_too(
    game_webkit_iphone: GamePage,
) -> None:
    """The refusal is a line of text the phone player reads, in another engine."""
    game = game_webkit_iphone
    game.goto()
    game.start("Lotte")
    message = game.import_code(
        _code({"v": 2, "name": "Lotte", "interests": [BREAKOUT]})
    )
    assert "cannot read" in message and "interests" in message, message
    assert game.page.evaluate(NO_MARKUP) == 0
    box = game.page.locator("#syncmsg").bounding_box()
    assert box and box["x"] >= 0 and box["x"] + box["width"] <= 393 + 1, box
    game.page.locator("#syncmsg").scroll_into_view_if_needed()
    game.screenshot("import_refused_iphone")
    game.assert_clean()


def test_a_link_from_camp_toml_is_held_to_http(game: GamePage) -> None:
    """repo_url and site_url are typed by the camp's owner and become hrefs."""
    game.goto()
    game.page.evaluate(
        "() => { const c = window.__data().config;"
        " c.repo = 'javascript:window.__pwned=1';"
        " c.site = 'javascript:window.__pwned=1//'; }"
    )
    assert game.page.evaluate("() => window.__siteDoc('syllabus.html')") == (
        "syllabus.html"
    )
    game.start("Lotte")
    game.open_roadmap()
    game.page.click("#s-map button:has-text('Setup guide')")
    game.page.wait_for_selector("#s-setup pre", state="attached")
    hrefs = game.page.eval_on_selector_all("#s-setup a", "as => as.map(a => a.href)")
    assert hrefs and all(h.startswith("https://") for h in hrefs), hrefs
    assert "javascript:" not in (game.page.text_content("#s-setup") or "")
    game.assert_clean()


def test_state_that_already_holds_markup_is_drawn_as_text(game: GamePage) -> None:
    """The sinks hold on their own: a state poisoned before the import learnt
    to refuse (or edited by hand) still reaches every panel as words."""
    game.goto(
        state={
            "name": "Lotte",
            "mode": "full",
            "interests": [BREAKOUT],
            "path": {"karpathy": BREAKOUT},
            "settings": {"difficulty": BREAKOUT},
            "chat": {"code": BREAKOUT, "port": BREAKOUT, "hist": []},
            "events": [
                {"ts": 1, "kind": BREAKOUT, "id": BREAKOUT, "world": BREAKOUT},
                {"ts": 2, "kind": "claim", "id": 1, "world": BREAKOUT},
            ],
        }
    )
    # The title screen: the shelves line and the setup commands.
    game.page.wait_for_selector("#onboard .choice", state="attached")
    assert game.page.evaluate(NO_MARKUP) == 0
    assert BREAKOUT in (game.page.text_content("#onboard") or "")
    game.resume()
    game.open_roadmap()
    assert game.page.evaluate(NO_MARKUP) == 0
    game.page.click("#s-map button:has-text('Setup guide')")
    game.page.wait_for_selector("#s-setup pre", state="attached")
    assert game.page.evaluate(NO_MARKUP) == 0
    game.page.keyboard.press("Escape")
    game.hud_action("#hud button:has-text('Stats')")
    game.page.wait_for_selector("#s-dash .tile", state="attached")
    assert game.page.evaluate(NO_MARKUP) == 0
    assert BREAKOUT in (game.page.text_content("#s-dash .feed") or "")
    game.page.keyboard.press("Escape")
    game.hud_action("#hud button:has-text('Settings')")
    game.page.wait_for_selector("#s-settings .setting", state="attached")
    assert game.page.evaluate(NO_MARKUP) == 0
    assert game.page.evaluate("() => window.__pwned") is None
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
    """No CDN: a boot, the Roadmap, a lesson and the dashboard stay home."""
    asked: list[str] = []
    game_desktop.page.on("request", lambda r: asked.append(r.url))
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
