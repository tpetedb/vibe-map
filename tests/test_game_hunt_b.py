"""Hunt batch B: panel chrome, toasts and overlap (issue #110).

One test per finding, each measuring a fact the page produced: a bounding box
against another bounding box, a rendered line against the line above it, a
name in the ARIA tree. Nothing here waits on a clock and nothing reads a toast
off the screen, because a toast is removed on a five second timer and a
rendered pixel is not a promise.

Every surface finding is measured on the three the course is played on: the
1440x900 laptop it is written for, Chromium with Pixel 7 metrics, and WebKit
with iPhone metrics. Where the finding is about the chrome around a panel the
measurement is repeated with the largest text size and the left-handed layout,
because both of those move what a player reads.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import pytest
from playwright.sync_api import Browser

from tests.conftest import (
    GAME_PATH,
    OUT,
    WAIT_MS,
    GamePage,
    _attach_error_collectors,
    encode_progress,
    phone_options,
)

# The laptop the course is written for, and the two phones.
SURFACES = ("desktop", "android", "iphone")
PHONES = ("android", "iphone")
DESKTOP = {"viewport": {"width": 1440, "height": 900}}

# The two ends of the reading settings: what a player gets out of the box, and
# the largest text with the stick swapped to the other hand. A layout that
# holds at both ends holds in between.
CONDITIONS = [
    pytest.param({"text": "normal", "hand": "right"}, id="default"),
    pytest.param({"text": "larger", "hand": "left"}, id="larger-left"),
]
# A toast lives five seconds. Headless Chromium draws this island in software,
# where a frame with soft shadows costs more than that to photograph, so the
# toast tests are played the way a player on a weak machine plays: shadows
# off. It is a setting in the panel and it changes nothing about where a box
# lands, only how long the renderer takes to hand one over.
FAST = {"shadows": "off"}


@pytest.fixture
def browsers(chromium: Browser, webkit: Browser) -> dict[str, Browser]:
    """The browser each surface runs in; WebKit is the proxy for iOS."""
    return {"desktop": chromium, "android": chromium, "iphone": webkit}


@contextmanager
def _surface(
    browsers: dict[str, Browser],
    server: str,
    surface: str,
    *,
    settings: dict[str, str] | None = None,
    record: dict[str, Any] | None = None,
) -> Iterator[GamePage]:
    """A started game on one surface, with its reading settings already set.

    The settings live in the same saved record as the progress, so a player
    who chose them last night arrives with them; seeding the record is how
    that player is reproduced rather than a way around the dropdown.
    """
    options = DESKTOP if surface == "desktop" else phone_options(surface)
    context = browsers[surface].new_context(**options)
    page = context.new_page()
    game = GamePage(page=page, url=server + GAME_PATH)
    _attach_error_collectors(page, game.errors)
    seed: dict[str, Any] = {"name": "Tom", "look": "own"}
    seed.update(record or {})
    if settings:
        seed["settings"] = settings
    game.goto(state=seed)
    game.start("Tom")
    try:
        yield game
    finally:
        context.close()


def _shot(game: GamePage, name: str) -> None:
    size = game.page.viewport_size
    game.screenshot(name, clip_height=size["height"] if size else 900)


def _shot_element(game: GamePage, selector: str, name: str) -> None:
    """One element, for a surface the page has scrolled to.

    A clipped page screenshot is measured from the top of the document, so it
    photographs the island rather than the vault once the reader is open.
    """
    OUT.mkdir(parents=True, exist_ok=True)
    game.page.locator(selector).screenshot(path=str(OUT / f"{name}.png"))


def _tag(surface: str, settings: dict[str, str]) -> str:
    return f"{surface}_{settings['text']}_{settings['hand']}"


# ---- B1: the panel scrolls under the HUD --------------------------------------

# The visible part of the reading column, against the pills the HUD is made
# of. An element scrolled out of the container still reports the box it would
# have, so each one is clipped to the scroller before it is compared: what is
# asked is whether a player can see text inside the HUD's band, not where the
# text would be if nothing were clipping it.
UNDER_HUD = """() => {
  const pills = [...document.querySelectorAll('#hud .pill, #hud .kpi')]
    .filter(e => e.getBoundingClientRect().height > 0.5)
    .filter(e => getComputedStyle(e).visibility !== 'hidden')
    .map(e => e.getBoundingClientRect());
  const inner = document.querySelector('#sheet .inner');
  const view = inner.getBoundingClientRect();
  const hits = [];
  for (const e of inner.querySelectorAll('h2,h3,h4,p,li,pre,button,code')) {
    const b = e.getBoundingClientRect();
    if (b.width < 1 || b.height < 1) continue;
    const t = Math.max(b.top, view.top), bo = Math.min(b.bottom, view.bottom);
    if (bo - t <= 0.5) continue;
    for (const pill of pills)
      if (Math.min(bo, pill.bottom) - Math.max(t, pill.top) > 0.5 &&
          Math.min(b.right, pill.right) - Math.max(b.left, pill.left) > 0.5)
        hits.push((e.textContent || '').trim().slice(0, 40) || e.tagName);
  }
  return {hits, innerTop: +view.top.toFixed(1),
          pillBottom: +Math.max(...pills.map(p => p.bottom)).toFixed(1),
          scrolled: inner.scrollTop};
}"""


@pytest.mark.parametrize("settings", CONDITIONS)
@pytest.mark.parametrize("surface", SURFACES)
def test_a_scrolled_panel_never_shows_text_inside_the_hud_band(
    browsers: dict[str, Browser],
    server: str,
    surface: str,
    settings: dict[str, str],
) -> None:
    """B1: the HUD floats over the panel, so the panel starts below it.

    The reading column is its own scroll container: when its top edge is under
    the bar, nothing it holds can appear inside the bar, however far it is
    scrolled.
    """
    with _surface(browsers, server, surface, settings=settings) as game:
        game.open_workstream(1)
        for scroll in (260, 10_000):
            game.page.eval_on_selector(
                "#sheet .inner", "(e, y) => e.scrollTop = y", scroll
            )
            game.still("document.querySelector('#sheet .inner').scrollTop")
            info = game.page.evaluate(UNDER_HUD)
            assert info["innerTop"] >= info["pillBottom"] - 0.5, info
            assert info["hits"] == [], info
        _shot(game, f"hunt_b1_{_tag(surface, settings)}")
        game.assert_clean()


# ---- B2: the toast covers the HUD ---------------------------------------------

# Every control the HUD offers, the minimap that hangs under it and the
# panel's own Close button, against the box the toast stack occupies.
CONTROLS = "#hud button, #hud .kpi, #hud-name, #sheet.on .x, #minimap, #minimap-btn"
TOAST_OVER = (
    """() => {
  const rect = e => { const b = e.getBoundingClientRect();
    return {t: b.top, b: b.bottom, l: b.left, r: b.right}; };
  const over = (a, b) => Math.min(a.b, b.b) - Math.max(a.t, b.t) > 0.5 &&
                         Math.min(a.r, b.r) - Math.max(a.l, b.l) > 0.5;
  const stack = document.getElementById('toast');
  const box = rect(stack);
  const covered = [...document.querySelectorAll('"""
    + CONTROLS
    + """')]
    .filter(e => e.getBoundingClientRect().height > 0.5)
    .filter(e => getComputedStyle(e).visibility !== 'hidden')
    .filter(e => over(box, rect(e)))
    .map(e => (e.textContent || '').trim().slice(0, 24) || e.id);
  return {box: {t: +box.t.toFixed(1), b: +box.b.toFixed(1),
                l: +box.l.toFixed(1), r: +box.r.toFixed(1)},
          covered, view: {w: innerWidth, h: innerHeight},
          notes: document.querySelectorAll('#toast .tst').length};
}"""
)

# The stack is up, its newest message has finished springing into place and
# the minimap has taken its own next place under the HUD. All three are
# things the page does for itself, so this waits for them instead of a clock;
# a layout that never reaches them runs out of the budget and fails.
SETTLED = """document.querySelectorAll('#toast .tst').length >= 1 &&
  (() => {
    const last = document.querySelector('#toast .tst:last-child');
    const t = getComputedStyle(last).transform;
    if (!(t === 'none' || Math.abs(new DOMMatrix(t).m42) < 0.5)) return false;
    const hud = document.getElementById('hud').getBoundingClientRect();
    return [...document.querySelectorAll('#minimap, #minimap-btn')]
      .filter(e => getComputedStyle(e).display !== 'none')
      .every(e => e.getBoundingClientRect().top >= hud.bottom - 0.5);
  })()"""


def _claim_the_first_stop(game: GamePage) -> None:
    """Deliver stop one through its own button, which unlocks an achievement.

    The achievement is a toast, so this is the shortest real path to one.
    """
    game.open_workstream(1)
    game.page.click("#sheet .screen.on button:has-text('Mark as done')")
    game.page.wait_for_selector("#toast .tst", state="attached", timeout=WAIT_MS)
    game.until(SETTLED)


@pytest.mark.parametrize("settings", CONDITIONS)
@pytest.mark.parametrize("surface", SURFACES)
def test_a_toast_covers_no_hud_control(
    browsers: dict[str, Browser],
    server: str,
    surface: str,
    settings: dict[str, str],
) -> None:
    """B2: the message hangs under the HUD instead of on top of its buttons."""
    with _surface(browsers, server, surface, settings={**settings, **FAST}) as game:
        _claim_the_first_stop(game)
        info = game.page.evaluate(TOAST_OVER)
        assert info["notes"] >= 1, info
        assert info["covered"] == [], info
        assert info["box"]["r"] <= info["view"]["w"] + 1, info
        assert info["box"]["b"] <= info["view"]["h"] + 1, info
        _shot(game, f"hunt_b2_{_tag(surface, settings)}")
        game.assert_clean()


MAP_SHOWN = """() => [...document.querySelectorAll('#minimap, #minimap-btn')]
     .filter(e => getComputedStyle(e).display !== 'none').length"""


@pytest.mark.parametrize("surface", ("desktop", "android"))
def test_a_toast_on_the_island_leaves_the_map_alone(
    browsers: dict[str, Browser], server: str, surface: str
) -> None:
    """B3 named the minimap, which puts itself under whatever the HUD holds.

    That is now where the stack hangs, so the two have to agree. A locked
    signpost says so in a toast with no panel open, which is the one moment
    the map is on screen to be covered.
    """
    with _surface(browsers, server, surface, settings=FAST) as game:
        game.walk_to(-14.4, 12.8)
        game.page.wait_for_selector("#toast .tst", state="attached", timeout=WAIT_MS)
        game.until(SETTLED)
        info = game.page.evaluate(TOAST_OVER)
        assert game.page.evaluate(MAP_SHOWN) >= 1, "no map on screen to measure"
        assert info["notes"] >= 1, info
        assert info["covered"] == [], info
        _shot(game, f"hunt_b3_{surface}_map")
        game.assert_clean()


TITLE_STACK = """() => {
  const stack = document.getElementById('toast');
  const box = stack.getBoundingClientRect();
  const z = e => Number(getComputedStyle(e).zIndex) || 0;
  return {visibility: getComputedStyle(stack).visibility,
          hud: z(document.getElementById('hud')),
          title: z(document.getElementById('title')),
          top: box.top, bottom: box.bottom, right: box.right,
          view: {w: innerWidth, h: innerHeight}};
}"""


@pytest.mark.parametrize("profile", PHONES)
def test_a_message_raised_on_the_title_is_not_left_behind_it(
    browsers: dict[str, Browser], server: str, profile: str
) -> None:
    """A repaired record is announced before the island is entered.

    The title owns the window then and the HUD is hidden under it, so the row
    the stack lives in has to come forward with the message in it. On a phone
    the panel covers the whole window, which is where this would be lost.
    """
    context = browsers[profile].new_context(**phone_options(profile))
    page = context.new_page()
    game = GamePage(page=page, url=server + GAME_PATH)
    _attach_error_collectors(page, game.errors)
    try:
        # Every record the game writes has a list under mentors; a string in
        # its place is the part that cannot be read, and the repair says so.
        game.goto(
            state={
                "name": "Tom",
                "look": "own",
                "mentors": "nonsense",
                "settings": FAST,
            }
        )
        page.wait_for_selector("#toast .tst", state="attached", timeout=WAIT_MS)
        info = page.evaluate(TITLE_STACK)
        assert info["visibility"] == "visible", info
        # Stacking has no geometry to measure: what can be asked is that the
        # row is painted over the panel that covers the window.
        assert info["hud"] > info["title"], info
        assert info["top"] >= 0 and info["bottom"] <= info["view"]["h"] + 1, info
        assert info["right"] <= info["view"]["w"] + 1, info
        _shot(game, f"hunt_b2_{profile}_title_message")
        game.assert_clean()
    finally:
        context.close()


VAULT_STACK = """() => {
  const stack = document.getElementById('toast');
  const box = stack.getBoundingClientRect();
  return {position: getComputedStyle(stack).position,
          hudBottom: document.getElementById('hud').getBoundingClientRect().bottom,
          top: box.top, bottom: box.bottom, right: box.right,
          view: {w: innerWidth, h: innerHeight}};
}"""


def test_the_stack_is_still_on_screen_while_the_vault_is_read(
    browsers: dict[str, Browser], server: str
) -> None:
    """Reading the vault takes the page past the HUD, and the stack with it.

    The stack belongs to the HUD, so it has to leave that row for as long as
    the reader owns the window, or a message raised while a note is open would
    be raised above the fold.
    """
    with _surface(browsers, server, "desktop", settings=FAST) as game:
        game.open_vault()
        game.still("window.scrollY")
        info = game.page.evaluate(VAULT_STACK)
        assert info["hudBottom"] <= 0, ("the HUD is still on screen", info)
        assert info["position"] == "fixed", info
        assert 0 <= info["bottom"] <= info["view"]["h"] + 1, info
        assert info["right"] <= info["view"]["w"] + 1, info
        game.assert_clean()


# ---- B3: a batch of unlocks stacks off the screen -----------------------------

STACK = """() => {
  const rect = e => { const b = e.getBoundingClientRect();
    return {t: +b.top.toFixed(1), b: +b.bottom.toFixed(1),
            l: +b.left.toFixed(1), r: +b.right.toFixed(1), h: +b.height.toFixed(1)}; };
  const stack = document.getElementById('toast');
  const notes = [...stack.querySelectorAll('.tst')];
  // A message that is still springing into place is on its way to the box,
  // not in it, so the newest one that has arrived is the one asked about.
  const still = notes.filter(n => { const t = getComputedStyle(n).transform;
    return t === 'none' || Math.abs(new DOMMatrix(t).m42) < 0.5; });
  const pills = [...document.querySelectorAll('#hud .pill, #hud .kpi')]
    .filter(e => e.getBoundingClientRect().height > 0.5)
    .map(e => e.getBoundingClientRect().bottom);
  return {box: rect(stack), pillBottom: +Math.max(...pills).toFixed(1),
          n: notes.length, arrived: still.length,
          newest: still.length ? rect(still[still.length - 1]) : null,
          view: {w: innerWidth, h: innerHeight}};
}"""


def _full_code() -> str:
    """A progress code with every island, mentor and artifact finished."""
    import json
    from pathlib import Path

    data = json.loads(
        (Path(__file__).resolve().parents[1] / "vibemap/data/campaign.json").read_text()
    )
    worlds = {
        world: list(range(1, len(island["ws"]) + 1))
        for world, island in data["evenings"].items()
    }
    return encode_progress(
        name="Tom",
        done_w=worlds,
        mentors=[m["id"] for m in data["mentors"]],
        artifacts_built=[a["id"] for a in data["artifacts"]],
    )


@pytest.mark.parametrize("surface", ("desktop", "android"))
def test_a_batch_of_unlocks_leaves_a_bounded_stack(
    browsers: dict[str, Browser], server: str, surface: str
) -> None:
    """B3: importing a finished campaign unlocks many achievements at once.

    The stack is bounded and stays under the HUD, so the newest message is
    always the one on screen and the island is never behind a column of them.
    Motion is off as well as the shadows: an import that places thirty-two
    buildings holds the frame loop for longer than a toast lives, so the
    springs that carry the messages in would outlast the messages.
    """
    with _surface(
        browsers, server, surface, settings={**FAST, "motion": "off"}
    ) as game:
        game.import_code(_full_code())
        game.until("document.querySelectorAll('#toast .tst').length >= 5")
        game.until(SETTLED)
        info = game.page.evaluate(STACK)
        covered = game.page.evaluate(TOAST_OVER)
        assert info["n"] >= 5, info
        assert covered["covered"] == [], covered
        assert info["box"]["t"] >= info["pillBottom"] - 0.5, info
        assert info["box"]["b"] <= info["view"]["h"] + 1, info
        assert info["box"]["h"] <= info["view"]["h"] * 0.45 + 1, info
        assert info["newest"] is not None, info
        assert info["newest"]["t"] >= info["box"]["t"] - 0.5, info
        assert info["newest"]["b"] <= info["box"]["b"] + 0.5, info
        _shot(game, f"hunt_b3_{surface}_batch")
        game.assert_clean()


# ---- B4: the panel dialog has no name and no aria-modal -----------------------


@pytest.mark.parametrize("screen", ("s-map", "s-1", "s-settings"))
def test_the_panel_is_a_named_modal_dialog(
    browsers: dict[str, Browser], server: str, screen: str
) -> None:
    """B4: a dialog without a name is announced as "dialog" and nothing else.

    The name is read out of the ARIA tree rather than out of the markup, so an
    attribute a browser ignores cannot pass this.
    """
    with _surface(browsers, server, "desktop") as game:
        game.page.evaluate("id => openSheet(id)", screen)
        game.page.wait_for_selector(f"#{screen}.on", state="attached")
        game.sheet_in_place()
        assert game.page.get_attribute("#sheet", "role") == "dialog"
        assert game.page.get_attribute("#sheet", "aria-modal") == "true"
        tree = game.page.locator("#sheet").aria_snapshot()
        first = tree.strip().splitlines()[0]
        assert re.match(r'^-\s+dialog\s+"[^"]+"', first), f"the panel is {first!r}"
        game.assert_clean()


# ---- B5: opening More blanks the KPI row --------------------------------------

KPIS = """() => {
  const rect = e => { const b = e.getBoundingClientRect();
    return {t: b.top, b: b.bottom, l: b.left, r: b.right}; };
  const over = (a, b) => Math.min(a.b, b.b) - Math.max(a.t, b.t) > 0.5 &&
                         Math.min(a.r, b.r) - Math.max(a.l, b.l) > 0.5;
  const menus = [document.getElementById('hud-menu'),
                 document.getElementById('hud-ter')]
    .filter(e => e.getBoundingClientRect().height > 0.5)
    .filter(e => getComputedStyle(e).display !== 'contents');
  const pills = [...document.querySelectorAll('#kpis .kpi')];
  return {visibility: getComputedStyle(document.getElementById('kpis')).visibility,
          total: pills.length,
          shown: pills.filter(p => p.getBoundingClientRect().height > 0.5).length,
          covered: pills.filter(p => menus.some(m => over(rect(m), rect(p))))
                        .map(p => (p.textContent || '').trim())};
}"""


@pytest.mark.parametrize("width", (1440, 1024, 900))
def test_the_menu_leaves_the_numbers_on_screen(
    chromium: Browser, server: str, width: int
) -> None:
    """B5: the open menu is nowhere near the pills, so they stay readable."""
    context = chromium.new_context(viewport={"width": width, "height": 900})
    page = context.new_page()
    game = GamePage(page=page, url=server + GAME_PATH)
    _attach_error_collectors(page, game.errors)
    try:
        game.goto(state={"name": "Tom", "look": "own"})
        game.start("Tom")
        page.click("#hud-more-btn")
        page.wait_for_selector("#hud-more.open", state="attached")
        info = page.evaluate(KPIS)
        assert info["visibility"] == "visible", info
        assert info["total"] >= 1 and info["shown"] == info["total"], info
        assert info["covered"] == [], info
        game.screenshot(f"hunt_b5_more_{width}", clip_height=320)
        game.assert_clean()
    finally:
        context.close()


# ---- B6: a wrapped heading has colliding lines --------------------------------

# One rect per rendered line, so the leading is measured where it is drawn.
LEADING = """() => {
  const out = [];
  for (const h of document.querySelectorAll('#sheet .screen.on h3')) {
    const node = [...h.childNodes].find(n => n.nodeType === 3 && n.textContent.trim());
    if (!node) continue;
    const range = document.createRange();
    range.selectNodeContents(node);
    const lines = [...range.getClientRects()].filter(r => r.width > 1);
    if (lines.length < 2) continue;
    out.push({text: (h.textContent || '').trim().slice(0, 40),
              size: parseFloat(getComputedStyle(h).fontSize),
              step: +(lines[1].top - lines[0].top).toFixed(2)});
  }
  return out;
}"""


@pytest.mark.parametrize("surface", ("desktop", "android"))
def test_a_wrapped_heading_keeps_its_leading(
    browsers: dict[str, Browser], server: str, surface: str
) -> None:
    """B6: two lines of 12px caps need more than 13.2px between their tops."""
    with _surface(browsers, server, surface) as game:
        game.page.evaluate("openArtifact('switchboard')")
        game.page.wait_for_selector("#s-artifact.on", state="attached")
        game.sheet_in_place()
        wrapped = game.page.evaluate(LEADING)
        assert wrapped, "no heading wrapped, so this measures nothing"
        for head in wrapped:
            assert head["step"] >= head["size"] * 1.25, head
        _shot(game, f"hunt_b6_{surface}_heading")
        game.assert_clean()


# ---- B7: the demo terminal wraps mid-column and mid-number --------------------

TERMINAL = """() => {
  const el = document.getElementById('art-term');
  const node = [...el.childNodes].find(n => n.nodeType === 3);
  const range = document.createRange();
  range.selectNodeContents(node);
  // A forced break draws a rect of its own with no width; a line of output
  // draws one with both. Two rects with width for one line of output is the
  // fold this is about.
  const drawn = [...range.getClientRects()]
    .filter(r => r.height > 1 && r.width > 1).length;
  const text = el.textContent || '';
  return {drawn, lines: text.split('\\n').filter(l => l.trim()).length,
          longest: text.split('\\n').reduce((a, l) => Math.max(a, l.length), 0),
          scrollable: el.scrollWidth > el.clientWidth + 1,
          page: document.documentElement.scrollWidth -
                document.documentElement.clientWidth,
          column: document.querySelector('#sheet .inner').scrollWidth -
                  document.querySelector('#sheet .inner').clientWidth};
}"""


@pytest.mark.parametrize("profile", PHONES)
def test_the_demo_terminal_keeps_every_line_whole(
    browsers: dict[str, Browser], server: str, profile: str
) -> None:
    """B7: a transcript is columns, so a phone scrolls it rather than folding it.

    One rendered line per line of output is the fact: a wrapped line draws two
    rects, which is what broke a number in half.
    """
    with _surface(browsers, server, profile) as game:
        game.page.evaluate("openArtifact('data-centre')")
        game.page.wait_for_selector("#s-artifact.on", state="attached")
        game.page.click("#s-artifact button[data-demo='0']")
        # The transcript types itself out line by line, so the wait is for the
        # last line of it rather than for the typing to look finished.
        game.page.wait_for_function(
            "t => (document.getElementById('art-term').textContent || '').includes(t)",
            arg="one token at a time",
            timeout=WAIT_MS,
        )
        info = game.page.evaluate(TERMINAL)
        assert info["lines"] >= 5, info
        assert info["drawn"] == info["lines"], info
        assert info["scrollable"], "a line wider than the phone has to scroll"
        assert info["page"] <= 1 and info["column"] <= 1, info
        _shot(game, f"hunt_b7_{profile}_terminal")
        game.assert_clean()


# ---- B8: a dimmed shelf cannot be undimmed on a touch screen ------------------

# The contrast of the text a dimmed shelf shows, composited the way the screen
# composites it: opacity multiplies every layer, so the ratio is computed from
# the colours after the stack of opacities has been applied.
DIMMED = """() => {
  const lin = c => { const v = c / 255;
    return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
  const parse = s => (s.match(/[\\d.]+/g) || [0, 0, 0]).map(Number);
  const alpha = e => { let a = 1;
    for (let n = e; n && n !== document.body; n = n.parentElement)
      a *= Number(getComputedStyle(n).opacity);
    return a; };
  // Everything sits on the tree's own background, which is the page black.
  const tree = document.getElementById('vtree');
  const page = parse(getComputedStyle(tree).backgroundColor);
  const mix = (c, a) => c.slice(0, 3).map((v, i) => v * a + page[i] * (1 - a));
  const lum = c => 0.2126 * lin(c[0]) + 0.7152 * lin(c[1]) + 0.0722 * lin(c[2]);
  const ratio = (x, y) => { const a = lum(x), b = lum(y);
    return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05); };
  // A surface with no fill of its own shows the page through it.
  const surface = e => { const c = parse(getComputedStyle(e).backgroundColor);
    return c.length > 3 && c[3] === 0 ? page.slice(0, 3) : mix(c, alpha(e)); };
  const shelf = document.querySelector('#vtree .age.faded');
  if (!shelf) return null;
  const a = alpha(shelf);
  const back = surface(shelf);
  const out = [];
  for (const sel of ['h4', '.lvl', 'p', '.tech']) {
    const el = shelf.querySelector(sel);
    if (!el) continue;
    const fg = mix(parse(getComputedStyle(el).color), alpha(el));
    const bg = sel === '.tech' ? surface(el) : back;
    out.push({what: sel, size: parseFloat(getComputedStyle(el).fontSize),
              ratio: +ratio(fg, bg).toFixed(2)});
  }
  return {opacity: a, parts: out,
          shelves: document.querySelectorAll('#vtree .age.faded').length};
}"""


@pytest.mark.parametrize("profile", PHONES)
def test_a_shelf_you_did_not_choose_still_reads_without_a_hover(
    browsers: dict[str, Browser], server: str, profile: str
) -> None:
    """B8: a finger has no hover, so a set-back shelf has to read as it is."""
    with _surface(browsers, server, profile, record={"interests": ["data"]}) as game:
        game.hud_action("#hud button:has-text('Tree')")
        game.page.wait_for_selector("#vtree.on", state="attached")
        game.page.wait_for_selector("#vtree .age.faded", state="attached")
        # The vault fades in, and a colour read mid-fade is the fade's, not
        # the shelf's: the end of that animation is the page's own signal.
        game.until(
            "Number(getComputedStyle(document.getElementById('vault')).opacity) === 1"
        )
        info = game.page.evaluate(DIMMED)
        assert info is not None and info["shelves"] >= 1, info
        for part in info["parts"]:
            assert part["ratio"] >= 4.5, (part, info["opacity"])
        _shot_element(game, "#vtree", f"hunt_b8_{profile}_tree")
        game.assert_clean()
