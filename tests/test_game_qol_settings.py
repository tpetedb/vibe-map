"""Quality of life: reading comfort, contrast and the hand that holds the phone.

Every test drives the real dropdown in the real Settings panel and then reads
the page back: the computed size of the text a player reads, the measured gap
between a chevron and its word, the box the stick actually occupies. Nothing
calls applySettings() directly, because a setting that never reaches the panel
is not a setting.
"""

from __future__ import annotations

from typing import Any

from tests.conftest import GamePage, encode_progress

# A returning player, so the Roadmap and the lessons are there to measure.
RETURNING: dict[str, Any] = {"name": "Tom", "look": "own", "doneW": {"campus": [1, 2]}}

# The gap between the disclosure chevron and the word after it, measured where
# it is drawn. The chevron is generated content, so its own box cannot be read
# back; a probe span in the summary's own font gives the width of the same
# glyph, and what is left over is the spacing under test.
GAP = """() => {
  const s = document.querySelector('#sheet .screen.on details.cmds summary');
  const cs = getComputedStyle(s);
  const marker = getComputedStyle(s, '::before').content;
  const node = [...s.childNodes].find(n => n.nodeType === 3 && n.textContent.trim());
  const range = document.createRange();
  range.selectNodeContents(node);
  const probe = document.createElement('span');
  probe.textContent = marker.replace(/^["']|["']$/g, '');
  probe.style.cssText = 'position:absolute;visibility:hidden;white-space:pre';
  probe.style.fontFamily = cs.fontFamily;
  probe.style.fontSize = cs.fontSize;
  probe.style.fontWeight = cs.fontWeight;
  probe.style.letterSpacing = cs.letterSpacing;
  document.body.appendChild(probe);
  const glyph = probe.getBoundingClientRect().width;
  probe.remove();
  const box = s.getBoundingClientRect();
  const left = box.left + parseFloat(cs.borderLeftWidth) + parseFloat(cs.paddingLeft);
  return {
    gap: range.getBoundingClientRect().left - left - glyph,
    display: cs.display,
    marker: marker,
    word: s.textContent,
  };
}"""

# The contrast ratio of an element's own colour against the page behind it,
# the WCAG formula, so the assertion is a number and not an opinion.
RATIO = """sel => {
  const lin = c => {
    const v = c / 255;
    return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
  };
  const lum = s => {
    const [r, g, b] = s.match(/[\\d.]+/g).map(Number);
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
  };
  const a = lum(getComputedStyle(document.querySelector(sel)).color);
  const b = lum(getComputedStyle(document.body).backgroundColor);
  return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
}"""

# The two boxes the thumbs land on, and the zoom column above one of them.
CONTROLS = """() => {
  const box = id => {
    const r = document.getElementById(id).getBoundingClientRect();
    return {left: r.left, right: r.right, top: r.top, bottom: r.bottom};
  };
  return {joy: box('joy'), jump: box('jump'), zoom: box('zoom'),
          width: document.documentElement.clientWidth};
}"""

# A select too narrow for the longest option it can show, which is the one
# that decides whether the control holds its value: the selected one only says
# what this player happens to have picked. A select hides the overflow rather
# than scrolling it, so scrollWidth says nothing; the text is measured in the
# select's own font and compared with the room it has, less its padding and
# the drop-down arrow.
NARROW = """() => {
  const probe = document.createElement('span');
  probe.style.cssText = 'position:absolute;visibility:hidden;white-space:pre';
  document.body.appendChild(probe);
  const tight = [];
  for (const s of document.querySelectorAll('#s-settings select')) {
    const cs = getComputedStyle(s);
    probe.style.font = cs.font;
    probe.style.letterSpacing = cs.letterSpacing;
    let widest = 0, text = '';
    for (const option of s.options) {
      probe.textContent = option.text;
      const w = probe.getBoundingClientRect().width;
      if (w > widest) { widest = w; text = option.text; }
    }
    const need = widest +
      parseFloat(cs.paddingLeft) + parseFloat(cs.paddingRight) + 24;
    if (need > s.getBoundingClientRect().width + 1) tight.push(s.id + ': ' + text);
  }
  probe.remove();
  return tight;
}"""

