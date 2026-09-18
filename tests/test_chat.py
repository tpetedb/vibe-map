"""The chat bridge: what it refuses, what it builds and what it streams.

Every test drives the real HTTP endpoint with a fake provider, so the refusals
that are the point of the feature (a stranger's origin, a wrong pairing code, a
body that is too big, a second question while one is running) are tested where
they are enforced rather than where they are decided.
"""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from collections.abc import Iterator
from typing import Any

import pytest

from vibemap import chat
from vibemap.config import Config

FAKE_ANSWER = ["a stop is an hour of the evening.\n", "look at the roadmap.\n"]


def fake_runner(provider_id: str, prompt: str, timeout: int) -> Iterator[str]:
    """A provider that never starts a process; it echoes the prompt it was given."""
    yield f"prompt-length:{len(prompt)}\n"
    yield from FAKE_ANSWER


@pytest.fixture
def bridge() -> chat.Bridge:
    return chat.Bridge(Config.load(), code="ABCD2345", runner=fake_runner)


@pytest.fixture
def running(bridge: chat.Bridge) -> Iterator[tuple[str, chat.Bridge]]:
    server = chat.serve(bridge, port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    yield f"http://{host}:{port}", bridge
    server.shutdown()
    server.server_close()


def post(
    url: str,
    payload: dict[str, Any] | bytes,
    *,
    origin: str = "http://localhost:8000",
    code: str | None = "ABCD2345",
    length: int | None = None,
) -> tuple[int, str]:
    body = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
    headers = {"Content-Type": "application/json"}
    if origin:
        headers["Origin"] = origin
    if code is not None:
        headers["X-Vibe-Code"] = code
    if length is not None:
        headers["Content-Length"] = str(length)
    req = urllib.request.Request(url + "/ask", data=body, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


# ---- origins -------------------------------------------------------------------


@pytest.mark.parametrize(
    "origin",
    [
        "http://localhost:8000",
        "http://127.0.0.1:7717",
        "null",
        "https://tpetedb.github.io",
    ],
)
def test_allowed_origins(origin: str) -> None:
    assert chat.origin_allowed(origin)


@pytest.mark.parametrize(
    "origin",
    ["", "https://evil.example", "http://localhost.evil.example", "file://"],
)
def test_refused_origins(origin: str) -> None:
    assert not chat.origin_allowed(origin)


def test_an_extra_origin_can_be_allowed_explicitly() -> None:
    assert chat.origin_allowed("https://me.example", frozenset({"https://me.example"}))


def test_a_stranger_origin_is_refused_by_the_endpoint(running) -> None:
    url, _ = running
    status, body = post(
        url, {"question": "what is a stop"}, origin="https://evil.example"
    )
    assert status == 403
    assert "origin" in json.loads(body)["error"]


def test_a_request_without_an_origin_is_refused(running) -> None:
    url, _ = running
    status, _ = post(url, {"question": "hello"}, origin="")
    assert status == 403


# ---- the pairing code ----------------------------------------------------------


def test_the_code_alphabet_avoids_the_ambiguous_characters() -> None:
    code = chat.new_code()
    assert len(code) == chat.CODE_LENGTH
    assert not set(code) & set("OI01")


def test_a_code_is_read_back_through_spaces_and_case() -> None:
    assert chat.normalise_code("abcd-2345") == "ABCD2345"
    with pytest.raises(ValueError):
        chat.normalise_code("oi0")


def test_a_wrong_code_is_refused(running) -> None:
    url, _ = running
    status, body = post(url, {"question": "hello"}, code="ZZZZ9999")
    assert status == 401
    assert "pairing code" in json.loads(body)["error"]


def test_a_missing_code_is_refused(running) -> None:
    url, _ = running
    assert post(url, {"question": "hello"}, code="")[0] == 401


def test_the_bridge_locks_out_after_too_many_wrong_codes(running) -> None:
    url, bridge = running
    for _ in range(chat.MAX_FAILURES):
        post(url, {"question": "hello"}, code="ZZZZ9999")
    assert bridge.locked_out
    status, body = post(url, {"question": "hello"})
    assert status == 403
    assert "too many" in json.loads(body)["error"]


# ---- the body ------------------------------------------------------------------


def test_an_empty_question_is_refused(running) -> None:
    url, _ = running
    assert post(url, {"question": "   "})[0] == 400


def test_a_body_over_the_cap_is_refused(running) -> None:
    url, _ = running
    status, body = post(url, {"question": "x" * (chat.MAX_BODY + 100)})
    assert status == 413
    assert "bytes" in json.loads(body)["error"]


def test_a_lying_content_length_is_still_capped(running) -> None:
    """The cap is read off the header, so an oversized claim never reaches the read."""
    url, _ = running
    status, _ = post(url, b"{}", length=chat.MAX_BODY + 1)
    assert status == 413


def test_a_question_over_the_character_cap_is_refused() -> None:
    with pytest.raises(ValueError, match="at most"):
        chat.Ask.from_payload({"question": "x" * (chat.MAX_QUESTION + 1)})


def test_an_unknown_world_is_refused() -> None:
    with pytest.raises(ValueError, match="unknown world"):
        chat.Ask.from_payload({"question": "hi", "world": "moon"})


def test_identifiers_that_are_not_identifiers_are_dropped() -> None:
    ask = chat.Ask.from_payload(
        {"question": "hi", "mentor": "karpathy; rm -rf /", "artifact": "cafe"}
    )
    assert ask.mentor is None
    assert ask.artifact == "cafe"


# ---- the prompt ----------------------------------------------------------------


def test_the_prompt_carries_the_stop_the_player_is_on() -> None:
    ask = chat.Ask(question="where do the numbers live", world="campus", stop=3)
    prompt = chat.system_prompt(ask, Config.load())
    assert "Data Warehouse" in prompt
    assert "where do the numbers live" in prompt
    assert "Innovation Campus" in prompt


def test_the_prompt_carries_the_mentor_and_the_artifact_in_view() -> None:
    ask = chat.Ask(question="why", world="campus", mentor="cherny", artifact="cafe")
    prompt = chat.system_prompt(ask, Config.load())
    assert "Boris Cherny" in prompt
    assert "The cafe" in prompt


def test_the_context_line_names_what_the_question_is_about() -> None:
    ask = chat.Ask(question="why", world="campus", stop=3, artifact="cafe")
    line = chat.context_line(ask)
    assert "Innovation Campus" in line
    assert "stop 3" in line
    assert "The cafe" in line


# ---- answering -----------------------------------------------------------------


def test_an_answer_streams_back_as_server_sent_events(running) -> None:
    url, _ = running
    status, body = post(url, {"question": "what is a stop", "stop": 3})
    assert status == 200
    assert "event: start" in body
    assert "event: done" in body
    texts = [
        json.loads(line[len("data: ") :])["text"]
        for line in body.splitlines()
        if line.startswith("data: ") and '"text"' in line
    ]
    assert "".join(texts).endswith("look at the roadmap.\n")
    assert "prompt-length:" in "".join(texts)


def test_only_one_question_is_answered_at_a_time(running) -> None:
    url, bridge = running
    bridge.lock.acquire()
    try:
        status, body = post(url, {"question": "what is a stop"})
    finally:
        bridge.lock.release()
    assert status == 409
    assert "already" in json.loads(body)["error"]


def test_a_missing_provider_binary_is_reported_in_the_stream(running) -> None:
    url, bridge = running

    def missing(provider_id: str, prompt: str, timeout: int) -> Iterator[str]:
        raise chat.ProviderMissing("Claude Code is not installed. Install: curl ...")
        yield  # pragma: no cover

    bridge.runner = missing
    status, body = post(url, {"question": "hello"})
    assert status == 200
    assert "event: error" in body
    assert "not installed" in body


def test_health_says_which_provider_answers(running) -> None:
    url, _ = running
    req = urllib.request.Request(
        url + "/health", headers={"Origin": "http://localhost:8000"}
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        payload = json.loads(resp.read())
    assert payload["ok"] is True
    assert payload["provider"] in {"claude", "codex", "gemini", "copilot", "opencode"}


def test_an_unknown_endpoint_is_a_404(running) -> None:
    url, _ = running
    req = urllib.request.Request(
        url + "/run", headers={"Origin": "http://localhost:8000"}
    )
    with pytest.raises(urllib.error.HTTPError) as e:
        urllib.request.urlopen(req, timeout=10)
    assert e.value.code == 404


def test_the_bridge_binds_loopback_only(running) -> None:
    url, _ = running
    assert url.startswith("http://127.0.0.1:")


# ---- the terminal side ---------------------------------------------------------


def test_vibe_chat_ask_prints_the_answer(monkeypatch: pytest.MonkeyPatch) -> None:
    from click.testing import CliRunner

    from vibemap.cli import cli

    monkeypatch.setattr(chat, "_default_runner", fake_runner)
    result = CliRunner().invoke(
        cli, ["chat", "ask", "where do the numbers live", "-s", "3"]
    )
    assert result.exit_code == 0, result.output
    assert "a stop is an hour" in result.output
    assert "Data Warehouse" in result.output  # the context line


def test_vibe_chat_ask_refuses_an_empty_question() -> None:
    from click.testing import CliRunner

    from vibemap.cli import cli

    result = CliRunner().invoke(cli, ["chat", "ask", "   "])
    assert result.exit_code == 1
    assert "no question" in result.output
