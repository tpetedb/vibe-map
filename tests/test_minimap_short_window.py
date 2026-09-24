"""The minimap and zoom controls stay usable in short desktop windows."""

from __future__ import annotations

import pytest
from playwright.sync_api import Browser, Page

from tests.conftest import game_page


def _boxes(page: Page) -> dict[str, dict[str, float]]:
    return page.evaluate(
        "() => Object.fromEntries("
        "['minimap', 'minimap-big', 'minimap-btn', 'zoom'].map(id => {"
        " const r = document.getElementById(id).getBoundingClientRect();"
        " return [id, {left:r.left,right:r.right,top:r.top,bottom:r.bottom}]}))"
    )


@pytest.mark.parametrize("window", [(800, 640), (720, 600), (640, 480)])
def test_short_window_keeps_zoom_clear_of_minimap(
    chromium: Browser, server: str, window: tuple[int, int]
) -> None:
    """The canvas and Bigger button stay clear without moving the normal corner."""
    with game_page(
        chromium,
        server,
        viewport={"width": window[0], "height": window[1]},
        device_scale_factor=1,
    ) as game:
        game.goto().start()
        game.until("window.__minimap().painted > 0")
        boxes = _boxes(game.page)
        if window == (640, 480):
            game.page.locator("#minimap-big").click()
            game.until("window.__minimap().big === true")
            game.page.locator("#minimap-big").click()
            game.until("window.__minimap().big === false")
            assert _boxes(game.page)["minimap"] == boxes["minimap"]
        game.assert_clean()
    zoom = boxes["zoom"]
    for name in ("minimap", "minimap-big"):
        rect = boxes[name]
        assert (
            rect["right"] <= zoom["left"]
            or zoom["right"] <= rect["left"]
            or rect["bottom"] <= zoom["top"]
            or zoom["bottom"] <= rect["top"]
        ), f"{name} intersects zoom in a {window[0]}x{window[1]} window: {boxes}"
    if window == (800, 640):
        assert boxes["minimap"]["right"] == window[0] - 10, boxes


@pytest.mark.parametrize("window", [(375, 667), (320, 568)])
def test_phone_map_opens_below_its_toggle_without_shifting(
    chromium: Browser, server: str, window: tuple[int, int]
) -> None:
    with game_page(
        chromium,
        server,
        viewport={"width": window[0], "height": window[1]},
        device_scale_factor=1,
        has_touch=True,
        is_mobile=True,
    ) as game:
        game.goto().start()
        game.page.locator("#minimap-btn").click()
        game.until("window.__minimap().open === true")
        boxes = _boxes(game.page)
        assert boxes["minimap"]["right"] == window[0] - 10, boxes
        assert boxes["minimap-btn"]["right"] == window[0] - 10, boxes
        game.assert_clean()
