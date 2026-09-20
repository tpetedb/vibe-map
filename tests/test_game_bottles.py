"""Messages in a bottle: eight lessons washed up on the shores, outside every count.

The data is checked first, then the game through the real walk: the bottles lie
on land near the shore, walking over one opens it, the Backpack keeps it, and a
reload does not put it back.
"""

from __future__ import annotations

import math
from typing import Any

import pytest

from tests.conftest import GamePage
from vibemap import campaign

WORLDS = ("campus", "winter", "desert", "prod")


def _bottles(page: GamePage) -> dict[str, Any]:
    return page.page.evaluate("window.__bottles()")


@pytest.fixture
def island(game: GamePage) -> GamePage:
    game.goto()
    game.start("Lotte")
    return game


def test_the_data_holds_two_true_lessons_an_island() -> None:
    data = campaign.items_raw()
    bottles = data["bottles"]
    assert len(data["items"]) == 40, "the bottles must stay outside the forty"
    assert [b["world"] for b in bottles].count("campus") == 2
    assert {b["world"] for b in bottles} == set(WORLDS)
    assert len({b["id"] for b in bottles}) == len(bottles) == 8
    topics = {t[0] for t in __import__("vibemap.tech", fromlist=["T"]).T}
    for b in bottles:
        assert set(b) == {"id", "world", "deg", "topic", "title", "lesson"}, b["id"]
        assert b["topic"] in topics, b["id"]
        assert 0 <= b["deg"] < 360, b["id"]
        assert b["lesson"].endswith("."), b["id"]
        assert 60 <= len(b["lesson"]) <= 260, b["id"]
        assert not b["title"].endswith("."), b["id"]


def test_the_bottles_lie_on_the_shore_of_every_island(island: GamePage) -> None:
    for world in WORLDS:
        island.page.evaluate("id => setWorld(id)", world)
        island.until(f"window.__debug().world === '{world}'")
        island.until("window.__bottles().here.length === 2")
        for b in _bottles(island)["here"]:
            assert b["land"] and not b["bridge"], (world, b)
            assert 0 < b["shore"] < 3, (world, b)
    island.assert_clean()


def test_walking_over_a_bottle_opens_it_and_the_backpack_keeps_it(
    island: GamePage,
) -> None:
    before = island.page.evaluate("window.__avatar().items.length")
    pos = island.page.evaluate("window.__debug().pos")
    here = _bottles(island)["here"]
    target = min(here, key=lambda b: math.hypot(b["x"] - pos[0], b["z"] - pos[2]))
    island.walk_to(target["x"], target["z"], tol=0.9, steps=900)
    island.until(f"window.__bottles().found.includes('{target['id']}')")
    island.page.wait_for_selector("#toast .tst", state="attached")
    text = island.page.text_content("#toast") or ""
    assert "A message in a bottle" in text
    island.screenshot("bottle_opened", clip_height=700)

    # Outside every count: the forty are untouched, and so are the badges.
    assert island.page.evaluate("window.__avatar().items.length") == before
    assert len(_bottles(island)["here"]) == 1

    island.hud_action("#hud button[aria-label='Backpack']")
    island.page.wait_for_selector("#bottlescard", state="attached")
    card = island.page.text_content("#bottlescard") or ""
    assert "1 of 8 found" in card

    island.page.reload()
    island.page.wait_for_function("() => window.__bottles !== undefined")
    assert _bottles(island)["found"] == [target["id"]]
    island.assert_clean()
