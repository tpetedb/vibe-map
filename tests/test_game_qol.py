"""Quality of life: copy on every command, the Continue card, the wake lock.

Every test drives the real controls: it clicks the Copy button a player would
click and reads the clipboard back where the browser lets it. Chromium gets
the clipboard permissions and the real API; WebKit has no permission for it,
so there the call itself is the assertion.
"""

from __future__ import annotations

from typing import Any

from tests.conftest import GamePage

# A returning player two stops in: 20:00, Data Warehouse is what comes next.
RETURNING: dict[str, Any] = {
    "name": "Tom",
    "look": "own",
    "doneW": {"campus": [1, 2]},
}
NEXT_STOP = "20:00, Data Warehouse"
NEXT_CMD = "uv run vibe check 3"

# A camp adds its own stop to an island, and its lesson carries a command with
# the placeholder the camp template uses for the player's name.
CAMP_STOP = (
    "() => window.__data().campaign.prod.ws.push({h: 'Stop 9',"
    " n: 'My own stop', d: 'The one I added',"
    ' html: \'<div class="lesson"><pre><code>vibe name'
    " &lt;your_name&gt;</code></pre></div>'})"
)


def _prod_camp(name: str) -> dict[str, Any]:
    return {
        "name": name,
        "look": "own",
        "world": "prod",
        "doneW": {"prod": [1, 2, 3, 4, 5, 6, 7, 8]},
    }


# A wake lock this test can count. The real API is secure context only and
# absent in WebKit, so the stub is installed before the page boots.
WAKE_STUB = """
window.__wake = {req: 0, rel: 0};
Object.defineProperty(navigator, 'wakeLock', {configurable: true, value: {
  request: () => {
    window.__wake.req++;
    return Promise.resolve({
      release() { window.__wake.rel++; return Promise.resolve(); },
      addEventListener() {},
    });
  }}});
"""
# The page cannot be hidden from a test, so visibilityState is answered for it
# and the event the platform would fire is fired by hand.
VISIBILITY = """state => {
  Object.defineProperty(document, 'visibilityState',
    {configurable: true, get: () => state});
  document.dispatchEvent(new Event('visibilitychange', {bubbles: true}));
}"""
# WebKit has no clipboard permission to grant, so the call is recorded instead.
CLIPBOARD_STUB = """
window.__copied = [];
Object.defineProperty(navigator, 'clipboard', {configurable: true, value: {
  writeText: t => { window.__copied.push(t); return Promise.resolve(); }}});
"""


def _allow_clipboard(game: GamePage) -> None:
    game.page.context.grant_permissions(["clipboard-read", "clipboard-write"])


def _clipboard(game: GamePage) -> str:
    return str(game.page.evaluate("() => navigator.clipboard.readText()"))


def _copy(game: GamePage, selector: str) -> str:
    """Click a Copy button and wait for the confirmation it prints."""
    game.page.click(selector)
    game.until(
        f"(document.querySelector({selector!r}).textContent || '')"
        ".indexOf('Copied') === 0"
    )
    return game.page.text_content(selector) or ""


def _open_lesson(game: GamePage, name: str = "Tom") -> None:
    game.goto()
    game.start(name)
    game.open_workstream(1)


# ---- copy on every command block ---------------------------------------------


def test_every_command_block_of_a_lesson_carries_one_copy_button(
    game_desktop: GamePage,
) -> None:
    _open_lesson(game_desktop)
    screen = "#sheet .screen.on"
    blocks = game_desktop.page.locator(f"{screen} details.cmds").count()
    assert blocks >= 3
    bars = game_desktop.page.locator(f"{screen} details.cmds .cmdbar button.copy")
    assert bars.count() == blocks
    # The button is under the command, never over it.
    pre = game_desktop.page.locator(f"{screen} details.cmds pre").first
    bars.first.scroll_into_view_if_needed()
    game_desktop.still("document.querySelector('#sheet .inner').scrollTop")
    box, bar = pre.bounding_box(), bars.first.bounding_box()
    assert box and bar
    assert bar["y"] >= box["y"] + box["height"] - 1, (box, bar)
    game_desktop.screenshot("qol-desktop-lesson")
    game_desktop.assert_clean()


