"""Run the cache-version step as Actions does, including shell error handling."""

from __future__ import annotations

import importlib.metadata
import os
import shlex
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("lookup_fails", [False, True])
def test_workflow_cache_version(tmp_path: Path, lookup_fails: bool) -> None:
    workflow = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())
    step = next(
        step
        for step in workflow["jobs"]["browser-shard"]["steps"]
        if step.get("id") == "pw"
    )
    # Keep the workflow's real Python argument and shell; replace only uv's
    # environment selection so the test cannot resolve dependencies or use a cache.
    uv = tmp_path / "uv"
    body = (
        "exit 23\n"
        if lookup_fails
        else f'shift\nshift\nexec {shlex.quote(sys.executable)} "$@"\n'
    )
    uv.write_text("#!/bin/sh\n" + body)
    uv.chmod(0o755)
    output = tmp_path / "output"
    output.touch()
    result = subprocess.run(
        ["bash", "-e", "-o", "pipefail", "-c", step["run"]],
        env={
            **os.environ,
            "PATH": str(tmp_path) + os.pathsep + os.environ["PATH"],
            "GITHUB_OUTPUT": str(output),
        },
        capture_output=True,
        text=True,
    )
    if lookup_fails:
        assert result.returncode == 23, result.stderr
        assert output.read_text() == ""
    else:
        assert result.returncode == 0, result.stderr
        assert output.read_text() == (
            f"version={importlib.metadata.version('playwright')}\n"
        )
