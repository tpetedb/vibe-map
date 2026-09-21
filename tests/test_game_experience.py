"""The experience contract, and the four golden pictures that freeze the islands.

Two halves, both about the seam ADR 0015 cuts. The first drives
`EXPERIENCES.islands` through the contract only, never the functions behind
it, so a delegation that stops delegating fails here. The second records what
each island looks like, because every later Galaxy order has to be able to
prove it did not touch them.

How the pictures are made comparable, in order of what would otherwise move:

* No text is in them. The overlays are made invisible and the picture is the
  canvas alone, and the letters of the name plates, which are painted into the
  scene itself, are stubbed out before the page loads: their pills stay, their
  words go. A font is the one thing two machines never agree on, and one that
  measures a hair wider flips a plate to the wide canvas and doubles it.
* The camera is the fitted view (zoom 0), the framing the whole island is in,
  and the shot waits for it to land rather than for a clock.
* Motion is off, so the ambient clock stands at zero: no cloud, no boat, no
  blade and no pulse is anywhere but where it started.
* Math.random is replaced before the page loads, so the flowers, the stars and
  the dunes fall in the same places every time.
* The companion is set to none: its sprite cycles on real seconds, which is
  the one thing in the scene that reduced motion does not stop.
* Three stops are delivered, so the buildings, the annexes and a dusk sky with
  its lamps lit are all in the picture rather than an empty green disc.

What is compared is structure, not pixels. A pixel-exact comparison cannot
survive another machine's rasteriser, and a flaky guard is worse than none
(issue 148), so each picture is reduced to a grid of mean colours and two
numbers are taken: the mean distance over all 160 regions and the worst
single region, both in colour levels out of 255. Every run prints them, so
the numbers below can be measured again on any machine:

    the same tree twice on this Mac        mean 0.00, worst 0.00
    the same tree on Linux, on this
      branch's own CI run                  printed by that run
    one island colour nudged by eleven
      levels in src/game/20-worlds.js      mean 2.84, worst 10.33

The mean is what catches a recoloured island: it sits an order of magnitude
above the two machines and a third of the way to the smallest change worth
catching. The worst region is the second half of the guard, for a change that
moves one corner of the picture a long way (a building gone, a prop moved)
without moving the average anywhere. A missing picture is never a silent
pass: the test writes it and fails, so somebody looks at it before it becomes
the record.
"""

from __future__ import annotations

from pathlib import Path
from statistics import median
from typing import Any

import pytest
from PIL import Image

from tests.conftest import OUT, ROOT, WAIT_MS, GamePage

GOLDEN = ROOT / "tests" / "golden"
ISLANDS = ("campus", "winter", "desert", "prod")
# The contract, in the order docs/GALAXY.md section 4 writes it.
CONTRACT = ("name", "build", "dispose", "tick", "goTo", "where", "listing")

# A window the picture is taken in, chosen so the grid below divides it
# exactly: every region is then the plain mean of 40 by 40 pixels.
VIEW = {"width": 640, "height": 400}
GRID = (16, 10)
# The fitted view: the framing that has the whole island in it, whatever the
# shape of the window (src/game/23-camera.js).
ZOOM = 0
# Delivered on the island in the picture: buildings, annexes, a dusk sky.
DONE = [1, 2, 3]
# Measured, both halves of it (see the module docstring).
MEAN_TOL = 1.0
WORST_TOL = 12.0

