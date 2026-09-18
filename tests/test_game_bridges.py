"""The archipelago: four islands in one scene, joined by bridges you walk.

The crossing is the thing worth testing, so these drive the real walker with
the frame-based helper rather than calling the world switch. Every wait is on
something the page produced (a frame, a world, a state), never on a clock.
"""

from __future__ import annotations

from typing import Any

import pytest

from tests.conftest import WAIT_MS, GamePage

# A sampler that runs on the frame loop: how often the walker was off any
# ground, and how often it was on a bridge deck. Installed before a crossing
# and read after it, so the whole walk is covered and not just its ends.
WATCH = """() => {
  window.__walk = {off: 0, deck: 0, n: 0};
  const step = () => {
    const d = window.__debug();
    if (d.started) {
      window.__walk.n++;
      if (!d.onLand) window.__walk.off++;
      if (d.onBridge) window.__walk.deck++;
    }
    requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}"""


def _bridge(game: GamePage, a: str, b: str) -> dict[str, Any]:
    bridges = game.page.evaluate("window.__debug().bridges")
    match = [x for x in bridges if {x["a"], x["b"]} == {a, b}]
    assert match, bridges
    return match[0]


def _cross(game: GamePage, bridge: dict[str, Any], *, upto: float = 0.62) -> str:
    """Walk from the near shore along the deck, a few paces at a time.

    Short hops keep the arrow-key steering on the deck: the helper picks one
    of eight directions per hop, and a long hop on a diagonal bridge would
    drift off the side before it corrected. The walk stops the moment the
    world changes, because the waypoints ahead are in the island that was
    just left behind.
    """
    ax, az = bridge["pa"]
    bx, bz = bridge["pb"]
    here = game.page.evaluate("window.__S().world")
    game.walk_to(ax, az, tol=2.2, steps=120)
    hops = max(2, round(bridge["len"] * upto / 7))
    for i in range(1, hops + 1):
        t = upto * i / hops
        game.walk_to(ax + (bx - ax) * t, az + (bz - az) * t, tol=2.2, steps=40)
        now = game.page.evaluate("window.__S().world")
        if now != here:
            return now
    return game.page.evaluate("window.__S().world")


@pytest.fixture
def opened(game: GamePage) -> GamePage:
    """A campus with its first stop done, which is what opens the bridge."""
    game.goto(state={"name": "Lotte", "done": [1], "doneW": {"campus": [1]}})
    game.resume()
    return game


def test_the_bridge_to_winter_is_open_after_the_first_stop(opened: GamePage) -> None:
    bridge = _bridge(opened, "campus", "winter")
    assert bridge["open"] is True
    assert bridge["near"] is True, "a bridge that touches this island is built"
    assert bridge["len"] > 20, f"a bridge you walk is long: {bridge['len']}"
    assert _bridge(opened, "desert", "prod")["near"] is False
    opened.assert_clean()


def test_a_bridge_stays_shut_until_the_island_before_it_has_a_stop(
    game: GamePage,
) -> None:
    """Nothing done anywhere: every bridge is shut, and the deck is not ground."""
    game.goto(state={"name": "Lotte", "done": [], "doneW": {"campus": []}})
    game.resume()
    difficulty = game.page.evaluate("window.__data().config.difficulty")
    bridge = _bridge(game, "campus", "winter")
    if difficulty == "beginner":
        assert bridge["open"] is True, "beginner gates nothing"
        return
    assert bridge["open"] is False
    open_now = game.page.evaluate(
        "() => window.__debug().bridges.filter(b => b.open).length"
    )
    assert open_now == 0, "no island has a stop yet"
    assert game.page.evaluate("window.__debug().onBridge") is False
    game.assert_clean()


def test_walking_the_bridge_switches_the_island(opened: GamePage) -> None:
    """Crossing the middle changes the world with no reload and no gap."""
    bridge = _bridge(opened, "campus", "winter")
    opened.page.evaluate(WATCH)
    _cross(opened, bridge)
    opened.page.wait_for_function(
        "() => window.__S().world === 'winter'", timeout=WAIT_MS
    )
    walk = opened.page.evaluate("window.__walk")
    assert walk["n"] > 10, walk
    assert walk["deck"] > 0, "the walker never set foot on the deck"
    assert walk["off"] == 0, f"the walker left the ground {walk['off']} times"
    # The island is rebuilt, not reloaded: the HUD follows the new world.
    name = opened.page.text_content("#hud-name") or ""
    assert "Evening 2" in name, name
    opened.screenshot("arch_on_the_bridge", clip_height=700)
    opened.assert_clean()


def test_progress_and_items_survive_the_crossing(opened: GamePage) -> None:
    before = opened.state()
    bridge = _bridge(opened, "campus", "winter")
    _cross(opened, bridge)
    opened.page.wait_for_function(
        "() => window.__S().world === 'winter'", timeout=WAIT_MS
    )
    after = opened.state()
    assert after["doneW"]["campus"] == before["doneW"]["campus"] == [1]
    assert after["name"] == before["name"]
    assert after["done"] == after["doneW"].get("winter", [])
    assert (after.get("items") or []) == (before.get("items") or [])
    # Walking back to the campus is the same bridge, the other way round.
    back = _bridge(opened, "campus", "winter")
    assert back["open"] is True
    opened.assert_clean()


def test_the_world_button_is_still_fast_travel(opened: GamePage) -> None:
    """The flight is a camera move; the world changes when it lands."""
    opened.next_world()
    assert opened.state()["world"] == "winter"
    assert opened.page.evaluate("window.__debug().flying") is False
    opened.assert_clean()


def test_the_minimap_maps_the_archipelago(opened: GamePage) -> None:
    """At phone width the map waits behind its button, then shows everything."""
    info = opened.page.evaluate("window.__minimap()")
    assert info["islands"] == 4, info
    assert info["bridges"] == 3, info
    assert info["phone"] is True and info["open"] is False, info
    opened.page.click("#minimap-btn")
    opened.frames()
    assert opened.page.evaluate("window.__minimap()")["open"] is True
    box = opened.page.locator("#minimap").bounding_box()
    assert box and box["width"] > 40 and box["height"] > 40, box
    painted = opened.page.evaluate(
        """() => { const c = document.getElementById('minimap');
           const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
           let n = 0; for (let i = 3; i < d.length; i += 4) if (d[i] > 0) n++;
           return n; }"""
    )
    assert painted > 500, "the minimap drew nothing"
    opened.assert_clean()


def test_the_archipelago_holds_the_phone_draw_call_budget(
    game_webkit_iphone: GamePage,
) -> None:
    """Three silhouettes and three bridges, and every island stays in budget."""
    phone = game_webkit_iphone
    phone.goto(state={"name": "Lotte", "done": [1], "doneW": {"campus": [1]}})
    phone.resume()
    draws = {}
    for _ in range(4):
        phone.frames(4)
        info = phone.page.evaluate("window.__debug()")
        draws[info["world"]] = info["draws"]
        assert len(info["bridges"]) == 3, info["bridges"]
        phone.next_world()
    assert set(draws) == {"campus", "winter", "desert", "prod"}, draws
    over = {w: n for w, n in draws.items() if n >= 300 or n == 0}
    assert over == {}, f"draw calls out of budget: {draws}"
    phone.screenshot("arch_phone_budget", clip_height=700)
    phone.assert_clean()
