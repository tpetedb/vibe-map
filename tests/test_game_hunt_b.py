"""Hunt batch B: panel chrome, toasts and overlap (issue #110).

One test per finding, each measuring a fact the page produced: a bounding box
against another bounding box, a rendered line against the line above it, a
name in the ARIA tree.

Nothing here waits on a clock, and nothing measures a toast that the page put
on screen: a toast removes itself five seconds after it was raised, so a test
that walks to a signpost and then looks for the element is racing that timer
on a loaded runner. The two halves are measured where neither can expire. The
real path is proved by what the page keeps: the count in window.__toasts()
and the node recorded by a mutation observer as it was appended, both of
which outlive the message. The geometry is measured on a stack this file
fills with the markup toast() writes, which the real path test pins.

Every surface finding is measured on the three the course is played on: the
1440x900 laptop it is written for, Chromium with Pixel 7 metrics, and WebKit
with iPhone metrics. Where the finding is about the chrome around a panel the
measurement is repeated with the largest text size and the left-handed
layout, because both of those move what a player reads: left-handed the zoom
column swaps to the side the stack hangs on, which is the hand the stack has
to be measured in.

A message is measured with the longest one the game can raise, the widest
bottle lesson out of the package data, because a message is as tall as its
words and the bound is about height. It is measured over an open panel as
well as over the island, because that is where a batch of unlocks is raised
and where a card that leans on what is behind it stops being readable.
"""

from __future__ import annotations

import io
import re
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import pytest
from PIL import Image
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
# Headless Chromium draws this island in software, where a frame with soft
# shadows costs more than the rest of the frame put together. The toast tests
# are played the way a player on a weak machine plays: shadows off. It is a
# setting in the panel and it changes nothing about where a box lands.
FAST = {"shadows": "off"}


@pytest.fixture
def browsers(chromium: Browser, webkit: Browser) -> dict[str, Browser]:
    """The browser each surface runs in; WebKit is the proxy for iOS."""
    return {"desktop": chromium, "android": chromium, "iphone": webkit}


def _options(surface: str) -> dict[str, Any]:
    """The context a surface is played in: the laptop, or one of the phones."""
    return DESKTOP if surface == "desktop" else phone_options(surface)


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
    context = browsers[surface].new_context(**_options(surface))
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


def _shot_view(game: GamePage, name: str) -> None:
    """What the window shows, for a message that is fixed to the window."""
    OUT.mkdir(parents=True, exist_ok=True)
    game.page.screenshot(path=str(OUT / f"{name}.png"))


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


# ---- B2 and B3: the toast stack -----------------------------------------------

# Every message the game raises, recorded as it is appended. A toast is gone
# five seconds later, so this is what a test can read afterwards and be sure
# of: where the node was put, what it was made of, and how many there were.
# The document is what is watched rather than its root element, because this
# also runs before the page has one, to catch a message raised during boot.
WATCH = """() => {
  window.__seen = [];
  new MutationObserver(list => {
    for (const change of list) for (const node of change.addedNodes)
      if (node.nodeType === 1 && node.classList &&
          node.classList.contains('tst'))
        window.__seen.push({
          parent: node.parentElement ? node.parentElement.id : null,
          hud: !!node.closest('#hud'),
          cls: node.className,
          kids: [...node.children].map(k => k.tagName),
          text: (node.textContent || '').trim().slice(0, 40)});
  }).observe(document, {subtree: true, childList: true});
}"""

# The markup toast() writes: the icon, the title, the line under it. The real
# path test asserts a raised message has exactly this shape, so what is
# measured here is the message a player gets and not a box of the test's own.
FILL = """([n, title, body]) => {
  const stack = document.getElementById('toast');
  for (let i = 0; i < n; i++) {
    const node = document.createElement('div');
    node.className = 'tst';
    node.innerHTML =
      '<b><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"></svg>' +
      title + '</b><span>' + body + '</span>';
    stack.appendChild(node);
  }
  return document.querySelectorAll('#toast .tst').length;
}"""

# The message a claim raises, as 18-avatar.js writes it.
CLAIMED = (
    "Achievement: First light",
    "You delivered your first stop. Unlocked: the head torch, in the Backpack.",
)


