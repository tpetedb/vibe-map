"""Hunt batch F: the artifacts in the world and on their sheet.

One test per finding of `work/orders/hunt-f-artifacts/findings.md`. Each one
drives the control a player uses and waits for a fact the page produced: the
scene the world builder made, the text the terminal holds, the style the
browser computed. Nothing here waits on a clock.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import pytest
from playwright.sync_api import Browser

from tests.conftest import (
    GAME_PATH,
    WAIT_MS,
    GamePage,
    _attach_error_collectors,
    phone_options,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "game" / "16-artifacts.js"

# The on-demand price of one t3.small hour, by region, from the same vendor
# table the demo's "Do it for real" step sends the learner to look at:
# https://aws-pricing.com/t3.small.html (read 2026-09-21). The demo may name
# any region in this table; it may not name one and charge another's rate.
T3_SMALL_USD_PER_HOUR = {"us-east-1": 0.0208, "eu-west-1": 0.0228}


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


def _open_artifact(game: GamePage, aid: str) -> None:
    """Open one artifact's sheet with the Roadmap's own Open button."""
    names = game.page.evaluate(
        "Object.fromEntries(window.__artifacts().map(a => [a.id, a.name]))"
    )
    game.open_roadmap()
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
def test_a_step_that_says_print_exactly_is_drawn_without_ligatures(
    game: GamePage,
) -> None:
    game.goto()
    game.start()
    targets = game.page.evaluate(
        """() => window.__data().artifacts
             .filter(a => a.real.steps.some(s => s.includes('->')))
             .map(a => ({id: a.id, step: a.real.steps.find(s => s.includes('->'))}))"""
    )
    # The finding's premise: there are steps whose text has to be reproduced
    # character for character, and the check reads the line back.
    assert targets, "no artifact step asks for an arrow to be printed"
    for target in targets:
        _open_artifact(game, target["id"])
        step = game.page.locator("#s-artifact .lesson ol li").filter(
            has_text=target["step"]
        )
        assert step.count() == 1, target["id"]
        assert "->" in (step.text_content() or ""), target["id"]
        # The commands under it are typed as they stand, so they are held to
        # the same rule.
        for part in (step, game.page.locator("#s-artifact .lesson pre code")):
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
def test_every_artifact_ring_is_the_zone_that_offers_inspect(
    game: GamePage,
) -> None:
    game.goto()
    game.start()
    rings = _rings(game)
    assert len(rings) >= 10
    # "Walk up to the yellow ring and press Inspect" is the copy, so the ring
    # the player sees is the radius nearArtifact tests against, not a smaller
    # decoration inside it.
    assert [r["id"] for r in rings if abs(r["r"] - r["zone"]) > 1e-6] == []
    # And none of them is buried in the thing it belongs to, the way the
    # mountain's was inside the mountain.
    assert [r["id"] for r in rings if r["r"] <= r["block"]] == []
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
    # The keyboard is one of the two ways in, so the note opens from a key.
    link.focus()
    game.page.keyboard.press("Enter")
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


# P9 ------------------------------------------------------------------------
def test_no_demo_names_a_module_of_this_project_in_the_wrong_folder() -> None:
    package = ROOT / "vibemap"
    modules = {p.name for p in package.glob("*.py")}
    wrong = [
        path
        for path in re.findall(r"[\w.-]+/[\w./-]+\.py", _demo_text())
        if Path(path).name in modules and Path(path).parent.name != package.name
    ]
    assert wrong == [], f"named outside {package.name}/: {wrong}"


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
    context = (webkit if profile == "iphone" else chromium).new_context(**options)
    page = context.new_page()
    game = GamePage(page=page, url=server + GAME_PATH)
    _attach_error_collectors(page, game.errors)
    game.goto()
    game.start()
    try:
        yield game
    finally:
        context.close()


@pytest.mark.parametrize("profile", PROFILES)
def test_the_artifact_surfaces_are_photographed(
    chromium: Browser, webkit: Browser, server: str, profile: str
) -> None:
    with _profile(chromium, webkit, server, profile) as game:
        _open_artifact(game, "cafe")
        game.page.click("#s-artifact button[data-demo='0']")
        _wait_line(game, game.page.evaluate("window.__demos().cafe[0].o.at(-1)"))
        game.screenshot(f"hunt_f_sheet_{profile}")
        # The vault links sit at the foot of the sheet, past the walkthrough.
        game.page.locator("#s-artifact .wl").first.scroll_into_view_if_needed()
        game.still("document.getElementById('sheet').scrollTop")
        game.screenshot(f"hunt_f_links_{profile}")
        game.page.click("#sheet .x")
        # The lake pushes the walker out at its bank, so this is as close to
        # the fountain as a player can stand: the ring has to be visible here.
        game.walk_to(-3.2, 6.4, tol=0.9, steps=300)
        game.frames(4)
        game.screenshot(f"hunt_f_fountain_{profile}")
        game.assert_clean()
