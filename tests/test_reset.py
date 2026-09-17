"""Reset progress: two clicks, or ?reset in the URL, back to the roadmap start."""

from __future__ import annotations

from tests.conftest import GamePage

DONE = {"campus": [1, 2, 3], "winter": [], "desert": [], "prod": []}


def test_reset_button_needs_two_clicks_and_keeps_the_name(game: GamePage) -> None:
    game.goto(state={"name": "Tom", "doneW": DONE, "path": {}})
    game.resume()
    page = game.page
    page.click("#hud button:has-text('Roadmap')")
    page.wait_for_timeout(500)
    page.click("#s-map button:has-text('Reset progress')")
    assert page.evaluate("window.__S().doneW.campus") == [1, 2, 3]
    assert "Really" in (page.text_content("#s-map button.danger") or "")
    page.click("#s-map button.danger")
    page.wait_for_function("typeof window.__S === 'function'")
    page.wait_for_timeout(800)
    st = page.evaluate("window.__S()")
    assert st["doneW"]["campus"] == [] and st["artifacts"] == [] and st["name"] == "Tom"
    assert page.is_visible("#title")
    assert not game.errors, game.errors


def test_reset_query_parameter_wipes_and_cleans_the_url(game: GamePage) -> None:
    """?reset has to run after load(), or it saves the defaults over the record."""
    game.goto(
        state={
            "name": "Tom",
            "look": "frank",
            "mode": "full",
            "doneW": DONE,
            "path": {},
            "settings": {"difficulty": "hard"},
        }
    )
    game.page.goto(game.url + "?reset")
    game.page.wait_for_function("typeof window.__S === 'function'")
    game.page.wait_for_timeout(800)
    st = game.page.evaluate("window.__S()")
    assert st["doneW"]["campus"] == []
    assert st["name"] == "Tom" and st["look"] == "frank" and st["mode"] == "full"
    assert st["settings"]["difficulty"] == "hard"
    assert "reset" not in game.page.url
    assert game.errors == []


def test_reset_keeps_the_chosen_look_and_mode(game: GamePage) -> None:
    game.goto(state={"name": "Frank", "look": "frank", "mode": "full", "doneW": DONE})
    game.resume()
    page = game.page
    page.click("#hud button:has-text('Roadmap')")
    page.wait_for_timeout(500)
    page.click("#s-map button:has-text('Reset progress')")
    page.click("#s-map button.danger")
    page.wait_for_function("typeof window.__S === 'function'")
    s = game.state()
    assert s["look"] == "frank" and s["mode"] == "full" and s["name"] == "Frank"
    assert s["doneW"]["campus"] == []