# Both go in before anything on the page runs, so the world is built with
# them in force. The random numbers come from a linear congruential generator,
# because what is wanted is the same numbers every time rather than good ones;
# the text stub leaves every plate its pill and takes away its letters, and
# gives the pill a width that follows the words instead of the font.
SEED = """(() => {
  let s = 0x2F6E2B1;
  Math.random = () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
  const g = CanvasRenderingContext2D.prototype;
  g.measureText = function (t) {
    const px = /(\\d+(?:\\.\\d+)?)px/.exec(this.font || "");
    return {width: String(t).length * (px ? +px[1] : 16) * 0.5};
  };
  g.fillText = function () {};
  g.strokeText = function () {};
})()"""
# The picture is the island, so everything the page draws over it goes. Hidden
# rather than removed, because the stage keeps its size either way.
HIDE_OVERLAYS = (
    "#stage > *:not(#c), body > *:not(#stage) { visibility: hidden !important }"
)
# A second view, registered from the test: the smallest thing that answers
# every question core may ask, and nothing more.
STUB_VIEW = """() => { window.__experiences().galaxy = {
  name: "Galaxy", build() {}, dispose() {}, tick() {},
  goTo() { return false }, where() { return null }, listing() { return [] } } }"""


def _golden_state(island: str) -> dict[str, Any]:
    return {
        "name": "Lotte",
        "world": island,
        "pet": "none",
        "doneW": {island: list(DONE)},
        "settings": {"zoom": ZOOM, "motion": "off", "map": "tall", "shadows": "high"},
    }


def _regions(path: Path) -> list[tuple[int, int, int]]:
    """A picture as a grid of mean colours.

    BOX over an exact integer ratio is the mean of each region and nothing
    else, so this is the structure of the picture with its pixels averaged
    away: a shape that moved by a pixel is the same picture, a colour that
    changed is not.
    """
    with Image.open(path) as im:
        small = im.convert("RGB").resize(GRID, Image.Resampling.BOX)
        raw = small.tobytes()
    return [tuple(raw[i : i + 3]) for i in range(0, len(raw), 3)]  # type: ignore[misc]


Picture = list[tuple[int, int, int]]


def _distance(golden: Picture, live: Picture) -> tuple[float, float]:
    """(mean, worst) region distance between two pictures, in colour levels.

    The median difference over every region is taken out first: a machine
    whose rasteriser renders the whole picture a shade darker is still showing
    the same island, and what a changed island does instead is move some
    regions and not others. That is the part that is left and measured. The
    cost is that a change which moves the whole picture by one flat amount is
    invisible here; the colour pipeline itself is watched by
    tests/test_game_graphics.py.
    """
    diff = [[b[c] - a[c] for c in range(3)] for a, b in zip(golden, live, strict=True)]
    shift = [median([d[c] for d in diff]) for c in range(3)]
    per = [sum(abs(d[c] - shift[c]) for c in range(3)) / 3 for d in diff]
    return sum(per) / len(per), max(per)


def _shoot(game: GamePage, island: str) -> Path:
    """The island under the camera the record was taken with."""
    game.page.add_init_script(SEED)
    game.goto(state=_golden_state(island))
    game.page.set_viewport_size(VIEW)
    game.resume()
    # Two facts the page produces: the camera has landed on the frame it was
    # asked for, and the whole island is inside it (rim over one is a crop).
    game.page.wait_for_function(
        "() => window.__gfx().cam.off < 0.05 && window.__gfx().rim < 1",
        timeout=WAIT_MS,
    )
    game.page.add_style_tag(content=HIDE_OVERLAYS)
    game.frames(3)
    OUT.mkdir(parents=True, exist_ok=True)
    shot = OUT / f"experience_{island}.png"
    game.page.locator("#c").screenshot(path=str(shot))
    return shot


# ---- the contract -------------------------------------------------------------


def _island(game: GamePage, **over: Any) -> GamePage:
    state: dict[str, Any] = {"name": "Lotte", "look": "own", "pet": "none"}
    state.update(over)
    game.goto(state=state)
    game.resume()
    return game


def test_the_islands_are_registered_under_the_contract(game: GamePage) -> None:
    """One experience, under its id, with the seven things core may ask for."""
    _island(game)
    shape = game.page.evaluate(
        "() => { const x = window.__experiences();"
        " return {ids: Object.keys(x),"
        " types: Object.keys(x.islands).map(k => k + ':' + typeof x.islands[k])} }"
    )
    assert shape["ids"] == ["islands"], shape
    for name in CONTRACT:
        kind = "string" if name == "name" else "function"
        assert f"{name}:{kind}" in shape["types"], (name, shape["types"])
    game.assert_clean()