NO_VIBRATE = (
    "Object.defineProperty(navigator, 'vibrate', "
    "{configurable: true, value: undefined});"
)


def _open_settings(game: GamePage) -> None:
    game.hud_action("#hud button:has-text('Settings')")
    game.page.wait_for_selector("#s-settings.on", state="attached")
    game.sheet_in_place()


def _set(game: GamePage, key: str, value: str) -> None:
    """Change one setting through its dropdown, as a player does."""
    _open_settings(game)
    game.page.select_option(f"#set-{key}", value)
    game.until(
        f"(window.__S().settings || {{}})[{key!r}] === {value!r}",
    )


def _font(game: GamePage, selector: str) -> float:
    return float(
        game.page.evaluate(
            "sel => parseFloat(getComputedStyle(document.querySelector(sel)).fontSize)",
            selector,
        )
    )


def _started(game: GamePage) -> GamePage:
    game.goto(state=RETURNING)
    game.resume()
    return game


# ---- the chevron and its word -------------------------------------------------


def _chevron_gap(game: GamePage, shot: str) -> None:
    """A coarse pointer lays the summary out as a flex row; the gap survives it."""
    _started(game)
    game.open_workstream(1)
    summary = game.page.locator("#sheet .screen.on details.cmds summary").first
    summary.scroll_into_view_if_needed()
    game.still("document.querySelector('#sheet .inner').scrollTop")
    info = game.page.evaluate(GAP)
    assert info["display"] == "flex", info
    assert info["word"] == "Commands", info
    assert info["marker"] in ('"v"', "'v'", '">"', "'>'"), info
    assert info["gap"] >= 3, info
    game.screenshot(shot, clip_height=760)
    game.assert_clean()


def test_the_command_chevron_keeps_its_gap_on_android(game_android: GamePage) -> None:
    _chevron_gap(game_android, "qol1-android-cmds")


def test_the_command_chevron_keeps_its_gap_on_iphone(
    game_webkit_iphone: GamePage,
) -> None:
    _chevron_gap(game_webkit_iphone, "qol1-iphone-cmds")


# ---- text size ----------------------------------------------------------------


def test_larger_text_grows_the_lesson_and_survives_a_reload(
    game_desktop: GamePage,
) -> None:
    game = _started(game_desktop)
    game.open_workstream(1)
    before = _font(game, "#sheet .screen.on .lesson pre")
    _set(game, "text", "larger")
    game.open_workstream(1)
    after = _font(game, "#sheet .screen.on .lesson pre")
    assert after > before * 1.3, (before, after)
    game.screenshot("qol1-desktop-lesson-larger")
    # The setting is this browser's, so it is there again after a reload.
    game.goto()
    game.resume()
    assert game.page.evaluate("() => document.body.dataset.text") == "larger"
    game.open_workstream(1)
    assert _font(game, "#sheet .screen.on .lesson pre") == after
    game.assert_clean()


def test_the_text_size_leaves_the_hud_and_the_stick_where_they_were(
    game_android: GamePage,
) -> None:
    """The multiplier is for reading surfaces: a thumb control must not move."""
    game = _started(game_android)
    before = game.page.evaluate(CONTROLS)
    pill = _font(game, "#hud-bar button")
    _set(game, "text", "larger")
    game.page.click("#sheet button.x")
    assert game.page.evaluate(CONTROLS) == before
    assert _font(game, "#hud-bar button") == pill
    game.assert_clean()


def _fits_at_larger(game: GamePage, shot: str) -> None:
    """Bigger type must not clip an option or push the page sideways.

    Whether a value fits beside its label is a question about font metrics,
    which differ between one device and the next, so the answer must not come
    from this machine's fonts: the row gives the select the whole width above
    Normal, and the check measures the option's own text in the select's own
    font against the room the select has.
    """
    _started(game)
    _set(game, "text", "larger")
    assert game.page.evaluate(NARROW) == [], game.page.evaluate(NARROW)
    wide = game.page.evaluate(
        """() => {
             const i = document.querySelector('#sheet .inner');
             return [i.scrollWidth - i.clientWidth,
                     document.documentElement.scrollWidth -
                     document.documentElement.clientWidth];
           }"""
    )
    assert wide[0] <= 1 and wide[1] <= 1, wide
    game.screenshot(shot, clip_height=900)
    game.assert_clean()


