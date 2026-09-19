"""The note checks: a stop is green only when the learner wrote the note.

A fresh camp is the hard case. `vibe init` writes a stub for every workstream,
so the checks run against a camp built the way a learner gets one, through
`vibe new`, and every island must be red before anything is written.
"""

from __future__ import annotations

import os
import subprocess
import sys
from datetime import date
from pathlib import Path

from click.testing import CliRunner

from tests.conftest import encode_progress
from vibemap import campaign
from vibemap.cli import cli
from vibemap.config import Config
from vibemap.quests import quest_for
from vibemap.state import State
from vibemap.vault import Vault, learner_sections, safe_title, stub_bullet

OWN_NOTE = """Today I built the thing myself and it took two evenings of
reading and swearing. The agent wrote the first draft, I rewrote the half that
made no sense, and the check told me what was missing before I could claim it.
What I learned: the check reads the note, so the note is the work, and writing
it down is what made the next stop obvious to me. See [[Git]] and
[[Docker and containers]] for the parts I had to look up twice.
"""


def _camp(tmp_path: Path) -> Path:
    """A camp the way a learner gets one: the template, the vault, no edits."""
    camp = tmp_path / "camp"
    out = CliRunner().invoke(cli, ["new", str(camp), "--name", "T"])
    assert out.exit_code == 0, out.output
    return camp


def _check(camp: Path, world: str, n: int) -> str:
    env = dict(os.environ, VIBE_HOME=str(camp))
    out = subprocess.run(
        [
            sys.executable,
            "-m",
            "vibemap.cli",
            "check",
            "--no-claim",
            "-w",
            world,
            str(n),
        ],
        cwd=camp,
        env=env,
        capture_output=True,
        text=True,
    )
    return out.stdout + out.stderr


