"""Render the screenshots and the gameplay GIF for the README and the docs.

Everything comes from the built game through headless Chromium with software
WebGL, so the pictures always match the code. Output lands in docs/media/.

    uv run python tools/media.py            all screenshots and the GIF
    uv run python tools/media.py --quick    screenshots only
"""

from __future__ import annotations

import functools
import http.server
import json
import sys
import threading
from pathlib import Path

from PIL import Image
from playwright.sync_api import Page, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "media"
GAME = "/game/vibe-map.html"
CHROMIUM_ARGS = [
    "--use-angle=swiftshader",
    "--use-gl=angle",
    "--enable-unsafe-swiftshader",
    "--ignore-gpu-blocklist",
    "--enable-webgl",
]
PLAYED = {
    "name": "<your_name>",
    "done": [1, 2, 3, 4, 5],
    "doneW": {"campus": [1, 2, 3, 4, 5], "winter": [1, 2], "desert": [], "prod": []},
    "path": {"cherny": "deep", "karpathy": "deep", "lecun": "skip"},
    "rolls": [12, 7, 19],
    "versions": [{"t": "A scoring board ranked by coffee", "at": "2026-09-25T20:41"}],
    "bridges": {"cal": True, "files": True},
    "date": None,
    "wine": None,
    "world": "campus",
    "mascot": {
        "name": "Gilded Otter", "str": 12, "wis": 17, "cha": 9,
        "badge": False, "hue": 40,
    },
}  # fmt: skip


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args: object) -> None:
        pass


def _serve() -> tuple[http.server.ThreadingHTTPServer, str]:
    handler = functools.partial(_Quiet, directory=str(ROOT))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    host, port = httpd.server_address[:2]
    return httpd, f"http://{host}:{port}{GAME}"


def _load(page: Page, url: str, state: dict | None) -> None:
    page.goto(url)
    if state is not None:
        page.evaluate(
            "([k, v]) => localStorage.setItem(k, JSON.stringify(v))",
            ["vibemap1", state],
        )
        page.reload()
    page.wait_for_function("typeof window.__S === 'function'")
    page.wait_for_timeout(400)


def _start(page: Page) -> None:
    page.click("#btn-continue, #title button.primary")
    page.wait_for_selector("#title.off", state="attached")
    page.wait_for_timeout(1500)


def screenshots(browser, url: str) -> list[Path]:
    out: list[Path] = []
    OUT.mkdir(parents=True, exist_ok=True)

    # Hero: the title screen at the social-card size.
    ctx = browser.new_context(
        viewport={"width": 1200, "height": 630}, device_scale_factor=2
    )
    page = ctx.new_page()
    _load(page, url, None)
    # The island orbits behind the title; give it a turn before the shot.
    page.wait_for_timeout(2200)
    page.screenshot(
        path=str(OUT / "hero.png"), clip={"x": 0, "y": 0, "width": 1200, "height": 630}
    )
    out.append(OUT / "hero.png")
    ctx.close()

    # Desktop: every world with a played state, then roadmap, vault and tree.
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 760}, device_scale_factor=1
    )
    page = ctx.new_page()
    _load(page, url, PLAYED)
    _start(page)
    for world in ("campus", "winter", "desert", "prod"):
        page.evaluate(f"setWorld('{world}')")
        page.wait_for_timeout(1800)
        page.screenshot(
            path=str(OUT / f"island-{world}.png"),
            clip={"x": 0, "y": 0, "width": 1280, "height": 640},
        )
        out.append(OUT / f"island-{world}.png")
    page.evaluate("setWorld('campus')")
    page.wait_for_timeout(1200)
    page.click("#hud button:has-text('Roadmap')")
    page.wait_for_timeout(600)
    page.screenshot(path=str(OUT / "roadmap.png"), full_page=True)
    out.append(OUT / "roadmap.png")
    page.click("#hud button:has-text('Vault')")
    page.wait_for_timeout(2500)
    page.locator("#vault").screenshot(path=str(OUT / "vault.png"))
    out.append(OUT / "vault.png")
    page.click("#vtop button:has-text('Tech tree')")
    page.wait_for_timeout(600)
    page.locator("#vault").screenshot(path=str(OUT / "tree.png"))
    out.append(OUT / "tree.png")
    ctx.close()

    # Phone.
    ctx = browser.new_context(
        viewport={"width": 393, "height": 852},
        device_scale_factor=2,
        is_mobile=True,
        has_touch=True,
    )
    page = ctx.new_page()
    _load(page, url, PLAYED)
    _start(page)
    page.screenshot(
        path=str(OUT / "phone.png"), clip={"x": 0, "y": 0, "width": 393, "height": 640}
    )
    out.append(OUT / "phone.png")
    ctx.close()
    return out


def gameplay_gif(browser, url: str, *, frames: int = 36) -> Path:
    """Walk to the 18:00 signpost, open the workstream, claim it: one GIF."""
    ctx = browser.new_context(
        viewport={"width": 640, "height": 480}, device_scale_factor=1
    )
    page = ctx.new_page()
    _load(page, url, None)
    _start(page)
    shots: list[Image.Image] = []

    def snap(n: int = 1) -> None:
        for _ in range(n):
            png = page.screenshot(clip={"x": 0, "y": 0, "width": 640, "height": 480})
            shots.append(Image.open(_bytes(png)).convert("RGB"))
            page.wait_for_timeout(120)

    snap(3)
    page.mouse.click(300, 380)  # tap the ground near the 18:00 plot
    for _ in range(frames // 3):
        snap()
    page.click("#hud button:has-text('Roadmap')")
    page.wait_for_timeout(500)
    snap(4)
    page.evaluate("openCh(1)")
    page.wait_for_timeout(500)
    page.evaluate("window.scrollTo(0, 0)")
    snap(4)
    page.evaluate("claim(1)")
    page.wait_for_timeout(300)
    for _ in range(frames // 3):
        snap()
    ctx.close()
    target = OUT / "gameplay.gif"
    small = [im.resize((480, 360), Image.LANCZOS).quantize(colors=128) for im in shots]
    small[0].save(
        target,
        save_all=True,
        append_images=small[1:],
        duration=120,
        loop=0,
        optimize=True,
    )
    return target


def _bytes(data: bytes):
    import io

    return io.BytesIO(data)


def main() -> None:
    quick = "--quick" in sys.argv
    httpd, url = _serve()
    with sync_playwright() as p:
        browser = p.chromium.launch(args=CHROMIUM_ARGS)
        paths = screenshots(browser, url)
        if not quick:
            paths.append(gameplay_gif(browser, url))
        browser.close()
    httpd.shutdown()
    for path in paths:
        print(f"{path.relative_to(ROOT)}  {path.stat().st_size // 1024} KB")
    print(json.dumps({"files": len(paths)}))


if __name__ == "__main__":
    main()
