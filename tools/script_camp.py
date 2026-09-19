"""Write into a camp the deliverables a learner would have built, so every
check passes.

This is the one home for the scripted set. The tests use it to prove the
checks can go green, and the nightly regeneration of the played instance uses
it so a fresh camp has real work on disk before the progress code is imported.

It is safe against a camp that is already a real repository: it never
overwrites a file that is there, never rewrites a remote it did not add, never
switches the branch it was called on, and never discards uncommitted work.

    uv run python tools/script_camp.py --camp DIR
    uv run python tools/script_camp.py --camp DIR --only mentors
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from vibemap import campaign, quests
from vibemap.vault import safe_title, stub_bullet

ROOT = Path(__file__).resolve().parents[1]
CAMP_MARKER = "config/camp.toml"
WORLDS = ("winter", "desert", "prod")


class ScriptError(RuntimeError):
    """A scripted step did not do what a learner would see."""


# ---- the plumbing --------------------------------------------------------------


def _vibe(camp: Path, *args: str) -> str:
    """Run vibe in this camp the way a learner would, and return its output."""
    env = dict(os.environ, VIBE_HOME=str(camp))
    out = subprocess.run(
        [sys.executable, "-m", "vibemap.cli", *args],
        cwd=camp,
        env=env,
        capture_output=True,
        text=True,
    )
    return out.stdout + out.stderr


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)


def _git_out(repo: Path, *args: str) -> str:
    """Ask git something. A failure is an empty answer, not an exception: the
    questions here are all "is this already the case"."""
    out = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)
    return out.stdout.strip()


def _branch(repo: Path) -> str:
    """The checked-out branch, or an empty string when there is not one yet."""
    name = _git_out(repo, "rev-parse", "--abbrev-ref", "HEAD")
    return "" if name in ("", "HEAD") else name


def _commit(repo: Path, message: str) -> bool:
    """Commit whatever is uncommitted, and say whether there was anything.

    A clean tree is not an error: this runs against camps that are already
    committed, where `git commit` would exit non-zero and stop the script.
    """
    _git(repo, "add", "-A")
    if not _git_out(repo, "status", "--porcelain"):
        return False
    _git(repo, "-c", "user.email=t@e.st", "-c", "user.name=T", "commit", "-qm", message)
    return True


def _write(camp: Path, rel: str, text: str) -> bool:
    """Write a file the learner has not written, and say whether it was written.

    Anything already on disk is theirs and is left alone, so a second run over
    a real camp adds what is missing instead of replacing what is there.
    """
    p = camp / rel
    if p.exists():
        return False
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return True


def _plural(n: int, one: str) -> str:
    return f"{n} {one}" + ("" if n == 1 else "s")


# ---- the stops -----------------------------------------------------------------

OWN_NOTE = """Tonight I did the work myself and wrote it down while it was
still fresh. The agent drafted, I rewrote the half that made no sense, and the
check told me what was still missing before I could claim the stop. What I
learned is that the deliverable is the point: the file on disk is what the
check reads, and the note is what I will read again. See [[Git]] and
[[Docker and containers]] for the parts I had to look up twice, and
[[Prompting - task, goal, hard constraints]] for the way I asked.
"""

# Hard and god add the strict note check: a source the learner added under
# Sources and a third link of their own. The third link is in OWN_NOTE; this
# bullet joins the note's Sources section.
OWN_SOURCE = (
    "- I read around it afterwards to get the history straight: "
    "https://en.wikipedia.org/wiki/History_of_artificial_intelligence"
)


# The stub names its own stop, so the line to replace differs per note.
def _stub(world: str, n: int) -> str:
    return f"- {stub_bullet(world, n)}"


def _write_notes(camp: Path) -> int:
    """The floor under every stop: the learner's own words in every note.

    A note the learner has already written has no stub left in it, and keeps
    the words they wrote. Returns how many notes this run filled in.
    """
    filled = 0
    for world in WORLDS:
        for ws in campaign.evenings()[world].workstreams:
            note = camp / "vault" / "Camp" / f"{safe_title(ws.name)}.md"
            if not note.exists():
                raise ScriptError(f"no vault note for {ws.name}; is this a camp?")
            text = note.read_text(encoding="utf-8")
            stub = _stub(world, ws.n)
            if stub not in text:
                continue
            text = text.replace(
                stub,
                "\n".join(f"- {line}" for line in OWN_NOTE.strip().splitlines()),
            )
            if OWN_SOURCE not in text:
                text = re.sub(
                    r"\n(#\w+\s*)$", "\n" + OWN_SOURCE + r"\n\n\1", text, count=1
                )
            note.write_text(text, encoding="utf-8")
            filled += 1
    return filled


MERMAID = """# The transformer block
Tokens go in, attention mixes them, the block repeats.

```mermaid
flowchart LR
  A[token] --> B[embedding]
  B --> C[attention]
  C --> D[feed forward]
```

