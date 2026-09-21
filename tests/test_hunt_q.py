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
from pathlib import Path

from tools.gen_syllabus import spell
from tools.regen_tree import render
from vibemap import campaign
from vibemap.tech import T

ROOT = Path(__file__).resolve().parents[1]
BRIEF = ROOT / "docs" / "BRIEF.md"
ROADMAP = ROOT / "docs" / "ROADMAP.md"
SCORES = ROOT / "workspace" / "python" / "scores.py"
HANDWRITTEN = ROOT / "src" / "game" / "50-notes.js"

# Q3 is not fixed here: the two titles below are handwritten notes in
# src/game/50-notes.js (team panels) that shadow the generated topic note of
# the same name, because tools/build.py concatenates the handwritten module
# last. This order owns neither file; what it guards is that no third one
# joins them.
KNOWN_SHADOWED = {"Git", "Python"}

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


def test_q3_no_new_tree_note_is_shadowed_by_a_handwritten_one() -> None:
    """Two notes of one title become one in the game, and the last one wins."""
    generated, _tree_js, _md = render()
    handwritten = set(
        re.findall(r'^"([^"]+)":\{t:', HANDWRITTEN.read_text(encoding="utf-8"), re.M)
    )
    shadowed = set(generated) & handwritten
    assert shadowed <= KNOWN_SHADOWED, sorted(shadowed - KNOWN_SHADOWED)


def test_q4_the_scores_script_names_a_path_that_exists() -> None:
    """The docstring's command is run from the camp root, like every other."""
    doc = ast.get_docstring(ast.parse(SCORES.read_text(encoding="utf-8"))) or ""
    commands = re.findall(r"python3 (\S+)", doc)
    assert commands, "the script no longer says how to run it"
    missing = [c for c in commands if not (ROOT / c).exists()]
    assert missing == [], missing
