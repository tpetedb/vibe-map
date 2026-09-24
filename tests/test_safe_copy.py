"""No learner-facing copy tells a beginner to approve a prompt they do not understand.

A beginner cannot judge what an agent wants to run or change, so the first lesson
says to pause, read and ask before saying yes. Reads files only; no browser.
"""

from __future__ import annotations

import html
import re
from collections.abc import Iterator
from pathlib import Path

import pytest

from tests.conftest import ROOT

GAME = ROOT / "game" / "vibe-map.html"
BODY = ROOT / "src" / "body.html"
SYLLABUS = ROOT / "docs" / "SYLLABUS.md"
SYLLABUS_PAGE = ROOT / "docs" / "site" / "syllabus.html"

# The one sentence both copies of workstream 1's Definition of done carry.
SAFE = (
    "If Claude asks permission for something you do not understand, pause: read "
    "what it wants to run or change, and ask Tom before you say yes; understanding "
    "permissions in depth is workstream 4."
)

# An instruction to approve: "answer yes", "click allow", "approve it".
_APPROVE = re.compile(
    r"\b(?:answer|say|click|press|type|reply|hit)\s+(?:yes|y|allow|accept)\b"
    r"|\b(?:approve|accept|allow)\s+(?:it|them|the prompt|the request|everything)\b",
    re.IGNORECASE,
)
# The same words are fine when a guard stands right in front of them.
_GUARDED = re.compile(
    r"(?:before you|do not|don't|never|only after you|only then)\s+$", re.IGNORECASE
)
_TEXT_SUFFIXES = {".html", ".js", ".md", ".json", ".toml", ".txt"}
_SKIP_PARTS = {"vendor", "pets"}


def _plain(text: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", " ", text))


def _sentences(text: str) -> Iterator[str]:
    for sentence in re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", _plain(text))):
        if "permission" in sentence.lower():
            yield sentence


def unsafe_sentences(text: str) -> list[str]:
    """Every sentence about a permission that tells the reader to approve it."""
    found = []
    for sentence in _sentences(text):
        for m in _APPROVE.finditer(sentence):
            if not _GUARDED.search(sentence[: m.start()]):
                found.append(sentence)
                break
    return found


def _learner_files() -> list[Path]:
    files = [GAME, SYLLABUS, SYLLABUS_PAGE]
    for base in (ROOT / "src", ROOT / "vibemap" / "data"):
        files += [
            p
            for p in sorted(base.rglob("*"))
            if p.is_file()
            and p.suffix in _TEXT_SUFFIXES
            and not _SKIP_PARTS & set(p.relative_to(base).parts)
        ]
    return files


def _first_lesson(page: str) -> str:
    m = re.search(r'<section class="screen" id="s-1">(.*?)</section>', page, re.S)
    assert m, "workstream 1's screen is missing"
    return m.group(1)


def _definition_of_done(chunk: str) -> str:
    m = re.search(r"<b>Definition of done</b>(.*?)</div>", chunk, re.S)
    assert m, "workstream 1 has no Definition of done"
    return m.group(1)


def test_the_detector_catches_the_old_instruction_and_passes_the_new_one() -> None:
    old = (
        "If Claude asked a permission question you did not understand, answer yes "
        "and tell Tom; understanding permissions is workstream 4."
    )
    assert unsafe_sentences(old) == [old]
    assert unsafe_sentences(SAFE) == []


@pytest.mark.parametrize(
    "path", _learner_files(), ids=lambda p: str(p.relative_to(ROOT))
)
def test_no_copy_says_to_approve_a_permission(path: Path) -> None:
    assert unsafe_sentences(path.read_text(errors="replace")) == []


@pytest.mark.parametrize("path", [BODY, GAME], ids=["src/body.html", "game"])
def test_the_first_lesson_says_pause_read_and_ask(path: Path) -> None:
    done = re.sub(r"\s+", " ", _definition_of_done(_first_lesson(path.read_text())))
    assert SAFE in done


def test_the_syllabus_says_the_same_in_workstream_1() -> None:
    text = SYLLABUS.read_text()
    m = re.search(r"^## 18:00: .*?(?=^## )", text, re.S | re.M)
    assert m, "the syllabus has no 18:00 section"
    assert SAFE in re.sub(r"\s+", " ", m.group(0))
    assert SAFE in re.sub(r"\s+", " ", _plain(SYLLABUS_PAGE.read_text()))
