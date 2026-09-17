"""Shared fixtures: a static server over the repo and Playwright browsers.

The game is one HTML file, but it is served over HTTP rather than opened as a
file URL because WebKit sandboxes localStorage on file origins and the real
deployment is GitHub Pages. Browsers are session scoped (launch once), pages
are function scoped (fresh origin state per test).
"""

from __future__ import annotations

import base64
import functools
import http.server
import json
import math
import threading
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest
from playwright.sync_api import Browser, Page, Playwright, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tests" / "out"
GAME_PATH = "/game/vibe-map.html"
STORAGE_KEY = "vibemap1"

# Software WebGL for headless Chromium. Without ANGLE on SwiftShader the
# canvas has no context and the game falls back to the roadmap list, which
# would hide every 3D regression behind a green test.
CHROMIUM_ARGS = [
    "--use-angle=swiftshader",
    "--use-gl=angle",
    "--enable-unsafe-swiftshader",
    "--ignore-gpu-blocklist",
    "--enable-webgl",
]


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        pass


@pytest.fixture(scope="session")
def server() -> Iterator[str]:
    """Serve the repo root on a free localhost port for the whole session."""
    handler = functools.partial(_QuietHandler, directory=str(ROOT))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    host, port = httpd.server_address[:2]
    yield f"http://{host}:{port}"
    httpd.shutdown()


@pytest.fixture(scope="session")
def playwright() -> Iterator[Playwright]:
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def chromium(playwright: Playwright) -> Iterator[Browser]:
    browser = playwright.chromium.launch(args=CHROMIUM_ARGS)
    yield browser
    browser.close()


@pytest.fixture(scope="session")
def webkit(playwright: Playwright) -> Iterator[Browser]:
    browser = playwright.webkit.launch()
    yield browser
    browser.close()


def encode_progress(
    *,
    name: str = "Lotte",
    done_w: dict[str, list[int]] | None = None,
    path: dict[str, str] | None = None,
    version: int = 2,
) -> str:
    """Build the base64url progress code the CLI and the game exchange."""
    done_w = done_w or {"campus": []}
    payload = {
        "v": version,
        "name": name,
        "done": done_w.get("campus", []),
        "doneW": done_w,
        "path": path or {},
    }
    raw = json.dumps(payload).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


