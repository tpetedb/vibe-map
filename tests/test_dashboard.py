"""The terminal dashboard: the numbers, the report, and the tokens it shares."""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from click.testing import CliRunner
from playwright.sync_api import Browser

from tests.conftest import OUT, ROOT
from vibemap import dashboard
from vibemap.cli import cli
from vibemap.config import DIFFICULTIES
from vibemap.palette import CSS_TOKENS, css_tokens
from vibemap.quests import XP_BASE
from vibemap.state import CheckRecord, State


def _state() -> State:
    """Three days of claims, one check, one mentor, one artifact built."""
    st = State(name="Lotte")
    today = dt.date.today()
    for i, n in enumerate((1, 2, 3)):
        at = dt.datetime.combine(
            today - dt.timedelta(days=2 - i), dt.time(20, 30)
        ).isoformat(timespec="minutes")
        st.mark_done("campus", n, note=f"stop {n}", xp=100)
        st.log[-1].at = at
    st.mark_done("winter", 1, xp=100)
    st.checks["campus:3"] = CheckRecord(ok=True, passed=["scores.csv"])
    st.mentors.append("karpathy")
    st.artifacts.extend(["cache-fountain", "well"])
    st.artifacts_built.append("cache-fountain")
    st.badges.append("first-ship")
    return st


def test_events_keep_the_shape_the_game_uses() -> None:
    events = dashboard.events_from_state(_state())
    assert events, "a state with a log has events"
    dated = [e.ts for e in events if e.ts is not None]
    assert dated == sorted(dated)
    assert [e.ts is None for e in events] == sorted(e.ts is None for e in events)
    first = events[0].as_dict()
    assert set(first) >= {"ts", "kind", "id", "world"}
    assert {e.kind for e in events} >= {"claim", "check", "verified", "built"}


def test_a_mentor_carries_the_time_its_check_recorded() -> None:
    """R16: a verified mentor borrowed the last claim's clock; now it has none."""
    st = _state()
    events = dashboard.events_from_state(st)
    verified = next(e for e in events if e.kind == "verified")
    assert verified.ts is None, "nothing verified it here, so there is no time"
    assert "ts" not in verified.as_dict()
    # A mentor the CLI verified files a check record; that is its time.
    at = "2026-01-02T03:04"
    st.checks["mentor:karpathy"] = CheckRecord(ok=True, at=at)
    events = dashboard.events_from_state(st)
    verified = next(e for e in events if e.kind == "verified")
    assert verified.ts == dt.datetime.fromisoformat(at)
    # The encounter's record is that one event, never a second "check" line.
    assert [e.id for e in events if e.kind == "check"] == ["3"]


def test_an_empty_scores_file_reads_as_no_runs(tmp_path: Path) -> None:
    """R13: an empty CSV raised polars NoDataError out of `vibe dashboard`."""
    scores = tmp_path / "workspace" / "data"
    scores.mkdir(parents=True)
    (scores / "scores.csv").write_text("", encoding="utf-8")
    data = dashboard.numbers(_state(), tmp_path)
    assert data["scores"]["runs"] == 0
    assert "No runs yet" in dashboard.render(data)


def test_the_report_names_a_badge_the_way_the_terminal_does(tmp_path: Path) -> None:
    """R17: the card printed the raw id."""
    st = _state()
    st.badges.append("first-light")
    html = dashboard.render(dashboard.numbers(st, tmp_path))
    assert "First light" in html and ">first-light<" not in html


def test_the_stops_sparkline_counts_stops(tmp_path: Path) -> None:
    """R15: it plotted every event, so it matched the streak line exactly."""
    data = dashboard.numbers(_state(), tmp_path)
    assert sum(data["claims_per_day"]) < sum(data["per_day"])
    # Neither line is the activity line any more: a check is activity, not a
    # stop delivered and not a streak day.
    assert data["claims_per_day"] != data["per_day"]
    assert data["delivered_per_day"] != data["per_day"]
    html = dashboard.render(data)
    assert "Stops delivered per day, last seven days:" in html
    assert 'aria-label="Last seven days"' not in html, "a spark states its reading"


def test_a_player_name_is_cut_before_it_is_escaped() -> None:
    """R14: a cut after escaping lands inside an entity."""
    bars = dashboard.score_bars(
        {"scores": {"players": [{"player": "Bob <b> and Jerry", "best": 9, "runs": 1}]}}
    )
    assert "Bob &lt;b&gt; and" in bars
    assert "&lt;b&gt;" in bars and "&lt;b&gt<" not in bars


def test_the_panel_and_the_report_share_their_definitions() -> None:
    """One XP rule and one streak behind one label, in both languages."""
    js = (ROOT / "src" / "game" / "89-dashboard.js").read_text(encoding="utf-8")
    base = re.search(r"const DASH_XP_BASE=(\d+);", js)
    assert base and int(base.group(1)) == XP_BASE
    table = re.search(r"const DASH_XP_MULT=\{(.+?)\};", js)
    assert table
    in_game = dict(
        (m.group(1), float(m.group(2)))
        for m in re.finditer(r"(\w+):([\d.]+)", table.group(1))
    )
    assert in_game == {k: v.xp_multiplier for k, v in DIFFICULTIES.items()}
    kinds = re.search(r"const DASH_DELIVERED=\[(.+?)\];", js)
    assert kinds and re.findall(r'"(\w+)"', kinds.group(1)) == list(dashboard.DELIVERED)