Attention is the part that looks at every other token in the window.
A token is a chunk of text, not a word, which is why counting letters fails.
"""

LOCAL_MODEL = """# A model on my own laptop
I ran ollama run llama3.2 and asked it the three questions I asked Claude.
It was faster to start and much worse at long instructions.
The GPU tab in Activity Monitor lit up while it answered.
Licences: Llama has a community licence, Apache-2.0 has none of that.
Question one: it invented a plausible source.
Question two: it refused for no reason.
Question three: it was fine, and offline, which is the point.
"""

DOTFOLDERS = """# Every dot entry, one line each
- .git: the repository itself, every version of every file.
- .gitignore: the list of paths git is told to leave alone.
- .env: secrets for this folder, never committed.
- .venv: the Python environment uv builds here.
- .claude: Claude Code's settings, hooks and agents for this camp.
- .agents: skills in the Agent Skills standard, read by every agent.
- .github: what GitHub runs for me, workflows and templates.
- .vibe: my progress state, ignored by git.
"""

SPEC = """# Nicknames for players

## Why
Two players share a first name and the leaderboard is confusing.

## What
A player may set a nickname; the leaderboard shows it instead of the name.

## Not this
No profiles, no avatars, no login.
No migration of the rows already in scores.csv.

## Files
workspace/python/scores.py reads it; workspace/sql/top_runs.sql groups on it.

## Done when
The nickname appears in scores.csv and the tests cover an empty one.
A run with no nickname still shows the name, and the test says so.
"""

CI = """name: checks
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pipx run ruff check .
      - run: pipx run pytest -q
