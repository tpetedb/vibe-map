"""iOS Safari proxy: WebKit with iPhone metrics and touch events.

Playwright's WebKit is the same engine as Safari, so this is the closest a
headless test gets to the phone. HANDOVER asks for tap-to-move, the joystick,
sheet scrolling and WebGL with the shadow map; each has a test here.
"""

from __future__ import annotations

import math

import pytest

from tests.conftest import WAIT_MS, GamePage


def _pos(game: GamePage) -> list[float]:
    d = game.page.evaluate("window.__debug()")
    assert d["started"] and d["pos"] is not None, d
    return d["pos"]


def _dist(a: list[float], b: list[float]) -> float:
    return math.hypot(a[0] - b[0], a[2] - b[2])


def _wait_moved(game: GamePage, before: list[float]) -> None:
    """Input is consumed by the frame loop: wait for the walker, not a clock."""
    game.page.wait_for_function(
        "p => { const q = window.__debug().pos;"
        " return Math.hypot(q[0] - p[0], q[2] - p[2]) > 0.5; }",
        arg=before,
        timeout=WAIT_MS,
    )


@pytest.fixture
def phone(game_webkit_iphone: GamePage) -> GamePage:
    game_webkit_iphone.goto()
    game_webkit_iphone.start("Lotte")
    return game_webkit_iphone


def test_webgl_starts_on_iphone_webkit(phone: GamePage) -> None:
    assert phone.webgl_started()
    info = phone.page.evaluate("window.__debug()")
    assert info["draws"] > 0, "nothing was drawn"
    assert info["draws"] < 300, f"draw calls {info['draws']} over budget"
    phone.screenshot("webkit_iphone_island", clip_height=700)
    phone.assert_clean()


def test_tap_on_the_ground_moves_lotte(phone: GamePage) -> None:
    before = _pos(phone)
    box = phone.page.locator("#c").bounding_box()
    assert box
    phone.page.touchscreen.tap(
        box["x"] + box["width"] * 0.7, box["y"] + box["height"] * 0.55
    )
    _wait_moved(phone, before)
    after = _pos(phone)
    assert _dist(before, after) > 0.5, f"did not move: {before} -> {after}"
    phone.assert_clean()


def test_joystick_drag_moves_lotte(phone: GamePage) -> None:
    before = _pos(phone)
    joy = phone.page.locator("#joy").bounding_box()
    assert joy
    cx, cy = joy["x"] + joy["width"] / 2, joy["y"] + joy["height"] / 2
    phone.page.evaluate(
        """([x, y]) => {
          const el = document.getElementById('joy');
          const t = (type, px, py) => el.dispatchEvent(new PointerEvent(type, {
            pointerId: 1, pointerType: 'touch', clientX: px, clientY: py,
            bubbles: true, isPrimary: true }));
          t('pointerdown', x, y);
          t('pointermove', x + 40, y - 40);
        }""",
        [cx, cy],
    )
    _wait_moved(phone, before)
    phone.page.evaluate(
        "([x, y]) => document.getElementById('joy').dispatchEvent(new PointerEvent("
        "'pointerup', {pointerId: 1, pointerType: 'touch', clientX: x, clientY: y, "
        "bubbles: true}))",
        [cx + 40, cy - 40],
    )
    after = _pos(phone)
    assert _dist(before, after) > 0.5, f"joystick did not move: {before} -> {after}"
    phone.assert_clean()


def test_sheet_scrolls_in_normal_flow(phone: GamePage) -> None:
    phone.open_workstream(1)
    metrics = phone.page.evaluate(
        """() => ({
          scrollY: window.scrollY,
          docH: document.documentElement.scrollHeight,
          winH: window.innerHeight,
          sheetPos: getComputedStyle(document.getElementById('sheet')).position,
          fixed: [...document.querySelectorAll('body *')].filter(e =>
            getComputedStyle(e).position === 'fixed' && e.offsetParent !== null
          ).map(e => e.id || e.className).slice(0, 10),
        })"""
    )
    assert metrics["docH"] > metrics["winH"], metrics
    assert metrics["sheetPos"] != "fixed", metrics
    assert metrics["scrollY"] > 0, "openSheet should scroll the sheet into view"
    phone.screenshot("webkit_iphone_sheet")
    phone.assert_clean()


