"""Quality of life: the hidden page, the buzz, the log and the saved mark.

Every test drives the real path (the real button, the real dropdown, the real
event the browser fires) and waits for a fact the page produced: a state, a
drawn frame, a line in the log. Nothing here waits on a wall clock, and
nothing reads a toast off the screen, because a toast removes itself after
five seconds and a loaded runner loses that race.
"""

from __future__ import annotations

import math
from typing import Any

import pytest

from tests.conftest import GamePage

# A returning player, so the Roadmap and the lessons are there to claim.
RETURNING: dict[str, Any] = {"name": "Tom", "look": "own", "doneW": {"campus": [1, 2]}}

# The page's own visibility, driven from the test. Playwright cannot hide a
# page, so the two properties the game reads are replaced and the event the
# browser would fire is fired by hand: the listener under test is the real one,
# and because the frames keep coming here, a clock that was not paused is
# caught moving rather than only caught jumping.
FAKE_VISIBILITY = """(() => {
  window.__hidden = false;
  Object.defineProperty(document, 'hidden', {
    configurable: true, get: () => window.__hidden});
  Object.defineProperty(document, 'visibilityState', {
    configurable: true, get: () => window.__hidden ? 'hidden' : 'visible'});
  window.__setHidden = v => {
    window.__hidden = v;
    document.dispatchEvent(new Event('visibilitychange'));
  };
})()"""

# Every vibration the page asks for, in order. Headless Chromium has no motor,
# so the API the game talks to is what the test listens to.
RECORD_VIBRATIONS = """(() => {
  window.__vibes = [];
  Object.defineProperty(navigator, 'vibrate', {configurable: true,
    value: p => { window.__vibes.push(p); return true; }});
})()"""

# The saved mark lives for about a second, so where it was put and how it was
# announced are recorded as it arrives instead of looked for afterwards.
RECORD_SAVED = """(() => {
  window.__savedSeen = [];
  const note = n => { if (n.nodeType === 1 && n.classList.contains('saved'))
    window.__savedSeen.push({parent: n.parentElement.id,
      hidden: n.getAttribute('aria-hidden'), text: n.textContent}); };
  const root = document.documentElement || document;
  new MutationObserver(rs => rs.forEach(r => r.addedNodes.forEach(note)))
    .observe(root, {childList: true, subtree: true});
})()"""


def _well_formed(field: str, entry: Any) -> bool:
    """The shape load() promises for one entry of a list it validates."""
    if field == "hints":
        return isinstance(entry, str)
    return (
        isinstance(entry, dict)
        and isinstance(entry.get("ts"), (int, float))
        and isinstance(entry.get("t"), str)
        and isinstance(entry.get("b"), str)
    )


def _open_settings(game: GamePage) -> None:
    game.hud_action("#hud button:has-text('Settings')")
    game.page.wait_for_selector("#s-settings.on", state="attached")
    game.sheet_in_place()


def _set(game: GamePage, key: str, value: str) -> None:
    """Change one setting through its dropdown, as a player does."""
    _open_settings(game)
    game.page.select_option(f"#set-{key}", value)
    game.until(f"(window.__S().settings || {{}})[{key!r}] === {value!r}")
    game.page.click("#sheet button.x")


def _open_pack(game: GamePage, tab: str) -> None:
    game.hud_action("#hud button[aria-label='Backpack']")
    game.page.wait_for_selector("#s-pack.on", state="attached")
    game.page.click(f"#s-pack .packtabs button:has-text('{tab}')")
    game.sheet_in_place()


def _nearest_item(game: GamePage) -> dict[str, Any]:
    """The collectible closest to the walker, from the game's own debug seam."""
    pos = game.page.evaluate("window.__debug().pos")
    on_ground = game.page.evaluate("window.__avatar().onGround")
    assert on_ground, "no collectibles on the island"
    return min(on_ground, key=lambda i: math.hypot(i["x"] - pos[0], i["z"] - pos[2]))


def _started(game: GamePage, state: dict[str, Any] | None = None) -> GamePage:
    game.goto(state=dict(RETURNING, **(state or {})))
    game.resume()
    return game


# ---- 7. the page nobody is looking at -----------------------------------------


