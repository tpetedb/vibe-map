"""Quality of life: continuity and photo mode (issue #127, proposals 24, 25, 27).

The save is one browser's localStorage, so the game says when it saved and
offers the export before anything could lose it. A long sitting earns one plain
word from Rolinda between stops. Photo mode hides the HUD and hands over the
frame as a PNG to save or share. Every test drives the real button, key or
clock and waits for something the page produced: a frame, a check, a state.
"""

from __future__ import annotations

from typing import Any

import pytest

from tests.conftest import STORAGE_KEY, GamePage

# A returning player with two stops on the campus and no export behind them.
RETURNING: dict[str, Any] = {"name": "Tom", "look": "own", "doneW": {"campus": [1, 2]}}

# A sitting is written into the record in the page's own clock, which the
# fixtures shift to noon: ticks a minute apart, the last one `ago` ms back,
# and an optional gap in the middle that ends a sitting.
SEED_SITTING = """([key, rec, n, ago, gapAt, gapMs]) => {
  const now = Date.now(), ev = [];
  let ts = now - ago;
  for (let i = 0; i < n; i++) {
    ev.unshift({ts: ts, kind: 'play', id: 'tick', world: 'campus', v: 60});
    ts -= 60000;
    if (i + 1 === gapAt) ts -= gapMs;
  }
  rec.events = ev;
  localStorage.setItem(key, JSON.stringify(rec));
}"""

# The captured picture, decoded and read back: a frame taken outside the
# frame it was drawn in is one flat colour, a real one is many.
COLOURS = """async () => {
  const img = document.querySelector('#photoview img');
  await img.decode();
  const c = document.createElement('canvas');
  c.width = 96; c.height = 96;
  const g = c.getContext('2d');
  g.drawImage(img, 0, 0, 96, 96);
  const d = g.getImageData(0, 0, 96, 96).data, seen = new Set();
  for (let i = 0; i < d.length; i += 4)
    seen.add((d[i] >> 3) << 10 | (d[i + 1] >> 3) << 5 | d[i + 2] >> 3);
  return {colours: seen.size, w: img.naturalWidth, h: img.naturalHeight};
}"""


def seed(
    game: GamePage,
    rec: dict[str, Any],
    n: int,
    *,
    ago: int = 30_000,
    gap_at: int = 0,
    gap_ms: int = 0,
) -> None:
    game.page.goto(game.url)
    game.page.wait_for_function("typeof window.__S === 'function'")
    game.page.evaluate(SEED_SITTING, [STORAGE_KEY, rec, n, ago, gap_at, gap_ms])
    game.page.reload()
    game.page.wait_for_function("typeof window.__S === 'function'")


def checks_pass(game: GamePage, n: int = 2) -> None:
    """Wait for the break check to run n more times, whatever it decided."""
    start = game.page.evaluate("window.__breaks().checks")
    game.until(f"window.__breaks().checks >= {start + n}", what=f"{n} break checks")


def settled(game: GamePage) -> None:
    """Wait until the panels have finished coming in and the flash is gone."""
    game.until(
        "!document.getElementById('photoflash') && [...document.querySelectorAll("
        "'#breakcard,#photobar,#photoview,#sheet')].every(e => !e.getAnimations"
        "({subtree: true}).some(a => a.playState === 'running'))",
        what="the panels to settle",
    )


def visible(game: GamePage, selector: str) -> bool:
    return bool(
        game.page.evaluate(
            "s => { const e = document.querySelector(s);"
            " return !!e && getComputedStyle(e).visibility !== 'hidden'"
            " && e.getClientRects().length > 0 }",
            selector,
        )
    )


# ---- 24: the saved mark and the export reminder ---------------------------


def test_a_save_lights_the_mark_once_and_never_moves_the_hud(game: GamePage) -> None:
    """24: nothing said the game had saved, so a player could not tell it had."""
    game.goto()
    game.start()
    bar = "document.getElementById('hud-bar').getBoundingClientRect().width"
    game.until("window.__saved && window.__saved().on", what="the saved mark")
    width = game.page.evaluate(bar)
    raised = game.page.evaluate("window.__saved().raised")
    # A burst of saves is one mark, not fifty: the mark is throttled.
    game.page.evaluate(
        "() => { for (let i = 0; i < 50; i++) window.track('chat', 'burst') }"
    )
    assert game.page.evaluate("window.__saved().raised") - raised <= 1
    assert game.page.evaluate(bar) == width
    game.until("!window.__saved().on", what="the saved mark to fade")
    assert game.page.evaluate(bar) == width
    # A mark that is only decoration is not read out every minute.
    assert game.page.get_attribute("#savedmark", "aria-hidden") == "true"
    game.assert_clean()


