"""Player controls, not frame sleeps, prove Galaxy autopilot and its exits."""

from __future__ import annotations

import pytest
from playwright.sync_api import expect

from tests.conftest import GamePage


def _chart(game: GamePage, motion: str = "on") -> None:
    game.goto(
        state={
            "name": "Lotte",
            "topics": ["unix"],
            "settings": {"experience": "galaxy", "motion": motion},
        }
    )
    game.resume()
    game.page.get_by_role("button", name="Chart", exact=True).click()


def _land(game: GamePage) -> None:
    game.page.get_by_role("button", name="Land at UC Santa Barbara", exact=True).click()


def _arrived(game: GamePage) -> None:
    expect(game.page.locator("#galaxy-flight")).not_to_be_visible()
    expect(game.page.locator("#vault")).not_to_have_class("on")
    expect(game.page.locator("#galaxy-title")).to_have_text("UC Santa Barbara")
    expect(game.page.locator('[data-galaxy-view="dome"]')).to_have_attribute(
        "aria-pressed", "true"
    )
    expect(game.page.locator("#c")).to_be_focused()
    game.assert_clean()


def test_autopilot_arrives_without_input(game_desktop: GamePage) -> None:
    game = game_desktop
    _chart(game)
    _land(game)
    expect(game.page.get_by_role("dialog", name="In flight")).to_be_visible()
    expect(game.page.get_by_role("button", name="Skip flight")).to_be_focused()
    game.screenshot("galaxy_ship_flight")
    _arrived(game)


@pytest.mark.parametrize("exit_key", ["Enter", "Escape"])
def test_keyboard_can_skip(game_desktop: GamePage, exit_key: str) -> None:
    game = game_desktop
    _chart(game)
    _land(game)
    game.page.get_by_role("button", name="Skip flight").press(exit_key)
    _arrived(game)


def test_motion_off_cuts_to_destination(game_desktop: GamePage) -> None:
    game = game_desktop
    _chart(game, "off")
    _land(game)
    _arrived(game)


def test_system_motion_change_lands_in_flight(game_desktop: GamePage) -> None:
    game = game_desktop
    _chart(game)
    _land(game)
    game.page.emulate_media(reduced_motion="reduce")
    _arrived(game)


def test_touch_skip(game_android: GamePage) -> None:
    game = game_android
    _chart(game)
    _land(game)
    game.page.get_by_role("button", name="Skip flight").tap()
    _arrived(game)


def test_landing_then_islands_keeps_progress(game_desktop: GamePage) -> None:
    game = game_desktop
    _chart(game)
    before = game.state()
    _land(game)
    game.page.get_by_role("button", name="Skip flight").click()
    _arrived(game)
    game.page.locator("#galaxy-list button").first.click()
    expect(game.page.locator("#vault")).to_have_class("on")
    game.page.evaluate("closeVault(); openSettings()")
    game.page.locator("#set-experience").select_option("islands")
    expect(game.page.locator("body")).to_have_attribute("data-experience", "islands")
    expect(game.page.locator("#galaxy-flight")).not_to_be_visible()
    assert game.page.locator("#c").get_attribute("tabindex") is None
    assert game.state().get("topics") == before.get("topics")
    assert game.state().get("done") == before.get("done")
    game.page.reload()
    game.resume()
    assert game.page.evaluate("window.__experienceId()") == "islands"
    game.assert_clean()


def test_experience_contract_disposes_an_active_flight(game_desktop: GamePage) -> None:
    game = game_desktop
    _chart(game)
    _land(game)
    expect(game.page.get_by_role("dialog", name="In flight")).to_be_visible()
    # Exercise the same settings entry point when navigation arrives during flight.
    game.page.evaluate("setSetting('experience', 'islands')")
    expect(game.page.locator("#galaxy-flight")).not_to_be_visible()
    assert game.page.evaluate("window.__experienceId()") == "islands"
    game.page.evaluate("setSetting('experience', 'galaxy')")
    expect(game.page.locator("#galaxy-title")).to_have_text("Your journey")
    expect(game.page.locator("#galaxy-flight")).not_to_be_visible()
    assert game.state()["topics"] == ["unix"]
    game.assert_clean()


def test_enter_keeps_focus_until_release(game_desktop: GamePage) -> None:
    game = game_desktop
    _chart(game)
    game.page.get_by_role(
        "button", name="Land at Bell Labs, Murray Hill", exact=True
    ).click()
    skip = game.page.get_by_role("button", name="Skip flight")
    game.page.keyboard.down("Enter")
    expect(skip).to_be_focused()
    game.page.keyboard.down("Enter")
    expect(skip).to_be_focused()
    game.page.keyboard.up("Enter")
    expect(game.page.locator("#galaxy-flight")).not_to_be_visible()
    expect(game.page.locator("#vault")).not_to_have_class("on")
    expect(game.page.locator("#galaxy-title")).to_have_text("Bell Labs, Murray Hill")
    game.assert_clean()
