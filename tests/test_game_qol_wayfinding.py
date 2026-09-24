"""Wayfinding and movement: walk me there, the arrow, the map, hurrying.

Every test presses what a player presses (a palette button, a plot on the map,
a stop in its list, a key, the stick) and then waits for a fact the page
produced: where the walker is, what window.__walk() says, how many frames the
renderer drew. The arrow at the edge of the screen is read rather than
pressed, because it takes no press. Nothing here waits on a clock, and the one
place where the game counts a minute hands the tests a shorter one so the wait
stays a fact rather than a minute of sleeping.
"""

from __future__ import annotations

import io
import math
from collections.abc import Iterator
from typing import Any

import pytest
from playwright.sync_api import Browser

from tests.conftest import SHOT_MS, WAIT_MS, GamePage, game_page

# A returning player two stops in: stop 3 is the next one, on the campus.
RETURNING: dict[str, Any] = {
    "name": "Tom",
    "look": "own",
    "doneW": {"campus": [1, 2]},
}
NEXT_STOP = 3
# The hour a stop is named by sorts it to the top of the palette; a note and a
# mentor carry words, not times.
NEXT_QUERY = "20:00"

# Counting rendered frames against animation frames: the browser hands out
# both, so the ratio is the page's own answer to "is every frame drawn".
FRAME_RATIO = """n => new Promise(done => {
  const start = window.__debug().frame;
  let ticks = 0;
  const step = () => {
    if (++ticks >= n) return done(window.__debug().frame - start);
    requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
})"""
TICKS = 16


@pytest.fixture
def game_small(chromium: Browser, server: str) -> Iterator[GamePage]:
    """A window a quarter of the laptop's, for the one walk that is a long one.

    A software renderer is paid by the pixel, and the game moves the walker by
    a frame's worth of ground per frame however long the frame took. A walk
    right across the island is a hundred frames and more, so it is watched
    through a window that draws them three times as fast.
    """
    with game_page(chromium, server, viewport={"width": 640, "height": 400}) as gp:
        yield gp


def _walk(game: GamePage) -> dict[str, Any]:
    return dict(game.page.evaluate("() => window.__walk()"))


def _map(game: GamePage) -> dict[str, Any]:
    return dict(game.page.evaluate("() => window.__minimap()"))


def _distance(game: GamePage, target: list[float]) -> float:
    pos = game.page.evaluate("() => window.__debug().pos")
    return math.hypot(pos[0] - target[0], pos[2] - target[1])


def _plot(game: GamePage, n: int) -> list[float]:
    """Where stop n stands, from the map that draws it."""
    return list(_map(game)["at"][n - 1])


def _aimed_at(game: GamePage, n: int) -> dict[str, Any]:
    """The walk is on, and its destination is stop n and no other."""
    walk = _walk(game)
    assert walk["has"] is True, walk
    want = _plot(game, n)
    assert math.hypot(walk["target"][0] - want[0], walk["target"][1] - want[1]) < 0.01
    return walk


def _closing_in(game: GamePage, target: list[float], by: float = 1.5) -> None:
    """Wait for the walker to have covered ground towards the destination.

    A software renderer draws a handful of frames a second, so walking the
    whole island is minutes. The fact waited for is the distance falling,
    which is the walk happening, and a pace and a half is enough of it.
    """
    start = _distance(game, target)
    game.page.wait_for_function(
        "([x, z, d]) => {const p = window.__debug().pos;"
        " return Math.hypot(p[0] - x, p[2] - z) < d;}",
        arg=[target[0], target[1], start - by],
        timeout=WAIT_MS,
    )


def _over(game: GamePage) -> None:
    """Wait for the walk to end, however it ends.

    A walk is the one thing here that takes the renderer's own time rather
    than a moment, so it is given three of the usual budgets. It is still a
    fact the page produced: the walk is over when the game says it is.
    """
    game.until(
        "window.__walk().has === false",
        what="the end of the walk",
        budget=WAIT_MS * 3,
    )


def _arrived(game: GamePage, target: list[float]) -> None:
    """The walk is over because the walker is standing at its destination."""
    _over(game)
    assert _distance(game, target) < 0.7, game.page.evaluate("window.__debug().pos")
    assert not [t for t in game.toasts() if "Stopped short" in t], game.toasts()


def _open_palette(game: GamePage, query: str) -> None:
    game.hud_action("#hud-search")
    game.page.wait_for_selector("#pal.on", state="attached")
    _type_in_palette(game, query)


def _type_in_palette(game: GamePage, query: str) -> None:
    game.page.fill("#pal-q", query)
    game.page.wait_for_function(
        "q => {const r = document.querySelectorAll('#pal-list .pal-row');"
        " return r.length > 0 && (r[0].textContent || '').includes(q);}",
        arg=query,
        timeout=WAIT_MS,
    )


