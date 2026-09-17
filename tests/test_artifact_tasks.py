"""Artifacts as tasks: the Do it for real walkthroughs and their checks.

Every artifact gets a fixture that is a plausible finished piece of work, built
the way its own walkthrough says. The check then has to pass on it. A check
that needs a tool this machine may not have says so in its detail instead of
failing, and the test reads that sentence rather than guessing.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from vibemap import campaign
from vibemap.artifact_checks import (
    ARTIFACT_SECTION,
    KINDS,
    artifact_ids,
    artifact_quest,
    get_artifact,
)
from vibemap.config import Config
from vibemap.quests import run_quest
from vibemap.state import State, decode_code

NOTE = (
    f"{ARTIFACT_SECTION}\n\nI built the thing the sheet asked for and read the "
    "page it came from. The part I had not understood before was how little of "
    "it is magic once you see the commands, and how much of the work is "
    "deciding what counts as done before you start.\n"
)

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

MCP = {
    "mcpServers": {
        "camp-scores": {
            "command": "uv",
            "args": ["--directory", "/Users/you/vibe-map-camp", "run", "scores.py"],
        }
    }
}

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
    "bridge": {"mcp.json": json.dumps(MCP, indent=2) + "\n"},
    "factory": {"raw.csv": RAW_CSV, "pipeline.py": PIPELINE},
    "post-office": {"postoffice.py": POST_OFFICE},
    "shop": {"pyproject.toml": PYPROJECT, "uv.lock": UV_LOCK},
    "bank": {".gitignore": ".env\n", "env.example": "ANTHROPIC_API_KEY=\n"},
    "data-centre": {"batch.py": BATCH},
    "energy-grid": {"backoff.py": BACKOFF},
    "library": {"retrieve.py": RETRIEVE},
    "office": {"reviewer.md": REVIEWER},
    "households": {"erase.py": ERASE},
    "school": {"split.py": SPLIT},
}

GOD = Config.model_validate({"learner": {"difficulty": "god"}})


def _build(tmp_path: Path, artifact_id: str, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Write the fixture into a workspace of its own and point the checks at it."""
    here = tmp_path / "workspace" / "artifacts" / artifact_id
    here.mkdir(parents=True)
    for name, body in FIXTURES[artifact_id].items():
        (here / name).write_text(body, encoding="utf-8")
    (here / "notes.md").write_text(NOTE, encoding="utf-8")
    monkeypatch.setattr(
        "vibemap.artifact_checks.ARTIFACTS_DIR", tmp_path / "workspace" / "artifacts"
    )
    return here


# ---- the data ------------------------------------------------------------------


def test_every_artifact_has_a_sourced_walkthrough_under_twenty_minutes() -> None:
    for a in campaign.artifacts():
        real = a["real"]
        assert real["dir"] == f"workspace/artifacts/{a['id']}", a["id"]
        assert 0 < real["minutes"] <= 20, a["id"]
        assert real["doc"]["url"].startswith("https://"), a["id"]
        assert real["doc"]["title"] and real["done"], a["id"]
        assert 3 <= len(real["steps"]) <= 5, a["id"]
        assert real["commands"], a["id"]
        assert real["check"]["kind"] in KINDS, a["id"]


def test_the_walkthroughs_keep_the_house_style() -> None:
    for a in campaign.artifacts():
        text = json.dumps(a["real"], ensure_ascii=False)
        assert "—" not in text and "–" not in text, a["id"]


def test_every_artifact_quest_has_two_checks_with_hints() -> None:
    for artifact_id in artifact_ids():
        quest = artifact_quest(artifact_id, GOD)
        assert len(quest.checks) == 2, artifact_id
        assert all(c.hint for c in quest.checks), artifact_id


def test_an_unknown_artifact_id_is_refused() -> None:
    with pytest.raises(ValueError, match="unknown artifact"):
        get_artifact("nothing-like-that")


# ---- the checks ----------------------------------------------------------------


