"""The onboarding screen, driven headlessly by Textual's pilot."""

from __future__ import annotations

import asyncio
from pathlib import Path

from textual.widgets import Button, DataTable, Input

from grimoire.tui import Checks, GrimoireApp, Launch, Welcome


def test_onboarding_screens_walk_through(tmp_path: Path) -> None:
    async def drive() -> str | None:
        app = GrimoireApp(
            config_path=tmp_path / "grimoire.toml", state_path=tmp_path / "state.json"
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
            await pilot.click("#act-quit")
            await pilot.pause()
        return app.return_value

    assert asyncio.run(drive()) == "quit"
    assert (tmp_path / "grimoire.toml").exists() and (tmp_path / "state.json").exists()
