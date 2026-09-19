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
# The two title buttons carry theme wording, so the tests address their place
# in the form instead of their label.
GO_BUTTON = "#title .row.go button.primary"
RESUME_BUTTON = "#btn-continue"
# One budget for every wait on a page signal. Generous, because a loaded CI
# runner is slow, not broken; a wait that runs out is a real defect.
WAIT_MS = 20_000

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
    mentors: list[str] | None = None,
    artifacts_built: list[str] | None = None,
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
        "mentors": mentors or [],
        "artifactsBuilt": artifacts_built or [],
    }
    raw = json.dumps(payload).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


# Wait until a number the page computes stops changing. A spring and a smooth
# scroll have no completion event, so "it has not moved over five painted
# frames" is the signal. The timer paces the sampling, because software WebGL
# renders at a handful of frames a second and the scroll does not wait for it,
# but a sample only counts once the page has painted again: on a loaded runner
# the timer outruns the frames a spring advances on, and a value that has not
# moved because nothing was drawn is not stillness, it is a stale read. The
# deadline keeps a value that never settles from hanging a test.
STILL = """expr => new Promise(done => {
  const read = new Function('return (' + expr + ')');
  let last = null, stable = 0, painted = 0, sampled = -1, running = true;
  const frame = () => { painted++; if (running) requestAnimationFrame(frame); };
  requestAnimationFrame(frame);
  const deadline = performance.now() + 4000;
  const stop = () => { running = false; done(true); };
  const tick = () => {
    if (painted > sampled) {
      const v = read();
      stable = last !== null && Math.abs(v - last) < 0.5 ? stable + 1 : 0;
      sampled = painted;
      last = v;
    }
    if (stable >= 5 || performance.now() > deadline) return stop();
    setTimeout(tick, 32);
  };
  tick();
})"""


