"""The HUD hierarchy, the command palette, the sheet overlay and the copy.

Every test drives the real entry point: a click on the button a player would
press, or the key they would type. Desktop is 1440x900, the laptop the course
is written for; the phone tests run in the 420px Chromium context.
"""

from __future__ import annotations

from tests.conftest import WAIT_MS, GamePage

# Everything but Roadmap and Search is secondary or tertiary; the order is the
# one the HUD renders and a new button is one more entry in #hud-sec.
SECONDARY = ["Backpack", "Ask", "Stats", "Vault", "Tree", "World"]


def _started(game: GamePage) -> GamePage:
    game.goto()
    game.start("Lotte")
    return game


def _visible(game: GamePage, label: str) -> bool:
    return game.page.locator(f"#hud button:has-text('{label}')").first.is_visible()


def test_the_desktop_hud_shows_the_secondary_row_and_hides_settings(
    game_desktop: GamePage,
) -> None:
    game = _started(game_desktop)
    assert _visible(game, "Roadmap")
    assert _visible(game, "Search")
    for label in SECONDARY:
        assert _visible(game, label), f"{label} should be in the pill at 1440px"
    assert not _visible(game, "Settings"), "Settings is tertiary: menu only"
    game.page.click("#hud-more-btn")
    assert game.page.get_attribute("#hud-more-btn", "aria-expanded") == "true"
    assert _visible(game, "Settings")
    game.screenshot("ui_desktop_hud", clip_height=200)
    game.page.keyboard.press("Escape")
    game.page.wait_for_selector("#hud-more.open", state="detached")
    assert not _visible(game, "Settings")
    game.assert_clean()


def test_the_phone_hud_keeps_one_button_and_a_menu(game: GamePage) -> None:
    """At 420px only Roadmap and Search stay out; the rest is one menu away."""
    game = _started(game)
    assert _visible(game, "Roadmap")
    for label in [*SECONDARY, "Settings"]:
        assert not _visible(game, label), f"{label} should be behind More"
    game.page.click("#hud-more-btn")
    game.page.wait_for_selector("#hud-more.open", state="attached")
    for label in [*SECONDARY, "Settings"]:
        assert _visible(game, label), f"{label} should be in the menu"
    game.screenshot("ui_phone_hud_menu", clip_height=520)
    # Picking one closes the menu, so the island is not left with a popup on it.
    game.page.click("#hud button:has-text('Stats')")
    game.page.wait_for_selector("#hud-more.open", state="detached")
    game.assert_clean()


def test_the_hud_does_not_overflow_the_phone_with_the_menu_open(
    game: GamePage,
) -> None:
    game = _started(game)
    game.page.click("#hud-more-btn")
    game.page.wait_for_selector("#hud-more.open", state="attached")
    overflow = game.page.evaluate(
        """() => [...document.querySelectorAll('#hud .pill, #hud-menu, #kpis .kpi')]
             .map(e => e.getBoundingClientRect())
             .filter(r => r.right > window.innerWidth + 1 || r.left < -1).length"""
    )
    assert overflow == 0
    game.assert_clean()


def test_the_palette_opens_with_the_keyboard_and_opens_a_note(
    game_desktop: GamePage,
) -> None:
    game = _started(game_desktop)
    game.page.keyboard.press("Control+k")
    game.page.wait_for_selector("#pal.on", state="attached")
    game.page.fill("#pal-q", "hook")
    game.page.wait_for_function(
        "() => document.querySelectorAll('#pal-list .pal-row').length > 0"
    )
    kinds = game.page.evaluate(
        "() => [...document.querySelectorAll('#pal-list .pal-kind')]"
        ".map(e => e.textContent)"
    )
    assert kinds, "the palette found nothing for a word in the tech tree"
    game.screenshot("ui_palette", clip_height=620)
    game.page.keyboard.press("ArrowDown")
    game.page.keyboard.press("Enter")
    game.page.wait_for_selector("#vault.on", state="attached")
    assert (game.page.text_content("#vnote") or "").strip()
    game.page.keyboard.press("Escape")
    game.assert_clean()


