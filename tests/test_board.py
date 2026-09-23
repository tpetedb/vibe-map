"""The board room: one append-only file every worktree shares, one reader.

The promises are about files and processes (two writers at once, a hook that
must never fail a session start), so the tests use real files and real
processes, never a mock of either.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
import tomllib
from pathlib import Path

import pytest

from tests.conftest import ROOT
from tools import board, sync_template

BOARD = ROOT / "tools" / "board.py"


@pytest.fixture
def room(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("VIBE_BOARD_DIR", str(tmp_path / "board"))
    monkeypatch.setenv("VIBE_MEMORY_FILE", str(tmp_path / "board" / "memory.jsonl"))
    return tmp_path / "board" / "ROOM.md"


def test_two_writers_at_once_leave_whole_entries_with_stable_ids(room: Path) -> None:
    writer = textwrap.dedent(
        """
        import sys
        sys.path.insert(0, sys.argv[1])
        import board
        who = sys.argv[2]
        for k in range(60):
            board.append(f"w {who}, team:claude", f"CHECKPOINT {who}-{k}\\nline {k}")
        """
    )
    env = {**os.environ, "VIBE_BOARD_DIR": str(room.parent)}
    procs = [
        subprocess.Popen(
            [sys.executable, "-c", writer, str(ROOT / "tools"), who], env=env
        )
        for who in ("a", "b")
    ]
    assert [p.wait(timeout=60) for p in procs] == [0, 0]

    first = board.entries()
    assert len(first) == 120
    for e in first:
        # Nothing of one entry leaked into another: the body is exactly two lines.
        tag = e.body.split()[1]
        assert e.who == f"w {tag.split('-')[0]}, team:claude"
        assert e.body == f"CHECKPOINT {tag}\nline {tag.split('-')[1]}"
        assert e.kinds == ["CHECKPOINT"]
    assert len({e.id for e in first}) == 120

    board.append("reader, team:codex", "QUESTION: still the same ids?")
    again = board.entries()
    assert [e.id for e in again[:120]] == [e.id for e in first]
    assert again[-1].kinds == ["QUESTION"]


def test_an_entry_cannot_forge_a_header_or_a_second_author(room: Path) -> None:
    with pytest.raises(ValueError, match="header"):
        board.append("x, team:claude", "hi\n## 2026-01-01T00:00:00Z [someone else]\n")
    with pytest.raises(ValueError, match="--who"):
        board.append("x] [y", "hi")
    with pytest.raises(ValueError, match="--who"):
        board.append("", "hi")
    assert not room.exists()


def test_the_reader_keeps_the_three_columns_apart(
    room: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for who, text in [
        ("Fable 5.1, team:claude", "DECISION: one reader for both teams"),
        ("Opus 5.5, team:claude", "SLOT take job=galaxy-verify worktree=/w/a"),
        ("Sol, team:codex", "SLOT take job=issue59-verify worktree=/w/b"),
        ("Sol, team:codex", "SLOT free job=issue59-verify worktree=/w/b"),
        ("Codex lead, team:codex", "SLOT: a free-form line is prose, not a slot"),
    ]:
        board.append(who, text)
    monkeypatch.setattr(
        board,
        "orders_view",
        lambda: (["- board-and-memory [harness, claude/b] owns tools/board.py"], []),
    )
    out = board.read()
    head, rest = out.split("-- checked out", 1)
    owns, rest = rest.split("-- landed", 1)
    landed, rest = rest.split("-- slots", 1)
    slots, memory = rest.split("-- shared memory", 1)
    assert out.startswith(board.HEADER)
    assert "DECISION: one reader for both teams" in head
    assert "not proof an agent is live" in owns and "owns tools/board.py" in owns
    assert "accepting review on origin/main" in landed and ": none" in landed
    assert "1 held" in slots and "galaxy-verify" in slots
    assert "issue59-verify" not in slots, "a freed slot is no longer held"
    assert "observed" not in out, "the process scan is asked for, never implied"
    assert "no memory yet" in memory

    monkeypatch.setattr(board, "observed", lambda: ["123 python -m pytest"])
    assert "- 123 python -m pytest" in board.read(observe=True)


def test_the_reader_reports_what_it_could_not_derive(
    room: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The reader imports tools/work.py as the hook's bare python3 would.
    monkeypatch.syspath_prepend(str(ROOT / "tools"))
    import work

    def broken(*_: object, **__: object) -> None:
        raise RuntimeError("no origin/main here")

    monkeypatch.setattr(work, "active", broken)
    owns, done = board.orders_view()
    assert owns == done == ["unknown (RuntimeError: no origin/main here)"]


def test_only_decisions_and_verified_landings_are_mirrored_once() -> None:
    room = board.parse_room(
        textwrap.dedent(
            """
            ## 2026-09-23T21:00:00Z [Fable 5.1, team:claude]

            1. DECISION (joint): one reader.

            ## 2026-09-23T21:01:00Z [Opus 5.5, team:claude]

            LANDED board-and-memory in PR #200.

            ## 2026-09-23T21:02:00Z [Opus 5.5, team:claude]

            LANDED not-accepted-yet in PR #201.

            ## 2026-09-23T21:03:00Z [usage monitor, team:board]

            USAGE: Claude session 6%
            """
        )
    )
    todo = board.to_mirror(room, posted=set(), landed={"board-and-memory"})
    assert [e.at[11:16] for e in todo] == ["21:00", "21:01"]
    again = board.to_mirror(room, posted={todo[0].id}, landed={"board-and-memory"})
    assert [e.at[11:16] for e in again] == ["21:01"]
    body = board.mirror_body(todo[0])
    assert body.startswith("[Fable 5.1, team:claude]\n")
    assert board.MARKER.findall(body) == [todo[0].id]


def _hook_commands() -> list[tuple[str, str]]:
    claude = json.loads((ROOT / ".claude" / "settings.json").read_text())
    codex = json.loads((ROOT / ".codex" / "hooks.json").read_text())
    out = []
    for name, cfg in (("claude", claude), ("codex", codex)):
        for group in cfg["hooks"]["SessionStart"]:
            assert set(group["matcher"].split("|")) >= {"startup", "resume", "compact"}
            out += [(name, h["command"]) for h in group["hooks"]]
    return out


@pytest.mark.parametrize("vendor", ["claude", "codex"])
def test_the_session_start_hook_prints_the_digest_with_no_memory_file(
    vendor: str, tmp_path: Path
) -> None:
    [cmd] = [c for v, c in _hook_commands() if v == vendor]
    assert "tools/board.py" in cmd and " read" in cmd
    env = {
        **os.environ,
        "CLAUDE_PROJECT_DIR": str(ROOT),
        "VIBE_BOARD_DIR": str(tmp_path / "nowhere"),
        "VIBE_MEMORY_FILE": str(tmp_path / "nowhere" / "memory.jsonl"),
    }
    run = subprocess.run(
        ["sh", "-c", cmd], cwd=ROOT, env=env, capture_output=True, text=True
    )
    assert run.returncode == 0, run.stderr
    assert run.stdout.startswith(board.HEADER)
    assert "-- shared memory: 0 entities" in run.stdout
    assert not (tmp_path / "nowhere").exists(), "a reader never creates the room"


def test_both_clients_start_the_same_memory_and_neither_can_dump_it() -> None:
    mcp = json.loads((ROOT / ".mcp.json").read_text())["mcpServers"]["memory"]
    codex = tomllib.loads((ROOT / ".codex" / "config.toml").read_text())
    server = codex["mcp_servers"]["memory"]
    assert "scripts/memory-mcp.sh" in " ".join(mcp["args"])
    assert "scripts/memory-mcp.sh" in " ".join(server["args"])
    assert server["disabled_tools"] == ["read_graph"]
    settings = json.loads((ROOT / ".claude" / "settings.json").read_text())
    assert "mcp__memory__read_graph" in settings["permissions"]["deny"]
    script = (ROOT / "scripts" / "memory-mcp.sh").read_text()
    assert "@modelcontextprotocol/server-memory@2026.8.31" in script
    assert "memory-serve" in script and "--git-common-dir" in script


def test_a_camp_gets_no_board_hook_no_memory_rule_and_no_memory_skill() -> None:
    camp = sync_template.camp_settings()
    assert "board.py" not in camp and "memory" not in camp
    assert "SessionStart" not in json.loads(camp)["hooks"]
    assert "shared-memory" in sync_template.PRODUCT_ONLY_SKILLS
    shipped = {dst.as_posix() for _, dst in sync_template.pairs()}
    assert not [p for p in shipped if "shared-memory" in p]
    assert not (sync_template.TEMPLATE / ".mcp.json").exists()
    assert not (sync_template.TEMPLATE / "_mcp.json").exists()
