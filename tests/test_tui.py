"""The onboarding screen, driven headlessly by Textual's pilot."""

from __future__ import annotations

import asyncio
import sys
import threading
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

from rich.text import Text
from textual.containers import VerticalScroll
from textual.widgets import Button, DataTable, Input, Static

from vibemap import dotfiles, toolbelt
from vibemap.config import Config
from vibemap.palette import plain
from vibemap.state import PLACEHOLDER, CheckRecord, State
from vibemap.themes import THEMES
from vibemap.tui import Checks, Dotfiles, Launch, Map, VibeApp, Welcome

SMALL = (80, 24)
ST = State(name="Lotte")


def drive(coro: Callable[[], Awaitable[Any]]) -> Any:
    """Run one pilot session and hand back what it returned.

    The Playwright fixtures leave an event loop on the main thread during the
    full battery, so the Textual pilot runs on its own thread with its own loop.
    """
    box: dict[str, Any] = {}

    def go() -> None:
        try:
            box["value"] = asyncio.run(coro())
        except BaseException as exc:  # re-raised on the calling thread
            box["error"] = exc

    thread = threading.Thread(target=go)
    thread.start()
    thread.join(timeout=300)
    if "error" in box:
        raise box["error"]
    assert "value" in box, "the pilot did not finish"
    return box["value"]


async def press(pilot: Any, selector: str) -> None:
    """Click a real button, scrolling it into view first, as a user does."""
    pilot.app.screen.query_one(selector).scroll_visible(animate=False)
    await pilot.pause()
    await pilot.click(selector)
    await pilot.pause()


def app_for(
    tmp_path: Path, *, cfg: Config | None = None, state: State | None = None
) -> VibeApp:
    """The app a camp of its own starts, with whatever it has saved so far."""
    config_path, state_path = tmp_path / "camp.toml", tmp_path / "state.json"
    if cfg is not None:
        cfg.save(config_path)
    if state is not None:
        state.save(state_path)
    return VibeApp(config_path=config_path, state_path=state_path)


def test_onboarding_screens_walk_through(tmp_path: Path) -> None:
    async def go() -> str | None:
        app = app_for(tmp_path)
        async with app.run_test(size=(120, 50)) as pilot:
            await pilot.pause()
            assert isinstance(app.screen, Welcome)
            app.screen.query_one("#name", Input).value = "Lotte"
            await pilot.click("#next")
            await pilot.pause()
            assert isinstance(app.screen, Checks)
            table = app.screen.query_one("#tools", DataTable)
            assert table.row_count >= 20
            await pilot.click("#next")
            await pilot.pause()
            assert isinstance(app.screen, Launch)
            # A learner who has not done the permissions lessons cannot skip them.
            assert app.screen.query_one("#act-yolo", Button).disabled
            await pilot.click("#act-map")
            await pilot.pause()
            assert isinstance(app.screen, Map)
            assert len(app.screen.query(".maprow")) == 4
            await pilot.click("#back")
            await pilot.pause()
            assert isinstance(app.screen, Launch)
            await pilot.click("#act-dotfiles")
            await pilot.pause()
            assert isinstance(app.screen, Dotfiles)
            assert len(app.screen.query("Button")) >= 7
            await pilot.click("#back")
            await pilot.pause()
            assert isinstance(app.screen, Launch)
            await pilot.click("#act-quit")
            await pilot.pause()
        return app.return_value

    assert drive(go) == "quit"
    assert (tmp_path / "camp.toml").exists() and (tmp_path / "state.json").exists()


def test_the_launcher_list_scrolls_on_a_small_terminal(tmp_path: Path) -> None:
    async def go() -> None:
        app = app_for(tmp_path, state=State(name="Lotte"))
        async with app.run_test(size=SMALL) as pilot:
            await pilot.pause()
            await press(pilot, "#next")
            await press(pilot, "#next")
            assert isinstance(app.screen, Launch)
            box = app.screen.query_one("#launch")
            assert isinstance(box, VerticalScroll)
            quit_button = app.screen.query_one("#act-quit", Button)
            assert not app.screen.region.contains_region(quit_button.region)
            for _ in range(40):
                if app.focused is quit_button:
                    break
                await pilot.press("tab")
            await pilot.pause()
            assert app.focused is quit_button
            # The focused button is on screen, and the list moved to put it there.
            assert box.scroll_offset.y > 0
            assert app.screen.region.contains_region(quit_button.region)

    drive(go)


