"""The Linux and shell pack: its topics, its origins and hands-ons that really run.

Each hands-on is checked twice: red on an empty folder and on a stub, green on
a folder built the way the topic's own try_it says. Where the exercise is plain
shell that runs the same on a Mac and on Linux, the test runs those commands
rather than writing the answer in, so a try_it that drifts from its check fails
here.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from tests.conftest import ROOT
from vibemap import places, topics
from vibemap.artifact_checks import KINDS, run_spec
from vibemap.vault import safe_title

PACK = "linux"
FOLDER = ROOT / "vibemap" / "data" / "topics" / PACK
ORDER = [
    "kernel",
    "permissions",
    "processes",
    "texttools",
    "scripting",
    "packages",
    "tmux",
    "netshell",
    "systemd",
    "cron",
    "wslmac",
]

# The folder a learner ends up with, per topic. A string is a file to write; a
# list of shell lines is run in the folder with bash, the way the topic says.
SCRIPTING = """#!/usr/bin/env bash
set -euo pipefail
trap 'echo "cleanup ran" >&2' EXIT
greet() { printf 'hello, %s\\n' "$1"; }
for name in "$@"; do greet "$name"; done
"""
WORKED: dict[str, dict[str, str] | list[str]] = {
    "kernel": {
        "os-release.txt": 'PRETTY_NAME="Debian GNU/Linux 12 (bookworm)"\nID=debian\n'
    },
    "permissions": [
        "touch secret.txt",
        "chmod 640 secret.txt",
        "ls -l secret.txt > perms.txt",
    ],
    "processes": [
        "bash -c 'sleep 30 & pid=$!; kill -TERM \"$pid\"; wait \"$pid\";"
        ' echo "exit: $?"\' > signals.txt',
    ],
    "texttools": [
        "printf 'ada,3\\nbob,5\\nada,4\\ncy,1\\n' > runs.csv",
        "cut -d, -f1 runs.csv | sort | uniq -c | sort -rn | head -1 > report.txt",
        "awk -F, '{ total += $2 } END { print \"total\", total }' runs.csv"
        " >> report.txt",
        "sed -n 's/^bob,/best: bob /p' runs.csv >> report.txt",
    ],
    "scripting": [
        f"cat > safe.sh <<'EOF'\n{SCRIPTING}EOF",
        'bash safe.sh "Ada Lovelace" > out.txt',
    ],
    "packages": {
        "Brewfile": 'brew "jq"\n',
        "install-debian.sh": "apt-get update\napt-get install -y jq\n",
    },
    "tmux": {
        "sessions.txt": "camp: 1 windows (created Wed Sep 23 23:40:59 2026)\n",
        "tmux.conf": "bind-key R source-file ~/.tmux.conf\n",
    },
    "netshell": {
        "head.txt": "HTTP/1.0 200 OK\nServer: SimpleHTTP/0.6 Python/3.12.14\n",
        "port.txt": "python3 40826 me 3u IPv4 0t0 TCP 127.0.0.1:8765 (LISTEN)\n",
    },
    "systemd": {
        "hello.service": (
            "[Unit]\nDescription=Hello\n\n[Service]\n"
            "ExecStart=/usr/bin/env echo hello\n\n"
            "[Install]\nWantedBy=multi-user.target\n"
        )
    },
    "cron": {"crontab.txt": "30 7 * * 1-5 /usr/bin/env date >> /tmp/c.log 2>&1\n"},
    "wslmac": [
        "printf 'colour\\n' > word.txt",
        "printf '%s\\n' \"sed -i.bak 's/colour/color/' word.txt\" > portable.sh",
        "sed -i.bak 's/colour/color/' word.txt && rm word.txt.bak",
    ],
}


def _pack() -> list[topics.Topic]:
    return topics.in_pack(PACK)


def _build(here: Path, how: dict[str, str] | list[str]) -> None:
    if isinstance(how, dict):
        for name, text in how.items():
            (here / name).write_text(text, encoding="utf-8")
        return
    for line in how:
        subprocess.run(["bash", "-c", line], cwd=here, check=True, timeout=60)


# ---- the pack -------------------------------------------------------------------


def test_the_pack_loads_in_its_reading_order_on_the_shell_shelf() -> None:
    pack = next(p for p in topics.packs() if p.id == PACK)
    assert pack.shelf == "shell" and pack.blurb and pack.maintainer
    assert [t.id for t in _pack()] == ORDER == pack.topics
    assert set(WORKED) == set(ORDER)


def test_ssh_stays_in_the_core_pack() -> None:
    assert topics.get("ssh").pack == "core"


def test_every_topic_is_written_under_the_content_rule() -> None:
    for topic in _pack():
        assert topic.shelf == "shell", topic.id
        assert topic.checked is not None, topic.id
        assert safe_title(topic.title) == topic.title, topic.id
        assert topic.summary and topic.history and topic.try_it, topic.id
        assert 3 <= len(topic.sources) <= 6, topic.id
        for source in topic.sources:
            assert source.url.startswith("https://"), (topic.id, source.url)
            assert source.checked == topic.checked, (topic.id, source.url)


def test_no_file_in_the_pack_carries_an_em_dash_or_a_scaffold_marker() -> None:
    for path in sorted(FOLDER.glob("*.toml")):
        text = path.read_text(encoding="utf-8")
        assert "—" not in text and "TODO" not in text, path.name


# ---- where it happened ----------------------------------------------------------


def test_every_topic_has_one_primary_origin_at_a_place_on_the_map() -> None:
    known = {p.id for p in places.all_places()}
    for topic in _pack():
        primary = [o for o in topic.origins if o.primary]
        assert len(primary) == 1, topic.id
        for origin in topic.origins:
            assert origin.place in known, (topic.id, origin.place)
            assert origin.source.startswith("https://"), topic.id


def test_the_places_report_has_nothing_to_say_about_the_pack() -> None:
    assert places.problems(packs=[PACK]) == []


# ---- the hands-on ---------------------------------------------------------------


@pytest.mark.parametrize("topic_id", ORDER)
def test_a_hands_on_is_red_before_the_work_and_green_after(
    topic_id: str, tmp_path: Path
) -> None:
    topic = topics.get(topic_id)
    hands_on = topic.hands_on
    assert hands_on is not None and hands_on.minutes <= 20
    spec = hands_on.check
    assert spec["kind"] in KINDS

    empty = tmp_path / "empty"
    empty.mkdir()
    assert not run_spec(empty, spec)[0]

    stub = tmp_path / "stub"
    stub.mkdir()
    for name in spec.get("files", {}):
        (stub / name).write_text(f"# TODO: {hands_on.title}\n", encoding="utf-8")
    assert not run_spec(stub, spec)[0]

    how = WORKED[topic_id]
    if isinstance(how, list) and shutil.which("bash") is None:
        pytest.skip("bash is not on this machine")
    done = tmp_path / "done"
    done.mkdir()
    _build(done, how)
    ok, detail = run_spec(done, spec)
    assert ok, detail


def test_the_portable_sed_check_refuses_the_mac_only_form(tmp_path: Path) -> None:
    spec = topics.get("wslmac").hands_on.check  # type: ignore[union-attr]
    (tmp_path / "portable.sh").write_text(
        "sed -i.bak x word.txt\nsed -i '' 's/a/b/' f\n", encoding="utf-8"
    )
    (tmp_path / "word.txt").write_text("color\n", encoding="utf-8")
    ok, detail = run_spec(tmp_path, spec)
    assert not ok and "must not contain" in detail
