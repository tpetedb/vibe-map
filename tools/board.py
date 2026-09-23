"""The board room and the shared memory: one reader for every session.

The room is an append-only Markdown file and the memory a JSONL knowledge graph,
both in the git common dir: never committed, the same two files for every
worktree and for both teams. `work/BOARD.md` is the protocol, the skill
`shared-memory` the how-to and `docs/adr/0018-shared-memory.md` the reasons.

    python3 tools/board.py read [--full] [--observe]   room, orders, memory digest
    python3 tools/board.py say --who "<model>, effort <e>, <role>, team:<t>" "..."
    python3 tools/board.py slot take|free <job> --who "..." [--note "..."]
    python3 tools/board.py memory-lint
    python3 tools/board.py mirror [--issue 95] [--dry-run]    a manager, never a hook
    python3 tools/board.py memory-serve -- <server command>   scripts/memory-mcp.sh

Standard library only, so a hook can run it with a bare python3.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import BinaryIO

ROOT = Path(__file__).resolve().parents[1]
HEADER = "== vibe-map board room and shared memory (tools/board.py read) =="
ROOM_HEAD = re.compile(
    r"^## (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z) \[([^\]\n]+)\]\s*$", re.M
)
KINDS = ("DECISION", "CLAIM", "CHECKPOINT", "LANDED", "QUESTION", "HANDOFF", "SLOT")
KIND_LINE = re.compile(rf"^(?:\d+\.\s+)?({'|'.join(KINDS)})\b", re.M)
SLOT_LINE = re.compile(r"^SLOT (take|free) job=(\S+)(.*)$", re.M)
LANDED_ORDER = re.compile(r"\bLANDED:?\s+`?([a-z0-9][a-z0-9-]{2,48})")
MARKER = re.compile(r"<!-- board-entry: ([0-9a-f]{8}) -->")
RECENT = 30
LINE = 150

# The memory's conventions; the skill `shared-memory` says them in prose.
MAX_ENTITIES = 300
MAX_OBSERVATIONS = 8
MAX_OBSERVATION = 200
DIGEST_BUDGET = 6000
NEWEST_DECISIONS = 10
NAME = re.compile(
    r"^(rule|gotcha|decision|contract|component|team):[a-z0-9][a-z0-9._/-]*$"
)
OBSERVATION = re.compile(
    r"^(\d{4}-\d{2}-\d{2}) \[team:(claude|codex|board)\] \S.*, src: \S.*$"
)
RELATIONS = {"owns", "depends_on", "supersedes", "documented_in"}
SECRET = re.compile(
    r"gh[pousr]_[A-Za-z0-9]{20,}|github_pat_\w{20,}|sk-[A-Za-z0-9_-]{20,}"
    r"|AKIA[0-9A-Z]{16}|xox[abprs]-[\w-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY"
    r"|(?i:\b(?:password|passwd|secret|token|api[_-]?key)\s*[:=]\s*\S{6,})"
)
# What the memory server changes on disk; read_graph dumps the whole graph into
# a context window, which is the cost this setup exists to avoid.
MUTATIONS = {
    "create_entities",
    "create_relations",
    "add_observations",
    "delete_entities",
    "delete_observations",
    "delete_relations",
}
REFUSED_TOOLS = {"read_graph"}
REFUSED_RESOURCE = "memory://knowledge-graph"
MUTATION_TIMEOUT = 60


# ---------------------------------------------------------------- where


def board_dir() -> Path:
    """The folder next to the git objects that every worktree shares."""
    if env := os.environ.get("VIBE_BOARD_DIR"):
        return Path(env)
    out = subprocess.run(
        [
            "git",
            "-C",
            str(ROOT),
            "rev-parse",
            "--path-format=absolute",
            "--git-common-dir",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(out.stdout.strip()) / "board"


def room_file() -> Path:
    return board_dir() / "ROOM.md"


def memory_file() -> Path:
    if env := os.environ.get("VIBE_MEMORY_FILE"):
        return Path(env)
    return board_dir() / "memory.jsonl"


@contextmanager
def locked(path: Path) -> Iterator[None]:
    """One writer at a time across processes, on a sibling lock file so the
    file itself can be replaced by rename while the lock is held."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path.with_name(path.name + ".lock"), "a", encoding="utf-8") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


# ---------------------------------------------------------------- the room


