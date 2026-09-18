"""Render the onboarding screens into docs/media, pet and all.

Textual exports a screen as SVG; headless Chromium turns that SVG into a PNG,
and Pillow stacks a run of frames into the GIF. Everything comes from the real
app, so the pictures cannot drift from the code.

    uv run python tools/tui_media.py              the launch screen and the GIF
    uv run python tools/tui_media.py --quick      the PNG only
"""

from __future__ import annotations

import asyncio
import sys
import tempfile
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

OUT = ROOT / "docs" / "media"
SIZE = (120, 50)
NAME = "<your_name>"
SPECIES = "crab"
# One full stroll of the pet, at the eight frames a second the widget runs.
FRAMES = 40
# The fraction of the screen the GIF keeps: the status line and the pet.
BAND = 0.36


async def _svgs(count: int, gap: float) -> list[str]:
    """The launch screen, exported once per pet tick."""
    from vibemap.config import Config
    from vibemap.tui import Launch, VibeApp

    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp)
        config_path = home / "config" / "camp.toml"
        config_path.parent.mkdir(parents=True)
        # The picture is about the sprites, so pin a species that has them.
        cfg = Config()
        cfg.pet.species = SPECIES
        cfg.pet.style = "pixel"
        cfg.save(config_path)
        app = VibeApp(config_path=config_path, state_path=home / "state.json")
        shots: list[str] = []
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause()
            app.screen.query_one("#name").value = NAME
            await pilot.click("#next")
            await pilot.pause()
            await pilot.click("#next")
            await pilot.pause()
            assert isinstance(app.screen, Launch), app.screen
            for _ in range(count):
                await pilot.pause(gap)
                shots.append(app.export_screenshot())
            await pilot.click("#act-quit")
        return shots


def _png(page, svg: str, path: Path) -> None:
    page.set_content(svg)
    element = page.locator("svg").first
    element.screenshot(path=str(path))


def main() -> int:
    quick = "--quick" in sys.argv
    frames = 1 if quick else FRAMES
    OUT.mkdir(parents=True, exist_ok=True)
    svgs = asyncio.run(_svgs(frames, 0.125))
    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        shots: list[Path] = []
        for n, svg in enumerate(svgs):
            shot = Path(tmp) / f"{n:03d}.png"
            _png(page, svg, shot)
            shots.append(shot)
        browser.close()
        still = OUT / "tui-pet.png"
        still.write_bytes(shots[0].read_bytes())
        print(f"{still.relative_to(ROOT)}  {still.stat().st_size // 1024} KB")
        if quick:
            return 0
        images = [Image.open(s).convert("RGB") for s in shots]
        # Only the top of the screen moves, so the GIF carries only that band.
        band = round(images[0].height * BAND)
        images = [im.crop((0, 0, im.width, band)) for im in images]
        wide = images[0].width
        small = [
            im.resize((760, round(im.height * 760 / wide)), Image.LANCZOS).quantize(
                colors=64
            )
            for im in images
        ]
        target = OUT / "tui-pet.gif"
        small[0].save(
            target,
            save_all=True,
            append_images=small[1:],
            duration=125,
            loop=0,
            optimize=True,
        )
        print(f"{target.relative_to(ROOT)}  {target.stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
