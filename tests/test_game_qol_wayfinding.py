"""Wayfinding and movement: walk me there, the arrow, the map, hurrying.

Every test presses the control a player presses (a palette button, the arrow
at the edge of the screen, a plot on the map, a key) and then waits for a fact
the page produced: where the walker is, what window.__walk() says, how many
frames the renderer drew. Nothing here waits on a clock, and the one place
where the game counts a minute hands the tests a shorter one so the wait stays
a fact rather than a minute of sleeping.
"""

from __future__ import annotations

import math
from typing import Any

from tests.conftest import WAIT_MS, GamePage

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


def _arrived(game: GamePage) -> None:
    """Wait for the walk to end, which is the walker reaching the marker.

    A walk is the one thing here that takes the renderer's own time rather
    than a moment, so it is given three of the usual budgets. It is still a
    fact the page produced: the walk is over when the game says it is.
    """
    game.page.wait_for_function(
        "() => window.__walk().has === false", timeout=WAIT_MS * 3
    )


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


# ---- the marker stays, and the line to it -------------------------------------


def test_the_marker_and_its_line_stay_up_for_the_whole_walk(
    game_desktop: GamePage,
) -> None:
    game_desktop.goto(state=RETURNING)
    game_desktop.resume()
    _tap_the_ground(game_desktop)
    game_desktop.frames(12)
    walking = _walk(game_desktop)
    assert walking["has"] is True
    # A dozen frames of the old fade left the marker at four fifths; the walk
    # is still on its way, so it is still fully lit, line and all.
    assert walking["marker"] == 1, walking
    assert walking["line"] is True, walking
    _arrived(game_desktop)
    game_desktop.frames(2)
    done = _walk(game_desktop)
    assert done["marker"] == 0, done
    assert done["line"] is False, done
    game_desktop.assert_clean()


def test_steering_away_puts_the_marker_out(game_desktop: GamePage) -> None:
    """One walk at a time: the arrow keys are a new intention, not a detour."""
    game_desktop.goto(state=RETURNING)
    game_desktop.resume()
    _tap_the_ground(game_desktop)
    game_desktop.page.keyboard.down("ArrowDown")
    game_desktop.frames(3)
    game_desktop.page.keyboard.up("ArrowDown")
    walk = _walk(game_desktop)
    assert walk["has"] is False
    assert walk["marker"] == 0, walk
    assert walk["line"] is False, walk
    game_desktop.assert_clean()


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
    game_android.goto(state=RETURNING)
    game_android.resume()
    game_android.until("window.__minimap().guide !== null")
    before = game_android.page.evaluate("() => window.__gfx().zoom.target")
    for _ in range(2):
        game_android.page.tap("#zoom-in")
    game_android.page.wait_for_function(
        "z => window.__gfx().zoom.target < z", arg=before, timeout=WAIT_MS
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