"""

COMPARISON = """# Two agents, one task
I asked opencode and codex for the same test on scores.py.
opencode: slower to start, picked up AGENTS.md without being told.
codex: faster, ignored the skill until I named it.
Both wrote a test that passed on the first run.
opencode needed the model set by hand.
codex asked before writing the file.
I would keep opencode for the local model and codex for speed.
"""

INSTALL_SH = """#!/usr/bin/env bash
# Symlink every config back into place.
set -euo pipefail
ln -sf "$PWD/zshrc" "$HOME/.zshrc"
"""


# The remote the stop asks for, used only when the camp has none of its own.
PLACEHOLDER_REMOTE = "https://github.com/learner/my-camp.git"
SECOND_BRANCH = "feature/nickname"
# The line that keeps the dotfiles repository out of the camp's index.
DOTFILES_IGNORE = "workspace/dotfiles/"
# What the production history check looks for in the reflog.
REWRITES = ("rebase", "revert", "cherry-pick", "reset")


def _write_deliverables(camp: Path) -> tuple[int, int]:
    """One deliverable per stop, exactly what the hint asks for.

    Returns (written, kept): a file the learner already has is never replaced.
    """
    files: dict[str, str] = {
        "workspace/winter/backprop/lecun1989.py": "print('one epoch')\n",
        "workspace/winter/transformer.md": MERMAID,
        "workspace/winter/local-model.md": LOCAL_MODEL,
        "workspace/winter/makemore/train.py": "print('makemore')\n",
        "workspace/winter/makemore/samples.txt": (
            "\n".join(f"name{i}" for i in range(12)) + "\n"
        ),
        "workspace/desert/dotfiles.md": DOTFOLDERS,
        "workspace/python/test_scores.py": (
            "def test_mean_of_one_row():\n    assert sum([3]) / 1 == 3\n"
        ),
        "workspace/specs/nickname.md": SPEC,
        ".github/workflows/checks.yml": CI,
        "workspace/jobs/nightly.sh": "#!/usr/bin/env bash\necho nightly\n",
        "workspace/jobs/log.csv": (
            "started,ended,exit\n08:00,08:01,0\n09:00,09:01,0\n"
        ),
        "workspace/evals/cases.csv": (
            "prompt,expected\n" + "".join(f"q{i},yes\n" for i in range(6))
        ),
        "workspace/evals/run.py": "print('score: 5/6')\n",
        "workspace/dotfiles/Brewfile": (
            "brew 'starship'\nbrew 'fzf'\nbrew 'ripgrep'\nbrew 'bat'\ncask 'ghostty'\n"
        ),
        "workspace/dotfiles/ghostty/config": "font-size = 14\n",
        "workspace/dotfiles/zshrc": 'eval "$(starship init zsh)"\n',
        "workspace/dotfiles/README.md": "# My dotfiles\nRun install.sh.\n",
        "workspace/dotfiles/install.sh": INSTALL_SH,
        "workspace/agents/comparison.md": COMPARISON,
    }
    written = sum(_write(camp, rel, text) for rel, text in files.items())
    kept = len(files) - written

    agents = camp / "AGENTS.md"
    text = agents.read_text(encoding="utf-8")
    if "## The dial" not in text:
        agents.write_text(
            text + "\n## The dial\n\nscratch/ is vibe-only. workspace/python needs "
            "tests before anything is merged.\n",
            encoding="utf-8",
        )
        written += 1
    else:
        kept += 1

    settings = camp / ".claude" / "settings.json"
    data = json.loads(settings.read_text(encoding="utf-8"))
    changed = False
    if not data.setdefault("hooks", {}).get("Stop"):
        data["hooks"]["Stop"] = [
            {"hooks": [{"type": "command", "command": "pytest -q", "timeout": 60}]}
        ]
        changed = True
    if not data.get("permissions", {}).get("allow"):
        data["permissions"] = {
            "allow": ["Bash(pytest*)", "Bash(ruff*)", "Bash(git status*)"]
        }
        changed = True
    if changed:
        settings.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        written += 1
    else:
        kept += 1

    return written, kept


def _script_git(camp: Path) -> list[str]:
    """The git shape the production stops ask for: a repository under
    workspace/dotfiles, a GitHub remote, a second branch, and a reflog that
    remembers a rewrite.

    Every step is conditional, because the played instance is a real repository
    with a real remote and a branch somebody pushes. The tool leaves it on the
    branch it found it on and never discards uncommitted work.
    """
    kept: list[str] = []

    dots = camp / "workspace" / "dotfiles"
    if not (dots / ".git").is_dir():
        _git(dots, "init", "-q")
    _commit(dots, "mine")

    # A repository inside the camp is kept out of the camp's index, or
    # `git add -A` below files it as a gitlink and a learner's own one stops
    # the command dead. The stop asks for this line; the script writes it.
    ignore = camp / ".gitignore"
    text = ignore.read_text(encoding="utf-8") if ignore.exists() else ""
    if DOTFILES_IGNORE not in text.splitlines():
        ignore.write_text(
            text.rstrip("\n") + f"\n{DOTFILES_IGNORE}\n"
            if text
            else f"{DOTFILES_IGNORE}\n",
            encoding="utf-8",
        )
    else:
        kept.append("kept the ignore line it already had")

    started_on = _branch(camp)

    # The check wants an origin on github.com. A real remote satisfies it better
    # than a placeholder, so a camp that has one keeps the one it has.
    if _git_out(camp, "remote"):
        kept.append("kept the origin it already had")
    else:
        _git(camp, "remote", "add", "origin", PLACEHOLDER_REMOTE)

    _commit(camp, "the deliverables of the evening")

    # The check counts branches; it does not ask which one is checked out, so
    # nothing here switches.
    branches = _git_out(camp, "branch", "--format=%(refname:short)").split()
    if SECOND_BRANCH in branches:
        kept.append(f"kept the branch {SECOND_BRANCH}")
    elif len(branches) >= 2:
        kept.append(f"kept its {len(branches)} branches")
    else:
        _git(camp, "branch", SECOND_BRANCH)

    # The stop wants a branch that reached the remote. Pushing needs a real
    # repository and the network, so a camp that has never fetched gets the
    # ref a fetch would have written, and one that has keeps what it has.
    if _git_out(camp, "for-each-ref", "--format=%(refname)", "refs/remotes/"):
        kept.append("kept the remote branches it already had")
    elif _git_out(camp, "rev-parse", "--verify", "-q", "HEAD"):
        here = _branch(camp) or "main"
        _git(camp, "update-ref", f"refs/remotes/origin/{here}", "HEAD")

    log = _git_out(camp, "reflog", "-n", "300")
    if any(word in log for word in REWRITES):
        kept.append("kept the rewrite its reflog already remembered")
    elif not _git_out(camp, "rev-parse", "--verify", "-q", "HEAD"):
        kept.append("no commit to rewrite yet")
    else:
        # --soft moves the tree not at all; it only writes the reflog entry the
        # stop looks for, so work the learner has not committed is never lost.
        _git(camp, "reset", "--soft", "HEAD")

    back = _branch(camp)
    if started_on and back != started_on:
        _git(camp, "switch", "-q", started_on)
    return kept


def script_stops(camp: Path) -> str:
    """Every stop of winter, desert and production: its deliverable and its note."""
    filled = _write_notes(camp)
    written, kept_files = _write_deliverables(camp)
    kept = _script_git(camp)
    said = f"stops: {_plural(written, 'deliverable')}, {_plural(filled, 'note')}"
    if kept_files:
        said += f", {kept_files} left as the learner had them"
    if kept:
        said += "; " + ", ".join(kept)
    return said


# ---- the fork ------------------------------------------------------------------


def _record(fork: Path, *, expect_ok: bool) -> None:
    out = subprocess.run(
        [sys.executable, "tools/record_build.py"],
        cwd=fork,
        capture_output=True,
        text=True,
    )
    if out.returncode != 0:
        raise ScriptError(f"record_build.py failed:\n{out.stdout}{out.stderr}")
    said = "build passed" if expect_ok else "build failed"
    if said not in out.stdout:
        raise ScriptError(f"expected {said!r} from record_build.py, got: {out.stdout}")


def script_fork(camp: Path, product: Path = ROOT) -> str:
    """The four challenges, done: made, configured, extended, broken, repaired.

    A fork the learner already made is theirs: this leaves it alone rather than
    replacing it, because `vibe fork --force` would delete their work.
    """
    fork = camp / quests.FORK_DIR
    if fork.is_dir() and any(fork.iterdir()):
        return f"fork: kept the {quests.FORK_DIR.as_posix()} that was already there"
    made = _vibe(camp, "fork", "--from", str(product))
    if "files" not in made:
        raise ScriptError(f"vibe fork did not copy the product:\n{made}")

    cfg_js = fork / "src" / "config" / "00-config.js"
    cfg_js.write_text(
        cfg_js.read_text(encoding="utf-8").replace(
            "const WORLD_SCALE=1.6;", "const WORLD_SCALE=2.4;"
        ),
        encoding="utf-8",
    )

    local = fork / "tools" / "generated" / "campaign.json"
    data = json.loads(local.read_text(encoding="utf-8"))
    data["evenings"]["prod"]["ws"].append(
        {"h": "Stop 9", "n": "Context engineering, my own stop", "d": "from the news"}
    )
    local.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    boot = fork / "src" / "game" / "90-boot.js"
    broken = boot.with_suffix(".js.off")
    boot.rename(broken)
    _record(fork, expect_ok=False)
    broken.rename(boot)
    _record(fork, expect_ok=True)
    return f"fork: {quests.FORK_DIR.as_posix()} with a failed and a passing build"


# ---- the artifacts -------------------------------------------------------------

CAFE = """\
import http.client
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer


