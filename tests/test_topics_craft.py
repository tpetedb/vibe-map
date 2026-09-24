"""The software craft and delivery pack: its topics, its origins, hands-ons that run.

Each hands-on is checked three ways: red on an empty folder, red on a stub, and
green on a folder built the way the topic's own try_it says. Where the exercise
runs offline with what this repository already has (Python, pytest), the test
runs it rather than writing the answer in, so a try_it that drifts from its
check fails here. A wrong answer that looks close is checked too, for the
exercises where a near miss is the likely mistake.
"""

from __future__ import annotations

import os
import re
import shlex
import subprocess
import sys
from importlib.util import find_spec
from pathlib import Path

import pytest

from tests.conftest import ROOT
from vibemap import places, topics
from vibemap.artifact_checks import KINDS, run_spec
from vibemap.vault import safe_title

PACK = "craft"
FOLDER = ROOT / "vibemap" / "data" / "topics" / PACK
ORDER = [
    "testdoubles",
    "fixtures",
    "properties",
    "refactoring",
    "codereview",
    "apidesign",
    "openapi",
    "oauth",
    "delivery",
    "containers",
    "manifests",
    "iac",
    "observability",
    "incidents",
    "licences",
    "buildersec",
    "supplychain",
]
# The DevOps module sequence the courses read in order, after core's ci.
DEVOPS = ["delivery", "containers", "manifests", "iac", "observability", "incidents"]
# The core topics this pack links to and must never copy.
CORE = ["tests", "ci", "docker", "kubernetes", "http", "apis", "semver", "security"]

NOTIFY = """import unittest
from unittest.mock import Mock


def notify(user, send):
    send(user, "welcome")


class NotifyTest(unittest.TestCase):
    def test_sends_welcome(self):
        send = Mock()
        notify("ada", send)
        send.assert_called_once_with("ada", "welcome")


if __name__ == "__main__":
    unittest.main()
"""
CART = """import pytest


@pytest.fixture
def cart():
    items = []
    yield items
    items.clear()


def test_cart_starts_empty(cart):
    assert cart == []


@pytest.mark.parametrize("price,qty,total", [(2, 3, 6), (5, 0, 0), (1, 10, 10)])
def test_line_total(price, qty, total):
    assert price * qty == total
"""
PROPS = """from hypothesis import given, strategies as st


def encode(text):
    runs = []
    for ch in text:
        if runs and runs[-1][0] == ch:
            runs[-1] = (ch, runs[-1][1] + 1)
        else:
            runs.append((ch, 1))
    return runs


def decode(runs):
    return "".join(ch * n for ch, n in runs)


@given(st.text())
def test_decode_undoes_encode(text):
    assert decode(encode(text)) == text
"""
# The same property checked over a few fixed strings, for a machine without
# Hypothesis: nobody here depends on it, and the report the check reads should
# still be one that the try_it's own pytest command wrote.
PROPS_STANDIN = """def encode(text):
    return [(ch, 1) for ch in text]


def decode(runs):
    return "".join(ch * n for ch, n in runs)


def test_decode_undoes_encode():
    for text in ["", "a", "aab", "abba"]:
        assert decode(encode(text)) == text
"""
OWING = """def print_owing(customer, amounts):
    print("***********************")
    print("**** Customer Owes ****")
    print("***********************")
    outstanding = sum(amounts)
    print_details(customer, outstanding)


def print_details(customer, outstanding):
    print(f"name: {customer}")
    print(f"amount: {outstanding}")


print_owing("Ada", [30, 12])
"""
PKCE = """import base64
import hashlib

verifier = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
digest = hashlib.sha256(verifier.encode("ascii")).digest()
challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
print(f"code_challenge={challenge}&code_challenge_method=S256")
"""
TRACE = """from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("camp.shop")

with tracer.start_as_current_span("checkout") as span:
    span.set_attribute("cart.items", 3)
    with tracer.start_as_current_span("charge"):
        pass
"""
MIT = """MIT License

Copyright (c) 2026 Ada Lovelace

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction.
"""
APP = """import os
import sys

key = os.environ.get("API_KEY")
if not key:
    sys.exit("API_KEY is not set; put it in .env, which git ignores")
print("key found")
"""

