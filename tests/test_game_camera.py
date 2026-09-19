"""The camera, its zoom and the 3D view's manners.

Zoom is one number in `S.settings.zoom`: -1 is close on the walker, 0 is the
fitted island, 1 is the archipelago. Every test here drives it through a real
input (the wheel, a key, a button, two fingers) and reads what the page says
through `window.__gfx()`, `window.__pet()` and `window.__debug()`, waiting on
those facts and never on a count of frames that a slow runner would stretch.

Both phones, always: the WebKit iPhone profile and the Chromium Pixel 7 one.
Chromium gets a real two finger gesture through the DevTools protocol; WebKit
has no such channel in Playwright, so there the same gesture is dispatched as
Pointer Events on the canvas, which is the API the game listens to.
"""

from __future__ import annotations

from typing import Any

import pytest

from tests.conftest import STORAGE_KEY, WAIT_MS, GamePage

ALL_DONE = [1, 2, 3, 4, 5, 6, 7, 8]
LANDED = "window.__gfx().cam.off < 0.5"
PHONES = ["game_android", "game_webkit_iphone"]


def _gfx(game: GamePage) -> dict[str, Any]:
    return game.page.evaluate("window.__gfx()")


def _zoom(game: GamePage) -> float:
    return game.page.evaluate("window.__gfx().zoom.target")


def _island(
    game: GamePage,
    *,
    done: list[int] | None = None,
    zoom: float | None = None,
    pet: str = "duck",
) -> GamePage:
    stops = done or []
    state: dict[str, Any] = {
        "name": "Lotte",
        "done": stops,
        "doneW": {"campus": stops},
        "pet": pet,
    }
    if zoom is not None:
        state["settings"] = {"zoom": zoom}
    game.goto(state=state)
    game.resume()
    game.until(LANDED)
    return game


def _zoom_is(game: GamePage, level: float) -> None:
    game.page.wait_for_function(
        "z => Math.abs(window.__gfx().zoom.target - z) < 0.001",
        arg=level,
        timeout=WAIT_MS,
    )


def _stage_point(game: GamePage, fx: float, fy: float) -> tuple[float, float]:
    box = game.page.evaluate(
        "(() => { const r = document.getElementById('c').getBoundingClientRect();"
        " return [r.left, r.top, r.width, r.height]; })()"
    )
    return box[0] + box[2] * fx, box[1] + box[3] * fy


def _pinch(game: GamePage, start: float, end: float, *, steps: int = 6) -> None:
    """Two fingers on the open ground, moved from `start` to `end` pixels apart."""
    cx, cy = _stage_point(game, 0.45, 0.5)

    def points(span: float) -> list[dict[str, float]]:
        return [
            {"x": cx - span / 2, "y": cy, "id": 0},
            {"x": cx + span / 2, "y": cy + 4, "id": 1},
        ]

    spans = [start + (end - start) * i / steps for i in range(steps + 1)]
    if game.page.context.browser.browser_type.name == "chromium":
        cdp = game.page.context.new_cdp_session(game.page)
        touch = "Input.dispatchTouchEvent"
        cdp.send(touch, {"type": "touchStart", "touchPoints": points(spans[0])[:1]})
        cdp.send(touch, {"type": "touchStart", "touchPoints": points(spans[0])})
        for span in spans[1:]:
            cdp.send(touch, {"type": "touchMove", "touchPoints": points(span)})
        cdp.send(touch, {"type": "touchEnd", "touchPoints": []})
        cdp.detach()
        return
    game.page.evaluate(
        """([frames]) => {
          const c = document.getElementById('c');
          const fire = (type, p) => c.dispatchEvent(new PointerEvent(type, {
            pointerId: 10 + p.id, pointerType: 'touch', isPrimary: p.id === 0,
            clientX: p.x, clientY: p.y, bubbles: true, cancelable: true }));
          frames[0].forEach(p => fire('pointerdown', p));
          frames.slice(1).forEach(f => f.forEach(p => fire('pointermove', p)));
          frames[frames.length - 1].forEach(p => fire('pointerup', p));
        }""",
        [[points(span) for span in spans]],
    )


