"""Echo lessons point to their real primary place through the public UI."""

from __future__ import annotations

import pytest
from playwright.sync_api import expect

from tests.conftest import GamePage


@pytest.mark.parametrize(
    ("echo_place", "topic", "primary_place"),
    [
        ("Hangzhou, China", "llm", "The internet"),
        ("A data centre", "cloud", "Amazon, Seattle"),
    ],
)
def test_echo_jump_uses_primary_and_keeps_learning(
    game_desktop: GamePage, echo_place: str, topic: str, primary_place: str
) -> None:
    game = game_desktop
    game.goto(
        state={
            "name": "Lotte",
            "topics": ["unix"],
            "settings": {"experience": "galaxy", "motion": "off"},
        }
    )
    game.resume()
    game.page.get_by_role("button", name="Chart", exact=True).click()
    game.page.get_by_role("button", name=f"Land at {echo_place}").click()
    row = game.page.locator(f'#galaxy-list [data-galaxy-topic="{topic}"]').locator(
        "xpath=ancestor::*[contains(@class, 'galaxy-place')]"
    )
    expect(row).to_contain_text("Echo")
    learn = row.get_by_role("button", name=f"Learn {topic}", exact=False)
    expect(learn).to_be_visible()
    jump = row.get_by_role("button", name=f"Jump to primary for {topic}", exact=False)
    expect(jump).to_be_visible()
    assert jump.get_attribute("tabindex") == "0"
    learn.focus()
    game.page.keyboard.press("Tab")
    expect(jump).to_be_focused()
    game.page.keyboard.press("Shift+Tab")
    expect(learn).to_be_focused()
    learn.press("Enter")
    expect(game.page.locator("#vault")).to_have_class("on")
    game.page.keyboard.press("Escape")
    expect(learn).to_be_focused()
    before = game.state()
    jump.focus()
    jump.press("Enter")
    expect(game.page.locator("#galaxy-title")).to_have_text(primary_place)
    expect(
        game.page.locator(f'#galaxy-list [data-galaxy-topic="{topic}"]')
    ).to_be_visible()
    assert game.state().get("topics") == before.get("topics")
    assert game.state().get("done") == before.get("done")
    game.assert_clean()


def test_echo_jump_is_available_in_list_only_phone_view(game_android: GamePage) -> None:
    game = game_android
    game.goto(state={"name": "Lotte", "settings": {"experience": "galaxy"}})
    game.resume()
    game.page.set_viewport_size({"width": 390, "height": 450})
    game.page.evaluate("openSettings()")
    game.page.locator("#set-text").select_option("larger")
    game.page.locator("#sheet > .x").click()
    game.page.get_by_role("button", name="Chart", exact=True).click()
    game.page.get_by_role("button", name="Land at Hangzhou, China").tap()
    row = game.page.locator('#galaxy-list [data-galaxy-topic="llm"]').locator(
        "xpath=ancestor::*[contains(@class, 'galaxy-place')]"
    )
    learn = row.get_by_role("button", name="Learn", exact=False)
    jump = row.get_by_role("button", name="Jump to primary", exact=False)
    for button in (learn, jump):
        width, height = button.evaluate(
            "el => { const r = el.getBoundingClientRect(); return [r.width, r.height] }"
        )
        assert width >= 44 and height >= 44
    row.scroll_into_view_if_needed()
    game.screenshot("galaxy_echo_phone")
    jump.tap()
    expect(game.page.locator("#galaxy-title")).to_have_text("The internet")
    expect(game.page.locator("#galaxy-flight")).not_to_be_visible()
    game.assert_clean()
