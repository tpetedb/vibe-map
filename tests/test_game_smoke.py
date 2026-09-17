"""Smoke tests for the game: start, claim, import, vault, every world.

Every test clicks the real buttons and ends by asserting that the page logged
zero errors. Screenshots land in tests/out/ so a human can look at them.
"""

from __future__ import annotations

from tests.conftest import WAIT_MS, GamePage, encode_progress


def test_game_loads_without_errors(game: GamePage) -> None:
    game.goto()
    assert game.page.is_visible("#title")
    assert game.page.title() == "Vibe Code Camp"
    game.screenshot("smoke_title", clip_height=860)
    game.assert_clean()


def test_every_claim_button_sits_in_its_own_screen(game: GamePage) -> None:
    """A stray closing tag once pushed workstream 6's button out of its section."""
    game.goto()
    homes = game.page.evaluate(
        """() => [1,2,3,4,5,6,7,8].map(n => {
          const b = document.querySelector(`[onclick="claim(${n})"]`);
          const s = b && b.closest('section.screen');
          return s ? s.id : 'none'; })"""
    )
    assert homes == [f"s-{n}" for n in range(1, 9)], homes
    assert (
        game.page.evaluate(
            "document.querySelectorAll('#sheet > .inner > section').length"
        )
        >= 13
    )


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
    first = game.page.locator("#plotlist button").nth(0).text_content() or ""
    assert "Pre-flight" in first, "Pre-flight must be the first roadmap entry"
    buttons = game.workstream_buttons()
    assert "blocked by dependency" in (buttons[1].text_content() or "")
    game.claim(1)
    state = game.state()
    assert state["done"] == [1]
    assert state["doneW"]["campus"] == [1]
    game.open_roadmap()
    buttons = game.workstream_buttons()
    assert "(delivered)" in (buttons[0].text_content() or "")
    assert "blocked" not in (buttons[1].text_content() or "")
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
    game.page.wait_for_function(
        "t => (document.getElementById('vnote').textContent || '') !== t", arg=first
    )
    assert (game.page.text_content("#vnote") or "") != first
    game.screenshot("smoke_vault")
    game.page.click("#vtop button:has-text('Tech tree')")
    game.page.wait_for_selector("#vtree.on", state="visible")
    assert game.page.locator("#vtree").is_visible()
    game.close_vault()
    game.assert_clean()