def _tap_the_ground(game: GamePage) -> None:
    """Click the island a short way from the walker, the way a player does.

    The follow camera keeps the walker near the middle of the screen and the
    ground runs away up it, so a click below the middle is a few paces off:
    far enough to watch the marker, near enough that the walk ends inside a
    test's patience on a renderer that draws three frames a second.
    """
    box = game.page.locator("#c").bounding_box()
    assert box
    game.page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] * 0.62)
    game.page.wait_for_function("() => window.__walk().has === true", timeout=WAIT_MS)


def _walk_there_from_the_palette(game: GamePage) -> None:
    """Send the walker to the next stop, which is across the island."""
    _open_palette(game, NEXT_QUERY)
    game.page.click("#pal-walk")
    game.page.wait_for_selector("#pal:not(.on)", state="attached")
    assert _walk(game)["has"] is True


SPEED = "Math.hypot(window.__debug().vel[0], window.__debug().vel[2])"


def _speed(game: GamePage, key: str, *, modifier: str | None = None) -> float:
    """Hold a direction until the walker stops speeding up, and read the speed.

    The acceleration is a ramp measured in seconds, so a fixed number of
    frames would be a different part of the ramp on a fast machine and on a
    slow one. The plateau is the fact to wait for, and it is reached a pace or
    two from where the walker set off, well short of the shore.
    """
    kb = game.page.keyboard
    if modifier:
        kb.down(modifier)
    kb.down(key)
    try:
        game.frames(4)
        game.still(SPEED)
        speed = float(game.page.evaluate(f"() => {SPEED}"))
    finally:
        kb.up(key)
        if modifier:
            kb.up(modifier)
    game.frames()
    return speed


# ---- walk me there ------------------------------------------------------------


def test_the_palette_walks_the_walker_to_the_stop_it_names(
    game_desktop: GamePage,
) -> None:
    game_desktop.goto(state=RETURNING)
    game_desktop.resume()
    _open_palette(game_desktop, NEXT_QUERY)
    button = game_desktop.page.locator("#pal-walk")
    assert button.is_visible()
    assert (button.get_attribute("aria-label") or "").startswith("Walk to 20:00")
    box = button.bounding_box()
    assert box and box["height"] >= 44, box
    button.click()
    game_desktop.page.wait_for_selector("#pal:not(.on)", state="attached")
    walk = _aimed_at(game_desktop, NEXT_STOP)
    assert walk["marker"] == 1
    # And the walker sets off for it: the distance to the stop falls.
    _closing_in(game_desktop, walk["target"])
    game_desktop.screenshot("wayfinding-desktop-walking")
    game_desktop.assert_clean()


def test_the_palette_offers_no_walk_for_a_note_or_a_mentor(
    game_desktop: GamePage,
) -> None:
    """The action is there for what stands on the island and nothing else."""
    game_desktop.goto(state=RETURNING)
    game_desktop.resume()
    _open_palette(game_desktop, NEXT_QUERY)
    assert game_desktop.page.is_visible("#pal-walk")
    _type_in_palette(game_desktop, "Rolinda")
    assert not game_desktop.page.is_visible("#pal-walk")
    game_desktop.assert_clean()


def test_shift_and_enter_walks_instead_of_opening(game_desktop: GamePage) -> None:
    game_desktop.goto(state=RETURNING)
    game_desktop.resume()
    _open_palette(game_desktop, NEXT_QUERY)
    game_desktop.page.keyboard.press("Shift+Enter")
    game_desktop.page.wait_for_selector("#pal:not(.on)", state="attached")
    # Walking is not opening: the lesson stays shut.
    assert not game_desktop.page.is_visible("#sheet.on")
    _aimed_at(game_desktop, NEXT_STOP)
    game_desktop.assert_clean()


# East of the hub, level with the corner between the hub and its terrace. From
# here the straight line to stop 3 runs into that corner, which is where a
# walker steered straight at its destination was pinned for good.
EAST_OF_THE_HUB = (9.0, 1.4)


def test_a_walk_with_the_hub_in_the_way_goes_round_it_and_arrives(
    game_small: GamePage,
) -> None:
    game_small.goto(state=RETURNING)
    game_small.resume()
    game_small.walk_to(*EAST_OF_THE_HUB, tol=1.0)
    _walk_there_from_the_palette(game_small)
    walk = _aimed_at(game_small, NEXT_STOP)
    # The way is planned when the destination is taken, and it has corners:
    # the hub is between here and there.
    assert walk["corners"], walk
    assert _distance(game_small, walk["target"]) > 25
    _arrived(game_small, walk["target"])
    game_small.assert_clean()


