"""The onboarding screen, driven headlessly by Textual's pilot."""

from __future__ import annotations

import asyncio
import threading
from pathlib import Path

from textual.widgets import Button, DataTable, Input

from vibemap.tui import Checks, Launch, Map, VibeApp, Welcome


def test_onboarding_screens_walk_through(tmp_path: Path) -> None:
    async def drive() -> str | None:
        app = VibeApp(
            config_path=tmp_path / "vibe.toml", state_path=tmp_path / "state.json"
        )
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
            buttons = app.screen.query(Button)
            assert any(b.id == "act-yolo" for b in buttons)
            await pilot.click("#act-map")
            await pilot.pause()
            assert isinstance(app.screen, Map)
            assert len(app.screen.query(".maprow")) == 4
            await pilot.click("#back")
            await pilot.pause()
            assert isinstance(app.screen, Launch)
            await pilot.click("#act-quit")
            await pilot.pause()
        return app.return_value

    # The Playwright fixtures leave an event loop on the main thread during the
    # full battery, so the Textual pilot runs on its own thread with its own loop.
    result: dict[str, str | None] = {}
    thread = threading.Thread(target=lambda: result.update(value=asyncio.run(drive())))
    thread.start()
    thread.join(timeout=120)
    assert result.get("value") == "quit"
    assert (tmp_path / "vibe.toml").exists() and (tmp_path / "state.json").exists()
