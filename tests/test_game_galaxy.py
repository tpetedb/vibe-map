"""The Galaxy is playable through its scene and its accessible list twin."""

from __future__ import annotations

import base64
import json
import re

import pytest
from playwright.sync_api import expect

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


def test_galaxy_journey_globe_and_dome_share_one_listing(
    game_desktop: GamePage,
) -> None:
    game = game_desktop
    _open(game)
    rows = game.page.evaluate("window.__experience().listing()")
    assert rows and {row["state"] for row in rows} >= {"next", "ahead"}
    assert game.page.locator("#galaxy-list .galaxy-place").count() == len(rows)
    assert game.page.locator("#galaxy-list").get_by_text("NEXT", exact=False).count()
    assert game.page.locator('#galaxy-list [aria-current="step"]').count() == 1
    assert all(row["year"] and row["placeTitle"] for row in rows)
    game.page.get_by_role("button", name="Chart", exact=True).click()
    chart_text = game.page.locator("#galaxy-list").inner_text()
    showcases = (
        ("UC Santa Barbara", "california"),
        ("Hangzhou, China", "hangzhou"),
        ("A data centre", "data_centre"),
    )
    for place, _ in showcases:
        assert place in chart_text
    game.screenshot("galaxy_three_places", clip_height=760)
    for place, shot in showcases:
        row = game.page.locator("#galaxy-list .galaxy-place").filter(has_text=place)
        row.get_by_role("button", name="Land").click()
        assert game.page.locator("#vault").get_attribute("class") != "on"
        assert game.page.locator("#galaxy-context").inner_text()
        row = game.page.locator("#galaxy-list .galaxy-place").first
        row.get_by_role("button", name="Learn").click()
        assert game.page.locator("#vault").get_attribute("class") == "on"
        game.page.evaluate("closeVault()")
        game.screenshot(f"galaxy_place_{shot}", clip_height=760)
        game.page.evaluate("galaxyView('chart')")
    game.page.get_by_role("button", name="Journey", exact=True).click()
    first_place = game.page.locator("[data-galaxy-place]").first
    first_place.focus()
    assert game.page.evaluate(
        "window.__scene().children.some(item => "
        "item.geometry?.type === 'TorusGeometry')"
    )
    first_place.blur()
    assert not game.page.evaluate(
        "window.__scene().children.some(item => "
        "item.geometry?.type === 'TorusGeometry')"
    )
    first_place.press("ArrowDown")
    assert game.page.evaluate("document.activeElement.dataset.galaxyPlace")
    first_place.press("Escape")
    chart = game.page.locator('[data-galaxy-view="chart"]')
    assert chart.get_attribute("class") == "on"

    for view in ("journey", "chart", "globe", "dome"):
        game.page.get_by_role("button", name=view.title(), exact=True).click()
        assert (
            game.page.locator(f'[data-galaxy-view="{view}"]').get_attribute("class")
            == "on"
        )
    game.screenshot("galaxy_desktop_dome", clip_height=760)
    first_place = game.page.locator("[data-galaxy-place]").first
    first_place.click()
    assert game.page.locator('[data-galaxy-view="dome"]').get_attribute("class") == "on"
    assert game.page.locator("#galaxy-title").inner_text()
    assert game.page.locator("#vault").get_attribute("class") == "on"
    game.assert_clean()


def test_galaxy_phone_targets_and_experience_switch(
    game_webkit_iphone: GamePage,
    game_android: GamePage,
) -> None:
    for game in (game_webkit_iphone, game_android):
        _open(game)
        sizes = game.page.locator("#galaxy-ui button:visible").evaluate_all(
            "buttons => buttons.map(b => { const r=b.getBoundingClientRect(); "
            "return [r.width,r.height] })"
        )
        assert sizes and all(width >= 44 and height >= 44 for width, height in sizes), (
            sizes
        )

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


