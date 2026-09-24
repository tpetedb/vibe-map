"""Issue 59 closes only when its history and three feature guides are findable."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_cycle_three_records_its_issues_pull_requests_and_releases() -> None:
    brief = _read("docs/BRIEF.md")
    cycle = brief.split("## 5. Cycle 3", 1)[1]

    for issue in (53, 54, 55, 56, 57, 58, 59, 60, 65, 69):
        assert f"#{issue}" in cycle
    for pull in (61, 62, 63, 64, 66, 67, 68, 71, 72, 116, 159):
        assert f"#{pull}" in cycle
    assert "0.10.0" in cycle and "0.11.0" in cycle
    assert "social preview" in cycle.lower()


def test_the_old_gaps_do_not_call_played_regeneration_unbuilt() -> None:
    gaps = _read("docs/BRIEF.md").split("## 3. Gaps, honestly", 1)[1]
    gaps = gaps.split("## 4.", 1)[0]
    assert "has to script those deliverables" not in gaps
    assert "Cycle 3" not in gaps or "closed" in gaps


def test_the_three_guides_are_linked_and_name_their_responsible_code() -> None:
    readme = _read("README.md")
    required = {
        "docs/DASHBOARD.md": ("src/game/89-dashboard.js", "vibemap/dashboard.py"),
        "docs/AVATAR.md": ("src/game/18-avatar.js", "src/game/19-items.js"),
        "docs/ARCHIPELAGO.md": (
            "src/game/22-archipelago.js",
            "tests/test_game_bridges.py",
        ),
    }
    for relative, sources in required.items():
        assert f"]({relative})" in readme
        text = _read(relative)
        assert all(source in text for source in sources)
        assert "Accessibility" in text
        assert "Saved state" in text
