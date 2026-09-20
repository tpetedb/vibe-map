"""Onboarding: the title form, the difficulty fold, the setup guide, vibe new."""

from __future__ import annotations

import json
import os
import stat
from datetime import date
from pathlib import Path

import pytest
from click.testing import CliRunner

from tests.conftest import GO_BUTTON, ROOT, GamePage
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
        "config/camp.toml",
        "justfile",
        "AGENTS.md",
        "CLAUDE.md",
        ".gitignore",
        ".claude/settings.json",
        ".claude/agents/scorekeeper.md",
        ".agents/skills/camp-progress/SKILL.md",
        ".github/workflows/pages.yml",
        ".github/CODEOWNERS",
        ".devcontainer/devcontainer.json",
        ".devcontainer/setup.sh",
        ".git/HEAD",
    ):
        assert (camp / rel).exists(), rel
    assert (camp / ".claude" / "skills" / "camp-progress").is_symlink()
    assert not (camp / "src").exists() and not (camp / "vibemap").exists()
    assert not (camp / ".agents" / "skills" / "develop-camp").exists()
    assert 'name = "Frank"' in (camp / "config" / "camp.toml").read_text()
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


def _fake_gh(bin_dir: Path, log: Path) -> None:
    """A gh on PATH that records its arguments and succeeds."""
    bin_dir.mkdir(parents=True, exist_ok=True)
    gh = bin_dir / "gh"
    gh.write_text(f'#!/bin/sh\necho "$@" >> "{log}"\n')
    gh.chmod(gh.stat().st_mode | stat.S_IXUSR)


@pytest.mark.parametrize(
    ("flags", "wanted"), [([], "--public"), (["--private"], "--private")]
)
def test_new_github_passes_the_visibility_the_flag_asked_for(
    tmp_path: Path, monkeypatch, flags: list[str], wanted: str
) -> None:
    log = tmp_path / "gh.log"
    _fake_gh(tmp_path / "bin", log)
    monkeypatch.setenv("PATH", f"{tmp_path / 'bin'}{os.pathsep}{os.environ['PATH']}")
    # The push only happens after a first commit, so git needs an identity here.
    for k, v in (
        ("GIT_AUTHOR_NAME", "Camp Test"),
        ("GIT_AUTHOR_EMAIL", "camp@example.com"),
        ("GIT_COMMITTER_NAME", "Camp Test"),
        ("GIT_COMMITTER_EMAIL", "camp@example.com"),
    ):
        monkeypatch.setenv(k, v)
    monkeypatch.chdir(tmp_path)
    out = CliRunner().invoke(
        cli, ["new", "camp", "--name", "Frank", "--github", "you/camp", *flags]
    )
    assert out.exit_code == 0, out.output
    call = log.read_text()
    assert wanted in call, call
    other = "--private" if wanted == "--public" else "--public"
    assert other not in call, call