# The folder a learner ends up with, per topic: file name to text. The report a
# pytest exercise's check reads is produced by running its try_it, see PYTEST_RUN.
WORKED: dict[str, dict[str, str]] = {
    "testdoubles": {"test_notify.py": NOTIFY},
    "fixtures": {"test_cart.py": CART},
    "properties": {"test_props.py": PROPS},
    "refactoring": {"owing.py": OWING},
    "codereview": {
        "review.md": (
            "Design: the retry belongs in the client, not the handler.\n"
            "Tests: add a case for an empty list.\n"
            "Nit: the variable n could be named count.\n\n"
            "Verdict: LGTM once the retry moves.\n"
        )
    },
    "apidesign": {
        "methods.txt": (
            "GET safe idempotent\nHEAD safe idempotent\nPUT idempotent\n"
            "DELETE idempotent\nPOST neither\n"
        ),
        "problem.json": (
            '{\n  "type": "https://example.com/probs/no-such-player",\n'
            '  "title": "No such player.",\n  "status": 404\n}\n'
        ),
    },
    "openapi": {
        "openapi.yaml": (
            "openapi: 3.1.1\ninfo:\n  title: Scores\n  version: 0.1.0\npaths:\n"
            "  /scores:\n    get:\n      responses:\n        '200':\n"
            "          description: every run, newest first\n"
        )
    },
    "oauth": {"pkce.py": PKCE},
    "delivery": {
        "deploy.yml": (
            "name: deploy\non:\n  workflow_dispatch:\njobs:\n  deploy:\n"
            "    runs-on: ubuntu-latest\n    environment: production\n"
            "    steps:\n      - run: echo deploying\n"
        )
    },
    "containers": {
        "Dockerfile": (
            "FROM python:3.12-slim AS build\nRUN echo hello > /hello.txt\n\n"
            "FROM python:3.12-slim\nCOPY --from=build /hello.txt /hello.txt\n"
            'CMD ["cat", "/hello.txt"]\n'
        ),
        "compose.yaml": "services:\n  hello:\n    build: .\n",
    },
    "manifests": {
        "deployment.yaml": (
            "apiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: scores\n"
            "spec:\n  replicas: 2\n  selector:\n    matchLabels:\n      app: scores\n"
            "  template:\n    metadata:\n      labels:\n        app: scores\n"
            "    spec:\n      containers:\n      - name: scores\n"
            "        image: scores:0.1.0\n        ports:\n"
            "        - containerPort: 8000\n"
        ),
        "service.yaml": (
            "apiVersion: v1\nkind: Service\nmetadata:\n  name: scores\nspec:\n"
            "  selector:\n    app: scores\n  ports:\n  - protocol: TCP\n"
            "    port: 80\n    targetPort: 8000\n"
        ),
    },
    "iac": {
        "main.tf": (
            'resource "terraform_data" "greeting" {\n  input = "hello, camp"\n}\n\n'
            'output "greeting" {\n  value = terraform_data.greeting.output\n}\n'
        )
    },
    "observability": {"trace.py": TRACE},
    "incidents": {
        "postmortem.md": (
            "# The game would not load\n\n## Summary\nDown for ten minutes.\n"
            "## Impact\nEvery visitor.\n## Root Causes\nA missing file.\n"
            "## Trigger\nA deploy.\n## Resolution\nRolled back.\n"
            "## Detection\nA learner said so.\n"
            "## Action Items\nAdd a smoke test, owner: me.\n"
            "## Lessons Learned\nWhat went well: the rollback.\n"
            "## Timeline\n20:01 deploy, 20:11 rollback.\n"
        )
    },
    "licences": {
        "LICENSE": MIT,
        "hello.py": "# SPDX-License-Identifier: MIT\nprint('hello')\n",
    },
    "buildersec": {".gitignore": ".env\n.venv/\n", "app.py": APP},
    "supplychain": {
        "dependabot.yml": (
            'version: 2\nupdates:\n  - package-ecosystem: "uv"\n'
            '    directory: "/"\n    schedule:\n      interval: "weekly"\n'
            '  - package-ecosystem: "github-actions"\n    directory: "/"\n'
            '    schedule:\n      interval: "weekly"\n'
        )
    },
}

