"""Play every path: four islands, thirty-two stops, twelve mentors, the finale.

Slow (about a minute) and the strongest guard the game has: every roadmap
button, every claim, every mentor screen and the finale run through the real
click paths with zero page errors, and the exported code imports cleanly
into the CLI's state model.
"""

from __future__ import annotations

import pytest
from playwright.sync_api import Browser

from tests.conftest import GAME_PATH
from tools.play import play_everything
from vibemap.state import State


@pytest.mark.integration
def test_every_path_plays_without_errors(chromium: Browser, server: str) -> None:
    result = play_everything(chromium, server + GAME_PATH, name="Lotte")
    assert result["errors"] == [], result["errors"]
    assert all(sorted(v) == list(range(1, 9)) for v in result["done"].values())
    assert result["mentors"] == 12 and len(result["path"]) == 12
    assert result["notes"] >= 100 and result["links"] >= 300
    assert "go-live" in result["finale"]
    state = State(name="x")
    payload = state.merge_code(result["code"])
    assert payload["v"] == 2
    assert state.total_done() == 32
    assert sum(1 for v in state.path.values() if v == "deep") >= 8
