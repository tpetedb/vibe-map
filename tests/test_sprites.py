"""The vendored pixel sprites: they decode, they paint, they step aside."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from rich.console import Console
from rich.text import Text

from vibemap import pet, sprites

ROOT = Path(__file__).resolve().parents[1]
# A red pixel over a blue one, with a transparent column and a bare bottom.
SWATCH: sprites.Frame = [
    ["#ff0000", None, "#ff0000", None],
    ["#0000ff", None, None, "#0000ff"],
    [None, "#00ff00", None, None],
    [None, None, None, None],
]


def test_every_vendored_set_decodes_and_is_credited() -> None:
    assert sprites.available() == ("crab", "duck", "snail", "turtle")
    credits = (sprites.PETS / "CREDITS.md").read_text()
    for name in sprites.available():
        sheet = sprites.sheet(name)
        assert sheet.licence == "MIT"
        assert sheet.author in credits
        assert (sprites.PETS / name / "LICENSE").read_text().startswith("MIT License")
        for state in sprites.STATES:
            frames = sheet.frames(state)
            assert frames, (name, state)
            for frame in frames:
                assert len(frame) == sheet.height
                assert all(len(row) == sheet.width for row in frame)
                assert all(c is None or c.startswith("#") for row in frame for c in row)


def test_an_unknown_format_version_is_refused(tmp_path, monkeypatch) -> None:
    data = json.loads((sprites.PETS / "crab" / "frames.json").read_text())
    data["version"] = 99
    (tmp_path / "crab").mkdir()
    (tmp_path / "crab" / "frames.json").write_text(json.dumps(data))
    monkeypatch.setattr(sprites, "PETS", tmp_path)
    sprites.sheet.cache_clear()
    with pytest.raises(ValueError, match="format version 99"):
        sprites.sheet("crab")
    sprites.sheet.cache_clear()


def test_half_blocks_pair_two_pixel_rows_into_one_cell() -> None:
    text = sprites.half_blocks(SWATCH)
    assert text.plain == "\u2580 \u2580\u2584\n \u2580  \n"
    spans = {(s.start, s.end): s.style for s in text.spans}
    assert spans[(0, 1)].color.name == "#ff0000"
    assert spans[(0, 1)].bgcolor.name == "#0000ff"
    # A bare bottom pixel is a lower half block with no background behind it.
    assert spans[(3, 4)].color.name == "#0000ff"
    assert spans[(3, 4)].bgcolor is None
    assert sprites.half_blocks(SWATCH, offset=3).plain.startswith("   \u2580")


def test_the_renderer_falls_back_when_the_terminal_cannot_show_it() -> None:
    truecolor = {"TERM": "xterm-256color", "COLORTERM": "truecolor"}
    assert sprites.truecolor(truecolor) is True
    assert sprites.truecolor({"TERM": "xterm-direct"}) is True
    assert sprites.truecolor({"TERM": "dumb", "COLORTERM": "truecolor"}) is False
    assert sprites.truecolor({"TERM": "xterm-256color"}) is False
    assert sprites.truecolor({**truecolor, "NO_COLOR": "1"}) is False
    assert sprites.style_for("auto", "crab", env=truecolor) == "pixel"
    assert sprites.style_for("auto", "crab", env={"TERM": "dumb"}) == "ascii"
    # No sprites for an owl, and an explicit ascii always wins.
    assert sprites.style_for("auto", "owl", env=truecolor) == "ascii"
    assert sprites.style_for("pixel", "owl", env=truecolor) == "ascii"
    assert sprites.style_for("ascii", "crab", env=truecolor) == "ascii"
    # A forced pixel is a choice, even on a terminal that plays it down.
    assert sprites.style_for("pixel", "crab", env={"TERM": "dumb"}) == "pixel"


def test_the_pet_paints_pixels_or_art_depending_on_the_style() -> None:
    p = pet.resolve("tom", species="crab", hat="crown")
    pixels = pet.render(p, 0, stats=False, style="pixel")
    art = pet.render(p, 0, stats=False, style="ascii")
    assert "\u2580" in pixels.plain and "\u2580" not in art.plain
    assert "\\^^^/" in art.plain
    # No hat sprite yet, so the hat is a line of text next to the pixels.
    assert "wearing a crown" in pixels.plain
    assert "wearing a crown" not in art.plain
    assert pet.columns(p, "pixel") == sprites.sheet("crab").width
    assert pet.columns(p, "ascii") == pet.WIDTH
    assert "Marc Duiker" in pet.credit(p, "pixel")
    assert pet.credit(p, "ascii") == ""
    assert pet.credit(pet.resolve("tom", species="owl"), "pixel") == ""


def test_the_gait_walks_only_while_the_stroll_moves() -> None:
    assert pet.gait(4, 40, sprite_width=20) == "walk"
    assert pet.gait(5, 20, sprite_width=20) == "idle"  # nowhere to go, so it idles


def test_a_pixel_pet_fits_the_panel_it_is_drawn_in() -> None:
    console = Console(width=40, no_color=False, force_terminal=True)
    p = pet.resolve("Lotte", species="snail")
    with console.capture() as cap:
        console.print(pet.render(p, 0, stats=False, style="pixel"))
    lines = cap.get().splitlines()
    assert len(lines) <= 12
    assert max(Text.from_ansi(line).cell_len for line in lines) <= 40


def test_sync_pets_check_passes_on_the_vendored_data() -> None:
    out = subprocess.run(
        [sys.executable, "tools/sync_pets.py", "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert out.returncode == 0, out.stdout + out.stderr