def test_a_walk_that_cannot_get_nearer_ends_and_says_so(
    game_desktop: GamePage,
) -> None:
    """The hub stands on the origin of every island, on ground a tap can reach.

    Nobody can stand there, so the walk gets as near as it can, and then it
    has to end and say so rather than press against the wall under a lit
    marker for as long as the page is open.
    """
    game_desktop.goto(state=RETURNING)
    game_desktop.resume()
    x, y = game_desktop.page.evaluate("() => window.__groundAt(0, 0)")
    game_desktop.page.mouse.click(x, y)
    game_desktop.until("window.__walk().has === true")
    target = _walk(game_desktop)["target"]
    assert math.hypot(*target) < 2, target
    _over(game_desktop)
    game_desktop.toast_said("Stopped short")
    assert _distance(game_desktop, target) > 1.5
    game_desktop.frames(2)
    done = _walk(game_desktop)
    assert done["marker"] == 0, done
    assert done["line"] is False, done
    game_desktop.assert_clean()


# ---- a walk belongs to the island it was taken on -----------------------------


def test_flying_to_another_island_ends_the_walk_at_take_off(
    game_desktop: GamePage,
) -> None:
    game_desktop.goto(state=RETURNING)
    game_desktop.resume()
    _walk_there_from_the_palette(game_desktop)
    game_desktop.hud_action("#hud button:has-text('World')")
    game_desktop.until("window.__debug().flying === true")
    # The flight owns the frame from here on, and the walk is over with it:
    # no marker and no way left lit over an island that is being left.
    game_desktop.frames(1)
    departing = _walk(game_desktop)
    assert departing["has"] is False, departing
    assert departing["marker"] == 0, departing
    assert departing["line"] is False, departing
    game_desktop.until("window.__S().world !== 'campus'")
    game_desktop.frames(2)
    landed = _walk(game_desktop)
    assert landed["has"] is False, landed
    assert landed["marker"] == 0, landed
    assert landed["line"] is False, landed
    game_desktop.assert_clean()


def test_reduced_motion_cuts_to_the_island_and_ends_the_walk_too(
    game_desktop: GamePage,
) -> None:
    """The flight is a cut under reduced motion, and a cut is leaving as well.

    A walk that outlived it steered the walker across the new island towards
    a point of the old one, with nobody at the keys.
    """
    game_desktop.page.emulate_media(reduced_motion="reduce")
    game_desktop.goto(state=RETURNING)
    game_desktop.resume()
    _walk_there_from_the_palette(game_desktop)
    game_desktop.next_world()
    landed = _walk(game_desktop)
    assert landed["has"] is False, landed
    assert landed["marker"] == 0, landed
    assert landed["line"] is False, landed
    game_desktop.still(SPEED)
    assert float(game_desktop.page.evaluate(f"() => {SPEED}")) < 0.3
    game_desktop.assert_clean()


# ---- the marker stays, and the way to it --------------------------------------


def test_the_marker_and_its_line_stay_up_for_the_whole_walk(
    game_desktop: GamePage,
) -> None:
    game_desktop.goto(state=RETURNING)
    game_desktop.resume()
    # A destination across the island, so the walk is long enough to watch
    # whatever speed the renderer is managing.
    _walk_there_from_the_palette(game_desktop)
    for _ in range(12):
        # The marker is lit the moment the destination is taken; the line to
        # it is drawn by the frame loop, so the frame comes first.
        game_desktop.frames(1)
        walking = _walk(game_desktop)
        assert walking["has"] is True, walking
        # A dozen frames of the old fade left the marker at four fifths; the
        # walk is still on its way, so it stays fully lit, line and all.
        assert walking["marker"] == 1, walking
        assert walking["line"] is True, walking
    # And both go out when the walk is over, which a few paces away is.
    _tap_the_ground(game_desktop)
    _arrived(game_desktop, _walk(game_desktop)["target"])
    game_desktop.frames(2)
    done = _walk(game_desktop)
    assert done["marker"] == 0, done
    assert done["line"] is False, done
    game_desktop.assert_clean()


def test_steering_away_puts_the_marker_out(game_desktop: GamePage) -> None:
    """One walk at a time: the arrow keys are a new intention, not a detour."""
    game_desktop.goto(state=RETURNING)
    game_desktop.resume()
    _walk_there_from_the_palette(game_desktop)
    game_desktop.page.keyboard.down("ArrowDown")
    game_desktop.frames(3)
    game_desktop.page.keyboard.up("ArrowDown")
    walk = _walk(game_desktop)
    assert walk["has"] is False
    assert walk["marker"] == 0, walk
    assert walk["line"] is False, walk
    game_desktop.assert_clean()