def _widest() -> tuple[str, str]:
    """The tallest message the game can raise, as 19c-bottles.js writes it.

    A bound on a stack is a bound on height, and height is words: the widest
    message is the longest bottle lesson and its link, read out of the package
    data so that a longer lesson written tomorrow is what this measures.
    """
    import json
    from pathlib import Path

    items = json.loads(
        (Path(__file__).resolve().parents[1] / "vibemap/data/items.json").read_text()
    )
    bottle = max(items["bottles"], key=lambda b: len(b["lesson"]))
    return (
        "A message in a bottle: " + bottle["title"],
        bottle["lesson"] + ' <a href="#">Read the topic</a>',
    )


WIDEST = _widest()

# One card, and the colour it is painted in. The strip measured is inside the
# border and left of the text, where the card draws nothing of its own: what a
# player sees there is the card's colour, or a blend of it and whatever is
# behind, which is what a card without its own surface shows.
CARD = """(which) => {
  const cards = [...document.querySelectorAll('#toast .tst')];
  const card = which === 'newest' ? cards[cards.length - 1] : cards[0];
  const b = card.getBoundingClientRect();
  return {x: b.left, y: b.top, w: b.width, h: b.height,
          colour: getComputedStyle(card).backgroundColor};
}"""

# Every control the HUD offers, the minimap that hangs under it, the zoom
# column and the panel's own Close button, against the box the stack occupies.
CONTROLS = (
    "#hud button, #hud .kpi, #hud-name, #sheet.on .x, "
    "#minimap, #minimap-btn, #zoom button"
)
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
    .filter(e => getComputedStyle(e).display !== 'none')
    .filter(e => over(box, rect(e)))
    .map(e => (e.textContent || '').trim().slice(0, 24) || e.id);
  return {box: {t: +box.t.toFixed(1), b: +box.b.toFixed(1),
                l: +box.l.toFixed(1), r: +box.r.toFixed(1)},
          covered, view: {w: innerWidth, h: innerHeight},
          notes: document.querySelectorAll('#toast .tst').length};
}"""
)

# What hangs under the HUD besides the stack, and the column of buttons in the
# bottom corner it must not be pushed onto. The minimap puts itself under the
# bar's own box (32-minimap.js), so this is the pair that says whether a
# message moved anything.
NEIGHBOURS = """() => {
  const rect = e => { if (!e) return null;
    if (getComputedStyle(e).display === 'none') return null;
    const b = e.getBoundingClientRect();
    return {t: +b.top.toFixed(1), b: +b.bottom.toFixed(1),
            l: +b.left.toFixed(1), r: +b.right.toFixed(1)}; };
  const over = (a, b) => a && b && Math.min(a.b, b.b) - Math.max(a.t, b.t) > 0.5 &&
                         Math.min(a.r, b.r) - Math.max(a.l, b.l) > 0.5;
  const map = rect(document.getElementById('minimap'));
  const btn = rect(document.getElementById('minimap-btn'));
  const zoom = rect(document.getElementById('zoom'));
  return {map, btn, zoom, hudBottom: +document.getElementById('hud')
            .getBoundingClientRect().bottom.toFixed(1),
          onZoom: [map, btn].filter(e => over(e, zoom)).length};
}"""

# Whatever the map is showing itself as on this surface: the canvas on a
# laptop, the button it hides behind on a phone. It lays itself out from the
# frame loop, so its top is the number that says it has had its say.
MAP_TOP = """(() => {
  const e = [...document.querySelectorAll('#minimap, #minimap-btn')]
    .find(x => getComputedStyle(x).display !== 'none');
  return e ? e.getBoundingClientRect().top
           : document.getElementById('hud').getBoundingClientRect().bottom;
})()"""


def _settled(game: GamePage) -> None:
    """The stack has its box and the map has taken its place under the bar.

    Both are things the page settles by itself, so this waits for them rather
    than for a number of frames or a length of time.
    """
    game.still("document.getElementById('toast').getBoundingClientRect().height")
    game.still(MAP_TOP)


def _fill(game: GamePage, n: int, message: tuple[str, str] = CLAIMED) -> int:
    """Put n messages of the shape toast() writes into the HUD's stack."""
    count = int(game.page.evaluate(FILL, [n, *message]))
    _settled(game)
    return count


