"""The vault, the tech tree and the finale, through the buttons a player uses.

Every check drives the real entry point: the link under an artifact, the tech
tree button, the date button on the finale screen. The bar is the one the
whole battery keeps, zero page errors, because most of these defects
announced themselves as a red banner rather than as a wrong pixel. The graph
is a canvas, so the two facts it has no DOM for, the selection and where the
nodes landed, are read through the ``window.__vault()`` seam.
"""

from __future__ import annotations

from tests.conftest import GamePage

EIGHT = [1, 2, 3, 4, 5, 6, 7, 8]


def _open_vault(game: GamePage) -> None:
    game.hud_action("#hud button:has-text('Vault')")
    game.page.wait_for_selector("#vault.on", state="attached")
    game.page.wait_for_selector("#vnote h1", state="attached")


def _open_finale(game: GamePage) -> None:
    """The last card of the Roadmap, which only eight delivered stops open."""
    game.open_roadmap()
    game.page.click("#plotlist button:has-text('Calendar alignment')")
    game.page.wait_for_selector("#dates button", state="attached")


def test_every_artifact_vault_link_opens_its_note(game: GamePage) -> None:
    """The links under "In the vault" are data; a title with no note is a bug.

    The walkthrough found eight of them, each one a page error and a vault
    that landed on Tonight instead of the note it promised.
    """
    game.goto()
    game.start()
    page = game.page
    links = page.evaluate(
        "() => window.__artifacts().flatMap(a => a.links.map(l => [a.id, l]))"
    )
    assert len(links) > 20
    for artifact, title in links:
        page.evaluate("t => openNote(t)", title)
        page.wait_for_selector("#vnote h1", state="attached")
        body = page.text_content("#vnote") or ""
        assert "No note by that name" not in body, (
            f"{artifact} links to {title}, which reaches no note"
        )
        assert page.text_content("#vnote h1")
    assert not game.errors, game.errors


def test_the_artifact_sheet_link_opens_the_note_it_names(game: GamePage) -> None:
    """The real click: inspect the bridge, then use the link it prints."""
    game.goto()
    game.start()
    page = game.page
    page.evaluate("openArtifact('bridge')")
    page.wait_for_selector("#s-artifact.on", state="attached")
    link = page.locator("#s-artifact .wl").first
    wanted = link.text_content() or ""
    link.click()
    page.wait_for_selector("#vault.on", state="attached")
    page.wait_for_selector("#vnote h1", state="attached")
    # The bridge links to the MCP topic, whose note is written by hand under
    # the short name, so the heading is the note's own title.
    assert (page.text_content("#vnote h1") or "") in wanted
    assert "No note by that name" not in (page.text_content("#vnote") or "")
    assert not game.errors, game.errors


def test_an_unknown_note_title_says_so_instead_of_throwing(game: GamePage) -> None:
    game.goto()
    game.start()
    page = game.page
    page.evaluate("openNote('No Such Note')")
    page.wait_for_selector("#vnote h1", state="attached")
    assert "No Such Note" in (page.text_content("#vnote h1") or "")
    assert "No note by that name" in (page.text_content("#vnote") or "")
    assert page.evaluate("() => window.__vault().sel") is None
    assert not game.errors, game.errors


def test_grow_mode_unlocks_a_campus_stop_the_theme_renamed(game: GamePage) -> None:
    """Stops 4 to 8 carry the theme's names, so they used to unlock nothing."""
    page = game.page
    page.goto(game.url + "?vault=grow")
    page.wait_for_function("typeof window.__S === 'function'")
    game.start()
    _open_vault(game)
    assert not page.evaluate("() => window.__vault().has('Business continuity')")
    before = page.evaluate("() => window.__vault().unlocked")
    game.close_vault()
    for n in (1, 2, 3, 4):
        game.claim(n)
    _open_vault(game)
    assert page.evaluate("() => window.__vault().has('Business continuity')")
    assert page.evaluate("() => window.__vault().unlocked") > before
    page.evaluate("openNote('Business continuity')")
    page.wait_for_selector("#vnote h1", state="attached")
    assert "Business continuity" in (page.text_content("#vnote h1") or "")
    assert "Not unlocked yet" not in (page.text_content("#vnote") or "")
    assert not game.errors, game.errors


def test_the_tech_tree_keeps_a_locked_note_locked(game: GamePage) -> None:
    """One rule: a locked note opens nowhere, not only from a wikilink."""
    page = game.page
    page.goto(game.url + "?vault=grow")
    page.wait_for_function("typeof window.__S === 'function'")
    game.start()
    _open_vault(game)
    page.click("#vmode")
    page.wait_for_selector("#vtree .tech", state="attached")
    locked = page.locator("#vtree .tech.locked").first
    title = (locked.text_content() or "").strip()
    locked.click()
    page.wait_for_selector("#vnote h1", state="attached")
    body = page.text_content("#vnote") or ""
    assert "Not unlocked yet" in body, title
    assert len(body) < 400, f"the locked note {title} rendered in full"
    assert not game.errors, game.errors


def test_a_wikilink_can_be_reached_and_opened_from_the_keyboard(
    game: GamePage,
) -> None:
    game.goto()
    game.start()
    _open_vault(game)
    page = game.page
    link = page.locator("#vnote .wl:not(.locked)").first
    wanted = link.text_content() or ""
    assert link.get_attribute("role") == "link"
    link.focus()
    assert page.evaluate("() => document.activeElement.dataset.n") == wanted
    page.keyboard.press("Enter")
    page.wait_for_selector("#vnote h1", state="attached")
    assert wanted in (page.text_content("#vnote h1") or "")
    assert page.get_attribute("#vg", "aria-label")
    assert not game.errors, game.errors


