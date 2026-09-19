"""The built game and the generated tree outputs must match their sources."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tests.conftest import ROOT


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args], cwd=ROOT, capture_output=True, text=True
    )


def test_game_matches_a_fresh_build_of_src() -> None:
    r = _run("tools/build.py", "--check")
    assert r.returncode == 0, r.stdout + r.stderr


def test_tree_outputs_match_tech_py() -> None:
    r = _run("tools/regen_tree.py", "--check")
    assert r.returncode == 0, r.stdout + r.stderr


def test_campaign_json_has_four_evenings_of_eight_and_twelve_mentors() -> None:
    data = json.loads((ROOT / "vibemap" / "data" / "campaign.json").read_text())
    assert list(data["evenings"]) == ["campus", "winter", "desert", "prod"]
    for world, ev in data["evenings"].items():
        assert len(ev["ws"]) == 8, world
        for ws in ev["ws"]:
            assert {"h", "n", "d", "src"} <= set(ws), (world, ws.get("n"))
    assert len(data["mentors"]) == 12
    assert all(
        {"id", "name", "role", "world", "bio", "ask"} <= set(m) for m in data["mentors"]
    )


def test_three_js_is_embedded_not_linked() -> None:
    html = (ROOT / "game" / "vibe-map.html").read_text()
    assert "Copyright 2010-2021 Three.js Authors" in html
    assert '<script src="http' not in html


def _fork_root(tmp_path):
    """A copy of the game's source shaped the way `vibe fork` leaves it."""
    root = tmp_path / "fork"
    shutil.copytree(ROOT / "src", root / "src")
    shutil.copytree(ROOT / "tools" / "generated", root / "tools" / "generated")
    (root / "game").mkdir(parents=True)
    return root


def test_build_py_imports_without_tomllib() -> None:
    """tomllib is 3.11+, and a fork can be started by an older python3.

    The module has to import on that python, or the hand-over to the python
    that carries vibemap never gets the chance to run.
    """
    r = subprocess.run(
        [
            sys.executable,
            "-c",
            "import importlib.util, sys; sys.modules['tomllib'] = None; "
            "s = importlib.util.spec_from_file_location('b', 'tools/build.py'); "
            "m = importlib.util.module_from_spec(s); s.loader.exec_module(m)",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stdout + r.stderr


def test_a_fork_builds_with_a_python_that_has_no_vibemap(tmp_path) -> None:
    """`just build` in a fork runs a plain python3; it borrows vibe's own."""
    base = Path(sys.base_prefix) / "bin" / "python3"
    shim = Path(sys.executable).parent / "vibe"
    if not base.exists() or not shim.exists():
        pytest.skip("no interpreter outside the virtualenv to start the fork with")
    root = _fork_root(tmp_path)
    env = {**os.environ, "PATH": f"{shim.parent}{os.pathsep}{os.environ['PATH']}"}
    env.pop("VIRTUAL_ENV", None)
    env.pop("PYTHONPATH", None)
    r = subprocess.run(
        [str(base), "tools/build.py", "--root", str(root)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        env=env,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    assert (root / "game" / "vibe-map.html").exists()


def test_the_build_refuses_javascript_it_cannot_read(tmp_path) -> None:
    root = _fork_root(tmp_path)
    cfg = root / "src" / "config" / "00-config.js"
    cfg.write_text(cfg.read_text() + "\nconst BROKEN=(;\n")
    r = _run("tools/build.py", "--root", str(root))
    assert r.returncode != 0
    assert "00-config.js" in r.stdout + r.stderr
    assert not (root / "game" / "vibe-map.html").exists(), "it wrote the broken game"


def test_no_game_source_throws_away_the_object_it_just_built() -> None:
    """A ternary on a side effect keeps the wrong half of the pair.

    `cone(...).rotateX(a) ? cone(...) : null` and
    `cyl(...).material.emissive.set(c) ? cyl(...) : null` both read as one
    object with a tweak applied and both build two, add the untouched one and
    drop the one that was tweaked. Neither the browser nor the type checker
    says a word, so the shape is banned here.
    """
    import re

    pattern = re.compile(r"\.(rotate[XYZ]|set|setScalar|translate[XYZ])\([^)]*\)\s*\?")
    bad = []
    for path in sorted((ROOT / "src" / "game").glob("*.js")):
        for n, line in enumerate(path.read_text().splitlines(), 1):
            if pattern.search(line):
                bad.append(f"{path.name}:{n}")
    assert bad == [], f"a built object is thrown away by a ternary: {bad}"
