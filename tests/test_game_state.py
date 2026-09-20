"""The saved record and the progress code: what the game does with a bad one.

The record is JSON in the player's own browser and a code arrives from a mail
or a chat, so neither of them is data. Every test here seeds something wrong
and then asks for the two things that matter: a playable evening, and a
message that says what happened.
"""

from __future__ import annotations

import base64
import json
from typing import Any

import pytest

from tests.conftest import STORAGE_KEY, GamePage


def _code(payload: dict[str, Any]) -> str:
    """A progress code with any payload, the way another machine would send it."""
    raw = json.dumps(payload).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _seed_raw(game: GamePage, raw: str) -> None:
    """Put a record under the key exactly as it is, broken JSON and all."""
    game.page.goto(game.url)
    game.page.evaluate("([k, v]) => localStorage.setItem(k, v)", [STORAGE_KEY, raw])
    game.page.reload()
    game.page.wait_for_function("typeof window.__S === 'function'")


def test_a_record_naming_an_island_the_game_lacks_still_plays(game: GamePage) -> None:
    """S.done is the island's own list, so an island that is not there is a
    blank page one frame later."""
    game.goto(
        state={
            "name": "Marsman",
            "world": "mars",
            "doneW": {"mars": [1, 2], "campus": [1]},
        }
    )
    # The repair is not silence: the player is told before anything else.
    game.page.wait_for_selector("#toast .tst", state="attached")
    assert "could not be read" in (game.page.text_content("#toast") or "")
    assert game.page.evaluate("() => window.__S().world") == "campus"
    assert game.page.evaluate("() => window.__S().done") == [1]
    assert game.page.evaluate("() => window.__loadFault()") != ""
    assert game.page.evaluate("() => window.__S().doneW.mars") is None
    game.resume()
    game.screenshot("state_unknown_island")
    game.assert_clean()


@pytest.mark.parametrize(
    "record",
    [
        {"name": "Lotte", "doneW": 5},
        {"name": "Lotte", "doneW": "campus"},
        {"name": "Lotte", "doneW": {"campus": "123"}},
        {"name": "Lotte", "doneW": {"campus": [1, "two", None]}},
        {"name": "Lotte", "path": 7, "met": "everyone"},
        {"name": "Lotte", "mentors": 3, "artifacts": "cafe", "events": "none"},
    ],
)
def test_a_broken_field_costs_that_field_and_not_the_evening(
    game: GamePage, record: dict[str, Any]
) -> None:
    game.goto(state=record)
    assert game.page.evaluate("() => Array.isArray(window.__S().done)")
    assert game.page.evaluate("() => window.__loadFault()") != ""
    game.resume()
    assert game.page.evaluate("() => window.__debug().started") is True
    game.assert_clean()


@pytest.mark.parametrize("raw", ["not json at all", "null", "[1,2,3]", '"Lotte"'])
def test_a_record_that_is_not_an_object_is_a_fresh_start(
    game: GamePage, raw: str
) -> None:
    _seed_raw(game, raw)
    assert game.page.evaluate("() => window.__S().name") == ""
    assert game.page.evaluate("() => window.__S().done") == []
    assert game.page.evaluate("() => window.__loadFault()") != ""
    game.start("Lotte")
    game.assert_clean()


def test_the_placeholder_name_is_never_a_player(game: GamePage) -> None:
    """An unnamed camp exports "<your_name>", which is an instruction, not a
    person: the import applies the rule a saved record already has."""
    game.goto()
    game.start("Lotte")
    game.import_code(_code({"v": 2, "name": "<your_name>"}))
    assert game.page.evaluate("() => window.__S().name") == "Lotte"
    assert "your_name" not in (game.page.text_content("#hud-name") or "").lower()
    # A real name still travels.
    game.import_code(_code({"v": 2, "name": "Tom"}))
    assert game.page.evaluate("() => window.__S().name") == "Tom"
    game.assert_clean()