def test_a_two_tag_line_renders_as_tags(game: GamePage) -> None:
    game.goto()
    game.start()
    _open_vault(game)
    page = game.page
    page.evaluate("openNote('Bash and shell scripts')")
    page.wait_for_selector("#vnote h1", state="attached")
    assert page.locator("#vnote .tag").count() >= 2
    assert not game.errors, game.errors


def test_a_mentor_role_renders_as_emphasis(game: GamePage) -> None:
    game.goto()
    game.start()
    _open_vault(game)
    page = game.page
    name = page.evaluate("() => window.__data().mentors[0].name")
    page.evaluate("n => openNote(n)", name)
    page.wait_for_selector("#vnote h1", state="attached")
    assert page.locator("#vnote i").count() >= 1
    assert "*" not in (page.text_content("#vnote") or "")
    assert not game.errors, game.errors


def test_the_vault_header_follows_the_graph_and_tree_switch(game: GamePage) -> None:
    game.goto()
    game.start()
    _open_vault(game)
    page = game.page
    assert "tap a node" in (page.text_content("#vcount") or "")
    page.click("#vmode")
    page.wait_for_selector("#vtree .tech", state="attached")
    header = page.text_content("#vcount") or ""
    assert "tap a node" not in header
    assert "topic" in header
    assert not game.errors, game.errors


def test_the_graph_spreads_instead_of_piling_on_the_edges(
    game_desktop: GamePage,
) -> None:
    """Nodes used to be clamped into a fixed canvas and stack along each edge."""
    game = game_desktop
    game.goto()
    game.start()
    _open_vault(game)
    page = game.page
    # The simulation's own alpha is the end of the layout. A sampler over the
    # sum of y calls a slow tick stillness and measures a graph that is still
    # spreading, so how many nodes share a line would depend on how fast the
    # page happens to run. The budget is the simulation's, not the harness's:
    # it decays per animation frame, and a software renderer draws few.
    page.wait_for_function(
        "() => ((window.__debug().vault() || {alpha: 1}).alpha < 0.05)",
        timeout=120_000,
    )
    # Clamping pinned the overflow to the exact border, so a couple of dozen
    # nodes shared one y to the pixel. A settled layout shares none.
    row = page.evaluate(
        "() => {const rows = {};"
        " window.__vault().nodes.forEach(p => {const k = Math.round(p.y);"
        " rows[k] = (rows[k] || 0) + 1});"
        " return Math.max(...Object.values(rows))}"
    )
    assert row <= 3, f"{row} nodes sit on one line"
    game.screenshot("vault-graph-spread")
    assert not game.errors, game.errors


def test_a_finale_date_with_an_apostrophe_is_pickable(game: GamePage) -> None:
    """Config text is data: an apostrophe used to break the inline onclick."""
    game.goto(state={"name": "Lotte", "done": EIGHT, "doneW": {"campus": EIGHT}})
    game.resume()
    page = game.page
    # What a camp writes into config/camp.toml [finale] dates, apostrophe and
    # all, reaches the game as CONFIG.dates.
    page.evaluate(
        "() => {const d = window.__finale().dates; d.length = 0;"
        " d.push(\"Rolinda's birthday, 12 May\", '<b>not a date</b>')}"
    )
    _open_finale(game)
    buttons = page.locator("#dates button")
    assert buttons.count() == 2
    assert (buttons.nth(1).text_content() or "") == "<b>not a date</b>"
    buttons.nth(0).click()
    page.wait_for_function('() => window.__S().date === "Rolinda\'s birthday, 12 May"')
    assert not game.errors, game.errors


def test_only_a_real_date_is_given_the_start_time(game: GamePage) -> None:
    """The last entry of the list is an escape hatch, not a date."""
    game.goto(state={"name": "Lotte", "done": EIGHT, "doneW": {"campus": EIGHT}})
    game.resume()
    _open_finale(game)
    configured = game.page.evaluate("() => window.__finale().dates")
    labels = game.page.locator("#dates button").all_text_contents()
    assert labels and len(labels) == len(configured)
    assert any(not any(c.isdigit() for c in d) for d in configured)
    for raw, label in zip(configured, labels, strict=True):
        wanted = raw + ", from 18:00" if any(c.isdigit() for c in raw) else raw
        assert label == wanted
    assert not game.errors, game.errors


def test_the_finale_message_counts_and_pairs_in_the_camps_words(
    game: GamePage,
) -> None:
    game.goto(
        state={
            "name": "Lotte",
            "done": EIGHT,
            "doneW": {"campus": EIGHT},
            "versions": ["v1"],
            "bridges": {"cal": True},
        }
    )
    game.resume()
    page = game.page
    _open_finale(game)
    page.click("#dates button")
    page.click("#wines button")
    page.wait_for_selector("#msgcard", state="visible")
    message = page.text_content("#msg") or ""
    assert "1 tagged release " in message and "1 tagged releases" not in message
    assert "1 live integration." in message and "1 live integrations" not in message
    wine = page.evaluate("() => window.__finale().pairing === 'wine'")
    assert ("decanted" in message) is wine
    assert not game.errors, game.errors