@dataclass
class GamePage:
    """A page with the game loaded and its console errors collected.

    Every helper drives the real entry point (a click on the real button)
    rather than calling the function behind it, so a dead click path fails
    the test even when the mechanism still works.
    """

    page: Page
    url: str
    errors: list[str] = field(default_factory=list)

    def goto(self, *, state: dict[str, Any] | None = None) -> GamePage:
        """Load the game, optionally seeding localStorage first."""
        self.page.goto(self.url)
        if state is not None:
            self.page.evaluate(
                "([k, v]) => localStorage.setItem(k, JSON.stringify(v))",
                [STORAGE_KEY, state],
            )
            self.page.reload()
        self.page.wait_for_function("typeof window.__S === 'function'")
        return self

    def start(self, name: str = "Lotte") -> None:
        self.page.fill("#name", name)
        self.page.click("text=Kick off the engagement")
        self.page.wait_for_selector("#title.off", state="attached")
        self.page.wait_for_timeout(600)

    def resume(self) -> None:
        self.page.click("text=Resume in-flight workstream")
        self.page.wait_for_selector("#title.off", state="attached")
        self.page.wait_for_timeout(600)

    def walk_to(self, x: float, z: float, *, tol: float = 1.6, steps: int = 70) -> None:
        """Steer the walker to a world coordinate with the arrow keys.

        The keyboard is one of the two documented ways to move, so this drives
        the real input path rather than writing the walker's position.
        """
        kb = self.page.keyboard
        held: set[str] = set()

        def hold(want: set[str]) -> None:
            for k in want - held:
                kb.down(k)
                held.add(k)
            for k in held - want:
                kb.up(k)
            held.intersection_update(want)

        try:
            for _ in range(steps):
                pos = self.page.evaluate("window.__debug().pos")
                dx, dz = x - pos[0], z - pos[2]
                if math.hypot(dx, dz) < tol:
                    return
                want: set[str] = set()
                if dx > 0.5:
                    want.add("ArrowRight")
                elif dx < -0.5:
                    want.add("ArrowLeft")
                if dz > 0.5:
                    want.add("ArrowDown")
                elif dz < -0.5:
                    want.add("ArrowUp")
                hold(want)
                self.page.wait_for_timeout(160)
        finally:
            hold(set())
            self.page.wait_for_timeout(400)

    def near(self) -> Any:
        return self.page.evaluate("window.__debug().near")

    def state(self) -> dict[str, Any]:
        return self.page.evaluate("window.__S()")

    def webgl_started(self) -> bool:
        return bool(
            self.page.evaluate(
                "() => { const c = document.getElementById('c');"
                " return !!(c && c.width > 0 && c.height > 0); }"
            )
        )

    def open_roadmap(self) -> None:
        self.page.click("#hud button:has-text('Roadmap')")
        self.page.wait_for_selector("#sheet.on", state="attached")
        self.page.wait_for_selector("#plotlist button", state="attached")
        self.page.wait_for_timeout(500)  # the sheet springs in over ~400 ms

    def workstream_buttons(self):
        """The eight workstream buttons, skipping Pre-flight on the campus."""
        buttons = self.page.locator("#plotlist button")
        offset = 1 if "Pre-flight" in (buttons.nth(0).text_content() or "") else 0
        return [buttons.nth(offset + i) for i in range(8)]

    def open_workstream(self, n: int) -> None:
        self.open_roadmap()
        self.workstream_buttons()[n - 1].click()
        self.page.wait_for_selector("#sheet .screen.on", state="attached")

    def claim(self, n: int) -> None:
        self.open_workstream(n)
        self.page.click("#sheet .screen.on button:has-text('Mark as done')")
        self.page.wait_for_timeout(400)

    def open_vault(self) -> None:
        self.page.click("#hud button:has-text('Vault')")
        self.page.wait_for_selector("#vault.on", state="attached")
        self.page.wait_for_timeout(300)

    def close_vault(self) -> None:
        self.page.click("#vtop button:has-text('Back to campus')")

    def next_world(self) -> None:
        self.page.click("#hud button:has-text('World')")
        self.page.wait_for_timeout(1200)

    def import_code(self, code: str) -> str:
        self.open_roadmap()
        self.page.fill("#impcode", code)
        self.page.click("#s-map button:has-text('Import')")
        self.page.wait_for_timeout(200)
        return self.page.text_content("#syncmsg") or ""

    def screenshot(self, name: str, *, clip_height: int | None = None) -> Path:
        OUT.mkdir(parents=True, exist_ok=True)
        target = OUT / f"{name}.png"
        if clip_height:
            width = self.page.viewport_size["width"] if self.page.viewport_size else 420
            self.page.screenshot(
                path=str(target),
                clip={"x": 0, "y": 0, "width": width, "height": clip_height},
            )
        else:
            self.page.screenshot(path=str(target), full_page=True)
        return target

    def assert_clean(self) -> None:
        assert self.errors == [], f"page errors: {self.errors}"


def _attach_error_collectors(page: Page, errors: list[str]) -> None:
    page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
    page.on(
        "console",
        lambda m: (
            errors.append(f"console.error: {m.text}")
            if m.type == "error" and "favicon" not in m.text
            else None
        ),
    )


@pytest.fixture
def game(chromium: Browser, server: str) -> Iterator[GamePage]:
    """A fresh Chromium page at a phone-sized viewport, errors collected."""
    context = chromium.new_context(viewport={"width": 420, "height": 860})
    page = context.new_page()
    gp = GamePage(page=page, url=server + GAME_PATH)
    _attach_error_collectors(page, gp.errors)
    yield gp
    context.close()


@pytest.fixture
def game_webkit_iphone(webkit: Browser, server: str) -> Iterator[GamePage]:
    """WebKit with iPhone 15 metrics and touch, the closest headless proxy for iOS."""
    context = webkit.new_context(
        viewport={"width": 393, "height": 852},
        device_scale_factor=3,
        is_mobile=True,
        has_touch=True,
        user_agent=(
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
            "Mobile/15E148 Safari/604.1"
        ),
    )
    page = context.new_page()
    gp = GamePage(page=page, url=server + GAME_PATH)
    _attach_error_collectors(page, gp.errors)
    yield gp
    context.close()
