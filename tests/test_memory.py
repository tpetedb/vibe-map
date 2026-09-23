"""The shared memory: a digest that stays small, a lint that refuses what must
not be stored, and writes from several server processes that never lose one.

The server stand-in below keeps the real server's write pattern (load the
whole file, change it, rename a new file into place), which is exactly what
loses a write when two processes do it at once without a lock.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
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
    assert "search_nodes('rule:')" in text.splitlines()[-1]


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

SERVER = textwrap.dedent(
    """
    import json, os, sys
    path, log = os.environ["MEMORY_FILE_PATH"], os.environ["FAKE_LOG"]

    def note(text):
        fd = os.open(log, os.O_WRONLY | os.O_APPEND | os.O_CREAT)
        os.write(fd, (text + "\\n").encode())
        os.close(fd)

    for line in sys.stdin:
        msg = json.loads(line)
        if msg.get("method") != "tools/call":
            continue
        note(f"start {os.getpid()}")
        try:
            lines = open(path).read().splitlines()
        except FileNotFoundError:
            lines = []
        for e in msg["params"]["arguments"].get("entities", []):
            lines.append(json.dumps({"type": "entity", **e}))
        tmp = f"{path}.{os.getpid()}.tmp"
        with open(tmp, "w") as fh:
            fh.write("\\n".join(lines))
        os.replace(tmp, path)
        note(f"end {os.getpid()}")
        print(json.dumps({"jsonrpc": "2.0", "id": msg["id"], "result": {}}), flush=True)
    """
)

CLIENT = textwrap.dedent(
    """
    import json, subprocess, sys
    board, server, who, n = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
    p = subprocess.Popen(
        [sys.executable, board, "memory-serve", "--", sys.executable, server],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True,
    )
    for k in range(n):
        name = f"gotcha:{who}-{k}"
        call = {"name": "create_entities", "arguments": {"entities": [
            {"name": name, "entityType": "gotcha", "observations": []}]}}
        p.stdin.write(json.dumps({"jsonrpc": "2.0", "id": k, "method": "tools/call",
                                  "params": call}) + "\\n")
        p.stdin.flush()
        assert json.loads(p.stdout.readline())["id"] == k
    p.stdin.close()
    sys.exit(p.wait())
    """
)


def test_two_server_processes_writing_at_once_lose_nothing(tmp_path: Path) -> None:
    server = tmp_path / "server.py"
    server.write_text(SERVER, encoding="utf-8")
    memory, log = tmp_path / "board" / "memory.jsonl", tmp_path / "server.log"
    env = {**os.environ, "VIBE_MEMORY_FILE": str(memory), "FAKE_LOG": str(log)}
    n = 60
    clients = [
        subprocess.Popen(
            [sys.executable, "-c", CLIENT, str(BOARD), str(server), who, str(n)],
            env=env,
        )
        for who in ("claude", "codex")
    ]
    assert [c.wait(timeout=120) for c in clients] == [0, 0]

    names = {e["name"] for e in board.load_graph(memory)[0]}
    assert len(names) == 2 * n, f"{2 * n - len(names)} writes lost"
    # One writer at a time: every start is followed by its own end.
    events = log.read_text().split("\n")[:-1]
    assert len(events) == 4 * n
    for start, end in zip(events[::2], events[1::2], strict=True):
        assert start.startswith("start ") and end == "end " + start[6:]


def test_the_whole_graph_is_never_served(tmp_path: Path) -> None:
    server = tmp_path / "server.py"
    server.write_text(SERVER, encoding="utf-8")
    env = {
        **os.environ,
        "VIBE_MEMORY_FILE": str(tmp_path / "memory.jsonl"),
        "FAKE_LOG": str(tmp_path / "server.log"),
    }
    asks = [
        {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
         "params": {"name": "read_graph", "arguments": {}}},
        {"jsonrpc": "2.0", "id": 2, "method": "resources/read",
         "params": {"uri": "memory://knowledge-graph"}},
    ]  # fmt: skip
    run = subprocess.run(
        [sys.executable, str(BOARD), "memory-serve", "--", sys.executable, str(server)],
        input="".join(json.dumps(a) + "\n" for a in asks),
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    answers = {m["id"]: m for m in map(json.loads, run.stdout.splitlines())}
    assert answers[1]["result"]["isError"] is True
    assert "search_nodes" in answers[1]["result"]["content"][0]["text"]
    assert "search_nodes" in answers[2]["error"]["message"]
    assert not (tmp_path / "server.log").exists(), "neither reached the server"


SILENT = "import sys\nfor line in sys.stdin:\n    pass\n"


def test_a_server_that_never_answers_a_write_does_not_hold_the_lock(
    tmp_path: Path,
) -> None:
    """A hung server gets the write's time limit, not every session's writes:
    its client is told the write may not have happened, and the lock is free."""
    silent, server = tmp_path / "silent.py", tmp_path / "server.py"
    silent.write_text(SILENT, encoding="utf-8")
    server.write_text(SERVER, encoding="utf-8")
    env = {
        **os.environ,
        "VIBE_MEMORY_FILE": str(tmp_path / "board" / "memory.jsonl"),
        "FAKE_LOG": str(tmp_path / "server.log"),
        "VIBE_MEMORY_WRITE_TIMEOUT": "1",
    }
    call = {"name": "create_entities", "arguments": {"entities": [
        {"name": "gotcha:after-the-hang", "entityType": "gotcha", "observations": []}
    ]}}  # fmt: skip
    ask = json.dumps(
        {"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": call}
    )
    hung = subprocess.Popen(
        [sys.executable, str(BOARD), "memory-serve", "--", sys.executable, str(silent)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        env=env,
        text=True,
    )
    assert hung.stdin and hung.stdout
    hung.stdin.write(ask + "\n")
    hung.stdin.flush()
    try:
        # A second process writes while the first still waits on its server.
        run = subprocess.run(
            [sys.executable, "-c", CLIENT, str(BOARD), str(server), "late", "1"],
            env=env,
            timeout=20,
        )
        assert run.returncode == 0
        answer = json.loads(hung.stdout.readline())
        assert answer["id"] == 7 and "did not answer" in answer["error"]["message"]
    finally:
        hung.stdin.close()
        hung.wait(timeout=20)
    assert board.MUTATION_TIMEOUT <= 10