@pytest.mark.parametrize("profile", ["game_desktop", "game_webkit_iphone"])
def test_import_refreshes_the_visible_course_with_motion_off(request, profile) -> None:
    game = request.getfixturevalue(profile)
    _open(game)
    payload = (
        base64.urlsafe_b64encode(json.dumps({"v": 2, "topics": ["unix"]}).encode())
        .decode()
        .rstrip("=")
    )
    assert "1 topic" in game.import_code(payload)
    game.page.locator("#sheet > .x").click()
    expect(game.page.locator("#galaxy-summary")).to_have_text("1 of 70 topics complete")
    expect(
        game.page.locator('[data-galaxy-topic="unix"]').locator("..")
    ).to_have_attribute("data-state", "done")
    route = game.page.evaluate("""() => window.__scene().children
        .find(item => item.userData.courseRoute).children
        .filter(item => item.userData.topicId).map(item => item.userData)""")
    listing = game.page.evaluate("window.__experience().listing()")
    assert [node["topicId"] for node in route] == [row["id"] for row in listing]
    assert [node["state"] for node in route] == [row["state"] for row in listing]
    assert len(route) == 70
    assert [node["order"] for node in route] == list(range(1, 71))
    assert sum(node["state"] == "next" for node in route) == 1
    assert next(node for node in route if node["topicId"] == "unix")["state"] == "done"
    expect(game.page.locator("#galaxy-next")).to_contain_text("Next:")
    game.screenshot("galaxy_journey_" + profile, clip_height=760)
    points = game.page.evaluate("window.__galaxyRoute()")
    assert len(points) <= 12
    assert game.page.locator("#galaxy-overview circle").count() == 70
    assert game.page.evaluate("window.__debug().draws") < 150
    assert all(p["hitRadius"] >= 22 for p in points)
    viewport = game.page.viewport_size
    assert all(0 < p["x"] < viewport["width"] for p in points)
    assert all(0 < p["y"] < viewport["height"] for p in points)
    target = next(p for p in points if p["state"] == "next")
    game.page.mouse.click(target["x"] + 18, target["y"])
    game.page.mouse.click(target["x"], target["y"])
    expect(game.page.locator("#vault")).to_have_class("on")
    expect(game.page.locator('[data-galaxy-view="journey"]')).to_have_class("on")
    game.page.locator('#vault button[onclick="closeVault()"]').click()
    game.page.get_by_role("button", name="Chart", exact=True).click()
    expect(game.page.locator("#galaxy-list")).to_contain_text("1 of")
    game.assert_clean()


@pytest.mark.parametrize("profile", ["game_desktop", "game_webkit_iphone"])
def test_galaxy_list_land_and_learn_without_webgl(request, profile) -> None:
    game = request.getfixturevalue(profile)
    game.page.add_init_script("""const context=HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext=function(kind,...args){
          return /webgl/.test(kind)?null:context.call(this,kind,...args);
        };""")
    game.goto(state={"name": "Lotte", "settings": {"experience": "galaxy"}})
    expect(game.page.locator("#btn-continue")).to_have_text("Resume Galaxy")
    expect(game.page.locator("#intro")).to_contain_text("Welcome to Galaxy")
    game.page.locator("#btn-continue").click()
    expect(game.page.locator("#sheet")).not_to_have_class("on")
    expect(game.page.locator("#bub-text")).to_have_attribute(
        "aria-label", re.compile("Follow the course journey")
    )
    game.page.get_by_role("button", name="Chart", exact=True).click()
    row = game.page.locator("#galaxy-list .galaxy-place").filter(has_text="Hangzhou")
    row.get_by_role("button", name="Land").click()
    expect(game.page.locator("#galaxy-title")).to_have_text("Hangzhou, China")
    game.page.locator("#galaxy-list").get_by_role("button", name="Learn").first.click()
    expect(game.page.locator("#vault")).to_have_class("on")
    game.page.get_by_role("button", name="Back to Galaxy", exact=True).click()
    game.page.get_by_role("button", name="More", exact=True).click()
    game.page.get_by_role("button", name="Settings", exact=True).click()
    expect(
        game.page.locator("#s-settings").get_by_role(
            "button", name="Back to Galaxy", exact=True
        )
    ).to_be_visible()
    game.page.locator("#s-settings").get_by_role(
        "button", name="Back to Galaxy", exact=True
    ).click()
    game.page.get_by_role("button", name="Journey", exact=True).click()
    payload = (
        base64.urlsafe_b64encode(json.dumps({"v": 2, "topics": ["unix"]}).encode())
        .decode()
        .rstrip("=")
    )
    assert "1 topic" in game.import_code(payload)
    game.page.locator("#sheet > .x").click()
    expect(game.page.locator("#galaxy-summary")).to_have_text("1 of 70 topics complete")
    expect(
        game.page.locator('[data-galaxy-topic="unix"]').locator("..")
    ).to_have_attribute("data-state", "done")
    assert not [error for error in game.errors if "WebGL context" not in error]