def test_the_walk_starts_close_and_zero_shows_the_whole_island(
    game_desktop: GamePage,
) -> None:
    """A fresh browser frames the walker; the 0 key returns the fitted island."""
    game = _island(game_desktop)
    gfx = _gfx(game)
    assert gfx["zoom"]["target"] == pytest.approx(gfx["zoom"]["start"])
    assert gfx["zoom"]["start"] < 0, "the default is the close view"
    assert gfx["rim"] > 1, "close on the walker, the shore is outside the frame"
    close = gfx["zoom"]["dist"]
    game.page.keyboard.press("0")
    _zoom_is(game, 0)
    game.until(LANDED)
    gfx = _gfx(game)
    assert gfx["rim"] < 1, f"the fitted view crops the island: {gfx['rim']}"
    assert gfx["zoom"]["dist"] > close * 1.5
    assert game.page.get_attribute("#zoom-fit", "aria-pressed") == "true"
    game.screenshot("camera_fitted")
    game.assert_clean()


def test_the_wheel_zooms_both_ways_and_stops_at_the_ends(
    game_desktop: GamePage,
) -> None:
    game = _island(game_desktop, zoom=0)
    x, y = _stage_point(game, 0.5, 0.5)
    game.page.mouse.move(x, y)
    game.page.mouse.wheel(0, -240)
    game.until("window.__gfx().zoom.target < -0.2")
    game.page.mouse.wheel(0, 240)
    # Back through the fitted view, which holds the level like a detent.
    _zoom_is(game, 0)
    for _ in range(12):
        game.page.mouse.wheel(0, 400)
    _zoom_is(game, 1)
    game.until(LANDED)
    assert game.page.is_disabled("#zoom-out"), "nothing further out than this"
    far = _gfx(game)
    assert far["plates"]["shown"] == 0, "no plates over the archipelago"
    game.screenshot("camera_archipelago")
    for _ in range(24):
        game.page.mouse.wheel(0, -400)
    _zoom_is(game, -1)
    assert game.page.is_disabled("#zoom-in")
    assert game.page.evaluate("window.scrollY") == 0, "the wheel scrolled the page"
    game.assert_clean()


def test_a_trackpad_pinch_zooms_the_island_and_not_the_page(
    game_desktop: GamePage,
) -> None:
    """A trackpad pinch arrives as a wheel with ctrlKey, which is page zoom."""
    game = _island(game_desktop, zoom=0)
    x, y = _stage_point(game, 0.5, 0.5)
    game.page.mouse.move(x, y)
    ratio = game.page.evaluate("window.devicePixelRatio")
    game.page.keyboard.down("Control")
    game.page.mouse.wheel(0, -60)
    game.page.keyboard.up("Control")
    game.until("window.__gfx().zoom.target < -0.3")
    assert game.page.evaluate("window.devicePixelRatio") == ratio
    assert game.page.evaluate("window.visualViewport.scale") == 1
    game.assert_clean()


def test_plus_and_minus_step_on_a_grid_that_has_the_fitted_view_on_it(
    game_desktop: GamePage,
) -> None:
    game = _island(game_desktop)
    game.page.keyboard.press("-")
    _zoom_is(game, -0.5)
    game.page.keyboard.press("-")
    game.page.keyboard.press("-")
    _zoom_is(game, 0)
    game.page.keyboard.press("+")
    _zoom_is(game, -0.25)
    game.assert_clean()


def test_keys_typed_into_a_field_stay_in_the_field(game_desktop: GamePage) -> None:
    """Arrows move the caret, and neither they nor minus reach the island."""
    game = _island(game_desktop)
    before = game.page.evaluate("window.__debug().pos")
    level = _zoom(game)
    game.open_roadmap()
    game.page.click("#impcode")
    game.page.keyboard.type("abcdef")
    for _ in range(3):
        game.page.keyboard.press("ArrowLeft")
    game.page.keyboard.type("X-0")
    assert game.page.input_value("#impcode") == "abcX-0def"
    game.frames(6)
    after = game.page.evaluate("window.__debug().pos")
    assert after[0] == pytest.approx(before[0], abs=0.01)
    assert after[2] == pytest.approx(before[2], abs=0.01)
    assert _zoom(game) == pytest.approx(level)
    game.assert_clean()


