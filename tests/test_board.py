"""The board room: one append-only file every worktree shares, one reader.

The promises are about files and processes (two writers at once, a hook that
must never fail a session start), so the tests use real files and real
processes, never a mock of either.
"""

from __future__ import annotations

import errno
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
    # The small, current sections first and the memory before the long lists,
    # so nothing that cuts the text short ever cuts the memory.
    head, rest = out.split("-- slots", 1)
    slots, rest = rest.split("-- shared memory", 1)
    memory, rest = rest.split("-- room", 1)
    room_part, rest = rest.split("-- checked out", 1)
    owns, landed = rest.split("-- landed", 1)
    assert out.startswith(board.HEADER)
    assert "DECISION: one reader for both teams" in room_part
    assert "not proof an agent is live" in owns and "owns tools/board.py" in owns
    assert "accepting review on origin/main" in landed and ": none" in landed
    assert "1 held" in slots and "galaxy-verify" in slots
    assert "issue59-verify" not in slots, "a freed slot is no longer held"
    assert "observed" not in out, "the process scan is asked for, never implied"
    assert "no memory yet" in memory

    monkeypatch.setattr(board, "observed", lambda: ["123 python -m pytest"])
    assert "- 123 python -m pytest" in board.read(observe=True)


def test_the_whole_session_start_text_fits_the_budget_and_keeps_the_memory(
    room: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Claude Code hands a model at most 10,000 characters of hook stdout and a
    2,000-character preview beyond that, so the reader caps the whole text."""
    for k in range(40):
        board.append(f"Opus 5.5, team:claude {k}", f"CHECKPOINT {k} " + "y" * 400)
    rows = [
        f"- order-{k:02d} [harness, b/{k:02d}] owns " + "z" * 300 for k in range(40)
    ]
    landed = [f"landed-{k:03d}" for k in range(120)]
    monkeypatch.setattr(board, "orders_view", lambda: (rows, landed))
    obs = "2026-09-{:02d} [team:claude] " + "x" * 150 + ", src: work/BOARD.md"
    lines = [
        json.dumps(
            {
                "type": "entity",
                "name": f"{kind}:item-{n:03d}",
                "entityType": kind,
                "observations": [obs.format(1 + k) for k in range(8)],
            }
        )
        for kind in ("rule", "gotcha", "decision")
        for n in range(100)
    ]
    board.memory_file().write_text("\n".join(lines), encoding="utf-8")

    out = board.read()
    assert len(out) + 1 < 10_000
    assert len(out) + 1 <= board.READ_BUDGET
    assert board.digest(board.memory_file()) in out, "the memory is never cut"
    assert "CHECKPOINT 39 " in out, "the newest room entry is shown"
    assert "CHECKPOINT 0 " not in out
    assert "board --full" in out, "what was left out says where it is"
    assert "landed-000" in out and "120" in out.split("-- landed", 1)[1]

    full = board.read(full=True)
    assert "CHECKPOINT 10 " in full and "order-39" in full and "landed-119" in full


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


# Every start source each client documents: Claude Code's hooks reference lists
# fork as well, Codex's does not.
SOURCES = {
    "claude": {"startup", "resume", "clear", "compact", "fork"},
    "codex": {"startup", "resume", "clear", "compact"},
}


def _hooks(vendor: str) -> dict:
    path = {"claude": ".claude/settings.json", "codex": ".codex/hooks.json"}[vendor]
    return json.loads((ROOT / path).read_text())["hooks"]


def _hook_commands() -> list[tuple[str, str]]:
    out = []
    for name in ("claude", "codex"):
        for group in _hooks(name)["SessionStart"]:
            assert set(group["matcher"].split("|")) == SOURCES[name]
            out += [(name, h["command"]) for h in group["hooks"]]
    return out


def test_codex_keeps_the_work_order_hooks_it_already_runs() -> None:
    """Tracking .codex/hooks.json replaces the untracked copy a checkout had,
    which carried Codex's work-order hooks; the tracked file must carry them."""
    claude, codex = _hooks("claude"), _hooks("codex")
    for event in ("PreToolUse", "PostToolUse", "SubagentStop", "Stop"):
        assert codex.get(event) == claude[event], event
    assert set(codex) == {"SessionStart", "PreToolUse", "PostToolUse"} | {
        "SubagentStop",
        "Stop",
    }


def _hook_env(vendor: str, tmp_path: Path) -> dict[str, str]:
    env = {
        **os.environ,
        "VIBE_BOARD_DIR": str(tmp_path / "nowhere"),
        "VIBE_MEMORY_FILE": str(tmp_path / "nowhere" / "memory.jsonl"),
    }
    # Codex sets no CLAUDE_PROJECT_DIR; its hooks run in the session's cwd.
    env.pop("CLAUDE_PROJECT_DIR", None)
    if vendor == "claude":
        env["CLAUDE_PROJECT_DIR"] = str(ROOT)
    return env


@pytest.mark.parametrize("vendor", ["claude", "codex"])
def test_the_session_start_hook_prints_the_digest_with_no_memory_file(
    vendor: str, tmp_path: Path
) -> None:
    [cmd] = [c for v, c in _hook_commands() if v == vendor]
    assert "tools/board.py" in cmd and " read" in cmd
    env = _hook_env(vendor, tmp_path)
    run = subprocess.run(
        ["sh", "-c", cmd], cwd=ROOT, env=env, capture_output=True, text=True
    )
    assert run.returncode == 0, run.stderr
    assert run.stdout.startswith(board.HEADER)
    assert "-- shared memory: 0 entities" in run.stdout
    assert not (tmp_path / "nowhere").exists(), "a reader never creates the room"


def _python_older_than_311() -> str | None:
    """An interpreter a hook's bare python3 may be: macOS ships 3.9 in /usr/bin."""
    found = subprocess.run(
        ["uv", "python", "find", "--no-project", ">=3.9,<3.11"],
        capture_output=True,
        text=True,
    ).stdout.strip()
    for exe in (found, "/usr/bin/python3"):
        if not exe or not Path(exe).exists():
            continue
        ver = subprocess.run(
            [exe, "-c", "import sys; print(sys.version_info >= (3, 11))"],
            capture_output=True,
            text=True,
        ).stdout.strip()
        if ver == "False":
            return exe
    return None


@pytest.mark.parametrize("vendor", ["claude", "codex"])
def test_the_session_start_hook_reads_under_an_older_python3(
    vendor: str, tmp_path: Path
) -> None:
    old = _python_older_than_311()
    if old is None:
        pytest.skip("no Python older than 3.11 on this machine")
    shim = tmp_path / "bin"
    shim.mkdir()
    (shim / "python3").symlink_to(old)
    git = subprocess.run(["which", "git"], capture_output=True, text=True).stdout
    path = os.pathsep.join([str(shim), str(Path(git.strip()).parent), "/bin"])
    [cmd] = [c for v, c in _hook_commands() if v == vendor]
    env = {**_hook_env(vendor, tmp_path), "PATH": path}
    run = subprocess.run(
        ["sh", "-c", cmd], cwd=ROOT, env=env, capture_output=True, text=True
    )
    assert run.returncode == 0, run.stderr
    assert run.stdout.startswith(board.HEADER), run.stdout + run.stderr
    assert "-- shared memory: 0 entities" in run.stdout
    assert "tools/work.py needs Python 3.11" in run.stdout


def test_no_memory_server_is_registered_and_no_writable_root_is_tracked() -> None:
    """The memory is files and board.py (DECISION #193 section 4): neither client
    starts a server. The tracked Codex config names no writable root: a relative
    one is not a directory in a linked worktree, whose .git is a file, and Codex
    then refuses every shell tool (amended A2). just codex adds the board."""
    assert not (ROOT / ".mcp.json").exists()
    assert not (ROOT / "scripts" / "memory-mcp.sh").exists()
    codex = tomllib.loads((ROOT / ".codex" / "config.toml").read_text())
    assert "mcp_servers" not in codex
    assert "writable_roots" not in codex.get("sandbox_workspace_write", {})
    assert "writable_roots" not in json.dumps(codex)
    settings = json.loads((ROOT / ".claude" / "settings.json").read_text())
    assert "mcp__memory" not in json.dumps(settings)
    assert "memory-serve" not in BOARD.read_text()


def test_a_camp_gets_no_board_hook_and_no_memory_skill() -> None:
    camp = sync_template.camp_settings()
    assert "board.py" not in camp and "memory" not in camp
    assert "SessionStart" not in json.loads(camp)["hooks"]
    assert "shared-memory" in sync_template.PRODUCT_ONLY_SKILLS
    shipped = {dst.as_posix() for _, dst in sync_template.pairs()}
    assert not [p for p in shipped if "shared-memory" in p]
    assert not (sync_template.TEMPLATE / ".mcp.json").exists()
    assert not (sync_template.TEMPLATE / "_mcp.json").exists()


def test_a_linked_worktree_reads_and_writes_the_same_room(tmp_path: Path) -> None:
    main, linked = tmp_path / "main", tmp_path / "linked"

    def git(*args: str, cwd: Path = main) -> None:
        subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True)

    (main / "tools").mkdir(parents=True)
    git("init", "-q", "-b", "main")
    (main / "tools" / "board.py").write_bytes(BOARD.read_bytes())
    git("add", ".")
    git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "board")
    git("worktree", "add", "-q", "-b", "other", str(linked))
    env = {
        k: v
        for k, v in os.environ.items()
        if k not in ("VIBE_BOARD_DIR", "VIBE_MEMORY_FILE")
    }

    def run(where: Path, *args: str) -> str:
        return subprocess.run(
            [sys.executable, str(where / "tools" / "board.py"), *args],
            cwd=where,
            env=env,
            capture_output=True,
            text=True,
            check=True,
        ).stdout

    run(linked, "say", "--who", "linked, team:codex", "QUESTION: do you see me?")
    from_main, from_linked = run(main, "read"), run(linked, "read")
    assert from_main == from_linked
    assert f"({main.resolve()}/.git/board/ROOM.md)" in from_main
    assert "QUESTION: do you see me?" in from_main
    assert f"{main.resolve()}/.git/board/memory.jsonl" in from_main