def test_the_view_is_a_preference_that_reading_never_writes(game: GamePage) -> None:
    """S.settings.experience decides, the islands are the default, and asking
    about it leaves the record alone. An id this build does not carry falls
    back rather than leaving the player with no view at all."""
    _island(game)
    assert game.page.evaluate("window.__experienceId()") == "islands"
    assert game.page.evaluate("window.__experience().name") == "Islands"
    assert "experience" not in (game.state().get("settings") or {})

    _island(game, settings={"experience": "islands"})
    assert game.page.evaluate("window.__experienceId()") == "islands"
    _island(game, settings={"experience": "orbit"})
    assert game.page.evaluate("window.__experienceId()") == "islands"
    assert (game.state().get("settings") or {})["experience"] == "orbit"
    game.assert_clean()


def test_a_second_view_registers_and_a_url_parameter_wins(game: GamePage) -> None:
    """The registry is open, and the parameter beats the record.

    Galaxy is the second view this seam exists for, and until it is written
    the only way to show that a second one is possible, and that the choice
    between them is read in the right order, is to register one here.
    """
    game.goto(state={"name": "Lotte", "settings": {"experience": "galaxy"}})
    game.page.evaluate(STUB_VIEW)
    assert game.page.evaluate("window.__experienceId()") == "galaxy"
    assert game.page.evaluate("window.__experience().name") == "Galaxy"
    # The record says galaxy; the parameter overrules it and writes nothing.
    game.page.goto(game.url + "?experience=islands")
    game.page.wait_for_function("typeof window.__S === 'function'")
    game.page.evaluate(STUB_VIEW)
    assert game.page.evaluate("window.__experienceId()") == "islands"
    assert game.state()["settings"]["experience"] == "galaxy"
    game.assert_clean()


def test_the_stops_come_back_as_plain_data(game: GamePage) -> None:
    """listing() is what the non-3D twin is built from: no mesh, no canvas."""
    _island(
        game, world="winter", doneW={"campus": [1, 2, 3, 4, 5, 6, 7, 8], "winter": [1]}
    )
    rows = game.page.evaluate("window.__experience().listing()")
    data = game.page.evaluate("window.__data().campaign")
    assert len(rows) == sum(len(data[k]["ws"]) for k in data), len(rows)
    campus = [r for r in rows if r["island"] == "campus"]
    winter = [r for r in rows if r["island"] == "winter"]
    assert [r["state"] for r in campus] == ["done"] * 8
    assert [r["state"] for r in winter][:3] == ["done", "next", "ahead"]
    assert (
        winter[1]["title"]
        == data["winter"]["ws"][1]["h"] + ", " + data["winter"]["ws"][1]["n"]
    )
    assert winter[1]["id"] == "winter:2" and winter[1]["stop"] == 2
    assert all(r["here"] for r in winter) and not any(r["here"] for r in campus)
    game.assert_clean()


def test_going_to_a_stop_brings_the_player_there_and_opens_it(game: GamePage) -> None:
    """goTo walks the walker to the signpost and opens the lesson, and where()
    reports the stop once he is standing at it."""
    _island(game)
    # The walk starts on the inn's terrace, and the cafe standing on it is
    # what the walker is at: where() answers with whatever the proximity
    # check made of this frame, a stop or one of the things beside it.
    game.page.wait_for_function(
        "() => { const w = window.__experience().where();"
        " return !!w && w.kind === 'artifact' && w.id === 'cafe' }",
        timeout=WAIT_MS,
    )
    assert game.page.evaluate("window.__experience().goTo({stop: 1})") is True
    game.page.wait_for_selector("#sheet.on", state="attached")
    plot = game.page.evaluate("window.__data().worlds.campus.plots[0]")
    game.page.wait_for_function(
        "p => Math.hypot(window.__debug().pos[0] - p[0],"
        " window.__debug().pos[2] - p[1]) < 2.5",
        arg=plot,
        timeout=WAIT_MS,
    )
    game.page.wait_for_function(
        "() => { const w = window.__experience().where();"
        " return !!w && w.kind === 'stop' && w.stop === 1 }",
        timeout=WAIT_MS,
    )
    assert game.page.evaluate("window.__experience().where()")["island"] == "campus"
    # A stop that has no signpost on this island is not somewhere to go.
    assert game.page.evaluate("window.__experience().goTo({stop: 99})") is False
    game.assert_clean()


