"""Echo lessons point to their real primary place through the public UI."""

from __future__ import annotations

import pytest
from playwright.sync_api import expect

from tests.conftest import GamePage


@pytest.mark.parametrize(
    ("echo_place", "topic", "primary_place", "topic_name", "primary_history"),
    [
        ("Hangzhou, China", "llm", "The internet", "LLM versus harness", "Transformer"),
        ("A data centre", "cloud", "Amazon, Seattle", "Cloud and servers", "Amazon"),
    ],
)
def test_echo_jump_uses_primary_and_keeps_learning(
    game_desktop: GamePage,
    echo_place: str,
    topic: str,
    primary_place: str,
    topic_name: str,
    primary_history: str,
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
    expect(game.page.locator("#galaxy-check")).to_contain_text(f"Finish {topic_name}")
    expect(game.page.locator("#galaxy-context")).to_contain_text(primary_history)
    expect(
        game.page.locator(f'#galaxy-list [data-galaxy-topic="{topic}"]')
    ).to_be_focused()
    assert game.state().get("topics") == before.get("topics")
    assert game.state().get("done") == before.get("done")
    game.assert_clean()


def test_only_current_echo_action_group_is_in_tab_order(game_desktop: GamePage) -> None:
    game = game_desktop
    game.goto(
        state={"name": "Lotte", "settings": {"experience": "galaxy", "motion": "off"}}
    )
    game.resume()
    game.page.get_by_role("button", name="Chart", exact=True).click()
    game.page.get_by_role("button", name="Land at Hangzhou, China").click()
    # Current data has one echo at this place. Clone its row to exercise the
    # list's focus policy when a second showcased origin appears.
    game.page.locator("#galaxy-list .galaxy-place:has([data-galaxy-jump])").evaluate(
        "row => row.after(row.cloneNode(true))"
    )
    jumps = game.page.locator("#galaxy-list [data-galaxy-jump]")
    expect(jumps).to_have_count(2)
    learns = game.page.locator("#galaxy-list [data-galaxy-topic]")
    first, second = learns.nth(0), learns.nth(1)
    first.focus()
    assert first.get_attribute("tabindex") == "0"
    assert jumps.nth(0).get_attribute("tabindex") == "0"
    assert second.get_attribute("tabindex") == "-1"
    assert jumps.nth(1).get_attribute("tabindex") == "-1"
    second.focus()
    assert first.get_attribute("tabindex") == "-1"
    assert jumps.nth(0).get_attribute("tabindex") == "-1"
    assert second.get_attribute("tabindex") == "0"
    assert jumps.nth(1).get_attribute("tabindex") == "0"
    game.assert_clean()


def test_animated_keyboard_echo_jump_keeps_topic(game_desktop: GamePage) -> None:
    game = game_desktop
    game.goto(
        state={"name": "Lotte", "settings": {"experience": "galaxy", "motion": "auto"}}
    )
    game.resume()
    game.page.get_by_role("button", name="Chart", exact=True).click()
    game.page.get_by_role("button", name="Land at Hangzhou, China").click()
    game.page.get_by_role("button", name="Skip flight").click()
    before = game.state()
    jump = game.page.get_by_role(
        "button", name="Jump to primary for LLM versus harness", exact=False
    )
    jump.focus()
    jump.press("Enter")
    expect(game.page.get_by_role("dialog", name="In flight")).to_be_visible()
    game.page.get_by_role("button", name="Skip flight").press("Enter")
    expect(game.page.locator("#galaxy-title")).to_have_text("The internet")
    expect(game.page.locator("#galaxy-check")).to_contain_text(
        "Finish LLM versus harness"
    )
    expect(game.page.locator('[data-galaxy-topic="llm"]')).to_be_focused()
    assert game.state().get("topics") == before.get("topics")
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


def test_echo_actions_fit_larger_desktop_text(game_desktop: GamePage) -> None:
    game = game_desktop
    game.goto(
        state={"name": "Lotte", "settings": {"experience": "galaxy", "motion": "off"}}
    )
    game.resume()
    game.page.evaluate("openSettings()")
    game.page.locator("#set-text").select_option("larger")
    game.page.locator("#sheet > .x").click()
    game.page.get_by_role("button", name="Chart", exact=True).click()
    game.page.get_by_role("button", name="Land at Hangzhou, China").click()
    row = game.page.locator("#galaxy-list .galaxy-place:has([data-galaxy-jump])")
    assert row.evaluate(
        "row => { const r=row.getBoundingClientRect(); "
        "return [...row.querySelectorAll('button')].every(button => { "
        "const b=button.getBoundingClientRect(); "
        "return b.width>=44 && b.height>=44 && b.left>=r.left && b.right<=r.right; "
        "}) }"
    )
    game.screenshot("galaxy_echo_desktop_larger")
    game.assert_clean()