def test_numbers_are_derived_from_the_state(tmp_path: Path) -> None:
    data = dashboard.numbers(_state(), tmp_path)
    assert data["stops"] == 4 and data["stops_total"] == 32
    assert data["per_island"]["campus"] == 3 and data["per_island"]["winter"] == 1
    assert data["xp"] == 400 and data["mentors"] == 1
    assert data["artifacts"] == 2 and data["artifacts_built"] == 1
    assert data["checks"] == 1 and data["checks_green"] == 1
    assert data["streak"] >= 1
    # The line never contradicts the tile: both come from the same log.
    assert sum(data["xp_day"].values()) == data["xp"]
    assert len(data["days"]) == 7 and len(data["per_day"]) == 7
    assert data["scores"]["runs"] == 0, "no scores.csv in an empty camp"
    assert data["notes"] == 0


def test_an_empty_camp_renders_without_charts_it_cannot_draw(tmp_path: Path) -> None:
    html = dashboard.render(dashboard.numbers(State(), tmp_path))
    assert "dash-empty" in html
    assert "0<span" in html or ">0<" in html


def test_the_report_is_one_self_contained_file(tmp_path: Path) -> None:
    html = dashboard.render(dashboard.numbers(_state(), tmp_path))
    assert "<script" not in html, "the report is data, not a program"
    assert "http://" not in html and "https://" not in html, "no CDN, no fetch"
    assert html.count("<svg") >= 6
    assert 'lang="en"' in html and 'role="img"' in html
    assert "viewport" in html


def test_the_report_uses_the_palette_tokens(tmp_path: Path) -> None:
    html = dashboard.render(dashboard.numbers(_state(), tmp_path))
    assert css_tokens() in html
    # Below the token block a colour is referenced, never respelled.
    body = html.split("</style>", 1)[1]
    assert not re.search(r"#[0-9A-Fa-f]{6}", body), "a raw colour escaped the tokens"


def test_the_tokens_are_the_ones_the_game_ships() -> None:
    """One design system: the CSS the CLI generates equals the game's :root."""
    style = (ROOT / "src" / "style.css").read_text(encoding="utf-8")
    root = style.split(":root{", 1)[1].split("}", 1)[0]
    declared = dict(
        (m.group(1), m.group(2).strip())
        for m in re.finditer(r"--([a-z0-9-]+)\s*:\s*([^;]+);", root)
    )
    for name, value in CSS_TOKENS.items():
        assert name in declared, f"src/style.css has no --{name}"
        assert declared[name] == value, f"--{name} differs from src/style.css"


def test_the_command_writes_the_report(tmp_path: Path) -> None:
    camp = tmp_path / "camp"
    runner = CliRunner()
    assert runner.invoke(cli, ["new", str(camp), "--name", "Tom"]).exit_code == 0
    out = subprocess.run(
        [sys.executable, "-m", "vibemap.cli", "dashboard", "--no-open"],
        cwd=camp,
        env=dict(os.environ, VIBE_HOME=str(camp), COLUMNS="200"),
        capture_output=True,
        text=True,
    )
    assert out.returncode == 0, out.stderr
    report = camp / "workspace" / "dashboard.html"
    assert report.exists(), out.stdout
    assert "Wrote" in out.stdout
    assert "<svg" in report.read_text(encoding="utf-8")
    numbers = subprocess.run(
        [sys.executable, "-m", "vibemap.cli", "dashboard", "--json"],
        cwd=camp,
        env=dict(os.environ, VIBE_HOME=str(camp), COLUMNS="200"),
        capture_output=True,
        text=True,
    )
    data = json.loads(numbers.stdout)
    assert data["stops"] == 0 and data["stops_total"] == 32


def test_the_report_renders_in_a_browser(chromium: Browser, tmp_path: Path) -> None:
    """The page a learner double-clicks: no errors, no sideways scroll on a phone."""
    OUT.mkdir(parents=True, exist_ok=True)
    report = dashboard.write(dashboard.numbers(_state(), ROOT), OUT / "report.html")
    context = chromium.new_context(viewport={"width": 393, "height": 852})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.goto(report.as_uri())
    assert page.locator(".tile").count() == 8
    assert page.locator(".ring").count() == 4
    overflow = page.evaluate(
        "() => document.documentElement.scrollWidth"
        " - document.documentElement.clientWidth"
    )
    assert overflow <= 0, f"horizontal overflow of {overflow}px"
    page.screenshot(path=str(OUT / "report_phone.png"), full_page=True)
    page.set_viewport_size({"width": 1280, "height": 900})
    page.screenshot(path=str(OUT / "report_desktop.png"), full_page=True)
    context.close()
    assert errors == [], errors
