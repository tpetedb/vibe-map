"""Render the onboarding screens into docs/media, pet and all.

Textual exports a screen as SVG, rich exports the pet the same way; headless
Chromium turns that SVG into a PNG, and Pillow stacks a run of frames into the
GIF. Everything comes from the real app, so the pictures cannot drift from the
code.

    uv run python tools/tui_media.py              the launch screen and the GIF
    uv run python tools/tui_media.py --quick      the PNG only
    uv run python tools/tui_media.py --pets       the gallery of pixel species
"""

from __future__ import annotations

import asyncio
import io
import sys
import tempfile
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright
from rich.text import Text

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
# The gallery: a narrow panel per species, one stroll each, and a contact
# sheet three species wide.
PET_WIDTH = 44
PET_FRAMES = 24
PET_GIF_WIDTH = 440
SHEET_WIDTH = 84


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


def _gif(shots: list[Path], target: Path, *, wide: int, band: float = 1.0) -> None:
    """A run of PNGs as one looping GIF, narrowed to the width the docs use."""
    images = [Image.open(s).convert("RGB") for s in shots]
    if band < 1.0:
        height = round(images[0].height * band)
        images = [im.crop((0, 0, im.width, height)) for im in images]
    at = images[0].width
    small = [
        im.resize((wide, round(im.height * wide / at)), Image.LANCZOS).quantize(
            colors=64
        )
        for im in images
    ]
    small[0].save(
        target,
        save_all=True,
        append_images=small[1:],
        duration=125,
        loop=0,
        optimize=True,
    )
    print(f"{target.relative_to(ROOT)}  {target.stat().st_size // 1024} KB")


def _console(width: int):
    """A recording console with the camp's theme, as a real terminal has it.

    It renders into a buffer rather than this process's stdout: what comes out
    is the picture, not a screenful of escape codes.
    """
    from rich.console import Console

    from vibemap.palette import RICH_THEME

    return Console(
        record=True,
        width=width,
        force_terminal=True,
        theme=RICH_THEME,
        file=io.StringIO(),
    )


def _terminal_theme():
    """The SVG window in the camp's colours: OLED black, not rich's grey."""
    from rich.terminal_theme import TerminalTheme

    from vibemap import palette

    def rgb(value: str) -> tuple[int, int, int]:
        return tuple(int(value[i : i + 2], 16) for i in (1, 3, 5))  # type: ignore[return-value]

    return TerminalTheme(
        rgb(palette.BLACK),
        rgb(palette.TEXT),
        [
            rgb(palette.SURFACE), rgb(palette.RED), rgb(palette.GREEN),
            rgb(palette.YELLOW), rgb(palette.BLUE), rgb(palette.ORANGE),
            rgb(palette.GREEN), rgb(palette.TEXT),
        ],
    )  # fmt: skip


def _pet_svgs(species: str, count: int) -> list[str]:
    """One species strolling, exported once per tick, as `vibe pet` draws it."""
    from vibemap import pet

    theme = _terminal_theme()
    creature = pet.resolve(NAME, species=species)
    sprite = pet.columns(creature, "pixel")
    out: list[str] = []
    for tick in range(count):
        console = _console(PET_WIDTH)
        console.print(
            pet.render(
                creature,
                tick,
                stats=False,
                offset=pet.stroll(tick, PET_WIDTH - 2, sprite_width=sprite),
                style="pixel",
                state=pet.gait(tick, PET_WIDTH - 2, sprite_width=sprite),
            )
        )
        console.print(f"[muted]{pet.credit(creature, 'pixel')}[/]")
        out.append(
            console.export_svg(title=f"vibe pet --species {species}", theme=theme)
        )
    return out


def _sheet_svg() -> str:
    """Every pixel species at once, the contact sheet the README opens with."""
    from rich.table import Table

    from vibemap import pet, sprites

    grid = Table.grid(padding=(1, 3))
    row: list = []
    for name in sprites.available():
        creature = pet.resolve(NAME, species=name)
        cell = Text(f"{name}\n", style="bold")
        cell.append(pet.body(creature, 0, style="pixel", state="idle"))
        row.append(cell)
        if len(row) == 3:
            grid.add_row(*row)
            row = []
    if row:
        grid.add_row(*row, *[""] * (3 - len(row)))
    console = _console(SHEET_WIDTH)
    console.print(grid)
    return console.export_svg(title="vibe pet --all", theme=_terminal_theme())


def pets() -> int:
    """A still, a clip and a contact sheet for every species with pixels."""
    from vibemap import sprites

    folder = OUT / "pets"
    folder.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        for name in sprites.available():
            svgs = _pet_svgs(name, PET_FRAMES)
            shots = []
            for n, svg in enumerate(svgs):
                shot = Path(tmp) / f"{name}-{n:03d}.png"
                _png(page, svg, shot)
                shots.append(shot)
            still = folder / f"{name}.png"
            still.write_bytes(shots[0].read_bytes())
            print(f"{still.relative_to(ROOT)}  {still.stat().st_size // 1024} KB")
            _gif(shots, folder / f"{name}.gif", wide=PET_GIF_WIDTH)
        sheet = Path(tmp) / "sheet.png"
        _png(page, _sheet_svg(), sheet)
        target = OUT / "pets.png"
        target.write_bytes(sheet.read_bytes())
        print(f"{target.relative_to(ROOT)}  {target.stat().st_size // 1024} KB")
        browser.close()
    return 0


def main() -> int:
    if "--pets" in sys.argv:
        return pets()
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
        # Only the top of the screen moves, so the GIF carries only that band.
        _gif(shots, OUT / "tui-pet.gif", wide=760, band=BAND)
    return 0


if __name__ == "__main__":
    sys.exit(main())