def test_the_toolbelt_shows_its_rows_on_a_small_terminal(tmp_path: Path) -> None:
    async def go() -> None:
        app = app_for(tmp_path, state=State(name="Lotte"))
        async with app.run_test(size=SMALL) as pilot:
            await pilot.pause()
            await press(pilot, "#next")
            assert isinstance(app.screen, Checks)
            table = app.screen.query_one("#tools", DataTable)
            assert table.row_count >= 20
            # Two border rows and the header row come off the visible height.
            assert table.size.height - 3 >= 5, "no tool rows fit at 80x24"
            assert app.screen.query_one("#log").size.height > 0

    drive(go)


def test_a_launcher_hint_wraps_instead_of_running_off_the_side(
    tmp_path: Path, monkeypatch
) -> None:
    from vibemap import tui

    # A camp has no engine, so the tests row carries the longest hint there is.
    monkeypatch.setattr(tui, "ROOT", tmp_path)

    async def go() -> None:
        app = app_for(tmp_path, state=State(name="Lotte"))
        async with app.run_test(size=SMALL) as pilot:
            await pilot.pause()
            await press(pilot, "#next")
            await press(pilot, "#next")
            row = app.screen.query_one("#act-tests", Button).parent
            assert row is not None
            hint = row.query_one(".hint", Static)
            assert hint.region.right <= SMALL[0], "the hint ran off the side"
            assert hint.size.height >= 2, "the hint had one line for 61 characters"

    drive(go)


def test_a_theme_of_your_own_survives_continue(tmp_path: Path) -> None:
    from vibemap.tui import theme_options

    cfg = Config()
    cfg.theme.preset = "my-custom"

    async def go() -> None:
        app = app_for(tmp_path, cfg=cfg, state=State(name="Lotte"))
        async with app.run_test(size=(120, 50)) as pilot:
            await pilot.pause()
            await press(pilot, "#next")
            assert isinstance(app.screen, Checks)

    drive(go)
    assert 'preset = "my-custom"' in (tmp_path / "camp.toml").read_text()
    assert [v for _, v in theme_options("my-custom")][-1] == "my-custom"
    assert all(v in THEMES for _, v in theme_options("studio"))


def test_an_empty_name_is_refused_rather_than_stored(tmp_path: Path) -> None:
    async def go() -> None:
        app = app_for(tmp_path)
        async with app.run_test(size=(120, 50)) as pilot:
            await pilot.pause()
            await pilot.click("#next")
            await pilot.pause()
            assert isinstance(app.screen, Welcome), "the placeholder went through"
            said = str(app.screen.query_one("#nameproblem", Static).content)
            assert "Type your name first" in said
            # Enter in the field is Continue, once there is something to submit.
            app.screen.query_one("#name", Input).value = "Lotte"
            await pilot.press("enter")
            await pilot.pause()
            assert isinstance(app.screen, Checks)

    drive(go)
    saved = (tmp_path / "camp.toml").read_text()
    assert PLACEHOLDER not in saved and 'name = "Lotte"' in saved


def test_the_map_grid_speaks_the_language_of_vibe_status(tmp_path: Path) -> None:
    state = State(name="Lotte")
    state.done_w["campus"] = [1, 2]
    state.checks["campus:1"] = CheckRecord(ok=True)

    async def go() -> str:
        app = app_for(tmp_path, state=state)
        async with app.run_test(size=(120, 50)) as pilot:
            await pilot.pause()
            await press(pilot, "#next")
            await press(pilot, "#next")
            await press(pilot, "#act-map")
            assert isinstance(app.screen, Map)
            markup = str(app.screen.query(".maprow").first(Static).content)
            return Text.from_markup(markup).plain

    row = drive(go)
    # x checked, i claimed but not verified, > the next stop, . still to do.
    assert "x i > . . . . ." in row, row


def test_a_dotfiles_row_says_installed_after_the_install(
    tmp_path: Path, monkeypatch
) -> None:
    from vibemap import tui

    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setattr(dotfiles, "default_home", lambda: home)
    monkeypatch.setattr(tui, "ROOT", tmp_path)

    async def go() -> tuple[str, str]:
        app = app_for(tmp_path, state=State(name="Lotte"))
        async with app.run_test(size=(120, 50)) as pilot:
            await pilot.pause()
            await press(pilot, "#next")
            await press(pilot, "#next")
            await press(pilot, "#act-dotfiles")
            assert isinstance(app.screen, Dotfiles)
            before = str(app.screen.query_one("#dothint-zsh", Static).content)
            await press(pilot, "#dot-zsh")
            hint = app.screen.query_one("#dothint-zsh", Static)
            button = app.screen.query_one("#dot-zsh", Button)
            assert button.variant == "success"
            return before, str(hint.content)

    before, after = drive(go)
    assert "not yet" in before and "not yet" not in after
    assert after.endswith("installed")
    assert (home / ".zshrc").exists()


