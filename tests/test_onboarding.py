"""Onboarding: the title form, the difficulty fold, the setup guide, vibe new."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from click.testing import CliRunner

from tests.conftest import GamePage
from vibemap.cli import camp_dir_name, cli


def test_camp_dir_name_follows_the_convention() -> None:
    assert (
        camp_dir_name("Tom Peters", date(2026, 9, 17))
        == "vibe-map-tom-peters-2026-09-17"
    )
    assert camp_dir_name("", date(2026, 1, 2)).startswith("vibe-map-")
    assert camp_dir_name("!!", date(2026, 1, 2)) == "vibe-map-player-2026-01-02"
    assert (
        camp_dir_name("Jörg Müller", date(2026, 1, 2))
        == "vibe-map-jorg-muller-2026-01-02"
    )


def test_vibe_new_makes_a_slim_camp_from_the_template(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.chdir(tmp_path)
    out = CliRunner().invoke(cli, ["new", "--name", "Frank"])
    assert out.exit_code == 0, out.output
    camp = tmp_path / f"vibe-map-frank-{date.today().isoformat()}"
    assert camp.is_dir()
    # The three zones and nothing of the engine.
    for rel in (
        "workspace/README.md",
        "vault/Camp/Tonight.md",
        "vibe.toml",
        "justfile",
        "AGENTS.md",
        "CLAUDE.md",
        ".gitignore",
        ".claude/settings.json",
        ".claude/agents/scorekeeper.md",
        ".agents/skills/camp-progress/SKILL.md",
        ".github/workflows/pages.yml",
        ".git/HEAD",
    ):
        assert (camp / rel).exists(), rel
    assert (camp / ".claude" / "skills" / "camp-progress").is_symlink()
    assert not (camp / "src").exists() and not (camp / "vibemap").exists()
    assert not (camp / ".agents" / "skills" / "develop-camp").exists()
    assert 'name = "Frank"' in (camp / "vibe.toml").read_text()
    # Expert in a camp asks for the learner's own tests under workspace/.
    import os
    import subprocess
    import sys

    env = dict(os.environ, VIBE_HOME=str(camp))
    (camp / "workspace" / "game").mkdir(parents=True, exist_ok=True)
    (camp / "workspace" / "game" / "index.html").write_text(
        "<script>let score=0</script>" + "x" * 900
    )
    (camp / "workspace" / "game" / "test_game.py").write_text(
        "def test_ok():\n    assert True\n"
    )
    run = subprocess.run(
        [sys.executable, "-m", "vibemap.cli", "difficulty", "expert"], cwd=camp, env=env
    )
    assert run.returncode == 0
    out = subprocess.run(
        [sys.executable, "-m", "vibemap.cli", "check", "1"],
        cwd=camp,
        env=env,
        capture_output=True,
        text=True,
    )
    assert "no test_*.py" not in out.stdout, out.stdout
    assert "Innovation Hub done" in out.stdout, out.stdout


def test_template_is_in_sync_with_the_product_configuration() -> None:
    from tools.sync_template import stale

    assert stale() == []


def test_first_visit_shows_the_steps_and_a_preset_changes_the_walker(
    game: GamePage,
) -> None:
    page = game.goto().page
    steps = page.locator("#onboard .step")
    assert steps.count() == 4
    page.click("#onboard button.choice:has-text('Frank')")
    assert page.input_value("#name") == "Frank"
    page.click("#onboard button.choice:has-text('Hard')")
    page.click("#onboard button.choice:has-text('The full experience')")
    guide = page.inner_text("#ob-setup")
    assert "vibe new ~/vibe-map-frank-" in guide
    assert "vibe difficulty hard" in guide
    assert "vibe name 'Frank'" in guide
    page.click("text=Kick off the engagement")
    page.wait_for_selector("#title.off", state="attached")
    s = game.state()
    assert s["name"] == "Frank" and s["look"] == "frank"
    assert s["settings"]["difficulty"] == "hard" and s["mode"] == "full"
    assert page.evaluate("document.body.dataset.difficulty") == "hard"
    assert game.errors == []


def test_commands_fold_at_hard_and_open_at_beginner(game: GamePage) -> None:
    page = game.goto().page
    total = page.locator("details.cmds").count()
    assert total >= 30
    assert page.locator("details.cmds[open]").count() == total
    page.click("#onboard button.choice:has-text('Expert')")
    assert page.locator("details.cmds[open]").count() == 0
    page.click("#onboard button.choice:has-text('Beginner')")
    assert page.locator("details.cmds[open]").count() == total
    game.start("Max")
    game.open_roadmap()
    page.click("#s-map button:has-text('Settings')")
    page.select_option("#set-difficulty", "god")
    assert page.locator("details.cmds[open]").count() == 0
    # Folded is never hidden: one click opens the commands of a lesson.
    game.open_roadmap()
    page.click("#s-map button:has-text('Setup guide')")
    assert "vibe new ~/vibe-map-max-" in page.inner_text("#s-setup")
    assert game.errors == []


def test_returning_player_sees_resume_first(game: GamePage) -> None:
    # Stop numbers run 1 to 8; the game never writes a 0, so neither does the seed.
    page = game.goto(
        state={
            "name": "Rolinda",
            "look": "rolinda",
            "done": [1],
            "doneW": {"campus": [1]},
        }
    ).page
    assert page.is_visible("#btn-continue")
    assert not page.is_visible("#onboard")
    game.resume()
    assert game.state()["look"] == "rolinda"
    assert game.errors == []


def test_an_empty_name_refuses_to_start(game: GamePage) -> None:
    """The placeholder is a placeholder; it never becomes the player's name."""
    page = game.goto().page
    page.click("#onboard button.choice:has-text('Your own name')")
    page.click("text=Kick off the engagement")
    # Nothing to wait for: the hint is the only thing an empty name produces.
    page.wait_for_selector("#namehint:has-text('Type your name first')")
    assert page.is_visible("#title")
    assert not page.locator("#title").evaluate("e => e.classList.contains('off')")
    assert "Type your name first" in (page.text_content("#namehint") or "")
    assert game.state()["name"] == ""
    assert "your_name" not in (page.text_content("#hud-name") or "")
    assert "Evening 1" in (page.text_content("#hud-name") or "")
    page.fill("#name", "Lotte")
    page.dispatch_event("#name", "input")
    page.click("text=Kick off the engagement")
    page.wait_for_selector("#title.off", state="attached")
    assert game.state()["name"] == "Lotte"
    assert game.errors == []