def test_larger_text_still_fits_the_panel_on_android(game_android: GamePage) -> None:
    _fits_at_larger(game_android, "qol1-android-settings-larger")


def test_larger_text_still_fits_the_panel_on_iphone(
    game_webkit_iphone: GamePage,
) -> None:
    _fits_at_larger(game_webkit_iphone, "qol1-iphone-settings-larger")


# ---- line spacing -------------------------------------------------------------


def test_comfortable_spacing_reaches_the_numbers_the_guideline_names(
    game_desktop: GamePage,
) -> None:
    """XAG 101: line 1.5, letter 0.12 times the size, word 0.16 times the size."""
    game = _started(game_desktop)
    _set(game, "spacing", "comfortable")
    game.open_workstream(1)
    got = game.page.evaluate(
        """() => {
             const p = document.querySelector('#sheet .screen.on .lesson li');
             const c = getComputedStyle(p);
             const pre = getComputedStyle(
               document.querySelector('#sheet .screen.on .lesson pre'));
             return {size: parseFloat(c.fontSize),
                     line: parseFloat(c.lineHeight),
                     letter: parseFloat(c.letterSpacing),
                     word: parseFloat(c.wordSpacing),
                     preLetter: pre.letterSpacing};
           }"""
    )
    assert got["line"] >= got["size"] * 1.5, got
    assert got["letter"] >= got["size"] * 0.12 - 0.01, got
    assert got["word"] >= got["size"] * 0.16 - 0.01, got
    # A command block keeps monospace alignment: it is read, not scanned.
    assert got["preLetter"] in ("normal", "0px"), got
    game.screenshot("qol1-desktop-lesson-comfortable")
    game.assert_clean()


# ---- contrast -----------------------------------------------------------------


def test_more_contrast_lifts_the_dim_text_past_seven_to_one(
    game_desktop: GamePage,
) -> None:
    """XAG 102 asks for 7:1 when a high contrast mode is on."""
    game = _started(game_desktop)
    _open_settings(game)
    plain = float(game.page.evaluate(RATIO, "#s-settings p.muted"))
    _set(game, "contrast", "more")
    raised = float(game.page.evaluate(RATIO, "#s-settings p.muted"))
    assert raised > plain, (plain, raised)
    assert raised >= 7, raised
    game.screenshot("qol1-desktop-settings-contrast")
    game.assert_clean()


def test_the_platform_asking_for_more_contrast_is_followed_and_overruled(
    game_desktop: GamePage,
) -> None:
    game_desktop.page.emulate_media(contrast="more")
    game = _started(game_desktop)
    game.until("document.body.classList.contains('contrast-more')")
    # A player whose eyes disagree with the platform has the last word.
    _set(game, "contrast", "off")
    game.until("!document.body.classList.contains('contrast-more')")
    _set(game, "contrast", "auto")
    game.until("document.body.classList.contains('contrast-more')")
    game.assert_clean()


def test_forced_colours_leave_the_controls_an_edge(game_desktop: GamePage) -> None:
    """The system repaints text and fills, so a control keeps a drawn border."""
    game_desktop.page.emulate_media(forced_colors="active")
    game = _started(game_desktop)
    _open_settings(game)
    width = game.page.evaluate(
        "() => parseFloat(getComputedStyle("
        "document.querySelector('#s-settings button')).borderTopWidth)"
    )
    assert float(width) >= 1, width
    game.assert_clean()


# ---- the hand that holds the phone --------------------------------------------


def _clear(boxes: dict[str, Any]) -> None:
    """No two thumb controls share a pixel, and all of them are on the screen."""
    names = ("joy", "jump", "zoom")
    for name in names:
        box = boxes[name]
        assert box["left"] >= 0 and box["right"] <= boxes["width"] + 1, (name, boxes)
    for i, one in enumerate(names):
        for other in names[i + 1 :]:
            a, b = boxes[one], boxes[other]
            apart = (
                a["right"] <= b["left"]
                or b["right"] <= a["left"]
                or a["bottom"] <= b["top"]
                or b["bottom"] <= a["top"]
            )
            assert apart, (one, other, boxes)