class Cafe(BaseHTTPRequestHandler):
    def do_GET(self):
        code = 200 if self.path == "/coffee" else 404
        self.send_response(code)
        self.end_headers()
        self.wfile.write(b"one coffee" if code == 200 else b"not on the menu")

    def log_message(self, fmt, *args):
        pass


httpd = HTTPServer(("127.0.0.1", 0), Cafe)
threading.Thread(target=httpd.serve_forever, daemon=True).start()
port = httpd.server_address[1]
for path in ("/coffee", "/unicorn-milk"):
    con = http.client.HTTPConnection("127.0.0.1", port)
    con.request("GET", path)
    print(f"GET {path} -> {con.getresponse().status}")
    con.close()
httpd.shutdown()
"""

FOUNTAIN = """\
import time
from functools import lru_cache


@lru_cache
def water(kind):
    time.sleep(0.2)
    return f"a cup of {kind}"


for _ in range(2):
    start = time.perf_counter()
    water("cold")
    print(f"{(time.perf_counter() - start) * 1000:.0f} ms")
print(water.cache_info())
"""

WELL = """\
import sqlite3

con = sqlite3.connect("well.db")
cur = con.cursor()
cur.execute("DROP TABLE IF EXISTS scores")
cur.execute("CREATE TABLE scores(player, score)")
cur.executemany(
    "INSERT INTO scores VALUES (?, ?)",
    [("Lotte", 412), ("Tom", 380), ("Max", 512), ("Frank", 299), ("Rolinda", 640)],
)
cur.execute("CREATE INDEX scores_player ON scores(player)")
cur.execute("UPDATE scores SET score = score + 10 WHERE player = 'Lotte'")
cur.execute("UPDATE scores SET score = score - 10 WHERE player = 'Tom'")
con.commit()
for row in cur.execute("SELECT player, score FROM scores ORDER BY score DESC"):
    print(row)
con.close()
"""

LOOKUP = """\
import socket

print("localhost ->", socket.gethostbyname("localhost"))
for family, _, _, _, address in socket.getaddrinfo("localhost", 80):
    print(family.name, address[0])
try:
    print("vibe-map.invalid ->", socket.gethostbyname("vibe-map.invalid"))
except socket.gaierror as e:
    print("vibe-map.invalid -> no such name:", e.strerror)
"""

DOCKERFILE = """\
FROM python:3.12-slim
WORKDIR /app
COPY . .
CMD ["python", "app.py"]
"""

NIGHTLY = """\
name: nightly
on:
  schedule:
    - cron: "15 4 * * *"
jobs:
  turn:
    runs-on: ubuntu-latest
    steps:
      - run: date -u
"""

METER = """\
# The rate is from the AWS EC2 On-Demand pricing page for t3.small in eu-west-1:
# https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-on-demand-instances.html
RATE = 0.0228  # USD per instance-hour

print(f"2 hours: {RATE * 2:.2f} USD")
print(f"30 days: {RATE * 24 * 30:.2f} USD")
"""

LAYERS = """\
import platform
import sqlite3

print("1 hardware:", platform.machine(), platform.processor() or "(not reported)")
print("2 operating system:", platform.platform())
print("3 runtime: Python", platform.python_version())
print("4 libraries: sqlite3", sqlite3.sqlite_version)
print("5 your app: vibe, in this camp")
print("6 the agent: whatever is reading and writing all of the above")
"""

MAIN = """\
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/coffee")
async def coffee():
    return {"cup": "one", "milk": "oat, on the side"}


if __name__ == "__main__":
    from fastapi.testclient import TestClient

    answer = TestClient(app).get("/")
    print(answer.status_code, answer.json()["message"])
"""


def _mcp_json(camp: Path) -> str:
    """The bridge artifact's .mcp.json, naming the path this camp really has.

    An MCP server is started from an absolute path, so a path copied from
    another machine starts nothing and the artifact teaches the wrong thing.
    """
    server = {
        "command": "uv",
        "args": ["--directory", str(camp), "run", "scores.py"],
    }
    return json.dumps({"mcpServers": {"camp-scores": server}}, indent=2) + "\n"


RAW_CSV = """\
played_at,player,score
2026-09-16,Lotte,412
2026-09-16,Tom,380
2026-09-17,Lotte,455
2026-09-17,Max,512
2026-09-17,Tom,four hundred
2026-09-17,Rolinda,640
"""

PIPELINE = """\
import duckdb

