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
* Every frame is the same length. Reduced motion does not stop what the player
  causes, and the mentor who follows the walker takes steps as long as the
  last frame took: on the machine's own clock he comes to rest a pixel or two
  from where the record has him, and his dusk shadow lies across four more
  regions. Measured that way he was the whole of the noise, in four unchanged
  pictures of twenty-eight on this Mac and in all eight on the runner. So the
  page's clock moves by one capped frame per drawn frame, and the shot waits
  until nothing in the scene differs from the frame before.
* Math.random is replaced before the page loads, so the flowers, the stars and
  the dunes fall in the same places every time.
* The companion is set to none: its sprite cycles on real seconds.
* Three stops are delivered, so the buildings, the annexes and a dusk sky with
  its lamps lit are all in the picture rather than an empty green disc.

What is compared is structure, not pixels. A pixel-exact comparison cannot
survive another machine's rasteriser, and a flaky guard is worse than none
(issue 148), so each picture is reduced to a grid of mean colours, kept as
fractions, and two numbers are taken: the mean distance over all 160 regions
and the worst single region, both in colour levels out of 255. Every run
prints them, so everything below can be measured again on any machine.

The noise, which is what the tolerances follow:

    an unchanged tree on this Mac, 56 pictures,
      three at a time to load the machine     no pixel differs from the record
    the record, made on a Mac, against Linux
      on the runner (CI runs 35619326089 and
      35622986955: the same software
      renderer, the other architecture, the
      machine's own clock)
        outside the follower's ten regions    mean 0.0002, worst 0.010, the
                                              same numbers in both runs
        his ten regions, with his wander      mean 0.004, worst 0.553

So the rasterisers differ by a hundredth of a level, and by the same hundredth
every time, and the tolerances are ten times that: the worst region at 0.1,
the mean at 0.002. What the runner makes of the follower's own regions under
the frame clock is not in that table; every run prints it, and the arithmetic
of his walk is the same on both machines, so it should be the same hundredth.

What that sees, each one edit of the built game, measured on the campus as
mean and worst. The first and the fourth are tests below, so the guard cannot
go blind to them again without failing:

    grass, eleven levels on one channel       0.819, 2.949  (and 0.027, 2.375
                                              from the desert, 0.069, 2.764
                                              from prod, where the campus is a
                                              silhouette on the horizon)
    grass, one level on one channel           0.075, 0.289
    the paths, eleven levels on one channel   0.025, 0.438
    the well taken away                       0.028, 1.008
    the windmill taken away                   0.238, 10.238
    the well moved by one unit                0.007, 0.438
    the well moved by a fifth of a unit       0.002, 0.119  (seen, only just)
    exposure 1.06 to 1.08                     0.950, 1.363

What it cannot see:

* Anything smaller than the tolerance. The stone of the well alone, moved by
  thirty levels on one channel, comes out at 0.001 and 0.091 and passes; so
  does its roof made a ninth narrower, at 0.001 and 0.064. A region is 40 by
  40 pixels, so a change passes when it moves a region's summed colour by less
  than about 480 levels, and that is a recolour of one small prop or a few
  pixels of its shape. One level on the campus paths is the edge: 0.00205 on
  the mean, and seen by that alone.
* Anything that is not in the picture. The words on the plates and every font
  (stubbed out above, on purpose); the overlays and the HUD (hidden); whatever
  the ambient clock moves, which is seen only where it starts; the companion;
  dust and confetti; every zoom level but the fitted one and every window but
  this one; the day and the night sky, and the buildings of the five stops
  that are not delivered here.
* A new renderer. Another Chromium or another three.js draws another picture,
  and then the record is made again: delete the four files, run the test,
  look at what it wrote.

A missing picture is never a silent pass: the test writes it and fails, so
somebody looks at it before it becomes the record.
"""

from __future__ import annotations

from array import array
from pathlib import Path
from typing import Any

import pytest
from PIL import Image
from playwright.sync_api import Route

from tests.conftest import GAME_PATH, ROOT, WAIT_MS, GamePage

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
# Ten times what two machines differ by on an unchanged island (the module
# docstring has the measurements, and what passes underneath these).
MEAN_TOL = 0.002
WORST_TOL = 0.1
# What the guard has to go on seeing: the smallest honest example of a changed
# colour and of a missing prop, each as one edit of the built game on its way
# to the browser. The first is a colour of src/game/20-worlds.js moved by
# eleven levels on one channel; the second takes the well off the campus.
CHANGES = {
    "grass": ('grass:"#79CC72"', 'grass:"#79CC7D"'),
    "well": ('"stall","well","birds"', '"stall","birds"'),
}

# All three go in before anything on the page runs, so the world is built with
# them in force. The random numbers come from a linear congruential generator,
# because what is wanted is the same numbers every time rather than good ones;
# the text stub leaves every plate its pill and takes away its letters, and
# gives the pill a width that follows the words instead of the font. The frame
# clock makes every frame as long as the longest one the loop accepts (it caps
# a frame at a twentieth of a second), so a runner that draws two frames a
# second needs no more of them than a laptop does, and both walk the follower
# along the same steps to the same place.
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
  let now = 0, stamp = -1;
  const raf = window.requestAnimationFrame.bind(window);
  window.requestAnimationFrame = cb => raf(ts => {
    if (ts !== stamp) { stamp = ts; now += 50; }
    cb(ts);
  });
  performance.now = () => now;
})()"""
# The scene has come to rest: two drawn frames in a row in which no object of
# it and nothing about the camera differs from the frame before. A frame that
# was not drawn is not evidence, so the question is only asked of a new one.
AT_REST = """() => {
  const f = window.__debug().frame;
  const k = window.__rest || (window.__rest = {frame: -1, sig: "", same: 0});
  if (f === k.frame) return false;
  const g = window.__gfx();
  const sig = [g.cam.dist, g.cam.off, g.rim, g.zoom.level, g.zoom.dist];
  window.__scene().traverse(o => { sig.push.apply(sig, o.matrixWorld.elements); });
  const now = sig.join();
  k.same = now === k.sig ? k.same + 1 : 0;
  k.frame = f;
  k.sig = now;
  return k.same >= 2;
}"""
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


Picture = list[tuple[float, float, float]]


def _regions(path: Path) -> Picture:
    """A picture as a grid of mean colours, kept as the fractions they are.

    BOX over an exact integer ratio is the mean of each region and nothing
    else, so this is the structure of the picture with its pixels averaged
    away: a shape that moved by a pixel is the same picture, a colour that
    changed is not. The mean is taken per channel in floating point, because
    a mean rounded to a whole level turns a difference of a hundredth into
    nothing or into a third of a level, whichever side of a half it fell on.
    """
    with Image.open(path) as im:
        bands = [
            array("f", band.convert("F").resize(GRID, Image.Resampling.BOX).tobytes())
            for band in im.convert("RGB").split()
        ]
    return list(zip(*bands, strict=True))


def _distance(golden: Picture, live: Picture) -> tuple[float, float]:
    """(mean, worst) region distance between two pictures, in colour levels.

    Nothing is taken out first. The two machines this was measured on agree on
    the level of the whole picture exactly, so a picture that is one flat
    amount brighter is a changed picture and is counted as one.
    """
    per = [
        sum(abs(b[c] - a[c]) for c in range(3)) / 3
        for a, b in zip(golden, live, strict=True)
    ]
    return sum(per) / len(per), max(per)


def _moved(island: str, shot: Path) -> str:
    """Why this picture is not the recorded one, or nothing when it is."""
    mean, worst = _distance(_regions(GOLDEN / f"{island}.png"), _regions(shot))
    print(f"\n{shot.stem} against golden {island}: mean {mean:.4f}, worst {worst:.3f}")
    if mean <= MEAN_TOL and worst <= WORST_TOL:
        return ""
    return (
        f"{island} has moved: mean {mean:.4f} (max {MEAN_TOL}),"
        f" worst region {worst:.3f} (max {WORST_TOL})."
        f" Compare {shot.relative_to(ROOT)} with tests/golden/{island}.png"
    )


def _shoot(game: GamePage, island: str, name: str | None = None) -> Path:
    """The island under the camera the record was taken with."""
    game.page.add_init_script(SEED)
    game.goto(state=_golden_state(island))
    game.page.set_viewport_size(VIEW)
    game.resume()
    # Three facts the page produces: the camera has landed on the frame it was
    # asked for, the whole island is inside it (rim over one is a crop), and
    # nothing in the scene is still on its way somewhere.
    game.until(
        "window.__gfx().cam.off < 0.05 && window.__gfx().rim < 1",
        what=f"the fitted view of {island} to land",
    )
    with game.named_wait(f"{island} to come to rest"):
        game.page.wait_for_function(AT_REST, timeout=WAIT_MS)
    # The clock the loop read is the frame clock: whole frames, nothing else.
    assert game.page.evaluate("performance.now() % 50") == 0
    game.page.add_style_tag(content=HIDE_OVERLAYS)
    game.frames(3)
    # The canvas is the whole window, so the window is the clip.
    return game.screenshot(
        name or f"experience_{island}", clip={"x": 0, "y": 0, **VIEW}
    )


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
    # A key every object has is not a view either, whoever put it there.
    _island(game, settings={"experience": "constructor"})
    assert game.page.evaluate("window.__experienceId()") == "islands"
    assert game.page.evaluate("window.__experience().name") == "Islands"
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


def test_going_to_a_stop_on_another_island_finishes_the_trip(
    game: GamePage,
) -> None:
    """A compound destination survives the flight and starts its walk."""
    _island(game, doneW={"winter": [1]})
    assert (
        game.page.evaluate("window.__experience().goTo({island: 'winter', stop: 2})")
        is True
    )
    game.page.wait_for_function(
        "() => window.__debug().world === 'winter' && !window.__debug().flying",
        timeout=WAIT_MS,
    )
    game.page.wait_for_selector("#sheet.on", state="attached")
    plot = game.page.evaluate("window.__data().worlds.winter.plots[1]")
    game.page.wait_for_function(
        "p => Math.hypot(window.__debug().pos[0] - p[0],"
        " window.__debug().pos[2] - p[1]) < 2.5",
        arg=plot,
        timeout=WAIT_MS,
    )
    game.page.wait_for_function(
        "() => { const w = window.__experience().where();"
        " return !!w && w.kind === 'stop' && w.stop === 2 }",
        timeout=WAIT_MS,
    )
    where = game.page.evaluate("window.__experience().where()")
    assert where == {"kind": "stop", "stop": 2, "island": "winter"}
    game.assert_clean()


def test_a_new_destination_replaces_a_compound_trip(game: GamePage) -> None:
    """A destination accepted during flight is the destination that lands."""
    _island(game)
    assert game.page.evaluate("window.__experience().goTo({island: 'winter', stop: 2})")
    assert game.page.evaluate("window.__experience().goTo({island: 'desert'})")
    game.page.wait_for_function(
        "() => window.__debug().world === 'desert' && !window.__debug().flying",
        timeout=WAIT_MS,
    )
    assert game.page.evaluate("window.__experience().where()") is None
    game.assert_clean()


def test_the_campus_finale_is_not_a_ninth_plot(game: GamePage) -> None:
    """The inn finale is a place, but it is not a listed or navigable stop."""
    _island(game, doneW={"campus": list(range(1, 9))})
    game.page.wait_for_function(
        "() => { const w = window.__experience().where();"
        " return !!w && w.kind === 'finale' }",
        timeout=WAIT_MS,
    )
    where = game.page.evaluate("window.__experience().where()")
    assert where == {"kind": "finale", "island": "campus"}
    rows = game.page.evaluate("window.__experience().listing()")
    assert [r["stop"] for r in rows if r["island"] == "campus"] == list(range(1, 9))
    assert game.page.evaluate("window.__experience().goTo({stop: 9})") is False
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


def test_dispose_cancels_flight_walk_and_proximity(game: GamePage) -> None:
    """A disposed experience cannot finish or accept abandoned navigation."""
    _island(game)
    assert game.page.evaluate("window.__experience().goTo({island: 'winter', stop: 2})")
    game.page.evaluate("window.__experience().dispose()")
    assert game.page.evaluate("window.__experience().where()") is None
    assert game.page.evaluate("window.__experience().goTo({stop: 1})") is False
    game.page.evaluate(
        "() => new Promise(resolve => requestAnimationFrame("
        "() => requestAnimationFrame(resolve)))"
    )
    assert game.page.evaluate("window.__debug().flying") is False
    assert game.page.evaluate("() => window.__scene() === null") is True
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
    with capsys.disabled():
        moved = _moved(island, shot)
    assert not moved, moved
    game.assert_clean()


@pytest.mark.parametrize("change", sorted(CHANGES))
def test_a_changed_campus_does_not_pass_for_the_recorded_one(
    game: GamePage, change: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """A guard is worth what goes past it, so two small changes are tried on
    it: one colour of the island on one channel, and one prop taken away."""
    old, new = CHANGES[change]
    found: list[int] = []

    def edited(route: Route) -> None:
        response = route.fetch()
        html = response.text()
        found.append(html.count(old))
        route.fulfill(response=response, body=html.replace(old, new))

    game.page.route(f"**{GAME_PATH}", edited)
    shot = _shoot(game, "campus", name=f"experience_campus_changed_{change}")
    # An edit that found nothing to change would prove nothing.
    assert found and set(found) == {1}, (old, found)
    with capsys.disabled():
        moved = _moved("campus", shot)
    assert moved, f"the campus with its {change} changed passed for the record"
    game.assert_clean()


# ---- the comparison itself ----------------------------------------------------


def _flat(path: Path, level: int, patch: tuple[int, int] | None = None) -> Path:
    """A window of one grey, and optionally one region of it a level up in
    this many of its 1600 pixels."""
    im = Image.new("RGB", (VIEW["width"], VIEW["height"]), (level, level, level))
    if patch is not None:
        region, pixels = patch
        side = VIEW["width"] // GRID[0]
        x0, y0 = (region % GRID[0]) * side, (region // GRID[0]) * side
        for i in range(pixels):
            im.putpixel((x0 + i % side, y0 + i // side), (level + 1,) * 3)
    im.save(path)
    return path


def test_the_same_picture_is_at_no_distance(tmp_path: Path) -> None:
    same = _regions(_flat(tmp_path / "a.png", 100))
    assert _distance(same, same) == (0.0, 0.0)


def test_a_picture_that_is_one_flat_amount_brighter_has_moved(tmp_path: Path) -> None:
    """Nothing is taken out before the comparison: exposure up by two hundredths
    moves every region by about a level, and that is a changed island."""
    mean, worst = _distance(
        _regions(_flat(tmp_path / "a.png", 100)),
        _regions(_flat(tmp_path / "b.png", 101)),
    )
    assert mean == pytest.approx(1.0) and worst == pytest.approx(1.0)
    assert mean > MEAN_TOL and worst > WORST_TOL


def test_a_region_that_moves_by_less_than_a_level_is_measured(tmp_path: Path) -> None:
    """The tolerances are fractions of a level, so the means have to be: 640
    of one region's 1600 pixels a level up is 0.4 there, which a mean rounded
    to a whole level calls nothing."""
    mean, worst = _distance(
        _regions(_flat(tmp_path / "a.png", 100)),
        _regions(_flat(tmp_path / "b.png", 100, patch=(37, 640))),
    )
    assert worst == pytest.approx(0.4, abs=1e-4)
    assert mean == pytest.approx(0.4 / (GRID[0] * GRID[1]), abs=1e-6)
    assert worst > WORST_TOL