@pytest.mark.parametrize("fixture", PHONES)
def test_the_zoom_buttons_work_under_a_thumb(
    fixture: str, request: pytest.FixtureRequest
) -> None:
    game = _island(request.getfixturevalue(fixture))
    for button in ("#zoom-in", "#zoom-fit", "#zoom-out"):
        box = game.page.locator(button).bounding_box()
        assert box and box["width"] >= 44 and box["height"] >= 44, button
        assert box["x"] + box["width"] <= game.page.viewport_size["width"]
    game.page.tap("#zoom-in")
    _zoom_is(game, -0.75)
    game.page.tap("#zoom-fit")
    _zoom_is(game, 0)
    game.page.tap("#zoom-out")
    _zoom_is(game, 0.25)
    assert game.page.evaluate("window.visualViewport.scale") == 1
    game.assert_clean()


@pytest.mark.parametrize("fixture", PHONES)
def test_two_fingers_zoom_and_never_walk(
    fixture: str, request: pytest.FixtureRequest
) -> None:
    """A pinch moves the camera; the walker and the page stay where they are."""
    game = _island(request.getfixturevalue(fixture), zoom=0)
    before = game.page.evaluate("window.__debug().pos")
    _pinch(game, 90, 260)
    game.until("window.__gfx().zoom.target < -0.3")
    game.until(LANDED)
    game.screenshot(f"camera_pinch_in_{fixture}", clip_height=915)
    _pinch(game, 260, 40)
    game.until("window.__gfx().zoom.target > 0.3")
    game.frames(8)
    after = game.page.evaluate("window.__debug().pos")
    assert after[0] == pytest.approx(before[0], abs=0.05), "the pinch walked him"
    assert after[2] == pytest.approx(before[2], abs=0.05), "the pinch walked him"
    assert game.page.evaluate("window.visualViewport.scale") == 1
    game.assert_clean()


def test_a_finger_on_the_stick_is_not_half_a_pinch(game_android: GamePage) -> None:
    """One finger steers, a second lands on the ground: that is not a zoom."""
    game = _island(game_android, zoom=0)
    stick = game.page.locator("#joy").bounding_box()
    assert stick
    sx, sy = stick["x"] + stick["width"] / 2, stick["y"] + stick["height"] / 2
    gx, gy = _stage_point(game, 0.6, 0.45)
    cdp = game.page.context.new_cdp_session(game.page)
    touch = "Input.dispatchTouchEvent"
    one = {"x": sx, "y": sy, "id": 0}
    cdp.send(touch, {"type": "touchStart", "touchPoints": [one]})
    for dx in (0, 40, 80, 120):
        two = {"x": gx + dx, "y": gy, "id": 1}
        kind = "touchStart" if dx == 0 else "touchMove"
        cdp.send(touch, {"type": kind, "touchPoints": [one, two]})
    cdp.send(touch, {"type": "touchEnd", "touchPoints": []})
    cdp.detach()
    game.frames(4)
    assert _zoom(game) == 0
    game.assert_clean()


def test_the_zoom_is_state(game_desktop: GamePage) -> None:
    """It survives a reload, and Back to the defaults resets it."""
    game = _island(game_desktop)
    start = _gfx(game)["zoom"]["start"]
    game.page.keyboard.press("-")
    game.page.keyboard.press("-")
    _zoom_is(game, -0.25)
    game.page.wait_for_function(
        "k => (JSON.parse(localStorage.getItem(k)).settings || {}).zoom === -0.25",
        arg=STORAGE_KEY,
        timeout=WAIT_MS,
    )
    game.page.reload()
    game.page.wait_for_function("typeof window.__S === 'function'")
    game.resume()
    _zoom_is(game, -0.25)
    game.hud_action("#hud button:has-text('Settings')")
    game.page.wait_for_selector("#s-settings.on", state="attached")
    game.page.click("#s-settings button:has-text('Back to the defaults')")
    _zoom_is(game, start)
    game.assert_clean()