@dataclass(frozen=True, slots=True)
class Entry:
    at: str
    who: str
    body: str

    @property
    def id(self) -> str:
        """Derived from the entry itself, so it is the same in every reader and
        an append never changes the id of anything before it."""
        raw = f"{self.at}\n{self.who}\n{self.body}".encode()
        return hashlib.sha256(raw).hexdigest()[:8]

    @property
    def kinds(self) -> list[str]:
        return sorted(set(KIND_LINE.findall(self.body)), key=KINDS.index)


def parse_room(text: str) -> list[Entry]:
    heads = list(ROOM_HEAD.finditer(text))
    out = []
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        out.append(Entry(m[1], m[2].strip(), text[m.end() : end].strip()))
    return out


def entries() -> list[Entry]:
    try:
        return parse_room(room_file().read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []


def append(who: str, text: str, now: datetime | None = None) -> Entry:
    """One whole entry in one write, under the room's lock."""
    who, text = " ".join(who.split()), text.strip()
    if not who or "]" in who:
        raise ValueError(
            "--who is one line without ']', "
            "e.g. 'Opus 5.5, effort high, builder, team:claude'"
        )
    if not text or ROOM_HEAD.search(text):
        raise ValueError("the text is empty or carries an entry header of its own")
    at = (now or datetime.now(UTC)).strftime("%Y-%m-%dT%H:%M:%SZ")
    path = room_file()
    with locked(path):
        new = not path.exists()
        with open(path, "a", encoding="utf-8") as fh:
            if new:
                fh.write(
                    "# Board room: vibe-map\n\n"
                    "Append-only; the protocol is work/BOARD.md.\n"
                )
            fh.write(f"\n## {at} [{who}]\n\n{text}\n")
    return Entry(at, who, text)


def open_slots(room: list[Entry]) -> dict[str, tuple[Entry, str]]:
    """Reservations taken and not freed: the capacity authority. A process scan
    only cross-checks them (work/BOARD.md)."""
    held: dict[str, tuple[Entry, str]] = {}
    for e in room:
        for verb, job, rest in SLOT_LINE.findall(e.body):
            if verb == "take":
                held[job] = (e, rest.strip())
            else:
                held.pop(job, None)
    return held


def observed() -> list[str]:
    """Heavy-looking processes on this machine. Unknown stays unknown."""
    try:
        out = subprocess.run(
            ["ps", "-axo", "pid=,command="],
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return ["unknown: no process list here"]
    hits = [
        " ".join(line.split())[:LINE]
        for line in out.splitlines()
        if re.search(r"\bpytest\b|playwright", line) and "board.py" not in line
    ]
    return hits or ["none seen"]


def _short(text: str, width: int = LINE) -> str:
    text = " ".join(text.split())
    return text if len(text) <= width else text[: width - 3] + "..."


# ---------------------------------------------------------------- the memory


def load_graph(path: Path) -> tuple[list[dict], list[dict], list[str]]:
    """Entities, relations and whatever line could not be read."""
    ents: list[dict] = []
    rels: list[dict] = []
    bad: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return ents, rels, bad
    for n, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            bad.append(f"line {n}: not JSON")
            continue
        if not isinstance(item, dict):
            bad.append(f"line {n}: not an object")
        elif item.get("type") == "entity":
            obs = item.get("observations")
            if not isinstance(item.get("name"), str) or not isinstance(obs, list):
                bad.append(f"line {n}: an entity needs a name and observations")
            else:
                ents.append(item)
        elif item.get("type") == "relation":
            rels.append(item)
        else:
            bad.append(f"line {n}: type is neither entity nor relation")
    return ents, rels, bad


def lint(path: Path) -> list[str]:
    ents, rels, out = load_graph(path)
    if len(ents) > MAX_ENTITIES:
        out.append(
            f"{len(ents)} entities, the cap is {MAX_ENTITIES}: fold some into a doc"
        )
    names = [e["name"] for e in ents]
    out += [
        f"{n}: named twice" for n in sorted({n for n in names if names.count(n) > 1})
    ]
    for e in ents:
        name, obs = e["name"], e["observations"]
        if not NAME.match(name):
            out.append(
                f"{name}: a name is kind:slug, kind one of "
                "rule gotcha decision contract component team"
            )
        elif e.get("entityType") != name.split(":")[0]:
            out.append(f"{name}: entityType must be {name.split(':')[0]!r}")
        if len(obs) > MAX_OBSERVATIONS:
            out.append(
                f"{name}: {len(obs)} observations, the cap is {MAX_OBSERVATIONS}"
            )
        for o in obs:
            if (
                not isinstance(o, str)
                or not OBSERVATION.match(o)
                or len(o) > MAX_OBSERVATION
            ):
                out.append(
                    f"{name}: not 'YYYY-MM-DD [team:t] fact, src: pointer' "
                    f"under {MAX_OBSERVATION} characters: {str(o)[:60]!r}"
                )
    for e in ents:
        for text in (e["name"], *map(str, e["observations"])):
            if SECRET.search(text):
                out.append(
                    f"{e['name']}: a line looks like a secret; "
                    "remove it and rotate the value"
                )
                break
    known = set(names)
    for r in rels:
        ends = (r.get("from"), r.get("to"))
        if any(x not in known for x in ends):
            out.append(
                f"relation {ends[0]} -> {ends[1]}: "
                "points at an entity that does not exist"
            )
        if r.get("relationType") not in RELATIONS:
            out.append(
                f"relation {ends[0]} -> {ends[1]}: "
                f"type is one of {', '.join(sorted(RELATIONS))}"
            )
    return out


def _newest(entity: dict) -> str:
    dates = [m[1] for o in entity["observations"] if (m := OBSERVATION.match(str(o)))]
    return max(dates, default="")


def digest(path: Path, budget: int = DIGEST_BUDGET) -> str:
    """Every rule and gotcha, the newest decisions, one line each, under budget.
    What does not fit is one search away, and the last line says so."""
    ents, rels, _ = load_graph(path)
    head = (
        f"-- shared memory: {len(ents)} entities, {len(rels)} relations "
        "(search_nodes for more; read_graph is off)"
    )
    if not ents:
        return f"{head}\nno memory yet at {path}"
    groups = [
        (
            "rules",
            sorted(
                (e for e in ents if e["name"].startswith("rule:")),
                key=lambda e: e["name"],
            ),
        ),
        (
            "gotchas",
            sorted(
                (e for e in ents if e["name"].startswith("gotcha:")),
                key=lambda e: e["name"],
            ),
        ),
        (
            f"{NEWEST_DECISIONS} newest decisions",
            sorted(
                (e for e in ents if e["name"].startswith("decision:")),
                key=_newest,
                reverse=True,
            )[:NEWEST_DECISIONS],
        ),
    ]
    lines, used, left = [head], len(head), 0
    reserve = 160  # room for the closing line
    for title, group in groups:
        for i, e in enumerate(group):
            obs = [str(o) for o in e["observations"]]
            more = f" (+{len(obs) - 1} older)" if len(obs) > 1 else ""
            line = _short(f"- {e['name']}: {obs[-1] if obs else ''}{more}", 240)
            if i == 0:
                line = f"{title}:\n{line}"
            if used + len(line) + 1 > budget - reserve:
                left += len(group) - i
                break
            lines.append(line)
            used += len(line) + 1
    if left:
        lines.append(
            f"... {left} more not shown: "
            "search_nodes('rule:'), ('gotcha:') or ('decision:')"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------- read


def _tools_on_path() -> None:
    """tools/work.py is imported the way a hook's bare python3 finds it."""
    if str(ROOT / "tools") not in sys.path:
        sys.path.insert(0, str(ROOT / "tools"))


def orders_view() -> tuple[list[str], list[str]]:
    """Declared owns of checked-out orders, and landed ones, from tools/work.py."""
    try:
        _tools_on_path()
        import work  # noqa: PLC0415  only the reader needs it, not the memory proxy

        orders = sorted(work.active(), key=lambda o: o.id)
        done = sorted(work.landed())
    except Exception as e:  # noqa: BLE001  the reader must print, not fall over
        why = _short(f"{type(e).__name__}: {e}", 100)
        return [f"unknown ({why})"], [f"unknown ({why})"]
    rows = [
        _short(f"- {o.id} [{o.team}, {o.branch}] owns {', '.join(o.owns)}", 200)
        for o in orders
    ]
    return rows or ["none"], done


def read(full: bool = False, observe: bool = False) -> str:
    room = entries()
    out = [
        HEADER,
        "Protocol: work/BOARD.md. Write: just board-say. "
        "Memory: search_nodes with one keyword; never read_graph.",
        f"-- room: last {min(RECENT, len(room))} of {len(room)} entries "
        f"({room_file()})",
    ]
    for e in room[-RECENT:]:
        # The kinds up front unless the text already opens with them.
        kinds = "/".join(e.kinds)
        tag = f"{kinds}: " if kinds and not e.body.startswith(e.kinds[0]) else ""
        if full:
            out.append(f"[{e.id}] {e.at} [{e.who}]\n{tag}{e.body}\n")
        else:
            out.append(
                _short(f"[{e.id}] {e.at[5:16]} {e.who.split(',')[0]}: {tag}{e.body}")
            )
    owns, done = orders_view()
    out.append("-- checked out (a branch is checked out; not proof an agent is live):")
    out += owns
    out.append(
        f"-- landed (accepting review on origin/main): {', '.join(done) or 'none'}"
    )
    held = open_slots(room)
    out.append(
        "-- slots (explicit reservations, 4 heavy jobs across both teams): "
        f"{len(held)} held"
    )
    out += [
        _short(f"- {job} since {e.at[5:16]} by {e.who.split(',')[0]} {rest}")
        for job, (e, rest) in held.items()
    ]
    if observe:
        out.append("-- observed processes (a cross-check, never a reservation):")
        out += [f"- {line}" for line in observed()]
    out.append(digest(memory_file()))
    return "\n".join(out)


# ---------------------------------------------------------------- mirror


def to_mirror(room: list[Entry], posted: set[str], landed: set[str]) -> list[Entry]:
    """DECISION entries, and LANDED ones whose order work.py confirms, that the
    issue does not carry yet."""
    out = []
    for e in room:
        if e.id in posted:
            continue
        kinds = e.kinds
        if "DECISION" in kinds or (
            "LANDED" in kinds and any(o in landed for o in LANDED_ORDER.findall(e.body))
        ):
            out.append(e)
    return out


def mirror_body(e: Entry) -> str:
    return (
        f"[{e.who}]\n\nBoard room entry {e.id}, {e.at}:\n\n{e.body}\n\n"
        f"<!-- board-entry: {e.id} -->\n"
    )


def _gh(*args: str) -> str:
    return subprocess.run(
        ["gh", *args], capture_output=True, text=True, check=True
    ).stdout


# ---------------------------------------------------------------- memory proxy


def _request(line: bytes) -> dict | None:
    try:
        msg = json.loads(line)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    return msg if isinstance(msg, dict) and "method" in msg and "id" in msg else None


def serve(
    cmd: list[str],
    memory: Path,
    stdin: BinaryIO | None = None,
    stdout: BinaryIO | None = None,
) -> int:
    """Stand between a client and the memory server on stdio. Each mutation
    holds the memory's lock from request to response: the server reloads the
    file, changes it and renames a new one into place, so with every writer in
    every process behind one lock no write is lost. The whole-graph reads are
    answered here and never reach the server."""
    stdin = stdin or sys.stdin.buffer
    stdout = stdout or sys.stdout.buffer
    env = {**os.environ, "MEMORY_FILE_PATH": str(memory)}
    memory.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=env)
    assert proc.stdin and proc.stdout
    write = threading.Lock()
    waiting: dict[str, threading.Event] = {}

    def to_client(data: bytes) -> None:
        with write:
            stdout.write(data if data.endswith(b"\n") else data + b"\n")
            stdout.flush()

    def pump() -> None:
        for line in proc.stdout:
            to_client(line)
            try:
                msg = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            if isinstance(msg, dict) and "method" not in msg and "id" in msg:
                if ev := waiting.pop(json.dumps(msg["id"]), None):
                    ev.set()
        for ev in list(waiting.values()):
            ev.set()

    threading.Thread(target=pump, daemon=True).start()
    for line in stdin:
        msg = _request(line)
        method = msg and msg["method"]
        params = (msg or {}).get("params") or {}
        if msg and method == "tools/call" and params.get("name") in REFUSED_TOOLS:
            text = (
                "read_graph is off in this repository: search_nodes with one "
                "keyword or a prefix like 'gotcha:', or open_nodes by name."
            )
            to_client(
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "id": msg["id"],
                        "result": {
                            "content": [{"type": "text", "text": text}],
                            "isError": True,
                        },
                    }
                ).encode()
            )
            continue
        if msg and method == "resources/read" and params.get("uri") == REFUSED_RESOURCE:
            err = {
                "code": -32600,
                "message": "the whole graph is not served here: "
                "search_nodes or open_nodes",
            }
            to_client(
                json.dumps({"jsonrpc": "2.0", "id": msg["id"], "error": err}).encode()
            )
            continue
        try:
            if msg and method == "tools/call" and params.get("name") in MUTATIONS:
                done = threading.Event()
                waiting[json.dumps(msg["id"])] = done
                with locked(memory):
                    proc.stdin.write(line)
                    proc.stdin.flush()
                    done.wait(MUTATION_TIMEOUT)
                continue
            proc.stdin.write(line)
            proc.stdin.flush()
        except BrokenPipeError:
            break  # the server is gone; its exit code says why
    try:
        proc.stdin.close()
    except BrokenPipeError:
        pass
    return proc.wait()