def test_private_without_github_says_so(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    out = CliRunner().invoke(cli, ["new", "camp", "--private"])
    assert out.exit_code != 0
    assert "--github" in out.output


def test_template_is_in_sync_with_the_product_configuration() -> None:
    from tools.sync_template import stale

    assert stale() == []


def _devcontainer(path: Path) -> dict:
    """Parse a devcontainer.json. Ours stay strict JSON so this is the whole check."""
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize(
    "rel",
    [
        ".devcontainer/devcontainer.json",
        "vibemap/data/template/_devcontainer/devcontainer.json",
    ],
)
def test_devcontainers_declare_only_keys_the_spec_has(rel: str) -> None:
    # An unknown key is ignored in silence, so the set is closed on purpose.
    # https://containers.dev/implementors/json_reference/
    spec = {
        "name",
        "image",
        "features",
        "containerEnv",
        "remoteEnv",
        "remoteUser",
        "containerUser",
        "onCreateCommand",
        "updateContentCommand",
        "postCreateCommand",
        "postStartCommand",
        "postAttachCommand",
        "waitFor",
        "forwardPorts",
        "portsAttributes",
        "otherPortsAttributes",
        "hostRequirements",
        "customizations",
    }
    conf = _devcontainer(ROOT / rel)
    assert set(conf) <= spec, set(conf) - spec
    assert conf["forwardPorts"] == [8000, 7717]
    assert conf["portsAttributes"]["7717"]["label"] == "Chat bridge"
    for attrs in conf["portsAttributes"].values():
        assert set(attrs) <= {
            "label",
            "protocol",
            "onAutoForward",
            "requireLocalPort",
            "elevateIfNeeded",
        }
        assert attrs["onAutoForward"] in {"notify", "openBrowser", "silent", "ignore"}
    assert conf["features"] == {"ghcr.io/devcontainers/features/github-cli:1": {}}
    assert conf["customizations"]["vscode"]["extensions"]


def test_only_the_product_container_downloads_browsers() -> None:
    product = (ROOT / ".devcontainer" / "setup.sh").read_text()
    camp = (
        ROOT / "vibemap" / "data" / "template" / "_devcontainer" / "setup.sh"
    ).read_text()
    assert "playwright install-deps" in product and "--frozen" in product
    assert "playwright" not in camp
    assert "uv tool install" in camp


def test_codeowners_lines_are_a_pattern_and_an_owner() -> None:
    # GitHub reads .github/CODEOWNERS first; a line is a gitignore pattern plus
    # one or more @owners. https://docs.github.com/en/repositories/
    # managing-your-repositorys-settings-and-features/customizing-your-repository/
    # about-code-owners
    for rel in (".github/CODEOWNERS", "vibemap/data/template/_github/CODEOWNERS"):
        lines = [
            ln.split()
            for ln in (ROOT / rel).read_text().splitlines()
            if ln.strip() and not ln.lstrip().startswith("#")
        ]
        assert lines, rel
        assert lines[0][0] == "*", rel
        for parts in lines:
            assert len(parts) >= 2, (rel, parts)
            assert all(o.startswith("@") for o in parts[1:]), (rel, parts)


def test_first_visit_shows_the_steps_and_a_preset_changes_the_walker(
    game: GamePage,
) -> None:
    page = game.goto().page
    steps = page.locator("#onboard .step")
    assert steps.count() == 5
    page.click("#onboard button.choice:has-text('Frank')")
    assert page.input_value("#name") == "Frank"
    page.click("#onboard button.choice:has-text('Hard')")
    page.click("#onboard button.choice:has-text('The full experience')")
    guide = page.inner_text("#ob-setup")
    assert "vibe new ~/vibe-map-frank-" in guide
    assert "vibe difficulty hard" in guide
    assert "vibe name 'Frank'" in guide
    page.click(GO_BUTTON)
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
    page.click(GO_BUTTON)
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
    page.click(GO_BUTTON)
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


def test_the_setup_guide_gives_every_command_it_offers(game: GamePage) -> None:
    """It offered a clone it never printed, and broke a flag across a line."""
    page = game.goto().page
    page.click("#onboard button.choice:has-text('The full experience')")
    page.wait_for_selector("#ob-setup", state="visible")
    guide = page.inner_text("#ob-setup")
    assert "clone below" not in guide, "an offer with no command behind it"
    # Every command a reader is told to type lives in a pre block, which never
    # wraps, so a flag can never arrive as two words.
    flags = page.evaluate(
        """() => [...document.querySelectorAll('#ob-setup')]
             .flatMap(g => [...g.querySelectorAll('code')])
             .filter(c => c.textContent.includes('--github'))
             .map(c => c.parentElement.tagName)"""
    )
    assert flags == ["PRE"], flags
    assert "--github" in guide
    assert game.errors == []


def test_resume_is_offered_only_when_there_is_a_name_to_resume_with(
    game: GamePage,
) -> None:
    """A saved look is not a saved game: start() refuses an empty name."""
    page = game.goto(state={"look": "own", "name": "", "doneW": {"campus": []}}).page
    assert not page.is_visible("#btn-continue")
    page = game.goto(state={"name": "Max", "look": "max", "doneW": {"campus": []}}).page
    assert page.is_visible("#btn-continue")
    # Nothing is done yet, so the five steps stay on screen.
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


# A stop done, so the steps are folded and the resume button is offered.
RETURNING = {"name": "Tom", "look": "own", "done": [1], "doneW": {"campus": [1]}}


def _title_box_holds(page, selector: str) -> bool:
    """Is the element inside the visible part of the scrolling title box?"""
    return bool(
        page.evaluate(
            """sel => { const box = document.querySelector('#title .box');
              const r = document.querySelector(sel).getBoundingClientRect();
              const b = box.getBoundingClientRect();
              return r.top >= b.top - 0.5 && r.bottom <= b.bottom + 0.5; }""",
            selector,
        )
    )


def test_the_go_row_stays_on_screen_when_the_setup_guide_opens(
    game_desktop: GamePage,
) -> None:
    """The row the copy points at is sticky at both ends, so it cannot leave."""
    page = game_desktop.goto().page
    page.click("#onboard button.choice:has-text('The full experience')")
    page.wait_for_selector("#ob-setup", state="visible")
    game_desktop.still("document.querySelector('#title .box').scrollTop")
    assert _title_box_holds(page, "#name"), "the name field scrolled out of the box"
    assert _title_box_holds(page, GO_BUTTON), "Start scrolled out of the box"
    page.fill("#name", "Tom")
    page.click(GO_BUTTON)
    page.wait_for_selector("#title.off", state="attached")
    assert game_desktop.state()["name"] == "Tom"
    game_desktop.screenshot("title-full-experience")
    assert game_desktop.errors == []


def test_the_sticky_row_does_not_cover_the_text_below_it(
    game_desktop: GamePage,
) -> None:
    page = game_desktop.goto(state=RETURNING).page
    overlap = page.evaluate(
        """() => { const go = document.querySelector('#title .row.go');
          const intro = document.getElementById('intro');
          return go.getBoundingClientRect().bottom
            - intro.getBoundingClientRect().top; }"""
    )
    assert overlap <= 0.5, f"the go row prints over the intro by {overlap} px"
    game_desktop.screenshot("title-returning")
    assert game_desktop.errors == []


def test_the_campus_is_covered_and_deaf_until_start(game_desktop: GamePage) -> None:
    """The title is modal: no tab stop, no click and no key reaches the HUD."""
    page = game_desktop.goto().page
    assert not page.is_visible("#hud")
    assert not page.is_visible("#talk")
    for _ in range(4):
        page.keyboard.press("Tab")
        assert page.evaluate(
            "() => document.getElementById('title').contains(document.activeElement)"
        ), "focus reached the campus behind the title"
    page.keyboard.press("c")
    assert not page.evaluate(
        "() => document.getElementById('sheet').classList.contains('on')"
    )
    page.keyboard.press("Meta+k")
    assert not page.evaluate(
        "() => document.getElementById('pal').classList.contains('on')"
    )
    # The same keys work the moment the game has started.
    game_desktop.start("Tom")
    assert page.is_visible("#hud")
    page.keyboard.press("Meta+k")
    page.wait_for_selector("#pal.on", state="attached")
    assert game_desktop.errors == []


def test_enter_in_the_name_field_starts_the_game(game: GamePage) -> None:
    page = game.goto().page
    page.click("#onboard button.choice:has-text('Your own name')")
    page.fill("#name", "Tom")
    page.dispatch_event("#name", "input")
    page.press("#name", "Enter")
    page.wait_for_selector("#title.off", state="attached")
    assert game.state()["name"] == "Tom"
    assert game.errors == []


def test_your_own_name_keeps_a_name_that_was_typed(game: GamePage) -> None:
    page = game.goto().page
    page.fill("#name", "Tom")
    page.dispatch_event("#name", "input")
    page.click("#onboard button.choice:has-text('Your own name')")
    assert page.input_value("#name") == "Tom"
    assert game.state()["name"] == "Tom"
    # A preset's label was never typed, so that one is cleared.
    page.click("#onboard button.choice:has-text('Frank')")
    page.click("#onboard button.choice:has-text('Your own name')")
    assert page.input_value("#name") == ""
    assert game.errors == []


def test_a_returning_player_can_open_the_steps_again(game: GamePage) -> None:
    """ "You can switch to this later" has a later: the steps fold, not vanish."""
    page = game.goto(state=RETURNING).page
    assert not page.is_visible("#onboard")
    page.click("#obfold > summary")
    page.wait_for_selector("#onboard", state="visible")
    page.click("#onboard button.choice:has-text('Just the game')")
    assert game.state()["mode"] == "online"
    assert game.errors == []


def test_the_setup_guide_sends_you_to_the_roadmap_for_sync(game: GamePage) -> None:
    page = game.goto().page
    page.click("#onboard button.choice:has-text('The full experience')")
    guide = page.inner_text("#ob-setup")
    assert "under Roadmap, Sync" in guide, guide
    assert "World, Sync" not in guide, guide
    assert game.errors == []


def test_the_title_form_fits_an_iphone(game_webkit_iphone: GamePage) -> None:
    """Every control of the form is reachable on the smallest screen."""
    page = game_webkit_iphone.goto().page
    assert not page.is_visible("#hud")
    page.click("#onboard button.choice:has-text('The full experience')")
    page.wait_for_selector("#ob-setup", state="visible")
    game_webkit_iphone.still("document.querySelector('#title .box').scrollTop")
    assert _title_box_holds(page, "#name")
    assert _title_box_holds(page, GO_BUTTON)
    assert page.evaluate(
        "() => document.documentElement.scrollWidth <= window.innerWidth + 1"
    ), "the title form scrolls sideways"
    game_webkit_iphone.screenshot("title-iphone")
    page.fill("#name", "Tom")
    page.press("#name", "Enter")
    page.wait_for_selector("#title.off", state="attached")
    assert game_webkit_iphone.errors == []
