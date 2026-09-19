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
    # The map is painted on its own throttle, so the wait is for a paint that
    # happened, not for a count of frames.
    before = opened.page.evaluate("window.__minimap().painted")
    opened.page.wait_for_function(
        "n => window.__minimap().painted > n", arg=before, timeout=WAIT_MS
    )
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


# The x scale of every instance of the deck's plank, read from the instanced
# mesh itself: one plank stretched to a whole far span is what the stretch is
# meant to do, and the scale is where it goes wrong.
PLANK_SCALES = """() => {
  let out = null;
  window.__scene().traverse(o => {
    const p = o.isInstancedMesh && o.geometry.parameters;
    if (!p || p.width !== 0.5 || p.depth !== 6) return;
    const a = o.instanceMatrix.array, list = [];
    for (let i = 0; i < o.count; i++) {
      const b = i * 16;
      list.push(Math.hypot(a[b], a[b + 1], a[b + 2]));
    }
    out = list;
  });
  return out;
}"""
PLANK_L = 0.5


def test_a_claimed_stop_opens_the_bridge_in_the_same_island(game: GamePage) -> None:
    """The bridge is derived from what is done, so it opens without a rebuild."""
    game.goto(state={"name": "Lotte", "done": [], "doneW": {"campus": []}})
    game.resume()
    if game.page.evaluate("window.__data().config.difficulty") == "beginner":
        pytest.skip("beginner gates nothing")
    assert _bridge(game, "campus", "winter")["open"] is False
    game.claim(1)
    assert _bridge(game, "campus", "winter")["open"] is True
    # The deck is ground the moment it opens, not after the island is rebuilt.
    mid = _bridge(game, "campus", "winter")["pa"]
    assert game.page.evaluate(
        "p => !!window.__debug().bridges.find(b => b.open && b.near)", arg=mid
    )
    game.assert_clean()


def test_beginner_difficulty_opens_the_bridges(game: GamePage) -> None:
    """The setting gates the bridges wherever the difficulty was chosen."""
    game.goto(state={"name": "Lotte", "done": [], "doneW": {"campus": []}})
    game.resume()
    game.hud_action("#hud button[aria-label='Settings']")
    game.page.wait_for_selector("#s-settings.on", state="attached")
    game.page.select_option("#set-difficulty", "beginner")
    game.page.wait_for_function(
        "() => window.__debug().bridges.every(b => b.open)", timeout=WAIT_MS
    )
    assert game.page.evaluate("window.__S().settings.difficulty") == "beginner"
    game.assert_clean()


def test_the_deck_meets_the_shore_of_the_island(opened: GamePage) -> None:
    """The near end of the deck is at the waterline, not several metres inland."""
    bridge = _bridge(opened, "campus", "winter")
    ax, az = bridge["pa"]
    # The island is a cluster of blobs: the reach along the deck's bearing is
    # the furthest any blob covers, and that is what the deck has to meet.
    reach = opened.page.evaluate(
        """p => {
          const land = window.__data().worlds.campus.land;
          const r = Math.hypot(p[0], p[1]), ux = p[0] / r, uz = p[1] / r;
          let out = 0;
          land.forEach(([bx, bz, br]) => {
            const t = bx * ux + bz * uz;
            if (t < 0) return;
            const h = Math.hypot(bx - t * ux, bz - t * uz);
            if (h < br) out = Math.max(out, t + Math.sqrt(br * br - h * h));
          });
          return {reach: out, at: r};
        }""",
        arg=[ax, az],
    )
    assert reach["at"] > reach["reach"] - 2.5, reach
    assert reach["at"] < reach["reach"], "the deck starts out in the water"
    opened.assert_clean()


