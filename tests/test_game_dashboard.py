"""The in-game dashboard: what the event log records and what the panel draws.

Every test clicks the real button and ends on zero page errors. The seeded log
is written the way the game writes it, so a change to the event shape fails
here first.
"""

from __future__ import annotations

import time
from typing import Any

from tests.conftest import GamePage

HOUR = 3_600_000
DAY = 86_400_000


def seeded_events() -> list[dict[str, Any]]:
    """Three days of play, so every chart on the panel has something to draw."""
    now = int(time.time() * 1000)
    out: list[dict[str, Any]] = []
    for day in (2, 1, 0):
        base = now - day * DAY - 4 * HOUR
        out.append({"ts": base, "kind": "session", "id": "start", "world": "campus"})
        out.append(
            {
                "ts": base + 60_000,
                "kind": "play",
                "id": "tick",
                "world": "campus",
                "v": 60,
            }
        )
        n = 3 - day
        out.append(
            {"ts": base + 120_000, "kind": "open", "id": str(n), "world": "campus"}
        )
        out.append(
            {
                "ts": base + 300_000,
                "kind": "dwell",
                "id": f"s-{n}",
                "world": "campus",
                "v": 180,
            }
        )
        out.append(
            {"ts": base + 360_000, "kind": "claim", "id": str(n), "world": "campus"}
        )
    out.append(
        {
            "ts": now - 1000,
            "kind": "artifact",
            "id": "cache-fountain",
            "world": "campus",
        }
    )
    return out


def seeded_state() -> dict[str, Any]:
    return {
        "name": "Lotte",
        "doneW": {"campus": [1, 2, 3], "winter": [1], "desert": [], "prod": []},
        "done": [1, 2, 3],
        "artifacts": ["cache-fountain"],
        "artifactsBuilt": [],
        "mentors": [],
        "met": {},
        "path": {},
        "events": seeded_events(),
    }


def open_dashboard(game: GamePage) -> None:
    game.hud_action("#hud button:has-text('Stats')")
    game.page.wait_for_selector("#s-dash.on", state="attached")
    game.page.wait_for_selector("#s-dash .tile", state="attached")
    game.sheet_in_place()


def test_playing_records_events(game: GamePage) -> None:
    game.goto()
    game.start("Lotte")
    game.claim(1)
    kinds = [e["kind"] for e in game.state()["events"]]
    assert "session" in kinds and "open" in kinds and "claim" in kinds
    first = game.state()["events"][0]
    assert set(first) >= {"ts", "kind", "id", "world"}, first
    assert first["world"] == "campus"
    game.assert_clean()


def test_track_is_exposed_for_the_other_modules(game: GamePage) -> None:
    """X1 (chat) and X3 (avatar) record through this one helper."""
    game.goto()
    game.start("Lotte")
    game.page.evaluate("window.track('item', 'mug')")
    last = game.state()["events"][-1]
    assert last["kind"] == "item" and last["id"] == "mug"
    game.assert_clean()


def test_the_log_stays_bounded(game: GamePage) -> None:
    game.goto(state=seeded_state())
    game.start("Lotte")
    game.page.evaluate(
        "() => { for (let i = 0; i < 700; i++) track('play', 'tick', 60); }"
    )
    events = game.state()["events"]
    assert len(events) <= 600
    # Compaction folds a day of ticks into one event rather than dropping them.
    ticks = [e for e in events if e["kind"] == "play"]
    assert any(e["id"] == "day" and e["v"] > 60 for e in ticks), ticks[:3]
    game.assert_clean()


def test_dashboard_panel_draws_every_chart(game: GamePage) -> None:
    game.page.set_viewport_size({"width": 1280, "height": 900})
    game.goto(state=seeded_state())
    game.resume()
    open_dashboard(game)
    assert game.page.locator("#s-dash .tile").count() == 6
    assert game.page.locator("#s-dash .ring").count() == 4
    # Four rings, the shelves, the XP line, the heatmap and the bars, plus a
    # sparkline on every tile whose seven days are not all zero.
    assert game.page.locator("#s-dash .card svg.ch").count() == 8
    assert game.page.locator("#s-dash .tile svg.ch").count() >= 4
    assert game.page.locator("#s-dash .feed li").count() > 0
    assert game.page.locator("#s-dash .path .step").count() == 3
    numbers = game.page.evaluate("window.__dash()")
    assert numbers["stops"] == 4 and numbers["claims"] == 3
    assert numbers["xp"] == 3 * 100 + 10 and numbers["played"] == 180
    assert numbers["dwell"] == {"1": 180, "2": 180, "3": 180}
    assert "Dashboard" in (game.page.text_content("#s-dash h2") or "")
    game.screenshot("dashboard_desktop")
    game.assert_clean()


def test_dashboard_is_keyboard_reachable_and_escapes(game: GamePage) -> None:
    game.goto(state=seeded_state())
    game.resume()
    open_dashboard(game)
    # The sheet moves the focus a tick after it opens, so wait for the move.
    game.until("document.activeElement === document.querySelector('#sheet .x')")
    game.page.keyboard.press("Escape")
    game.page.wait_for_selector("#sheet.on", state="detached")
    game.assert_clean()


def test_dashboard_says_so_when_there_is_nothing_yet(game: GamePage) -> None:
    game.goto()
    game.start("Lotte")
    open_dashboard(game)
    assert game.page.locator("#s-dash .dash-empty").count() >= 3
    assert "0" in (game.page.text_content("#s-dash .tile .tv") or "")
    game.assert_clean()


def test_dashboard_on_a_phone(game_webkit_iphone: GamePage) -> None:
    phone = game_webkit_iphone
    phone.goto(state=seeded_state())
    phone.resume()
    open_dashboard(phone)
    # Nothing may push the 393px viewport sideways.
    overflow = phone.page.evaluate(
        "() => document.documentElement.scrollWidth"
        " - document.documentElement.clientWidth"
    )
    assert overflow <= 0, f"horizontal overflow of {overflow}px"
    phone.screenshot("dashboard_phone")
    phone.assert_clean()