def test_the_palette_finds_a_stop_a_mentor_and_an_artifact(
    game_desktop: GamePage,
) -> None:
    game = _started(game_desktop)
    game.page.click("#hud button:has-text('Search')")
    game.page.wait_for_selector("#pal.on", state="attached")

    def kinds_for(query: str) -> list[str]:
        game.page.fill("#pal-q", query)
        game.page.wait_for_function(
            "() => document.querySelectorAll('#pal-list .pal-row').length >= 0"
        )
        return game.page.evaluate(
            "() => [...document.querySelectorAll('#pal-list .pal-kind')]"
            ".map(e => e.textContent)"
        )

    assert "Mentor" in kinds_for("karpathy")
    assert "Artifact" in kinds_for("cafe")
    stop_label = game.page.evaluate("() => window.__data().config.theme.stopLabel")
    assert stop_label in kinds_for("innovation hub")
    game.page.keyboard.press("Escape")
    game.page.wait_for_selector("#pal.on", state="detached")
    game.assert_clean()


def test_the_palette_opens_the_stop_it_was_asked_for(game_desktop: GamePage) -> None:
    game = _started(game_desktop)
    game.page.click("#hud button:has-text('Search')")
    game.page.fill("#pal-q", "Data Warehouse")
    game.page.wait_for_function(
        "() => document.querySelectorAll('#pal-list .pal-row').length > 0"
    )
    stop_label = game.page.evaluate("() => window.__data().config.theme.stopLabel")
    game.page.click(f"#pal-list .pal-row:has(.pal-kind:text-is('{stop_label}'))")
    game.page.wait_for_selector("#s-3.on", state="attached")
    game.assert_clean()


def test_the_sheet_is_an_overlay_with_a_sticky_action_bar(
    game_desktop: GamePage,
) -> None:
    game = _started(game_desktop)
    game.open_workstream(1)
    game.still(
        "document.querySelector('#s-1 .row.actions').getBoundingClientRect().top"
    )
    # The bar's own requirement, waited for rather than sampled: it sits on the
    # bottom edge of the window once the sheet's open spring has landed.
    game.until(
        "Math.abs(document.querySelector('#s-1 .row.actions')"
        ".getBoundingClientRect().bottom - window.innerHeight) < 2"
    )
    metrics = game.page.evaluate(
        """() => {
          const sheet = document.getElementById('sheet');
          const inner = sheet.querySelector('.inner');
          const bar = document.querySelector('#s-1 .row.actions');
          const r = bar.getBoundingClientRect();
          return {pos: getComputedStyle(sheet).position,
                  barPos: getComputedStyle(bar).position,
                  barBottom: r.bottom, winH: window.innerHeight,
                  scrolls: inner.scrollHeight > inner.clientHeight + 1,
                  pageY: window.scrollY,
                  labels: [...bar.querySelectorAll('button')].map(b => b.textContent)};
        }"""
    )
    assert metrics["pos"] == "fixed"
    assert metrics["barPos"] == "sticky"
    assert metrics["scrolls"], "the lesson should scroll inside the sheet"
    assert metrics["pageY"] == 0, "the page behind the overlay must not move"
    assert abs(metrics["barBottom"] - metrics["winH"]) < 2, metrics
    assert any("Mark as done" in label for label in metrics["labels"]), metrics
    assert any("Back" in label for label in metrics["labels"]), metrics
    game.screenshot("ui_desktop_sheet")
    game.assert_clean()


def test_the_hud_stays_reachable_while_the_sheet_is_open(
    game_desktop: GamePage,
) -> None:
    """The overlay covers the island, not the bar: Ask and Search still work."""
    game = _started(game_desktop)
    game.open_workstream(1)
    assert _visible(game, "Search")
    game.page.click("#hud button:has-text('Search')")
    game.page.wait_for_selector("#pal.on", state="attached")
    game.page.keyboard.press("Escape")
    game.assert_clean()


def test_a_list_screen_has_no_bar_over_its_own_items(game_desktop: GamePage) -> None:
    game = _started(game_desktop)
    game.open_roadmap()
    assert game.page.locator("#s-map .row.actions").count() == 0
    game.assert_clean()


