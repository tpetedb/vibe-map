"""The avatar: sitting with the laptop, collectibles, achievements, wearables.

Every browser test drives the real entry point (a key the player presses, a
button in the Backpack) and waits for something the page produced, never for a
wall clock. The pure-Python tests cover the progress code, which is the only
place the game and the CLI have to agree.
"""

from __future__ import annotations

import json
import math
from typing import Any

import pytest

from tests.conftest import GamePage, encode_progress
from vibemap import campaign
from vibemap.state import State


@pytest.fixture
def island(game: GamePage) -> GamePage:
    game.goto()
    game.start("Lotte")
    return game


def _avatar(page: GamePage) -> dict[str, Any]:
    return page.page.evaluate("window.__avatar()")


def _sit(page: GamePage) -> None:
    page.page.keyboard.press("x")
    page.page.wait_for_function(
        "() => window.__avatar().pose === 'sit'", timeout=20_000
    )
    page.frames()


def _nearest_item(page: GamePage) -> dict[str, Any]:
    pos = page.page.evaluate("window.__debug().pos")
    on_ground = _avatar(page)["onGround"]
    assert on_ground, "no collectibles on the island"
    return min(on_ground, key=lambda i: math.hypot(i["x"] - pos[0], i["z"] - pos[2]))


def test_the_data_places_everything_relative_to_a_plot_or_an_annex() -> None:
    """No collectible carries a world coordinate; the next layout moves them."""
    data = campaign.items_raw()
    assert len(data["items"]) == 40
    for entry in data["items"] + data["seats"]:
        at = entry["at"]
        assert set(at) <= {"plot", "annex", "path", "d", "a"}
        assert {"plot", "annex", "path"} & set(at), entry["id"]
    topics = {t[0] for t in __import__("vibemap.tech", fromlist=["T"]).T}
    for item in data["items"]:
        assert item["topic"] in topics, item["id"]
        assert item["concept"].endswith("."), item["id"]


def test_the_progress_code_carries_the_avatar_additively() -> None:
    """items, ach and wear travel inside version 2, and merge without loss."""
    sender = State(items=["campus-commit"], ach=["first-sit"], wear=["cap"])
    payload = json.loads(
        __import__("base64").urlsafe_b64decode(
            sender.to_code() + "=" * (-len(sender.to_code()) % 4)
        )
    )
    assert payload["v"] == 2
    assert payload["items"] == ["campus-commit"]

    receiver = State(items=["campus-token"], ach=[], wear=[])
    receiver.merge_code(sender.to_code())
    assert receiver.items == ["campus-token", "campus-commit"]
    assert receiver.ach == ["first-sit"]
    assert receiver.wear == ["cap"]
    # An older code simply has none of the three keys.
    receiver.merge_code(State(name="Lotte").to_code())
    assert receiver.items == ["campus-token", "campus-commit"]


def test_x_sits_the_walker_down_with_the_laptop_open(island: GamePage) -> None:
    _sit(island)
    state = _avatar(island)
    assert state["pose"] == "sit"
    assert state["laptop"], "the laptop did not open on the lap"
    assert "first-sit" in state["ach"]
    island.page.wait_for_selector("#toast .tst", state="attached")
    island.screenshot("avatar_sitting_with_laptop", clip_height=700)
    island.assert_clean()


def test_walking_stands_the_walker_back_up(island: GamePage) -> None:
    _sit(island)
    island.page.keyboard.down("ArrowUp")
    try:
        island.page.wait_for_function(
            "() => window.__avatar().pose === 'stand'", timeout=20_000
        )
    finally:
        island.page.keyboard.up("ArrowUp")
    assert _avatar(island)["laptop"] is False
    island.assert_clean()


def test_a_seat_is_there_and_the_mentors_work_at_theirs(island: GamePage) -> None:
    assert _avatar(island)["seats"], "no seats were placed on the island"
    assert _avatar(island)["sitting"] > 0, "the mentors are not at their laptops"


