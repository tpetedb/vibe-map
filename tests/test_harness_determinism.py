"""What a browser test may depend on: not the hour, not the screen, not a file.

Three leaks made a green run depend on when and where it ran (issue 148): the
runner's clock unlocked an achievement whose toast took another test's place,
a toast was read off the screen after the five second timer had taken it away,
and the battery rendered into `docs/media`, which is tracked. A fourth item is
a wait that could not say why it gave up. Each finding has a test here, and
each of them fails without its fix.

The guards read the test sources, because that is where the leak is written
down: what a test passes to a screenshot is the path it will write, and a
selector that reads `#toast` is a test asking the screen instead of the page.
"""

from __future__ import annotations

import ast
import re
import tempfile
from datetime import date
from pathlib import Path
from typing import Any, cast

import pytest
from playwright.sync_api import Browser, Page
from playwright.sync_api import TimeoutError as PageTimeout

from tests.conftest import (
    GAME_PATH,
    NOON,
    OUT,
    ROOT,
    SHOT_MS,
    GamePage,
    game_context,
    out_file,
    writes_only_to_out,
)
from tests.test_game_camera import _zoom_is

FIXTURES = ["game", "game_desktop", "game_android", "game_webkit_iphone"]
TESTS = sorted(p for p in (ROOT / "tests").glob("test_*.py"))
# The two files the rule is written in: conftest.py is the one helper that
# owns it, this file is where the helper is put to the test.
GUARDS = {"conftest.py", "test_harness_determinism.py"}
# Two files still read a toast off the screen, and two build their own game
# page instead of taking a fixture. Neither pair is among the files this order
# may touch, so both are named here, both are on issue 148, and both lists may
# only shrink: a test below holds each name to still being the exception it
# claims to be.
STILL_READ_THE_SCREEN = {"test_game_bottles.py", "test_game_ui.py"}
HAND_BUILT_PAGES = {"test_game_phone.py", "test_game_news.py"}
# Whether the stack is on the screen is a fair question to ask the screen, and
# `#toast` on its own is the stack. A selector that reaches past it into a
# notice reads text that expires on a five second timer, whatever the call
# that holds it is called.
NOT_A_READ = {"is_visible"}
THE_STACK = "#toast"
# What names the stack or a notice inside it: the two selectors, and the
# element id as a page script quotes it, which is this suite's other idiom for
# reading text. A test that asks for a toast by its words instead
# (`get_by_text`) names no selector and no guard on selectors can see it; the
# record is what makes writing one unnecessary.
TOAST_SELECTORS = ("#toast", ".tst", "'toast'", '"toast"')
SCRIPT_READS_TOAST_TEXT = re.compile(
    r"(?:getElementById\(\s*['\"]toast['\"]\s*\)|"
    r"querySelector(?:All)?\(\s*['\"][^'\"]*(?:#toast|\.tst)[^'\"]*['\"]\s*\))"
    r"\s*\.\s*(?:textContent|innerText|innerHTML)\b"
)
# What tells a context opened for the game from one opened for another page
# the battery visits: the dashboard report and the syllabus are not this.
GAME_FILE = "vibe-map.html"


def _tree(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _calls(path: Path, name: str) -> list[ast.Call]:
    """Every call in the file to a method of that name, whoever it is on."""
    return [
        node
        for node in ast.walk(_tree(path))
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == name
    ]


def _literal_names(tree: ast.Module) -> dict[str, str]:
    """Every name in the file bound to a string literal.

    A selector is as often held in a variable as written at the call, so the
    guard has to see through one, annotated or not. Deliberately flat: the
    last binding wins, which over-reports rather than letting a read past.
    """
    names: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            targets: list[ast.expr] = list(node.targets)
            value = node.value
        elif isinstance(node, ast.AnnAssign):
            targets, value = [node.target], node.value
        else:
            continue
        if not isinstance(value, ast.Constant) or not isinstance(value.value, str):
            continue
        for target in targets:
            if isinstance(target, ast.Name):
                names[target.id] = value.value
    return names


def _strings(node: ast.AST, names: dict[str, str]) -> list[str]:
    """Every string this expression can be: written out, or held in a name."""
    out: list[str] = []
    for sub in ast.walk(node):
        if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
            out.append(sub.value)
        elif isinstance(sub, ast.Name) and sub.id in names:
            out.append(names[sub.id])
    return out


def _parents(tree: ast.Module) -> dict[ast.AST, ast.AST]:
    return {
        child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)
    }