# The exercises whose check reads a report pytest writes, and the test file the
# try_it runs. The test runs the try_it's own pytest arguments, so a try_it that
# drifts from its check fails here.
PYTEST_RUN = {"fixtures": "test_cart.py", "properties": "test_props.py"}
TRY_PYTEST = re.compile(r"\buv run (?:--with \S+ )*pytest (.+?\.py)\b")

# The pytest settings of the folder a hands-on sits in. Its folder is
# workspace/topics/<id> of a camp, and pytest reads the settings of the nearest
# pyproject.toml above it: this repository's adds -q, a fresh camp has none.
CAMP_INI = {
    "this-repository": (ROOT / "pyproject.toml").read_text(encoding="utf-8"),
    "a-fresh-camp": "",
    "a-quiet-ini": '[tool.pytest.ini_options]\naddopts = "-qq -x"\n',
}

# Correct work the checks have to accept, written another way than WORKED.
GREEN_VARIANT: dict[str, tuple[str, dict[str, str]]] = {
    "apidesign-compact-json": (
        "apidesign",
        {
            "methods.txt": WORKED["apidesign"]["methods.txt"],
            "problem.json": (
                '{"type":"https://example.com/probs/no-such-player",'
                '"title":"No such player.","status":404}'
            ),
        },
    ),
    "supplychain-unquoted": (
        "supplychain",
        {"dependabot.yml": WORKED["supplychain"]["dependabot.yml"].replace('"', "")},
    ),
    "testdoubles-module-import": (
        "testdoubles",
        {
            "test_notify.py": NOTIFY.replace(
                "from unittest.mock import Mock", "from unittest import mock"
            ).replace("send = Mock()", "send = mock.Mock()")
        },
    ),
}

# A near miss where one is the likely mistake, by case: (topic, folder); each
# must be red.
NEAR_MISS: dict[str, tuple[str, dict[str, str]]] = {
    # base64 with padding, the classic PKCE slip: RFC 7636 wants it stripped.
    "oauth": ("oauth", {"pkce.py": PKCE.replace('.rstrip(b"=")', "")}),
    # the stage is copied by number, so reordering the Dockerfile breaks it
    "containers": (
        "containers",
        {
            "Dockerfile": (
                "FROM python:3.12-slim\nFROM python:3.12-slim\nCOPY --from=0 /a /a\n"
            ),
            "compose.yaml": "services:\n  hello:\n    build: .\n",
        },
    ),
    # POST marked idempotent, which RFC 9110 does not say
    "apidesign": (
        "apidesign",
        {
            "methods.txt": WORKED["apidesign"]["methods.txt"].replace(
                "POST neither", "POST idempotent"
            ),
            "problem.json": WORKED["apidesign"]["problem.json"],
        },
    ),
    # every answer written down in the hope that one is right: only the absent
    # list sees it, since the right lines are all there
    "apidesign-every-answer": (
        "apidesign",
        {
            "methods.txt": WORKED["apidesign"]["methods.txt"] + "POST idempotent\n",
            "problem.json": WORKED["apidesign"]["problem.json"],
        },
    ),
    # the licence still carries the choosealicense.com placeholders
    "licences": (
        "licences",
        {
            "LICENSE": MIT.replace("2026 Ada Lovelace", "[year] [fullname]"),
            "hello.py": "# SPDX-License-Identifier: MIT\n",
        },
    ),
    # the key written into the code, under its own name or another, in either
    # quote
    "buildersec": (
        "buildersec",
        {
            ".gitignore": ".env\n",
            "app.py": 'import os\nAPI_KEY = "sk-live-123"\nos.environ\n',
        },
    ),
    "buildersec-other-name": (
        "buildersec",
        {
            ".gitignore": ".env\n",
            "app.py": APP.replace(
                'key = os.environ.get("API_KEY")',
                'key = "sk-live-123"\nos.environ.get("API_KEY")',
            ),
        },
    ),
    "buildersec-single-quotes": (
        "buildersec",
        {
            ".gitignore": ".env\n",
            "app.py": "import os\nAPI_KEY='sk-live-123'\nos.environ\n",
        },
    ),
    # the refactoring changed the behaviour: the amount is no longer printed
    "refactoring": (
        "refactoring",
        {"owing.py": OWING.replace('print(f"amount: {outstanding}")', "pass")},
    ),
    # print_details is written but never called: the prints are still inline
    "refactoring-never-called": (
        "refactoring",
        {
            "owing.py": OWING.replace(
                "    print_details(customer, outstanding)\n",
                '    print(f"name: {customer}")\n    print(f"amount: {outstanding}")\n',
            )
        },
    ),
    # a review with no verdict at the end
    "codereview": (
        "codereview",
        {
            "review.md": WORKED["codereview"]["review.md"].replace(
                "Verdict: LGTM once the retry moves.\n", ""
            )
        },
    ),
    # the mock expects the wrong call, so the test itself fails
    "testdoubles": (
        "testdoubles",
        {
            "test_notify.py": NOTIFY.replace(
                'assert_called_once_with("ada", "welcome")',
                'assert_called_once_with("ada", "goodbye")',
            )
        },
    ),
}