def test_walking_over_a_collectible_picks_it_up(island: GamePage) -> None:
    item = _nearest_item(island)
    island.walk_to(item["x"], item["z"], tol=0.9)
    island.page.wait_for_function(
        "id => window.__avatar().items.includes(id)", arg=item["id"], timeout=20_000
    )
    island.page.wait_for_selector("#toast .tst", state="attached")
    text = island.page.text_content("#toast .tst") or ""
    assert "Picked up" in text
    island.screenshot("avatar_item_pickup", clip_height=700)
    island.assert_clean()


def test_the_backpack_lists_the_inventory_and_the_achievements(
    island: GamePage,
) -> None:
    island.hud_action("#hud button[aria-label='Backpack']")
    island.page.wait_for_selector("#s-pack.on", state="attached")
    island.sheet_in_place()
    assert "Backpack" in (island.page.text_content("#s-pack h2") or "")
    island.screenshot("avatar_backpack")
    island.page.click("#s-pack .packtabs button:has-text('Achievements')")
    island.page.wait_for_selector("#s-pack .pathrow", state="attached")
    assert "First sit" in (island.page.text_content("#s-pack") or "")
    island.assert_clean()


def test_an_achievement_unlocks_a_hat_you_can_wear(island: GamePage) -> None:
    _sit(island)
    island.page.keyboard.press("x")
    island.page.wait_for_function("() => window.__avatar().pose === 'stand'")
    island.hud_action("#hud button[aria-label='Backpack']")
    island.page.wait_for_selector("#s-pack.on", state="attached")
    island.page.click("#s-pack .packtabs button:has-text('Wardrobe')")
    island.page.click("#s-pack button:has-text('Wear')")
    island.page.wait_for_function("() => window.__avatar().wear.includes('cap')")
    island.page.click("#sheet button.x")
    island.frames()
    assert _avatar(island)["wearing"] > 0, "nothing was put on the walker"
    island.screenshot("avatar_wearing_a_hat", clip_height=700)
    island.assert_clean()


def test_x_sits_the_walker_down_at_the_end_of_a_walk(island: GamePage) -> None:
    """The speed left from the last step must not stand the walker back up.

    Walking to the seat and pressing x is how a player sits down, so the key
    is released and pressed in the same breath: the walker still carries the
    speed of the walk when the sit arrives.
    """
    island.page.keyboard.down("ArrowUp")
    island.frames(4)
    island.page.keyboard.up("ArrowUp")
    _sit(island)
    assert _avatar(island)["laptop"], "the laptop did not open on the lap"
    island.assert_clean()


def test_the_walker_keeps_his_seat_when_the_name_rebuilds_him(
    island: GamePage,
) -> None:
    """Typing the name rebuilds the walker, and the rebuild lands whenever.

    The name box rebuilds the body a moment after typing stops, so on a fast
    machine that rebuild arrives after the game has started and after the
    walker has sat down. The new body has to take over the pose.
    """
    _sit(island)
    # The handler the name box calls on every keystroke, and with it the
    # rebuild it schedules; the new plate over the walker is the page's own
    # signal that the new body is in the scene.
    island.page.evaluate("window.nameTyped('Rolinda')")
    island.until(
        "((window.__debug().label || {}).text || '').startsWith('Rolinda')"
    )
    state = _avatar(island)
    assert state["pose"] == "sit"
    assert state["laptop"], "the laptop did not come back to the lap"
    island.assert_clean()


def test_an_imported_code_brings_the_avatar_across(island: GamePage) -> None:
    code = encode_progress(name="Lotte")
    padded = json.loads(
        __import__("base64").urlsafe_b64decode(code + "=" * (-len(code) % 4))
    )
    padded.update({"items": ["campus-commit"], "ach": ["first-light"], "wear": ["cap"]})
    raw = json.dumps(padded).encode()
    with_avatar = __import__("base64").urlsafe_b64encode(raw).decode().rstrip("=")
    island.import_code(with_avatar)
    island.frames()
    state = _avatar(island)
    assert state["items"] == ["campus-commit"]
    assert "campus-commit" not in [i["id"] for i in state["onGround"]]
    assert state["wear"] == ["cap"]
    island.assert_clean()
