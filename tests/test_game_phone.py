"""The game on a phone: the HUD, the More menu, the hint and the contrast.

Every test drives the real controls at real device metrics, on both phones:
Chromium with Pixel 7 metrics, which is what the owner plays on, and WebKit
with iPhone metrics, the closest headless proxy for iOS. Widths 360, 393 and
412 are the three phones the course is played on.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

import pytest
from playwright.sync_api import Browser

from tests.conftest import (
    GAME_PATH,
    WAIT_MS,
    GamePage,
    _attach_error_collectors,
    phone_options,
)

PROFILES = ("android", "iphone")
# Contrast of two colours the page reports, straight from WCAG 2.1: the pair
# has to clear 4.5:1 for body text.
CONTRAST = """([fg, bg]) => {
  const lin = c => c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
  const lum = css => { const [r, g, b] = css.match(/[\\d.]+/g).map(Number);
    return 0.2126 * lin(r / 255) + 0.7152 * lin(g / 255) + 0.0722 * lin(b / 255); };
  const a = lum(fg), b = lum(bg);
  return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
}"""


@pytest.fixture
def phones(chromium: Browser, webkit: Browser) -> dict[str, Browser]:
    """The browser each phone profile runs in."""
    return {"android": chromium, "iphone": webkit}


@contextmanager
def _phone(
    phones: dict[str, Browser],
    server: str,
    profile: str,
    *,
    width: int | None = None,
    height: int | None = None,
    name: str = "Lotte",
    init_script: str | None = None,
) -> Iterator[GamePage]:
    """A started game on one of the two phones, optionally at another size."""
    context = phones[profile].new_context(
        **phone_options(profile, width=width, height=height)
    )
    if init_script:
        context.add_init_script(init_script)
    page = context.new_page()
    game = GamePage(page=page, url=server + GAME_PATH)
    _attach_error_collectors(page, game.errors)
    game.goto()
    game.start(name)
    try:
        yield game
    finally:
        context.close()


@contextmanager
def _window(
    browser: Browser, server: str, width: int, height: int
) -> Iterator[GamePage]:
    """A page in a plain desktop window: a fine pointer, no touch."""
    context = browser.new_context(viewport={"width": width, "height": height})
    page = context.new_page()
    game = GamePage(page=page, url=server + GAME_PATH)
    _attach_error_collectors(page, game.errors)
    game.goto()
    try:
        yield game
    finally:
        context.close()


def _open_menu(game: GamePage) -> None:
    game.page.tap("#hud-more-btn")
    game.page.wait_for_selector("#hud-more.open", state="attached")
    game.until("document.getElementById('hud-menu').getBoundingClientRect().height > 0")


def _shot(game: GamePage, name: str) -> None:
    size = game.page.viewport_size
    game.screenshot(name, clip_height=size["height"] if size else 800)


MENU = """() => {
  const menu = document.getElementById('hud-menu');
  const rows = [...menu.querySelectorAll('button')]
    .filter(b => getComputedStyle(b).display !== 'none');
  const rect = e => { const r = e.getBoundingClientRect();
    return {t: r.top, b: r.bottom, l: r.left, r: r.right, h: r.height, w: r.width}; };
  const hits = [];
  for (let i = 0; i < rows.length; i++) for (let j = i + 1; j < rows.length; j++) {
    const a = rows[i].getBoundingClientRect(), b = rows[j].getBoundingClientRect();
    if (Math.min(a.right, b.right) - Math.max(a.left, b.left) > 0.5 &&
        Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > 0.5)
      hits.push(rows[i].textContent.trim() + ' over ' + rows[j].textContent.trim());
  }
  const style = getComputedStyle(menu);
  return {box: rect(menu), background: style.backgroundColor,
          backdrop: style.backdropFilter || style.webkitBackdropFilter,
          overflowY: style.overflowY,
          scrolls: menu.scrollHeight > menu.clientHeight + 1,
          labels: rows.map(b => b.textContent.trim()),
          rows: rows.map(rect), overlaps: hits,
          view: {w: innerWidth, h: innerHeight}};
}"""


@pytest.mark.parametrize("profile", PROFILES)
@pytest.mark.parametrize(
    ("width", "height"), [(360, 800), (393, 852), (412, 915), (852, 393)]
)
def test_the_more_menu_is_one_opaque_sheet_inside_the_window(
    phones: dict[str, Browser], server: str, profile: str, width: int, height: int
) -> None:
    """Issue 124: no row over another, nothing see through, nothing off screen."""
    with _phone(phones, server, profile, width=width, height=height) as game:
        _shot(game, f"phone_{profile}_{width}x{height}_island")
        _open_menu(game)
        menu = game.page.evaluate(MENU)
        _shot(game, f"phone_{profile}_{width}x{height}_menu")
        assert menu["overlaps"] == [], menu["overlaps"]
        assert menu["background"].startswith("rgb("), menu["background"]
        assert menu["backdrop"] == "none", menu["backdrop"]
        box = menu["box"]
        assert box["l"] >= -1 and box["r"] <= menu["view"]["w"] + 1, box
        assert box["t"] >= -1 and box["b"] <= menu["view"]["h"] + 1, box
        for label, row in zip(menu["labels"], menu["rows"], strict=True):
            assert row["h"] >= 44, f"{label} is {row['h']}px tall"
            assert row["l"] >= box["l"] - 1 and row["r"] <= box["r"] + 1, label
        if menu["scrolls"]:
            assert menu["overflowY"] == "auto", "a menu too tall to fit has to scroll"
            game.page.eval_on_selector(
                "#hud-menu", "m => m.scrollTo(0, m.scrollHeight)"
            )
            game.until(
                "document.querySelector('#hud-menu button:last-of-type')"
                ".getBoundingClientRect().bottom <= innerHeight + 1"
            )
        else:
            for label, row in zip(menu["labels"], menu["rows"], strict=True):
                assert row["t"] >= -1, f"{label} is above the window"
                assert row["b"] <= menu["view"]["h"] + 1, f"{label} is below the fold"
        game.assert_clean()


@pytest.mark.parametrize("profile", PROFILES)
def test_every_menu_row_opens_its_panel_on_a_tap(
    phones: dict[str, Browser], server: str, profile: str
) -> None:
    with _phone(phones, server, profile) as game:
        for label, ready in (
            ("Stats", "#s-dash.on"),
            ("Vault", "#vault.on"),
            ("Settings", "#s-settings.on"),
            ("Backpack", "#s-pack.on"),
        ):
            _open_menu(game)
            game.page.tap(f"#hud-menu button:has-text('{label}')")
            game.page.wait_for_selector(ready, state="attached", timeout=WAIT_MS)
            game.page.wait_for_selector("#hud-more.open", state="detached")
        game.assert_clean()


@pytest.mark.parametrize("profile", PROFILES)
def test_a_tap_beside_the_menu_closes_it_and_leaves_the_walker_alone(
    phones: dict[str, Browser], server: str, profile: str
) -> None:
    """The sheet's backdrop takes the tap, so the island is not walked to."""
    with _phone(phones, server, profile) as game:
        before = game.page.evaluate("window.__debug().pos")
        _open_menu(game)
        size = game.page.viewport_size or {"width": 412, "height": 915}
        game.page.touchscreen.tap(size["width"] // 2, size["height"] // 3)
        game.page.wait_for_selector("#hud-more.open", state="detached")
        game.frames(10)
        after = game.page.evaluate("window.__debug().pos")
        moved = max(abs(a - b) for a, b in zip(before, after, strict=True))
        assert moved < 0.5, f"the dismissing tap walked the avatar: {before} {after}"
        game.assert_clean()


@pytest.mark.parametrize("profile", PROFILES)
def test_escape_closes_the_menu(
    phones: dict[str, Browser], server: str, profile: str
) -> None:
    with _phone(phones, server, profile) as game:
        _open_menu(game)
        game.page.keyboard.press("Escape")
        game.page.wait_for_selector("#hud-more.open", state="detached")
        assert game.page.get_attribute("#hud-more-btn", "aria-expanded") == "false"
        game.assert_clean()


@pytest.mark.parametrize("profile", PROFILES)
def test_the_hint_names_the_controls_a_finger_has_and_stays_clear_of_them(
    phones: dict[str, Browser], server: str, profile: str
) -> None:
    with _phone(phones, server, profile) as game:
        info = game.page.evaluate(
            """() => {
              const hint = document.getElementById('hint');
              const over = other => { const a = hint.getBoundingClientRect();
                const b = other.getBoundingClientRect();
                return Math.min(a.right, b.right) - Math.max(a.left, b.left) > 0 &&
                       Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top) > 0; };
              const shown = [...hint.children]
                .filter(s => getComputedStyle(s).display !== 'none')
                .map(s => s.className);
              return {shown, text: hint.innerText,
                      onJoy: over(document.getElementById('joy')),
                      onJump: over(document.getElementById('jump'))};
            }"""
        )
        assert info["shown"] == ["touch"], info
        text = (info["text"] or "").lower()
        assert "stick" in text
        for keyboard in ("wasd", "space", "x to sit"):
            assert keyboard not in text, text
        assert not info["onJoy"] and not info["onJump"], info
        _shot(game, f"phone_{profile}_hint")
        game.assert_clean()


def test_the_hint_names_the_keys_on_a_mouse_and_keyboard(
    chromium: Browser, server: str
) -> None:
    with _window(chromium, server, 1440, 900) as game:
        game.start("Lotte")
        # The pill is uppercased by the stylesheet, so the words are compared
        # in one case.
        text = (game.page.inner_text("#hint") or "").lower()
        assert "wasd" in text and "x to sit" in text
        assert "stick" not in text, text
        game.assert_clean()


@pytest.mark.parametrize("profile", PROFILES)
def test_both_hud_rows_are_the_width_of_the_hud(
    phones: dict[str, Browser], server: str, profile: str
) -> None:
    """Issue 124: the name pill and the button pill line up, and fingers fit."""
    with _phone(phones, server, profile) as game:
        info = game.page.evaluate(
            """() => {
              const w = id => document.getElementById(id).getBoundingClientRect().width;
              const small = [...document.querySelectorAll('#hud-bar button')]
                .filter(b => b.getBoundingClientRect().height > 0)
                .filter(b => b.getBoundingClientRect().height < 44)
                .map(b => b.textContent.trim() + ':' +
                     Math.round(b.getBoundingClientRect().height));
              return {name: w('hud-name'), bar: w('hud-bar'), kpis: w('kpis'), small};
            }"""
        )
        assert abs(info["name"] - info["bar"]) < 1, info
        assert abs(info["name"] - info["kpis"]) < 1, info
        assert info["small"] == [], info["small"]
        game.assert_clean()


@pytest.mark.parametrize("profile", PROFILES)
@pytest.mark.parametrize(("width", "height"), [(393, 852), (852, 393)])
def test_the_stage_fits_the_window_and_the_speech_band_is_on_screen(
    phones: dict[str, Browser], server: str, profile: str, width: int, height: int
) -> None:
    """The stylesheet's promise: the scene and the bubble together are the window."""
    with _phone(phones, server, profile, width=width, height=height) as game:
        info = game.page.evaluate(
            """() => {
              const talk = document.getElementById('talk').getBoundingClientRect();
              const stage = document.getElementById('stage').getBoundingClientRect();
              return {scroll: document.documentElement.scrollHeight,
                      view: innerHeight, talkBottom: talk.bottom,
                      gap: talk.top - stage.bottom};
            }"""
        )
        assert info["scroll"] <= info["view"] + 1, info
        assert info["talkBottom"] <= info["view"] + 1, info
        assert abs(info["gap"]) < 2, info
        _shot(game, f"phone_{profile}_stage_{width}x{height}")
        game.assert_clean()


@pytest.mark.parametrize("profile", PROFILES)
def test_the_tall_map_keeps_the_speech_band_and_the_controls_on_screen(
    phones: dict[str, Browser], server: str, profile: str
) -> None:
    """Map size Tall gives the scene the window; the line still has to be read."""
    with _phone(phones, server, profile) as game:
        _open_menu(game)
        game.page.tap("#hud-menu button:has-text('Settings')")
        game.page.wait_for_selector("#s-settings.on", state="attached")
        game.page.select_option("#set-map", "tall")
        game.until("document.getElementById('stage').classList.contains('map-tall')")
        game.page.keyboard.press("Escape")
        game.page.wait_for_selector("#sheet.on", state="detached")
        info = game.page.evaluate(
            """() => {
              const r = id => document.getElementById(id).getBoundingClientRect();
              const talk = r('talk');
              const over = b =>
                Math.min(b.bottom, talk.bottom) - Math.max(b.top, talk.top) > 0 &&
                Math.min(b.right, talk.right) - Math.max(b.left, talk.left) > 0;
              return {bottom: talk.bottom, view: innerHeight, onJoy: over(r('joy')),
                      onJump: over(r('jump')), onHint: over(r('hint'))};
            }"""
        )
        assert info["bottom"] <= info["view"] + 1, info
        assert not (info["onJoy"] or info["onJump"] or info["onHint"]), info
        _shot(game, f"phone_{profile}_map_tall")
        game.assert_clean()


@pytest.mark.parametrize("profile", PROFILES)
def test_a_settings_option_shows_its_whole_value(
    phones: dict[str, Browser], server: str, profile: str
) -> None:
    """The bracketed value is the only thing an option adds, so it stays whole."""
    with _phone(phones, server, profile) as game:
        _open_menu(game)
        game.page.tap("#hud-menu button:has-text('Settings')")
        game.page.wait_for_selector("#s-settings.on", state="attached")
        clipped = game.page.evaluate(
            """() => [...document.querySelectorAll('#s-settings select')]
                 .filter(s => s.scrollWidth > s.clientWidth + 1)
                 .map(s => s.id + ': ' + s.options[s.selectedIndex].text)"""
        )
        assert clipped == [], clipped
        _shot(game, f"phone_{profile}_settings")
        game.assert_clean()


@pytest.mark.parametrize("profile", PROFILES)
def test_a_field_is_never_small_enough_to_zoom_the_page(
    phones: dict[str, Browser], server: str, profile: str
) -> None:
    """iOS zooms in on a focused field under 16px and never zooms back out."""
    with _phone(phones, server, profile) as game:
        game.open_roadmap()
        small = game.page.evaluate(
            """() => [...document.querySelectorAll('input, textarea, select')]
                 .filter(e => e.offsetParent !== null)
                 .filter(e => parseFloat(getComputedStyle(e).fontSize) < 16)
                 .map(e => (e.id || e.tagName) + ': ' +
                      getComputedStyle(e).fontSize)"""
        )
        assert small == [], small
        game.assert_clean()


@pytest.mark.parametrize("profile", PROFILES)
def test_a_tap_does_not_leave_a_button_looking_hovered(
    phones: dict[str, Browser], server: str, profile: str
) -> None:
    """A finger has no hover, so the lift a mouse gets must not stick to it."""
    with _phone(phones, server, profile) as game:
        game.page.tap("#hud-more-btn")
        game.page.wait_for_selector("#hud-more.open", state="attached")
        game.page.tap("#hud-more-btn")
        game.page.wait_for_selector("#hud-more.open", state="detached")
        transform = game.page.evaluate(
            "() => getComputedStyle(document.getElementById('hud-more-btn')).transform"
        )
        assert transform in ("none", "matrix(1, 0, 0, 1, 0, 0)"), transform
        game.assert_clean()


@pytest.mark.parametrize("profile", PROFILES)
def test_the_full_screen_entry_is_gone_where_the_api_is_not(
    phones: dict[str, Browser], server: str, profile: str
) -> None:
    """iPhone Safari has no Fullscreen API: the control would do nothing."""
    without = """Object.defineProperty(document, 'fullscreenEnabled',
        {value: false, configurable: true});
      Object.defineProperty(document, 'webkitFullscreenEnabled',
        {value: undefined, configurable: true});"""
    with _phone(phones, server, profile, init_script=without) as game:
        game.open_roadmap()
        assert not game.page.locator("#s-map button.fs-only").is_visible()
        game.page.evaluate("openSettings()")
        game.page.wait_for_selector("#s-settings.on", state="attached")
        assert not game.page.locator("#s-settings button.fs-only").is_visible()
        game.assert_clean()
    with _phone(phones, server, profile) as game:
        game.open_roadmap()
        has_api = game.page.evaluate(
            "() => !!(document.fullscreenEnabled || document.webkitFullscreenEnabled)"
        )
        shown = game.page.locator("#s-map button.fs-only").is_visible()
        assert shown == has_api, "the entry follows what the browser can do"
        game.assert_clean()


@pytest.mark.parametrize("profile", PROFILES)
def test_the_sheet_is_closed_with_its_own_button_over_the_hud(
    phones: dict[str, Browser], server: str, profile: str
) -> None:
    """The HUD stays above the sheet, so it may not sit on the sheet's Close."""
    with _phone(phones, server, profile) as game:
        _open_menu(game)
        game.page.tap("#hud-menu button:has-text('Settings')")
        game.page.wait_for_selector("#s-settings.on", state="attached")
        game.sheet_in_place()
        covered = game.page.evaluate(
            """() => {
              const x = document.querySelector('#sheet .x').getBoundingClientRect();
              const bar = document.getElementById('hud-bar').getBoundingClientRect();
              const head = document.querySelector('#s-settings h2')
                .getBoundingClientRect();
              const onX =
                Math.min(x.right, bar.right) - Math.max(x.left, bar.left) > 0 &&
                Math.min(x.bottom, bar.bottom) - Math.max(x.top, bar.top) > 0;
              return {onX, onHead: head.top < bar.bottom};
            }"""
        )
        assert not covered["onX"], "the HUD bar covers the sheet's Close button"
        assert not covered["onHead"], "the screen starts behind the HUD bar"
        game.page.tap("#sheet .x")
        game.page.wait_for_selector("#sheet.on", state="detached")
        game.assert_clean()


@pytest.mark.parametrize("profile", PROFILES)
def test_a_long_name_stays_on_one_line(
    phones: dict[str, Browser], server: str, profile: str
) -> None:
    long_name = "Wilhelmina Aleksandra Katharina von Hohenzollern-Sigmaringen"
    with _phone(phones, server, profile, name=long_name) as game:
        info = game.page.evaluate(
            """() => {
              const pill = document.getElementById('hud-name');
              return {h: pill.getBoundingClientRect().height,
                      clipped: pill.scrollWidth > pill.clientWidth + 1};
            }"""
        )
        assert info["h"] < 48, info
        assert info["clipped"], "a name too long for the pill gets an ellipsis"
        game.screenshot(f"phone_{profile}_long_name", clip_height=300)
        game.assert_clean()


@pytest.mark.parametrize("profile", PROFILES)
def test_a_blocked_roadmap_row_is_readable(
    phones: dict[str, Browser], server: str, profile: str
) -> None:
    """Seven of the eight rows a beginner first reads are blocked ones."""
    with _phone(phones, server, profile) as game:
        game.open_roadmap()
        pairs = game.page.evaluate(
            """() => {
              const row = document.querySelector('#plotlist button[disabled]');
              const read = e => ({fg: getComputedStyle(e).color,
                                  o: Number(getComputedStyle(e).opacity)});
              return {bg: getComputedStyle(row).backgroundColor,
                      rows: [read(row), read(row.querySelector('span'))]};
            }"""
        )
        for part in pairs["rows"]:
            assert part["o"] == 1, part
            ratio = game.page.evaluate(CONTRAST, [part["fg"], pairs["bg"]])
            assert ratio >= 4.5, f"{part['fg']} on {pairs['bg']} is {ratio:.2f}:1"
        _shot(game, f"phone_{profile}_roadmap_blocked")
        game.assert_clean()


@pytest.mark.parametrize("profile", PROFILES)
def test_a_status_pill_keeps_its_date_on_one_line(
    phones: dict[str, Browser], server: str, profile: str
) -> None:
    with _phone(phones, server, profile) as game:
        game.open_roadmap()
        tall = game.page.evaluate(
            """() => [...document.querySelectorAll('.pathrow .st')]
                 .filter(s => s.getBoundingClientRect().height > 26)
                 .map(s => s.textContent.trim())"""
        )
        assert tall == [], tall
        game.assert_clean()


def test_the_secondary_buttons_collapse_into_the_menu_below_820px(
    chromium: Browser, server: str
) -> None:
    """A 768px tablet window is not a desktop: the pill would run off the edge."""
    with _window(chromium, server, 768, 1024) as game:
        game.start("Lotte")
        assert not game.page.locator("#hud button:has-text('Vault')").is_visible()
        over = game.page.evaluate(
            """() => [...document.querySelectorAll('#hud .pill')]
                 .filter(p => p.getBoundingClientRect().right > innerWidth + 1)
                 .length"""
        )
        assert over == 0, "the HUD pill runs off the right edge"
        game.page.click("#hud-more-btn")
        game.page.wait_for_selector("#hud-more.open", state="attached")
        assert game.page.locator("#hud button:has-text('Vault')").is_visible()
        game.screenshot("viewport_768_menu", clip_height=520)
        game.assert_clean()


def test_the_name_pill_is_as_wide_as_its_name(chromium: Browser, server: str) -> None:
    """On an ultrawide screen the pill is a label, not a bar across the window."""
    with _window(chromium, server, 2560, 1080) as game:
        game.start("Lotte")
        width = game.page.evaluate(
            "() => document.getElementById('hud-name').getBoundingClientRect().width"
        )
        assert width < 600, f"the name pill is {width}px wide"
        game.screenshot("viewport_ultrawide", clip_height=300)
        game.assert_clean()


def test_a_vault_note_reads_at_aa(chromium: Browser, server: str) -> None:
    """The reader uses the palette surfaces, where the link blue clears AA."""
    with _window(chromium, server, 1440, 900) as game:
        game.start("Lotte")
        game.open_vault()
        note = game.page.evaluate(
            """() => {
              const bg = getComputedStyle(
                document.getElementById('vault')).backgroundColor;
              const parts = [];
              const sel = '#vnote .wl, #vnote h2, #vnote a';
              for (const el of document.querySelectorAll(sel)) {
                if (!el.textContent.trim()) continue;
                if (el.classList.contains('locked')) continue;
                parts.push([getComputedStyle(el).color,
                            el.textContent.trim().slice(0, 30)]);
              }
              return {bg, parts};
            }"""
        )
        assert note["parts"], "the note reader showed no links"
        low, name = 21.0, ""
        for colour, text in note["parts"]:
            ratio = game.page.evaluate(CONTRAST, [colour, note["bg"]])
            if ratio < low:
                low, name = ratio, text
        assert low >= 4.5, f"{name} reads at {low:.2f}:1"
        game.screenshot("viewport_vault_contrast")
        game.assert_clean()


def test_the_kpi_row_says_its_numbers_out_loud(chromium: Browser, server: str) -> None:
    with _window(chromium, server, 1440, 900) as game:
        game.start("Lotte")
        assert game.page.get_attribute("#kpis", "aria-live") == "polite"
        game.assert_clean()
