"""Hunt batch F: the artifacts in the world and on their sheet.

One test per finding of `work/orders/hunt-f-artifacts/findings.md`, and one
per point the review of that work raised. Each one drives the control a player
uses and waits for a fact the page produced: the scene the world builder made,
the text the terminal holds, the nodes it added, the style the browser
computed. Nothing here waits on a clock.

Two of them guard rather than repair. F2 does not reproduce on the font stack
the game ships, so its test holds the style that keeps it from coming back,
and says so. The places where a ring is not the whole answer are listed here,
so a test holds that list to what the islands actually have.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest
from playwright.sync_api import Browser

from tests.conftest import (
    WAIT_MS,
    GamePage,
    game_page,
    phone_options,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "game" / "16-artifacts.js"
VAULT = ROOT / "src" / "game" / "60-vault.js"
CAMPAIGN = json.loads((ROOT / "vibemap" / "data" / "campaign.json").read_text("utf-8"))

# The on-demand price of one t3.small hour, by region, from the same vendor
# table the demo's "Do it for real" step sends the learner to look at:
# https://aws-pricing.com/t3.small.html (read 2026-09-21). The demo may name
# any region in this table; it may not name one and charge another's rate.
T3_SMALL_USD_PER_HOUR = {"us-east-1": 0.0208, "eu-west-1": 0.0228}

# What the walk-up test in `src/game/31-animate.js` offers before a ring: a
# mentor within 2.4, the finale within 6.6 of the island's centre once every
# stop is delivered, an open signpost within 2.6. Then the nearer ring.
STOP_RADIUS = 2.6
MENTOR_RADIUS = 2.4
INN_RADIUS = 6.6

# What lies under each ring where a player can stand on it, from rays straight
# down. Level: the highest level top below the knee; one above it, or under a
# metre across (a bottle, a crate), stands in front of the ring. Slope: the
# highest face tilted up that reaches down to the ring's height, however high
# it rises over it, so a ring deep under a hillside counts as much as a shallow
# one and a roof above the ring does not. A point inside an obstacle is behind
# the prop at any height.
UNDER_RINGS = """() => {
  const T = window.THREE, obs = window.__obstacles();
  const ray = new T.Raycaster(), down = new T.Vector3(0, -1, 0);
  const up = new T.Vector3(), v = new T.Vector3();
  const nm = new T.Matrix3(), bb = new T.Box3();
  const m = new T.Matrix4(), inst = new T.Matrix4();
  const ground = [];
  window.__scene().traverse(o => {
    if (!o.isMesh || (o.geometry && o.geometry.type === 'TorusGeometry')) return;
    bb.setFromObject(o);
    if (bb.max.x - bb.min.x >= 1 && bb.max.z - bb.min.z >= 1) ground.push(o);
  });
  return window.__rings().map(r => {
    let level = 0, slope = 0;
    for (let i = 0; i < 96; i++) {
      const th = i / 96 * Math.PI * 2;
      const x = r.x + Math.cos(th) * r.r, z = r.z + Math.sin(th) * r.r;
      if (obs.some(o => Math.hypot(o[0] - x, o[1] - z) < o[2])) continue;
      ray.set(new T.Vector3(x, 6, z), down);
      for (const h of ray.intersectObjects(ground, false)) {
        if (!h.face) continue;
        // An instanced prop (a tree, a bush) is placed by its own matrix too.
        m.copy(h.object.matrixWorld);
        if (h.instanceId !== undefined) {
          h.object.getMatrixAt(h.instanceId, inst);
          m.multiply(inst);
        }
        up.copy(h.face.normal).applyMatrix3(nm.getNormalMatrix(m)).normalize();
        if (up.y > .95) {
          if (h.point.y <= .6) level = Math.max(level, h.point.y);
        } else if (up.y > .3) {
          const at = h.object.geometry.attributes.position;
          const foot = Math.min(...[h.face.a, h.face.b, h.face.c].map(k =>
            v.fromBufferAttribute(at, k).applyMatrix4(m).y));
          if (foot <= r.y) slope = Math.max(slope, h.point.y);
        }
      }
    }
    return {...r, level, slope};
  });
}"""


def _demo_text(artifact: str | None = None) -> str:
    """The demo transcripts as they are written, all of them or one artifact's.

    Read from the source rather than from the page: these are findings about
    what the copy says, and the build check already proves the built game
    carries the same source.
    """
    text = SOURCE.read_text(encoding="utf-8")
    if artifact is None:
        return text
    start = re.search(rf'^  "?{re.escape(artifact)}"?:\[$', text, re.M)
    assert start, f"no demo block for {artifact}"
    rest = text[start.end() :]
    end = re.search(r'^  "?[\w-]+"?:\[$', rest, re.M)
    return rest[: end.start()] if end else rest


def _demo_lines(artifact: str) -> list[list[str]]:
    """One artifact's transcripts, line by line, from the arrays themselves.

    The source writes each one as a JSON array of strings, so it is read as
    one instead of by a regular expression over escaped quotes.
    """
    blocks = [json.loads(m) for m in re.findall(r"o:(\[.*?\])\}", _demo_text(artifact))]
    assert blocks, f"no transcripts for {artifact}"
    return blocks


def _open_artifact(game: GamePage, aid: str) -> None:
    """Open one artifact's sheet with the Roadmap's own Open button.

    A click waits for its button to hold still, which is the Roadmap's spring
    ending, so only the artifact screen's own arrival is waited for.
    """
    names = game.page.evaluate(
        "Object.fromEntries(window.__artifacts().map(a => [a.id, a.name]))"
    )
    game.hud_action("#hud button:has-text('Roadmap')")
    game.page.click(f"#s-map button[aria-label='Open {names[aid]}']")
    game.page.wait_for_selector("#s-artifact.on", state="attached")
    game.sheet_in_place()


def _wait_line(game: GamePage, line: str) -> None:
    """Wait for one line of a transcript to be in the terminal."""
    game.page.wait_for_function(
        "t => (document.getElementById('art-term').textContent || '').includes(t)",
        arg=line,
        timeout=WAIT_MS,
    )


def _rings(game: GamePage) -> list[dict[str, Any]]:
    """Every artifact ring on this island, with the zone it is meant to be."""
    return game.page.evaluate("window.__rings()")


@pytest.fixture(scope="module")
def course_rings(chromium: Browser, server: str) -> list[dict[str, Any]]:
    """Every ring in the course, measured once on islands with every stop delivered.

    A delivered stop lays its slab, so a finished island is where the ground
    under a ring is highest. The islands are walked with the HUD's World button,
    once for the three tests that read the result.
    """
    stops = {
        w: list(range(1, len(e["ws"]) + 1)) for w, e in CAMPAIGN["evenings"].items()
    }
    seen: dict[str, dict[str, Any]] = {}
    with game_page(chromium, server, viewport={"width": 420, "height": 860}) as game:
        game.goto(state={"name": "Lotte", "done": stops["campus"], "doneW": stops})
        game.resume()
        for _ in stops:
            for ring in game.page.evaluate(UNDER_RINGS):
                seen[ring["id"]] = ring
            game.next_world()
        game.assert_clean()
    assert set(seen) == {a["id"] for a in CAMPAIGN["artifacts"]}
    return list(seen.values())


def _walk_onto_the_fountain_ring(game: GamePage) -> None:
    """Walk at the fountain until it is the fountain that Inspect offers.

    The lake pushes the walker out at its bank, so a walk at the middle ends
    where a player would stand: on the ring, in the band between the bank and
    the edge of the zone. The arrow keys are held towards the middle and the
    page answers on the frame the prompt becomes the fountain's; the keys are
    aimed again every eight frames until it does.
    """
    fountain = game.page.evaluate(
        "window.__artifacts().find(a => a.id === 'fountain').pos"
    )
    kb, held = game.page.keyboard, set[str]()
    try:
        for _ in range(60):
            pos = game.page.evaluate("window.__debug().pos")
            dx, dz = fountain[0] - pos[0], fountain[1] - pos[2]
            want = {
                *(["ArrowRight"] if dx > 0.5 else ["ArrowLeft"] if dx < -0.5 else []),
                *(["ArrowDown"] if dz > 0.5 else ["ArrowUp"] if dz < -0.5 else []),
            }
            for k in want - held:
                kb.down(k)
            for k in held - want:
                kb.up(k)
            held = want
            arrived = game.page.wait_for_function(
                """f => { const d = window.__debug();
                          return d.near === 'a:fountain' || d.frame >= f; }""",
                arg=game.frame_count() + 8,
                timeout=WAIT_MS,
            )
            if arrived and game.near() == "a:fountain":
                return
    finally:
        for k in held:
            kb.up(k)
    stopped = game.page.evaluate("window.__debug().pos")
    raise AssertionError(f"never reached the fountain's ring, stopped at {stopped}")


# F1 ------------------------------------------------------------------------
def test_a_second_demo_press_cancels_the_lines_the_first_still_owes(
    game: GamePage,
) -> None:
    game.goto()
    game.start()
    _open_artifact(game, "cafe")
    demos = game.page.evaluate("window.__demos().cafe.map(d => d.o)")
    # The second press lands while the first demo is still printing, which is
    # the whole finding: two transcripts in one terminal. By the time the
    # second demo has printed its last line, every line the first one owed
    # before that moment has either been cancelled or is on the screen.
    game.page.click("#s-artifact button[data-demo='0']")
    game.page.click("#s-artifact button[data-demo='1']")
    _wait_line(game, demos[1][-1])
    assert game.page.text_content("#art-term") == "\n".join(demos[1])
    game.assert_clean()


# F2 ------------------------------------------------------------------------
def test_the_walkthrough_and_the_terminal_are_drawn_with_ligatures_off(
    game: GamePage,
) -> None:
    """A guard, not a repair: F2 does not reproduce on the stack we ship.

    The finding said Inter drew "GET /coffee -> 200" with an arrow glyph, but
    Inter and JetBrains Mono left `src/style.css` in f00a348 and the type is
    now system-ui and ui-monospace. Rendered at 40 px in Chromium and WebKit,
    `font-variant-ligatures: normal` and `none` give the same pixels and the
    same text width in both stacks, so nothing is joined today. What this
    holds is the rule itself: a fork that sets a typeface which joins "->" or
    "--" must not silently break a line the learner has to copy and a check
    reads back.
    """
    game.goto()
    game.start()
    targets = game.page.evaluate(
        """() => window.__data().artifacts
             .filter(a => a.real.steps.some(s => s.includes('->')))
             .map(a => ({id: a.id, step: a.real.steps.find(s => s.includes('->'))}))"""
    )
    # The rule's premise: there are steps whose text has to be reproduced
    # character for character, and the check reads the line back.
    assert targets, "no artifact step asks for an arrow to be printed"
    for target in targets:
        _open_artifact(game, target["id"])
        step = game.page.locator("#s-artifact .lesson ol li").filter(
            has_text=target["step"]
        )
        assert step.count() == 1, target["id"]
        assert "->" in (step.text_content() or ""), target["id"]
        # The commands under it are typed as they stand, and the terminal
        # prints command lines of its own, so both are held to the same rule.
        for part in (
            step,
            game.page.locator("#s-artifact .lesson pre code"),
            game.page.locator("#art-term"),
        ):
            assert (
                part.first.evaluate("el => getComputedStyle(el).fontVariantLigatures")
                == "none"
            ), target["id"]
    game.assert_clean()


# F3 ------------------------------------------------------------------------
def test_under_reduced_motion_a_demo_prints_at_once_and_is_announced(
    game: GamePage,
) -> None:
    game.page.emulate_media(reduced_motion="reduce")
    game.goto()
    game.start()
    _open_artifact(game, "cafe")
    lines = game.page.evaluate("window.__demos().cafe[0].o")
    assert game.page.get_attribute("#art-term", "aria-live") == "polite"
    # The press and the read are one task, so a transcript that is whole here
    # was printed without a timer: that is what reduced motion asks for, and
    # it is what a screen reader gets to read out of the live region.
    printed = game.page.evaluate(
        """() => {
             const el = document.getElementById('art-term');
             document.querySelector("#s-artifact button[data-demo='0']").click();
             return el.textContent;
           }"""
    )
    assert printed == "\n".join(lines)
    game.assert_clean()


def test_while_it_types_the_terminal_hands_a_reader_one_line_at_a_time(
    game: GamePage,
) -> None:
    """The live region announces what was added, so what is added is a line.

    Appending to textContent replaces the single text node that holds the
    whole transcript, and a reader that speaks additions then hears every
    line printed so far again on each new one.
    """
    game.goto()
    game.start()
    _open_artifact(game, "cafe")
    lines = game.page.evaluate("window.__demos().cafe[0].o")
    game.page.evaluate(
        """() => {
             window.__added = [];
             const el = document.getElementById('art-term');
             new MutationObserver(rs => rs.forEach(r => r.addedNodes.forEach(
               n => window.__added.push(n.textContent)))).observe(
                 el, {childList: true});
           }"""
    )
    game.page.click("#s-artifact button[data-demo='0']")
    _wait_line(game, lines[-1])
    added = game.page.evaluate("window.__added")
    assert [text.lstrip("\n") for text in added] == lines
    assert game.page.text_content("#art-term") == "\n".join(lines)
    game.assert_clean()


# F4 ------------------------------------------------------------------------
def test_the_fountain_ring_is_drawn_where_a_player_can_see_it(
    game: GamePage,
) -> None:
    game.goto()
    game.start()
    ring = next(r for r in _rings(game) if r["id"] == "fountain")
    # The lake disc and the fountain share a centre, and the walker is pushed
    # out at the lake's bank: a ring drawn inside that radius is under the
    # water, where nobody can stand and nothing can be seen.
    assert ring["block"] > 0, "the lake stopped pushing the walker out"
    assert ring["r"] > ring["block"]
    game.assert_clean()


# F5 ------------------------------------------------------------------------
def test_every_artifact_ring_on_every_island_is_the_zone_that_offers_inspect(
    course_rings: list[dict[str, Any]],
) -> None:
    # Every artifact in the course, not only the thirteen on the campus.
    assert len(course_rings) >= 20
    # "Walk up to the yellow ring and press Inspect" is the copy, so the ring
    # the player sees is the radius nearArtifact tests against, not a smaller
    # decoration inside it.
    assert [r["id"] for r in course_rings if abs(r["r"] - r["zone"]) > 1e-6] == []
    # And none of them is buried in the thing it belongs to, the way the
    # mountain's was inside the mountain.
    assert [r["id"] for r in course_rings if r["r"] <= r["block"]] == []


def test_the_ring_is_drawn_on_top_of_the_ground_it_crosses(
    course_rings: list[dict[str, Any]],
) -> None:
    """What RING_Y is for, on every island and with every stop delivered.

    The level ground under a ring is the path slabs, the river, the lake disc,
    the dock's planks and a delivered stop's slab. A ring whose tube dips into
    one of them is cut in half exactly where the copy sends the player to look.
    """
    rings = course_rings
    assert [r["id"] for r in rings if r["y"] - r["tube"] <= r["level"]] == []
    # Not a test that cannot fail: these rings do cross flat things, and the
    # finished slabs are the highest of them.
    assert max(r["level"] for r in rings) >= 0.2
    # And the ring lies on the ground rather than floating above it.
    assert [r["id"] for r in rings if r["y"] - r["level"] > 0.3] == []


# The one ring a slope still covers, and how high the slope may stand over it.
# The mountain is a seven-sided cone of base radius 6 in the world, so a flat
# ring clears its corners only from a zone of 6 / 1.6 = 3.75, and campus
# signpost 4 stands 3.61 from its centre, which test_game_smoke.py keeps outside
# every zone. At 3.5 the ring dips under the seven corners by at most
# 7 * (1 - 5.6 / 6) = 0.47. The cure is the cone's footprint or where the
# mountain stands, in src/game/21-world-build.js and 20-worlds.js; until then
# this bound keeps the dip from growing, and the entry goes when it is cured.
UNDER_A_SLOPE = {"mountain": 0.5}


def test_no_ring_runs_under_a_slope(course_rings: list[dict[str, Any]]) -> None:
    """A flat ring cannot follow a slope, so it has to stay off one.

    However deep the ring runs under the slope: a smaller zone round the
    mountain buries the ring further, and that is the worse defect, not a
    smaller one.
    """
    under = {
        r["id"]: round(r["slope"], 2) for r in course_rings if r["slope"] >= r["y"]
    }
    assert set(under) == set(UNDER_A_SLOPE), under
    assert [k for k, v in under.items() if v > UNDER_A_SLOPE[k]] == [], under


def test_the_places_where_a_ring_is_not_the_whole_answer_are_the_named_ones(
    game: GamePage,
) -> None:
    """Every place where something the walk-up test asks first reaches a ring.

    A mentor, the finale on a finished island, an open signpost and a nearer
    ring each answer ahead of the ring you are standing in. The list is the
    island's truth; a new entry is a place to look at before it ships.
    """
    game.goto()
    game.start()
    reach = game.page.evaluate(
        """([stop, mentor, inn]) => {
             const d = window.__data(), out = [];
             const far = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1]);
             Object.entries(d.worlds).forEach(([w, cfg]) => {
               const arts = d.artifacts.filter(a => a.world === w);
               arts.forEach((a, i) => arts.slice(i + 1).forEach(b => {
                 if (far(a.pos, b.pos) < a.r + b.r)
                   out.push(w + ': ' + [a.id, b.id].sort().join(' and '));
               }));
               cfg.plots.forEach((p, k) => arts.forEach(a => {
                 if (far(p, a.pos) < a.r + stop)
                   out.push(w + ': signpost ' + (k + 1) + ' and ' + a.id);
               }));
               d.mentors.filter(m => m.world === w).forEach(m => arts.forEach(a => {
                 if (far(m.pos, a.pos) < a.r + mentor)
                   out.push(w + ': ' + m.id + ' and ' + a.id);
               }));
               arts.forEach(a => {
                 if (far([0, 0], a.pos) < a.r + inn)
                   out.push(w + ': the finale and ' + a.id);
               });
             });
             return out;
           }""",
        [STOP_RADIUS, MENTOR_RADIUS, INN_RADIUS],
    )
    assert sorted(reach) == [
        "campus: cafe and stall",
        "campus: signpost 4 and mountain",
        "campus: signpost 6 and dock",
        "campus: the finale and cafe",
        "campus: the finale and fountain",
        "campus: the finale and stall",
        "campus: the finale and well",
        "prod: the finale and office",
        "winter: amodei and library",
        "winter: signpost 6 and energy-grid",
        "winter: the finale and data-centre",
    ]
    game.assert_clean()


# F6 ------------------------------------------------------------------------
def test_a_vault_link_on_an_artifact_sheet_looks_and_works_like_a_link(
    game: GamePage,
) -> None:
    game.goto()
    game.start()
    _open_artifact(game, "cafe")
    link = game.page.locator("#s-artifact .wl").first
    title = (link.text_content() or "").strip()
    assert title
    look = link.evaluate(
        """el => {
             const own = getComputedStyle(el);
             const parent = getComputedStyle(el.parentElement);
             return {color: own.color, parent: parent.color, tab: el.tabIndex,
                     underline: parseFloat(own.borderBottomWidth) || 0,
                     decoration: own.textDecorationLine};
           }"""
    )
    assert look["color"] != look["parent"]
    assert look["underline"] > 0 or look["decoration"] != "none"
    assert look["tab"] >= 0
    # Reached from the keyboard, it wears the ring every button on the sheet
    # wears, so a keyboard user sees where they are the same way everywhere.
    ring = """el => { const s = getComputedStyle(el);
                      return {visible: el.matches(':focus-visible'),
                              outline: [s.outlineStyle, s.outlineWidth,
                                        s.outlineColor, s.outlineOffset]}; }"""
    kb = game.page.keyboard
    button = game.page.locator("#s-artifact button[data-demo]").first
    button.focus()
    kb.press("Shift+Tab")
    kb.press("Tab")
    house = button.evaluate(ring)
    link.focus()
    kb.press("Shift+Tab")
    kb.press("Tab")
    own = link.evaluate(ring)
    assert house["visible"] and house["outline"][0] == "solid", house
    assert own == house, (own, house)
    # The keyboard is one of the two ways in, so the note opens from a key.
    kb.press("Enter")
    game.page.wait_for_selector("#vault.on", state="attached")
    assert title in (game.page.text_content("#vnote") or "")
    game.assert_clean()


# F7 ------------------------------------------------------------------------
def test_the_balloon_demo_charges_the_region_it_rents_in() -> None:
    block = _demo_text("balloon")
    regions = set(re.findall(r"--region ([a-z0-9-]+)", block))
    assert len(regions) == 1, f"the demo rents in {regions or 'no region'}"
    rate = T3_SMALL_USD_PER_HOUR[regions.pop()]
    meter = re.search(r"meter: ([\d.]+) USD per hour", block)
    assert meter, "the demo never reads the meter"
    assert float(meter.group(1)) == rate
    # And the bill it leaves running for a month is that rate times the hours.
    month = re.search(r"30 days later \.\.\.\s+([\d.]+) USD", block)
    assert month, "the demo never leaves the balloon up"
    assert float(month.group(1)) == round(rate * 24 * 30, 2)


# P9 (10-6) -----------------------------------------------------------------
def test_the_stall_answers_a_path_it_does_not_have_with_404() -> None:
    """The status code is the lesson, so it has to be the one the thing gives.

    The cafe two artifacts away answers an unknown path with 404, and so does
    the framework the stall's own walkthrough builds on. Answering it with
    400 tells the reader the sentence was malformed and sends them to fix the
    body, which is the one part of that request that was fine.
    """
    demos = _demo_lines("stall")
    menu = next(line for d in demos for line in d if line.startswith("endpoints:"))
    listed = set(re.findall(r"/[a-z]+", menu))
    assert listed, menu
    asked = 0
    for lines in demos:
        for ask, answer in zip(lines, lines[1:], strict=False):
            path = re.match(r"(?:GET|POST) (/[\w.-]+)", ask)
            code = re.match(r"(\d{3}) ", answer)
            if not path or not code:
                continue
            asked += 1
            if path.group(1) in listed:
                # A body the server cannot read is the client's grammar.
                assert code.group(1) in {"200", "400", "422"}, (ask, answer)
            else:
                assert code.group(1) == "404", (ask, answer)
    assert asked >= 3, "the stall never orders anything"


def test_the_stall_names_both_codes_its_wrong_order_gets() -> None:
    """The sentence above the terminal names every code the demo prints.

    Ordering without reading the menu gets a 404 for the wrong path and a 400
    for the wrong body, so a sentence that promises one of them is half true.
    """
    stall = next(a for a in CAMPAIGN["artifacts"] if a["id"] == "stall")
    sentence = next(s for s in stall["what"].split(". ") if "without reading" in s)
    demo = next(d for d in _demo_lines("stall") if any("404" in line for line in d))
    printed = {m for line in demo for m in re.findall(r"^(4\d\d) ", line)}
    assert printed == {"404", "400"}
    assert set(re.findall(r"\b4\d\d\b", sentence)) == printed, sentence


def test_no_number_in_a_transcript_breaks_between_its_digits() -> None:
    """A thousands gap is a no-break space, so "312 000 tokens" stays one number.

    The terminal folds a long step onto the next line on a phone, and a plain
    space is where it may fold. Read as written, escapes and all.
    """
    demos = _demo_text()
    demos = demos[demos.index("const ART_DEMOS") : demos.index("\n};\n")]
    assert "\\u00a0" in demos
    assert re.findall(r"\d \d{3}\b[^\"']*", demos) == []


def test_the_tech_tree_says_set_back_for_a_shelf_it_sets_back() -> None:
    """A shelf you did not choose is set back and still open, so the line says so."""
    tree = next(
        line for line in VAULT.read_text("utf-8").splitlines() if "treenav" in line
    )
    assert "the rest set back" in tree
    assert "dimmed" not in tree


# Found while reading this file for P9, and a defect of the same kind as the
# batch it came from: a demo that names a module of this project in a folder
# the project does not have.
def test_no_demo_names_a_module_of_this_project_in_the_wrong_folder() -> None:
    package = ROOT / "vibemap"
    modules = {p.name for p in package.glob("*.py")}
    wrong = [
        path
        for path in re.findall(r"[\w.-]+/[\w./-]+\.py", _demo_text())
        if Path(path).name in modules and Path(path).parent.name != package.name
    ]
    assert wrong == [], f"named outside {package.name}/: {wrong}"


def test_the_mountain_transcripts_keep_their_columns_in_line() -> None:
    """Both mountain demos are tables, and a table is read down its columns.

    The padding is by hand, so a word that grows in the first column leaves
    the second one ragged, and the reader sees that before the lesson.
    """
    for lines in _demo_lines("mountain"):
        columns = set()
        for line in lines:
            runs = list(re.finditer(r"\S {2,}", line))
            if runs:
                columns.add(runs[-1].end())
        assert len(columns) == 1, (columns, lines)


# The changed surfaces, on the laptop the course is written for and on both
# phones: the sheet (steps, terminal, vault links) and the ring in the world.
PROFILES = ("desktop", "android", "iphone")


@contextmanager
def _profile(
    chromium: Browser, webkit: Browser, server: str, profile: str
) -> Iterator[GamePage]:
    options: dict[str, Any] = (
        {"viewport": {"width": 1440, "height": 900}}
        if profile == "desktop"
        else phone_options(profile)
    )
    browser = webkit if profile == "iphone" else chromium
    # Three sizes across two browsers is more than the fixtures offer, so this
    # opens a page of its own, through the helper the fixtures use: that is
    # where the clock, the toast record and the write rule are installed.
    with game_page(browser, server, **options) as game:
        game.goto()
        game.start()
        yield game


@pytest.mark.parametrize("profile", PROFILES)
def test_the_artifact_surfaces_are_photographed(
    chromium: Browser, webkit: Browser, server: str, profile: str
) -> None:
    with _profile(chromium, webkit, server, profile) as game:
        _open_artifact(game, "cafe")
        lines = game.page.evaluate("window.__demos().cafe[0].o")
        game.page.click("#s-artifact button[data-demo='0']")
        _wait_line(game, lines[-1])
        # Photograph the transcript that is whole, not one still printing.
        assert game.page.text_content("#art-term") == "\n".join(lines)
        game.screenshot(f"hunt_f_sheet_{profile}")
        # The vault links sit at the foot of the sheet, past the walkthrough.
        link = game.page.locator("#s-artifact .wl").first
        link.scroll_into_view_if_needed()
        game.still("document.getElementById('sheet').scrollTop")
        assert link.is_visible()
        game.screenshot(f"hunt_f_links_{profile}")
        # The demo copy that changed: the balloon's meter, the mountain's
        # module path and columns, and the stall's two status codes, each
        # read back in the terminal it prints into.
        for aid, demo in (("balloon", 0), ("mountain", 1), ("stall", 1)):
            _open_artifact(game, aid)
            transcript = game.page.evaluate(f"window.__demos()['{aid}'][{demo}].o")
            game.page.click(f"#s-artifact button[data-demo='{demo}']")
            _wait_line(game, transcript[-1])
            assert game.page.text_content("#art-term") == "\n".join(transcript)
            game.screenshot(f"hunt_f_{aid}_{profile}")
        game.page.click("#sheet .x")
        # The lake pushes the walker out at its bank, so this is as close to
        # the fountain as a player can stand: the ring has to be visible here,
        # and the walk has to have arrived, which the prompt is the proof of.
        _walk_onto_the_fountain_ring(game)
        game.page.wait_for_selector("#enter.on", state="attached")
        # The prompt rises into place, so the shot waits for it to land.
        game.still("document.getElementById('enterbtn').getBoundingClientRect().top")
        assert "fountain" in (game.page.text_content("#enterbtn") or "").lower()
        game.screenshot(f"hunt_f_fountain_{profile}")
        game.assert_clean()