def test_the_touch_controls_are_gone_on_a_pointer_that_is_fine(
    game_desktop: GamePage,
) -> None:
    game = _started(game_desktop)
    shown = game.page.evaluate(
        """() => ['joy', 'jump'].filter(id =>
             getComputedStyle(document.getElementById(id)).display !== 'none')"""
    )
    assert shown == [], f"touch controls drawn on a mouse: {shown}"
    game.assert_clean()


def test_the_scene_and_the_bubble_fill_the_window(game_desktop: GamePage) -> None:
    """No black letterbox: the stage ends where the talk band begins."""
    metrics = _started(game_desktop).page.evaluate(
        """() => {
          const stage = document.getElementById('stage').getBoundingClientRect();
          const talk = document.getElementById('talk').getBoundingClientRect();
          return {gap: talk.top - stage.bottom,
                  below: window.innerHeight - talk.bottom};
        }"""
    )
    assert abs(metrics["gap"]) < 2, metrics
    assert abs(metrics["below"]) < 2, metrics


def test_the_hint_carries_its_own_backing(game_desktop: GamePage) -> None:
    """Light grey on bright grass fails; the hint gets a pill behind it."""
    background = _started(game_desktop).page.evaluate(
        "getComputedStyle(document.getElementById('hint')).backgroundColor"
    )
    assert background not in ("rgba(0, 0, 0, 0)", "transparent"), background


def test_the_name_field_is_in_view_with_the_button_that_needs_it(
    game_desktop: GamePage,
) -> None:
    """At 1440x900 the field the copy points at cannot be below the fold."""
    page = game_desktop.goto().page
    box = page.locator("#name").bounding_box()
    go = page.locator("#title .row.go button.primary").bounding_box()
    assert box and go
    assert box["y"] + box["height"] <= 900, box
    assert go["y"] + go["height"] <= 900, go
    game_desktop.screenshot("ui_desktop_title")
    game_desktop.assert_clean()


def test_a_refused_clipboard_says_so_and_selects_the_text(game: GamePage) -> None:
    game = _started(game)
    game.open_workstream(1)
    game.page.evaluate(
        """() => { Object.defineProperty(navigator, 'clipboard', {
             value: {writeText: () => Promise.reject(new Error('no'))},
             configurable: true}); }"""
    )
    game.page.fill("#pitch", "A game. Anyone plays it. You win by crossing.")
    game.page.click("#pitch-copy")
    game.page.wait_for_function(
        "() => document.getElementById('pitch-copy').textContent.includes('Selected')",
        timeout=WAIT_MS,
    )
    assert (game.page.evaluate("() => String(getSelection())") or "").strip()
    game.assert_clean()


def test_an_empty_release_note_is_refused_with_a_reason(game: GamePage) -> None:
    game = _started(game)
    game.page.evaluate("openCh(4)")
    game.page.wait_for_selector("#s-4.on", state="attached")
    game.sheet_in_place()
    game.page.fill("#release", "")
    game.page.click("#s-4 button:has-text('Commit and tag release')")
    game.page.wait_for_function(
        "() => (document.getElementById('release-msg').textContent || '') !== ''"
    )
    assert "empty" in (game.page.text_content("#release-msg") or "")
    assert game.state()["versions"] == []
    game.assert_clean()


def test_the_precise_change_request_changes_only_what_it_named(
    game: GamePage,
) -> None:
    """Both asks start from the same card, so the demo matches its own text."""
    game = _started(game)
    game.page.evaluate("openCh(2)")
    game.page.wait_for_selector("#s-2.on", state="attached")
    game.sheet_in_place()
    game.page.click("#s-2 button.prompt:has-text('more impactful')")
    ruined = game.page.text_content("#card-demo") or ""
    assert "Impactful" in ruined
    game.page.click("#s-2 button.prompt:has-text('small badge')")
    card = game.page.evaluate(
        """() => {
          const el = document.querySelector('#card-demo .demo-card');
          return {text: el.textContent, serif: el.classList.contains('serif'),
                  cols: [...el.querySelectorAll('th')].map(t => t.textContent)};
        }"""
    )
    assert "Tonight's scores" in card["text"], card
    assert card["cols"] == ["Player", "Score"], card
    assert not card["serif"], card
    assert "new" in card["text"], "the badge is the one thing that was asked for"
    game.assert_clean()