# Every GL buffer the page asks for from here on is counted. A buffer made in
# a frame is a buffer made sixty times a second, and the renderer's own
# counters say nothing about it: they count what is alive, not what was made.
COUNT_BUFFERS = """() => {
  window.__buffers = 0;
  for (const C of [window.WebGLRenderingContext, window.WebGL2RenderingContext]) {
    if (!C) continue;
    const make = C.prototype.createBuffer;
    C.prototype.createBuffer = function () {
      window.__buffers++;
      return make.call(this);
    };
  }
}"""


# No dust is kicked up while this holds: what an unlucky draw of Math.random,
# or a slow first frame, does to a walk on a runner.
HOLD_DUST = "() => { window.__random = Math.random; Math.random = () => 0.999; }"
LET_DUST = "() => { Math.random = window.__random; }"


@pytest.mark.parametrize("dust", ["any-time", "late"])
def test_a_walk_makes_its_buffers_once_and_not_every_frame(
    game_desktop: GamePage, dust: str
) -> None:
    game_desktop.goto(state=RETURNING)
    game_desktop.resume()
    game_desktop.page.evaluate(COUNT_BUFFERS)
    if dust == "late":
        game_desktop.page.evaluate(HOLD_DUST)
    _walk_there_from_the_palette(game_desktop)
    # The first frames of a walk draw the way for the first time, and what it
    # is drawn with is made then.
    game_desktop.frames(3)
    if dust == "late":
        game_desktop.page.evaluate(LET_DUST)
    # Every puff of dust shares one shape, made when the first is kicked up,
    # and when that is is a random draw per frame; the count starts after it.
    game_desktop.until(
        "window.__scene().children.some(m => m.userData.dust)", what="a dust puff"
    )
    game_desktop.frames(1)
    made = int(game_desktop.page.evaluate("() => window.__buffers"))
    game_desktop.frames(12)
    assert _walk(game_desktop)["has"] is True
    after = int(game_desktop.page.evaluate("() => window.__buffers"))
    assert after - made <= 2, (made, after)
    game_desktop.assert_clean()


# The two colours a dash is made of, as the screen shows them, and how far a
# pixel may be from one and still count: the edge of a plate is blended with
# what is next to it, its middle is not.
DASH_LIGHT = (241, 241, 248)
DASH_DARK = (0, 0, 0)
DASH_NEAR = 24