def test_copying_a_command_puts_exactly_that_command_on_the_clipboard(
    game_desktop: GamePage,
) -> None:
    _allow_clipboard(game_desktop)
    _open_lesson(game_desktop)
    screen = "#sheet .screen.on"
    wanted = game_desktop.page.locator(
        f"{screen} details.cmds pre"
    ).first.text_content()
    said = _copy(game_desktop, f"{screen} details.cmds .cmdbar button.copy")
    assert said == "Copied"
    assert _clipboard(game_desktop) == wanted
    # The same words a screen reader hears.
    assert (game_desktop.page.text_content("#copysay") or "") == "Copied"
    game_desktop.assert_clean()


def test_the_setup_guide_and_an_artifact_carry_copy_buttons_too(
    game_desktop: GamePage,
) -> None:
    """Every screen the sheet opens is wrapped, not only the campus lessons."""
    page = game_desktop.goto().page
    game_desktop.start("Tom")
    game_desktop.open_roadmap()
    page.click("#s-map button:has-text('Setup guide')")
    page.wait_for_selector("#s-setup.on", state="attached")
    guides = page.locator("#s-setup pre").count()
    assert guides >= 5
    assert page.locator("#s-setup .cmdbar button.copy").count() == guides
    game_desktop.open_roadmap()
    card = page.locator("#plotlist .card", has_text="Artifacts on the islands")
    card.locator("button").first.click()
    page.wait_for_selector("#s-artifact.on", state="attached")
    assert page.locator("#s-artifact .cmdbar button.copy").count() == 1
    game_desktop.assert_clean()


def test_a_refused_clipboard_selects_the_text_and_names_the_key(
    game_desktop: GamePage,
) -> None:
    _open_lesson(game_desktop)
    game_desktop.page.evaluate(
        """() => { Object.defineProperty(navigator, 'clipboard', {
             value: {writeText: () => Promise.reject(new Error('no'))},
             configurable: true}); }"""
    )
    button = "#sheet .screen.on details.cmds .cmdbar button.copy"
    game_desktop.page.click(button)
    game_desktop.until(
        f"(document.querySelector({button!r}).textContent || '')"
        ".indexOf('Selected') === 0"
    )
    said = game_desktop.page.text_content(button) or ""
    assert said.endswith(" C"), said
    assert (game_desktop.page.evaluate("() => String(getSelection())") or "").strip()
    assert "Selected" in (game_desktop.page.text_content("#copysay") or "")
    game_desktop.assert_clean()


def test_a_command_that_names_the_player_copies_with_the_name_filled_in(
    game_desktop: GamePage,
) -> None:
    _allow_clipboard(game_desktop)
    game_desktop.goto(state=_prod_camp("Tom"))
    game_desktop.resume()
    game_desktop.page.evaluate(CAMP_STOP)
    game_desktop.open_roadmap()
    game_desktop.page.click("#plotlist button:has-text('My own stop')")
    game_desktop.page.wait_for_selector("#s-gen.on", state="attached")
    game_desktop.sheet_in_place()
    said = _copy(game_desktop, "#s-gen .cmdbar button.copy")
    assert said == "Copied, with your name"
    assert _clipboard(game_desktop) == "vibe name Tom"
    game_desktop.assert_clean()


def test_a_name_that_is_not_one_plain_word_is_copied_shell_safe(
    game_desktop: GamePage,
) -> None:
    """shq() is the project's spelling of a name a shell cannot misread."""
    _allow_clipboard(game_desktop)
    game_desktop.goto(state=_prod_camp("Tom O'Hara"))
    game_desktop.resume()
    game_desktop.page.evaluate(CAMP_STOP)
    game_desktop.open_roadmap()
    game_desktop.page.click("#plotlist button:has-text('My own stop')")
    game_desktop.page.wait_for_selector("#s-gen.on", state="attached")
    game_desktop.sheet_in_place()
    _copy(game_desktop, "#s-gen .cmdbar button.copy")
    assert _clipboard(game_desktop) == "vibe name 'Tom O'\\''Hara'"
    game_desktop.assert_clean()


