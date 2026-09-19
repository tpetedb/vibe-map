"""Repo hygiene: the facts HANDOVER.md asks every session to re-verify."""

from __future__ import annotations

import re
import subprocess
import sys

import pytest

from tests.conftest import ROOT

GAME = ROOT / "game" / "vibe-map.html"


def _origin_url() -> str | None:
    try:
        out = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    m = re.match(r"(?:git@github\.com:|https://github\.com/)([^/]+/[^/.]+)", out)
    return f"https://github.com/{m.group(1)}" if m else None


def test_template_link_in_game_matches_the_git_remote() -> None:
    origin = _origin_url()
    if origin is None:
        pytest.skip("no GitHub origin configured")
    m = re.search(r'id="tplink" href="([^"]+)"', GAME.read_text())
    assert m, "tplink anchor missing from the game"
    assert m.group(1) == origin


def test_nothing_loads_the_learners_index_html() -> None:
    """workspace/game/index.html is replaced on the night; only prose may mention it."""
    html = GAME.read_text()
    assert not re.search(r'(src|href)="[^"]*index\.html"', html)
    # quests.py may look at the file to verify workstream 1; nothing else may
    # read it (prose mentions in notes and recipes are fine).
    readers = ("read_text", "open(", 'Path("', '/ "index.html"')
    for py in (ROOT / "vibemap").glob("*.py"):
        if py.name == "quests.py":
            continue
        for line in py.read_text().splitlines():
            if "index.html" in line:
                assert not any(r in line for r in readers), (py.name, line.strip())


def test_no_em_dashes_or_emoji_in_tracked_text() -> None:
    from tools.checks import check_style

    assert check_style([]) == 0


def test_every_value_the_game_writes_as_html_has_been_looked_at() -> None:
    """docs/SECURITY-MODEL.md: escape it, or register it as build-time data."""
    from tools.checks import check_sinks

    assert check_sinks() == 0


def test_the_sink_guard_catches_a_raw_value_and_a_new_sink(tmp_path) -> None:
    """The guard is only worth its register if it bites on the real mistake."""
    import shutil

    from tools.checks import GAME_SRC, check_sinks

    src = tmp_path / "game"
    shutil.copytree(GAME_SRC, src)
    assert check_sinks(src=src) == 0
    sheet = src / "40-sheet.js"
    sheet.write_text(
        sheet.read_text()
        + '\nfunction feedLine(i){return `<p class="small">${i.title}</p>`}\n'
    )
    assert check_sinks(src=src) == 1
    sheet.write_text(sheet.read_text() + '\n$("newsmsg").innerHTML=newsData.note;\n')
    assert check_sinks(src=src) == 2
    # An escaped value passes, and eval never does.
    (src / "41-search.js").write_text(
        (src / "41-search.js").read_text()
        + "\nfunction hit(r){return `<b>${esc(r.t)}</b>`}\nconst run=s=>eval(s);\n"
    )
    assert check_sinks(src=src) == 3


def test_version_matches_pyproject() -> None:
    import tomllib

    import vibemap

    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert vibemap.__version__ == data["project"]["version"]


def _workflows() -> dict[str, dict]:
    import yaml

    out = {}
    for p in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        # `on` is YAML 1.1 for True, so the parsed key is the boolean.
        out[p.stem] = yaml.safe_load(p.read_text(encoding="utf-8"))
    return out


def test_every_workflow_parses_and_has_jobs() -> None:
    flows = _workflows()
    assert {"ci", "nightly", "pages", "news"} <= set(flows)
    for name, flow in flows.items():
        assert flow["jobs"], name
        assert flow.get(True) or flow.get("on"), name


def test_the_fast_ci_never_runs_the_slow_tests() -> None:
    """ci.yml is the gate on a pull request; integration runs belong to nightly."""
    steps = [
        s.get("run", "")
        for job in _workflows()["ci"]["jobs"].values()
        for s in job["steps"]
    ]
    pytests = [s for s in steps if "pytest" in s]
    assert pytests
    for step in pytests:
        assert "not integration" in step or "test_game_webkit.py" in step, step
        # A second -q on the command line would hide the -ra summary.
        assert " -q" not in step, step


def test_nightly_runs_on_a_schedule_on_tags_and_on_demand() -> None:
    flow = _workflows()["nightly"]
    triggers = flow.get(True) or flow.get("on")
    assert "schedule" in triggers and "workflow_dispatch" in triggers
    assert triggers["push"]["tags"] == ["v*"]
    runs = [s.get("run", "") for j in flow["jobs"].values() for s in j["steps"]]
    assert any("tools/fresh_camp.py" in r for r in runs)
    assert any("-m integration" in r for r in runs)


def _browser_test_files() -> set[str]:
    """The files pytest itself puts in the browser battery, asked of pytest."""
    out = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-m",
            "browser and not integration",
            "--collect-only",
            "--no-header",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    ).stdout
    # The quiet collect prints one "tests/test_x.py: 4" line per file.
    return set(re.findall(r"^(tests/\S+\.py)(?=[:\s])", out, re.MULTILINE))


def test_every_browser_test_file_is_in_exactly_one_shard() -> None:
    """A browser test file in no shard would never run; in two it runs twice."""
    from tools.ci_shards import shards

    owned: list[str] = [f for s in shards() for f in s.files]
    collected = _browser_test_files()
    assert collected, "collected no browser tests, so this guard proves nothing"
    assert len(owned) == len(set(owned)), "a file is in two shards"
    assert collected - set(owned) == set(), "browser test files in no shard"
    assert set(owned) - collected == set(), "a shard names a file with no browser test"


def test_the_required_context_is_its_own_job_and_keeps_its_name() -> None:
    """Branch protection names these two contexts; a rename blocks every PR."""
    jobs = _workflows()["ci"]["jobs"]
    assert jobs["lint-and-unit"]["name"] == "lint, unit tests, generated files in sync"
    assert jobs["browser"]["name"] == "Playwright tests (Chromium and WebKit)"
    # The matrix job carries the leg in its name, so it can never be the
    # required context; the aggregator that needs it is.
    assert jobs["browser"]["needs"] == ["browser-shard"]
    assert "matrix" not in jobs["browser"].get("strategy", {})
    assert jobs["browser"]["if"] == "always()"
