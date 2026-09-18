"""How the island looks: the framing, the colour pipeline, the light rig.

Every assertion here reads `window.__gfx()`, which reports what the renderer
and the scene are actually set to rather than what the source says, so a
regression in the build or in a setting fails the test. The draw-call budget
is the phone's, because that is the machine the scene has to fit on.
"""

from __future__ import annotations

from typing import Any

import pytest

from tests.conftest import WAIT_MS, GamePage

ALL_DONE = [1, 2, 3, 4, 5, 6, 7, 8]
# The three shapes the report caught the camera cropping the island in: a wide
# desktop window, a near-square one, and a phone held upright.
ASPECTS = [(1440, 900), (1100, 1000), (393, 852)]


def _gfx(game: GamePage) -> dict[str, Any]:
    return game.page.evaluate("window.__gfx()")


def _island(game: GamePage, done: list[int] | None = None) -> GamePage:
    stops = done or []
    game.goto(state={"name": "Lotte", "done": stops, "doneW": {"campus": stops}})
    game.resume()
    return game


def test_the_renderer_tone_maps_with_aces_and_writes_srgb(game: GamePage) -> None:
    """Filmic roll-off and an sRGB framebuffer, set on the r128 renderer."""
    gfx = _gfx(_island(game))
    assert gfx["aces"] is True, gfx["tone"]
    assert gfx["srgb"] is True
    assert 0.6 < gfx["exposure"] < 2.0, gfx["exposure"]
    game.assert_clean()


def test_the_camera_keeps_the_island_in_frame_at_every_aspect(game: GamePage) -> None:
    """The island's shore stays inside the viewport, however the window is shaped."""
    _island(game)
    worst = {}
    for width, height in ASPECTS:
        game.page.set_viewport_size({"width": width, "height": height})
        # The camera eases, so wait for the distance to settle before reading.
        game.still("window.__gfx().cam.dist")
        gfx = _gfx(game)
        worst[f"{width}x{height}"] = round(gfx["rim"], 3)
        shape = f"{width}x{height}"
        assert gfx["rim"] < 1, f"the island is cropped at {shape}: {gfx['rim']}"
        # A fit that framed nothing would also pass the line above.
        assert gfx["rim"] > 0.4, f"the island is lost in the frame at {shape}"
        assert gfx["cam"]["dist"] > gfx["cam"]["fit"] * 0.85, gfx["cam"]
    game.screenshot("gfx_camera_fit", clip_height=700)
    assert len(set(worst.values())) > 1, f"the fit ignores the aspect ratio: {worst}"
    game.assert_clean()


def test_the_light_rig_follows_the_sky_stage(game: GamePage) -> None:
    """Eight stops done is midnight: the sun is dimmer, colder, and a moon."""
    day = _gfx(_island(game))
    assert day["stage"] == 0, day["stage"]
    assert day["sun_disc"] is True and day["moon_disc"] is False

    night_page = _island(game, ALL_DONE)
    game.page.wait_for_function("() => window.__gfx().stage === 8", timeout=WAIT_MS)
    game.still("window.__gfx().sun.i")
    night = _gfx(night_page)
    assert night["sun"]["i"] < day["sun"]["i"] * 0.5, (day["sun"], night["sun"])
    assert night["hemi"] < day["hemi"], (day["hemi"], night["hemi"])
    assert night["amb"] < day["amb"], (day["amb"], night["amb"])
    assert night["moon_disc"] is True and night["sun_disc"] is False

    # Cold at night, warm by day: compare the blue channel against the red.
    def _cool(hex_colour: str) -> bool:
        red, blue = int(hex_colour[1:3], 16), int(hex_colour[5:7], 16)
        return blue > red

    assert _cool(night["sun"]["c"]), night["sun"]["c"]
    assert not _cool(day["sun"]["c"]), day["sun"]["c"]
    # The light still comes from above, or nothing on the island is lit at all.
    assert night["sun"]["up"] is True, night["sun"]
    game.screenshot("gfx_night_rig", clip_height=700)
    game.assert_clean()


def test_the_sky_the_sea_and_the_contact_shadows_are_built(game: GamePage) -> None:
    """One dome, one shader-driven sea, one instanced decal for every blob."""
    gfx = _gfx(_island(game))
    assert gfx["sky"] is True, "no sky dome"
    assert gfx["sea"] is True, "the sea has no uniforms, so it is not animated"
    assert gfx["blobs"] > 10, f"only {gfx['blobs']} contact shadows"
    game.assert_clean()


def test_distant_name_plates_are_not_drawn(game: GamePage) -> None:
    """A plate costs a draw call, so only the ones near the walker are drawn."""
    gfx = _gfx(_island(game, ALL_DONE))
    plates = gfx["plates"]
    assert plates["total"] > 10, plates
    assert plates["shown"] < plates["total"], plates
    game.assert_clean()


def test_a_finished_island_holds_the_phone_draw_call_budget(
    game_webkit_iphone: GamePage,
) -> None:
    """Eight buildings, eight annexes and eight causeways, still inside 300."""
    phone = game_webkit_iphone
    phone.goto(
        state={
            "name": "Lotte",
            "done": ALL_DONE,
            "doneW": {w: ALL_DONE for w in ("campus", "winter", "desert", "prod")},
        }
    )
    phone.resume()
    draws = {}
    for _ in range(4):
        phone.frames(4)
        info = phone.page.evaluate("window.__debug()")
        draws[info["world"]] = info["draws"]
        assert phone.page.evaluate("window.__gfx().lit") > 0, "no windows to light"
        phone.next_world()
    assert set(draws) == {"campus", "winter", "desert", "prod"}, draws
    over = {w: n for w, n in draws.items() if n >= 300 or n == 0}
    assert over == {}, f"a finished island is out of budget: {draws}"
    phone.screenshot("gfx_phone_finished_budget", clip_height=700)
    phone.assert_clean()


@pytest.mark.parametrize("shadows", ["high", "low", "off"])
def test_every_shadow_setting_still_renders_the_island(
    game: GamePage, shadows: str
) -> None:
    """The contact shadows are what ground the props when the map is off."""
    _island(game)
    game.page.evaluate("s => window.setSetting('shadows', s)", shadows)
    game.frames(4)
    gfx = _gfx(game)
    assert gfx["blobs"] > 10, gfx["blobs"]
    assert game.page.evaluate("window.__debug().draws") > 0
    game.assert_clean()