@pytest.mark.parametrize("profile", ["game_desktop", "game_webkit_iphone"])
def test_galaxy_tablet_composition_leaves_room_for_the_dome(request, profile) -> None:
    game = request.getfixturevalue(profile)
    game.page.set_viewport_size({"width": 807, "height": 1571})
    _open(game)
    for place, shot in [("Hangzhou", "city"), ("A data centre", "racks")]:
        game.page.get_by_role("button", name="Chart", exact=True).click()
        game.page.locator("#galaxy-list .galaxy-place").filter(
            has_text=place
        ).get_by_role("button", name="Land").click()
        frame = game.page.evaluate("window.__galaxyFrame()")
        assert frame["inside"], frame
        assert frame["clearOfUi"], frame
        game.screenshot("galaxy_tablet_" + shot)
    game.assert_clean()


def test_landing_reuses_the_island_builder_without_changing_the_campaign(
    game_desktop: GamePage,
) -> None:
    game = game_desktop
    _open(game)
    campaign = game.page.evaluate(
        """() => {const s=window.__S();return {
          world:s.world,done:s.done,doneW:s.doneW,
          chapters:window.__experiences().islands.listing()}}"""
    )
    for place in ("UC Santa Barbara", "Hangzhou", "A data centre"):
        game.page.get_by_role("button", name="Chart", exact=True).click()
        game.page.locator("#galaxy-list .galaxy-place").filter(
            has_text=place
        ).get_by_role("button", name="Land").click()
        model = game.page.evaluate("""() => {
          let miniature=null;
          window.__scene().traverse(o=>{if(o.userData.miniature)miniature=o});
          return miniature && {surface:miniature.userData.walkSurface,
            lessons:miniature.userData.lessonSites.map(s=>s.id),
            pavilions:miniature.children.filter(o=>o.userData.lessonId).length};
        }""")
        assert model, "Landing must use the shared miniature builder"
        assert model["surface"]["radius"] > 0
        assert model["lessons"] == game.page.locator(
            "#galaxy-list [data-galaxy-topic]"
        ).evaluate_all("buttons=>buttons.map(b=>b.dataset.galaxyTopic)")
        assert model["pavilions"] == len(model["lessons"])
        assert campaign == game.page.evaluate(
            """() => {const s=window.__S();return {
          world:s.world,done:s.done,doneW:s.doneW,
          chapters:window.__experiences().islands.listing()}}"""
        )
    game.assert_clean()


@pytest.mark.parametrize("motion", ["off", "auto"])
def test_world_control_keeps_galaxy_and_campaign_intact(game_desktop, motion):
    game = game_desktop
    game.goto(
        state={"name": "Lotte", "settings": {"experience": "galaxy", "motion": motion}}
    )
    game.resume()
    before = game.page.evaluate("window.__S().world")
    game.hud_action('#hud button:has-text("World")')
    assert game.page.evaluate("window.__S().world") == before
    assert not game.page.evaluate("window.__debug().flying")
    expect(game.page.locator('[data-galaxy-view="chart"]')).to_have_class("on")
    game.page.get_by_role("button", name="Journey", exact=True).click()
    expect(game.page.locator('[data-galaxy-topic="unix"]')).to_be_visible()
    game.assert_clean()


def test_galaxy_learning_keeps_focus_and_explains_check_import(game_desktop):
    game = game_desktop
    _open(game)
    button = game.page.get_by_role(
        "button", name="Learn Unix and the terminal", exact=True
    )
    button.focus()
    button.press("Enter")
    expect(game.page.locator("#vault")).to_have_class("on")
    expect(game.page.locator("#vnote")).to_contain_text(
        "uv run vibe check --topic unix"
    )
    expect(game.page.locator("#vnote")).to_contain_text("uv run vibe export")
    expect(game.page.locator("#vnote .galaxy-check .copy")).to_be_visible()
    game.page.keyboard.press("Escape")
    expect(button).to_be_focused()
    expect(game.page.locator('[data-galaxy-view="journey"]')).to_have_attribute(
        "aria-pressed", "true"
    )
    assert game.page.locator('#galaxy-list button[tabindex="0"]').count() == 1
    button.press("ArrowDown")
    expect(
        game.page.get_by_role(
            "button", name="Learn Files, folders and paths", exact=True
        )
    ).to_be_focused()
    game.assert_clean()