def test_a_hidden_page_stops_the_island_clock_and_comes_back_to_it(
    game: GamePage,
) -> None:
    """The clock the ambient animations read is an absolute phase: an hour in
    another app would teleport the boats, the birds and the lighthouse beam."""
    game.page.add_init_script(FAKE_VISIBILITY)
    _started(game)
    game.frames(2)
    game.page.evaluate("window.__setHidden(true)")
    game.until("window.__awake().hidden === true")
    stopped = float(game.page.evaluate("window.__awake().t"))
    assert stopped > 0, "the island clock never started"
    # The frames keep being drawn here; the clock they read does not move.
    game.frames(20)
    assert float(game.page.evaluate("window.__awake().t")) == stopped
    game.page.evaluate("window.__setHidden(false)")
    game.until("window.__awake().hidden === false")
    # Back on exactly the frame it left, and running again from there.
    assert float(game.page.evaluate("window.__awake().t")) == stopped
    game.frames(3)
    assert float(game.page.evaluate("window.__awake().t")) > stopped
    game.assert_clean()


def test_the_battery_saver_turned_off_keeps_the_island_running(
    game_desktop: GamePage,
) -> None:
    """Keep running is a setting a player chooses, so it is obeyed."""
    game = game_desktop
    game.page.add_init_script(FAKE_VISIBILITY)
    _started(game)
    _set(game, "saver", "off")
    before = float(game.page.evaluate("window.__awake().t"))
    game.page.evaluate("window.__setHidden(true)")
    game.frames(5)
    assert game.page.evaluate("window.__awake().hidden") is False
    assert float(game.page.evaluate("window.__awake().t")) > before
    game.page.evaluate("window.__setHidden(false)")
    game.assert_clean()


# ---- 10. a buzz on Android -----------------------------------------------------


def test_a_claim_buzzes_the_phone_and_the_setting_silences_it(
    game_android: GamePage,
) -> None:
    game = game_android
    game.page.add_init_script(RECORD_VIBRATIONS)
    game.goto()
    game.start("Tom")
    game.claim(1)
    game.until("(window.__vibes || []).length > 0")
    # The claim's own pattern first; the achievement it earns has its own and
    # is the next test.
    assert game.page.evaluate("window.__vibes[0]") == [22, 40, 22]
    _set(game, "haptics", "off")
    silent_from = int(game.page.evaluate("window.__vibes.length"))
    game.claim(2)
    assert int(game.page.evaluate("window.__vibes.length")) == silent_from
    game.assert_clean()


def test_an_achievement_buzzes_with_its_own_pattern(game_android: GamePage) -> None:
    """The second call site. A claim that earns one gives two patterns in the
    order they happened, the claim's and then the achievement's."""
    game = game_android
    game.page.add_init_script(RECORD_VIBRATIONS)
    game.goto()
    game.start("Tom")
    game.claim(1)
    game.until("(window.__S().ach || []).includes('first-light')")
    # The tail, not the whole list: after eleven at night Night owl unlocks
    # first, and that is the island being right rather than the test failing.
    vibes = game.page.evaluate("window.__vibes")
    assert vibes[-2:] == [[22, 40, 22], [16, 30, 16]], vibes
    game.assert_clean()


def test_walking_over_a_collectible_buzzes_the_phone(game_android: GamePage) -> None:
    """The third call site, reached the way a player reaches it: the arrow keys
    and a thing on the ground. The find's pattern is a single number, so no
    other call site can be mistaken for it."""
    game = game_android
    game.page.add_init_script(RECORD_VIBRATIONS)
    game.goto()
    game.start("Tom")
    item = _nearest_item(game)
    game.walk_to(item["x"], item["z"], tol=0.9)
    game.until(f"window.__avatar().items.includes({item['id']!r})")
    assert 16 in game.page.evaluate("window.__vibes")
    game.assert_clean()


def test_an_untouched_page_is_never_asked_to_buzz(game_android: GamePage) -> None:
    """An achievement unlocks from the frame loop, which runs behind the title
    screen, so a returning record reaches the buzz before anybody has tapped.
    Chrome blocks a vibration there and reports the refusal at error level, and
    zero page errors is the bar. The harness cannot show this by itself:
    Playwright's evaluate hands the page user activation, so the browser would
    take the call. What the island asks for is what this watches, and nothing
    here is ever clicked.
    """
    game = game_android
    game.page.add_init_script(RECORD_VIBRATIONS)
    game.goto(state={"name": "Tom", "doneW": {"campus": [1]}})
    game.until("(window.__S().ach || []).includes('first-light')")
    # The unlock really happened, and it said so: only the buzz was withheld.
    assert game.page.evaluate("window.__log().some(n => n.t.includes('Achievement'))")
    assert game.page.evaluate("window.__vibes") == []
    game.assert_clean()