def test_the_roadmap_offers_an_export_until_one_is_made(game: GamePage) -> None:
    """24: two stops lived in one browser and nothing said so."""
    game.goto(state=RETURNING)
    game.resume()
    game.open_roadmap()
    assert visible(game, "#exportnudge")
    said = game.page.text_content("#exportnudge") or ""
    assert "2 stops" in said and "only in this browser" in said
    game.page.click("#s-map button:has-text('Export progress')")
    game.until("typeof window.__S().exportedAt === 'number'", what="the export")
    assert not visible(game, "#exportnudge")
    game.page.reload()
    game.page.wait_for_function("typeof window.__S === 'function'")
    game.resume()
    game.open_roadmap()
    assert not visible(game, "#exportnudge")
    game.assert_clean()


def test_a_stop_after_the_export_brings_the_line_back(game: GamePage) -> None:
    """24: a code exported yesterday does not carry tonight's stop."""
    game.goto(state={**RETURNING, "exportedAt": 1})
    game.resume()
    game.open_roadmap()
    assert not visible(game, "#exportnudge")
    game.page.keyboard.press("Escape")
    game.claim(3)
    game.open_roadmap()
    said = game.page.text_content("#exportnudge") or ""
    assert "1 stop since your last export" in said
    game.assert_clean()


def test_reset_to_greenfield_warns_about_an_unexported_evening(
    game: GamePage,
) -> None:
    """24: the reset confirm never mentioned that nothing had been exported."""
    game.goto(state=RETURNING)
    game.resume()
    said: list[str] = []
    game.page.once("dialog", lambda d: (said.append(d.message), d.dismiss()))
    game.page.evaluate("reset()")
    assert said and "never been exported" in said[0]
    assert game.page.evaluate("window.__S().doneW.campus") == [1, 2]
    game.assert_clean()


# ---- 25: the break card ------------------------------------------------------


def test_the_break_card_waits_between_stops_and_says_where_you_are(
    game: GamePage,
) -> None:
    """25: fifty minutes in one sitting went by without a word."""
    # Off until the Roadmap is open: the Resume click is itself a player being
    # there, and a check between it and the Roadmap would be a race.
    seed(game, {**RETURNING, "settings": {"breaks": "off"}}, 51)
    game.resume()
    game.open_roadmap()
    game.page.evaluate("setSetting('breaks', 'on')")
    game.page.keyboard.press("Shift")
    checks_pass(game)
    assert game.page.evaluate("window.__breaks().due")
    assert not visible(game, "#breakcard"), "the card came up during a stop"
    game.page.keyboard.press("Escape")
    game.until("!!document.querySelector('#breakcard')", what="the break card")
    said = game.page.text_content("#breakcard") or ""
    assert "2 of 8" in said and "Rolinda" in said
    assert "\u2014" not in said
    game.page.click("#breakcard button:has-text('Keep going')")
    assert not visible(game, "#breakcard")
    assert isinstance(game.page.evaluate("window.__S().breakAt"), int | float)
    # Once a sitting: a reload in the same sitting does not ask again.
    game.page.reload()
    game.page.wait_for_function("typeof window.__S === 'function'")
    game.resume()
    game.page.keyboard.press("Shift")
    checks_pass(game)
    assert not visible(game, "#breakcard")
    game.assert_clean()


def test_the_break_card_can_be_switched_off_and_closed_by_key(
    game: GamePage,
) -> None:
    """25: an interruption the player cannot suppress is a nag."""
    seed(game, RETURNING, 55)
    game.resume()
    game.page.keyboard.press("Shift")
    game.until("!!document.querySelector('#breakcard')", what="the break card")
    buttons = game.page.locator("#breakcard button")
    for i in range(buttons.count()):
        assert buttons.nth(i).bounding_box()["height"] >= 44
    game.page.click("#breakcard button:has-text('Stop reminding me')")
    assert game.page.evaluate("window.__S().settings.breaks") == "off"
    assert not visible(game, "#breakcard")
    game.page.evaluate("window.__S().breakAt = 0")
    checks_pass(game)
    assert not game.page.evaluate("window.__breaks().due")
    game.assert_clean()


def test_escape_closes_the_break_card(game: GamePage) -> None:
    seed(game, RETURNING, 51)
    game.resume()
    game.page.keyboard.press("Shift")
    game.until("!!document.querySelector('#breakcard')", what="the break card")
    game.page.keyboard.press("Escape")
    assert not visible(game, "#breakcard")
    game.assert_clean()


@pytest.mark.parametrize(
    ("n", "gap_at", "gap_ms", "ago"),
    [
        (49, 0, 0, 30_000),  # a short sitting
        (60, 20, 20 * 60_000, 30_000),  # two sittings with a long gap between
        (60, 0, 0, 30 * 60_000),  # a sitting that ended half an hour ago
    ],
)
def test_a_short_or_broken_sitting_earns_no_break(
    game: GamePage, n: int, gap_at: int, gap_ms: int, ago: int
) -> None:
    """25: only minutes on screen in one sitting count, not a day's total."""
    seed(game, RETURNING, n, ago=ago, gap_at=gap_at, gap_ms=gap_ms)
    game.resume()
    game.page.keyboard.press("Shift")
    checks_pass(game)
    assert not game.page.evaluate("window.__breaks().due")
    assert not visible(game, "#breakcard")
    game.assert_clean()