def _recipe(name: str) -> str:
    text = (ROOT / "justfile").read_text()
    return text.split(f"\n{name}", 1)[1].split("\n\n", 1)[0]


@pytest.fixture
def codex_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A temporary HOME, so no test reads or writes the real ~/.codex."""
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.delenv("CODEX_HOME", raising=False)
    return tmp_path / "home" / ".codex" / "config.toml"


def test_just_codex_goes_through_the_launcher_and_names_the_flag() -> None:
    assert "python3 tools/board.py codex" in _recipe("codex *args:")
    assert "codex-trust" not in (ROOT / "justfile").read_text()
    assert board.CODEX_FLAG in (ROOT / "work" / "BOARD.md").read_text()


def test_the_hooks_count_as_on_only_when_trusted_and_approved(
    tmp_path: Path,
) -> None:
    top, cfg = Path("/r/wt"), tmp_path / "config.toml"
    assert not board.codex_hooks_on(top, cfg)
    project = '[projects."/r/wt"]\ntrust_level = "trusted"\n'
    cfg.write_text(project)
    assert not board.codex_hooks_on(top, cfg)
    cfg.write_text(
        project
        + '[hooks.state."/r/wt/.codex/hooks.json:pre_tool_use:0:0"]\n'
        + 'trusted_hash = "sha256:1"\n'
    )
    assert not board.codex_hooks_on(top, cfg)
    cfg.write_text(
        project
        + '[hooks.state."/r/wt/.codex/hooks.json:session_start:0:0"]\n'
        + 'trusted_hash = "sha256:1"\n'
    )
    assert board.codex_hooks_on(top, cfg)
    assert not board.codex_hooks_on(Path("/r/other"), cfg)


def test_a_linked_worktree_counts_the_main_checkouts_hooks(tmp_path: Path) -> None:
    # Codex loads a linked worktree's project hooks from the main checkout and
    # keys their /hooks trust by that path; the worktree inherits its trust.
    top, root, cfg = Path("/r/wt"), Path("/r"), tmp_path / "config.toml"
    approved = '[hooks.state."{}/.codex/hooks.json:session_start:0:0"]\n'
    approved += 'trusted_hash = "sha256:1"\n'
    for trusted in ("/r/wt", "/r"):
        project = f'[projects."{trusted}"]\ntrust_level = "trusted"\n'
        cfg.write_text(project + approved.format("/r/wt"))
        assert not board.codex_hooks_on(top, cfg, root)
        cfg.write_text(project + approved.format("/r"))
        assert board.codex_hooks_on(top, cfg, root)
    cfg.write_text(
        '[projects."/r/wt"]\ntrust_level = "untrusted"\n'
        + '[projects."/r"]\ntrust_level = "trusted"\n'
        + approved.format("/r")
    )
    assert not board.codex_hooks_on(top, cfg, root)


def test_the_hooks_root_is_the_main_checkout(tmp_path: Path) -> None:
    main, linked = tmp_path / "main", tmp_path / "main" / "wt"
    subprocess.run(["git", "init", "-q", "-b", "main", str(main)], check=True)
    subprocess.run(
        ["git", "-C", str(main), "-c", "user.name=t", "-c", "user.email=t@t"]
        + ["commit", "-q", "--allow-empty", "-m", "root"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(main), "worktree", "add", "-q", "-b", "o", str(linked)],
        check=True,
    )
    assert board.codex_hooks_root(main) == main.resolve()
    assert board.codex_hooks_root(linked) == main.resolve()


@pytest.mark.parametrize(
    ("args", "rest", "prompt"),
    [
        ([], [], None),
        (["fix it"], [], "fix it"),
        (["-m", "gpt", "fix it"], ["-m", "gpt"], "fix it"),
        (["-c", "a=1", "--search"], ["-c", "a=1", "--search"], None),
        (["-i", "a.png", "b.png"], ["-i", "a.png", "b.png"], None),
        (["--no-alt-screen", "--", "-x"], ["--no-alt-screen"], "-x"),
    ],
)
def test_the_digest_leads_the_first_prompt_of_a_new_session(
    args: list[str], rest: list[str], prompt: str | None
) -> None:
    b = Path("/r/.git/board")
    argv = board.codex_argv(args, b, "DIGEST")
    assert argv[: len(rest) + 1] == ["codex", *rest]
    assert argv[len(rest) + 1 : -1] == ["--add-dir", str(b)]
    fed = argv[-1]
    assert fed.startswith(board.CODEX_FED) and "\n\nDIGEST" in fed
    assert fed.endswith(f"\n\n{prompt}" if prompt else "DIGEST")


@pytest.mark.parametrize(
    "args", [["resume", "--last"], ["-m", "gpt", "fork", "abc"], ["exec", "hi"]]
)
def test_a_subcommand_and_hooks_that_run_get_no_fed_digest(args: list[str]) -> None:
    b = Path("/r/.git/board")
    assert board.codex_argv(args, b, "DIGEST") == ["codex", *args, "--add-dir", str(b)]
    assert board.codex_argv(["hi"], b, None) == ["codex", "hi", "--add-dir", str(b)]


def test_the_launcher_feeds_the_digest_where_the_hooks_are_off(
    room: Path, codex_home: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen: list[list[str]] = []
    monkeypatch.setattr(board.os, "execvp", lambda _f, argv: seen.append(argv))
    board.launch_codex(["hello"])
    (argv,) = seen
    assert argv[1:3] == ["--add-dir", str(room.parent.resolve())]
    assert room.parent.is_dir()
    assert board.HEADER in argv[-1] and argv[-1].endswith("\n\nhello")


@pytest.mark.parametrize(
    "args",
    [
        ["say", "--who", "Sol, team:codex", "QUESTION: may I write?"],
        ["slot", "take", "a-job", "--who", "Sol, team:codex"],
        ["memory", "add", "gotcha:x", "a fact", "--team", "codex", "--src", "PR #1"],
    ],
)
@pytest.mark.skipif(os.geteuid() == 0, reason="root writes through a read-only mode")
def test_a_refused_write_names_the_launch_flag_in_one_line(
    tmp_path: Path, args: list[str]
) -> None:
    """A sandbox that does not grant the board refuses the write; the writer
    says how to launch, in one line, and never prints a traceback."""
    folder = tmp_path / "board"
    folder.mkdir()
    folder.chmod(0o500)
    env = {
        **os.environ,
        "VIBE_BOARD_DIR": str(folder),
        "VIBE_MEMORY_FILE": str(folder / "memory.jsonl"),
    }
    try:
        run = subprocess.run(
            [sys.executable, str(BOARD), *args],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
        )
    finally:
        folder.chmod(0o700)
    assert run.returncode == 2, run.stdout + run.stderr
    assert "Traceback" not in run.stderr
    assert run.stderr.count("\n") == 1, run.stderr
    assert board.CODEX_FLAG in run.stderr
    assert not list(folder.iterdir())


def test_a_sandbox_refusal_is_told_the_flag_and_other_failures_are_not() -> None:
    for code in (errno.EPERM, errno.EACCES, errno.EROFS):
        err = PermissionError(code, os.strerror(code), "/r/.git/board/ROOM.md")
        line = board.refused(err)
        assert "\n" not in line and board.CODEX_FLAG in line, line
    other = board.refused(OSError(errno.ENOSPC, os.strerror(errno.ENOSPC), "/r"))
    assert "--add-dir" not in other and "\n" not in other


def test_the_session_start_text_tells_codex_the_launch() -> None:
    assert "just codex" in board.read() and board.CODEX_FLAG in board.read()
