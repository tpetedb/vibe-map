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
    assert 'vibe name "Frank"' in guide
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
    page.click("#hud button:has-text('Roadmap')")
    page.wait_for_timeout(500)
    page.click("#s-map button:has-text('Settings')")
    page.select_option("#set-difficulty", "god")
    assert page.locator("details.cmds[open]").count() == 0
    # Folded is never hidden: one click opens the commands of a lesson.
    page.click("#hud button:has-text('Roadmap')")
    page.wait_for_timeout(500)
    page.click("#s-map button:has-text('Setup guide')")
    assert "vibe new ~/vibe-map-max-" in page.inner_text("#s-setup")
    assert game.errors == []


def test_returning_player_sees_resume_first(game: GamePage) -> None:
    page = game.goto(
        state={
            "name": "Rolinda",
            "look": "rolinda",
            "done": [0],
            "doneW": {"campus": [0]},
        }
    ).page
    assert page.is_visible("#btn-continue")
    assert not page.is_visible("#onboard")
    game.resume()
    assert game.state()["look"] == "rolinda"
    assert game.errors == []
