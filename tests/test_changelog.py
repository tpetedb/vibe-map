"""The changelog harness: fragments in, a Keep a Changelog section out.

The tool is tested through its functions rather than its output text, except
for `release`, where the shape of the file is the point.
"""

from __future__ import annotations

import re

import pytest

from tests.conftest import ROOT
from tools import changelog, sync_main

FRAGMENTS = ROOT / "changelog.d"


def write(folder, name: str, body: str) -> None:
    (folder / name).write_text(body)


def test_the_repository_carries_a_readable_fragment_folder() -> None:
    """Empty right after a release is fine; a malformed fragment is not."""
    assert (FRAGMENTS / "README.md").is_file()
    changelog.read_fragments()


def test_changelog_md_has_no_entries_of_its_own() -> None:
    """A branch adds a fragment; Unreleased stays empty until a release."""
    text = changelog.CHANGELOG.read_text()
    head, unreleased, _ = changelog._split(text)
    assert "changelog.d" in unreleased
    assert "### " not in unreleased


def test_a_fragment_is_read_as_its_slug_type_and_body(tmp_path) -> None:
    write(tmp_path, "a-thing.added.md", "- A thing.\n")
    write(tmp_path, "b-thing.fixed.md", "- Another thing.\n")
    got = changelog.read_fragments(tmp_path)
    assert [(f.slug, f.type) for f in got] == [
        ("a-thing", "added"),
        ("b-thing", "fixed"),
    ]
    assert got[0].body == "- A thing."


@pytest.mark.parametrize(
    "name, body",
    [
        ("nope.md", "- A thing.\n"),
        ("a-thing.improved.md", "- A thing.\n"),
        ("a-thing.added.md", "\n"),
        ("a-thing.added.md", "A thing without a bullet.\n"),
    ],
)
def test_a_fragment_that_is_not_one_fails_loudly(
    tmp_path, name: str, body: str
) -> None:
    write(tmp_path, name, body)
    with pytest.raises(SystemExit):
        changelog.read_fragments(tmp_path)


def test_draft_prints_the_six_headings_in_order(tmp_path) -> None:
    write(tmp_path, "b.fixed.md", "- A fix.\n")
    write(tmp_path, "a.added.md", "- An addition.\n")
    draft = changelog.draft(changelog.read_fragments(tmp_path))
    assert draft.startswith("## [Unreleased]")
    assert draft.index("### Added") < draft.index("### Fixed")
    assert "- An addition." in draft and "- A fix." in draft


def test_draft_of_nothing_points_at_the_folder(tmp_path) -> None:
    assert "changelog.d" in changelog.draft(changelog.read_fragments(tmp_path))


def _latest_release() -> tuple[str, str]:
    """The newest released section: these tests must outlive a release."""
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    found = re.search(r"^## \[(\d+\.\d+\.\d+)\] - (\S+)", text, flags=re.M)
    assert found, "CHANGELOG.md has no released section"
    return found.group(1), found.group(2)


def test_release_writes_a_dated_section_and_moves_the_links(tmp_path) -> None:
    write(tmp_path, "a.added.md", "- An addition.\n")
    previous, released_on = _latest_release()
    out = changelog.release("99.0.0", "2026-09-18", changelog.read_fragments(tmp_path))
    assert "## [99.0.0] - 2026-09-18" in out
    assert "- An addition." in out
    base = "https://github.com/tpetedb/vibe-map/compare"
    assert f"[Unreleased]: {base}/v99.0.0...HEAD" in out
    assert f"[99.0.0]: {base}/v{previous}...v99.0.0" in out
    # The section that was there before is untouched, and Unreleased is empty.
    assert f"## [{previous}] - {released_on}" in out
    head, unreleased, _ = changelog._split(out)
    assert "### " not in unreleased


def test_release_refuses_a_version_that_is_already_in_the_file(tmp_path) -> None:
    write(tmp_path, "a.added.md", "- An addition.\n")
    with pytest.raises(SystemExit):
        changelog.release(
            _latest_release()[0], "2026-09-18", changelog.read_fragments(tmp_path)
        )


def test_release_refuses_a_number_that_is_not_semver(tmp_path) -> None:
    write(tmp_path, "a.added.md", "- An addition.\n")
    with pytest.raises(SystemExit):
        changelog.release("v1.0", "2026-09-18", changelog.read_fragments(tmp_path))


def test_release_refuses_an_empty_folder(tmp_path) -> None:
    with pytest.raises(SystemExit):
        changelog.release("1.0.0", "2026-09-18", changelog.read_fragments(tmp_path))