def test_an_unknown_name_copies_the_command_as_it_is_and_says_so(
    game_desktop: GamePage,
) -> None:
    _allow_clipboard(game_desktop)
    page = game_desktop.goto().page
    page.click("#onboard button.choice:has-text('The full experience')")
    page.wait_for_selector("#ob-setup", state="visible")
    pre = page.locator("#ob-setup pre").filter(has_text="vibe name")
    button = pre.locator(
        "xpath=following-sibling::div[contains(@class,'cmdbar')][1]//button"
    )
    button.click()
    game_desktop.until(
        "(document.querySelector('#copysay').textContent || '').indexOf('Copied') === 0"
    )
    assert "fill in your name" in (page.text_content("#copysay") or "")
    assert "vibe name <your_name>" in _clipboard(game_desktop)
    game_desktop.assert_clean()


# ---- the Continue card --------------------------------------------------------


def test_a_returning_player_is_told_where_to_carry_on(game_desktop: GamePage) -> None:
    page = game_desktop.goto(state=RETURNING).page
    card = page.locator("#cont .cont")
    assert card.is_visible()
    text = page.text_content("#cont") or ""
    assert "Innovation Campus" in text and NEXT_STOP in text
    assert "Persisted scores and a dashboard" in text, text
    assert NEXT_CMD in text
    assert page.locator("#cont .cmdbar button.copy").count() == 1
    game_desktop.screenshot("qol-desktop-title-returning")
    page.click("#cont button:has-text('Open it')")
    page.wait_for_selector("#title.off", state="attached")
    page.wait_for_selector("#s-3.on", state="attached")
    game_desktop.assert_clean()


def test_a_first_visit_has_nothing_to_continue(game_desktop: GamePage) -> None:
    page = game_desktop.goto().page
    assert not page.is_visible("#cont")
    assert (page.text_content("#cont") or "").strip() == ""
    game_desktop.assert_clean()


def test_the_roadmap_leads_with_the_next_stop_and_says_where_you_are(
    game_desktop: GamePage,
) -> None:
    _allow_clipboard(game_desktop)
    game_desktop.goto(state=RETURNING)
    game_desktop.resume()
    game_desktop.open_roadmap()
    page = game_desktop.page
    assert NEXT_STOP in (page.text_content("#mapcont") or "")
    here = page.text_content("#plotlist .here") or ""
    assert "Innovation Campus" in here and "2 of 8 delivered" in here, here
    rows = page.locator("#plotlist button.date.next")
    assert rows.count() == 1
    assert "(next)" in (rows.first.text_content() or "")
    assert NEXT_STOP in (rows.first.text_content() or "")
    said = _copy(game_desktop, "#mapcont .cmdbar button.copy")
    assert said == "Copied"
    assert _clipboard(game_desktop) == NEXT_CMD
    game_desktop.screenshot("qol-desktop-roadmap")
    page.click("#mapcont button:has-text('Open it')")
    page.wait_for_selector("#s-3.on", state="attached")
    game_desktop.assert_clean()


def test_a_finished_island_offers_no_next_stop(game_desktop: GamePage) -> None:
    game_desktop.goto(state=_prod_camp("Tom"))
    game_desktop.resume()
    game_desktop.open_roadmap()
    assert (game_desktop.page.text_content("#mapcont") or "").strip() == ""
    here = game_desktop.page.text_content("#plotlist .here") or ""
    assert "8 of 8 delivered" in here, here
    assert game_desktop.page.locator("#plotlist button.date.next").count() == 0
    game_desktop.assert_clean()


# ---- the screen stays awake ---------------------------------------------------