def _operation(call: ast.Call, parents: dict[ast.AST, ast.AST]) -> str:
    """What the chain starting at this call finally does.

    `page.locator(sel).first.inner_text()` names the selector two steps before
    it reads it, and that chain is how Playwright asks to be used, so the
    guard follows the attributes up to the last call in the chain.
    """
    node: ast.AST = call
    name = call.func.attr if isinstance(call.func, ast.Attribute) else "call"
    while True:
        up = parents.get(node)
        if isinstance(up, ast.Attribute) and up.value is node:
            node = up
            continue
        if (
            isinstance(up, ast.Call)
            and up.func is node
            and isinstance(node, ast.Attribute)
        ):
            name = node.attr
            node = up
            continue
        return name


def toast_reads(source: str, name: str = "<sample>") -> list[str]:
    """Every place in this source that asks the screen about a toast.

    A call that names the stack or a notice inside it, in an argument of its
    own or through a variable, is a read of the screen unless it asks only
    whether the stack is there. Asking which method reads text would miss
    every shape but the one that was there when the rule was written.
    """
    tree = ast.parse(source, filename=name)
    names = _literal_names(tree)
    parents = _parents(tree)
    found: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        args: list[ast.AST] = [*node.args, *(kw.value for kw in node.keywords)]
        said = [
            s for a in args if not isinstance(a, ast.Call) for s in _strings(a, names)
        ]
        operation = _operation(node, parents)
        hits = [s for s in said if any(sel in s for sel in TOAST_SELECTORS)]
        if operation in {"evaluate", "still", "wait_for_function"}:
            hits = [s for s in hits if SCRIPT_READS_TOAST_TEXT.search(s)]
        if not hits:
            continue
        stack_only = all(s == THE_STACK for s in hits)
        if stack_only and operation in NOT_A_READ:
            continue
        found.append(f"{name}:{node.lineno} {ast.unparse(node)}")
    return found


def _builds_a_page(node: ast.AST) -> bool:
    """A call that opens a browser context, or wraps a page in a GamePage.

    Both halves are needed, because a page arrives by more names than one:
    `new_page` on the browser and `launch_persistent_context` each hand back
    a page with no init script on it, and what they all end in is a GamePage
    built outside the fixture, so that wrapper is the half that catches them.
    """
    if not isinstance(node, ast.Call):
        return False
    if isinstance(node.func, ast.Attribute):
        return node.func.attr == "new_context"
    return isinstance(node.func, ast.Name) and node.func.id == "GamePage"


def opens_its_own_game_page(source: str, name: str = "<sample>") -> list[str]:
    """Every place in this source that builds a game page by hand.

    game_page() in tests/conftest.py is where the clock, the toast record and
    the write guard are installed, so a file that opens its own context for
    the game, or wraps a page of its own in a GamePage, runs with none of the
    three. A context for one of the other pages the battery opens is not this.
    """
    tree = ast.parse(source, filename=name)
    said = _strings(tree, {})
    game = any(GAME_FILE in s for s in said) or any(
        (isinstance(node, ast.Name) and node.id == "GAME_PATH")
        or (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "GamePage"
        )
        for node in ast.walk(tree)
    )
    if not game:
        return []
    return [
        f"{name}:{node.lineno} {ast.unparse(node.func)}"
        for node in ast.walk(tree)
        if _builds_a_page(node)
    ]


# ---- D1 the clock -----------------------------------------------------------


@pytest.mark.parametrize("fixture", FIXTURES)
def test_every_page_fixture_believes_it_is_noon_of_today(
    fixture: str, request: pytest.FixtureRequest
) -> None:
    """One helper for the four fixtures, so one clock for all of them.

    A shard that runs between eleven and midnight unlocks Night owl and its
    toast replaces the one another test is waiting for. The hour is moved and
    the day is kept: the dashboard groups its events by day, and the records a
    test seeds for it are written in Python against the same calendar.
    """
    game: GamePage = request.getfixturevalue(fixture)
    before = date.today()
    game.goto()
    now = game.page.evaluate(
        "() => {const d = new Date();"
        " return [d.getFullYear(), d.getMonth() + 1, d.getDate(), d.getHours(),"
        " window.Date !== (window.__realDate || window.Date)];}"
    )
    after = date.today()
    # The hour on its own proves nothing between noon and one o'clock, which
    # is an hour of every run the fix would be missing from: what is asserted
    # is that the page is answering off a shifted clock at all.
    assert now[4] is True, "the page was never given a clock of its own"
    assert now[3] == NOON, f"the page thinks it is {now[3]} o'clock"
    assert date(now[0], now[1], now[2]) in (before, after), now