@pytest.mark.parametrize(
    "paths, code",
    [
        (["vibemap/cli.py"], 1),
        (["src/game/00-state.js"], 1),
        (["tools/build.py"], 1),
        (["vibemap/cli.py", "changelog.d/a-thing.added.md"], 0),
        (["docs/MAINTAINERS.md"], 0),
        (["tests/test_cli.py"], 0),
        (["vibemap/data/fork_source/tools/build.py"], 0),
        (["vibemap/data/template/justfile"], 0),
        (["tools/generated/notes.js"], 0),
        (["CHANGELOG.md"], 1),
        (["CHANGELOG.md", "changelog.d/a-thing.added.md"], 0),
    ],
)
def test_check_asks_for_a_fragment_where_it_matters(
    paths: list[str], code: int
) -> None:
    got, message = changelog.check(paths)
    assert got == code, message


def test_check_names_the_file_that_needs_the_entry() -> None:
    _, message = changelog.check(["vibemap/quests.py"])
    assert "vibemap/quests.py" in message


def test_the_ci_lint_job_runs_the_check() -> None:
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
    assert "tools/changelog.py check" in workflow


def test_the_justfile_offers_the_harness_recipes() -> None:
    recipes = (ROOT / "justfile").read_text()
    for recipe in ("sync-main", "changelog:", "release version"):
        assert recipe in recipes


# --- sync-main ---------------------------------------------------------------


def test_a_conflict_in_a_generated_file_is_not_a_real_conflict() -> None:
    generated, real = sync_main.classify(
        [
            "game/vibe-map.html",
            "docs/ROADMAP.md",
            "tools/generated/notes.js",
            "vibemap/data/fork_source/src/game/00-state.js",
            "vibemap/data/template/_agents/skills/changelog/SKILL.md",
            "vault/Camp/Tonight.md",
        ]
    )
    assert real == []
    assert len(generated) == 6


def test_a_conflict_in_a_source_file_stops_the_merge() -> None:
    generated, real = sync_main.classify(
        ["game/vibe-map.html", "src/game/00-state.js", "vibemap/cli.py"]
    )
    assert generated == ["game/vibe-map.html"]
    assert real == ["src/game/00-state.js", "vibemap/cli.py"]


def test_the_changelog_is_a_source_file_now() -> None:
    """Fragments are why it stops conflicting, not a merge rule that hides it."""
    _, real = sync_main.classify(["CHANGELOG.md"])
    assert real == ["CHANGELOG.md"]


def test_every_generated_path_is_regenerated_by_one_of_the_tools() -> None:
    """A file that nothing regenerates must not be resolved by taking a side."""
    tools = " ".join(" ".join(cmd) for cmd in sync_main.REGENERATE)
    for tool in ("regen_tree", "gen_cookbook", "sync_template", "build",
                 "sync_fork_source", "vault build"):  # fmt: skip
        assert tool in tools


def test_the_generated_files_are_marked_for_review() -> None:
    attributes = (ROOT / ".gitattributes").read_text()
    for path in sync_main.GENERATED:
        pattern = path.rstrip("/") + ("/**" if path.endswith("/") else "")
        assert pattern in attributes, path
    # Only git's built-in drivers: a custom one would need per-clone config.
    rules = [
        line.split() for line in attributes.splitlines() if line and line[0] != "#"
    ]
    merges = {a for _, *rest in rules for a in rest if a.startswith("merge=")}
    assert merges == {"merge=binary"}


def _section(version: str) -> str:
    text = changelog.CHANGELOG.read_text()
    start = text.index(f"## [{version}]")
    return text[start : text.index("\n## [", start + 1)]


def test_the_0_12_0_galaxy_walk_says_a_button_opens_the_lesson() -> None:
    """Walking up only names the lesson; the button or Enter opens it."""
    section = _section("0.12.0")
    assert "walking up to a pavilion opens" not in section
    assert "Open nearby lesson" in section
    assert "Open nearby lesson" in (ROOT / "src" / "body.html").read_text()


@pytest.mark.parametrize(
    "control",
    ["Open nearby lesson", "Bigger", "Walk there", "Take photo", "Keep going",
     "Stop reminding me", "Tap to hurry", "Keep running"],
)  # fmt: skip
def test_a_control_the_0_12_0_section_names_exists_in_the_game(control) -> None:
    assert control in _section("0.12.0")
    source = " ".join(p.read_text() for p in (ROOT / "src").rglob("*.*")
                      if p.suffix in {".js", ".html"})  # fmt: skip
    assert control in source


def test_the_0_12_0_section_says_the_map_once() -> None:
    assert "The map is one you can use" not in _section("0.12.0")
