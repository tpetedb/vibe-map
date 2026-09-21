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
    # An evening on the winter island. Only the campus renders a stop into its
    # own sheet; every other island renders into s-gen, so the pair of events
    # is what says which stop the time was spent in.
    base = now - 3 * HOUR
    for n, seconds in ((1, 240), (2, 120)):
        out.append({"ts": base, "kind": "open", "id": str(n), "world": "winter"})
        out.append(
            {
                "ts": base + 1000,
                "kind": "dwell",
                "id": "s-gen",
                "world": "winter",
                "v": seconds,
            }
        )
        base += 600_000
    out.append({"ts": now - 2000, "kind": "world", "id": "winter", "world": "winter"})
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
    # Looking at an artifact is worth nothing here, as it is in the terminal.
    assert numbers["xp"] == 3 * 100 and numbers["played"] == 180
    assert "Dashboard" in (game.page.text_content("#s-dash h2") or "")
    game.screenshot("dashboard_desktop")
    game.assert_clean()


def test_time_per_stop_counts_every_island(game: GamePage) -> None:
    """R1, R2: the winter stops were logged as s-gen and never counted."""
    game.page.set_viewport_size({"width": 1280, "height": 900})
    game.goto(state=seeded_state())
    game.resume()
    open_dashboard(game)
    dwell = game.page.evaluate("window.__dash()")["dwell"]
    assert dwell == {
        "campus:1": 180,
        "campus:2": 180,
        "campus:3": 180,
        "winter:1": 240,
        "winter:2": 120,
    }
    bars = game.page.locator("#s-dash .card:has(h3:has-text('Time per stop')) svg.ch")
    labels = bars.locator("text.at:not(.v)").all_text_contents()
    assert labels == [
        "Innovation 1",
        "Innovation 2",
        "Innovation 3",
        "Cold 1",
        "Cold 2",
    ]
    # A row is coloured by that island's own stops: winter 1 is delivered,
    # winter 2 is not.
    fills = bars.locator("rect").evaluate_all(
        "els => els.map(e => e.getAttribute('fill'))"
    )
    assert fills[3] == "var(--green)" and fills[4] == "var(--blue)"
    bars.scroll_into_view_if_needed()
    game.screenshot("dashboard_stops")
    game.assert_clean()


def test_the_xp_tile_follows_the_difficulty(game: GamePage) -> None:
    """R4, R5: the tile paid a flat 100 a stop and 10 for a look."""
    state = seeded_state()
    state["settings"] = {"difficulty": "god"}
    game.goto(state=state)
    game.resume()
    open_dashboard(game)
    numbers = game.page.evaluate("window.__dash()")
    assert numbers["stopXp"] == 300 and numbers["xp"] == 3 * 300
    caption = game.page.text_content("#s-dash .tiles .tile:nth-child(2) .tc") or ""
    assert "300 a stop" in caption and "150 a mentor" in caption
    assert "god difficulty" in caption
    game.assert_clean()


def test_the_mentors_tile_counts_the_mentors_you_met(game: GamePage) -> None:
    """R3: the number only moved on an import, under a caption about meeting."""
    state = seeded_state()
    state["met"] = {"karpathy": 1, "willison": 1}
    game.goto(state=state)
    game.resume()
    open_dashboard(game)
    assert game.page.evaluate("window.__dash()")["met"] == 2
    tile = game.page.locator("#s-dash .tiles .tile:nth-child(6)")
    assert "Mentors met" in (tile.locator(".tl").text_content() or "")
    assert (tile.locator(".tv").text_content() or "").startswith("2")
    assert "verified in your camp" in (tile.locator(".tc").text_content() or "")
    game.assert_clean()


def test_the_feed_names_screens_and_islands(game: GamePage) -> None:
    """R6, R9: it printed s-map and a bare world id, and called a sheet a stop."""
    state = seeded_state()
    now = int(time.time() * 1000)
    state["events"] = state["events"] + [
        {"ts": now - 500, "kind": "dwell", "id": "s-map", "world": "campus", "v": 4}
    ]
    game.goto(state=state)
    game.resume()
    open_dashboard(game)
    feed = game.page.text_content("#s-dash .feed") or ""
    assert "Time on a screen Roadmap" in feed
    assert "Island reached Cold Storage Cluster" in feed
    # A stop on another island renders into s-gen; the line still names it.
    assert "Time on a screen Cold 2" in feed
    assert "s-map" not in feed and "s-gen" not in feed
    assert "Time in a stop" not in feed
    # Every kind in the feed carries a hue of its own, never the grey default.
    dots = game.page.locator("#s-dash .feed i").evaluate_all(
        "els => els.map(e => e.style.background)"
    )
    assert all(d and "rgba(0, 0, 0, 0)" not in d for d in dots), dots
    game.assert_clean()


def test_a_chosen_shelf_with_nothing_on_it_gets_a_row(game: GamePage) -> None:
    """R7, R8: it asked for a shelf although one was picked, and cut names."""
    game.page.set_viewport_size({"width": 1280, "height": 900})
    state = seeded_state()
    # The three longest shelf names, plus the one nothing lies on.
    state["interests"] = ["future", "agents", "net", "knowledge"]
    game.goto(state=state)
    game.resume()
    open_dashboard(game)
    card = game.page.locator("#s-dash .card:has(h3:has-text('Your shelves'))")
    assert card.locator(".dash-empty").count() == 0
    labels = card.locator("text.at:not(.v)").all_text_contents()
    assert labels == [
        "Web, networks and APIs",
        "Agents and the harness",
        "Knowledge and Obsidian",
        "What is coming",
    ]
    assert (card.locator("text.at.v").all_text_contents())[3] == "0/0"
    card.scroll_into_view_if_needed()
    game.screenshot("dashboard_shelves")
    game.assert_clean()


def test_one_event_reads_as_one_event(game: GamePage) -> None:
    """R12: a count was interpolated into a hardcoded plural."""
    game.goto()
    game.start("Lotte")
    open_dashboard(game)
    assert game.page.evaluate("window.__dash()")["events"] == 1
    assert "1 event recorded" in (game.page.text_content("#s-dash > p.small") or "")
    game.assert_clean()


def test_the_streak_counts_what_the_terminal_counts(game: GamePage) -> None:
    """R10: a session event alone made the panel claim a streak of one."""
    game.goto()
    game.start("Lotte")
    open_dashboard(game)
    assert game.page.evaluate("window.__dash()")["streak"] == 0
    tile = game.page.locator("#s-dash .tiles .tile:nth-child(3)")
    assert "nothing delivered today yet" in (tile.locator(".tc").text_content() or "")
    game.claim(1)
    assert game.page.evaluate("window.__dash()")["streak"] == 1
    game.assert_clean()


def test_every_sparkline_states_its_reading(game: GamePage) -> None:
    """R11: all six shared one aria-label that said nothing."""
    game.goto(state=seeded_state())
    game.resume()
    open_dashboard(game)
    labels = game.page.locator("#s-dash .tile svg.ch").evaluate_all(
        "els => els.map(e => e.getAttribute('aria-label'))"
    )
    assert labels and all("last seven days:" in (a or "") for a in labels), labels
    assert len(set(labels)) == len(labels), "one reading each, not one for all"
    titles = game.page.locator("#s-dash .tile svg.ch title").all_text_contents()
    assert len(titles) == len(labels), "every mark carries a title"
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