def test_a_page_with_no_wrapper_gets_the_same_three_rules(
    chromium: Browser, server: str
) -> None:
    """The three rules hang off the context, not off GamePage.

    A test of one of our own tools is handed a bare Page (tools/media.py takes
    one), and a test that wants a size or a browser the fixtures do not offer
    opens its own. Both take game_context(), so neither has to be taught the
    clock, the record and the write rule a second time.
    """
    # The write the guard has to refuse is aimed at a temporary directory and
    # not at docs/media: a run where the guard is missing is exactly the run
    # that would then overwrite the tracked picture it aimed at.
    outside = Path(tempfile.gettempdir()) / "vibe-map-write-guard-probe.png"
    with game_context(chromium, viewport={"width": 420, "height": 860}) as page:
        page.goto(server + GAME_PATH)
        hour = page.evaluate("() => new Date().getHours()")
        recorded = page.evaluate("() => Array.isArray(window.__toastLog)")
        with pytest.raises(AssertionError, match="outside tests/out"):
            page.screenshot(path=str(outside))
    assert hour == NOON, f"the page thinks it is {hour} o'clock"
    assert recorded, "the page keeps no record of the toasts it raises"


def test_the_shifted_clock_still_runs(game: GamePage) -> None:
    """Shifted, never frozen: the game measures with it.

    Sheet dwell, the speed run achievement and the dashboard's days are all
    read off Date, so a clock that stands still breaks them instead. The
    distance between the page's clock and the runner's is what stays put.
    """
    game.goto()
    game.start("Lotte")
    apart = "() => [Date.now(), Date.now() - performance.timeOrigin"
    apart += " - performance.now()]"
    first = game.page.evaluate(apart)
    game.frames(8)
    second = game.page.evaluate(apart)
    assert second[0] > first[0], "the page's clock stopped"
    assert abs(second[1] - first[1]) < 100, (first, second)


def test_the_clock_does_not_go_back_when_the_page_loads_again(game: GamePage) -> None:
    """One clock for the context, not one per navigation.

    goto() reloads to seed a record and a test may load again itself. A shift
    worked out inside the page re-anchors to the hour on the dot each time, so
    the clock walks backwards across a reload and an interval measured across
    one comes out negative. The anchor is fixed, so the time only runs on.
    """
    game.goto()
    game.start("Lotte")
    game.frames(8)
    before = game.page.evaluate("Date.now()")
    game.goto(state={"name": "Lotte", "doneW": {"campus": [1]}})
    after = game.page.evaluate("Date.now()")
    assert after >= before, f"the page's clock went back {before - after} ms"


def test_the_shifted_clock_answers_a_bare_date_call(game: GamePage) -> None:
    """`Date()` without `new` is a string, the way the real one answers.

    The game only ever says `new Date(`, so nothing breaks on it today. A
    vendored library that stamps a log line with `Date()` would fail under
    test and nowhere else, which is the worst place to learn it.
    """
    game.goto()
    answers = game.page.evaluate(
        "() => [typeof Date(), new Date() instanceof Date, typeof Date.now(),"
        " typeof Date.parse('2020-01-01T00:00:00Z'), typeof Date.UTC(2020, 0, 1),"
        " new window.__realDate(Date()).getHours()]"
    )
    assert answers == ["string", True, "number", "number", "number", NOON]


# ---- D2 the toasts ----------------------------------------------------------


def test_the_toast_record_outlives_the_toast(game: GamePage) -> None:
    """The record is not the screen, which is the whole point of it.

    A toast is removed after five seconds and the next one takes its place, so
    a test that reads `#toast` asks a question whose answer changes while it
    is being answered. Here the page is told to drop the notice on the floor,
    the way the timer would, and the record still knows what was said.
    """
    game.goto(state={"name": "Marsman", "world": "mars", "doneW": {"mars": [1]}})
    game.toast_said("could not be read")
    game.page.evaluate(
        "() => document.querySelectorAll('#toast .tst').forEach(n => n.remove())"
    )
    assert game.page.locator("#toast .tst").count() == 0
    assert any("could not be read" in said for said in game.toasts())
    game.toast_said("could not be read")


