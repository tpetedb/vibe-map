"""The pixel companion in the browser game.

The pets were a terminal feature; the game carries the same packed frames,
injected by the build, so there is one source for six sets of pixels. Every
browser test here drives the real control (the Companion select in Settings,
a key the player presses) and waits for a fact the page produced.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import pytest

from tests.conftest import GamePage
from vibemap import sprites
from vibemap.state import State

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "docs" / "media" / "pets-game"
PETS = ("cat", "crab", "dog", "duck", "snail", "turtle")


@pytest.fixture
def island(game_desktop: GamePage) -> GamePage:
    game_desktop.goto()
    game_desktop.start("Lotte")
    return game_desktop


def _pet(page: GamePage) -> dict[str, Any]:
    return page.page.evaluate("window.__pet()")


def _choose(page: GamePage, pet_id: str) -> None:
    """Pick a companion through the real control in the Settings sheet."""
    page.hud_action("#hud button:has-text('Settings')")
    page.page.wait_for_selector("#s-settings.on", state="attached")
    page.sheet_in_place()
    page.page.wait_for_selector("#set-pet", state="visible")
    page.page.select_option("#set-pet", pet_id)
    page.page.wait_for_function(
        "id => window.__S().pet === id", arg=pet_id, timeout=20_000
    )
    page.page.click("#s-settings button:has-text('Back to the campus')")
    page.page.wait_for_selector("#sheet.on", state="detached")
    page.frames(2)


def test_every_pet_can_be_chosen_in_settings_and_appears_on_the_island(
    island: GamePage,
) -> None:
    """The six vendored sets, each picked through the Settings control."""
    MEDIA.mkdir(parents=True, exist_ok=True)
    for pet_id in PETS:
        _choose(island, pet_id)
        island.page.wait_for_function(
            "id => window.__pet().id === id && window.__pet().on",
            arg=pet_id,
            timeout=20_000,
        )
        seen = _pet(island)
        assert seen["state"] in ("idle", "walk", "sit"), seen
        assert seen["frames"] > 0, f"{pet_id} has no frames"
        island.page.screenshot(path=str(MEDIA / f"{pet_id}.png"))
    island.assert_clean()


def test_the_pet_follows_the_walker(island: GamePage) -> None:
    """It keeps up over a walk and ends within a short lag of the walker."""
    _choose(island, "crab")
    island.walk_to(9, -6)
    island.still("window.__pet().x")
    pos = island.page.evaluate("window.__debug().pos")
    pet = _pet(island)
    gap = math.hypot(pet["x"] - pos[0], pet["z"] - pos[2])
    assert gap < 5, f"the pet stayed {gap:.1f} behind"
    assert island.page.evaluate(
        "window.__debug().onLand || window.__debug().onBridge"
    ), "the walker left the land, which is not this test"
    assert _pet(island)["onLand"], "the pet walked off the island"
    island.assert_clean()


def test_the_pet_sits_when_the_walker_sits(island: GamePage) -> None:
    _choose(island, "dog")
    island.page.keyboard.press("x")
    island.page.wait_for_function(
        "() => window.__avatar().pose === 'sit'", timeout=20_000
    )
    island.page.wait_for_function(
        "() => window.__pet().state === 'sit'", timeout=20_000
    )
    island.assert_clean()


def test_none_removes_the_companion(island: GamePage) -> None:
    _choose(island, "duck")
    island.page.wait_for_function("() => window.__pet().on", timeout=20_000)
    _choose(island, "none")
    island.page.wait_for_function("() => !window.__pet().on", timeout=20_000)
    assert _pet(island)["id"] == "none"
    island.assert_clean()


def test_the_choice_survives_a_reload(island: GamePage) -> None:
    _choose(island, "turtle")
    island.page.reload()
    island.page.wait_for_function("typeof window.__S === 'function'")
    island.resume()
    island.page.wait_for_function(
        "() => window.__pet().id === 'turtle' && window.__pet().on", timeout=20_000
    )
    island.assert_clean()


def test_the_choice_travels_in_the_progress_code(island: GamePage) -> None:
    """Out of the game into the CLI, and back in from a code the CLI wrote."""
    _choose(island, "snail")
    island.open_roadmap()
    island.page.click("#s-map button:has-text('Export')")
    island.page.wait_for_function(
        "() => (document.getElementById('impcode').value || '') !== ''",
        timeout=20_000,
    )
    code = island.page.input_value("#impcode")
    state = State()
    state.merge_code(code)
    assert state.pet == "snail"

    state.pet = "cat"
    island.import_code(state.to_code())
    island.page.wait_for_function(
        "() => window.__pet().id === 'cat' && window.__pet().on", timeout=20_000
    )
    island.assert_clean()


def test_a_code_with_an_unknown_pet_is_refused_loudly(island: GamePage) -> None:
    """An id this game has no pixels for is named, not silently defaulted."""
    _choose(island, "crab")
    payload = json.loads(json.dumps({"v": 2, "name": "Lotte", "pet": "dragon"}))
    code = island.page.evaluate(
        "d => btoa(unescape(encodeURIComponent(JSON.stringify(d))))"
        ".replace(/\\+/g,'-').replace(/\\//g,'_').replace(/=+$/,'')",
        payload,
    )
    message = island.import_code(code)
    assert "dragon" in message, message
    assert _pet(island)["id"] == "crab", "the refused code changed the companion"
    island.assert_clean()


def test_the_pet_holds_the_draw_call_budget_on_the_iphone(
    game_webkit_iphone: GamePage,
) -> None:
    """One sprite, one draw call: the phone budget of 300 still holds."""
    phone = game_webkit_iphone
    phone.goto()
    phone.start("Lotte")
    before = phone.page.evaluate("window.__debug().draws")
    _choose(phone, "cat")
    phone.frames(4)
    after = phone.page.evaluate("window.__debug().draws")
    assert after - before <= 2, f"the companion cost {after - before} draw calls"
    assert after < 300, f"draw calls {after} over budget"
    phone.screenshot("pet_iphone", clip_height=700)
    phone.assert_clean()


# ---- the two sides agree, without a browser ---------------------------------


def _injected() -> dict[str, Any]:
    """The PETS constant the build wrote into the game, parsed back out."""
    html = (ROOT / "game" / "vibe-map.html").read_text(encoding="utf-8")
    line = next(ln for ln in html.splitlines() if ln.startswith("const PETS="))
    return json.loads(line[len("const PETS=") : -1])


def test_the_injected_frames_are_the_package_data() -> None:
    """One source of pixels: the game carries what vibemap/data/pets holds."""
    injected = _injected()
    assert set(injected) == set(sprites.available())
    for name, packed in injected.items():
        on_disk = json.loads(
            (sprites.PETS / name / "frames.json").read_text(encoding="utf-8")
        )
        assert packed == on_disk, f"{name} differs from the package data"


def test_the_cli_and_the_game_know_the_same_pets() -> None:
    assert set(sprites.available()) == set(PETS)
    state = State()
    state.pet = "crab"
    assert json.loads(state.model_dump_json())["pet"] == "crab"


def test_the_state_refuses_a_pet_it_has_no_pixels_for() -> None:
    with pytest.raises(ValueError, match="dragon"):
        State(pet="dragon")
    state = State()
    with pytest.raises(ValueError, match="dragon"):
        state.merge_code(State.model_construct(pet="dragon").to_code())