# ---------------------------------------------------------------- commands


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="board", description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("read")
    r.add_argument(
        "--full", action="store_true", help="whole entries, not one line each"
    )
    r.add_argument("--observe", action="store_true", help="add the process cross-check")
    s = sub.add_parser("say")
    s.add_argument("--who", default=os.environ.get("BOARD_WHO", ""))
    s.add_argument("text")
    sl = sub.add_parser("slot")
    sl.add_argument("verb", choices=("take", "free"))
    sl.add_argument("job")
    sl.add_argument("--who", default=os.environ.get("BOARD_WHO", ""))
    sl.add_argument("--note", default="")
    sub.add_parser("memory-lint")
    m = sub.add_parser("mirror")
    m.add_argument("--issue", type=int, default=95)
    m.add_argument("--dry-run", action="store_true")
    sv = sub.add_parser("memory-serve")
    sv.add_argument("server", nargs=argparse.REMAINDER)
    a = p.parse_args(argv)

    if a.cmd == "read":
        try:
            print(read(a.full, a.observe))
        except Exception as e:  # noqa: BLE001  a session start must not fail on the board
            print(f"{HEADER}\nboard unreadable: {type(e).__name__}: {e}")
        return 0
    if a.cmd in ("say", "slot"):
        if a.cmd == "slot":
            if not re.fullmatch(r"[A-Za-z0-9._:/-]+", a.job):
                print(
                    "board: a job id is one word: letters, digits, . _ : / -",
                    file=sys.stderr,
                )
                return 2
            wt = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
            ).stdout.strip()
            a.text = f"SLOT {a.verb} job={a.job} worktree={wt or '?'} {a.note}".strip()
        try:
            e = append(a.who, a.text)
        except ValueError as err:
            print(f"board: {err}", file=sys.stderr)
            return 2
        print(f"board: entry {e.id} at {e.at}")
        return 0
    if a.cmd == "memory-lint":
        path = memory_file()
        problems = lint(path)
        for line in problems:
            print(f"memory: {line}")
        if not problems:
            n = len(load_graph(path)[0])
            print(
                f"memory ok: {n} entities in {path}"
                if path.exists()
                else f"memory ok: no file yet at {path}"
            )
        return 1 if problems else 0
    if a.cmd == "mirror":
        _tools_on_path()
        import work  # noqa: PLC0415

        bodies = _gh(
            "api",
            "--paginate",
            f"repos/{{owner}}/{{repo}}/issues/{a.issue}/comments",
            "--jq",
            ".[].body",
        )
        todo = to_mirror(entries(), set(MARKER.findall(bodies)), work.landed())
        for e in todo:
            if a.dry_run:
                print(mirror_body(e))
            else:
                _gh(
                    "api",
                    f"repos/{{owner}}/{{repo}}/issues/{a.issue}/comments",
                    "-f",
                    f"body={mirror_body(e)}",
                )
        print(
            f"board: {len(todo)} entries "
            f"{'would be ' if a.dry_run else ''}mirrored to #{a.issue}"
        )
        return 0
    cmd = a.server[1:] if a.server[:1] == ["--"] else a.server
    if not cmd:
        print("board: memory-serve -- <the server command>", file=sys.stderr)
        return 2
    return serve(cmd, memory_file())


if __name__ == "__main__":
    raise SystemExit(main())