def test_the_left_handed_layout_swaps_the_stick_and_the_jump_button(
    game_android: GamePage,
) -> None:
    game = _started(game_android)
    before = game.page.evaluate(CONTROLS)
    assert before["joy"]["left"] < before["jump"]["left"], before
    _clear(before)
    _set(game, "hand", "left")
    game.page.click("#sheet button.x")
    after = game.page.evaluate(CONTROLS)
    assert after["joy"]["left"] > after["jump"]["left"], after
    _clear(after)
    game.screenshot("qol1-android-hand-left", clip_height=900)
    game.assert_clean()


# ---- interruptions ------------------------------------------------------------


def test_quiet_hides_the_toast_and_keeps_what_it_would_have_said(
    game_desktop: GamePage,
) -> None:
    game = game_desktop
    game.goto()
    game.start("Tom")
    _set(game, "toasts", "quiet")
    game.page.click("#sheet button.x")
    before = int(game.page.evaluate("window.__toasts()"))
    # The first stop delivered is an achievement, which is a toast.
    game.claim(1)
    game.until(f"window.__toasts() > {before}")
    assert not game.page.is_visible("#toast")
    assert game.page.evaluate("() => (window.__S().ach || []).length") >= 1
    game.assert_clean()


# ---- the rows a browser cannot obey -------------------------------------------


def test_a_browser_without_a_buzz_is_not_offered_the_buzz_row(
    game_desktop: GamePage,
) -> None:
    game_desktop.page.add_init_script(NO_VIBRATE)
    game = _started(game_desktop)
    _open_settings(game)
    assert game.page.locator("#set-haptics").count() == 0
    # The rows that do not depend on the platform are all there.
    for key in ("text", "spacing", "contrast", "hand", "toasts", "saver", "breaks"):
        assert game.page.locator(f"#set-{key}").count() == 1, key
    # A browser that can buzz is offered the row, so the gate is not a blanket.
    game.page.evaluate(
        "() => Object.defineProperty(navigator, 'vibrate',"
        " {configurable: true, value: () => true})"
    )
    game.page.click("#sheet button.x")
    _open_settings(game)
    assert game.page.locator("#set-haptics").count() == 1
    game.assert_clean()


def test_the_hints_button_waits_until_there_is_a_hint_to_show(
    game_desktop: GamePage,
) -> None:
    game = _started(game_desktop)
    _open_settings(game)
    assert game.page.locator("#s-settings button:has-text('hints')").count() == 0
    game.goto(state=dict(RETURNING, hints=["bridge"]))
    game.resume()
    _open_settings(game)
    game.page.click("#s-settings button:has-text('Show the hints again')")
    game.until("(window.__S().hints || []).length === 0")
    assert game.page.locator("#s-settings button:has-text('hints')").count() == 0
    game.assert_clean()


# ---- what a setting is, and is not --------------------------------------------


def test_a_setting_survives_an_imported_progress_code(game_desktop: GamePage) -> None:
    """The code carries the journey; the settings belong to this browser."""
    game = _started(game_desktop)
    _set(game, "text", "larger")
    _set(game, "hand", "left")
    said = game.import_code(encode_progress(name="Tom", done_w={"campus": [1, 2, 3]}))
    assert "3" in said, said
    assert game.page.evaluate("() => document.body.dataset.text") == "larger"
    assert game.page.evaluate("() => document.body.classList.contains('hand-left')")
    game.assert_clean()


def test_back_to_the_defaults_puts_every_new_row_back(game_desktop: GamePage) -> None:
    game = _started(game_desktop)
    _set(game, "text", "larger")
    _set(game, "spacing", "comfortable")
    _set(game, "hand", "left")
    _set(game, "toasts", "quiet")
    game.page.click("#s-settings button:has-text('Back to the defaults')")
    game.until("document.body.dataset.text === 'normal'")
    assert game.page.evaluate("() => document.body.dataset.spacing") == "normal"
    assert not game.page.evaluate(
        "() => document.body.classList.contains('hand-left')"
        " || document.body.classList.contains('quiet')"
    )
    game.assert_clean()