def test_reduced_motion_steps_the_zoom_and_stills_the_island(
    game_desktop: GamePage,
) -> None:
    """No easing, no clouds, no pulses: two frames of a still island are equal."""
    game_desktop.page.emulate_media(reduced_motion="reduce")
    game = _island(game_desktop, done=[1, 2], zoom=0, pet="none")
    game.page.keyboard.press("+")
    game.frames(2)
    gfx = _gfx(game)
    assert gfx["zoom"]["level"] == pytest.approx(gfx["zoom"]["target"])
    # Tom walks up to the walker when the island starts. That is somebody
    # going somewhere, not ambient motion, so the still frames come after it.
    game.until(
        "(() => { const tom = window.__scene().children.find(o => o.children.some("
        "c => c.isSprite && (c.userData.text || '').startsWith('Tom,')));"
        " const p = window.__debug().pos;"
        " return Math.hypot(tom.position.x - p[0], tom.position.z - p[2]) <= 3.2; })()"
    )
    game.frames(2)
    cloud = gfx["ambient"]
    # The island without the HUD above it or the toasts beside it.
    clip = {"x": 100, "y": 200, "width": 900, "height": 480}
    first = game.page.screenshot(clip=clip)
    game.frames(12)
    assert _gfx(game)["ambient"] == cloud, "the clouds still drift"
    assert game.page.screenshot(clip=clip) == first, "something on the island moves"
    game.assert_clean()


def test_without_reduced_motion_the_island_is_alive(game_desktop: GamePage) -> None:
    game = _island(game_desktop, zoom=0)
    cloud = _gfx(game)["ambient"]
    game.frames(6)
    assert _gfx(game)["ambient"] != cloud
    game.assert_clean()


@pytest.mark.parametrize("fixture", PHONES)
def test_every_zoom_level_holds_the_phone_budget(
    fixture: str, request: pytest.FixtureRequest
) -> None:
    """Draw calls, plates, contact shadows and the pet's pixels, at each level."""
    game = _island(request.getfixturevalue(fixture), done=ALL_DONE)
    for taps, button, level in (
        (2, "#zoom-in", -1),
        (3, "#zoom-out", -0.25),
        (1, "#zoom-fit", 0),
        (4, "#zoom-out", 1),
    ):
        for _ in range(taps):
            game.page.tap(button)
        _zoom_is(game, level)
        game.until(LANDED)
        game.frames(2)
        gfx = _gfx(game)
        pet = game.page.evaluate("window.__pet()")
        draws = game.page.evaluate("window.__debug().draws")
        assert draws < 300, f"{draws} draw calls at zoom {level}"
        assert gfx["blobs"] > 10, "the contact shadows are gone"
        assert pet["on"] and pet["texel"] >= 1
        assert pet["texel"] == int(pet["texel"]), "a sprite pixel is a whole number"
        game.screenshot(f"camera_{fixture}_zoom_{level}", clip_height=915)
    game.assert_clean()


def test_plates_are_legible_from_the_fitted_view_and_do_not_collide(
    game_desktop: GamePage,
) -> None:
    game = _island(game_desktop, zoom=0)
    game.until("window.__gfx().plates.list.some(p => p.o > 0.9)")
    plates = [p for p in _gfx(game)["plates"]["list"] if p["o"] > 0.5]
    assert plates, "no plate near the walker"
    texts = [p["text"] for p in plates]
    assert any(t.startswith("Lotte") for t in texts), texts
    for p in plates:
        assert p["h"] >= 14, f"{p['text']} is {p['h']:.1f} px tall"
    for i, a in enumerate(plates):
        for b in plates[i + 1 :]:
            apart = (
                abs(a["x"] - b["x"]) >= (a["w"] + b["w"]) / 2
                or abs(a["y"] - b["y"]) >= (a["h"] + b["h"]) / 2
            )
            assert apart, f"{a['text']} is drawn over {b['text']}"
    game.assert_clean()


def test_the_hosts_plates_carry_the_roles_of_the_theme(game_desktop: GamePage) -> None:
    game = _island(game_desktop)
    theme = game.page.evaluate("window.__data().config.theme")
    texts = game.page.evaluate(
        "window.__scene().children.flatMap(o => o.children)"
        ".filter(o => o.isSprite && o.userData.text).map(o => o.userData.text)"
    )
    assert "Tom, " + theme["hostRole"] in texts, texts
    assert "Rolinda, " + theme["guideRole"] in texts, texts
    game.assert_clean()