# A pytest exercise whose run is wrong, by case: (topic, test file text).
PYTEST_NEAR_MISS: dict[str, tuple[str, str]] = {
    "fixtures-a-failing-test": ("fixtures", CART.replace("== total", "== total + 1")),
    # fourteen passed is not four passed, though its line ends in "4 passed"
    "fixtures-fourteen-tests": (
        "fixtures",
        CART.replace(
            "[(2, 3, 6), (5, 0, 0), (1, 10, 10)]", "[(n, 1, n) for n in range(13)]"
        ),
    ),
}


def _pack() -> list[topics.Topic]:
    return topics.in_pack(PACK)


def _write(here: Path, files: dict[str, str]) -> None:
    for name, text in files.items():
        (here / name).write_text(text, encoding="utf-8")


def _pytest_args(topic_id: str) -> list[str]:
    """The arguments the try_it gives pytest, up to the test file it names."""
    found = TRY_PYTEST.search(topics.get(topic_id).try_it or "")
    assert found, f"{topic_id}: the try_it names no uv run ... pytest command"
    return shlex.split(found.group(1))


def _run_try_it(here: Path, topic_id: str) -> str:
    """Run the try_it's pytest command in the folder; the report is its output."""
    name = PYTEST_RUN[topic_id]
    written = (here / name).read_text(encoding="utf-8")
    if "hypothesis" in written and find_spec("hypothesis") is None:
        (here / name).write_text(PROPS_STANDIN, encoding="utf-8")
    # The options of the run this test is part of are not the learner's.
    env = {k: v for k, v in os.environ.items() if k != "PYTEST_ADDOPTS"}
    try:
        out = subprocess.run(
            [sys.executable, "-m", "pytest", *_pytest_args(topic_id)],
            cwd=here,
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
    finally:
        (here / name).write_text(written, encoding="utf-8")
    return out.stdout


def _camp_folder(root: Path, topic_id: str, ini: str) -> Path:
    """workspace/topics/<id> of a camp whose pyproject.toml holds `ini`."""
    if ini:
        (root / "pyproject.toml").write_text(ini, encoding="utf-8")
    here = root / "workspace" / "topics" / topic_id
    here.mkdir(parents=True)
    return here


# ---- the pack -------------------------------------------------------------------


def test_the_pack_loads_in_its_reading_order_on_the_ship_shelf() -> None:
    pack = next(p for p in topics.packs() if p.id == PACK)
    assert pack.shelf == "ship" and pack.blurb and pack.maintainer
    assert [t.id for t in _pack()] == ORDER == pack.topics
    assert set(WORKED) == set(ORDER)


def test_the_devops_topics_read_as_one_sequence_after_ci() -> None:
    at = [ORDER.index(t) for t in DEVOPS]
    assert at == sorted(at)
    assert "ci" in topics.get("delivery").prerequisites
    for before, after in zip(DEVOPS, DEVOPS[1:], strict=False):
        linked = after in topics.get(before).unlocks or before in (
            topics.get(after).prerequisites
        )
        assert linked, (before, after)


def test_the_core_topics_stay_in_core_and_are_linked_not_copied() -> None:
    titles = {t.title for t in _pack()}
    linked = {x for t in _pack() for x in (*t.unlocks, *t.prerequisites)}
    for tid in CORE:
        core = topics.get(tid)
        assert core.pack == "core", tid
        assert core.title not in titles, tid
    assert {"tests", "ci", "docker", "kubernetes", "http", "apis"} <= linked


def test_every_topic_is_written_under_the_content_rule() -> None:
    for topic in _pack():
        assert topic.checked is not None, topic.id
        assert safe_title(topic.title) == topic.title, topic.id
        assert topic.summary and topic.history and topic.try_it, topic.id
        assert topic.for_agents, topic.id
        assert 3 <= len(topic.sources) <= 6, topic.id
        for source in topic.sources:
            assert source.url.startswith("https://"), (topic.id, source.url)
            assert source.checked == topic.checked, (topic.id, source.url)


def test_no_file_in_the_pack_carries_an_em_dash_or_a_scaffold_marker() -> None:
    dash = chr(0x2014)  # spelled as a code point so this file passes the style check
    for path in sorted(FOLDER.glob("*.toml")):
        text = path.read_text(encoding="utf-8")
        assert dash not in text and "TODO" not in text, path.name


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


def test_at_most_a_quarter_of_the_primary_origins_sit_on_the_internet() -> None:
    primary = [o for t in _pack() for o in t.origins if o.primary]
    online = [o for o in primary if o.place == "the-internet"]
    assert len(online) * 4 <= len(primary), [o.what for o in online]


def test_every_primary_origin_is_also_a_cited_source() -> None:
    for topic in _pack():
        primary = next(o for o in topic.origins if o.primary)
        assert primary.source in {s.url for s in topic.sources}, topic.id


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
    names = [spec["file"]] if "file" in spec else list(spec.get("files", {}))
    for name in names:
        (stub / name).write_text(f"# TODO: {hands_on.title}\n", encoding="utf-8")
    assert not run_spec(stub, spec)[0]

    done = tmp_path / "done"
    done.mkdir()
    _write(done, WORKED[topic_id])
    if topic_id in PYTEST_RUN:
        _run_try_it(done, topic_id)
    ok, detail = run_spec(done, spec)
    assert ok, detail


@pytest.mark.parametrize("case", sorted(NEAR_MISS))
def test_a_near_miss_is_red(case: str, tmp_path: Path) -> None:
    topic_id, files = NEAR_MISS[case]
    spec = topics.get(topic_id).hands_on.check  # type: ignore[union-attr]
    _write(tmp_path, files)
    ok, detail = run_spec(tmp_path, spec)
    assert not ok, detail


@pytest.mark.parametrize("case", sorted(GREEN_VARIANT))
def test_correct_work_written_another_way_is_green(case: str, tmp_path: Path) -> None:
    topic_id, files = GREEN_VARIANT[case]
    spec = topics.get(topic_id).hands_on.check  # type: ignore[union-attr]
    _write(tmp_path, files)
    ok, detail = run_spec(tmp_path, spec)
    assert ok, detail


@pytest.mark.parametrize("ini", sorted(CAMP_INI))
@pytest.mark.parametrize("topic_id", sorted(PYTEST_RUN))
def test_a_pytest_hands_on_is_green_in_a_camp_whatever_its_pytest_settings(
    topic_id: str, ini: str, tmp_path: Path
) -> None:
    spec = topics.get(topic_id).hands_on.check  # type: ignore[union-attr]
    here = _camp_folder(tmp_path, topic_id, CAMP_INI[ini])
    _write(here, WORKED[topic_id])
    printed = _run_try_it(here, topic_id)
    ok, detail = run_spec(here, spec)
    assert ok, f"{detail}; pytest printed: {printed[-300:]}"


@pytest.mark.parametrize("case", sorted(PYTEST_NEAR_MISS))
def test_a_wrong_pytest_run_is_red(case: str, tmp_path: Path) -> None:
    topic_id, text = PYTEST_NEAR_MISS[case]
    spec = topics.get(topic_id).hands_on.check  # type: ignore[union-attr]
    here = _camp_folder(tmp_path, topic_id, CAMP_INI["this-repository"])
    _write(here, {PYTEST_RUN[topic_id]: text})
    _run_try_it(here, topic_id)
    ok, detail = run_spec(here, spec)
    assert not ok, detail


def test_the_pkce_script_prints_the_rfc_7636_example(tmp_path: Path) -> None:
    _write(tmp_path, {"pkce.py": PKCE})
    out = subprocess.run(
        [sys.executable, "pkce.py"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=60,
    )
    challenge = "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"
    assert out.stdout.strip() == (
        f"code_challenge={challenge}&code_challenge_method=S256"
    )
    assert challenge in (topics.get("oauth").history or "")