def test_a_fresh_camp_fails_every_note_check(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    # The stub the vault writes is there, and it is not enough.
    for world in ("winter", "desert", "prod"):
        for n in (1, 5, 8):
            output = _check(camp, world, n)
            assert "fail" in output, output
            assert "pass" not in output, output


def test_a_note_in_the_learners_own_words_passes(tmp_path: Path) -> None:
    # A reading-only stop, where the note is the whole deliverable; the stops
    # that also leave a file behind are covered in tests/test_stops.py.
    camp = _camp(tmp_path)
    ws = campaign.evenings()["winter"].workstreams[1]
    note = camp / "vault" / "Camp" / f"{safe_title(ws.name)}.md"
    text = note.read_text(encoding="utf-8")
    assert "not done yet" in text
    note.write_text(
        text.replace(
            f"- {stub_bullet('winter', ws.n)}",
            "\n".join(f"- {line}" for line in OWN_NOTE.strip().splitlines()),
        ),
        encoding="utf-8",
    )
    output = _check(camp, "winter", 2)
    assert "pass" in output, output
    assert "fail" not in output, output


def test_generated_lines_never_count_as_the_learners_words(tmp_path: Path) -> None:
    cfg = Config.model_validate({"vault": {"path": str(tmp_path), "folder": "G"}})
    v = Vault(cfg, State(name="T"))
    ws = campaign.evenings()["winter"].workstreams[1]
    v.upsert_dated(
        ws.name,
        summary=f"{ws.hour}, [[Evening 2]]. Outcome: {ws.outcome}.",
        bullets=[
            stub_bullet("winter", ws.n),
            "links: [[Tonight]], [[Map]]",
        ],
        tags=["workstream"],
        sources=[u for _, u in ws.sources],
    )
    text = v.path(ws.name).read_text(encoding="utf-8")
    own = [
        ln
        for _, lines in learner_sections(text, tuple(u for _, u in ws.sources))
        for ln in lines
    ]
    assert own == [], own
    check = quest_for("winter", 2, cfg).checks[0]
    assert not check.run(cfg).ok


def test_a_claim_replaces_the_stub_instead_of_contradicting_it(tmp_path: Path) -> None:
    cfg = Config.model_validate({"vault": {"path": str(tmp_path), "folder": "G"}})
    v = Vault(cfg, State(name="T"))
    ws = campaign.evenings()["campus"].workstreams[0]
    common = {
        "summary": f"{ws.hour}, [[Evening 1]]. Outcome: {ws.outcome}.",
        "tags": ["workstream"],
        "sources": [u for _, u in ws.sources],
    }
    v.upsert_dated(ws.name, bullets=[stub_bullet("campus", ws.n)], **common)
    v.upsert_dated(ws.name, bullets=["done at 19:10", "built the game"], **common)
    text = v.path(ws.name).read_text(encoding="utf-8")
    assert "not done yet" not in text
    assert text.count(f"## {date.today().isoformat()}") == 1
    # A second entry on the same day joins that heading instead of adding one.
    v.upsert_dated(ws.name, bullets=["and then I wrote the note"], **common)
    text = v.path(ws.name).read_text(encoding="utf-8")
    assert text.count(f"## {date.today().isoformat()}") == 1
    assert "- built the game" in text and "- and then I wrote the note" in text
    assert "## Sources" in text and "#workstream" in text


def test_undo_takes_the_xp_and_the_claim_back(tmp_path: Path) -> None:
    cfg = Config.model_validate({"vault": {"path": str(tmp_path), "folder": "G"}})
    st = State(name="T")
    st.mark_done("campus", 1, note="built it", xp=100)
    v = Vault(cfg, st)
    ws = campaign.evenings()["campus"].workstreams[0]
    v.upsert_dated(
        ws.name,
        summary="s",
        bullets=["done at 19:10", "my own line about the evening"],
        tags=["workstream"],
        sources=[],
    )
    assert st.undo("campus", 1) == 100
    assert st.xp == 0 and not st.is_done("campus", 1) and st.log == []
    assert v.drop_claim(ws.name)
    text = v.path(ws.name).read_text(encoding="utf-8")
    assert "done at 19:10" not in text
    assert "my own line about the evening" in text


def test_the_linked_badge_counts_only_the_learners_own_links(tmp_path: Path) -> None:
    """The generated vault is full of wikilinks; the badge is for your own."""
    from vibemap.quests import OWN_LINKS_BADGE, new_badges

    camp = tmp_path / "camp"
    assert CliRunner().invoke(cli, ["new", str(camp), "--name", "Tom"]).exit_code == 0
    cfg = Config.model_validate(
        {"vault": {"path": str(camp / "vault"), "folder": "Camp"}}
    )
    st = State(name="Tom")
    report = Vault(cfg, st).lint()
    assert report.link_count() >= OWN_LINKS_BADGE
    assert report.own_link_count() == 0
    assert "linked" not in new_badges(st, cfg)

    mine = "\n".join(f"- a line of mine about [[Map]] number {i}" for i in range(25))
    (camp / "vault" / "Camp" / "Mine.md").write_text(
        "---\ntitle: Mine\ndate: 2026-09-18\ntags: [note]\n---\n\n# Mine\n\n"
        f"## 2026-09-18\n\n{mine}\n",
        encoding="utf-8",
    )
    assert Vault(cfg, st).lint().own_link_count() >= OWN_LINKS_BADGE
    assert "linked" in new_badges(st, cfg)


def test_the_stub_names_the_command_that_checks_that_stop(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    ws = campaign.evenings()["winter"].workstreams[7]
    note = camp / "vault" / "Camp" / f"{safe_title(ws.name)}.md"
    assert "run `vibe check -w winter 8` when it is" in note.read_text("utf-8")
    first = campaign.evenings()["campus"].workstreams[0]
    campus = camp / "vault" / "Camp" / f"{safe_title(first.name)}.md"
    assert "run `vibe check 1` when it is" in campus.read_text("utf-8")


def test_an_imported_stop_stops_saying_it_is_not_done(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    ws = campaign.evenings()["winter"].workstreams[7]
    note = camp / "vault" / "Camp" / f"{safe_title(ws.name)}.md"
    assert "not done yet" in note.read_text(encoding="utf-8")
    code = encode_progress(name="T", done_w={"winter": list(range(1, 9))})
    env = dict(os.environ, VIBE_HOME=str(camp))
    out = subprocess.run(
        [sys.executable, "-m", "vibemap.cli", "import", code],
        cwd=camp,
        env=env,
        capture_output=True,
        text=True,
    )
    assert out.returncode == 0, out.stdout + out.stderr
    text = note.read_text(encoding="utf-8")
    assert "not done yet" not in text, text
    assert "imported" in text, text


def test_a_links_line_of_the_learners_own_counts(tmp_path: Path) -> None:
    """Only the links line vibe writes is generated; the learner's is theirs."""
    camp = _camp(tmp_path)
    ws = campaign.evenings()["winter"].workstreams[1]
    note = camp / "vault" / "Camp" / f"{safe_title(ws.name)}.md"
    text = note.read_text(encoding="utf-8")
    own = "\n".join(f"- {line}" for line in OWN_NOTE.strip().splitlines())
    own = own.replace("See [[Git]] and\n- [[Docker and containers]]", "See them")
    note.write_text(
        text.replace(
            f"- {stub_bullet('winter', ws.n)}",
            own + "\n- links: [[Git]], [[Docker and containers]], [[Tonight]]",
        ),
        encoding="utf-8",
    )
    output = _check(camp, "winter", 2)
    assert "pass" in output, output
    assert "fail" not in output, output


def test_a_claim_drops_the_stub_line_the_learner_wrote_around(tmp_path: Path) -> None:
    """The note keeps their paragraph and loses the line that contradicts it."""
    cfg = Config.model_validate({"vault": {"path": str(tmp_path), "folder": "G"}})
    v = Vault(cfg, State(name="T"))
    ws = campaign.evenings()["winter"].workstreams[0]
    common = {
        "summary": f"{ws.hour}, [[Evening 2]]. Outcome: {ws.outcome}.",
        "tags": ["workstream"],
        "sources": [u for _, u in ws.sources],
    }
    v.upsert_dated(
        ws.name,
        bullets=[stub_bullet("winter", ws.n), "links: [[Tonight]], [[Map]]"],
        **common,
    )
    note = v.path(ws.name)
    text = note.read_text(encoding="utf-8")
    note.write_text(
        text.replace(
            "- links: [[Tonight]], [[Map]]",
            "- links: [[Tonight]], [[Map]]\n" + OWN_NOTE.strip(),
        ),
        encoding="utf-8",
    )
    v.upsert_dated(ws.name, bullets=["done at 16:50", "built it"], **common)
    text = note.read_text(encoding="utf-8")
    assert "not done yet" not in text, text
    assert "done at 16:50" in text, text
    assert "the agent wrote the first draft" in text.lower(), text
    assert text.count(f"## {date.today().isoformat()}") == 1, text


def test_the_graph_groups_use_the_palette_and_not_the_banned_hues() -> None:
    """docs/DESIGN.md bans the cyan, violet and pink the graph used to carry."""
    from vibemap.palette import CSS_TOKENS, MUTED
    from vibemap.vault import GRAPH_GROUPS

    banned = {"#22D3EE", "#8B5CF6", "#A78BFA", "#F472B6", "#D1477D", "#C084FC"}
    known = {v.upper() for v in CSS_TOKENS.values() if v.startswith("#")}
    known |= {MUTED.upper()}
    known |= {c.upper() for c in _category_colours()}
    for query, colour in GRAPH_GROUPS:
        assert colour.upper() not in banned, query
        assert colour.upper() in known, (query, colour)


def _category_colours() -> list[str]:
    from vibemap.palette import CATEGORY_COLOURS

    return list(CATEGORY_COLOURS.values())