def test_leaving_an_island_gives_its_memory_back(game_desktop: GamePage) -> None:
    """Eight fast travels: what the GPU holds ends where a fresh island starts."""
    game_desktop.page.emulate_media(reduced_motion="reduce")
    game = _island(game_desktop, done=ALL_DONE)
    first = _gfx(game)["mem"]
    peak = dict(first)
    for _ in range(8):
        game.next_world()
        game.frames(2)
        now = _gfx(game)["mem"]
        peak = {k: max(peak[k], now[k]) for k in peak}
    last = _gfx(game)["mem"]
    assert game.page.evaluate("window.__S().world") == "campus"
    assert last["geometries"] <= first["geometries"] * 1.15, (first, last)
    assert last["textures"] <= first["textures"] + 4, (first, last)
    assert peak["geometries"] <= first["geometries"] * 1.6, (first, peak)
    game.assert_clean()


def test_a_walk_leaves_no_dust_behind_on_the_gpu(game_desktop: GamePage) -> None:
    game = _island(game_desktop)
    before = _gfx(game)["mem"]["geometries"]
    for key in ("ArrowRight", "ArrowLeft"):
        game.page.keyboard.down(key)
        game.frames(30)
        game.page.keyboard.up(key)
    game.frames(40)
    assert _gfx(game)["mem"]["geometries"] <= before + 2
    game.assert_clean()


def test_sitting_down_compiles_no_shaders(game_desktop: GamePage) -> None:
    """The laptop's glow is a light the island always has.

    three.js compiles every lit material again when the number of lights
    changes, which froze the frame for a second on every sit and every stand.
    """
    game = _island(game_desktop)
    programs = _gfx(game)["mem"]["programs"]
    game.page.keyboard.press("x")
    game.until("window.__avatar().pose === 'sit'")
    game.frames(3)
    assert _gfx(game)["mem"]["programs"] == programs
    game.page.keyboard.press("x")
    game.until("window.__avatar().pose !== 'sit'")
    game.frames(3)
    assert _gfx(game)["mem"]["programs"] == programs
    game.assert_clean()


def test_a_lost_webgl_context_says_so_and_comes_back(game_desktop: GamePage) -> None:
    game = _island(game_desktop)
    game.page.evaluate(
        "() => { const c = document.getElementById('c');"
        " window.__lose = (c.getContext('webgl2') || c.getContext('webgl'))"
        ".getExtension('WEBGL_lose_context'); window.__lose.loseContext(); }"
    )
    game.until("window.__gfx().lost === true")
    game.page.wait_for_selector("#gfxlost", state="visible")
    game.page.wait_for_selector("#sheet.on #s-map.on", state="attached")
    assert not game.page.is_visible("#enter"), "the proximity button carried on"
    game.screenshot("camera_context_lost")
    game.page.evaluate("window.__lose.restoreContext()")
    game.until("window.__gfx().lost === false")
    game.page.wait_for_selector("#gfxlost", state="hidden")
    game.frames(3)
    # The error collector sees three.js log the loss; nothing else is an error.
    assert [e for e in game.errors if "Context Lost" not in e] == []


def test_a_change_of_pixel_ratio_resizes_the_drawing_buffer(
    game_desktop: GamePage,
) -> None:
    """Browser zoom and a move to another screen both arrive as a resize."""
    game = _island(game_desktop)
    width = game.page.evaluate("document.getElementById('c').clientWidth")
    assert game.page.evaluate("document.getElementById('c').width") == width
    cdp = game.page.context.new_cdp_session(game.page)
    cdp.send(
        "Emulation.setDeviceMetricsOverride",
        {"width": 1440, "height": 900, "deviceScaleFactor": 2, "mobile": False},
    )
    game.page.wait_for_function(
        "w => document.getElementById('c').width === w * 2",
        arg=width,
        timeout=WAIT_MS,
    )
    cdp.detach()
    game.assert_clean()


@pytest.mark.parametrize("fixture", PHONES)
def test_the_companion_cheers_a_claimed_stop(
    fixture: str, request: pytest.FixtureRequest
) -> None:
    game = _island(request.getfixturevalue(fixture))
    game.claim(1)
    game.until("window.__pet().state === 'cheer'")
    game.screenshot(f"camera_pet_cheer_{fixture}", clip_height=915)
    game.assert_clean()