def test_the_launchers_run_what_their_hints_say(tmp_path: Path, monkeypatch) -> None:
    from vibemap import tui

    cfg = Config()
    cfg.vault.path = "notes"
    ran: dict[str, Any] = {}

    class FakeApp:
        def __init__(self, **kwargs: Any) -> None:
            self.cfg = cfg

        def run(self) -> str:
            return ran["choice"]

    monkeypatch.setattr(tui, "VibeApp", FakeApp)
    monkeypatch.setattr(tui, "ROOT", tmp_path)
    monkeypatch.setattr(tui.os, "execvp", lambda f, a: ran.update(argv=[f, *a[1:]]))
    monkeypatch.setattr(tui.subprocess, "run", lambda a, **k: ran.update(argv=a))

    ran["choice"] = "status"
    tui.run()
    # `uv run --no-sync` warns in every camp; this interpreter has the CLI.
    assert ran["argv"] == [sys.executable, "-m", "vibemap.cli", "status"]
    assert "vibe status" in tui.ACTIONS["status"][1]

    ran["choice"] = "obsidian"
    tui.run()
    assert ran["argv"] == ["open", "-a", "Obsidian", str(tmp_path / "notes")]


def test_a_version_string_arrives_without_escape_codes() -> None:
    # btop writes its version in bold; a table cell and NO_COLOR take neither.
    loud = toolbelt.Tool(
        "loud", "Loud", "prints escapes", "python3", "install", "https://x.test",
        "core", version_args=("-c", "print('\\x1b[1m1.4.7\\x1b[0m')"),
    )  # fmt: skip
    assert loud.version() == "1.4.7"
    assert plain("btop version: \x1b[1m1.4.7\x1b[0m") == "btop version: 1.4.7"


def test_launchers_grey_out_what_a_camp_cannot_run(tmp_path: Path, monkeypatch) -> None:
    from vibemap import tui

    rows = {key: (hint, disabled) for key, _, hint, disabled in tui.launchers(ST)}
    assert rows["tests"][1] is False  # the product has tools/build.py
    assert "hosted" in rows["play"][0] and "build" not in rows["news"][0]
    monkeypatch.setattr(tui, "ROOT", tmp_path)
    rows = {key: (hint, disabled) for key, _, hint, disabled in tui.launchers(ST)}
    assert rows["tests"][1] is True
    assert rows["tests"][0] == tui.NO_ENGINE
    assert rows["play"][1] is False and rows["news"][1] is False


def test_yolo_mode_waits_for_the_permissions_lessons() -> None:
    from vibemap import tui

    def yolo(st: State) -> tuple[str, bool]:
        rows = {key: (hint, off) for key, _, hint, off in tui.launchers(st)}
        return rows["yolo"]

    st = State(name="Lotte")
    hint, off = yolo(st)
    assert off, "a beginner was offered claude --dangerously-skip-permissions"
    assert "skips every permission prompt" in hint
    assert "Hooks as gates" in hint and "Claude Code, the power settings" in hint
    st.mark_done("desert", 4)
    assert yolo(st)[1], "one of the two permissions lessons is not enough"
    st.mark_done("prod", 5)
    assert yolo(st) == ("claude --dangerously-skip-permissions", False)


def test_the_progress_line_carries_stops_mentors_and_artifacts() -> None:
    from vibemap import campaign
    from vibemap.state import State
    from vibemap.tui import progress_line

    # Every denominator comes from the campaign, so a camp that adds a stop,
    # a mentor or an artifact is counted against what it really has.
    stops = campaign.total_stops()
    people = len(campaign.mentors())
    built = len(campaign.artifacts())
    st = State(name="Lotte")
    assert progress_line(st) == (
        f"0/{stops} stops, 0/{people} mentors verified, "
        f"0/{built} artifacts built for real"
    )
    st.done_w["campus"] = [1, 2]
    st.mentors.append("torvalds")
    st.artifacts_built.extend(["dock", "crane"])
    line = progress_line(st)
    assert f"2/{stops} stops" in line and f"1/{people} mentors verified" in line
    assert f"2/{built} artifacts built for real" in line
