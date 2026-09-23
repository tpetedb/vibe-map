"""The documents that tell an agent what to run and what it may lean on.

A recipe, a skill or a helper a document names and the code does not have
sends the next reader down a path that ends in an error, so each name is
checked against the file that defines it, not against another document.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.conftest import ROOT
from tools import build, work
from vibemap import cli

SKILLS_DOC = ROOT / "docs" / "SKILLS.md"
CONFIG_DOC = ROOT / "docs" / "CONFIG.md"
CONTRACTS_DOC = ROOT / "docs" / "CONTRACTS.md"
ADR_BUILD = ROOT / "docs" / "adr" / "0001-single-file-game.md"
ADR_WORK = ROOT / "docs" / "adr" / "0016-work-orders.md"
SKILL_DIRS = ROOT / ".agents" / "skills"

# A recipe line: a name at the start of the line, optional parameters, a colon
# that is not the start of `:=` (a variable or a setting).
RECIPE = re.compile(r"^@?([A-Za-z_][\w-]*)(?:[ \t][^:\n]*)?:(?!=)", re.MULTILINE)
# `just name` in inline code, or at the start of an indented code line.
JUST_CALL = re.compile(r"(?:`|^[ \t]{4,})just ([a-z][a-z0-9-]*)", re.MULTILINE)
SKILL_ROW = re.compile(r"^\| `([a-z0-9-]+)` \|", re.MULTILINE)


def _recipes(text: str) -> set[str]:
    return set(RECIPE.findall(text))


def _all_recipes() -> set[str]:
    """Every recipe a reader of these documents can run: the product's, a
    camp's, and the fork's, which `vibe fork` writes from the CLI."""
    files = [
        ROOT / "justfile",
        ROOT / "agents.just",
        ROOT / "vibemap" / "data" / "template" / "justfile",
    ]
    found = {r for f in files for r in _recipes(f.read_text(encoding="utf-8"))}
    return found | _recipes(cli.FORK_JUSTFILE)


def _section(text: str, heading: str) -> str:
    """The body under one `## heading`, up to the next one."""
    start = text.index(f"\n## {heading}\n")
    end = text.find("\n## ", start + 1)
    return text[start : end if end >= 0 else len(text)]


def _skills() -> set[str]:
    return {d.name for d in SKILL_DIRS.iterdir() if d.is_dir()}


def test_the_recipe_parser_reads_a_justfile_the_way_just_does() -> None:
    sample = (
        "set shell := ['bash', '-c']\n"
        "name := 'x'\n"
        "# a doc comment: with a colon\n"
        "build:\n    echo\n"
        "release version:\n    echo {{version}}\n"
        "sync-main *args:\n    echo\n"
        "@quiet:\n    echo\n"
    )
    assert _recipes(sample) == {"build", "release", "sync-main", "quiet"}


@pytest.mark.parametrize("doc", [SKILLS_DOC, CONFIG_DOC, CONTRACTS_DOC])
def test_every_just_recipe_a_document_names_exists(doc: Path) -> None:
    named = set(JUST_CALL.findall(doc.read_text(encoding="utf-8")))
    missing = sorted(named - _all_recipes())
    assert not missing, f"{doc.name} names recipes no justfile has: {missing}"


def test_the_config_doc_names_recipes_at_all() -> None:
    """The guard above proves nothing if the pattern stops matching."""
    named = set(JUST_CALL.findall(CONFIG_DOC.read_text(encoding="utf-8")))
    assert {"build", "tree", "verify", "record"} <= named


@pytest.mark.parametrize(
    "heading", ["The skills", "Test that each one triggers"], ids=["what", "trigger"]
)
def test_every_skill_has_a_row_in_each_table_of_the_skills_doc(heading: str) -> None:
    table = _section(SKILLS_DOC.read_text(encoding="utf-8"), heading)
    rows = set(SKILL_ROW.findall(table))
    assert not _skills() - rows, f"no row under {heading!r}: {_skills() - rows}"
    assert not rows - _skills(), f"a row under {heading!r} names no skill"


def test_every_skill_a_document_names_exists() -> None:
    """`name` skill, or the skill `name`, in prose as well as in a table."""
    pattern = re.compile(r"`([a-z0-9-]+)` skill\b|\bskill `([a-z0-9-]+)`")
    for doc in (SKILLS_DOC, CONFIG_DOC, CONTRACTS_DOC):
        text = doc.read_text(encoding="utf-8")
        named = {a or b for a, b in pattern.findall(text)}
        assert not named - _skills(), f"{doc.name}: {named - _skills()}"


def test_the_skills_doc_names_the_skills_that_stay_in_the_product() -> None:
    """A camp does not get these two, and the doc has to say so."""
    from tools import sync_template

    text = _section(SKILLS_DOC.read_text(encoding="utf-8"), "The skills")
    for name in sync_template.PRODUCT_ONLY_SKILLS:
        row = next(line for line in text.splitlines() if line.startswith(f"| `{name}`"))
        assert "Product-only" in row, f"the {name} row does not say product-only"


@pytest.mark.parametrize("doc", [CONFIG_DOC, SKILLS_DOC, ADR_BUILD])
def test_no_document_describes_the_retired_load_order_list(doc: Path) -> None:
    assert "GAME_ORDER" not in doc.read_text(encoding="utf-8")


def test_the_build_has_no_load_order_list_either() -> None:
    """The documents say modules are found by name; the build has to agree."""
    assert not hasattr(build, "GAME_ORDER")
    assert build.MODULE_DIRS[0] == "game"


@pytest.mark.parametrize("doc", [CONFIG_DOC, ADR_BUILD])
def test_the_build_docs_name_what_the_build_reads(doc: Path) -> None:
    text = doc.read_text(encoding="utf-8")
    assert "MODULE_NAME" in text
    assert build.BOOT_MODULE in text, f"{doc.name} does not say boot comes last"
    for folder in build.MODULE_DIRS:
        assert f"src/{folder}/" in text, f"{doc.name} does not name src/{folder}/"


def test_adr_0016_is_accepted_and_says_how_touched_json_is_kept() -> None:
    text = " ".join(ADR_WORK.read_text(encoding="utf-8").split())
    assert text.startswith("# ADR 0016")
    assert "Status: Accepted" in text
    assert "never pruned" not in text
    assert "TOUCHED_KEEP" in text
    assert f"{work.TOUCHED_KEEP} " in text, "the number the ADR gives is not the tool's"


def test_the_patch_id_rule_is_more_than_one_sentence() -> None:
    """A review is tied to a patch id; the sentence that said so ran to eight
    clauses. Each sentence of the paragraph stays readable."""
    para = next(
        p
        for p in ADR_WORK.read_text(encoding="utf-8").split("\n\n")
        if p.startswith("**One tool decides")
    )
    longest = max(len(s) for s in re.split(r"(?<=[.:])\s", para))
    assert longest < 400, f"a sentence of {longest} characters"


# A line of the contracts file: the date it was made, the pull request that
# made it (or the comment that agreed it), then what it is.
CONTRACT_LINE = re.compile(r"^- (\d{4}-\d{2}-\d{2}), (#\d+|#95 comment)[ ,:(]")


def _contract_lines() -> list[str]:
    text = CONTRACTS_DOC.read_text(encoding="utf-8")
    return [line for line in text.splitlines() if line.startswith("- ")]


def test_every_contract_line_carries_a_date_and_its_source() -> None:
    lines = _contract_lines()
    assert len(lines) >= 30
    bad = [line[:80] for line in lines if not CONTRACT_LINE.match(line)]
    assert not bad, f"a contract with no date or no pull request: {bad}"


def _code_text() -> str:
    roots = [ROOT / "src", ROOT / "tools", ROOT / "vibemap"]
    parts = [
        p.read_text(encoding="utf-8")
        for r in roots
        for p in sorted(r.rglob("*"))
        if p.is_file()
        and p.suffix in {".js", ".py", ".html", ".css"}
        and "fork_source" not in p.parts
        and "vendor" not in p.parts
    ]
    parts.append((ROOT / "tests" / "conftest.py").read_text(encoding="utf-8"))
    return "\n".join(parts)


def test_every_helper_a_contract_names_is_defined() -> None:
    """`name()` in the contracts file is a function the code defines."""
    code = _code_text()
    named = set(
        re.findall(r"`(?:[\w.]+\.)?([A-Za-z_]\w*)\(", CONTRACTS_DOC.read_text())
    )
    assert len(named) >= 20
    definition = (
        r"(?:function {0}\b|def {0}\b|class {0}\b|\b{0}=|\b{0} = |\bconst {0}\b)"
    )
    missing = sorted(n for n in named if not re.search(definition.format(n), code))
    assert not missing, f"docs/CONTRACTS.md names helpers nothing defines: {missing}"


def test_every_path_a_contract_names_exists() -> None:
    text = CONTRACTS_DOC.read_text(encoding="utf-8")
    paths = set(
        re.findall(r"`([\w.-]+(?:/[\w.-]+)+/?)`", text)
        + re.findall(r"`([\w-]+\.(?:md|toml|json|py|js|yml|html))`", text)
    )
    # A bare file name is resolved where the contracts file says it lives.
    missing = sorted(
        p
        for p in paths
        if not (ROOT / p).exists()
        and not any(ROOT.glob(f"**/{p}"))
        and not p.startswith("work/orders/")
    )
    assert not missing, f"docs/CONTRACTS.md names paths that do not exist: {missing}"


def test_every_element_a_contract_names_is_on_the_page() -> None:
    body = (ROOT / "src" / "body.html").read_text(encoding="utf-8")
    ids = set(re.findall(r"`#([a-z][\w-]*)`", CONTRACTS_DOC.read_text()))
    assert ids, "the HUD contract names no element"
    missing = sorted(i for i in ids if f'id="{i}"' not in body)
    assert not missing, f"no element with these ids in src/body.html: {missing}"
