"""Repo hygiene: the facts AGENTS.md asks every session to re-verify."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

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


def test_the_design_doc_prints_the_tokens_that_ship() -> None:
    """docs/DESIGN.md quotes :root; a copy that drifts documents nothing."""
    css = (ROOT / "src" / "style.css").read_text(encoding="utf-8")
    root = css[css.index(":root{") :]
    root = root[: root.index("\n}\n") + 3]
    design = (ROOT / "docs" / "DESIGN.md").read_text(encoding="utf-8")
    assert f"```css\n{root}```" in design, (
        "docs/DESIGN.md no longer quotes :root from src/style.css verbatim"
    )


def test_every_skill_has_a_row_in_the_skills_doc() -> None:
    """docs/SKILLS.md is the index; a skill missing from it is invisible."""
    doc = (ROOT / "docs" / "SKILLS.md").read_text(encoding="utf-8")
    folders = sorted(
        d.name for d in (ROOT / ".agents" / "skills").iterdir() if d.is_dir()
    )
    missing = [n for n in folders if f"| `{n}` |" not in doc]
    assert not missing, f"no row in docs/SKILLS.md for: {', '.join(missing)}"
    listed = set(re.findall(r"^\| `([a-z0-9-]+)` \|", doc, re.MULTILINE))
    assert listed - set(folders) == set(), "docs/SKILLS.md names a skill that is gone"


def test_no_claude_artifact_link_survives_anywhere() -> None:
    """The syllabus is published from this repository, not from an artifact.

    A page in a personal claude.ai account cannot be versioned or reviewed, so
    the product may not point at one; `tools/gen_syllabus.py` owns the page it
    points at instead.
    """
    roots = [ROOT / "src", ROOT / "docs", ROOT / "vibemap", ROOT / "README.md"]
    offenders = [
        path.relative_to(ROOT)
        for root in roots
        for path in ([root] if root.is_file() else sorted(root.rglob("*")))
        if path.is_file()
        and path.suffix in {".md", ".js", ".html", ".css", ".py", ".json", ".toml"}
        and "claude.ai/artifact" in path.read_text(encoding="utf-8", errors="ignore")
    ]
    assert offenders == []


def test_the_licence_is_the_whole_mit_text() -> None:
    """A truncated MIT text is detected as "Other", so the repo has no licence."""
    text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    assert "Copyright (c) 2026 Tom Peters" in text
    # The clause GitHub's detector and a reuser both need, and the one that
    # was missing: the warranty disclaimer in full, plus the liability limit.
    for clause in (
        "WITHOUT WARRANTY OF ANY KIND, EXPRESS OR",
        "MERCHANTABILITY",
        "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT",
        "IN NO EVENT SHALL THE",
        "BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER",
    ):
        assert clause in text, clause


def test_the_community_files_are_there() -> None:
    """GitHub's community profile, and what an outsider needs on day one."""
    for name in (
        "LICENSE",
        "SECURITY.md",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        ".github/PULL_REQUEST_TEMPLATE.md",
        ".github/ISSUE_TEMPLATE/bug.yml",
        ".github/ISSUE_TEMPLATE/feature.yml",
        ".github/ISSUE_TEMPLATE/config.yml",
    ):
        p = ROOT / name
        assert p.is_file() and p.stat().st_size > 0, name
    # No personal address anywhere in them: reports go through GitHub.
    for name in ("SECURITY.md", "CODE_OF_CONDUCT.md"):
        assert "@gmail" not in (ROOT / name).read_text(encoding="utf-8"), name


def test_every_vendored_bundle_carries_its_licence() -> None:
    """MIT and ISC both say the licence text travels with the copy."""
    vendor = ROOT / "src" / "vendor"
    for bundle, licence in (
        ("three.min.js", "THREE-LICENSE.txt"),
        ("motion.min.js", "MOTION-LICENSE.txt"),
        ("d3-force.min.js", "D3-LICENSE.txt"),
    ):
        assert (vendor / bundle).is_file(), bundle
        text = (vendor / licence).read_text(encoding="utf-8")
        assert "Copyright" in text and "WARRANT" in text.upper(), licence


def test_the_page_says_what_it_is_and_where_it_lives() -> None:
    """A link pasted into a chat shows a title, a sentence and the card."""
    head = (ROOT / "src" / "head.html").read_text(encoding="utf-8")
    for tag in (
        'name="description"',
        'rel="canonical"',
        'property="og:title"',
        'property="og:description"',
        'property="og:image"',
        'property="og:url"',
        'name="twitter:card"',
        'name="theme-color"',
        'rel="icon"',
    ):
        assert tag in head, tag
    built = GAME.read_text()
    # The placeholders are filled at build time, and the card is absolute:
    # a crawler cannot resolve a relative one.
    assert "{{" not in built[: built.index("<style>")]
    assert 'content="https://tpetedb.github.io/vibe-map/hero.png"' in built
    assert 'href="data:image/svg+xml,' in built


# What makes a browser fetch something, as opposed to offering a link the
# reader may click: the course is full of honest anchors to other people's
# documentation and those are content, not a dependency.
_FETCHES_SRC = re.compile(
    r'<(?:script|img|iframe|source|video|audio|embed)\b[^>]*?\bsrc="([^"]+)"', re.I
)
_FETCHES_LINK = re.compile(
    r'<link\b[^>]*?\brel="(stylesheet|preconnect|dns-prefetch|preload|icon'
    r'|apple-touch-icon|manifest)"[^>]*?\bhref="([^"]+)"',
    re.I,
)
_CSS_FETCHES = re.compile(r"(?:@import\b|\burl\()\s*[\"']?([^)\"']+)", re.I)
# A build placeholder counts as ours: tools/build.py refuses to leave one
# behind, and the built head is checked for that above.
_OURS = ("data:", "blob:", "#", "./", "news.json", "{{")


def _loaded_from_outside(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    urls = [m.group(1) for m in _FETCHES_SRC.finditer(text)]
    urls += [m.group(2) for m in _FETCHES_LINK.finditer(text)]
    if path.suffix == ".css":
        urls += [m.group(1) for m in _CSS_FETCHES.finditer(text)]
    return [u for u in urls if not u.startswith(_OURS)]


def test_no_source_file_makes_the_page_fetch_a_third_party() -> None:
    """One file, no CDN. A link the reader clicks is fine; a load is not."""
    src = ROOT / "src"
    files = [src / "head.html", src / "body.html", src / "style.css"]
    files += sorted(src.glob("game/*.js")) + sorted(src.glob("config/*.js"))
    for f in files:
        outside = _loaded_from_outside(f)
        assert outside == [], (f.name, outside)


def test_the_published_site_carries_the_card_and_a_way_home() -> None:
    """og:image and the 404 page are files the Pages workflow really writes."""
    assert (ROOT / "docs" / "media" / "hero.png").is_file()
    page = ROOT / "site" / "404.html"
    assert page.is_file()
    steps = [
        s.get("run", "")
        for job in _workflows()["pages"]["jobs"].values()
        for s in job["steps"]
    ]
    run = "\n".join(steps)
    assert "docs/media/hero.png site/hero.png" in run
    # The way home is filled in from the site's own base path, never guessed.
    assert "base_path" in run
    assert "{{BASE}}" in page.read_text(encoding="utf-8")
