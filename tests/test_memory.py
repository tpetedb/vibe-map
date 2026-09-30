"""The shared memory: a digest that stays small, a lint that refuses what must
not be stored, writes from several CLI processes that never lose one, and an
index that is derived, so rebuilding it twice changes nothing.

Every write loads the whole file, changes it and renames a new file into place,
which is exactly what loses a write when two processes do it at once without
the lock; the writer test runs real processes for that reason.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from tests.conftest import ROOT
from tools import board

BOARD = ROOT / "tools" / "board.py"


def _obs(day: int, text: str, team: str = "claude") -> str:
    return f"2026-09-{day:02d} [team:{team}] {text}, src: work/BOARD.md"


def _write(path: Path, entities: list[dict], relations: list[dict] = ()) -> Path:
    lines = [json.dumps({"type": "entity", **e}) for e in entities]
    lines += [json.dumps({"type": "relation", **r}) for r in relations]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _entity(name: str, *obs: str) -> dict:
    return {"name": name, "entityType": name.split(":")[0], "observations": list(obs)}


def test_the_digest_stays_under_budget_on_a_full_graph(tmp_path: Path) -> None:
    filler = "x" * 150
    ents = [
        _entity(
            f"{kind}:item-{n:03d}", *(_obs(1 + k, f"{filler} {k}") for k in range(8))
        )
        for kind in ("rule", "gotcha", "decision")
        for n in range(100)
    ]
    ents[-1]["observations"][-1] = _obs(30, "the newest decision")
    path = _write(tmp_path / "memory.jsonl", ents)
    assert board.lint(path) == []

    text = board.digest(path)
    assert len(text) < 6000
    assert text.startswith("-- shared memory: 300 entities, 0 relations")
    assert text.splitlines()[-1].startswith("... ")
    assert "memory search rule:" in text.splitlines()[-1]


def test_a_small_graph_shows_every_rule_and_gotcha_and_ten_newest_decisions(
    tmp_path: Path,
) -> None:
    ents = [_entity("rule:no-em-dashes", _obs(1, "no em-dashes in copy"))]
    ents += [_entity("gotcha:gh-merge-auto", _obs(2, "old"), _obs(3, "gh pr merge"))]
    ents += [
        _entity(f"decision:d{n:02d}", _obs(n + 1, f"decided {n}")) for n in range(12)
    ]
    ents += [_entity("component:tools/board.py", _obs(4, "the reader"))]
    text = board.digest(_write(tmp_path / "memory.jsonl", ents))
    assert "- rule:no-em-dashes: 2026-09-01" in text
    assert "- gotcha:gh-merge-auto: 2026-09-03 [team:claude] gh pr merge" in text
    assert "(+1 older)" in text
    shown = [n for n in range(12) if f"decision:d{n:02d}:" in text]
    assert shown == list(range(2, 12)), "the ten newest, not the first ten"
    assert "component:" not in text, "components are searched for, not pushed"


def test_the_lint_passes_a_good_graph_and_a_missing_file(tmp_path: Path) -> None:
    good = _write(
        tmp_path / "memory.jsonl",
        [_entity("rule:a", _obs(1, "a")), _entity("component:tools/board.py")],
        [
            {
                "from": "rule:a",
                "to": "component:tools/board.py",
                "relationType": "documented_in",
            }
        ],
    )
    assert board.lint(good) == []
    assert board.lint(tmp_path / "absent.jsonl") == []


@pytest.mark.parametrize(
    ("entities", "relations", "says"),
    [
        (
            [_entity(f"gotcha:g{n}", _obs(1, "x")) for n in range(301)],
            [],
            "301 entities, the cap is 300",
        ),
        (
            [_entity("rule:a", *(_obs(1, f"f{n}") for n in range(9)))],
            [],
            "9 observations",
        ),
        ([_entity("rule:a", "remember to be kind")], [], "src: pointer"),
        ([_entity("rule:a", _obs(1, "y" * 200))], [], "under 200"),
        ([_entity("Rule:A", _obs(1, "x"))], [], "kind:slug"),
        (
            [_entity("gotcha:ci", _obs(1, "token: ghp_" + "a" * 36))],
            [],
            "looks like a secret",
        ),
        (
            [_entity("gotcha:ci", _obs(1, "the password = hunter2hunter2"))],
            [],
            "looks like a secret",
        ),
        (
            [_entity("rule:a", _obs(1, "x"))],
            [{"from": "rule:a", "to": "rule:gone", "relationType": "supersedes"}],
            "does not exist",
        ),
        (
            [_entity("rule:a", _obs(1, "x")), _entity("rule:b", _obs(1, "x"))],
            [{"from": "rule:a", "to": "rule:b", "relationType": "likes"}],
            "type is one of",
        ),
    ],
)
def test_the_lint_refuses(
    tmp_path: Path, entities: list[dict], relations: list[dict], says: str
) -> None:
    problems = board.lint(_write(tmp_path / "memory.jsonl", entities, relations))
    assert any(says in p for p in problems), problems


def test_the_lint_command_fails_on_a_malformed_line(tmp_path: Path) -> None:
    bad = tmp_path / "memory.jsonl"
    bad.write_text('{"type":"entity","name":"rule:a"\n', encoding="utf-8")
    run = subprocess.run(
        [sys.executable, str(BOARD), "memory-lint"],
        env={**os.environ, "VIBE_MEMORY_FILE": str(bad)},
        capture_output=True,
        text=True,
    )
    assert run.returncode == 1 and "line 1: not JSON" in run.stdout


# ---------------------------------------------------------------- writers


@pytest.fixture
def memory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    path = tmp_path / "board" / "memory.jsonl"
    monkeypatch.setenv("VIBE_MEMORY_FILE", str(path))
    return path


def _orders_root(tmp_path: Path) -> Path:
    """A checkout with four orders, one in each state a folder can say."""
    root = tmp_path / "checkout"
    (root / "work").mkdir(parents=True)
    (root / "work" / "teams.toml").write_bytes((ROOT / "work/teams.toml").read_bytes())
    for oid, builder, verdict in (
        ("alpha-open", "", ""),
        ("bravo-building", "builder-b", ""),
        ("charlie-improve", "builder-c", "improve"),
        ("delta-accepted", "builder-d", "accept"),
    ):
        folder = root / "work" / "orders" / oid
        folder.mkdir(parents=True)
        (folder / "order.toml").write_text(
            f'v = 1\nid = "{oid}"\ntitle = "About {oid}"\nteam = "harness"\n'
            f'branch = "b/{oid}"\ngoal = ""\nbuilder = "{builder}"\n'
            f'owns = ["tools/{oid}.py"]\ncross = []\nneeds = []\n\n'
            '[[criteria]]\nid = "c1"\ntext = "t"\ncheck = "true"\n',
            encoding="utf-8",
        )
        if verdict:
            (folder / "review.toml").write_text(f'verdict = "{verdict}"\n')
    return root


def test_add_makes_an_entity_then_appends_and_replaces(memory: Path) -> None:
    day = board.datetime(2026, 9, 24, tzinfo=board.UTC_ZONE)
    board.remember("gotcha:gh-merge", "gh pr merge is denied", "claude", "PR #192",
                   now=day)  # fmt: skip
    board.remember("gotcha:gh-merge", "hand Tom the command", "codex", "ROOM 1a2b",
                   now=day, relate=("documented_in=gotcha:gh-merge",))  # fmt: skip
    [e], [r], _ = board.load_graph(memory)
    assert e["entityType"] == "gotcha"
    assert e["observations"] == [
        "2026-09-24 [team:claude] gh pr merge is denied, src: PR #192",
        "2026-09-24 [team:codex] hand Tom the command, src: ROOM 1a2b",
    ]
    assert r == {"type": "relation", "from": "gotcha:gh-merge",
                 "to": "gotcha:gh-merge", "relationType": "documented_in"}  # fmt: skip
    board.remember("gotcha:gh-merge", "merge by hand", "board", "ADR 18",
                   replace="is denied", now=day)  # fmt: skip
    [e], _, _ = board.load_graph(memory)
    assert [o.split("] ")[1] for o in e["observations"]] == [
        "hand Tom the command, src: ROOM 1a2b",
        "merge by hand, src: ADR 18",
    ]
    assert board.lint(memory) == []


@pytest.mark.parametrize(
    ("name", "fact", "relate", "says"),
    [
        ("Rule:A", "x", (), "kind:slug"),
        ("rule:a", "api_key = abcdefgh1234", (), "looks like a secret"),
        ("rule:a", "y" * 200, (), "under 200"),
        ("rule:full", "the ninth", (), "9 observations"),
        ("rule:a", "x", ("likes=rule:full",), "type is one of"),
        ("rule:a", "x", ("supersedes=rule:gone",), "does not exist"),
        ("rule:a", "x", ("supersedes",), "type=kind:slug"),
    ],
)
def test_add_refuses_a_write_that_would_break_the_lint_and_writes_nothing(
    memory: Path, name: str, fact: str, relate: tuple[str, ...], says: str
) -> None:
    _write(memory.parent.mkdir(parents=True) or memory,
           [_entity("rule:full", *(_obs(1, f"f{n}") for n in range(8)))])  # fmt: skip
    before = memory.read_bytes()
    with pytest.raises(ValueError, match=says):
        board.remember(name, fact, "claude", "work/BOARD.md", relate=relate)
    assert memory.read_bytes() == before
    assert not board.index_file().exists()


def test_the_index_is_derived_from_the_memory_and_the_orders_and_idempotent(
    memory: Path, tmp_path: Path
) -> None:
    root = _orders_root(tmp_path)
    board.remember("decision:old", "first", "claude", "ROOM 1", root=root)
    board.remember("decision:new", "about bravo-building", "codex", "ROOM 2",
                   relate=("supersedes=decision:old",), root=root)  # fmt: skip
    for n in range(8):
        board.remember("gotcha:big", f"fact {n}", "board", "ROOM 3", root=root)
    first = board.index_file().read_bytes()
    assert board.reindex(root) == 7
    assert board.index_file().read_bytes() == first, "rebuilding changes nothing"

    rows = {r["id"]: r for r in json.loads(first)["rows"]}
    assert list(rows) == sorted(rows)
    assert all(set(r) == {"id", "order", "topic", "owner", "status", "next"}
               for r in rows.values())  # fmt: skip
    assert rows["order:alpha-open"]["status"] == "open"
    assert rows["order:bravo-building"]["owner"] == "team:harness, builder-b"
    assert rows["order:bravo-building"]["status"] == "building"
    assert rows["order:charlie-improve"]["status"] == "improve"
    assert rows["order:delta-accepted"]["next"] == "work-accept, then land"
    assert rows["decision:new"] == {
        "id": "decision:new", "order": "bravo-building", "topic": "decision",
        "owner": "team:codex", "status": "current", "next": "",
    }  # fmt: skip
    assert rows["decision:old"]["status"] == "superseded"
    assert rows["gotcha:big"]["next"] == "fold into a doc"


def test_search_finds_entities_and_orders_by_every_word(
    memory: Path, tmp_path: Path
) -> None:
    root = _orders_root(tmp_path)
    board.remember("gotcha:sync-main", "take either side of a generated file",
                   "claude", "tools/sync_main.py", root=root)  # fmt: skip
    board.remember("rule:no-em-dashes", "no em-dashes", "claude", "AGENTS.md",
                   root=root)  # fmt: skip
    [hit] = board.search("GENERATED")
    assert hit.startswith("- gotcha:sync-main: 2026-") and "either side" in hit
    assert board.search("gotcha: generated side")[0].startswith("- gotcha:sync-main")
    assert board.search("nothing like this") == []
    assert board.search("bravo building") == [
        "- order:bravo-building [building] About bravo-building; "
        "next: work-check OK, then a review"
    ]
    full = board.search("sync-main", full=True)
    assert full[0] == "- gotcha:sync-main" and full[1].startswith("    2026-")


def test_the_writers_refuse_under_an_older_python(
    memory: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(board.sys, "version_info", (3, 9, 6))
    with pytest.raises(ValueError, match="needs Python 3.11"):
        board.remember("rule:a", "x", "claude", "s")
    assert not memory.exists()


WRITER = """
import sys
from pathlib import Path
# tools/ first, as for python3 tools/board.py: work/ is a folder here too
sys.path[:0] = [sys.argv[1] + "/tools", sys.argv[1]]
from tools import board
who, n, board.ROOT = sys.argv[2], int(sys.argv[3]), Path(sys.argv[4])
for k in range(n):
    argv = ["memory", "add", f"gotcha:{who}-{k}", f"write {k} of {who}",
            "--team", who, "--src", "tests/test_memory.py"]
    assert board.main(argv) == 0
"""


def test_two_cli_writers_at_once_lose_nothing(memory: Path, tmp_path: Path) -> None:
    """Each process runs the command line's main in a loop over a small checkout,
    so the two write as fast as they can and their writes overlap: without the
    lock this loses writes on every run."""
    n, root = 100, _orders_root(tmp_path)
    writers = [
        subprocess.Popen(
            [sys.executable, "-c", WRITER, str(ROOT), who, str(n), str(root)],
            stdout=subprocess.DEVNULL,
        )
        for who in ("claude", "codex")
    ]
    assert [w.wait(timeout=120) for w in writers] == [0, 0]

    names = {e["name"] for e in board.load_graph(memory)[0]}
    assert len(names) == 2 * n, f"{2 * n - len(names)} writes lost"
    assert board.lint(memory) == []
    rows = json.loads(board.index_file().read_text())["rows"]
    assert {r["id"] for r in rows if not r["id"].startswith("order:")} == names
    assert not list(memory.parent.glob("*.tmp")), "no half-written file is left"
