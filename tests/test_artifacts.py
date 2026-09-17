"""The island artifacts: open one, press its buttons, see it persist and export."""

from __future__ import annotations

from tests.conftest import GamePage
from vibemap.state import State, decode_code


def test_cafe_serves_a_status_code_and_is_remembered(game: GamePage) -> None:
    game.goto()
    game.start()
    page = game.page
    assert page.evaluate("window.__artifacts().length") == 10
    page.evaluate("openArtifact('cafe')")
    page.wait_for_selector("#s-artifact.on", state="attached")
    page.click("#s-artifact button[data-demo='0']")
    page.wait_for_timeout(1800)
    term = page.text_content("#art-term") or ""
    assert "GET /coffee" in term and "200 OK" in term
    page.click("#s-artifact button[data-demo='1']")
    page.wait_for_timeout(1500)
    assert "404 Not Found" in (page.text_content("#art-term") or "")
    state = page.evaluate("window.__S()")
    assert state["artifacts"] == ["cafe"]
    # the roadmap card and the KPI reflect it
    page.click("#sheet .x")
    assert page.text_content("#k4") == "1"
    page.click("#hud button:has-text('Roadmap')")
    page.wait_for_timeout(500)
    assert "found" in (page.text_content("#plotlist") or "")
    # the progress code carries it to the CLI
    page.evaluate("exportProgress()")
    code = page.input_value("#impcode")
    assert "cafe" in decode_code(code)["artifacts"]
    st = State(name="Lotte")
    st.merge_code(code)
    assert st.artifacts == ["cafe"]
    assert not game.errors, game.errors


def test_every_artifact_opens_and_the_vault_note_lists_them(game: GamePage) -> None:
    game.goto()
    game.start()
    page = game.page
    ids = page.evaluate("window.__artifacts().map(a => a.id)")
    for aid in ids:
        page.evaluate(f"openArtifact({aid!r})")
        page.wait_for_selector("#s-artifact.on", state="attached")
        assert page.locator("#s-artifact button[data-demo]").count() >= 1, aid
    assert page.evaluate("window.__S().artifacts.length") == 10
    page.click("#sheet .x")
    page.evaluate("openNote('Artifacts')")
    page.wait_for_timeout(1500)
    note = page.text_content("#vnote") or ""
    assert note.count("found:") == 10 and "not yet" not in note
    assert not game.errors, game.errors
