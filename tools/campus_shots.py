"""Two pictures of the campus for the docs: empty, and with every annex out.

Headless Chromium with software WebGL, like tools/media.py, so the pictures
always match the built game. Output lands in docs/media/.

    uv run python tools/campus_shots.py
"""

from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright

from tools.media import CHROMIUM_ARGS, OUT, PLAYED, ROOT, _load, _serve

EXPANDED = dict(
    PLAYED,
    done=[1, 2, 3, 4, 5, 6, 7, 8],
    doneW={"campus": [1, 2, 3, 4, 5, 6, 7, 8], "winter": [], "desert": [], "prod": []},
)
SHOTS = [("island-campus-start.png", None), ("island-campus-expanded.png", EXPANDED)]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    httpd, url = _serve()
    paths: list[Path] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(args=CHROMIUM_ARGS)
        for name, state in SHOTS:
            ctx = browser.new_context(
                viewport={"width": 1280, "height": 760}, device_scale_factor=1
            )
            page = ctx.new_page()
            _load(page, url, state)
            # The title screen's slow orbit frames the whole island; hide the
            # title without starting so the camera stays on that orbit.
            page.evaluate("document.getElementById('title').classList.add('off')")
            page.wait_for_timeout(3500)
            target = OUT / name
            page.screenshot(
                path=str(target),
                clip={"x": 0, "y": 0, "width": 1280, "height": 640},
            )
            paths.append(target)
            ctx.close()
        browser.close()
    httpd.shutdown()
    for path in paths:
        print(f"{path.relative_to(ROOT)}  {path.stat().st_size // 1024} KB")
    print(json.dumps({"files": len(paths)}))


if __name__ == "__main__":
    main()
