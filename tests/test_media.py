"""What the media tool promises about the pictures it writes.

The pictures themselves are the documentation, so these tests read the files
that are committed, not a fresh render: a picture that cuts its own subject is
a defect whether or not the tool would make that mistake again.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image, ImageChops
from playwright.sync_api import Browser

from tests.conftest import GAME_PATH, ROOT, game_context
from tools import media

MEDIA = ROOT / "docs" / "media"
# The palette yellow of the Start button, and how much of a row has to be it
# before that row is the button rather than a heading or a badge.
YELLOW = (255, 191, 0)
TOLERANCE = 26
BUTTON_SHARE = 40
BUTTON_TALL = 46


def _rows_of_yellow(picture: Path, floor: float) -> tuple[int, int, int]:
    """The tallest band of rows that is mostly button, and the picture's height.

    Returns (top, bottom, height). A band that ends at the last row is a
    button the clip cut through.
    """
    image = Image.open(picture).convert("RGB")
    bands = [
        channel.point(
            [255 if abs(v - want) <= TOLERANCE else 0 for v in range(256)], "L"
        )
        for channel, want in zip(image.split(), YELLOW, strict=True)
    ]
    mask = ImageChops.multiply(ImageChops.multiply(bands[0], bands[1]), bands[2])
    best, run = (0, 0), None
    for y in range(image.height):
        hit = mask.crop((0, y, image.width, y + 1)).histogram()[255] >= floor
        run = (run[0] if run else y, y) if hit else None
        if run and run[1] - run[0] > best[1] - best[0]:
            best = run
    return best[0], best[1], image.height


@pytest.mark.parametrize(
    ("name", "window"),
    [("hero.png", media.SOCIAL), ("onboarding-start.png", media.DESKTOP)],
)
def test_the_start_button_is_whole_in_the_title_pictures(
    name: str, window: tuple[int, int]
) -> None:
    """The title card is laid out against the window, so a shot clipped to the
    stage cuts the Start button in half. hero.png is the og:image."""
    picture = MEDIA / name
    scale = Image.open(picture).width / window[0]
    top, bottom, tall = _rows_of_yellow(picture, BUTTON_SHARE * scale)
    assert bottom - top > 0, f"{name}: no Start button in the picture"
    assert bottom <= tall - 10 * scale, (
        f"{name}: the Start button runs to the bottom edge ({bottom} of {tall}), "
        "so the picture cuts it"
    )
    assert 0.7 <= (bottom - top + 1) / (BUTTON_TALL * scale) <= 1.3, (
        f"{name}: the Start button is {bottom - top + 1} rows tall, not about "
        f"{round(BUTTON_TALL * scale)}"
    )


def test_the_more_menu_picture_is_the_whole_phone_window() -> None:
    """The More sheet lies on the window's bottom edge, below the stage, so
    the last rows of the menu are only in a picture of the whole window."""
    wide, tall = media.PHONE
    size = Image.open(MEDIA / "phone-more.png").size
    assert size[0] / wide == size[1] / tall, (
        f"phone-more.png is {size}, which is not a {wide}x{tall} window"
    )


def test_a_subject_over_an_edge_is_named() -> None:
    clip = {"x": 0, "y": 0, "width": 393, "height": 748}
    whole = {"x": 12, "y": 450, "width": 369, "height": 200}
    assert media._outside(clip, whole) == ()
    assert media._outside(clip, {**whole, "height": 400}) == ("bottom",)
    assert media._outside(clip, {**whole, "x": -4, "width": 420}) == ("left", "right")
    assert media._outside(clip, None) == ("missing",)


@pytest.mark.parametrize("window", [media.GIF_WINDOW, (640, 480)])
def test_the_gif_window_keeps_the_zoom_column_off_the_minimap(
    chromium: Browser, server: str, window: tuple[int, int]
) -> None:
    """The zoom column sits above the stage's bottom edge and the minimap
    hangs under the HUD at the top of the window, so a short window draws one
    over the other (issue 161). The GIF is recorded where they do not meet."""
    with game_context(
        chromium,
        viewport={"width": window[0], "height": window[1]},
        device_scale_factor=1,
    ) as page:
        media._load(page, server + GAME_PATH, media.PLAYED)
        media._start(page)
        media._settled(page, "campus")
        boxes = page.evaluate(
            "() => ['minimap', 'zoom'].map(id => {"
            " const el = document.getElementById(id);"
            " const r = el.getBoundingClientRect(); return [r.top, r.bottom] })"
        )
    clear = boxes[1][0] > boxes[0][1]
    assert clear == (window == media.GIF_WINDOW), (
        f"in a {window[0]}x{window[1]} window the minimap ends at {boxes[0][1]} "
        f"and the zoom column starts at {boxes[1][0]}"
    )


def test_the_gif_crosses_a_bridge_and_claims_a_stop(
    chromium: Browser, server: str
) -> None:
    """The issue asks for the journey itself: deck underfoot, then a claim."""
    with game_context(
        chromium,
        viewport={"width": media.GIF_WINDOW[0], "height": media.GIF_WINDOW[1]},
        device_scale_factor=1,
    ) as page:
        media._load(
            page,
            server + GAME_PATH,
            {"name": "Lotte", "done": [1], "doneW": {"campus": [1]}},
        )
        media._start(page)
        media._settled(page, "campus")
        result = media._bridge_journey(page, lambda: None)

    assert result["from"] == "campus" and result["to"] == "winter"
    assert result["deck_frames"] > 0
    assert result["claimed"] == 1

    committed = Image.open(MEDIA / "gameplay.gif")
    assert committed.info.get("comment") == media.GAMEPLAY_MARKER
    assert committed.n_frames >= 20


def test_no_tap_lands_under_the_stage(chromium: Browser, server: str) -> None:
    """The window is taller than the stage, and what lies under the stage is
    the talk band: a point there walks nobody, however much of the picture it
    is. Aimed at one, the tool aims shorter until the point is the island."""
    wide, tall = media.GIF_WINDOW
    with game_context(
        chromium, viewport={"width": wide, "height": tall}, device_scale_factor=1
    ) as page:
        media._load(page, server + GAME_PATH, None)
        media._start(page)
        media._settled(page, "campus")
        stage = media._stage(page, wide)
        at = media._tap_towards(page, (wide / 2, tall - 20), share=1.0)
    # _tap_towards refuses every point that is not the canvas before clicking.
    # The click itself may open the artifact at that world position.
    assert at[1] < stage["height"], f"the tap at {at} is under the stage"