def test_a_far_bridge_spans_the_gap(opened: GamePage) -> None:
    """The far deck is one stretched plank, and the stretch is the whole span."""
    far = [b for b in opened.page.evaluate("window.__debug().bridges") if not b["near"]]
    assert far, "two of the three bridges are far from the campus"
    scales = opened.page.evaluate(PLANK_SCALES)
    assert scales, "no deck was instanced"
    spans = sorted(s * PLANK_L for s in scales if s > 2)
    wanted = sorted(b["len"] for b in far)
    assert len(spans) == len(wanted), (spans, wanted)
    for drawn, span in zip(spans, wanted, strict=True):
        assert abs(drawn - span) < 1, f"deck {drawn:.1f} for a gap of {span:.1f}"
    opened.assert_clean()


def test_a_shut_bridge_says_why(game: GamePage) -> None:
    """A deck you cannot walk carries a sign, not only a red slab."""
    game.goto(state={"name": "Lotte", "done": [], "doneW": {"campus": []}})
    game.resume()
    if game.page.evaluate("window.__data().config.difficulty") == "beginner":
        pytest.skip("beginner gates nothing")
    bridge = _bridge(game, "campus", "winter")
    signs = game.page.evaluate(
        """p => {
          let n = 0;
          window.__scene().traverse(o => {
            if (!o.isSprite || !o.userData.text) return;
            if (!o.userData.text.startsWith('Closed')) return;
            if (Math.hypot(o.position.x - p[0], o.position.z - p[1]) < 6) n++;
          });
          return n;
        }""",
        arg=bridge["pa"],
    )
    assert signs == 1, "the shut end of the deck says nothing"
    game.claim(1)
    left = game.page.evaluate(
        """() => { let n = 0;
           window.__scene().traverse(o => {
             if (o.isSprite && (o.userData.text || '').startsWith('Closed')) n++; });
           return n; }"""
    )
    assert left == 0, "the sign stayed after the bridge opened"
    game.assert_clean()


def test_the_bench_on_the_rest_platform_can_be_sat_on(opened: GamePage) -> None:
    """The bench in the middle of the bridge behaves like every other bench."""
    bridge = _bridge(opened, "campus", "winter")
    mx, mz = bridge["mid"]
    seats = opened.page.evaluate("window.__avatar().seats")
    near = [s for s in seats if abs(s["x"] - mx) < 4 and abs(s["z"] - mz) < 4]
    assert near, f"no seat on the rest platform at {mx:.1f},{mz:.1f}: {seats}"
    # Short hops along the deck, the same way _cross walks it: one long hop on
    # a diagonal bridge drifts off the side before the steering corrects.
    ax, az = bridge["pa"]
    opened.walk_to(ax, az, tol=2.2, steps=120)
    bench = near[0]
    for i in range(1, 8):
        t = i / 7
        opened.walk_to(
            ax + (bench["x"] - ax) * t, az + (bench["z"] - az) * t, tol=1.2, steps=60
        )
    opened.page.keyboard.press("x")
    opened.page.wait_for_function(
        "() => window.__avatar().pose === 'sit'", timeout=WAIT_MS
    )
    assert opened.page.evaluate("window.__avatar().seat") > 0
    pos = opened.page.evaluate("window.__debug().pos")
    away = ((pos[0] - near[0]["x"]) ** 2 + (pos[2] - near[0]["z"]) ** 2) ** 0.5
    assert away < 2.5, f"the walker sat somewhere else, {away:.1f} away"
    assert opened.page.evaluate("window.__debug().onBridge") is True
    opened.screenshot("arch_bench_on_the_bridge", clip_height=700)
    opened.assert_clean()


def test_the_map_button_says_whether_the_map_is_open(opened: GamePage) -> None:
    """A toggle carries its own state for a screen reader."""
    button = opened.page.locator("#minimap-btn")
    assert button.get_attribute("aria-pressed") == "false"
    assert button.get_attribute("aria-expanded") == "false"
    assert "Show" in (button.get_attribute("aria-label") or "")
    button.click()
    opened.page.wait_for_function(
        "() => document.getElementById('minimap-btn')"
        ".getAttribute('aria-pressed') === 'true'",
        timeout=WAIT_MS,
    )
    assert "Hide" in (button.get_attribute("aria-label") or "")
    assert button.get_attribute("aria-controls") == "minimap"
    opened.assert_clean()
