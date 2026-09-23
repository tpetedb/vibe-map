"""Hunt batch Q: the brief, the roadmap headings, the tree notes, a run path.

One test per finding in `work/orders/hunt-q-docs-generators/findings.md`.
Every number and every path checked here is derived from the data or from the
file system, never typed twice: a count in prose that drifts from
`vibemap/data/` and a command that names a path nobody can run both fail here
instead of in a reader's face.
"""

from __future__ import annotations

import ast
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tools.gen_syllabus import spell
from tools.regen_tree import render
from vibemap import campaign
from vibemap.tech import T
from vibemap.vault import safe_title

ROOT = Path(__file__).resolve().parents[1]
BRIEF = ROOT / "docs" / "BRIEF.md"
ROADMAP = ROOT / "docs" / "ROADMAP.md"
SCORES = ROOT / "workspace" / "python" / "scores.py"
HANDWRITTEN = ROOT / "src" / "game" / "50-notes.js"

# A title has one owner. Duplicate object keys silently keep the last note.
KNOWN_SHADOWED: set[str] = set()

# The counts in the prose are written out, so a count is recognised by the
# word in front of the noun; "winter stops" and "which artifacts" are not
# counts and are passed over.
NUMBER_WORDS = {spell(n) for n in range(1, 100)}


def _counted(text: str, noun: str) -> list[str]:
    """Every spelled-out count of `noun` in the text, in order."""
    words = re.findall(rf"([A-Za-z]+(?:-[a-z]+)?) {noun}", text)
    return [w.lower() for w in words if w.lower() in NUMBER_WORDS]


def test_q1_the_brief_counts_what_the_campaign_data_holds() -> None:
    """The brief's counts are the data spelled out, or they are wrong."""
    text = BRIEF.read_text(encoding="utf-8")
    expected = {
        "stops": campaign.total_stops(),
        "mentors": len(campaign.mentors()),
        "artifacts": len(campaign.artifacts()),
    }
    for noun, count in expected.items():
        found = _counted(text, noun)
        assert found, f"docs/BRIEF.md no longer counts the {noun}"
        assert found == [spell(count)] * len(found), (
            f"docs/BRIEF.md says {found} {noun}; the data has {spell(count)}"
        )


def test_q2_the_roadmap_gives_every_topic_its_own_heading() -> None:
    """A heading glued behind the depth label renders as paragraph text."""
    md = ROADMAP.read_text(encoding="utf-8")
    assert not re.search(r"^\S.*###", md, re.M), (
        "a ### that is not at the start of its line is not a heading"
    )
    headings = re.findall(r"^### (.+)$", md, re.M)
    titles = [n for _i, _a, n, *_ in T]
    assert sorted(headings) == sorted(titles), (
        f"{len(headings)} headings for {len(titles)} topics"
    )


def test_q3_no_tree_note_is_shadowed_by_a_handwritten_one() -> None:
    """Two notes of one title become one in the game, and the last one wins."""
    generated, _tree_js, _md = render()
    handwritten = set(
        re.findall(r'^"([^"]+)":\{t:', HANDWRITTEN.read_text(encoding="utf-8"), re.M)
    )
    assert {"Git", "Python"} <= set(generated)
    shadowed = set(generated) & handwritten
    assert shadowed == KNOWN_SHADOWED, sorted(shadowed)


def _fork_root(tmp_path: Path) -> Path:
    root = tmp_path / "fork"
    shutil.copytree(ROOT / "src", root / "src")
    shutil.copytree(ROOT / "tools" / "generated", root / "tools" / "generated")
    (root / "game").mkdir(parents=True)
    return root


