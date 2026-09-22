"""The Galaxy is playable through its scene and its accessible list twin."""

from __future__ import annotations

from tests.conftest import GamePage


def _open(game: GamePage) -> None:
    game.goto(
        state={
            "name": "Lotte",
            "topics": ["shell-basics"],
            "settings": {"experience": "galaxy", "motion": "off"},
        }
    )
    game.resume()
    game.page.wait_for_function("document.body.dataset.experience === 'galaxy'")


def test_galaxy_journey_globe_and_dome_share_one_listing(game: GamePage) -> None:
    _open(game)
    rows = game.page.evaluate("window.__experience().listing()")
    assert rows and {row["state"] for row in rows} >= {"next", "ahead"}
    assert game.page.locator("#galaxy-list .galaxy-place").count() == len(rows)
    assert game.page.locator("#galaxy-list").get_by_text("NEXT", exact=False).count()
    assert game.page.locator('#galaxy-list [aria-current="step"]').count() == 1
    assert all(row["year"] and row["placeTitle"] for row in rows)
    first_place = game.page.locator("[data-galaxy-place]").first
    first_place.focus()
    assert game.page.evaluate(
        "window.__scene().children.some(item => item.geometry?.type === 'TorusGeometry')"
    )
    first_place.blur()
    assert not game.page.evaluate(
        "window.__scene().children.some(item => item.geometry?.type === 'TorusGeometry')"
    )

    for view in ("journey", "globe", "dome"):
        game.page.get_by_role("button", name=view.title(), exact=True).click()
        assert (
            game.page.locator(f'[data-galaxy-view="{view}"]').get_attribute("class")
            == "on"
        )
    first_place.click()
    assert game.page.locator('[data-galaxy-view="dome"]').get_attribute("class") == "on"
    assert game.page.locator("#galaxy-title").inner_text() == rows[0]["placeTitle"]
    game.screenshot("galaxy_desktop_dome", clip_height=760)
    game.assert_clean()


def test_galaxy_phone_targets_and_experience_switch(
    game_webkit_iphone: GamePage,
) -> None:
    game = game_webkit_iphone
    _open(game)
    sizes = game.page.locator("#galaxy-ui button").evaluate_all(
        "buttons => buttons.map(b => { const r=b.getBoundingClientRect(); "
        "return [r.width,r.height] })"
    )
    assert sizes and all(width >= 44 and height >= 44 for width, height in sizes), sizes

    game.page.evaluate("openSettings()")
    game.page.wait_for_function("document.activeElement.classList.contains('x')")
    choice = game.page.locator("#set-experience")
    choice.focus()
    choice.select_option("islands")
    game.page.wait_for_function("document.body.dataset.experience === 'islands'")
    assert game.page.locator("#sheet").get_attribute("class") == "on"
    game.page.wait_for_function("document.activeElement.id === 'set-experience'")
    assert game.page.evaluate("document.activeElement.id") == "set-experience"
    assert game.page.locator("#copysay").inner_text() == "Islands experience shown"
    game.assert_clean()