def test_the_artifact_header_says_what_the_number_counts(game: GamePage) -> None:
    game = _started(game)
    game.page.evaluate("openArtifact('cafe')")
    game.page.wait_for_selector("#s-artifact.on", state="attached")
    head = game.page.text_content("#s-artifact .hour") or ""
    assert "found" in head, head
    game.assert_clean()


def test_the_repeated_open_buttons_carry_their_own_labels(game: GamePage) -> None:
    game = _started(game)
    game.open_roadmap()
    labels = game.page.evaluate(
        """() => [...document.querySelectorAll('#plotlist button')]
             .filter(b => b.textContent.trim() === 'Open')
             .map(b => b.getAttribute('aria-label'))"""
    )
    assert len(labels) >= 30, len(labels)
    assert all(label and label != "Open" for label in labels)
    assert len(set(labels)) == len(labels), "every label names its own row"
    game.assert_clean()


def test_the_settings_screen_names_the_file_a_camp_really_has(
    game: GamePage,
) -> None:
    game = _started(game)
    game.page.evaluate("openSettings()")
    game.page.wait_for_selector("#s-settings.on", state="attached")
    text = game.page.text_content("#s-settings") or ""
    assert "config/camp.toml" in text
    assert "vibe.toml" not in text.replace("config/camp.toml", "")
    game.assert_clean()


def test_no_screen_still_points_at_the_retired_config_file(game: GamePage) -> None:
    game = _started(game)
    body = game.page.evaluate("() => document.body.innerText")
    assert "vibe.toml" not in body


def test_the_export_message_is_a_command_you_can_follow(game: GamePage) -> None:
    game = _started(game)
    game.open_roadmap()
    game.page.click("#s-map button:has-text('Export progress')")
    game.page.wait_for_function(
        "() => (document.getElementById('syncmsg').textContent || '') !== ''"
    )
    msg = game.page.text_content("#syncmsg") or ""
    assert "…" not in msg, "the command was cut with an ellipsis"
    assert "vibe import" in msg
    assert "in the repo" not in msg, "a camp is not the repo"
    assert "camp" in msg
    game.assert_clean()


def test_the_go_live_pairing_block_is_a_sentence(game: GamePage) -> None:
    """The items carry commas of their own, so the list needs more than one."""
    game = _started(game)
    game.page.evaluate("() => { window.__S().done = [1,2,3,4,5,6,7,8]; }")
    game.page.evaluate("openCh(9)")
    game.page.wait_for_selector("#s-9.on", state="attached")
    text = game.page.text_content("#s-9 .pairing") or ""
    if "go-live" in text.lower() and ";" not in text:
        # The wine theme keeps its handwritten block, which is already a sentence.
        assert "Rolinda" in text or "pre-approved" in text, text
    else:
        assert ";" in text and " and " in text, text
    game.assert_clean()


def test_a_reload_restores_exactly_the_islands_that_were_played(
    game: GamePage,
) -> None:
    """Two islands played, then a reload: every island keeps its own stops.

    The campus is the one that used to collect another island's progress,
    because the saved record carried both the map and the alias of the active
    island's array.
    """
    game = _started(game)
    game.next_world()
    game.claim(1)
    game.next_world()
    game.claim(1)
    before = game.state()["doneW"]
    assert before["campus"] == []
    game.page.reload()
    game.page.wait_for_function("typeof window.__S === 'function'")
    game.resume()
    assert game.state()["doneW"] == before
    game.assert_clean()