def test_reduced_motion_is_a_still_phone_too(game_android: GamePage) -> None:
    """A buzz moves the phone, so the request for less movement covers it."""
    game = game_android
    game.page.add_init_script(RECORD_VIBRATIONS)
    game.page.emulate_media(reduced_motion="reduce")
    game.goto()
    game.start("Tom")
    before = int(game.page.evaluate("window.__toasts()"))
    game.claim(1)
    game.until(f"window.__toasts() > {before}")
    assert game.page.evaluate("window.__vibes") == []
    game.assert_clean()


# ---- 20. quiet, and the log that survives it -----------------------------------


def test_quiet_raises_no_toast_and_keeps_what_it_would_have_said(
    game_desktop: GamePage,
) -> None:
    game = game_desktop
    game.goto()
    game.start("Tom")
    _set(game, "toasts", "quiet")
    before = int(game.page.evaluate("window.__log().length"))
    raised = len(game.toasts())
    game.claim(1)
    game.until(f"window.__log().length > {before}")
    # The log grew, so the message happened; the page's record of the cards
    # it raised did not, so none was shown for it.
    assert game.toasts()[raised:] == []
    said = game.page.evaluate("window.__log().map(n => n.t).join(' ')")
    assert "Achievement" in said, said
    _open_pack(game, "Notifications")
    assert "Achievement" in (game.page.text_content("#s-pack") or "")
    game.screenshot("qol4-desktop-quiet-log", clip_height=900)
    game.assert_clean()


def test_a_message_that_mattered_outlives_the_five_seconds(game: GamePage) -> None:
    """A repaired record is the message a player most needs to read late."""
    game.goto(state={"name": "Tom", "path": "not a map"})
    game.until("window.__log().some(n => n.t.includes('Saved progress repaired'))")
    line = game.page.evaluate(
        "window.__log().find(n => n.t.includes('Saved progress repaired'))"
    )
    # The line keeps the words, not the markup they were shown in.
    assert "path" in line["b"], line
    assert "<" not in line["t"] and "<" not in line["b"], line
    game.assert_clean()


def test_the_log_keeps_the_last_sixty_lines(game: GamePage) -> None:
    """A full log and one more message: the oldest line is the one that goes.

    The record arrives full, so the cap is reached by a real message (the
    first-time hint the Backpack shows) rather than by a loop.
    """
    full = [{"ts": 1758400000000 + i, "t": f"old {i}", "b": "b"} for i in range(60)]
    _started(game, {"notes": full})
    assert len(game.page.evaluate("window.__log()")) == 60
    _open_pack(game, "Notifications")
    game.until("window.__log().some(n => n.t.includes('Tip'))")
    log = game.page.evaluate("window.__log()")
    said = [n["t"] for n in log]
    assert len(log) == 60
    assert "old 0" not in said, said[:3]
    assert "Tip" in said, said[-3:]
    game.assert_clean()


def test_the_stack_shows_a_few_cards_and_the_tab_keeps_them_all(
    game_android: GamePage,
) -> None:
    """A record that arrives having earned four achievements: one pass of the
    check unlocks all four, so four cards want the screen at once. Three is
    what a phone can read, and the tab keeps every line.
    """
    game = game_android
    # Thirty-two stops and ten things picked up: First light, Full evening,
    # Campaign and Ten things all answer true on the same pass.
    done = {w: [1, 2, 3, 4, 5, 6, 7, 8] for w in ("campus", "winter", "desert", "prod")}
    state = {"name": "Tom", "doneW": done, "items": [f"item-{i}" for i in range(10)]}
    game.goto(state=state)
    game.until("window.__log().filter(n => n.t.includes('Achievement')).length >= 4")
    # The peak is the fixture's, taken as each card arrived: a card removes
    # itself after five seconds, so the screen cannot be asked afterwards.
    seen = game.toast_peak()
    assert 0 < seen <= 3, (seen, game.toasts())
    game.assert_clean()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("hints", "not a list"),
        ("hints", [{"id": 1}]),
        ("notes", "not a list"),
        ("notes", [{"ts": "soon", "t": "x", "b": "y"}]),
    ],
)
def test_a_bad_value_in_the_record_costs_that_field_and_nothing_else(
    game: GamePage, field: str, value: Any
) -> None:
    game.goto(state={"name": "Tom", "doneW": {"campus": [1]}, field: value})
    game.until(f"Array.isArray(window.__S().{field})")
    # Nothing that was seeded survived; what is left is the shape load()
    # promises, which for notes is the line about the repair itself.
    kept = game.state()[field]
    assert all(_well_formed(field, entry) for entry in kept), kept
    assert [e for e in kept if str(e).find("soon") >= 0] == [], kept
    # The evening runs on everything else, and the player is told which part
    # started fresh.
    assert game.state()["doneW"]["campus"] == [1]
    game.until(f"window.__log().some(n => n.b.includes({field!r}))")
    game.resume()
    game.assert_clean()