def test_going_to_another_island_is_the_fast_travel(game: GamePage) -> None:
    """The World button's own path, asked for through the contract."""
    _island(game)
    assert game.page.evaluate("window.__experience().goTo({island: 'winter'})") is True
    game.page.wait_for_function(
        "() => window.__debug().world === 'winter'", timeout=WAIT_MS
    )
    game.frames(3)
    assert (
        game.page.evaluate("window.__experience().goTo({island: 'atlantis'})") is False
    )
    assert game.page.evaluate("window.__debug().world") == "winter"
    game.assert_clean()


def test_the_view_is_advanced_through_the_contract(game: GamePage) -> None:
    """tick() moves the island's own frame on: the camera eases towards the
    level the zoom control asked for, by the seconds it is handed."""
    _island(game)
    game.page.wait_for_function("() => window.__gfx().cam.off < 0.05", timeout=WAIT_MS)
    moved = game.page.evaluate(
        "() => { window.zoomStep(-1);"
        " const before = window.__gfx().zoom.level;"
        " window.__experience().tick(0.5, 0);"
        " const after = window.__gfx().zoom.level;"
        " return {before, after, target: window.__gfx().zoom.target} }"
    )
    gap_before = abs(moved["target"] - moved["before"])
    gap_after = abs(moved["target"] - moved["after"])
    assert gap_before > 0.1, moved
    assert gap_after < gap_before / 3, moved
    game.assert_clean()


def test_the_island_is_given_back_and_built_again(game: GamePage) -> None:
    """dispose() hands the scene and its memory back; build() makes it again,
    and the frame loop picks up where it left off."""
    _island(game)
    game.frames(3)
    before = game.page.evaluate("window.__gfx().mem.geometries")
    game.page.evaluate("window.__experience().dispose()")
    assert game.page.evaluate("() => window.__scene() === null") is True
    freed = game.page.evaluate("window.__gfx().mem.geometries")
    assert freed < before / 2, (before, freed)
    game.page.evaluate("window.__experience().build()")
    assert game.page.evaluate("() => window.__scene() !== null") is True
    # The loop draws again, which is the proof that the island is back.
    game.frames(3)
    assert game.page.evaluate("window.__gfx().mem.geometries") > freed
    assert game.page.evaluate("window.__debug().world") == "campus"
    game.assert_clean()


# ---- the golden pictures ------------------------------------------------------


@pytest.mark.parametrize("island", ISLANDS)
def test_an_island_looks_the_way_it_is_recorded(
    game: GamePage, island: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """The picture of this island has not changed."""
    shot = _shoot(game, island)
    golden = GOLDEN / f"{island}.png"
    if not golden.exists():
        GOLDEN.mkdir(parents=True, exist_ok=True)
        golden.write_bytes(shot.read_bytes())
        pytest.fail(f"wrote {golden.relative_to(ROOT)}; look at it, then run again")
    mean, worst = _distance(_regions(golden), _regions(shot))
    with capsys.disabled():
        print(f"\ngolden {island}: mean {mean:.2f}, worst {worst:.2f}")
    assert mean <= MEAN_TOL and worst <= WORST_TOL, (
        f"{island} has moved: mean {mean:.2f} (max {MEAN_TOL}),"
        f" worst region {worst:.2f} (max {WORST_TOL})."
        f" Compare {shot.relative_to(ROOT)} with {golden.relative_to(ROOT)}"
    )
    game.assert_clean()
