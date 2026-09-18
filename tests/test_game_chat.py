"""The chat panel in the game, against a real bridge and against no bridge.

The bridge here is the real one from `vibe chat serve` with a fake provider in
place of the CLI, so the page talks HTTP to the same code the learner runs.
"""

from __future__ import annotations

import socket
import threading
from collections.abc import Iterator
from typing import Any

import pytest

from tests.conftest import WAIT_MS, GamePage
from vibemap import chat
from vibemap.config import Config

CODE = "ABCD2345"
ANSWER = "A stop is one hour of the evening. Open the roadmap and pick the next one."


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


def fake_runner(provider_id: str, prompt: str, timeout: int) -> Iterator[str]:
    """Answers without a subscription, and echoes that the prompt carried the stop."""
    if "Data Warehouse" in prompt:
        yield "About stop 3. "
    for word in ANSWER.split(" "):
        yield word + " "


def assert_clean_except_network(game: GamePage) -> None:
    """Zero page errors, minus the ones the browser logs for a refused fetch.

    A panel with no bridge is a tested path, and Chromium logs the failed
    request itself; anything else in the list is a real defect.
    """
    left = [e for e in game.errors if "Failed to load resource" not in e]
    assert left == [], f"page errors: {left}"


@pytest.fixture
def bridge_url() -> Iterator[str]:
    bridge = chat.Bridge(Config.load(), code=CODE, runner=fake_runner)
    server = chat.serve(bridge, port=0)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()


def seed(port: int) -> dict[str, Any]:
    return {
        "name": "Lotte",
        "doneW": {"campus": [1, 2], "winter": [], "desert": [], "prod": []},
        "chat": {"code": CODE, "port": port, "hist": []},
    }


def open_chat(game: GamePage) -> None:
    game.page.click("#hud button:has-text('Ask')")
    game.page.wait_for_selector("#s-chat.on", state="attached")
    game.page.wait_for_selector("#chatq", state="attached")
    game.sheet_in_place()


def test_the_hud_button_opens_the_panel_with_a_context_chip(game: GamePage) -> None:
    game.goto(state=seed(free_port()))
    game.resume()
    open_chat(game)
    assert "Innovation Campus" in (game.page.text_content("#chatchip") or "")
    assert game.page.locator("#chatsug button").count() >= 1
    game.screenshot("chat_panel", clip_height=860)
    game.assert_clean()


def test_the_c_key_opens_the_panel(game: GamePage) -> None:
    game.goto(state=seed(free_port()))
    game.resume()
    game.page.keyboard.press("c")
    game.page.wait_for_selector("#s-chat.on", state="attached")
    game.assert_clean()


def test_the_chip_follows_the_stop_whose_sheet_is_open(game: GamePage) -> None:
    game.goto(state=seed(free_port()))
    game.resume()
    game.open_workstream(3)
    open_chat(game)
    chip = game.page.text_content("#chatchip") or ""
    assert "stop 3" in chip
    game.assert_clean()


def test_a_bridge_answers_and_the_answer_is_kept(
    game: GamePage, bridge_url: str
) -> None:
    port = int(bridge_url.rsplit(":", 1)[1])
    game.goto(state=seed(port))
    game.resume()
    game.open_workstream(3)
    open_chat(game)
    game.page.fill("#chatq", "what is a stop")
    game.page.click("#s-chat button:has-text('Ask')")
    game.page.wait_for_function(
        "() => (document.querySelector('#chatlog .them')?.textContent || '')"
        ".includes('one hour of the evening')",
        timeout=WAIT_MS,
    )
    assert "About stop 3." in (game.page.text_content("#chatlog .them") or "")
    assert "claude" in (game.page.text_content("#chatlog .src") or "").lower()
    state = game.state()
    assert state["chat"]["hist"][-1]["q"] == "what is a stop"
    assert ANSWER.split(".")[0] in state["chat"]["hist"][-1]["a"]
    game.screenshot("chat_answered", clip_height=860)
    game.assert_clean()


def test_the_history_survives_a_reload(game: GamePage, bridge_url: str) -> None:
    port = int(bridge_url.rsplit(":", 1)[1])
    game.goto(state=seed(port))
    game.resume()
    open_chat(game)
    game.page.fill("#chatq", "what is a stop")
    game.page.click("#s-chat button:has-text('Ask')")
    game.page.wait_for_function(
        "() => (window.__S().chat.hist.slice(-1)[0] || {}).a", timeout=WAIT_MS
    )
    game.page.reload()
    game.page.wait_for_function("typeof window.__S === 'function'")
    game.resume()
    open_chat(game)
    assert "what is a stop" in (game.page.text_content("#chatlog") or "")
    game.assert_clean()


def test_without_a_bridge_the_panel_explains_and_searches_the_notes(
    game: GamePage,
) -> None:
    """Nothing listens on this port, so the panel has to stay useful."""
    game.goto(state=seed(free_port()))
    game.resume()
    open_chat(game)
    game.page.fill("#chatq", "what is a subagent")
    game.page.click("#s-chat button:has-text('Ask')")
    game.page.wait_for_selector("#chathelp", state="attached")
    help_text = game.page.text_content("#chathelp") or ""
    assert f"vibe chat serve --pair {CODE}" in help_text
    answer = game.page.text_content("#chatlog .them") or ""
    assert "Subagent" in answer or "subagent" in answer
    assert "notes in this file" in (game.page.text_content("#chatlog .src") or "")
    game.screenshot("chat_offline", clip_height=860)
    assert_clean_except_network(game)


def test_the_offline_answer_links_into_the_vault(game: GamePage) -> None:
    game.goto(state=seed(free_port()))
    game.resume()
    open_chat(game)
    game.page.fill("#chatq", "what is a subagent")
    game.page.click("#s-chat button:has-text('Ask')")
    game.page.wait_for_selector("#chatlog .wl", state="attached")
    game.page.click("#chatlog .wl")
    game.page.wait_for_selector("#vault.on", state="attached")
    assert_clean_except_network(game)


def test_a_wrong_pairing_code_falls_back_rather_than_hanging(
    game: GamePage, bridge_url: str
) -> None:
    port = int(bridge_url.rsplit(":", 1)[1])
    state = seed(port)
    state["chat"]["code"] = "ZZZZ9999"
    game.goto(state=state)
    game.resume()
    open_chat(game)
    game.page.fill("#chatq", "what is a stop")
    game.page.click("#s-chat button:has-text('Ask')")
    game.page.wait_for_selector("#chathelp", state="attached")
    assert "pairing code" in (game.page.text_content("#chatmsg") or "")
    assert_clean_except_network(game)
