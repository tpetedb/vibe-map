"""The built game and the generated tree outputs must match their sources."""

from __future__ import annotations

import json
import subprocess
import sys

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