con = duckdb.connect("camp.duckdb")
con.execute(
    "CREATE OR REPLACE TABLE bronze AS "
    "SELECT * FROM read_csv('raw.csv', all_varchar = true)"
)
con.execute(
    "CREATE OR REPLACE TABLE silver AS "
    "SELECT played_at, player, try_cast(score AS INTEGER) AS score FROM bronze "
    "WHERE try_cast(score AS INTEGER) IS NOT NULL"
)
con.execute(
    "CREATE OR REPLACE TABLE gold AS "
    "SELECT player, max(score) AS best FROM silver GROUP BY player"
)
for name in ("bronze", "silver", "gold"):
    print(name, con.execute(f"SELECT count(*) FROM {name}").fetchone()[0])
con.close()
"""

POST_OFFICE = """\
import queue
import threading

q = queue.Queue()
order = []


def worker():
    while True:
        letter, attempt = q.get()
        if letter == 3 and attempt == 1:
            order.append(f"retry {letter}")
            q.put((letter, 2))
        elif letter == 3:
            order.append(f"dead letter {letter}")
        else:
            order.append(f"delivered {letter}")
        q.task_done()


threading.Thread(target=worker, daemon=True).start()
for letter in (1, 2, 3):
    q.put((letter, 1))
q.join()
for line in order:
    print(line)
"""

PYPROJECT = """\
[project]
name = "shop"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = ["humanize>=4.0"]
"""

UV_LOCK = """\
version = 1

[[package]]
name = "humanize"
version = "4.12.3"
"""

BATCH = """\
import concurrent.futures
import time


def one_request(n):
    time.sleep(0.05)
    return n


start = time.perf_counter()
for n in range(20):
    one_request(n)
serial = time.perf_counter() - start
print(f"one at a time: {serial:.2f} s")

start = time.perf_counter()
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
    futures = [pool.submit(one_request, n) for n in range(20)]
    for future in concurrent.futures.as_completed(futures):
        future.result()
batched = time.perf_counter() - start
print(f"batched: {batched:.2f} s")
print(f"speedup: {serial / batched:.1f}x")
"""

BACKOFF = """\
# The rules are the ones the Claude API rate limits page states: a 429 carries a
# retry-after header saying how long to wait, and an earlier retry fails.
RESPONSES = [(429, 2), (429, None), (200, None)]

wait = 2
for status, retry_after in RESPONSES:
    if status == 200:
        print("200 OK")
        break
    if retry_after is not None:
        print(f"429 retry-after {retry_after}")
        wait = retry_after
    else:
        print("429 no retry-after")
        wait *= 2
    print(f"waiting {wait} s")
"""

RETRIEVE = """\
import math
from collections import Counter

NOTES = {
    "Headless agents and scheduling": (
        "the monday job runs vibe vault build on a schedule while you sleep and "
        "it failed because uv was missing on the runner"
    ),
    "CI-CD and automation": "a workflow runs the tests on every push to main",
    "Git hooks": "a hook runs before a commit and can refuse it",
    "Obsidian and the graph": "notes link to each other and the graph shows it",
}
QUESTION = "why did the monday run fail?"


def vector(text):
    return Counter(text.lower().split())


def cosine(a, b):
    dot = sum(a[word] * b[word] for word in set(a) & set(b))
    size = math.sqrt(sum(v * v for v in a.values())) * math.sqrt(
        sum(v * v for v in b.values())
    )
    return dot / size if size else 0.0


question = vector(QUESTION)
ranked = sorted(
    ((cosine(question, vector(text)), name) for name, text in NOTES.items()),
    reverse=True,
)
print("top 3 for:", QUESTION)
for score, name in ranked[:3]:
    print(f"  {score:.2f}  {name}")
print(f"It failed because uv was missing on the runner. source: {ranked[0][1]}")
"""

REVIEWER = """\
---
name: camp-reviewer
description: Reads a diff here and names what breaks AGENTS.md. Use before a commit.
tools: Read, Glob, Grep
---

You review one diff and nothing else. Read AGENTS.md first, then the diff.
Report, in one paragraph: what the change does, which rule it breaks if any,
and the smallest fix. You never edit a file and you never run a command that
writes.
"""

ERASE = """\
import csv

PLAYERS = [
    {"id": "7", "name": "Lotte", "email": "lotte@example.invalid"},
    {"id": "8", "name": "Tom", "email": "tom@example.invalid"},
    {"id": "9", "name": "Max", "email": "max@example.invalid"},
]
FIELDS = ["id", "name", "email"]
ERASE_ID = "7"


def write(path, rows):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


write("players.csv", PLAYERS)
with open("players.csv", newline="") as f:
    rows = list(csv.DictReader(f))