def test_a_sitting_nobody_is_at_earns_no_card(game: GamePage) -> None:
    """25: a laptop left open with the game on is not a player who needs a break."""
    seed(game, RETURNING, 51)
    game.resume()
    game.page.evaluate("window.__breakAway()")
    checks_pass(game)
    assert game.page.evaluate("window.__breaks().due")
    assert not visible(game, "#breakcard")
    game.assert_clean()


# ---- 27: photo mode and share ------------------------------------------------


def take_photo(game: GamePage) -> dict[str, Any]:
    game.frames(3)
    game.page.click("#photobar button:has-text('Take photo')")
    game.until("!!document.querySelector('#photoview img')", what="the photo")
    return game.page.evaluate(COLOURS)


def test_photo_mode_hides_the_hud_and_takes_the_drawn_frame(game: GamePage) -> None:
    """27: there was no clean picture of the island to keep."""
    game.goto(state=RETURNING)
    game.resume()
    game.hud_action("#hud-photo")
    game.until("window.__photo().on", what="photo mode")
    assert not visible(game, "#hud")
    assert visible(game, "#photobar")
    assert game.page.evaluate(
        "document.activeElement === document.querySelector('#photobar button')"
    )
    # The frame comes from the canvas as drawn: no preserved buffer to pay
    # for on every frame, so the capture has to sit in the frame it renders.
    assert game.page.evaluate("window.__photo().preserve") is False
    shot = take_photo(game)
    assert shot["colours"] > 24, shot
    assert shot["w"] > 200 and shot["h"] > 200
    link = game.page.locator("#photoview a[download]")
    assert (link.get_attribute("download") or "").endswith(".png")
    assert (link.get_attribute("href") or "").startswith("blob:")
    game.page.keyboard.press("Escape")
    game.until("!window.__photo().on", what="photo mode to close")
    assert visible(game, "#hud")
    assert game.page.evaluate("document.querySelector('#photoview')") is None
    game.assert_clean()


SHARE_STUB = """(() => {
  navigator.canShare = d => !!(d && d.files && d.files.length);
  navigator.share = async d => {
    const f = d.files[0];
    window.__shared = f.type + ' ' + f.name + ' ' + f.size;
  };
})()"""


def test_p_opens_photo_mode_and_a_phone_can_share_the_file(game: GamePage) -> None:
    """27: the share sheet takes a file, and needs a click of its own."""
    game.page.context.add_init_script(SHARE_STUB)
    game.goto(state=RETURNING)
    game.resume()
    game.page.keyboard.press("p")
    game.until("window.__photo().on", what="photo mode")
    take_photo(game)
    game.page.click("#photoview button:has-text('Share')")
    game.until("!!window.__shared", what="the share")
    shared = game.page.evaluate("window.__shared")
    assert shared.startswith("image/png ") and ".png" in shared
    game.page.keyboard.press("p")
    game.until("!window.__photo().on", what="photo mode to close")
    game.assert_clean()


def test_photo_mode_waits_while_a_panel_is_open(game: GamePage) -> None:
    game.goto(state=RETURNING)
    game.resume()
    game.open_roadmap()
    game.page.keyboard.press("p")
    game.frames(2)
    assert not game.page.evaluate("window.__photo().on")
    game.assert_clean()


# ---- the surfaces, on the laptop and both phones ---------------------------


@pytest.mark.parametrize(
    "profile", ["game_desktop", "game_android", "game_webkit_iphone"]
)
def test_the_new_surfaces_on_every_screen(
    request: pytest.FixtureRequest, profile: str
) -> None:
    game: GamePage = request.getfixturevalue(profile)
    seed(game, RETURNING, 51)
    game.resume()
    game.page.keyboard.press("Shift")
    game.until("!!document.querySelector('#breakcard')", what="the break card")
    game.frames(3)
    settled(game)
    game.screenshot(f"qol5-break-{profile}")
    box = game.page.locator("#breakcard").bounding_box()
    width = game.page.viewport_size["width"] if game.page.viewport_size else 0
    assert box and box["x"] >= 0 and box["x"] + box["width"] <= width
    game.page.click("#breakcard button:has-text('Keep going')")
    game.open_roadmap()
    game.page.locator("#exportnudge").scroll_into_view_if_needed()
    settled(game)
    game.screenshot(f"qol5-nudge-{profile}")
    game.page.keyboard.press("Escape")
    game.hud_action("#hud-photo")
    game.until("window.__photo().on", what="photo mode")
    game.frames(3)
    settled(game)
    game.screenshot(f"qol5-photo-{profile}")
    take_photo(game)
    settled(game)
    game.screenshot(f"qol5-preview-{profile}")
    for b in game.page.locator("#photoview button, #photoview a").all():
        bb = b.bounding_box()
        assert bb and bb["height"] >= 44, b.text_content()
    game.assert_clean()
