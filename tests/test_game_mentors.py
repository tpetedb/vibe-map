"""The mentor encounter in the game: dialogue, exercise, plaque.

The dialogue is walked with the real buttons, the exercise card is read from
the rendered screen, and the plaque only appears for an encounter the CLI
verified, which arrives as a progress code.
"""

from __future__ import annotations

from tests.conftest import GamePage, encode_progress


def _open_mentor(game: GamePage, mentor_id: str) -> None:
    game.open_roadmap()
    game.page.click(f"#s-map button[onclick=\"openMentor('{mentor_id}')\"]")
    game.page.wait_for_selector("#s-mentor.on", state="attached")


def test_the_dialogue_advances_one_exchange_at_a_time(game: GamePage) -> None:
    game.goto()
    game.start()
    _open_mentor(game, "karpathy")
    assert game.page.locator("#mtalk .mturn").count() == 1
    while game.page.locator("#talkmore").count():
        game.page.click("#talkmore")
        game.page.wait_for_timeout(120)
    turns = game.page.locator("#mtalk .mturn").count()
    assert turns == len(
        game.page.evaluate(
            "window.__data().mentors.find(m => m.id === 'karpathy').encounter.dialogue"
        )
    )
    assert game.state()["met"]["karpathy"] == turns
    # Every mentor line carries the link it was paraphrased from.
    assert game.page.locator("#mtalk .cite").count() == turns
    game.screenshot("mentor_encounter", clip_height=860)
    game.assert_clean()


def test_the_exercise_card_names_the_workspace_and_the_check(game: GamePage) -> None:
    game.goto()
    game.start()
    _open_mentor(game, "torvalds")
    text = game.page.text_content("#s-mentor") or ""
    assert "workspace/mentors/torvalds/" in text
    assert "vibe check --mentor torvalds" in text
    assert "Not verified yet" in text
    game.assert_clean()


def test_a_verified_encounter_leaves_a_plaque_on_the_island(game: GamePage) -> None:
    game.goto()
    game.start()
    assert game.page.evaluate("Object.keys(window.__plaques()).length") == 0
    msg = game.import_code(encode_progress(mentors=["cherny", "wu"]))
    assert msg.startswith("Imported"), msg
    assert game.state()["mentors"] == ["cherny", "wu"]
    # Both campus mentors get one, and importing twice does not double them.
    assert sorted(game.page.evaluate("Object.keys(window.__plaques())")) == [
        "cherny",
        "wu",
    ]
    game.import_code(encode_progress(mentors=["cherny"]))
    assert len(game.page.evaluate("Object.keys(window.__plaques())")) == 2
    _open_mentor(game, "cherny")
    assert "Verified" in (game.page.text_content("#s-mentor") or "")
    game.assert_clean()


def test_a_mentor_note_in_the_vault_holds_the_exercise(game: GamePage) -> None:
    game.goto()
    game.start()
    game.page.evaluate("openNote('Geoffrey Hinton')")
    game.page.wait_for_selector("#vault.on", state="attached")
    game.page.wait_for_timeout(300)
    note = game.page.text_content("#vnote") or ""
    assert "Your exercise" in note and "workspace/mentors/hinton/" in note
    assert "vibe check --mentor hinton" in note
    game.close_vault()
    game.assert_clean()


def test_a_plaque_pops_into_view_and_keeps_its_distance(game: GamePage) -> None:
    """The plaque is the advertised consequence, so it has to be visible.

    It arrives with the progress code, grows in like every other new thing on
    the island, and stands the same distance from its mentor whatever the
    world is scaled to.
    """
    game.goto()
    game.start()
    game.import_code(encode_progress(mentors=["cherny"]))
    game.page.wait_for_function(
        "() => (window.__plaques().cherny || {scale: {x: 0}}).scale.x > 0.95",
        timeout=20_000,
    )
    scale = game.page.evaluate("window.__data().scale")
    mentor = next(
        m for m in game.page.evaluate("window.__data().mentors") if m["id"] == "cherny"
    )
    at = game.page.evaluate(
        "() => [window.__plaques().cherny.position.x,"
        " window.__plaques().cherny.position.z]"
    )
    away = ((at[0] - mentor["pos"][0]) ** 2 + (at[1] - mentor["pos"][1]) ** 2) ** 0.5
    assert abs(away - 2.15 * scale) < 0.2, (away, scale)
    game.page.click("#sheet button.x")
    game.walk_to(mentor["pos"][0], mentor["pos"][1] + 3, tol=2.0, steps=250)
    game.frames(4)
    game.screenshot("mentor_plaque_in_view", clip_height=700)
    game.assert_clean()


def _roles(game: GamePage) -> dict:
    return game.page.evaluate("() => window.__data().config.theme")


def test_both_speakers_carry_the_roles_the_theme_gives_them(game: GamePage) -> None:
    """The bubble is the theme's, not the wine night's two job titles."""
    game.goto()
    game.start("Lotte")
    theme = _roles(game)
    game.next_world()
    game.open_workstream(1)
    assert game.page.text_content("#bub-who") == "Rolinda, " + theme["guideRole"]
    game.page.click("#sheet .screen.on .row button:has-text('Back')")
    _open_mentor(game, "olah")
    assert game.page.text_content("#bub-who") == "Tom, " + theme["hostRole"]
    game.assert_clean()


def test_opening_a_mentor_stops_the_line_that_was_typing(game: GamePage) -> None:
    """Rolinda types; a mentor line must not be overwritten mid-sentence."""
    game.goto()
    game.start("Lotte")
    game.walk_to(0, 16)
    game.until("window.__debug().near === 1")
    _open_mentor(game, "cherny")
    line = game.page.text_content("#bub-text") or ""
    game.frames(20)
    assert game.page.text_content("#bub-text") == line, line
    assert "Boris Cherny" in line, line
    game.assert_clean()


def test_the_bubble_does_not_name_a_mentor_from_the_island_you_left(
    game: GamePage,
) -> None:
    game.goto()
    game.start("Lotte")
    _open_mentor(game, "cherny")
    game.page.click("#s-mentor .row button:has-text('Back')")
    game.next_world()
    assert "Boris Cherny" not in (game.page.text_content("#bub-text") or "")
    game.assert_clean()


def test_the_roadmap_says_met_after_a_complete_encounter(game: GamePage) -> None:
    game.goto()
    game.start("Lotte")
    _open_mentor(game, "olah")
    game.page.wait_for_function("() => (window.__S().met || {}).olah >= 1")
    game.page.click("#s-mentor .row button:has-text('Back')")
    game.open_roadmap()
    row = game.page.locator("#s-map .pathrow", has_text="Chris Olah").first
    assert "met" in (row.text_content() or "")
    assert "not met" not in (row.text_content() or "")
    game.assert_clean()


def test_a_strict_camp_is_told_about_the_note_the_command_checks(
    game: GamePage,
) -> None:
    """At hard the same command also checks the mentor note, so the card says so."""
    game.goto()
    game.start("Lotte")
    game.page.evaluate("openSettings()")
    game.page.wait_for_selector("#s-settings.on", state="attached")
    game.page.select_option("#set-difficulty", "hard")
    game.page.wait_for_function("() => document.body.dataset.difficulty === 'hard'")
    _open_mentor(game, "li")
    card = game.page.text_content("#s-mentor .card") or ""
    assert "notes.md" in card, card
    assert "What I learned" in card, card
    game.assert_clean()