def test_galaxy_focus_names_the_exact_topic_and_chart_resets_north(game_desktop):
    game = game_desktop
    _open(game)
    dotfiles = game.page.locator('[data-galaxy-topic="dotfiles"]')
    dotfiles.focus()
    assert game.page.evaluate(
        "window.__scene().children.some(o=>o.userData.focusTopic==='dotfiles')"
    )
    expect(game.page.locator("#galaxy-label")).to_contain_text("Dotfiles")
    game.page.get_by_role("button", name="Chart", exact=True).click()
    game.page.get_by_role("button", name="Land at Hangzhou, China", exact=True).click()
    game.page.get_by_role("button", name="Globe", exact=True).click()
    expect(game.page.locator("#galaxy-label")).to_contain_text("Hangzhou")
    game.page.get_by_role("button", name="Chart", exact=True).click()
    assert game.page.evaluate(
        "window.__scene().children.filter(o=>o.userData.globe).every(o=>Math.abs(o.rotation.x)+Math.abs(o.rotation.z)<1e-8)"
    )
    game.assert_clean()


def test_explicit_setting_overrides_the_galaxy_url(game_desktop):
    game = game_desktop
    game.goto(state={"name": "Lotte", "settings": {"motion": "off"}})
    game.page.goto(game.url + "?experience=galaxy")
    game.resume()
    game.hud_action('#hud button[aria-label="Settings"]')
    game.page.locator("#set-experience").select_option("islands")
    expect(game.page.locator("body")).to_have_attribute("data-experience", "islands")
    assert "experience=" not in game.page.url
    assert game.state()["settings"]["experience"] == "islands"
    game.assert_clean()


def test_galaxy_short_screen_uses_the_complete_list(game_desktop):
    game = game_desktop
    game.page.set_viewport_size({"width": 720, "height": 450})
    _open(game)
    label = game.page.locator("#galaxy-list .galaxy-place b").first
    state = game.page.locator("#galaxy-list .galaxy-state").first
    learn = game.page.locator("#galaxy-list .galaxy-place button").first
    normal_label = float(
        label.evaluate("el => parseFloat(getComputedStyle(el).fontSize)")
    )
    normal_state = float(
        state.evaluate("el => parseFloat(getComputedStyle(el).fontSize)")
    )
    normal_learn = float(
        learn.evaluate("el => parseFloat(getComputedStyle(el).fontSize)")
    )
    game.hud_action('#hud button[aria-label="Settings"]')
    game.page.locator("#set-text").select_option("larger")
    game.page.locator("#sheet > .x").click()
    assert (
        float(label.evaluate("el => parseFloat(getComputedStyle(el).fontSize)"))
        > normal_label
    )
    assert (
        float(state.evaluate("el => parseFloat(getComputedStyle(el).fontSize)"))
        > normal_state
    )
    assert (
        float(learn.evaluate("el => parseFloat(getComputedStyle(el).fontSize)"))
        > normal_learn
    )
    expect(game.page.locator("#galaxy-ui")).to_have_attribute("data-rendering", "list")
    expect(game.page.locator("#c")).not_to_be_visible()
    assert game.page.locator("#galaxy-list [data-galaxy-topic]").count() == 70
    game.page.set_viewport_size({"width": 360, "height": 450})
    assert game.page.locator("#galaxy-ui").evaluate(
        "el => el.scrollWidth <= el.clientWidth + 1"
    )
    game.page.locator('[data-galaxy-topic="unix"]').click()
    expect(game.page.locator("#vault")).to_have_class("on")
    game.screenshot("galaxy_short_screen_lesson")
    game.assert_clean()


def test_mixed_progress_import_does_not_build_island_graphics_in_galaxy(game_desktop):
    game = game_desktop
    game.goto(
        state={
            "name": "Lotte",
            "world": "campus",
            "settings": {"experience": "galaxy", "motion": "off"},
        }
    )
    game.resume()
    payload = (
        base64.urlsafe_b64encode(
            json.dumps({"v": 2, "doneW": {"campus": [1]}, "topics": ["unix"]}).encode()
        )
        .decode()
        .rstrip("=")
    )
    assert "1 topic" in game.import_code(payload)
    game.page.locator("#sheet > .x").click()
    expect(game.page.locator("#galaxy-summary")).to_have_text("1 of 70 topics complete")
    assert game.page.evaluate("window.__scene().background.getHex()") == 0
    assert game.state()["doneW"]["campus"] == [1]
    game.assert_clean()