def _luminance(rgb: tuple[float, float, float]) -> float:
    """Relative luminance, as WCAG defines it for a contrast ratio."""

    def lin(c: float) -> float:
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def _contrast(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    la, lb = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def _the_ground(game: GamePage) -> dict[str, Any]:
    """The middle of the island as the screen shows it: dashes, and the ground.

    The band leaves out the HUD and the toasts above it and the controls
    under it, and it is taken at one image pixel per CSS pixel: what is
    counted is what somebody looking at the screen has to find. A dash is a
    light plate lying on a dark one, so what counts as a pixel of a dash is a
    pixel of the light colour with the dark colour right beside it; a name
    plate or a white flower has one of the two and not the other.
    """
    from PIL import Image, ImageChops, ImageFilter

    size = game.page.viewport_size
    assert size
    clip = {
        "x": 0,
        "y": round(size["height"] * 0.3),
        "width": size["width"],
        "height": round(size["height"] * 0.42),
    }
    shot = game.page.screenshot(clip=clip, scale="css", timeout=SHOT_MS)
    image = Image.open(io.BytesIO(shot)).convert("RGB")

    def mask(colour: tuple[int, int, int]) -> Image.Image:
        found = None
        for channel, want in zip(image.split(), colour, strict=True):
            table = [255 if abs(v - want) <= DASH_NEAR else 0 for v in range(256)]
            part = channel.point(table)
            found = part if found is None else ImageChops.multiply(found, part)
        assert found is not None
        return found

    beside_dark = mask(DASH_DARK).filter(ImageFilter.MaxFilter(7))
    dashes = ImageChops.multiply(mask(DASH_LIGHT), beside_dark)
    # The ground is the pixel in the middle when they are laid out from dark to
    # light: most of the band is ground, whatever stands on it.
    total = image.width * image.height
    seen, ground = 0, (0, 0, 0)
    colours = image.getcolors(total) or []
    for n, c in sorted(colours, key=lambda nc: _luminance(nc[1])):
        seen += n
        if seen >= total / 2:
            ground = c
            break
    return {"dashes": dashes.histogram()[255], "ground": ground}


def _the_way_is_on_the_screen(game: GamePage, shot: str) -> None:
    game.goto(state=dict(RETURNING, settings={"guide": "off"}))
    game.resume()
    game.frames(4)
    before = _the_ground(game)
    _walk_there_from_the_palette(game)
    game.frames(3)
    walk = _walk(game)
    assert walk["line"] is True, walk
    assert len(walk["dashes"]) >= 10, walk
    during = _the_ground(game)
    game.screenshot(shot, clip_height=820)
    # A flag that says the way is visible is not a way anybody can see. Each
    # dash has to have arrived on the screen as itself, light on dark, and a
    # good many pixels of it.
    assert during["dashes"] - before["dashes"] >= 60, (before, during)
    # Three to one is the floor for a graphic. No single colour has it against
    # snow and against lava rock alike, which is why there are two: whatever
    # the ground is, one of them stands out from it, and they do from each
    # other.
    ground = during["ground"]
    assert max(_contrast(DASH_LIGHT, ground), _contrast(DASH_DARK, ground)) >= 3, ground
    assert _contrast(DASH_LIGHT, DASH_DARK) >= 3
    game.assert_clean()


def test_the_way_to_the_marker_can_be_seen_on_the_laptop(
    game_desktop: GamePage,
) -> None:
    _the_way_is_on_the_screen(game_desktop, "wayfinding-desktop-way")


def test_the_way_to_the_marker_can_be_seen_on_a_phone(
    game_android: GamePage,
) -> None:
    """Grass on the Pixel profile is where a one pixel line measured 1.04 to 1."""
    _the_way_is_on_the_screen(game_android, "wayfinding-android-way")


# ---- the arrow at the edge of the screen --------------------------------------


def test_the_arrow_points_at_the_next_stop_with_the_distance(
    game_desktop: GamePage,
) -> None:
    game_desktop.goto(state=RETURNING)
    game_desktop.resume()
    game_desktop.until("window.__minimap().guide !== null")
    guide = _map(game_desktop)["guide"]
    assert guide["stop"] == NEXT_STOP
    assert guide["shown"] is True
    assert guide["said"].endswith(" m"), guide
    assert "Data Warehouse" in guide["name"], guide
    arrow = game_desktop.page.locator("#guide")
    assert arrow.get_attribute("aria-hidden") == "true"
    assert (arrow.text_content() or "").endswith(" m")
    # It follows the camera, so wherever it has got to, the island is still
    # what a tap there reaches: it says where to go and takes no press.
    box = arrow.bounding_box()
    assert box
    under = game_desktop.page.evaluate(
        "([x, y]) => (document.elementFromPoint(x, y) || {}).id",
        [box["x"] + box["width"] / 2, box["y"] + box["height"] / 2],
    )
    assert under == "c", under
    game_desktop.screenshot("wayfinding-desktop-arrow")
    game_desktop.assert_clean()


def test_the_arrow_never_takes_a_tap_from_the_zoom_buttons(
    game_android: GamePage,
) -> None:
    """The one that broke the phone's zoom: nothing of it is a target."""
    game_android.goto(
        state={"name": "Tom", "look": "own", "doneW": {"campus": [1, 2, 3, 4, 5, 6, 7]}}
    )
    game_android.resume()
    game_android.until("window.__minimap().guide !== null")
    button = game_android.page.locator("#zoom button:not(:disabled)").first
    box = button.bounding_box()
    assert box
    under = {
        "id": button.get_attribute("id"),
        "x": box["x"] + box["width"] / 2,
        "y": box["y"] + box["height"] / 2,
    }
    # Put the moving guide on the actual control instead of depending on one
    # camera angle. The real DOM hit test must still see the button below it.
    game_android.page.add_style_tag(
        content=f"#guide{{left:{under['x']}px!important;top:{under['y']}px!important}}"
    )
    hit = game_android.page.evaluate(
        "([x, y]) => document.elementFromPoint(x, y)?.closest('button')?.id || ''",
        [under["x"], under["y"]],
    )
    assert hit == under["id"], hit
    before = game_android.page.evaluate("() => window.__gfx().zoom.target")
    game_android.page.touchscreen.tap(under["x"], under["y"])
    game_android.until(
        f"window.__gfx().zoom.target !== {before}",
        what=f"the zoom to answer a tap on #{under['id']} under the arrow",
    )
    assert _walk(game_android)["has"] is False
    game_android.assert_clean()


def test_the_arrow_stays_on_the_screen_and_clear_of_the_controls(
    game_desktop: GamePage,
) -> None:
    """Wherever the stop is, the arrow is somewhere a finger can reach."""
    game_desktop.goto(state=RETURNING)
    game_desktop.resume()
    game_desktop.until("window.__minimap().guide !== null")
    size = game_desktop.page.viewport_size
    assert size
    for _ in range(2):
        box = game_desktop.page.locator("#guide").bounding_box()
        assert box
        assert box["x"] >= 0 and box["y"] >= 0, box
        assert box["x"] + box["width"] <= size["width"], box
        assert box["y"] + box["height"] <= size["height"] - 90, box
        # Turn the walker and look again: the arrow follows the camera.
        game_desktop.page.keyboard.down("ArrowLeft")
        game_desktop.frames(4)
        game_desktop.page.keyboard.up("ArrowLeft")
        game_desktop.frames(2)
    game_desktop.assert_clean()


def test_the_hardest_difficulties_start_without_the_arrow(
    game_desktop: GamePage,
) -> None:
    game_desktop.goto(state=dict(RETURNING, settings={"difficulty": "god"}))
    game_desktop.resume()
    game_desktop.frames(4)
    assert _map(game_desktop)["guide"] is None
    assert not game_desktop.page.is_visible("#guide")
    game_desktop.assert_clean()


def test_the_arrow_is_off_when_the_setting_says_off(game_desktop: GamePage) -> None:
    """S.settings.guide is the answer anywhere, whatever the difficulty."""
    game_desktop.goto(state=dict(RETURNING, settings={"guide": "off"}))
    game_desktop.resume()
    game_desktop.frames(4)
    assert _map(game_desktop)["guide"] is None
    assert not game_desktop.page.is_visible("#guide")
    game_desktop.assert_clean()


def test_a_finished_island_points_at_the_bridge_that_opened(
    game_desktop: GamePage,
) -> None:
    game_desktop.goto(
        state={
            "name": "Tom",
            "look": "own",
            "doneW": {"campus": [1, 2, 3, 4, 5, 6, 7, 8]},
        }
    )
    game_desktop.resume()
    game_desktop.until("window.__minimap().guide !== null")
    guide = _map(game_desktop)["guide"]
    assert guide["stop"] == 0, guide
    assert guide["name"].startswith("the bridge to "), guide
    game_desktop.assert_clean()


# ---- the map you can tap ------------------------------------------------------


def test_tapping_a_plot_on_the_map_walks_there(game_desktop: GamePage) -> None:
    game_desktop.goto(state=RETURNING)
    game_desktop.resume()
    game_desktop.until("window.__minimap().painted > 0")
    plots = _map(game_desktop)["plots"]
    assert len(plots) >= 4
    x, y = plots[3]
    game_desktop.page.mouse.click(x, y)
    # The fourth plot is where the tap landed, so the fourth stop is where the
    # walk goes, and the walker sets off for it.
    walk = _aimed_at(game_desktop, 4)
    assert walk["marker"] == 1, walk
    game_desktop.assert_clean()


def test_the_big_map_lists_every_stop_as_a_button(game_desktop: GamePage) -> None:
    game_desktop.goto(state=RETURNING)
    game_desktop.resume()
    game_desktop.until("window.__minimap().painted > 0")
    small = _map(game_desktop)["size"]
    game_desktop.page.click("#minimap-big")
    game_desktop.until("window.__minimap().big === true")
    big = _map(game_desktop)
    assert big["size"] > small
    assert big["stops"] == 8
    button = game_desktop.page.locator("#minimap-stops button").nth(4)
    assert (button.get_attribute("aria-label") or "").startswith("Walk to ")
    box = button.bounding_box()
    assert box and box["height"] >= 44, box
    game_desktop.screenshot("wayfinding-desktop-big-map")
    button.click()
    _aimed_at(game_desktop, 5)
    # The map has said what it had to say.
    game_desktop.until("window.__minimap().big === false")
    game_desktop.assert_clean()


def test_the_map_button_says_whether_the_map_is_big(game_desktop: GamePage) -> None:
    game_desktop.goto(state=RETURNING)
    game_desktop.resume()
    game_desktop.until("window.__minimap().painted > 0")
    button = game_desktop.page.locator("#minimap-big")
    assert button.get_attribute("aria-pressed") == "false"
    assert (button.get_attribute("aria-label") or "").startswith("Enlarge")
    button.click()
    game_desktop.until("window.__minimap().big === true")
    assert button.get_attribute("aria-pressed") == "true"
    assert (button.get_attribute("aria-label") or "").startswith("Shrink")
    assert (button.text_content() or "") == "Smaller"
    game_desktop.assert_clean()


def test_escape_closes_the_big_map(game_desktop: GamePage) -> None:
    game_desktop.goto(state=RETURNING)
    game_desktop.resume()
    game_desktop.until("window.__minimap().painted > 0")
    game_desktop.page.click("#minimap-big")
    game_desktop.until("window.__minimap().big === true")
    game_desktop.page.keyboard.press("Escape")
    game_desktop.until("window.__minimap().big === false")
    assert not game_desktop.page.is_visible("#minimap-stops")
    game_desktop.assert_clean()


def test_a_long_press_on_the_map_opens_it_big(game_android: GamePage) -> None:
    """The gesture the proposal asks for, next to the button that does it too.

    Playwright has no press that is held, so the pointer event a finger would
    send is sent, and the wait is for the map the page then opens.
    """
    game_android.goto(state=RETURNING)
    game_android.resume()
    game_android.page.click("#minimap-btn")
    game_android.until("window.__minimap().painted > 0")
    canvas = game_android.page.locator("#minimap")
    box = canvas.bounding_box()
    assert box
    where = {
        "pointerType": "touch",
        "clientX": box["x"] + box["width"] / 2,
        "clientY": box["y"] + box["height"] / 2,
    }
    canvas.dispatch_event("pointerdown", where)
    game_android.until("window.__minimap().big === true")
    canvas.dispatch_event("pointerup", where)
    # A press that became the big map is not also a tap on a plot.
    assert _walk(game_android)["has"] is False
    game_android.assert_clean()


# ---- hurrying -----------------------------------------------------------------


def test_holding_the_key_hurries_the_walker(game_desktop: GamePage) -> None:
    game_desktop.goto(state=RETURNING)
    game_desktop.resume()
    walk = _speed(game_desktop, "ArrowUp")
    assert not _walk(game_desktop)["run"]
    run = _speed(game_desktop, "ArrowUp", modifier="Shift")
    assert run > walk * 1.25, (walk, run)
    game_desktop.assert_clean()


def test_nothing_has_to_be_held_down_to_hurry(game_desktop: GamePage) -> None:
    """The alternative for a hand that cannot hold a key: one press latches."""
    game_desktop.goto(state=dict(RETURNING, settings={"run": "toggle"}))
    game_desktop.resume()
    walk = _speed(game_desktop, "ArrowUp")
    game_desktop.page.keyboard.press("Shift")
    assert _walk(game_desktop)["run"] is True
    run = _speed(game_desktop, "ArrowUp")
    assert run > walk * 1.25, (walk, run)
    game_desktop.page.keyboard.press("Shift")
    assert _walk(game_desktop)["run"] is False
    # A latch is said as well as set: nothing else on the screen shows it.
    assert [t for t in game_desktop.toasts() if t.startswith("Hurrying")]
    assert [
        t for t in game_desktop.toasts() if t.startswith("Walking") and "Shift" in t
    ]
    game_desktop.assert_clean()


def test_the_shift_of_shift_and_tab_is_not_a_request_to_hurry(
    game_desktop: GamePage,
) -> None:
    """Whoever this setting is for is likely to move through the page by keyboard."""
    game_desktop.goto(state=dict(RETURNING, settings={"run": "toggle"}))
    game_desktop.resume()
    game_desktop.page.keyboard.press("Shift+Tab")
    assert _walk(game_desktop)["run"] is False
    assert not [t for t in game_desktop.toasts() if t.startswith("Hurrying")]
    game_desktop.assert_clean()


def test_the_stick_pushed_to_its_rim_hurries_too(game_android: GamePage) -> None:
    """On a phone there is no key to hold, so the rim of the stick is it."""
    game_android.goto(state=RETURNING)
    game_android.resume()
    box = game_android.page.locator("#joy").bounding_box()
    assert box
    cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    page = game_android.page
    page.mouse.move(cx, cy)
    page.mouse.down()
    try:
        page.mouse.move(cx, cy - box["height"] / 4)
        game_android.frames(4)
        game_android.still(SPEED)
        half = float(page.evaluate(f"() => {SPEED}"))
        assert _walk(game_android)["run"] is False
        page.mouse.move(cx, cy - box["height"])
        game_android.frames(4)
        game_android.still(SPEED)
        rim = float(page.evaluate(f"() => {SPEED}"))
        assert _walk(game_android)["run"] is True
    finally:
        page.mouse.up()
    assert rim > half * 1.25, (half, rim)
    game_android.assert_clean()


# ---- the battery saver --------------------------------------------------------


def test_an_island_nobody_is_touching_draws_half_the_frames(
    game_desktop: GamePage,
) -> None:
    game_desktop.goto(state=RETURNING)
    game_desktop.resume()
    game_desktop.page.evaluate("() => window.__saverAfter(0)")
    game_desktop.until("window.__saver().half === true")
    drawn = int(game_desktop.page.evaluate(FRAME_RATIO, TICKS))
    assert drawn <= TICKS * 0.65, drawn
    game_desktop.assert_clean()


def test_a_key_brings_the_frames_back(game_desktop: GamePage) -> None:
    game_desktop.goto(state=RETURNING)
    game_desktop.resume()
    # Four hundred milliseconds of nobody there, so the state under test is
    # reached without a wait on a clock: the page says when it is in it.
    game_desktop.page.evaluate("() => window.__saverAfter(400)")
    game_desktop.until("window.__saver().half === true")
    game_desktop.page.keyboard.press("ArrowUp")
    assert game_desktop.page.evaluate("() => window.__saver().half") is False
    game_desktop.frames(4)
    game_desktop.assert_clean()


def test_a_press_anywhere_counts_as_somebody_being_there(
    game_android: GamePage,
) -> None:
    """The one that broke the phone's zoom: the island is not the only control.

    A player stepping through the zoom is present, so the saver must not start
    halving the frames the zoom spring is settling on.
    """
    game_android.goto(state=RETURNING)
    game_android.resume()
    game_android.page.evaluate("() => window.__saverAfter(400)")
    game_android.until("window.__saver().half === true")
    game_android.page.tap("#zoom-in")
    assert game_android.page.evaluate("() => window.__saver().half") is False
    game_android.assert_clean()


def test_the_saver_turned_off_keeps_every_frame(game_desktop: GamePage) -> None:
    game_desktop.goto(state=dict(RETURNING, settings={"saver": "off"}))
    game_desktop.resume()
    game_desktop.page.evaluate("() => window.__saverAfter(0)")
    game_desktop.frames(4)
    assert game_desktop.page.evaluate("() => window.__saver().half") is False
    drawn = int(game_desktop.page.evaluate(FRAME_RATIO, TICKS))
    assert drawn >= TICKS * 0.8, drawn
    game_desktop.assert_clean()


def test_an_open_lesson_is_never_halved(game_desktop: GamePage) -> None:
    """Somebody could be reading or typing in there, so the island waits."""
    game_desktop.goto(state=RETURNING)
    game_desktop.resume()
    game_desktop.open_workstream(1)
    game_desktop.page.evaluate("() => window.__saverAfter(0)")
    game_desktop.frames(4)
    assert game_desktop.page.evaluate("() => window.__saver().half") is False
    game_desktop.assert_clean()


# ---- both phones --------------------------------------------------------------


def _phone_map(game: GamePage, shot: str) -> None:
    """The map opens, grows, and walks the walker, all with fingers."""
    game.goto(state=RETURNING)
    game.resume()
    game.page.click("#minimap-btn")
    game.until("window.__minimap().open === true")
    game.page.click("#minimap-big")
    game.until("window.__minimap().big === true")
    assert _map(game)["stops"] == 8
    game.screenshot(shot, clip_height=820)
    button = game.page.locator("#minimap-stops button").nth(2)
    box = button.bounding_box()
    assert box and box["height"] >= 44, box
    button.click()
    _aimed_at(game, 3)
    # The map was covering the island the walk happens on.
    game.until("window.__minimap().open === false")
    game.assert_clean()


def test_the_map_walks_you_there_on_android(game_android: GamePage) -> None:
    _phone_map(game_android, "wayfinding-android-map")


def test_the_map_walks_you_there_on_iphone(game_webkit_iphone: GamePage) -> None:
    _phone_map(game_webkit_iphone, "wayfinding-iphone-map")


def test_the_arrow_fits_both_phones(
    game_android: GamePage, game_webkit_iphone: GamePage
) -> None:
    for game, shot in ((game_android, "android"), (game_webkit_iphone, "iphone")):
        game.goto(state=RETURNING)
        game.resume()
        game.until("window.__minimap().guide !== null")
        size = game.page.viewport_size
        assert size
        box = game.page.locator("#guide").bounding_box()
        assert box and box["height"] >= 44, box
        assert box["x"] >= 0 and box["x"] + box["width"] <= size["width"], box
        assert box["y"] >= 0 and box["y"] + box["height"] <= size["height"] - 90, box
        game.screenshot(f"wayfinding-{shot}-arrow", clip_height=820)
        game.assert_clean()


def test_losing_window_focus_releases_the_hurry_key(game_small: GamePage) -> None:
    game_small.goto(state=RETURNING)
    game_small.resume()
    game_small.page.keyboard.down("Shift")
    assert _walk(game_small)["run"] is True
    # A focus-loss event is the browser signal sent when the player switches apps.
    game_small.page.evaluate("() => window.dispatchEvent(new Event('blur'))")
    assert _walk(game_small)["run"] is False
    game_small.page.keyboard.up("Shift")
    game_small.assert_clean()