def test_the_toast_record_holds_each_notice_once(game: GamePage) -> None:
    """As many entries as the page raised toasts, from the first one on.

    The first toast of a page reaches the observer as two records in one
    batch, the stack and the notice inside it, so a record that notes whatever
    it is handed counts that one twice. The game's own counter is the second
    opinion: a length, an order or an `exactly one` written against a record
    that disagrees with it is wrong from the first toast.
    """
    # An island the game does not build is repaired away and the player is
    # told once; the campus stop earns First light, which may be noticed
    # behind the title screen or after resume, depending on rendering speed.
    game.goto(
        state={
            "name": "Marsman",
            "world": "mars",
            "doneW": {"campus": [1], "mars": [1]},
        }
    )
    game.toast_said("could not be read")
    both = "() => [window.__toasts(), (window.__toastLog || []).length]"
    raised, kept = game.page.evaluate(both)
    assert raised >= 1
    assert kept == raised, f"the record holds {kept} of {raised} toasts"
    assert sum("could not be read" in said for said in game.toasts()) == 1
    game.resume()
    game.toast_said("Achievement: First light")
    raised, kept = game.page.evaluate(both)
    assert raised >= 2, raised
    assert kept == raised, f"the record holds {kept} of {raised} toasts"
    assert sum("Achievement: First light" in said for said in game.toasts()) == 1