theirs = [row for row in rows if row["id"] == ERASE_ID]
rest = [row for row in rows if row["id"] != ERASE_ID]
write("export.csv", theirs)
write("players.csv", rest)
print(f"exported {len(theirs)} rows to export.csv")
print(f"erased {len(theirs)} rows, {len(rest)} rows left")
"""

SPLIT = """\
import random

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

rng = random.Random(0)
X = [[rng.random(), rng.random()] for _ in range(400)]
y = [1 if a + b > 1 else 0 for a, b in X]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.33, random_state=42
)
tree = DecisionTreeClassifier(max_depth=3, random_state=42).fit(X_train, y_train)
print(f"train accuracy: {tree.score(X_train, y_train):.3f}")
print(f"test accuracy: {tree.score(X_test, y_test):.3f}")
"""

SWITCHBOARD = """\
# say hello, to a name or to the camp
greet name='camp':
    @echo "hello {{name}}"

# the numbers in this folder, counted
count:
    @ls -1 | wc -l

# greet first, then count: one command for the whole round
round: greet
    @just count
"""

# One finished piece of work per artifact, built the way its walkthrough says.
FIXTURES: dict[str, dict[str, str]] = {
    "cafe": {"cafe.py": CAFE},
    "fountain": {"fountain.py": FOUNTAIN},
    "well": {"well.py": WELL},
    "lighthouse": {"lookup.py": LOOKUP},
    "dock": {"Dockerfile": DOCKERFILE, "app.py": "print('one crate, opened')\n"},
    "windmill": {"nightly.yml": NIGHTLY},
    "balloon": {"meter.py": METER},
    "mountain": {"layers.py": LAYERS},
    "stall": {"main.py": MAIN},
    # Empty on purpose: its one file names an absolute path, so fixture_files
    # writes it once the camp is known.
    "bridge": {},
    "factory": {"raw.csv": RAW_CSV, "pipeline.py": PIPELINE},
    "post-office": {"postoffice.py": POST_OFFICE},
    "switchboard": {"justfile": SWITCHBOARD},
    "shop": {"pyproject.toml": PYPROJECT, "uv.lock": UV_LOCK},
    "bank": {".gitignore": ".env\n", "env.example": "ANTHROPIC_API_KEY=\n"},
    "data-centre": {"batch.py": BATCH},
    "energy-grid": {"backoff.py": BACKOFF},
    "library": {"retrieve.py": RETRIEVE},
    "office": {"reviewer.md": REVIEWER},
    "households": {"erase.py": ERASE},
    "school": {"split.py": SPLIT},
}


def _artifact_note() -> str:
    from vibemap.artifact_checks import ARTIFACT_SECTION

    return (
        f"{ARTIFACT_SECTION}\n\nI built the thing the sheet asked for and read the "
        "page it came from. The part I had not understood before was how little of "
        "it is magic once you see the commands, and how much of the work is "
        "deciding what counts as done before you start.\n"
    )


NOTE = _artifact_note()


def fixture_files(artifact_id: str, camp: Path) -> dict[str, str]:
    """The finished files for one artifact, in the camp they belong to.

    Every fixture but one is the same text anywhere; the bridge's mcp.json
    names an absolute path and only the camp knows it.
    """
    if artifact_id == "bridge":
        return {"mcp.json": _mcp_json(camp)}
    return FIXTURES[artifact_id]


def script_artifacts(camp: Path) -> str:
    """Every artifact built for real, one folder each, with the learner's note."""
    written = kept = 0
    for artifact_id in FIXTURES:
        files = fixture_files(artifact_id, camp)
        rel = f"workspace/artifacts/{artifact_id}"
        wrote = [_write(camp, f"{rel}/{name}", body) for name, body in files.items()]
        wrote.append(_write(camp, f"{rel}/notes.md", NOTE))
        written += sum(wrote)
        kept += len(wrote) - sum(wrote)
    said = f"artifacts: {_plural(written, 'file')} under workspace/artifacts"
    return said + (f", {kept} left as the learner had them" if kept else "")


# ---- the mentors ---------------------------------------------------------------

CHERNY_MD = """# Working with my agent

## Rules
- Never edit a generated file; change the generator and run it again.

## How it is verified
`uv run pytest tests/test_build.py` rebuilds and compares, so a hand edit to a
generated file shows up as a failing test before I can commit it.
"""

WU_MD = """# A nickname on the leaderboard

## Spec
Done is: a player can set a nickname, the leaderboard shows it instead of the
name, and a player without one still shows their name.

## Plan
1. Add a nickname column to the CSV reader with an empty default.
2. Show nickname or name in the table.
3. Write two tests: one with a nickname, one without.

## To-do
- [ ] Read the CSV with the extra column.
- [ ] Render nickname or name.
- [ ] Two tests, both red first.
"""

BIGRAM_PY = '''"""Count every pair of neighbours and ask what follows an a."""

TEXT = "the cat sat on the mat"

counts: dict[str, dict[str, int]] = {}
for first, second in zip(TEXT, TEXT[1:]):
    counts.setdefault(first, {})
    counts[first][second] = counts[first].get(second, 0) + 1

after_a = counts["a"]
best = max(after_a, key=lambda c: after_a[c])
print(f"after a: {best}")
'''