def test_every_world_builds(game: GamePage) -> None:
    seeded = {
        "name": "Lotte",
        "done": [1, 2, 3, 4],
        "doneW": {"campus": [1, 2, 3, 4], "winter": [], "desert": [], "prod": []},
        "path": {},
        "pitch": "",
        "versions": [],
        "bridges": {},
        "date": None,
        "wine": None,
        "world": "campus",
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


def test_roadmap_renders_before_the_island_starts(game: GamePage) -> None:
    """When WebGL fails the game falls back to the Roadmap; S.world is not set yet."""
    page = game.goto(state={"name": "Max", "done": [], "doneW": {"campus": []}}).page
    page.evaluate("openSheet('s-map')")
    assert "Innovation" in (page.text_content("#plotlist") or "")
    assert game.errors == []


def test_no_artifact_swallows_a_signpost(game: GamePage) -> None:
    """The mountain's radius once covered the Business Continuity signpost."""
    game.goto()
    game.start()
    overlaps = game.page.evaluate(
        """() => { const d = window.__data();
           return Object.entries(d.worlds).flatMap(([w, cfg]) =>
             cfg.plots.flatMap((p, i) => d.artifacts
               .filter(a => a.world === w)
               .filter(a => Math.hypot(a.pos[0]-p[0], a.pos[1]-p[1]) < a.r)
               .map(a => `${w} plot ${i+1} inside ${a.id}`))); }"""
    )
    assert overlaps == [], overlaps
    game.assert_clean()


def test_walking_to_the_fourth_signpost_offers_the_stop(game: GamePage) -> None:
    """Its signpost stands inside the mountain's ring; the stop must still win."""
    game.goto(state={"name": "Lotte", "doneW": {"campus": [1, 2, 3]}})
    game.resume()
    plot = game.page.evaluate("window.__data().worlds.campus.plots[3]")
    game.walk_to(plot[0], plot[1])
    game.page.wait_for_function("window.__debug().near === 4", timeout=5000)
    assert game.near() == 4, game.page.evaluate("window.__debug()")
    label = game.page.text_content("#enterbtn") or ""
    assert "Business Continuity" in label, label
    game.screenshot("smoke_plot4", clip_height=640)
    game.assert_clean()


def test_a_progress_code_of_an_unknown_version_is_refused(game: GamePage) -> None:
    game.goto()
    game.start()
    msg = game.import_code(encode_progress(done_w={"campus": [1, 2]}, version=7))
    assert "version 7" in msg and "version 2" in msg, msg
    assert game.state()["doneW"]["campus"] == []
    game.assert_clean()


def test_escape_closes_the_sheet_and_the_vault(game: GamePage) -> None:
    game.goto()
    game.start()
    game.open_roadmap()
    game.page.keyboard.press("Escape")
    game.page.wait_for_selector("#sheet.on", state="detached")
    assert not game.page.locator("#sheet").evaluate("e => e.classList.contains('on')")
    game.open_vault()
    game.page.keyboard.press("Escape")
    game.page.wait_for_selector("#vault.on", state="detached")
    assert not game.page.locator("#vault").evaluate("e => e.classList.contains('on')")
    game.assert_clean()


def test_full_screen_takes_the_element_that_holds_the_panels(game: GamePage) -> None:
    game.goto()
    game.start()
    game.open_roadmap()
    game.page.click("#s-map button:has-text('Full screen')")
    # requestFullscreen resolves a frame or more after the click, and a browser
    # that refuses it never resolves at all: wait for the element, not a clock.
    game.page.wait_for_function("() => !!document.fullscreenElement")
    res = game.page.evaluate(
        """() => { const fe = document.fullscreenElement;
          if (!fe) return null;
          const has = id => fe.contains(document.getElementById(id));
          return {tag: fe.tagName, sheet: has('sheet'), vault: has('vault')}; }"""
    )
    assert res is not None, "the browser refused fullscreen"
    assert res["sheet"] and res["vault"], res
    game.assert_clean()


def test_the_tech_tree_says_it_scrolls(game: GamePage) -> None:
    game.goto()
    game.start()
    game.page.click("#hud button:has-text('Tree')")
    game.page.wait_for_selector("#vtree.on", state="attached")
    game.page.wait_for_selector("#vtree .treenav button", state="attached")
    assert game.page.locator("#vtree .treenav button").count() == 2
    before = game.page.evaluate("document.getElementById('vtree').scrollLeft")
    game.page.click("#vtree .treenav button:has-text('Later')")
    # A smooth scroll starts a few frames after the click on a slow runner;
    # wait for movement rather than for stillness, which can be the start.
    game.page.wait_for_function(
        "b => document.getElementById('vtree').scrollLeft > b",
        arg=before,
        timeout=WAIT_MS,
    )
    after = game.page.evaluate("document.getElementById('vtree').scrollLeft")
    assert after > before, (before, after)
    game.assert_clean()


def test_the_pairings_come_from_the_theme(game: GamePage) -> None:
    """A coffee theme must not show the handwritten wine blocks."""
    game.goto()
    kind = game.page.evaluate("window.__data().config.theme.pairing")
    texts = game.page.evaluate(
        "() => [...document.querySelectorAll('.pairing')].map(e => e.textContent)"
    )
    if kind == "wine":
        assert any("Chardonnay" in t for t in texts)
        return
    pairings = game.page.evaluate("window.__data().config.theme.pairings")
    if not pairings:
        assert texts == []
        return
    assert texts and all("Chardonnay" not in t for t in texts), texts
    assert pairings[0] in texts[0], texts[0]
    game.assert_clean()


def test_the_vault_graph_keeps_its_labels_on_the_canvas(game: GamePage) -> None:
    game.goto()
    game.start()
    game.open_vault()
    outside = game.page.evaluate(
        """() => { const c = document.getElementById('vg');
          const w = c.clientWidth, h = c.clientHeight;
          return window.__debug().vault().sample
            .filter(([x, y]) => x < 8 || x > w - 8 || y < 8 || y > h - 8); }"""
    )
    assert outside == [], outside
    game.assert_clean()


def test_the_theme_names_the_buttons_and_the_kpis(game: GamePage) -> None:
    """Labels follow the theme: the studio preset never says OKRs or Velocity."""
    page = game.goto().page
    theme = page.evaluate("window.__data().config.theme")
    assert page.text_content("#btn-go") == theme["goLabel"]
    assert page.text_content("#btn-continue") == theme["resumeLabel"]
    assert page.text_content("#hud-stoplabel") == theme["stopLabel"]
    labels = [page.text_content(f"#k{i}l") for i in (1, 2, 3, 4)]
    assert labels == theme["kpiLabels"]
    assert theme["taglineSuffix"] in (page.text_content("#tagline") or "")
    if theme["id"] == "studio":
        assert labels == ["Progress", "Streak", "Connections", "Found"]
        assert page.text_content("#btn-go") == "Start"
        assert "OKRs" not in (page.text_content("#hud-stoplabel") or "")
    game.assert_clean()


def test_the_title_puts_the_form_above_the_go_button(game: GamePage) -> None:
    """Form first, satire below: the four steps come before Go, the prose after."""
    page = game.goto().page
    order = page.evaluate(
        """() => [...document.querySelectorAll('#title .box > *')]
             .map(e => e.id || e.className)"""
    )
    go = order.index("row go")
    assert order.index("onboard") < go < order.index("intro") < order.index("roles")
    assert page.locator("#onboard .step").count() == 4
    assert "prerequisites" in (page.text_content("#prereq") or "")
    game.assert_clean()


def test_the_prompt_builder_writes_the_prompt_you_paste(game: GamePage) -> None:
    game.goto()
    game.start()
    game.open_workstream(1)
    page = game.page
    page.fill(
        "#pitch",
        "A one-button game about a cat. Anyone can play it. Cross five times to win.",
    )
    page.dispatch_event("#pitch", "input")
    out = page.text_content("#pitch-out") or ""
    assert "A one-button game about a cat." in out
    assert "single file called index.html" in out
    assert "Three sentences" in (page.text_content("#pitch-note") or "")
    assert game.state()["pitch"].startswith("A one-button game")
    game.assert_clean()


def test_renaming_a_column_breaks_the_query(game: GamePage) -> None:
    game.goto()
    game.start()
    game.claim(1)
    game.claim(2)
    game.open_workstream(3)
    page = game.page
    assert "Rolinda" in (page.text_content("#schema-out") or "")
    page.click("#s-3 button:has-text('Rename score to points')")
    assert "Binder Error" in (page.text_content("#schema-out") or "")
    page.click("#s-3 button:has-text('Rename it back')")
    assert "Binder Error" not in (page.text_content("#schema-out") or "")
    game.assert_clean()


def test_a_scoped_change_request_changes_one_thing(game: GamePage) -> None:
    game.goto()
    game.start()
    game.claim(1)
    game.open_workstream(2)
    page = game.page
    before = page.inner_html("#card-demo")
    page.click("#s-2 button:has-text('Add a small badge')")
    assert "demo-badge" in page.inner_html("#card-demo")
    assert "Tonight's scores" in page.inner_html("#card-demo")
    page.click("#s-2 button:has-text('Make it more impactful')")
    assert "Impactful Scores Experience" in page.inner_html("#card-demo")
    assert "<th>Score</th>" not in page.inner_html("#card-demo")
    page.click("#s-2 button:has-text('Start over')")
    assert page.inner_html("#card-demo") == before
    game.assert_clean()
