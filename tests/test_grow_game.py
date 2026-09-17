"""Grow mode in the game: the graph starts with the hubs and grows with play."""

from __future__ import annotations

from tests.conftest import GamePage


def test_graph_grows_as_you_play(game: GamePage) -> None:
    game.page.goto(game.url + "?vault=grow")
    game.page.wait_for_function("typeof window.__S === 'function'")
    game.start()
    page = game.page
    page.click("#hud button:has-text('Vault')")
    page.wait_for_timeout(1200)
    count = page.text_content("#vcount") or ""
    assert "of" in count and "unlocked" in count
    start_n = int(count.split(" of ")[0].strip())
    total = int(count.split(" of ")[1].split(" ")[0])
    assert 5 <= start_n < total // 3
    # a locked link renders dimmed and does not open
    page.evaluate("openNote('Tonight')")
    page.wait_for_timeout(300)
    assert page.locator("#vnote .wl.locked").count() >= 1
    page.click("#vtop button:has-text('Back to campus')")
    # inspect the dock: its notes unlock
    page.evaluate("openArtifact('dock')")
    page.wait_for_timeout(300)
    page.click("#sheet .x")
    page.click("#hud button:has-text('Vault')")
    page.wait_for_timeout(1200)
    after = int((page.text_content("#vcount") or "0 of").split(" of ")[0].strip())
    assert after > start_n
    page.evaluate("openNote('Docker and containers')")
    page.wait_for_timeout(300)
    assert "Docker" in (page.text_content("#vnote h1") or "")
    assert not game.errors, game.errors