@pytest.mark.parametrize("artifact_id", artifact_ids())
def test_a_finished_artifact_passes_its_own_check(
    artifact_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _build(tmp_path, artifact_id, monkeypatch)
    results = run_quest(artifact_quest(artifact_id, GOD), GOD)
    assert all(r.ok for r in results), [(r.name, r.detail) for r in results]


@pytest.mark.parametrize("artifact_id", artifact_ids())
def test_an_empty_workspace_fails_every_artifact_check(
    artifact_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "vibemap.artifact_checks.ARTIFACTS_DIR", tmp_path / "workspace" / "artifacts"
    )
    results = run_quest(artifact_quest(artifact_id, GOD), GOD)
    assert not any(r.ok for r in results), [(r.name, r.detail) for r in results]
    assert "does not exist" in results[0].detail


def test_a_missing_tool_is_reported_rather_than_failed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Docker and scikit-learn are optional; the check says which layer answered."""
    _build(tmp_path, "dock", monkeypatch)
    monkeypatch.setattr("vibemap.artifact_checks._tool", lambda name: False)
    detail = run_quest(artifact_quest("dock", GOD), GOD)[0].detail
    assert "docker is not installed" in detail and "parse" in detail

    _build(tmp_path, "school", monkeypatch)
    monkeypatch.setattr("vibemap.artifact_checks.find_spec", lambda name: None)
    detail = run_quest(artifact_quest("school", GOD), GOD)[0].detail
    assert "scikit-learn is not installed" in detail


def test_a_half_finished_artifact_says_what_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    here = _build(tmp_path, "post-office", monkeypatch)
    (here / "postoffice.py").write_text(
        "import queue\nq = queue.Queue()\nq.put(1)\nq.task_done()\n"
        "print('delivered 1')\n",
        encoding="utf-8",
    )
    detail = run_quest(artifact_quest("post-office", GOD), GOD)[0].detail
    assert "delivered 2" in detail

    (here / "notes.md").write_text(
        f"{ARTIFACT_SECTION}\n\nnot much\n", encoding="utf-8"
    )
    note = run_quest(artifact_quest("post-office", GOD), GOD)[1]
    assert not note.ok and "needs 25" in note.detail


def test_a_broken_file_fails_its_kind(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    here = _build(tmp_path, "windmill", monkeypatch)
    (here / "nightly.yml").write_text(
        "# cron goes here one day\non:\n  push:\njobs: {}\n", encoding="utf-8"
    )
    detail = run_quest(artifact_quest("windmill", GOD), GOD)[0].detail
    assert "at least one job" in detail

    here = _build(tmp_path, "bridge", monkeypatch)
    (here / "mcp.json").write_text('{"mcpServers": {}}\n', encoding="utf-8")
    assert "no mcpServers" in run_quest(artifact_quest("bridge", GOD), GOD)[0].detail

    here = _build(tmp_path, "office", monkeypatch)
    (here / "reviewer.md").write_text(
        "---\nname: Camp Reviewer\ndescription: x\ntools: Read\n---\n\nbody\n",
        encoding="utf-8",
    )
    assert "hyphens" in run_quest(artifact_quest("office", GOD), GOD)[0].detail


def test_a_secret_in_the_example_file_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    here = _build(tmp_path, "bank", monkeypatch)
    (here / "env.example").write_text(
        "ANTHROPIC_API_KEY=sk-ant-looks-real\n", encoding="utf-8"
    )
    detail = run_quest(artifact_quest("bank", GOD), GOD)[0].detail
    assert "must not contain" in detail


# ---- the CLI and the progress code ---------------------------------------------


def _run(camp: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "vibemap.cli", *args],
        cwd=camp,
        env=dict(os.environ, VIBE_HOME=str(camp), COLUMNS="200"),
        capture_output=True,
        text=True,
    )


def test_vibe_check_artifact_claims_and_reaches_the_vault(tmp_path: Path) -> None:
    from click.testing import CliRunner

    from vibemap.cli import cli

    camp = tmp_path / "camp"
    made = CliRunner().invoke(cli, ["new", str(camp), "--name", "Tom"])
    assert made.exit_code == 0, made.output

    out = _run(camp, "check", "--artifact", "fountain")
    assert out.returncode == 0, out.stdout + out.stderr
    assert "does not exist" in out.stdout

    here = camp / "workspace" / "artifacts" / "fountain"
    here.mkdir(parents=True)
    (here / "fountain.py").write_text(FOUNTAIN, encoding="utf-8")
    (here / "notes.md").write_text(NOTE, encoding="utf-8")

    out = _run(camp, "check", "--artifact", "fountain")
    assert out.returncode == 0, out.stdout + out.stderr
    assert "built for real" in out.stdout and "+" in out.stdout
    state = json.loads((camp / ".vibe" / "state.json").read_text())
    assert state["artifactsBuilt"] == ["fountain"]
    assert state["artifacts"] == ["fountain"] and state["xp"] > 0
    note = (camp / "vault" / "Camp" / "Artifacts.md").read_text()
    assert "built for real: **The fountain**" in note
    assert "vibe check --artifact fountain" in note

    # A second run does not pay twice.
    xp = state["xp"]
    _run(camp, "check", "--artifact", "fountain")
    assert json.loads((camp / ".vibe" / "state.json").read_text())["xp"] == xp


def test_an_unknown_artifact_on_the_command_line_is_refused(tmp_path: Path) -> None:
    from click.testing import CliRunner

    from vibemap.cli import cli

    camp = tmp_path / "camp"
    assert CliRunner().invoke(cli, ["new", str(camp), "--name", "Tom"]).exit_code == 0
    out = _run(camp, "check", "--artifact", "nowhere")
    assert out.returncode == 1 and "unknown artifact" in out.stdout


def test_the_progress_code_carries_what_was_built_for_real() -> None:
    s = State(name="Lotte")
    s.artifacts.append("cafe")
    s.artifacts_built.append("cafe")
    payload = decode_code(s.to_code())
    assert payload["v"] == 2 and payload["artifactsBuilt"] == ["cafe"]

    back = State()
    back.merge_code(s.to_code())
    assert back.artifacts_built == ["cafe"] and back.artifacts == ["cafe"]

    # A code from before this release is still a valid version 2 code, and a
    # reader of it simply learns nothing about what was built.
    older = json.dumps(
        {"v": 2, "name": "Lotte", "doneW": {"campus": [1]}, "artifacts": ["well"]}
    )
    import base64

    code = base64.urlsafe_b64encode(older.encode()).decode().rstrip("=")
    old = State()
    old.merge_code(code)
    assert old.artifacts == ["well"] and old.artifacts_built == []
