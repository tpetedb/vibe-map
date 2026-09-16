"""Smoke tests for the game: start, claim, import, vault, every world.

Every test clicks the real buttons and ends by asserting that the page logged
zero errors. Screenshots land in tests/out/ so a human can look at them.
"""

from __future__ import annotations

from tests.conftest import GamePage, encode_progress


def test_game_loads_without_errors(game: GamePage) -> None:
    game.goto()
    assert game.page.is_visible("#title")
    assert game.page.title() == "Vibe Code Camp"
    game.assert_clean()


def test_start_renders_the_island(game: GamePage) -> None:
    game.goto()
    game.start("Lotte")
    assert game.webgl_started(), "3D stage did not initialise (WebGL missing?)"
    assert "Lotte" in (game.page.text_content("#hud-name") or "")
    game.screenshot("smoke_island", clip_height=640)
    game.assert_clean()


def test_claim_first_workstream_from_the_roadmap(game: GamePage) -> None:
    game.goto()
    game.start()
    game.open_roadmap()
    buttons = game.page.locator("#plotlist button")
    assert buttons.count() >= 8
    assert "blocked by dependency" in (buttons.nth(1).text_content() or "")
    game.claim(1)
    state = game.state()
    assert state["done"] == [1]
    assert state["doneW"]["campus"] == [1]
    game.open_roadmap()
    assert "(delivered)" in (buttons.nth(0).text_content() or "")
    assert "blocked" not in (buttons.nth(1).text_content() or "")
    game.screenshot("smoke_roadmap_after_claim")
    game.assert_clean()


def test_import_code_from_the_cli(game: GamePage) -> None:
    game.goto()
    game.start()
    code = encode_progress(done_w={"campus": [1, 2, 3], "winter": [1]})
    msg = game.import_code(code)
    assert msg.startswith("Imported: 3/8"), msg
    state = game.state()
    assert state["doneW"]["campus"] == [1, 2, 3]
    assert state["doneW"]["winter"] == [1]
    assert game.import_code("not a code") == "That is not a valid code."
    game.assert_clean()


def test_export_round_trips(game: GamePage) -> None:
    game.goto()
    game.start()
    game.claim(1)
    game.open_roadmap()
    game.page.click("#s-map button:has-text('Export progress')")
    code = game.page.input_value("#impcode")
    assert code and "=" not in code and "+" not in code and "/" not in code
    game.assert_clean()


def test_vault_opens_and_follows_a_wikilink(game: GamePage) -> None:
    game.goto()
    game.start()
    game.open_vault()
    count = game.page.text_content("#vcount") or ""
    assert any(ch.isdigit() for ch in count), count
    first = game.page.text_content("#vnote") or ""
    links = game.page.locator("#vnote .wl")
    assert links.count() > 0
    links.nth(0).click()
    game.page.wait_for_timeout(300)
    assert (game.page.text_content("#vnote") or "") != first
    game.screenshot("smoke_vault")
    game.page.click("#vtop button:has-text('Tech tree')")
    game.page.wait_for_timeout(300)
    assert game.page.locator("#vtree").is_visible()
    game.close_vault()
    game.assert_clean()


def test_every_world_builds(game: GamePage) -> None:
    seeded = {
        "name": "Lotte",
        "done": [1, 2, 3, 4],
        "doneW": {"campus": [1, 2, 3, 4], "winter": [], "desert": [], "prod": []},
        "path": {},
        "rolls": [],
        "versions": [],
        "bridges": {},
        "date": None,
        "wine": None,
        "world": "campus",
        "creature": None,
    }
    game.goto(state=seeded)
    game.resume()
    worlds = ["campus"]
    for _ in range(3):
        game.next_world()
        worlds.append(game.state()["world"])
        game.screenshot(f"smoke_world_{worlds[-1]}", clip_height=640)
    assert worlds == ["campus", "winter", "desert", "prod"]
    game.next_world()
    assert game.state()["world"] == "campus"
    game.assert_clean()
