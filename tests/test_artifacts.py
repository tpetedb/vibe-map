"""The island artifacts: open one, press its buttons, see it persist and export."""

from __future__ import annotations

from playwright.sync_api import Page

from tests.conftest import WAIT_MS, GamePage, encode_progress
from vibemap.state import State, decode_code


def _wait_term(page: Page, line: str) -> None:
    page.wait_for_function(
        "t => (document.getElementById('art-term').textContent || '').includes(t)",
        arg=line,
        timeout=WAIT_MS,
    )


def test_cafe_serves_a_status_code_and_is_remembered(game: GamePage) -> None:
    game.goto()
    game.start()
    page = game.page
    assert page.evaluate("window.__artifacts().length") == 21
    page.evaluate("openArtifact('cafe')")
    page.wait_for_selector("#s-artifact.on", state="attached")
    # The terminal types itself out line by line, so wait for the last line.
    page.click("#s-artifact button[data-demo='0']")
    _wait_term(page, "200 OK")
    assert "GET /coffee" in (page.text_content("#art-term") or "")
    page.click("#s-artifact button[data-demo='1']")
    _wait_term(page, "404 Not Found")
    state = page.evaluate("window.__S()")
    assert state["artifacts"] == ["cafe"]
    # the roadmap card and the KPI reflect it
    page.click("#sheet .x")
    assert page.text_content("#k4") == "1"
    game.open_roadmap()
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
    assert page.evaluate("window.__S().artifacts.length") == 21
    page.click("#sheet .x")
    page.evaluate("openNote('Artifacts')")
    page.wait_for_function(
        "() => (document.getElementById('vnote').textContent || '')"
        ".split('found:').length - 1 === 21",
        timeout=WAIT_MS,
    )
    note = page.text_content("#vnote") or ""
    assert note.count("found:") == 21 and "not yet" not in note
    assert not game.errors, game.errors


def test_the_sheet_sets_a_task_with_the_commands_folded_away(game: GamePage) -> None:
    """Every artifact shows Do it for real, its source and the check that judges it."""
    game.goto()
    game.start()
    page = game.page
    page.evaluate("pickDifficulty('hard')")  # commands fold from hard up
    for aid in page.evaluate("window.__artifacts().map(a => a.id)"):
        page.evaluate(f"openArtifact({aid!r})")
        page.wait_for_selector("#s-artifact.on", state="attached")
        real = page.evaluate(f"window.__artifacts().find(a => a.id === {aid!r}).real")
        sheet = page.text_content("#s-artifact") or ""
        assert real["title"] in sheet, aid
        assert f"vibe check --artifact {aid}" in sheet, aid
        assert real["dir"] in sheet, aid
        href = page.get_attribute(f"#s-artifact a[href='{real['doc']['url']}']", "href")
        assert href == real["doc"]["url"], aid
        cmds = page.locator("#s-artifact details.cmds")
        assert cmds.count() == 1, aid
        assert not cmds.first.evaluate("d => d.open"), aid
        assert real["commands"][0] in (cmds.first.text_content() or ""), aid
    page.evaluate("pickDifficulty('normal')")
    page.evaluate("openArtifact('cafe')")
    assert page.locator("#s-artifact details.cmds").first.evaluate("d => d.open")
    game.screenshot("artifact-do-it-for-real")
    assert not game.errors, game.errors


def test_a_progress_code_marks_an_artifact_built_for_real(game: GamePage) -> None:
    game.goto()
    game.start()
    page = game.page
    page.evaluate("openArtifact('well')")
    page.wait_for_selector("#s-artifact.on", state="attached")
    assert "Not built yet" in (page.text_content("#s-artifact") or "")
    page.click("#sheet .x")
    assert "1/8" not in game.import_code(encode_progress(artifacts_built=["well"]))
    assert page.evaluate("window.__S().artifactsBuilt") == ["well"]
    page.click("#sheet .x")
    page.evaluate("openArtifact('well')")
    assert "Built for real" in (page.text_content("#s-artifact") or "")
    # and it travels back out again
    page.evaluate("exportProgress()")
    code = page.input_value("#impcode")
    assert decode_code(code)["artifactsBuilt"] == ["well"]
    st = State(name="Lotte")
    st.merge_code(code)
    assert st.artifacts_built == ["well"]
    assert not game.errors, game.errors