def test_enter_opens_the_stop_you_are_standing_on(game: GamePage) -> None:
    """The line says to tap Enter, so Enter has to be the button's twin."""
    game = _started(game)
    game.walk_to(0, 16)
    game.until("window.__debug().near === 1")
    game.page.evaluate("() => document.body.focus()")
    game.page.keyboard.press("Enter")
    game.page.wait_for_selector("#sheet.on", state="attached")
    assert game.page.text_content("#sheet .screen.on h2")
    game.assert_clean()


def test_a_locked_signpost_says_why_it_is_locked(game: GamePage) -> None:
    game = _started(game)
    game.walk_to(-14.4, 12.8)
    said = game.page.locator("#toast .tst", has_text="opens once").first
    said.wait_for(state="attached", timeout=WAIT_MS)
    assert "Centre of Excellence" in (said.text_content() or "")
    assert game.near() == 0
    game.assert_clean()


def test_the_streak_tile_counts_the_stops_done_today(game: GamePage) -> None:
    """The tile is labelled Streak, so it carries the number the CLI counts."""
    game = _started(game)
    game.claim(1)
    game.claim(2)
    game.until("document.getElementById('k2').textContent === '2'")
    game.assert_clean()


def test_the_terrace_of_the_inn_offers_the_finale(game: GamePage) -> None:
    """At eight of eight the walk back ends at the finale, not at the cafe."""
    game.goto(state={"name": "Tom", "doneW": {"campus": [1, 2, 3, 4, 5, 6, 7, 8]}})
    game.resume()
    game.walk_to(2.8, 5.2)
    game.until("window.__debug().near === 9")
    label = game.page.text_content("#enterbtn") or ""
    assert "Calendar alignment" in label, label
    game.screenshot("hunt1-terrace-finale")
    game.assert_clean()


def test_a_delivered_stop_shows_one_way_back(game: GamePage) -> None:
    """The primary of a delivered stop is never the secondary's label."""
    game = _started(game)
    game.next_world()
    game.claim(1)
    game.open_workstream(1)
    labels = game.page.locator("#sheet .screen.on .row button").all_text_contents()
    assert "Mark as done and unlock the OKR" not in labels, labels
    assert len(labels) == len(set(labels)), labels
    assert labels.count("Back to the island") == 1, labels
    game.page.click("#sheet .screen.on .row button")
    game.page.wait_for_selector("#sheet.on", state="detached")
    game.assert_clean()


def test_the_last_island_ends_the_campaign_rather_than_the_evening(
    game: GamePage,
) -> None:
    """Production is the end of the campaign: no next environment, no hub."""
    game.goto(
        state={
            "name": "Tom",
            "world": "prod",
            "doneW": {"prod": [1, 2, 3, 4, 5, 6, 7, 8]},
        }
    )
    game.resume()
    game.until("window.__debug().near === 9")
    game.page.click("#enterbtn")
    game.page.wait_for_selector("#s-gen.on", state="attached")
    text = game.page.text_content("#s-gen") or ""
    assert "Campaign complete" in text, text
    assert "Next environment" not in text, text
    assert "Come back to the hub" not in (game.page.text_content("#bub-text") or "")
    game.screenshot("hunt1-prod-campaign-complete")
    game.assert_clean()


def test_a_ninth_stop_on_an_island_opens_instead_of_the_island_ending(
    game: GamePage,
) -> None:
    """The fork challenge adds a stop to the island data; it has to be playable."""
    game.goto(
        state={
            "name": "Tom",
            "world": "prod",
            "doneW": {"prod": [1, 2, 3, 4, 5, 6, 7, 8]},
        }
    )
    game.resume()
    game.page.evaluate(
        "() => window.__data().campaign.prod.ws.push("
        "{h: 'Stop 9', n: 'My own stop', d: 'The one I added',"
        " html: '<p>Mine.</p>'})"
    )
    game.open_roadmap()
    game.page.click("#plotlist button:has-text('My own stop')")
    game.page.wait_for_selector("#s-gen.on", state="attached")
    assert game.page.text_content("#s-gen h2") == "My own stop"
    game.page.click("#s-gen button:has-text('Mark as done')")
    game.page.wait_for_function("() => window.__S().doneW.prod.includes(9)")
    game.assert_clean()
