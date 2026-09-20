"""The rest of the CLI: exit codes, help that matches behaviour, no tracebacks.

Every test runs the real command in a camp made by `vibe new`, because the
defects these guard against are a flag that is read but never used, an exit
code a recipe reports as a failure, and a traceback reaching the learner.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest
from click.testing import CliRunner

from vibemap import campaign
from vibemap.cli import cli
from vibemap.council import MAX_MENTORS, seated
from vibemap.state import State


def _run(camp: Path, *args: str, stdin: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "vibemap.cli", *args],
        cwd=camp,
        env=dict(os.environ, VIBE_HOME=str(camp), COLUMNS="200"),
        input=stdin,
        capture_output=True,
        text=True,
    )


@pytest.fixture
def camp(tmp_path: Path) -> Path:
    here = tmp_path / "camp"
    made = CliRunner().invoke(cli, ["new", str(here), "--name", "Tom"])
    assert made.exit_code == 0, made.output
    return here


def _flat(text: str) -> str:
    """The output as one line of words: a narrow console wraps a long message."""
    return " ".join(text.split())


def _a_camp_with_history(camp: Path) -> None:
    """A commit of the camp's own, without asking the machine for an identity.

    `vibe new` commits only where git already knows a name and an email, which
    a fresh CI runner does not, so the tests that read a history make one.
    """
    git = ["git", "-c", "user.name=Camp", "-c", "user.email=camp@example.com"]
    subprocess.run([*git, "init", "-q"], cwd=camp, check=True)
    subprocess.run([*git, "add", "-A"], cwd=camp, check=True)
    subprocess.run(
        [*git, "commit", "-q", "--allow-empty", "-m", "the camp"], cwd=camp, check=True
    )


def _state(camp: Path) -> State:
    return State.load(camp / ".vibe" / "state.json")


def _stub_provider(camp: Path, script: str) -> dict[str, str]:
    """A fake `claude` on PATH: the provider call is the entry point under test."""
    binaries = camp / "stub-bin"
    binaries.mkdir(exist_ok=True)
    fake = binaries / "claude"
    fake.write_text(f"#!/usr/bin/env python3\n{script}\n", encoding="utf-8")
    fake.chmod(0o755)
    return dict(
        os.environ,
        VIBE_HOME=str(camp),
        COLUMNS="200",
        PATH=f"{binaries}{os.pathsep}{os.environ['PATH']}",
    )


# ---- the progress grid ---------------------------------------------------------


def test_the_status_grid_marks_the_next_stop_and_prints_its_legend(
    camp: Path,
) -> None:
    out = _run(camp, "status")
    assert out.returncode == 0, out.stdout
    assert ">" in _flat(out.stdout) and "next" in _flat(out.stdout)
    assert "to do" in _flat(out.stdout)


def test_a_forced_claim_draws_an_i_and_the_legend_explains_it(camp: Path) -> None:
    assert _run(camp, "done", "1", "x", "--force").returncode == 0
    out = _run(camp, "status")
    assert "claimed, not verified" in _flat(out.stdout), out.stdout
    assert "pays the other half" in _flat(out.stdout)


def test_the_status_table_and_the_tui_map_read_the_same_marks() -> None:
    st = State(name="Tom")
    st.mark_done("campus", 1, xp=10)
    marks = campaign.stop_marks(st, "campus")
    assert marks[0] == "claimed" and marks[1] == "next" and marks[2] == "todo"
    assert set(campaign.MARKS) == {"done", "claimed", "next", "todo"}
    assert [g for g, _ in campaign.MARKS.values()] == ["x", "i", ">", "."]


def test_the_campaign_says_how_many_stops_an_evening_has(camp: Path) -> None:
    stops = campaign.stop_count("campus")
    out = _run(camp, "check", str(stops + 1))
    assert out.returncode == 1
    assert f"workstream is 1 to {stops}" in _flat(out.stdout)
    assert campaign.total_stops() == sum(
        campaign.stop_count(w) for w in campaign.evenings()
    )


# ---- check: one target at a time -----------------------------------------------


def test_two_targets_are_refused_instead_of_running_the_first(camp: Path) -> None:
    out = _run(camp, "check", "--mentor", "cherny", "--artifact", "cafe")
    assert out.returncode == 1, out.stdout
    assert "pick one of --mentor, --artifact" in _flat(out.stdout)
    assert "Boris Cherny" not in _flat(out.stdout)


@pytest.mark.parametrize("flag", ["--mentor", "--artifact", "--topic"])
def test_an_empty_target_is_refused_like_an_unknown_one(camp: Path, flag: str) -> None:
    out = _run(camp, "check", flag, "")
    assert out.returncode == 1, out.stdout
    assert "Innovation Hub" not in _flat(out.stdout)
    assert "unknown" in _flat(out.stdout)


# ---- check --fork --------------------------------------------------------------


def test_one_fork_challenge_says_what_it_proved_and_claims_nothing(
    camp: Path,
) -> None:
    assert _run(camp, "fork").returncode == 0
    out = _run(camp, "check", "--fork", "exists")
    assert out.returncode == 0, out.stdout
    assert "exists passes" in _flat(out.stdout)
    assert "your fork builds and is yours" not in _flat(out.stdout)
    assert not _state(camp).is_done("prod", 6)


def test_the_four_fork_challenges_claim_the_forking_stop(camp: Path) -> None:
    from tools.script_camp import script_fork

    script_fork(camp)
    out = _run(camp, "check", "--fork", "all")
    assert out.returncode == 0, out.stdout + out.stderr
    assert "your fork builds and is yours" in _flat(out.stdout)
    st = _state(camp)
    assert st.is_done("prod", 6) and st.is_verified("prod", 6)
    # Running it again re-checks and says so, instead of paying twice.
    again = _run(camp, "check", "--fork", "all")
    assert again.returncode == 0
    assert _state(camp).xp == st.xp


# ---- XP is paid once -----------------------------------------------------------


def _passing_game(camp: Path) -> None:
    page = camp / "workspace" / "game" / "index.html"
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(
        "<!doctype html><html><head><title>Catch</title></head><body>"
        "<canvas id=c width=400 height=300></canvas>"
        "<script>let score=0;function loop(){score++;"
        "requestAnimationFrame(loop);}loop();</script>"
        + "<p>a real page with plenty of words in it</p>" * 40
        + "</body></html>",
        encoding="utf-8",
    )


def test_raising_the_difficulty_does_not_re_pay_a_verified_stop(camp: Path) -> None:
    _passing_game(camp)
    assert _run(camp, "check", "1").returncode == 0
    paid = _state(camp).xp
    assert _run(camp, "difficulty", "hard").returncode == 0
    out = _run(camp, "check", "1")
    assert out.returncode == 0, out.stdout
    assert "claimed without a check" not in _flat(out.stdout)
    assert _state(camp).xp == paid


def test_a_stop_claimed_without_a_check_is_still_topped_up(camp: Path) -> None:
    assert _run(camp, "done", "1", "x", "--force").returncode == 0
    half = _state(camp).xp
    _passing_game(camp)
    out = _run(camp, "check", "1")
    assert "claimed without a check" in _flat(out.stdout), out.stdout
    assert _state(camp).xp > half


# ---- hints ---------------------------------------------------------------------


def test_full_hints_and_short_hints_are_not_the_same_text(camp: Path) -> None:
    from vibemap.cli import _hint_line

    hint = "workspace/jobs/: the script, and log.csv. Run it twice."
    assert _hint_line(hint, "full") == hint
    assert _hint_line(hint, "short") == "workspace/jobs/: the script, and log.csv."
    # A one-sentence hint has no tail to drop, so both spellings keep it whole.
    assert _hint_line("one line only", "short") == "one line only"
    assert _run(camp, "difficulty", "beginner").returncode == 0
    assert "hint" in _flat(_run(camp, "check", "8").stdout)


# ---- council -------------------------------------------------------------------


def test_the_council_takes_the_mentors_of_the_island_you_are_on() -> None:
    st = State(name="Tom")
    here, _ = seated(st, [])
    assert {m["world"] for m in here} == {"campus"}
    for n in range(1, campaign.stop_count("campus") + 1):
        st.mark_done("campus", n, xp=1)
    later, dropped = seated(st, [])
    assert {m["world"] for m in later} == {"winter"}
    assert len(later) == MAX_MENTORS and dropped


def test_the_council_says_who_did_not_fit_at_the_table(camp: Path) -> None:
    ids = "cherny,wu,karpathy,lecun,hinton,li,sutton"
    out = _run(camp, "council", "z", "-m", ids, "--dry-run")
    assert out.returncode == 0, out.stdout
    assert f"the council seats {MAX_MENTORS}" in _flat(out.stdout)
    assert out.stdout.count("--- ") == MAX_MENTORS
    assert f"at most {MAX_MENTORS}" in _flat(_run(camp, "council", "--help").stdout)


def test_the_council_refuses_a_question_that_is_not_there(camp: Path) -> None:
    out = _run(camp, "council", "   ", "--dry-run")
    assert out.returncode == 1, out.stdout
    assert "say what the council is about" in _flat(out.stdout)
    assert not list((camp / "vault" / "Camp").glob("Council*.md"))


# ---- explain -------------------------------------------------------------------


def test_explain_escapes_what_the_provider_wrote(camp: Path) -> None:
    _a_camp_with_history(camp)
    env = _stub_provider(camp, "print('[core] and [/b] are not markup')")
    out = subprocess.run(
        [sys.executable, "-m", "vibemap.cli", "explain", "-n", "1"],
        cwd=camp,
        env=env,
        capture_output=True,
        text=True,
    )
    assert out.returncode == 0, out.stdout + out.stderr
    assert "MarkupError" not in out.stderr
    assert "[core]" in _flat(out.stdout) and "[/b]" in _flat(out.stdout)


def test_explain_diffs_from_the_first_commit_when_the_history_is_shorter(
    camp: Path,
) -> None:
    _a_camp_with_history(camp)
    env = _stub_provider(
        camp,
        "import sys, pathlib\n"
        "pathlib.Path('prompt.txt').write_text(sys.argv[-1], encoding='utf-8')\n"
        "print('ok')",
    )
    out = subprocess.run(
        [sys.executable, "-m", "vibemap.cli", "explain", "-n", "3"],
        cwd=camp,
        env=env,
        capture_output=True,
        text=True,
    )
    assert out.returncode == 0, out.stdout + out.stderr
    assert "shorter than 3 commits" in _flat(out.stdout)
    prompt = (camp / "prompt.txt").read_text(encoding="utf-8")
    assert "DIFF (truncated):" in prompt
    # The defect was an empty diff section, so what matters is that the prompt
    # carries a real one; which files reach it depends on where git truncates.
    body = prompt.split("DIFF (truncated):")[1]
    assert "diff --git" in body and len(body.strip()) > 500


@pytest.mark.parametrize("n", ["0", "-5"])
def test_explain_blames_the_argument_not_the_repository(camp: Path, n: str) -> None:
    out = _run(camp, "explain", "-n", n)
    assert out.returncode == 2, out.stdout + out.stderr
    assert "no git history" not in _flat(out.stdout)
    assert "--commits" in out.stderr


# ---- news ----------------------------------------------------------------------


@pytest.mark.parametrize("limit", ["0", "-1"])
def test_a_news_limit_below_one_is_refused_before_anything_is_written(
    camp: Path, limit: str
) -> None:
    out = _run(camp, "news", "--limit", limit, "--dry-run")
    assert out.returncode == 2, out.stdout + out.stderr
    assert "--limit" in out.stderr
    assert not (camp / "vault" / "Camp" / "News.md").exists()


# ---- scores --------------------------------------------------------------------


def test_the_day_one_state_of_the_scores_is_not_a_failed_recipe(camp: Path) -> None:
    out = _run(camp, "scores")
    assert out.returncode == 0, out.stdout
    assert "no scores yet" in _flat(out.stdout)


# ---- toolbelt ------------------------------------------------------------------


def test_an_unknown_tool_is_one_line_and_not_a_traceback(camp: Path) -> None:
    out = _run(camp, "toolbelt", "--install", "bogus", "--dry-run")
    assert out.returncode == 1, out.stdout
    assert "Traceback" not in out.stderr
    assert "unknown tool 'bogus'" in _flat(out.stdout)


def test_a_tier_with_nothing_missing_says_so(camp: Path) -> None:
    # A satisfied tier printed nothing at all, which reads like a dead command.
    out = _run(camp, "toolbelt", "--install", "missing", "--tier", "provider")
    assert out.returncode == 0, out.stdout
    assert out.stdout.strip()


# ---- play, dashboard, start ----------------------------------------------------


def _without_an_opener(camp: Path) -> dict[str, str]:
    return dict(os.environ, VIBE_HOME=str(camp), COLUMNS="200", PATH="/nonexistent")


@pytest.mark.parametrize("command", [["play"], ["dashboard"]])
def test_opening_something_where_there_is_no_opener_prints_it(
    camp: Path, command: list[str]
) -> None:
    out = subprocess.run(
        [sys.executable, "-m", "vibemap.cli", *command],
        cwd=camp,
        env=_without_an_opener(camp),
        capture_output=True,
        text=True,
    )
    assert out.returncode == 0, out.stdout + out.stderr
    assert "FileNotFoundError" not in out.stderr
    assert "open it yourself" in _flat(out.stdout)


def test_play_offline_without_a_network_says_so_and_falls_back(camp: Path) -> None:
    env = dict(
        os.environ,
        VIBE_HOME=str(camp),
        COLUMNS="200",
        PATH="/nonexistent",
        # No proxy can be reached, so urlretrieve fails the way a plane does.
        https_proxy="http://127.0.0.1:1",
        http_proxy="http://127.0.0.1:1",
    )
    out = subprocess.run(
        [sys.executable, "-m", "vibemap.cli", "play", "--offline"],
        cwd=camp,
        env=env,
        capture_output=True,
        text=True,
    )
    assert out.returncode == 0, out.stdout + out.stderr
    assert "Traceback" not in out.stderr
    assert "no copy to cache" in _flat(out.stdout)
    assert not (camp / ".vibe" / "vibe-map.html").exists()


def test_start_without_a_terminal_says_so_instead_of_hanging(camp: Path) -> None:
    out = _run(camp, "start")
    assert out.returncode == 1, out.stdout
    assert "needs a terminal" in _flat(out.stdout)


# ---- pet -----------------------------------------------------------------------


def test_the_gallery_refuses_to_be_a_write(camp: Path) -> None:
    out = _run(camp, "pet", "--all", "--species", "dog")
    assert out.returncode == 1, out.stdout
    assert "--all only shows the gallery" in _flat(out.stdout)
    toml = tomllib.loads((camp / "config" / "camp.toml").read_text(encoding="utf-8"))
    assert toml["pet"]["species"] == ""


def test_an_imported_companion_lands_in_camp_toml(camp: Path) -> None:
    st = State(name="Tom")
    st.pet = "crab"
    out = _run(camp, "import", st.to_code())
    assert out.returncode == 0, out.stdout + out.stderr
    toml = tomllib.loads((camp / "config" / "camp.toml").read_text(encoding="utf-8"))
    assert toml["pet"]["species"] == "crab" and toml["pet"]["enabled"] is True


# ---- fork ----------------------------------------------------------------------


def test_force_says_what_it_deletes_and_waits_for_an_answer(camp: Path) -> None:
    assert _run(camp, "fork").returncode == 0
    marker = camp / "workspace" / "forks" / "vibe-map" / "src" / "config" / "mine.js"
    marker.write_text("// my own\n", encoding="utf-8")
    refused = _run(camp, "fork", "--force", stdin="n\n")
    assert refused.returncode == 1, refused.stdout
    assert "the four fork challenges start again" in _flat(refused.stdout)
    assert marker.exists()
    agreed = _run(camp, "fork", "--force", stdin="y\n")
    assert agreed.returncode == 0, agreed.stdout + agreed.stderr
    assert not marker.exists()


# ---- the vault stays reachable -------------------------------------------------


def test_news_leaves_no_orphan_in_the_vault(camp: Path) -> None:
    feed = camp / "feed.xml"
    feed.write_text(
        '<?xml version="1.0"?><rss version="2.0"><channel><title>t</title>'
        "<item><title>One</title><link>https://example.test/a</link>"
        "<description>a line</description></item></channel></rss>",
        encoding="utf-8",
    )
    toml = camp / "config" / "camp.toml"
    toml.write_text(
        toml.read_text(encoding="utf-8").replace(
            "feeds = []", f'feeds = ["{feed.as_uri()}"]'
        ),
        encoding="utf-8",
    )
    out = _run(camp, "news", "--limit", "5")
    assert out.returncode == 0, out.stdout + out.stderr
    assert (camp / "vault" / "Camp" / "News.md").exists()
    lint = _run(camp, "vault", "lint")
    assert lint.returncode == 0, lint.stdout
    assert "orphan" not in _flat(lint.stdout)
    assert json.loads((camp / ".vibe" / "news.json").read_text(encoding="utf-8"))[
        "items"
    ]
