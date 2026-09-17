"""A camp from nothing: the checks refuse, then they pass, then the code travels.

Marked integration: it starts a process per step and takes a minute. The
nightly workflow runs the same journey against the installed `vibe`, which is
the only run that also proves the packaging.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from tools.fresh_camp import run_fresh_camp


@pytest.mark.integration
def test_a_fresh_camp_refuses_then_passes_and_carries_its_code(
    tmp_path: Path,
) -> None:
    result = run_fresh_camp([sys.executable, "-m", "vibemap.cli"], tmp_path)
    assert result["done"]["campus"] == [1, 3]
    assert result["imported"]["campus"] == [1, 3]
    assert len(str(result["code"])) > 20