def _build(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "tools/build.py", "--root", str(root)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def _add(root: Path, source: str, addition: str) -> None:
    """Prepend to the handwritten object body, append to anything else."""
    path = root / "src" / "game" / source
    text = path.read_text(encoding="utf-8")
    if source == "50-notes.js" and not addition.startswith("\n"):
        path.write_text(addition + text, encoding="utf-8")
    else:
        path.write_text(text + addition, encoding="utf-8")


GEN, HAND, DYN = (
    "tools/generated/notes.js",
    "src/game/50-notes.js",
    "src/game/51-notes-dynamic.js",
)
UNIX = "Unix and the terminal"

# Each is valid JavaScript for one note title; owners lists every occurrence
# in build order, so a title written twice in one file names that file twice.
COLLISIONS = {
    "spaced key": ("50-notes.js", f'"{UNIX}": {{t:"c",md:`d`}},\n', UNIX, (GEN, HAND)),
    "two on a line": (
        "50-notes.js",
        f'"Hunt Q fresh":{{t:"c",md:`x`}},"{UNIX}":{{t:"c",md:`d`}},\n',
        UNIX,
        (GEN, HAND),
    ),
    "single quotes": (
        "50-notes.js",
        f"'{UNIX}':{{t:\"c\",md:`d`}},\n",
        UNIX,
        (GEN, HAND),
    ),
    "md before t": ("50-notes.js", f'"{UNIX}":{{md:`d`,t:"c"}},\n', UNIX, (GEN, HAND)),
    "inline comment": (
        "50-notes.js",
        f'"{UNIX}" /* by hand */ :{{t:"c",md:`d`}},\n',
        UNIX,
        (GEN, HAND),
    ),
    "identifier key": (
        "50-notes.js",
        'Tonight:{t:"c",md:`d`},\n',
        "Tonight",
        (HAND, HAND),
    ),
    "assignment after the object": (
        "50-notes.js",
        '\nNOTES["Tonight"]={t:"c",md:`d`};\n',
        "Tonight",
        (HAND, HAND),
    ),
    "dynamic assignment": (
        "51-notes-dynamic.js",
        f'\nNOTES["{UNIX}"]={{t:"c",md:`d`}};\n',
        UNIX,
        (GEN, DYN),
    ),
    "dynamic single quotes": (
        "51-notes-dynamic.js",
        f"\nNOTES['{UNIX}'] = {{t:\"c\",md:`d`}};\n",
        UNIX,
        (GEN, DYN),
    ),
    "dynamic spaced brackets": (
        "51-notes-dynamic.js",
        '\nNOTES[ "Tonight" ]={t:"c",md:`d`};\n',
        "Tonight",
        (HAND, DYN),
    ),
    "dynamic property": (
        "51-notes-dynamic.js",
        '\nNOTES.Tonight={t:"c",md:`d`};\n',
        "Tonight",
        (HAND, DYN),
    ),
}


@pytest.mark.parametrize(
    ("source", "addition", "title", "owners"),
    list(COLLISIONS.values()),
    ids=list(COLLISIONS),
)
def test_q3_build_refuses_every_kind_of_note_title_collision(
    tmp_path: Path,
    source: str,
    addition: str,
    title: str,
    owners: tuple[str, ...],
) -> None:
    """Generated, handwritten and dynamic notes share one title namespace."""
    root = _fork_root(tmp_path)
    _add(root, source, addition)
    result = _build(root)
    message = result.stdout + result.stderr
    assert result.returncode != 0, "the build accepted two notes with one title"
    line = next((ln for ln in message.splitlines() if repr(title) in ln), "")
    assert line, message
    assert line.endswith(": " + ", ".join(owners)), line


# Code that reads a note, or text that only mentions one, creates nothing.
NOT_COLLISIONS = {
    "comparison": f'\nif(NOTES["{UNIX}"]===undefined)console.warn("gone");\n',
    "inside a template": (
        '\nNOTES["Hunt Q example"]={t:"c",md:`Write NOTES["Tonight"]={} here.`};\n'
    ),
    "inside a comment": '\n// NOTES["Tonight"]={} would shadow the note.\n',
}


@pytest.mark.parametrize(
    "addition", list(NOT_COLLISIONS.values()), ids=list(NOT_COLLISIONS)
)
def test_q3_build_does_not_count_a_read_as_a_note(
    tmp_path: Path, addition: str
) -> None:
    """Only a key or an assignment in code makes a note."""
    root = _fork_root(tmp_path)
    _add(root, "51-notes-dynamic.js", addition)
    result = _build(root)
    assert result.returncode == 0, result.stdout + result.stderr


def test_q3_collision_diagnostic_includes_a_spaced_handwritten_key(
    tmp_path: Path,
) -> None:
    """Every owner is named even when harmless whitespace differs."""
    root = _fork_root(tmp_path)
    handwritten = root / "src" / "game" / "50-notes.js"
    handwritten.write_text(
        '"Unix and the terminal": {t:"c",md:`handwritten`},\n'
        + handwritten.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    dynamic = root / "src" / "game" / "51-notes-dynamic.js"
    dynamic.write_text(
        dynamic.read_text(encoding="utf-8")
        + '\nNOTES["Unix and the terminal"]={t:"c",md:`dynamic`};\n',
        encoding="utf-8",
    )
    result = _build(root)
    message = result.stdout + result.stderr
    assert result.returncode != 0
    assert "Unix and the terminal" in message
    assert "tools/generated/notes.js" in message
    assert "src/game/50-notes.js" in message
    assert "src/game/51-notes-dynamic.js" in message


def test_q3_every_tree_note_in_the_vault_lists_its_topic_docs() -> None:
    """A source added to a topic reaches the vault note, not only the game."""
    stale = []
    for n in campaign.tech_nodes():
        note = ROOT / "vault" / "Camp" / f"{safe_title(n.name)}.md"
        if not n.docs or not note.exists():
            continue
        docs = ", ".join(f"[{t}]({u})" for t, u in n.docs)
        if f"- Docs: {docs}\n" not in note.read_text(encoding="utf-8"):
            stale.append(note.name)
    assert not stale, f"run `uv run vibe vault build`: {stale}"


def test_q4_the_scores_script_names_a_path_that_exists() -> None:
    """The docstring's command is run from the camp root, like every other."""
    doc = ast.get_docstring(ast.parse(SCORES.read_text(encoding="utf-8"))) or ""
    commands = re.findall(r"python3 (\S+)", doc)
    assert commands, "the script no longer says how to run it"
    missing = [c for c in commands if not (ROOT / c).exists()]
    assert missing == [], missing