@dataclass
class GamePage:
    """A page with the game loaded and its console errors collected.

    Every helper drives the real entry point (a click on the real button)
    rather than calling the function behind it, so a dead click path fails
    the test even when the mechanism still works. Every helper waits for a
    signal the page produces, never for a wall clock, so a slow runner is
    slow rather than red.
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

    def frames(self, n: int = 3) -> None:
        """Wait for the frame loop to draw n more frames.

        Proximity, the camera and the pop-in animations are sampled in the
        loop, so a read straight after a click can be a frame stale.
        """
        start = int(self.page.evaluate("window.__debug().frame") or 0)
        self.page.wait_for_function(
            "n => window.__debug().frame >= n", arg=start + n, timeout=WAIT_MS
        )

    def still(self, expression: str) -> None:
        """Wait until a numeric JavaScript expression stops changing."""
        self.page.wait_for_function(STILL, arg=expression, timeout=WAIT_MS)

    def until(self, expression: str) -> None:
        """Wait for a condition the page makes true.

        The counterpart to still() for a fact that has a shape rather than a
        value: it is the assertion's own condition, so a layout that never
        reaches it runs out of the budget and fails as the defect it is.
        """
        self.page.wait_for_function(f"() => ({expression})", timeout=WAIT_MS)

    def _entered(self) -> None:
        """The title is gone, the 3D scene runs and the first frames are drawn."""
        self.page.wait_for_selector("#title.off", state="attached")
        self.page.wait_for_function(
            "window.__debug().started === true", timeout=WAIT_MS
        )
        self.frames()

    def start(self, name: str = "Lotte") -> None:
        self.page.fill("#name", name)
        self.page.click(GO_BUTTON)
        self._entered()

    def resume(self) -> None:
        self.page.click(RESUME_BUTTON)
        self._entered()

    def walk_to(
        self, x: float, z: float, *, tol: float = 1.6, steps: int = 400
    ) -> None:
        """Steer the walker to a world coordinate with the arrow keys.

        The keyboard is one of the two documented ways to move, so this drives
        the real input path rather than writing the walker's position. The
        steering loop ticks on rendered frames, which is the unit the walker
        actually moves in, so a slow runner takes longer and never drifts off.
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
                self.frames(4)
        finally:
            hold(set())
            self.frames()

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

    def sheet_in_place(self) -> None:
        """Wait for the sheet's spring and openSheet's smooth scroll to finish.

        The spring is driven by animation frames. A loaded runner starves
        those, so a sampler reading every 32 ms sees the same number twice and
        calls a sheet that is still 16 px low settled. The transform reaching
        identity is the page's own end of the spring, so that is waited for
        first and the scroll is sampled after.
        """
        self.page.wait_for_function(
            "() => {const t = getComputedStyle("
            "document.getElementById('sheet')).transform;"
            " return t === 'none' || Math.abs(new DOMMatrix(t).m42) < 0.5;}",
            timeout=WAIT_MS,
        )
        self.still("document.getElementById('sheet').getBoundingClientRect().top")

    def hud_action(self, selector: str) -> None:
        """Click a HUD button, opening the More menu when it lives in there.

        Which buttons are in the pill and which are behind More is a width
        question the stylesheet answers, so the helper asks the page rather
        than the viewport. The HUD stays above the sheet overlay, so an open
        sheet is not in the way.
        """
        button = self.page.locator(selector)
        if not button.is_visible():
            self.page.click("#hud-more-btn")
            self.page.wait_for_selector("#hud-more.open", state="attached")
            button.wait_for(state="visible", timeout=WAIT_MS)
        button.click()

    def open_roadmap(self) -> None:
        self.hud_action("#hud button:has-text('Roadmap')")
        self.page.wait_for_selector("#sheet.on", state="attached")
        self.page.wait_for_selector("#plotlist button", state="attached")
        self.sheet_in_place()

    def workstream_buttons(self):
        """The eight workstream buttons, skipping Pre-flight on the campus."""
        buttons = self.page.locator("#plotlist button")
        offset = 1 if "Pre-flight" in (buttons.nth(0).text_content() or "") else 0
        return [buttons.nth(offset + i) for i in range(8)]

    def open_workstream(self, n: int) -> None:
        self.open_roadmap()
        self.workstream_buttons()[n - 1].click()
        self.page.wait_for_selector("#sheet .screen.on", state="attached")
        self.sheet_in_place()

    def claim(self, n: int) -> None:
        self.open_workstream(n)
        self.page.click("#sheet .screen.on button:has-text('Mark as done')")
        self.page.wait_for_function(
            "n => (window.__S().doneW[window.__S().world] || []).includes(n)",
            arg=n,
            timeout=WAIT_MS,
        )
        self.frames()

    def open_vault(self) -> None:
        self.hud_action("#hud button:has-text('Vault')")
        self.page.wait_for_selector("#vault.on", state="attached")
        self.page.wait_for_selector("#vnote .wl", state="attached")

    def close_vault(self) -> None:
        self.page.click("#vtop button:has-text('Back to campus')")

    def next_world(self) -> None:
        before = self.page.evaluate("window.__S().world")
        self.hud_action("#hud button:has-text('World')")
        self.page.wait_for_function(
            "w => window.__S().world !== w", arg=before, timeout=WAIT_MS
        )
        self.frames()

    def import_code(self, code: str) -> str:
        self.open_roadmap()
        # Two imports in a row can produce the same message; clear it first so
        # the wait is for this import's answer, not the previous one's.
        self.page.evaluate("document.getElementById('syncmsg').textContent = ''")
        self.page.fill("#impcode", code)
        self.page.click("#s-map button:has-text('Import')")
        self.page.wait_for_function(
            "() => (document.getElementById('syncmsg').textContent || '') !== ''",
            timeout=WAIT_MS,
        )
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


# Every test that takes a browser fixture is a browser test. Marking it here
# rather than by hand keeps the CI split honest: a new browser test lands in
# the browser job without anyone remembering to label it.
BROWSER_FIXTURES = frozenset(
    {
        "game",
        "game_desktop",
        "game_webkit_iphone",
        "game_android",
        "phone",
        "chromium",
        "webkit",
    }
)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    for item in items:
        if BROWSER_FIXTURES & set(getattr(item, "fixturenames", ())):
            item.add_marker("browser")


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
def game_desktop(chromium: Browser, server: str) -> Iterator[GamePage]:
    """A fresh Chromium page at 1440x900: the laptop the course is written for."""
    context = chromium.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()
    gp = GamePage(page=page, url=server + GAME_PATH)
    _attach_error_collectors(page, gp.errors)
    yield gp
    context.close()


@pytest.fixture
def game_android(chromium: Browser, server: str) -> Iterator[GamePage]:
    """Chromium with Pixel 7 metrics: the phone the owner actually plays on."""
    context = chromium.new_context(
        viewport={"width": 412, "height": 915},
        device_scale_factor=2.625,
        is_mobile=True,
        has_touch=True,
        user_agent=(
            "Mozilla/5.0 (Linux; Android 14; Pixel 7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/126.0.0.0 Mobile Safari/537.36"
        ),
    )
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