def test_a_code_naming_an_island_the_game_lacks_is_refused(game: GamePage) -> None:
    game.goto()
    game.start("Lotte")
    before = game.state()
    message = game.import_code(_code({"v": 2, "doneW": {"mars": [1, 2, 3]}}))
    assert "mars" in message and "does not have" in message, message
    after = game.state()
    assert after["doneW"] == before["doneW"]
    assert after["doneW"].get("mars") is None
    game.assert_clean()


def test_a_code_cannot_invent_a_stop_the_island_has_not_got(game: GamePage) -> None:
    """The bound is the campaign's, so a camp that adds a ninth stop can send
    it and a code still cannot invent one."""
    game.goto()
    game.start("Lotte")
    stops = int(game.page.evaluate("() => window.__data().campaign.campus.ws.length"))
    message = game.import_code(
        _code({"v": 2, "doneW": {"campus": [1, stops, stops + 1]}})
    )
    assert game.state()["doneW"]["campus"] == [1, stops], message
    game.assert_clean()


@pytest.mark.parametrize(
    ("payload", "wanted", "unwanted"),
    [
        ({"v": 3}, "just build", "vibe export"),
        ({"v": "2"}, "which version it is", "reads version 2"),
        ({"v": 1}, "vibe export", "just build"),
    ],
)
def test_a_version_refusal_names_the_side_that_is_behind(
    game: GamePage, payload: dict[str, Any], wanted: str, unwanted: str
) -> None:
    game.goto()
    game.start("Lotte")
    payload["doneW"] = {"campus": [1, 2]}
    message = game.import_code(_code(payload))
    assert wanted in message and unwanted not in message, message
    assert game.state()["doneW"]["campus"] == []
    game.assert_clean()


@pytest.mark.parametrize("fixture", ["game", "game_desktop"])
def test_the_export_hands_over_a_code_you_can_copy_and_a_command_you_can_run(
    fixture: str, request: pytest.FixtureRequest
) -> None:
    """The box shows about thirty of two thousand characters, so the code is
    selected: a refused clipboard still leaves one keystroke that works."""
    game: GamePage = request.getfixturevalue(fixture)
    game.goto()
    game.start("Lotte")
    game.claim(1)
    game.open_roadmap()
    assert game.page.get_attribute("#impcode", "aria-label")
    game.page.click("#s-map button:has-text('Export progress')")
    game.page.wait_for_function(
        "() => (document.getElementById('syncmsg').textContent || '') !== ''"
    )
    box = game.page.evaluate(
        "() => {const b = document.getElementById('impcode');"
        " return {focused: document.activeElement === b, start: b.selectionStart,"
        " end: b.selectionEnd, len: b.value.length};}"
    )
    assert box["focused"] and box["start"] == 0
    assert box["end"] == box["len"] and box["len"] > 100, box
    message = game.page.text_content("#syncmsg") or ""
    assert "vibe import <code>" in message, message
    assert "uv run" not in message, message
    game.screenshot(f"export_selected_{fixture}")
    game.assert_clean()


def test_no_animations_stops_rolinda_typing(game: GamePage) -> None:
    """The dropdown is the one motion switch: typeOut asks the same helper
    every other animation asks."""
    game.goto()
    game.start("Lotte")
    # The second stop opens once the first is delivered, and Rolinda speaks it.
    game.claim(1)
    game.hud_action("#hud button:has-text('Settings')")
    game.page.wait_for_selector("#s-settings .setting", state="attached")
    game.page.select_option("#set-motion", "off")
    game.page.keyboard.press("Escape")
    game.open_roadmap()
    game.workstream_buttons()[1].click()
    # Read at once: with the typewriter running the line is a prefix of itself.
    line = game.page.evaluate(
        "() => {const el = document.getElementById('bub-text');"
        " return [el.textContent, el.getAttribute('aria-label')];}"
    )
    assert line[1] and line[0] == line[1], line
    game.screenshot("motion_off_typing")
    game.assert_clean()
