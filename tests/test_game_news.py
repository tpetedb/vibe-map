"""The live world feed in the game: the card, the runtime refresh, the off switch.

The runtime refresh is same origin: the built game reads ./news.json next to
itself. Here that is the copy the build wrote into game/, served by the test
server; the tests that need other content route the request instead of
reaching anything real. Nothing in this file talks to the open internet.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from playwright.sync_api import Browser, Route

from tests.conftest import ROOT, WAIT_MS, GamePage

LIVE = {
    "version": 2,
    "fetched_at": "2026-09-18T06:00:00Z",
    "items": [
        {
            "id": "abc123abc123",
            "source": "markus-winand-modern-sql",
            "name": "Markus Winand, Modern SQL",
            "kind": "post",
            "title": "Structured Primary Keys",
            "link": "https://modern-sql.com/blog/2026-06/structured-primary-keys",
            "date": "2026-09-18T05:00:00Z",
            "summary": "Sometimes I hit a wall when optimizing a query.",
            "tags": ["data"],
        }
    ],
}


def _feed(payload: dict[str, Any]) -> Any:
    def handler(route: Route) -> None:
        route.fulfill(
            status=200, content_type="application/json", body=json.dumps(payload)
        )

    return handler


def _roadmap(game: GamePage) -> GamePage:
    game.goto()
    game.start("Lotte")
    game.open_roadmap()
    return game


def _rows(game: GamePage) -> int:
    return game.page.locator("#newslist .pathrow").count()


def test_the_build_publishes_the_feed_next_to_the_game() -> None:
    data = json.loads((ROOT / "game" / "news.json").read_text())
    assert data["version"] == 2
    assert all("summary" in i and "name" in i for i in data["items"])


def test_the_card_shows_the_baked_feed_with_names_and_summaries(
    game: GamePage,
) -> None:
    _roadmap(game)
    game.page.wait_for_selector("#newslist .pathrow", state="attached")
    assert _rows(game) > 0
    card = game.page.text_content("#newscard") or ""
    assert "Unofficial, not affiliated" in card
    assert game.page.locator("#newslist a[target='_blank']").count() > 0
    game.page.locator("#newscard").scroll_into_view_if_needed()
    game.screenshot("news_card")
    game.assert_clean()


def test_the_runtime_refresh_replaces_the_baked_copy(game: GamePage) -> None:
    game.page.route("**/news.json*", _feed(LIVE))
    _roadmap(game)
    game.page.wait_for_function(
        "() => (document.getElementById('newslist').textContent || '')"
        ".includes('Markus Winand')",
        timeout=WAIT_MS,
    )
    assert _rows(game) == 1
    game.assert_clean()


def test_a_refresh_of_an_unknown_version_leaves_the_baked_copy(game: GamePage) -> None:
    stale = {**LIVE, "version": 99}
    game.page.route("**/news.json*", _feed(stale))
    _roadmap(game)
    game.page.wait_for_selector("#newslist .pathrow", state="attached")
    assert "Markus Winand" not in (game.page.text_content("#newslist") or "")
    game.assert_clean()


def test_a_refresh_that_fails_is_silent(game: GamePage) -> None:
    game.page.route("**/news.json*", lambda r: r.abort())
    _roadmap(game)
    game.page.wait_for_selector("#newslist .pathrow", state="attached")
    assert _rows(game) > 0
    # A dead refresh is a non-event: the baked copy is the news and the game
    # says nothing. The browser logs the refused request itself, and that line
    # is the only thing allowed through; anything else is ours and is a defect.
    ours = [e for e in game.errors if "Failed to load resource" not in e]
    assert ours == [], f"page errors: {ours}"


def test_the_off_switch_hides_the_card_and_stops_the_fetch(game: GamePage) -> None:
    asked: list[str] = []
    game.page.route("**/news.json*", lambda r: (asked.append(r.request.url), r.abort()))
    game.goto(state={"name": "Lotte", "settings": {"live": "off"}})
    game.resume()
    game.open_roadmap()
    assert not game.page.locator("#newscard").is_visible()
    assert asked == []
    game.screenshot("news_off")
    # Back on: the card returns and the refresh runs after all.
    game.page.evaluate("() => setSetting('live', 'on')")
    game.page.wait_for_selector("#newscard", state="visible")
    game.assert_clean()


def test_the_settings_screen_offers_the_live_world_dropdown(game: GamePage) -> None:
    game.goto()
    game.start("Lotte")
    game.hud_action("#hud button:has-text('Settings')")
    game.page.wait_for_selector("#set-live", state="attached")
    labels = game.page.locator("#s-settings label").all_text_contents()
    assert "Live world" in labels
    options = game.page.locator("#set-live option").all_text_contents()
    assert any(o.startswith("Off") for o in options)
    game.assert_clean()


def test_a_file_url_game_shows_the_baked_feed_and_never_fetches(
    chromium: Browser,
) -> None:
    """No origin to ask, so nothing is asked: the baked NEWS is the feed."""
    context = chromium.new_context(viewport={"width": 420, "height": 860})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
    page.on(
        "console",
        lambda m: (
            errors.append(f"console.error: {m.text}")
            if m.type == "error" and "favicon" not in m.text
            else None
        ),
    )
    asked: list[str] = []
    page.on("request", lambda r: asked.append(r.url) if "news.json" in r.url else None)
    page.goto(Path(ROOT / "game" / "vibe-map.html").as_uri())
    page.fill("#name", "Lotte")
    page.click("#title .row.go button.primary")
    page.click("#hud button:has-text('Roadmap')")
    page.wait_for_selector("#newslist .pathrow", state="attached")
    assert page.locator("#newslist .pathrow").count() > 0
    assert asked == []
    assert errors == [], f"page errors: {errors}"
    context.close()
