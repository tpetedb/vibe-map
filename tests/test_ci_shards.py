"""The browser shards as CI calls them: `tools/ci_shards.py --files <shard>`.

Each test copies the tool into a small folder of its own with a workflow and a
few test files, and runs it as the shard step does, as a command. The guard over
this repository's own split lives in tests/test_repo.py.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from tests.conftest import ROOT
from tools import ci_shards

PYTEST_INI = """[pytest]
addopts = -q
markers =
    browser: needs a browser
    integration: slow
"""

BROWSER_TEST = "import pytest\n\n@pytest.mark.browser\ndef test_it():\n    pass\n"


def camp(
    tmp_path: Path, include: list[dict[str, object]], tests: dict[str, str]
) -> Path:
    """A folder with the tool, a browser matrix and these test files."""
    root = tmp_path / "camp"
    (root / "tools").mkdir(parents=True)
    shutil.copy(ROOT / "tools" / "ci_shards.py", root / "tools" / "ci_shards.py")
    flow = root / ".github" / "workflows" / "ci.yml"
    flow.parent.mkdir(parents=True)
    jobs = {"browser-shard": {"strategy": {"matrix": {"include": include}}}}
    flow.write_text(yaml.safe_dump({"jobs": jobs}), encoding="utf-8")
    (root / "pytest.ini").write_text(PYTEST_INI)
    (root / "tests").mkdir()
    for name, text in tests.items():
        (root / "tests" / name).write_text(text)
    return root


def files_of(root: Path, shard: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "tools/ci_shards.py", "--files", shard],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


TWO = [
    {"shard": "a", "files": "tests/test_game_a*.py", "default": True},
    {"shard": "b", "files": "tests/test_game_b.py"},
]


def test_files_prints_one_line_a_shard_hands_to_pytest(tmp_path: Path) -> None:
    root = camp(
        tmp_path,
        TWO,
        {
            "test_game_a1.py": BROWSER_TEST,
            "test_game_a2.py": BROWSER_TEST,
            "test_game_b.py": BROWSER_TEST,
            "test_game_new.py": BROWSER_TEST,
            "test_plain.py": "def test_x():\n    pass\n",
        },
    )
    ran = files_of(root, "a")
    assert ran.returncode == 0, ran.stderr
    # The default shard also takes the file no pattern claims; a test without
    # the browser marker is not the browser battery's.
    assert ran.stdout.split() == [
        "tests/test_game_a1.py",
        "tests/test_game_a2.py",
        "tests/test_game_new.py",
    ]
    assert files_of(root, "b").stdout.split() == ["tests/test_game_b.py"]


def test_files_refuses_a_shard_the_matrix_does_not_have(tmp_path: Path) -> None:
    root = camp(tmp_path, TWO, {"test_game_a.py": BROWSER_TEST})
    ran = files_of(root, "nope")
    assert ran.returncode == 1 and ran.stdout == ""
    assert "no shard named nope" in ran.stderr and "a, b" in ran.stderr


def test_files_refuses_a_split_it_cannot_trust(tmp_path: Path) -> None:
    root = camp(tmp_path, TWO, {"test_game_a.py": BROWSER_TEST})
    ran = files_of(root, "a")
    assert ran.returncode == 1 and ran.stdout == ""
    assert "tests/test_game_b.py claims no browser test file" in ran.stderr


def test_a_browser_test_file_that_does_not_import_stops_every_shard(
    tmp_path: Path,
) -> None:
    """A file that fails to collect would otherwise drop out of the split in
    silence: no shard runs it, and the guard sees nothing wrong."""
    broken = "import a_module_that_does_not_exist\n\n" + BROWSER_TEST
    root = camp(
        tmp_path,
        TWO,
        {
            "test_game_a.py": BROWSER_TEST,
            "test_game_b.py": BROWSER_TEST,
            "test_game_broken.py": broken,
        },
    )
    for shard in ("a", "b"):
        ran = files_of(root, shard)
        assert ran.returncode == 1 and ran.stdout == "", ran.stdout
        assert "test_game_broken.py" in ran.stderr, ran.stderr
    with pytest.raises(ci_shards.Unreadable, match="test_game_broken.py"):
        ci_shards.browser_test_files(root)


@pytest.mark.parametrize("value", ["false", "true", 1])
def test_default_is_a_boolean_or_the_matrix_is_refused(
    tmp_path: Path, value: object
) -> None:
    """YAML reads `default: "false"` as a string, and a string is truthy."""
    include = [
        {"shard": "a", "files": "tests/test_game_a.py", "default": True},
        {"shard": "b", "files": "tests/test_game_b.py", "default": value},
    ]
    root = camp(
        tmp_path,
        include,
        {"test_game_a.py": BROWSER_TEST, "test_game_b.py": BROWSER_TEST},
    )
    ran = files_of(root, "a")
    assert ran.returncode == 1 and "Traceback" not in ran.stderr, ran.stderr
    assert "shard b" in ran.stderr and "true or false" in ran.stderr


def test_a_pattern_claims_by_the_same_rule_everywhere() -> None:
    shard = ci_shards.Shard("a", ("tests/test_game_q*.py",))
    for name in ("tests/test_game_qol.py", "tests/test_game_Qol.py"):
        assert shard.claims(name) == ci_shards.matches(name, "tests/test_game_q*.py")
    # Case counts on every runner, as it does in the file system CI runs on.
    assert not shard.claims("tests/test_game_Qol.py")