def test_the_screen_is_kept_awake_while_a_sheet_is_open(
    game_desktop: GamePage,
) -> None:
    page = game_desktop.page
    page.add_init_script(WAKE_STUB)
    game_desktop.goto()
    game_desktop.start("Tom")
    game_desktop.open_roadmap()
    game_desktop.until("window.__wake.req === 1")
    # Hidden: the platform drops the lock, and so does the game.
    page.evaluate(VISIBILITY, "hidden")
    game_desktop.until("window.__wake.rel === 1")
    # Back: the sheet is still open, so the lock is taken again.
    page.evaluate(VISIBILITY, "visible")
    game_desktop.until("window.__wake.req === 2")
    page.click("#sheet button.x")
    game_desktop.until("window.__wake.rel === 2")
    game_desktop.assert_clean()


def test_a_browser_without_a_wake_lock_opens_a_lesson_anyway(
    game_desktop: GamePage,
) -> None:
    """Feature detection, not assumption: no API means no lock and no error."""
    game_desktop.page.add_init_script(
        "Object.defineProperty(navigator, 'wakeLock',"
        " {configurable: true, value: undefined});"
    )
    _open_lesson(game_desktop)
    assert game_desktop.page.locator("#sheet .screen.on .cmdbar button.copy").count()
    game_desktop.assert_clean()


# ---- both phones --------------------------------------------------------------


def _phone_copy_button(game: GamePage, shot: str) -> None:
    """The copy button on a phone: past 44 px, and never over the command."""
    _open_lesson(game)
    screen = "#sheet .screen.on"
    button = game.page.locator(f"{screen} details.cmds .cmdbar button.copy").first
    pre = game.page.locator(f"{screen} details.cmds pre").first
    button.scroll_into_view_if_needed()
    game.still("document.querySelector('#sheet .inner').scrollTop")
    box, bar = pre.bounding_box(), button.bounding_box()
    assert box and bar
    assert bar["height"] >= 44, bar
    assert bar["y"] >= box["y"] + box["height"] - 1, (box, bar)
    game.screenshot(shot, clip_height=760)
    game.assert_clean()


def test_the_copy_button_is_a_finger_target_on_android(
    game_android: GamePage,
) -> None:
    _phone_copy_button(game_android, "qol-android-lesson")


def test_the_copy_button_is_a_finger_target_on_iphone(
    game_webkit_iphone: GamePage,
) -> None:
    _phone_copy_button(game_webkit_iphone, "qol-iphone-lesson")


def test_copying_works_on_android(game_android: GamePage) -> None:
    _allow_clipboard(game_android)
    game_android.goto(state=RETURNING)
    game_android.resume()
    game_android.open_roadmap()
    said = _copy(game_android, "#mapcont .cmdbar button.copy")
    assert said == "Copied"
    assert _clipboard(game_android) == NEXT_CMD
    game_android.screenshot("qol-android-roadmap", clip_height=900)
    game_android.assert_clean()


def test_copying_calls_the_clipboard_on_iphone(
    game_webkit_iphone: GamePage,
) -> None:
    """WebKit grants no clipboard permission, so the call is the assertion."""
    game = game_webkit_iphone
    game.page.add_init_script(CLIPBOARD_STUB)
    game.goto(state=RETURNING)
    game.resume()
    game.open_roadmap()
    said = _copy(game, "#mapcont .cmdbar button.copy")
    assert said == "Copied"
    assert game.page.evaluate("() => window.__copied") == [NEXT_CMD]
    game.screenshot("qol-iphone-roadmap", clip_height=840)
    game.assert_clean()


def test_the_title_card_fits_both_phones(
    game_android: GamePage, game_webkit_iphone: GamePage
) -> None:
    """The Continue card is above the fold on the phone the owner plays on."""
    for game, shot in ((game_android, "android"), (game_webkit_iphone, "iphone")):
        page = game.goto(state=RETURNING).page
        assert page.is_visible("#cont .cont")
        box = page.locator("#cont .cont").bounding_box()
        assert box and box["width"] > 0
        assert NEXT_STOP in (page.text_content("#cont") or "")
        game.screenshot(f"qol-{shot}-title-returning", clip_height=820)
        game.assert_clean()