def _reads_as_itself(game: GamePage, which: str = "newest") -> dict[str, Any]:
    """The card shows its own colour, not a mix of it and what is behind it.

    A translucent card leans on a backdrop blur, which nothing behind a mask
    keeps and which a page of text defeats anyway. The strip is read off the
    screenshot, so this is the colour a player sees and not a declaration.
    """
    card = game.page.evaluate(CARD, which)
    want = tuple(int(v) for v in re.findall(r"\d+", card["colour"])[:3])
    clip = {
        "x": card["x"] + 3,
        "y": card["y"] + 16,
        "width": 6,
        "height": max(8, card["h"] - 32),
    }
    image = Image.open(io.BytesIO(game.page.screenshot(clip=clip))).convert("RGB")
    raw = image.tobytes()
    seen = {tuple(raw[i : i + 3]) for i in range(0, len(raw), 3)}
    off = [p for p in seen if max(abs(p[i] - want[i]) for i in range(3)) > 1]
    assert not off, ("what is behind the card reads through it", want, off[:6], card)
    return card


def test_a_claimed_stop_puts_its_message_in_the_huds_stack(
    browsers: dict[str, Browser], server: str
) -> None:
    """The real path, measured where nothing expires.

    Delivering stop one unlocks an achievement, which is a toast. What is
    asked is the part the geometry tests rest on: that the game appends its
    message to the stack the HUD holds, and that the message is a card with a
    title and a line.
    """
    with _surface(browsers, server, "desktop", settings=FAST) as game:
        game.page.evaluate(WATCH)
        game.open_workstream(1)
        game.page.click("#sheet .screen.on button:has-text('Mark as done')")
        game.until("window.__toasts() >= 1")
        seen = game.page.evaluate("window.__seen")
        assert len(seen) >= 1, seen
        for note in seen:
            assert note["parent"] == "toast", note
            assert note["hud"] is True, note
            assert note["cls"] == "tst", note
            assert note["kids"] == ["B", "SPAN"], note
        game.assert_clean()


@pytest.mark.parametrize("settings", CONDITIONS)
@pytest.mark.parametrize("surface", SURFACES)
def test_a_message_covers_no_control(
    browsers: dict[str, Browser],
    server: str,
    surface: str,
    settings: dict[str, str],
) -> None:
    """B2: the message hangs under the HUD instead of on top of its buttons."""
    with _surface(browsers, server, surface, settings={**settings, **FAST}) as game:
        _fill(game, 1)
        info = game.page.evaluate(TOAST_OVER)
        assert info["notes"] == 1, info
        assert info["covered"] == [], info
        assert info["box"]["r"] <= info["view"]["w"] + 1, info
        assert info["box"]["b"] <= info["view"]["h"] + 1, info
        _reads_as_itself(game)
        _shot(game, f"hunt_b2_{_tag(surface, settings)}")
        game.assert_clean()


@pytest.mark.parametrize("settings", CONDITIONS)
@pytest.mark.parametrize("surface", SURFACES)
def test_a_full_stack_is_bounded_and_moves_nothing(
    browsers: dict[str, Browser],
    server: str,
    surface: str,
    settings: dict[str, str],
) -> None:
    """B3: a batch of unlocks leaves a stack, and a stack is only itself.

    It is bounded, so it never runs off the top of the window, and it is out
    of the HUD's own box, so the minimap that hangs under that box stays
    where it was instead of stepping down the window onto the zoom column.

    The bound is the room between the bar and the buttons at the bottom, so it
    is measured in both hands: left-handed the zoom column swaps to the side
    the stack hangs on and stands straight under it. The stack is filled with
    the widest message the game has, because a bound reached by two messages
    is not reached by nine short ones.
    """
    with _surface(browsers, server, surface, settings={**settings, **FAST}) as game:
        _settled(game)
        before = game.page.evaluate(NEIGHBOURS)
        assert before["map"] or before["btn"], ("no map on screen", before)
        assert before["onZoom"] == 0, before
        assert _fill(game, 9, WIDEST) == 9
        after = game.page.evaluate(NEIGHBOURS)
        info = game.page.evaluate(TOAST_OVER)
        for part in ("map", "btn", "hudBottom"):
            assert before[part] == after[part], (part, before, after)
        assert after["onZoom"] == 0, after
        assert info["covered"] == [], info
        assert info["box"]["t"] >= 0, info
        assert info["box"]["b"] <= info["view"]["h"] + 1, info
        assert info["box"]["b"] - info["box"]["t"] <= info["view"]["h"] * 0.4 + 1, info
        # The message just raised is whole: the stack gives way at the far end
        # from the bar, never on the card a player is being shown.
        newest = _reads_as_itself(game)
        assert newest["y"] >= info["box"]["t"] - 0.5, (newest, info)
        assert newest["y"] + newest["h"] <= info["box"]["b"] + 0.5, (newest, info)
        _shot(game, f"hunt_b3_{_tag(surface, settings)}_stack")
        game.assert_clean()