def test_a_toast_that_never_comes_says_what_the_page_did_say(
    game: GamePage, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The wait every converted toast test hangs on, when it runs out.

    Reading the screen failed with the toast that was there, which is how the
    clock leak was diagnosed in the first place. A bare timeout on the record
    would have said only that twenty seconds passed.
    """
    game.goto(state={"name": "Marsman", "world": "mars", "doneW": {"mars": [1]}})
    game.toast_said("could not be read")
    monkeypatch.setattr("tests.conftest.WAIT_MS", 1000)
    with pytest.raises(AssertionError) as expired:
        game.toast_said("a toast nobody raises")
    said = str(expired.value)
    assert "a toast nobody raises" in said
    assert "could not be read" in said, said


def test_no_browser_test_reads_a_toast_off_the_screen() -> None:
    """A guard on the leak, not on the one test that had it."""
    found: list[str] = []
    for path in TESTS:
        if path.name in GUARDS or path.name in STILL_READ_THE_SCREEN:
            continue
        found += toast_reads(path.read_text(encoding="utf-8"), path.name)
    assert not found, (
        "a toast expires on a five second timer: ask GamePage.toasts() or "
        f"GamePage.toast_said() what the page said, not the screen. {found}"
    )


# The shapes a test reaches for a toast in. A selector is as often held in a
# name, or named two steps up a chain, or written as an element id inside a
# page script, as passed to the call that finally reads it, so the guard
# cannot decide on what this one call does.
TOAST_READS = [
    'game.page.text_content("#toast .tst")',
    'game.page.locator("#toast .tst").text_content()',
    'game.page.locator("#toast .tst").first.inner_text()',
    'el = game.page.wait_for_selector("#toast .tst")\nsaid = el.text_content()',
    "game.page.evaluate(\"document.querySelector('#toast .tst').textContent\")",
    "game.page.evaluate(\"document.getElementById('toast').textContent\")",
    'game.page.wait_for_function("() => '
    "document.getElementById('toast').textContent.includes('Picked up')\")",
    "game.page.wait_for_selector('#toast .tst:has-text(\"Picked up\")')",
    'SAYS = "#toast .tst"\nsaid = game.page.text_content(SAYS)',
    'SAYS: str = "#toast .tst"\nsaid = game.page.text_content(SAYS)',
    'game.page.locator("#toast .tst", has_text="Picked up").first',
    'game.page.locator("#toast .tst", has_text="Picked up").is_visible()',
    "game.page.is_visible('#toast .tst:has-text(\"Picked up\")')",
    'game.page.text_content(".tst")',
    'game.page.inner_html("#toast")',
    'expect(game.page.locator("#toast")).to_contain_text("Picked up")',
]


@pytest.mark.parametrize("source", TOAST_READS)
def test_the_toast_guard_sees_a_read_whatever_shape_it_takes(source: str) -> None:
    assert toast_reads(source), source


def test_the_toast_guard_leaves_a_question_about_the_stack_alone() -> None:
    """Whether the stack is on the screen is a fair question to ask it.

    tests/test_game_qol_settings.py asks exactly that, of a setting that turns
    toasts off, and nothing it reads expires while it is being read.
    """
    assert toast_reads('assert not game.page.is_visible("#toast")') == []
    geometry = "game.page.evaluate(\"document.getElementById('toast')"
    geometry += '.getBoundingClientRect().height")'
    assert toast_reads(geometry) == []


def test_the_files_that_still_read_the_screen_are_still_exactly_that() -> None:
    """The exceptions are real ones, and the list may only shrink.

    A name added with nothing behind it, and a converted file whose `#toast`
    survives in a comment, both fail here: the same guard decides.
    """
    for name in sorted(STILL_READ_THE_SCREEN):
        source = (ROOT / "tests" / name).read_text(encoding="utf-8")
        assert toast_reads(source, name), (
            f"{name} no longer reads a toast off the screen: take it out of "
            "STILL_READ_THE_SCREEN"
        )


HAND_BUILT = (
    "context = chromium.new_context(**phone_options(profile))\n"
    "page = context.new_page()\n"
    "game = GamePage(page=page, url=server + GAME_PATH)"
)
# The same page with no context of its own: new_page() on the browser, and a
# persistent context, are two more ways to the same page without the clock,
# the record or the write guard.
NO_CONTEXT_AT_ALL = (
    "page = chromium.new_page(**phone_options(profile))\n"
    "game = GamePage(page=page, url=server + GAME_PATH)"
)
ANOTHER_PAGE = (
    "context = chromium.new_context(viewport={'width': 393, 'height': 852})\n"
    "page = context.new_page()\n"
    "page.goto(report.as_uri())"
)


def test_the_page_guard_tells_the_game_from_the_other_pages() -> None:
    """The dashboard report and the syllabus open contexts of their own."""
    assert opens_its_own_game_page(HAND_BUILT)
    assert opens_its_own_game_page(NO_CONTEXT_AT_ALL)
    assert opens_its_own_game_page(ANOTHER_PAGE) == []


def test_a_game_page_comes_from_the_fixture() -> None:
    """The clock, the record and the write guard live in one helper.

    A file that opens its own context gets none of the three, so the two that
    still do are named and the list may only shrink.
    """
    found: list[str] = []
    for path in TESTS:
        if path.name in GUARDS or path.name in HAND_BUILT_PAGES:
            continue
        found += opens_its_own_game_page(path.read_text(encoding="utf-8"), path.name)
    assert not found, (
        "a game page comes from game_page() in tests/conftest.py, which gives "
        f"it the clock, the toast record and the write guard. {found}"
    )


def test_the_files_that_build_their_own_page_still_do() -> None:
    """The other half of the ratchet: a name with nothing behind it fails."""
    for name in sorted(HAND_BUILT_PAGES):
        source = (ROOT / "tests" / name).read_text(encoding="utf-8")
        assert opens_its_own_game_page(source, name), (
            f"{name} takes its page from the fixtures now: take it out of "
            "HAND_BUILT_PAGES"
        )


# ---- D3 what a test writes --------------------------------------------------


def test_a_browser_test_writes_only_under_tests_out() -> None:
    """The rule itself: the path decides, before anything is written."""
    assert out_file("pet_cat.png") == (OUT / "pet_cat.png").resolve()
    assert out_file(OUT / "deep" / "shot.png").is_relative_to(OUT.resolve())
    tracked = ROOT / "docs" / "media" / "pets-game" / "cat.png"
    with pytest.raises(AssertionError, match="outside tests/out"):
        out_file(tracked)
    with pytest.raises(AssertionError, match="outside tests/out"):
        out_file("../../docs/media/hero.png")


def test_the_page_refuses_a_write_outside_tests_out() -> None:
    """And the page holds a test to it at the moment of the write."""

    class Stub:
        """Enough of a page to take a screenshot: it records where it wrote."""

        def __init__(self) -> None:
            self.wrote: list[str] = []

        def screenshot(self, **options: Any) -> bytes:
            self.wrote.append(str(options.get("path", "")))
            return b""

    stub = Stub()
    writes_only_to_out(cast(Page, stub))
    page: Any = stub
    page.screenshot(path=str(OUT / "ok.png"))
    assert stub.wrote == [str((OUT / "ok.png").resolve())]
    with pytest.raises(AssertionError, match="outside tests/out"):
        page.screenshot(path=str(ROOT / "docs" / "media" / "pets-game" / "cat.png"))
    assert len(stub.wrote) == 1, "the refused write went through anyway"


def test_no_test_names_its_own_path_for_a_screenshot() -> None:
    """Where a test writes is an expression in its source: read them all.

    `git status` after the battery would answer the same question too late and
    only for the files git tracks. This asks before anything runs, and it
    names the line.
    """
    found: list[str] = []
    for path in TESTS:
        if path.name in GUARDS:
            continue
        for call in _calls(path, "screenshot"):
            for kw in call.keywords:
                if kw.arg != "path":
                    continue
                names = {n.id for n in ast.walk(kw.value) if isinstance(n, ast.Name)}
                if "OUT" not in names:
                    found.append(
                        f"{path.name}:{call.lineno} path={ast.unparse(kw.value)}"
                    )
    assert not found, (
        "a picture from a test belongs in tests/out: pass a name to "
        f"GamePage.screenshot(), which puts it there. {found}"
    )


# ---- D4 a wait that runs out ------------------------------------------------


def test_a_wait_that_runs_out_names_itself(game: GamePage) -> None:
    """Which wait, and how the page was doing: the two things a log lacks.

    The budget here is small on purpose. It is the wait under test, not a
    sleep standing in for a signal: what is asserted is the sentence a timeout
    writes, which is the only way the next occurrence of the zoom stall on CI
    can be read instead of guessed at.
    """
    game.goto()
    game.start("Lotte")
    with pytest.raises(AssertionError) as expired:
        game.until("false", what="the thing that never happens", budget=1000)
    said = str(expired.value)
    assert "the thing that never happens" in said
    assert "frames while waiting" in said, said


def test_the_zoom_level_and_the_camera_landing_fail_differently(
    game: GamePage, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The two waits of the zoom test, a line apart, no longer read alike."""
    monkeypatch.setattr("tests.test_game_camera.WAIT_MS", 1000)
    game.goto()
    game.start("Lotte")
    with pytest.raises(AssertionError) as expired:
        _zoom_is(game, 0.13)
    assert "the zoom level never reached 0.13" in str(expired.value)


def test_a_picture_that_never_arrives_names_itself_and_the_frames() -> None:
    """The third wait in the zoom loop, the one with no name of its own.

    A capture waits for the compositor, so it is spent in the same currency
    as the landing beside it, and it ran out on CI where the landing did not.
    Playwright says only that its default thirty seconds passed at a line
    inside the helper; what tells a starved runner from a page that stopped
    drawing is the frames, so the helper answers with those.
    """

    class Stalls:
        """A page whose picture never arrives, with a loop that keeps going."""

        def __init__(self) -> None:
            self.drawn = 0
            self.asked: dict[str, Any] = {}
            self.viewport_size = {"width": 412, "height": 915}

        def evaluate(self, *_: Any, **__: Any) -> int:
            self.drawn += 2
            return self.drawn

        def screenshot(self, **options: Any) -> bytes:
            self.asked = options
            raise PageTimeout(f"Page.screenshot: Timeout {SHOT_MS}ms exceeded")

    stalls = Stalls()
    game = GamePage(page=cast(Page, stalls), url="")
    with pytest.raises(AssertionError) as expired:
        game.screenshot("a_picture_that_never_arrives", clip_height=915)
    said = str(expired.value)
    assert "a_picture_that_never_arrives" in said, said
    assert "frames while waiting" in said, said
    assert "412 by 915 CSS pixels" in said, said
    assert stalls.asked["timeout"] == SHOT_MS, stalls.asked


def test_a_picture_from_a_phone_is_one_image_pixel_per_css_pixel(
    game_android: GamePage,
) -> None:
    """The cheaper half, in the currency the capture is paid in.

    The Pixel 7 profile draws 2.625 device pixels to the CSS pixel, so a full
    height picture was 2.6 megapixels of a scene no test measures. Nothing
    reads these pictures but a person looking at them, and the two that are
    read as pixels are taken at a desktop profile, where this changes nothing.
    """
    from PIL import Image

    game_android.goto()
    shot = game_android.screenshot("harness_phone_picture", clip_height=300)
    with Image.open(shot) as picture:
        assert picture.size == (412, 300), picture.size