def test_a_name_with_a_quote_is_shell_quoted(game: GamePage) -> None:
    page = game.goto().page
    page.click("#onboard button.choice:has-text('Your own name')")
    page.fill("#name", 'Lo"tte')
    page.dispatch_event("#name", "input")
    page.click("#onboard button.choice:has-text('The full experience')")
    guide = page.inner_text("#ob-setup")
    assert """vibe name 'Lo"tte'""" in guide, guide
    page.fill("#name", "O'Brien")
    page.dispatch_event("#name", "input")
    guide = page.inner_text("#ob-setup")
    assert "vibe name 'O'\\''Brien'" in guide, guide
    assert game.errors == []


def test_accents_fold_into_the_camp_directory(game: GamePage) -> None:
    page = game.goto().page
    page.click("#onboard button.choice:has-text('Your own name')")
    page.fill("#name", "J\u00f6rg \u00c5berg")
    page.dispatch_event("#name", "input")
    page.click("#onboard button.choice:has-text('The full experience')")
    guide = page.inner_text("#ob-setup")
    assert "vibe new ~/vibe-map-jorg-aberg-" in guide, guide
    assert game.errors == []


def test_the_setup_guide_renders_below_the_go_row(game: GamePage) -> None:
    page = game.goto().page
    page.click("#onboard button.choice:has-text('The full experience')")
    page.wait_for_selector("#ob-setup", state="visible")
    order = page.evaluate(
        """() => { const go = document.querySelector('#title .row.go');
          const setup = document.getElementById('ob-setup');
          return go.compareDocumentPosition(setup)
            & Node.DOCUMENT_POSITION_FOLLOWING ? 'after' : 'before'; }"""
    )
    assert order == "after"
    assert page.is_visible("#ob-setup")
    assert game.errors == []


def test_a_chosen_look_alone_offers_resume(game: GamePage) -> None:
    page = game.goto(state={"name": "Max", "look": "max", "doneW": {"campus": []}}).page
    assert page.is_visible("#btn-continue")
    # Nothing is done yet, so the four steps stay on screen.
    assert page.is_visible("#onboard")
    game.resume()
    assert game.state()["look"] == "max"
    assert game.errors == []


def test_the_title_counts_eight_workstreams(game: GamePage) -> None:
    page = game.goto().page
    intro = page.text_content("#intro") or ""
    assert "six" not in intro.lower(), intro
    assert "eight" in intro.lower(), intro


def test_workstreams_seven_and_eight_fold_their_commands(game: GamePage) -> None:
    page = game.goto().page
    for sid in ("#s-7", "#s-8"):
        assert page.locator(f"{sid} details.cmds").count() >= 3, sid
    page.click("#onboard button.choice:has-text('Expert')")
    assert page.locator("#s-7 details.cmds[open]").count() == 0
    assert page.locator("#s-8 details.cmds[open]").count() == 0
    assert game.errors == []