LECUN_MD = """# Renaming the score column

## What mattered
- The column is called `score` in workspace/data/scores.csv.
- Two files read it: workspace/python/scores.py and workspace/sql/top_runs.sql.
- The rename had to keep the old header readable for one release.

## What I could throw away
- The whole history of the file, which I pasted in for no reason.
- The game code, which never touches the CSV.
- My long explanation of why the name was bad. The agent only needed the name.
"""

DESCENT_PY = '''"""Twenty steps downhill on (w - 3) ** 2, learning from the error."""

w = 0.0
STEP = 0.1

for i in range(20):
    gradient = 2 * (w - 3)
    w -= STEP * gradient
    print(f"step {i + 1}: loss {(w - 3) ** 2:.4f}")

print(f"w = {round(w, 1)}")
'''

LABELS_CSV = """item,label
README.md,keep
notes-2024.md,archive
scratch.txt,delete
invoice-april.pdf,keep
screenshot-1.png,delete
screenshot-2.png,delete
meeting-notes.md,archive
budget.xlsx,keep
old-cv.docx,archive
untitled-3.md,delete
"""

SEARCH_PY = '''"""My clever rule first, then plain search over every pair."""

NUMS = [2, 17, 30, 41, 55, 70, 88]

# The rule I invented: the smallest and the largest should be the pair.
guess = (min(NUMS), max(NUMS))
print(f"my rule says: {guess[0]} {guess[1]} (sum {sum(guess)})")

for i, a in enumerate(NUMS):
    for b in NUMS[i + 1 :]:
        if a + b == 100:
            print(f"search found: {a} {b}")
'''

AMODEI_MD = """# A year from now

## What I expect in a year
By September 2027 I expect to hand an agent a one-line bug report and get a
merged pull request with a passing test, without me reading the diff, for at
least half of the small bugs in this camp.

## What would change my mind
If I keep having to rewrite the test it wrote because it tested the mock and
not the behaviour, three times in a row, I will call that expectation wrong.
"""

OLAH_MD = """# Why my mail client thinks a message is spam

## What I looked at
I moved three messages to spam and three out of it, then watched which ones it
guessed right the next day. The sender domain seems to weigh more than the
words.

```mermaid
flowchart LR
  A[sender domain] --> D[score]
  B[words in subject] --> D
  C[did I reply before] --> D
  D --> E{over the line}
  E -->|yes| F[spam folder]
  E -->|no| G[inbox]
```
"""

GHOSTTY_CONFIG = """# A big font because I read this all evening.
font-size = 14
# Rounded off the top so the tabs do not fight the tiling window manager.
window-decoration = false
# Enough history to scroll back to the traceback I just lost.
scrollback-limit = 10000
# The palette is OLED black, so an unfocused split should still be readable.
unfocused-split-opacity = 0.9
"""

HASH_PY = '''"""The same hash git gives, from the bytes git actually hashes."""

import hashlib

BODY = b"what is up, doc?"
blob = b"blob " + str(len(BODY)).encode() + b"\\x00" + BODY
print(hashlib.sha1(blob).hexdigest())
'''

OPENCODE_MD = """# The same prompt, two providers

## The same prompt
Read AGENTS.md, then the failing test I name, then change the smallest amount
of code that makes it pass. Do not touch a generated file. Show me the diff
before you write it, and tell me which rule in AGENTS.md you checked it against.

## What I would keep
The rules file, the test that says what done means, and the review step where I
read the diff. Those are mine. The model is the part I can swap on a Tuesday.
"""

# The file each mentor asks for, and the words the learner writes afterwards.
MENTOR_FILES: dict[str, dict[str, str]] = {
    "cherny": {"CLAUDE.md": CHERNY_MD},
    "wu": {"spec.md": WU_MD},
    "karpathy": {"bigram.py": BIGRAM_PY},
    "lecun": {"abstraction.md": LECUN_MD},
    "hinton": {"descent.py": DESCENT_PY},
    "li": {"labels.csv": LABELS_CSV},
    "sutton": {"search.py": SEARCH_PY},
    "amodei": {"forecast.md": AMODEI_MD},
    "olah": {"circuit.md": OLAH_MD},
    "hashimoto": {"config.ghostty": GHOSTTY_CONFIG},
    "torvalds": {"hash.py": HASH_PY},
    "opencode": {"providers.md": OPENCODE_MD},
}

