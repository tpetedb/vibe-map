"""Empty score files are a valid scoreboard, not a broken command."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def _run(camp: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "vibemap.cli", "scores"],
        cwd=camp,
        env=dict(os.environ, VIBE_HOME=str(camp), COLUMNS="200"),
        capture_output=True,
        text=True,
    )


def _scores_file(camp: Path) -> Path:
    path = camp / "workspace" / "data" / "scores.csv"
    path.parent.mkdir(parents=True)
    return path


def test_zero_byte_scores_file_reports_no_runs(tmp_path: Path) -> None:
    camp = tmp_path / "camp"
    scores = _scores_file(camp)
    scores.write_bytes(b"")

    result = _run(camp)

    assert result.returncode == 0, result.stdout + result.stderr
    assert "0 runs" in result.stdout
    assert "Traceback" not in result.stderr


def test_nonempty_malformed_header_still_fails_loudly(tmp_path: Path) -> None:
    camp = tmp_path / "camp"
    scores = _scores_file(camp)
    scores.write_text("player,points\nTom,10\n", encoding="utf-8")

    result = _run(camp)

    assert result.returncode != 0
    assert "scores.csv is missing columns" in result.stderr
