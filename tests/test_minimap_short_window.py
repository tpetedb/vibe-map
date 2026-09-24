"""The minimap and zoom controls stay usable in short desktop windows."""

from __future__ import annotations

import pytest
from playwright.sync_api import Browser

from tests.conftest import GAME_PATH, game_context
from tools import media


@pytest.mark.parametrize("window", [media.GIF_WINDOW, (720, 600), (640, 480)])
def test_short_window_keeps_zoom_clear_of_minimap(
    chromium: Browser, server: str, window: tuple[int, int]
) -> None:
    """The canvas and Bigger button stay clear without moving the normal corner."""
    with game_context(
        chromium,
        viewport={"width": window[0], "height": window[1]},
        device_scale_factor=1,
    ) as page:
        media._load(page, server + GAME_PATH, media.PLAYED)
        media._start(page)
        media._settled(page, "campus")
        boxes = page.evaluate(
            "() => Object.fromEntries(['minimap', 'minimap-big', 'zoom'].map(id => {"
            " const r = document.getElementById(id).getBoundingClientRect();"
            " return [id, {left:r.left,right:r.right,top:r.top,bottom:r.bottom}]}))"
        )
        if window == (640, 480):
            page.locator("#minimap-big").click()
            page.wait_for_function("window.__minimap().big === true")
    zoom = boxes["zoom"]
    for name in ("minimap", "minimap-big"):
        rect = boxes[name]
        assert (
            rect["right"] <= zoom["left"]
            or zoom["right"] <= rect["left"]
            or rect["bottom"] <= zoom["top"]
            or zoom["bottom"] <= rect["top"]
        ), f"{name} intersects zoom in a {window[0]}x{window[1]} window: {boxes}"
    if window == media.GIF_WINDOW:
        assert boxes["minimap"]["right"] == window[0] - 10, boxes