MENTOR_LEARNED: dict[str, str] = {
    "cherny": (
        "A rule nobody can check is a wish. Writing the command underneath it "
        "turned my vague preference about generated files into something the "
        "test run enforces, which means I stop arguing with the agent about it "
        "and let the failing test do the arguing for me."
    ),
    "wu": (
        "Writing the spec before the plan stopped me halfway through, because I "
        "could not say what done looked like for the empty nickname. Ten minutes "
        "of writing saved an evening of building the wrong thing, and the to-do "
        "list was short enough to hand over as it was."
    ),
    "karpathy": (
        "Counting pairs by hand made the whole idea of a language model much "
        "less mysterious. It is a table of what followed what, and the next "
        "character is whatever the table saw most often. Twenty lines and no "
        "libraries, and it still gets the letter after an a right."
    ),
    "lecun": (
        "Most of what I paste into a prompt is noise I added out of politeness. "
        "Splitting one real task into what mattered and what I could throw away "
        "left three facts and a file name. Next time I will start from that "
        "short list instead of the whole history."
    ),
    "hinton": (
        "Learning is just a small step against the error, twenty times over. "
        "Watching the loss shrink line by line made the word gradient concrete "
        "for me: it is the direction that makes things worse, so I walk the "
        "other way, and a tenth of a step at a time is enough."
    ),
    "li": (
        "Labelling ten things myself was harder than I expected, and the two "
        "screenshots were the ones I could not decide on. Now I understand why "
        "people argue about label quality: the boundary cases are where the "
        "real definition of the task lives, not in the easy rows."
    ),
    "sutton": (
        "My clever rule was wrong within a second, and the dumb loop over every "
        "pair was right and took no thought at all. The lesson is not that rules "
        "are useless, it is that I should reach for plain search first and only "
        "add a rule when the search is actually too slow."
    ),
    "amodei": (
        "A forecast is only worth writing if it can embarrass me later. Naming a "
        "date, a number and the observation that would change my mind turned a "
        "vague feeling about agents into something I can check next September, "
        "and I already suspect I have been too optimistic."
    ),
    "olah": (
        "Drawing the circuit showed me how little I actually know about a tool I "
        "use every day. Once the inputs, the middle and the output were on paper "
        "I could name the one thing I would test to find out whether the sender "
        "domain really matters more than the words."
    ),
    "hashimoto": (
        "Writing why above each setting made me delete two of them, because I "
        "could not say why they were there. A config file is documentation that "
        "happens to run, and a comment about the reason ages much better than a "
        "comment repeating the key name back at me."
    ),
    "torvalds": (
        "Git is not magic, it is a hash of a header and the bytes. Building the "
        "blob prefix myself and getting the same forty characters as git "
        "hash-object made the object store feel like something I could have "
        "written, and content addressing finally clicked for me."
    ),
    "opencode": (
        "Running the same prompt through two providers made it obvious which "
        "part of my setup is actually mine. The rules file, the checks and the "
        "review step survived the swap untouched, and the model turned out to be "
        "the easiest piece to replace of the whole lot."
    ),
}


def _mentor_note(mentor_id: str, name: str) -> str:
    return f"# {name}\n\n{quests.MENTOR_SECTION}\n\n{MENTOR_LEARNED[mentor_id]}\n"


def script_mentors(camp: Path) -> str:
    """The twelve encounters done: the file each exercise asks for, and a note."""
    written = kept = 0
    for m in campaign.mentors():
        mentor_id = m["id"]
        files = MENTOR_FILES.get(mentor_id)
        if files is None:
            raise ScriptError(f"no scripted exercise for mentor {mentor_id}")
        rel = f"workspace/mentors/{mentor_id}"
        wrote = [_write(camp, f"{rel}/{name}", body) for name, body in files.items()]
        wrote.append(
            _write(
                camp, f"{rel}/{quests.MENTOR_NOTE}", _mentor_note(mentor_id, m["name"])
            )
        )
        written += sum(wrote)
        kept += len(wrote) - sum(wrote)
    said = f"mentors: {_plural(written, 'file')} under workspace/mentors"
    return said + (f", {kept} left as the learner had them" if kept else "")


# ---- everything ----------------------------------------------------------------


def script_everything(camp: Path, product: Path = ROOT) -> list[str]:
    """All four parts, in the order that works: the fork needs the stops' commit."""
    return [
        script_stops(camp),
        script_fork(camp, product),
        script_artifacts(camp),
        script_mentors(camp),
    ]


PARTS = ("stops", "fork", "artifacts", "mentors")


def main() -> None:
    ap = argparse.ArgumentParser(prog="script_camp")
    ap.add_argument("--camp", required=True, help="the camp to write into")
    ap.add_argument(
        "--product",
        default=str(ROOT),
        help="the vibe-map checkout the fork is made from",
    )
    ap.add_argument(
        "--only",
        default=",".join(PARTS),
        help=f"comma-separated parts to run: {', '.join(PARTS)}",
    )
    a = ap.parse_args()

    camp = Path(a.camp).resolve()
    if not (camp / CAMP_MARKER).exists():
        sys.exit(f"{camp} is not a camp: it has no {CAMP_MARKER}")

    wanted = [p.strip() for p in a.only.split(",") if p.strip()]
    unknown = [p for p in wanted if p not in PARTS]
    if unknown:
        sys.exit(f"unknown part(s): {', '.join(unknown)}. Pick from {', '.join(PARTS)}")

    product = Path(a.product).resolve()
    runners = {
        "stops": lambda: script_stops(camp),
        "fork": lambda: script_fork(camp, product),
        "artifacts": lambda: script_artifacts(camp),
        "mentors": lambda: script_mentors(camp),
    }
    for part in PARTS:
        if part in wanted:
            print(runners[part]())


if __name__ == "__main__":
    main()
