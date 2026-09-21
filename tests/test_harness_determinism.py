"""What a browser test may depend on: not the hour, not the screen, not a file.

Three leaks made a green run depend on when and where it ran (issue 148): the
runner's clock unlocked an achievement whose toast took another test's place,
a toast was read off the screen after the five second timer had taken it away,
and the battery rendered into `docs/media`, which is tracked. Each finding has
a test here, and each of them fails without its fix.

The guards read the test sources, because that is where the leak is written
down: what a test passes to a screenshot is the path it will write, and a
selector that reads `#toast` is a test asking the screen instead of the page.
"""

from __future__ import annotations

import ast
from datetime import date
from pathlib import Path
from typing import Any, cast

import pytest
from playwright.sync_api import Page

from tests.conftest import NOON, OUT, ROOT, GamePage, out_file, writes_only_to_out
from tests.test_game_camera import _zoom_is

FIXTURES = ["game", "game_desktop", "game_android", "game_webkit_iphone"]
TESTS = sorted(p for p in (ROOT / "tests").glob("test_*.py"))
# The two files the rule is written in: conftest.py is the one helper that
# owns it, this file is where the helper is put to the test.
GUARDS = {"conftest.py", "test_harness_determinism.py"}
# Two files still read a toast off the screen. They are not among the files
# this order may touch, so converting them to GamePage.toasts() is a follow-up
# of issue 148; until then they are named here and the list may only shrink.
STILL_READ_THE_SCREEN = {"test_game_bottles.py", "test_game_ui.py"}
READS_TEXT = {"text_content", "inner_text", "all_text_contents", "text_contents"}


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
        " return [d.getFullYear(), d.getMonth() + 1, d.getDate(), d.getHours()];}"
    )
    after = date.today()
    assert now[3] == NOON, f"the page thinks it is {now[3]} o'clock"
    assert date(now[0], now[1], now[2]) in (before, after), now


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
    assert game.page.text_content("#toast") == ""
    assert any("could not be read" in said for said in game.toasts())
    game.toast_said("could not be read")


def test_no_browser_test_reads_a_toast_off_the_screen() -> None:
    """A guard on the leak, not on the one test that had it."""
    found: list[str] = []
    for path in TESTS:
        if path.name in GUARDS or path.name in STILL_READ_THE_SCREEN:
            continue
        for node in ast.walk(_tree(path)):
            if not isinstance(node, ast.Call) or not isinstance(
                node.func, ast.Attribute
            ):
                continue
            selectors = [
                a.value
                for a in node.args
                if isinstance(a, ast.Constant) and isinstance(a.value, str)
            ]
            if not any(s.startswith("#toast") for s in selectors):
                continue
            reads = node.func.attr in READS_TEXT or (
                node.func.attr == "locator"
                and any(kw.arg == "has_text" for kw in node.keywords)
            )
            if reads:
                found.append(f"{path.name}:{node.lineno} {ast.unparse(node)}")
    assert not found, (
        "a toast expires on a five second timer: ask GamePage.toasts() or "
        f"GamePage.toast_said() what the page said, not the screen. {found}"
    )


def test_the_list_of_files_that_still_read_the_screen_only_shrinks() -> None:
    """The two exceptions are real ones, and each is still exactly that."""
    for name in STILL_READ_THE_SCREEN:
        source = (ROOT / "tests" / name).read_text(encoding="utf-8")
        assert "#toast" in source, f"{name} no longer reads a toast: drop it here"


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