@pytest.mark.parametrize("surface", SURFACES)
def test_a_full_stack_over_an_open_panel_covers_nothing_and_hides_it(
    browsers: dict[str, Browser], server: str, surface: str
) -> None:
    """B3 where a batch is really raised: over the panel that raised it.

    The import button is in the Roadmap, so the messages come up over an open
    panel, and on a phone that panel is the whole window. Two things have to
    hold there: the stack still covers no control, the panel's own Close among
    them, and a message is still read, which a card without a surface of its
    own is not over a page of text.
    """
    with _surface(browsers, server, surface, settings=FAST) as game:
        game.open_workstream(1)
        assert _fill(game, 9, WIDEST) == 9
        info = game.page.evaluate(TOAST_OVER)
        assert info["covered"] == [], info
        assert info["box"]["t"] >= 0, info
        assert info["box"]["b"] <= info["view"]["h"] + 1, info
        assert info["box"]["b"] - info["box"]["t"] <= info["view"]["h"] * 0.4 + 1, info
        _reads_as_itself(game)
        _shot(game, f"hunt_b3_{surface}_stack_on_panel")
        game.assert_clean()


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


def test_a_batch_of_unlocks_raises_every_message_into_the_stack(
    browsers: dict[str, Browser], server: str
) -> None:
    """B3, the path: importing a finished campaign unlocks many at once.

    Nine messages in one pass is the case the finding was about. Where they
    went is read off the record the observer kept, because by the time the
    import has placed thirty-two buildings the first of them may be gone.
    """
    with _surface(
        browsers, server, "desktop", settings={**FAST, "motion": "off"}
    ) as game:
        game.page.evaluate(WATCH)
        game.import_code(_full_code())
        game.until("window.__toasts() >= 5")
        seen = game.page.evaluate("window.__seen")
        assert len(seen) >= 5, seen
        assert {note["parent"] for note in seen} == {"toast"}, seen
        assert all(note["hud"] for note in seen), seen
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


@pytest.mark.parametrize("surface", SURFACES)
def test_a_message_raised_on_the_title_is_not_left_behind_it(
    browsers: dict[str, Browser], server: str, surface: str
) -> None:
    """A repaired record is announced before the island is entered.

    The title owns the window then and the HUD is hidden under it, so the row
    the stack lives in has to come forward with the message in it. On a phone
    the panel covers the whole window, which is where this would be lost; on
    the laptop it is a box in the middle of the sky, and the message lands
    somewhere else, so both are photographed.
    """
    context = browsers[surface].new_context(**_options(surface))
    page = context.new_page()
    game = GamePage(page=page, url=server + GAME_PATH)
    _attach_error_collectors(page, game.errors)
    try:
        # The repair happens while the page boots, so the record of it has to
        # be running before the first script does.
        page.add_init_script(f"({WATCH})()")
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
        game.until("window.__toasts() >= 1")
        seen = page.evaluate("window.__seen")
        assert len(seen) >= 1, seen
        assert seen[0]["parent"] == "toast", seen
        game.page.evaluate(FILL, [1, *CLAIMED])
        game.still("document.getElementById('toast').getBoundingClientRect().height")
        info = page.evaluate(TITLE_STACK)
        assert info["visibility"] == "visible", info
        # Stacking has no geometry to measure: what can be asked is that the
        # row is painted over the panel that covers the window.
        assert info["hud"] > info["title"], info
        assert info["top"] >= 0 and info["bottom"] <= info["view"]["h"] + 1, info
        assert info["right"] <= info["view"]["w"] + 1, info
        _shot(game, f"hunt_b2_{surface}_title_message")
        game.assert_clean()
    finally:
        context.close()


