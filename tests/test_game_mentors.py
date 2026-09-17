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