def test_hud_fits_the_phone_width(phone: GamePage) -> None:
    overflow = phone.page.evaluate(
        """() => {
          const w = window.innerWidth;
          return [...document.querySelectorAll('#hud .pill, #kpis .kpi')].map(e => {
            const r = e.getBoundingClientRect();
            return {id: e.id || e.textContent.trim().slice(0, 12), right: r.right,
                    clipped: e.scrollWidth > e.clientWidth + 1};
          }).filter(x => x.right > w + 1 || x.clipped);
        }"""
    )
    assert overflow == [], f"HUD overflows or clips at phone width: {overflow}"


def test_vault_opens_on_iphone(phone: GamePage) -> None:
    phone.open_vault()
    assert phone.page.locator("#vnote .wl").count() > 0
    phone.close_vault()
    phone.assert_clean()


def test_the_title_keeps_its_primary_button_in_view(
    game_webkit_iphone: GamePage,
) -> None:
    """On a phone the form is taller than the screen; Go must stay reachable."""
    game = game_webkit_iphone.goto()
    page = game.page
    box = page.locator("#title .row.go").bounding_box()
    assert box, "the go row has no box"
    assert box["y"] + box["height"] <= page.viewport_size["height"] + 1, box
    assert box["y"] >= 0, box
    # The box is opaque, so the HUD behind it does not read through the text.
    bg = page.evaluate(
        "getComputedStyle(document.querySelector('#title .box')).backgroundColor"
    )
    assert "rgba" not in bg or bg.endswith(", 1)"), bg
    game.screenshot("webkit_iphone_title")
    assert game.errors == []


def test_the_walker_label_carries_the_typed_name(phone: GamePage) -> None:
    """The label is built at boot; typing a name has to rebuild the walker."""
    assert (phone.page.evaluate("window.__debug().label") or {})["text"].startswith(
        "Lotte"
    )
    phone.page.evaluate("document.getElementById('title').classList.remove('off')")
    phone.page.fill("#name", "Bartholomew Featherstonehaugh-Smythe")
    phone.page.dispatch_event("#name", "input")
    phone.page.wait_for_function(
        "() => (window.__debug().label || {}).text?.startsWith('Bartholomew')",
        timeout=WAIT_MS,
    )
    plate = phone.page.evaluate("window.__debug().label")
    assert plate["text"].startswith("Bartholomew"), plate
    # A long name shrinks to fit the plate instead of running off it.
    assert plate["fs"] < 30, plate
    assert plate["fs"] >= 11, plate
    phone.assert_clean()


def test_the_title_form_and_the_go_row_fit_the_phone(
    game_webkit_iphone: GamePage,
) -> None:
    """At 393x852 the whole form fits the box and Go is reachable without scrolling."""
    page = game_webkit_iphone.goto().page
    box = page.locator("#title .box").bounding_box()
    assert box and box["width"] <= 393 and box["height"] <= 852, box
    assert page.evaluate("document.documentElement.scrollWidth") <= 393
    assert page.locator("#onboard .step").count() == 4
    assert page.locator("#name").is_visible()
    go = page.locator("#title .row.go").bounding_box()
    assert go and go["y"] >= 0 and go["y"] + go["height"] <= 852, go
    game_webkit_iphone.screenshot("webkit_iphone_title", clip_height=852)
    # The row is sticky, so it is still on screen with the setup guide open.
    page.click("#onboard button.choice:has-text('The full experience')")
    page.wait_for_timeout(400)
    page.locator("#title .box").evaluate("e => e.scrollTo(0, 0)")
    page.wait_for_timeout(200)
    go = page.locator("#title .row.go").bounding_box()
    assert go and go["y"] >= 0 and go["y"] + go["height"] <= 852, go
    page.fill("#name", "Lotte")
    page.click("#title .row.go button.primary")
    page.wait_for_selector("#title.off", state="attached")
    game_webkit_iphone.assert_clean()