VAULT_STACK = """() => {
  const stack = document.getElementById('toast');
  const box = stack.getBoundingClientRect();
  return {position: getComputedStyle(stack).position,
          hudBottom: document.getElementById('hud').getBoundingClientRect().bottom,
          top: box.top, bottom: box.bottom, left: box.left, right: box.right,
          notes: document.querySelectorAll('#toast .tst').length,
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
        game.page.evaluate(FILL, [1, *CLAIMED])
        game.still("document.getElementById('toast').getBoundingClientRect().height")
        info = game.page.evaluate(VAULT_STACK)
        assert info["hudBottom"] <= 0, ("the HUD is still on screen", info)
        assert info["position"] == "fixed", info
        assert info["notes"] == 1, info
        assert 0 <= info["bottom"] <= info["view"]["h"] + 1, info
        assert 0 <= info["left"] and info["right"] <= info["view"]["w"] + 1, info
        _shot_view(game, "hunt_b3_vault_stack")
        game.assert_clean()


# ---- B4: the panel dialog has no name ------------------------------------------

# Where the focus goes from the panel's own Close button, which is the first
# thing in it: backwards out of the panel is the answer this asks about.
FOCUSED = """() => { const a = document.activeElement;
  const label = a.getAttribute('aria-label') || a.textContent || '';
  return {tag: a.tagName, id: a.id, what: label.trim().slice(0, 24),
          inSheet: !!a.closest('#sheet')}; }"""


@pytest.mark.parametrize("screen", ("s-map", "s-1", "s-settings"))
def test_the_panel_is_a_named_dialog_and_claims_no_more_than_that(
    browsers: dict[str, Browser], server: str, screen: str
) -> None:
    """B4 asked for a name, and for aria-modal with it.

    The name is the half the markup can keep: it is read out of the ARIA tree
    rather than out of the attribute, so a name a browser ignores cannot pass.
    The other half is a promise this panel does not keep. The HUD floats over
    an open panel on purpose and its buttons stay in the tab order, so the
    page behind the dialog is reachable and aria-modal would tell a screen
    reader to ignore it. Confining the focus belongs to openSheet(); until it
    does, the attribute stays off, and this holds the two together: the day
    the focus is confined, this test asks for the attribute.
    """
    with _surface(browsers, server, "desktop") as game:
        game.page.evaluate("id => openSheet(id)", screen)
        game.page.wait_for_selector(f"#{screen}.on", state="attached")
        game.sheet_in_place()
        assert game.page.get_attribute("#sheet", "role") == "dialog"
        tree = game.page.locator("#sheet").aria_snapshot()
        first = tree.strip().splitlines()[0]
        assert re.match(r'^-\s+dialog\s+"[^"]+"', first), f"the panel is {first!r}"
        game.page.focus("#sheet .x")
        game.page.keyboard.press("Shift+Tab")
        behind = game.page.evaluate(FOCUSED)
        assert behind["inSheet"] is False, behind
        modal = game.page.get_attribute("#sheet", "aria-modal")
        assert modal != "true", (
            "the panel says it is modal while the keyboard leaves it",
            behind,
        )
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


@pytest.mark.parametrize("surface", SURFACES)
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


# ---- B7: the demo terminal folds mid-column and mid-number --------------------

# Where every step of a transcript is drawn. A step is one line of output; a
# step too wide for the panel folds, and the hanging indent is what tells the
# two apart on screen: a step starts at the column origin and the rest of a
# folded step is set in from it. The rects are read per step, so the answer is
# about the line the player sees rather than the string behind it.
TERMINAL = """() => {
  const el = document.getElementById('art-term');
  const box = el.getBoundingClientRect();
  const node = [...el.childNodes].find(n => n.nodeType === 3);
  const text = node.data;
  const steps = [];
  let at = 0;
  for (const line of text.split('\\n')) {
    const start = at;
    at += line.length + 1;
    if (!line.trim()) continue;
    const range = document.createRange();
    range.setStart(node, start);
    range.setEnd(node, start + line.length);
    const drawn = [...range.getClientRects()].filter(r => r.height > 1 && r.width > 1);
    steps.push({text: line.trim().slice(0, 32),
                lefts: drawn.map(r => +r.left.toFixed(1)),
                right: +Math.max(...drawn.map(r => r.right)).toFixed(1)});
  }
  // The last thing the demo prints is the sentence it is for, so the end of
  // it is measured on its own: characters, not the line they sit on.
  const tail = text.replace(/\\s+$/, '');
  const range = document.createRange();
  range.setStart(node, Math.max(0, tail.length - 24));
  range.setEnd(node, tail.length);
  const ends = [...range.getClientRects()].filter(r => r.height > 1 && r.width > 1)
    .map(r => ({l: +r.left.toFixed(1), r: +r.right.toFixed(1)}));
  const inner = document.querySelector('#sheet .inner');
  return {steps, ends, box: {l: +box.left.toFixed(1), r: +box.right.toFixed(1)},
          origin: +Math.min(...steps.flatMap(s => s.lefts)).toFixed(1),
          over: el.scrollWidth - el.clientWidth,
          column: inner.scrollWidth - inner.clientWidth,
          page: document.documentElement.scrollWidth -
                document.documentElement.clientWidth};
}"""


def _run_demo(game: GamePage, artifact: str, demo: int, last: str) -> dict[str, Any]:
    """Open an artifact, press one of its demo buttons, read the transcript.

    The transcript types itself out a line at a time, so the wait is for the
    last line of it to be in the element rather than for the typing to look
    finished.
    """
    game.page.evaluate("id => openArtifact(id)", artifact)
    game.page.wait_for_selector("#s-artifact.on", state="attached")
    game.page.click(f"#s-artifact button[data-demo='{demo}']")
    game.page.wait_for_function(
        "t => (document.getElementById('art-term').textContent || '').includes(t)",
        arg=last,
        timeout=WAIT_MS,
    )
    game.sheet_in_place()
    return game.page.evaluate(TERMINAL)


@pytest.mark.parametrize("surface", SURFACES)
def test_a_demo_step_starts_at_the_column_and_a_fold_is_set_in(
    browsers: dict[str, Browser], server: str, surface: str
) -> None:
    """B7: the fold is what broke the columns, so the fold is marked.

    The data centre transcript is the one the finding measured: columns of
    arrows, tokens and milliseconds. Every step starts at the left edge of the
    text and nothing else does, so a line that begins at that edge is a step
    and a line set in from it is the rest of the step above. On a phone the
    steps are wider than the panel, which is the case this is about.
    """
    with _surface(browsers, server, surface) as game:
        info = _run_demo(game, "data-centre", 0, "one token at a time")
        steps, origin = info["steps"], info["origin"]
        assert len(steps) >= 5, info
        starts = 0
        for step in steps:
            assert min(step["lefts"]) <= origin + 0.5, (step, info)
            starts += sum(1 for left in step["lefts"] if left <= origin + 0.5)
        assert starts == len(steps), ("a fold started at the column", info)
        assert info["over"] <= 1, ("the transcript runs off its box", info)
        assert info["column"] <= 1 and info["page"] <= 1, info
        if surface in PHONES:
            assert any(len(step["lefts"]) > 1 for step in steps), (
                "nothing folded, so this measures nothing",
                info,
            )
        _shot(game, f"hunt_b7_{surface}_columns")
        game.assert_clean()


@pytest.mark.parametrize("surface", SURFACES)
def test_the_sentence_a_demo_ends_on_is_read_whole(
    browsers: dict[str, Browser], server: str, surface: str
) -> None:
    """B7, the other half: a transcript is mostly sentences, not columns.

    The fountain ends on a hundred and fifteen characters of plain English,
    which is longer than the box on every surface: it folds, and both halves
    of it are inside the box. A transcript that scrolled sideways instead
    would leave the end of that sentence off the right edge with nothing to
    say so.
    """
    with _surface(browsers, server, surface) as game:
        info = _run_demo(game, "fountain", 1, "the same way")
        assert info["ends"], info
        for rect in info["ends"]:
            assert rect["l"] >= info["box"]["l"] - 0.5, ("cut on the left", rect, info)
            assert rect["r"] <= info["box"]["r"] + 0.5, (
                "the end of the sentence is outside the box",
                rect,
                info,
            )
        assert info["over"] <= 1, ("the sentence runs off its box", info)
        assert info["column"] <= 1 and info["page"] <= 1, info
        last = info["steps"][-1]
        assert len(last["lefts"]) > 1, (
            "the sentence fits, so this proves nothing",
            info,
        )
        _shot(game, f"hunt_b7_{surface}_sentence")
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


@pytest.mark.parametrize("surface", SURFACES)
def test_a_shelf_you_did_not_choose_still_reads_without_a_hover(
    browsers: dict[str, Browser], server: str, surface: str
) -> None:
    """B8: a finger has no hover, so a set-back shelf has to read as it is.

    The laptop is here for the picture rather than for the hover: the colours
    a shelf keeps when nothing is pointing at it are the same on all three,
    and the tree is a wide grid there and a column on a phone.
    """
    with _surface(browsers, server, surface, record={"interests": ["data"]}) as game:
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
        _shot_element(game, "#vtree", f"hunt_b8_{surface}_tree")
        game.assert_clean()