# ---- 22. a first-time hint -----------------------------------------------------


def test_a_first_time_hint_shows_once_and_never_again(game_desktop: GamePage) -> None:
    game = _started(game_desktop)
    before = int(game.page.evaluate("window.__toasts()"))
    _open_pack(game, "Notifications")
    game.until(f"window.__toasts() > {before}")
    assert game.state()["hints"] == ["pack"]
    assert "Tip" in (game.page.text_content("#s-pack") or "")
    game.page.click("#sheet button.x")
    _open_pack(game, "Notifications")
    # The panel is open again and the hint was not said a second time. The
    # count is taken from the log rather than from the toasts, because the
    # island has other things to say while an evening runs.
    tips = game.page.evaluate("window.__log().filter(n => n.t.includes('Tip'))")
    assert len(tips) == 1, tips
    # The line was raised with an icon in front of it; what is kept is the
    # words, because the tab writes them back as text.
    assert tips[0]["t"] == "Tip", tips
    assert game.state()["hints"] == ["pack"]
    game.assert_clean()


# ---- 24. the mark that says it was written -------------------------------------


def test_a_claim_shows_the_saved_mark_and_takes_it_away_again(
    game_desktop: GamePage,
) -> None:
    game = game_desktop
    game.page.add_init_script(RECORD_SAVED)
    game.goto()
    game.start("Tom")
    before = int(game.page.evaluate("window.__saved().n"))
    game.claim(1)
    game.until(f"window.__saved().n > {before}")
    seen = game.page.evaluate("window.__savedSeen[window.__savedSeen.length - 1]")
    assert seen["text"] == "Saved"
    # In the message stack, out of the HUD's own layout, and silent to a
    # screen reader: the record being written is not news.
    assert seen["parent"] == "toast"
    assert seen["hidden"] == "true"
    game.until("document.querySelector('.saved') === null")
    game.assert_clean()


def test_the_mark_is_throttled_because_save_is_called_constantly(
    game: GamePage,
) -> None:
    game.goto()
    game.start("Tom")
    before = int(game.page.evaluate("window.__saved().n"))
    # setSetting is what every dropdown's onchange calls, and every call
    # writes the record: forty of them are still one mark.
    game.page.evaluate(
        "() => { for (let i = 0; i < 40; i++)"
        " setSetting('speed', i % 2 ? 'fast' : 'normal'); }"
    )
    assert int(game.page.evaluate("window.__saved().n")) <= before + 1
    game.assert_clean()


# ---- the panel, on the three screens the game is played on ---------------------


SEEDED_NOTES = [
    {"ts": 1758400000000, "t": "Picked up: The mug", "b": "A thing you carry."},
    {"ts": 1758403800000, "t": "<b>not markup</b>", "b": "A record is not our data."},
]


@pytest.mark.parametrize(
    "fixture", ["game_desktop", "game_android", "game_webkit_iphone"]
)
def test_the_notifications_tab_reads_a_record_it_did_not_write(
    fixture: str, request: pytest.FixtureRequest
) -> None:
    """The log is in the player's own browser, so it is text, never markup."""
    game: GamePage = request.getfixturevalue(fixture)
    # The hint has been seen and the achievements this record earns are
    # already unlocked, so the island has nothing of its own to say here.
    _started(
        game,
        {
            "notes": SEEDED_NOTES,
            "hints": ["pack"],
            "ach": ["first-light", "night-owl"],
        },
    )
    _open_pack(game, "Notifications")
    assert game.page.locator("#s-pack .pathrow").count() >= 2
    shown = game.page.text_content("#s-pack") or ""
    # The angle brackets are still angle brackets: a record is text.
    assert "<b>not markup</b>" in shown
    assert "Picked up: The mug" in shown
    game.screenshot(f"qol4-{fixture}-notifications", clip_height=900)
    game.assert_clean()