@pytest.mark.parametrize("profile", ["game_desktop", "game_webkit_iphone"])
def test_galaxy_landing_walks_to_a_lesson_with_shared_input(request, profile):
    game = request.getfixturevalue(profile)
    _open(game)
    assert game.page.evaluate("window.__experience().where()") is None
    game.page.get_by_role("button", name="Chart", exact=True).click()
    game.page.locator("#galaxy-list .galaxy-place").filter(
        has_text="UC Santa Barbara"
    ).get_by_role("button", name="Land").click()
    game.page.wait_for_function("window.__galaxyWalk?.()?.active")
    assert game.page.evaluate("window.__experience().where()") == {
        "kind": "place",
        "id": "uc-santa-barbara",
    }
    start = game.page.evaluate("window.__galaxyWalk()")
    assert start["valid"]
    game.page.locator("#c").focus()
    game.page.keyboard.down("ArrowLeft")
    game.page.wait_for_function(
        "x => window.__galaxyWalk().position[0] < x - .08", arg=start["position"][0]
    )
    game.page.keyboard.up("ArrowLeft")
    site = game.page.evaluate("window.__galaxyWalk().sites[0]")
    if profile == "game_webkit_iphone":
        game.page.touchscreen.tap(site["screen"][0] + 18, site["screen"][1])
    else:
        game.page.mouse.click(site["screen"][0] + 18, site["screen"][1])
    game.page.wait_for_function(
        "id => window.__galaxyWalk().near === id", arg=site["id"]
    )
    assert game.page.evaluate("window.__experience().where()") == {
        "kind": "topic",
        "id": site["id"],
        "place": "uc-santa-barbara",
    }
    game.screenshot("galaxy_walk_arrived_" + profile)
    game.page.get_by_role("button", name="Open nearby lesson").click()
    expect(game.page.locator("#vault")).to_have_class("on")
    paused = game.page.evaluate("window.__galaxyWalk()")
    game.page.keyboard.down("d")
    game.page.wait_for_function(
        "frame => window.__galaxyWalk().frame > frame + 4", arg=paused["frame"]
    )
    game.page.keyboard.up("d")
    assert game.page.evaluate("window.__galaxyWalk().position") == paused["position"]
    game.screenshot("galaxy_walk_lesson_" + profile)
    game.assert_clean()


@pytest.mark.parametrize("profile", ["game_desktop", "game_webkit_iphone"])
def test_galaxy_walk_stick_collision_and_water(request, profile):
    game = request.getfixturevalue(profile)
    _open(game)
    game.page.get_by_role("button", name="Chart", exact=True).click()
    game.page.locator("#galaxy-list .galaxy-place").filter(
        has_text="Hangzhou"
    ).get_by_role("button", name="Land").click()
    game.page.wait_for_function("window.__galaxyWalk?.()?.active")
    joy = game.page.locator("#joy")
    expect(joy).to_be_visible()
    box = joy.bounding_box()
    start = game.page.evaluate("window.__galaxyWalk()")
    game.page.mouse.move(box["x"] + box["width"] * 0.9, box["y"] + box["height"] / 2)
    game.page.mouse.down()
    game.page.wait_for_function(
        "start => window.__galaxyWalk().frame > start + 24", arg=start["frame"]
    )
    game.page.mouse.up()
    walked = game.page.evaluate("window.__galaxyWalk()")
    assert walked["position"][0] > start["position"][0] + 0.08
    assert walked["valid"], "The shared stick must respect the shoreline"
    assert sum(v * v for v in walked["position"]) < 0.94**2
    game.page.locator("#c").focus()
    game.page.keyboard.down("ArrowUp")
    game.page.wait_for_function(
        "start => window.__galaxyWalk().frame > start + 32", arg=walked["frame"]
    )
    game.page.keyboard.up("ArrowUp")
    blocked = game.page.evaluate("window.__galaxyWalk()")
    assert blocked["valid"]
    assert 0.12 < blocked["position"][1] < walked["position"][1] - 0.08
    water = game.page.evaluate("window.__galaxyGroundAt(-.33, .1)")
    game.page.mouse.click(*water)
    assert game.page.evaluate("window.__galaxyWalk().route") == 0
    assert game.page.evaluate("window.__galaxyWalk().valid")
    game.screenshot("galaxy_walk_surface_" + profile)
    game.page.get_by_role("button", name="Journey", exact=True).click()
    expect(joy).not_to_be_visible()
    assert game.page.evaluate("window.__galaxyWalk()") is None
    game.assert_clean()
