"""Render the screenshots and the gameplay GIF for the README and the docs.

Everything comes from the built game through headless Chromium with software
WebGL, so the pictures always match the code. Output lands in docs/media/.
One test writes there too: tests/test_game_pet.py rewrites the six
docs/media/pets-game crops while issue 148 is open, and this tool is what puts
them back.

    uv run python tools/media.py            all screenshots and the GIF
    uv run python tools/media.py --quick    screenshots only
    uv run python tools/media.py --gif      gameplay GIF only
"""

from __future__ import annotations

import functools
import http.server
import json
import math
import sys
import threading
import time
from pathlib import Path
from typing import Any

from PIL import Image
from playwright.sync_api import Page, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "media"
Event = dict[str, Any]
GAME = "/game/vibe-map.html"
CHROMIUM_ARGS = [
    "--use-angle=swiftshader",
    "--use-gl=angle",
    "--enable-unsafe-swiftshader",
    "--ignore-gpu-blocklist",
    "--enable-webgl",
]
PLAYED = {
    "name": "Lotte",
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
# The six vendored sprite sets, in the order the Companion select offers them.
PETS = ("cat", "crab", "dog", "duck", "snail", "turtle")
# The windows the pictures are taken in. A screen laid out against the window
# is photographed in a window of exactly that size: the stage is shorter than
# the window by the talk band, so growing the window to fill a stage-shaped
# clip pushes the title card and the More sheet out of the frame.
SOCIAL = (1200, 630)  # the Open Graph size, the one pages.yml publishes
DESKTOP = (1280, 760)
PHONE = (393, 852)
# The GIF's window. In a shorter one the zoom column, which sits above the
# stage's bottom edge, is drawn over the minimap, which hangs below the HUD at
# the top of the window (issue 161), and the picture opens on two controls at
# once.
GIF_WINDOW = (800, 640)
GAMEPLAY_MARKER = b"vibe-map:campus-to-winter-bridge:v1"
# A panel worth a picture, by the function its HUD button calls, the screen
# that function opens and what to do once it is open. The picture is the
# sheet, which is what a player sees.
PANELS = (
    ("backpack.png", "openPack()", "s-pack", ""),
    ("ask.png", "openChat()", "s-chat", ""),
    ("dashboard.png", "openDashboard()", "s-dash", ""),
    ("settings.png", "openSettings()", "s-settings", ""),
    ("artifact-cafe.png", "openArtifact('cafe')", "s-artifact", "runDemo('cafe', 2)"),
)
# Wait for a number the page computes to stop changing, the way the test
# battery does: the walker arrives when it arrives, not after so many seconds.
STILL = """expr => new Promise(done => {
  const read = new Function('return (' + expr + ')');
  let last = null, stable = 0, running = true, painted = 0, sampled = -1;
  const frame = () => { painted++; if (running) requestAnimationFrame(frame) };
  requestAnimationFrame(frame);
  const deadline = performance.now() + 20000;
  const tick = () => {
    if (painted > sampled) {
      const v = read();
      stable = last !== null && Math.abs(v - last) < 0.02 ? stable + 1 : 0;
      sampled = painted; last = v;
    }
    if (stable >= 6 || performance.now() > deadline) { running = false; done(true) }
    else setTimeout(tick, 60);
  };
  tick();
})"""


class Cut(Exception):
    """A picture that would leave its own subject out of frame, or a control
    that is not where a tap can reach it. Raised before the file is written."""


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args: object) -> None:
        pass


def _serve() -> tuple[http.server.ThreadingHTTPServer, str]:
    handler = functools.partial(_Quiet, directory=str(ROOT))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    host, port = httpd.server_address[:2]
    return httpd, f"http://{host}:{port}{GAME}"


def _ev(ts: float, kind: str, ident: str, world: str, v: int | None = None) -> Event:
    """One event in the shape the game records: {ts, kind, id, world} and v."""
    out: Event = {"ts": int(ts), "kind": kind, "id": ident, "world": world}
    if v is not None:
        out["v"] = v
    return out


def _events() -> list[Event]:
    """Three evenings of play, so every chart on the dashboard has a shape."""
    now = int(time.time() * 1000)
    day, hour, minute = 86_400_000, 3_600_000, 60_000
    out: list[Event] = []
    for back in (2, 1, 0):
        at, n = now - back * day - 4 * hour, str(3 - back)
        out += [
            _ev(at, "session", "start", "campus"),
            _ev(at + minute, "play", "tick", "campus", 60),
            _ev(at + 2 * minute, "open", n, "campus"),
            _ev(at + 5 * minute, "dwell", f"s-{n}", "campus", 180),
            _ev(at + 6 * minute, "claim", n, "campus"),
        ]
    at = now - 3 * hour
    for n, seconds in ((1, 240), (2, 120)):
        out += [
            _ev(at, "open", str(n), "winter"),
            _ev(at + 1000, "dwell", "s-gen", "winter", seconds),
        ]
        at += 10 * minute
    out.append(_ev(now - 1000, "artifact", "cafe", "campus"))
    return out


def rich() -> dict[str, Any]:
    """A camp with something in every panel, so no picture is of an empty box.

    The island shots keep PLAYED: their framing is what the README leans on.
    """
    return dict(
        PLAYED,
        artifacts=["cafe", "fountain", "well"],
        artifactsBuilt=["cafe"],
        items=["campus-commit", "campus-pr", "campus-token", "campus-crate"],
        ach=["first-light", "first-sit", "collector"],
        wear=["cap"],
        bottles=["campus-bottle-cause"],
        events=_events(),
    )


def _load(page: Page, url: str, state: dict | None) -> None:
    page.goto(url)
    if state is not None:
        page.evaluate(
            "([k, v]) => localStorage.setItem(k, JSON.stringify(v))",
            ["vibemap1", state],
        )
        page.reload()
    page.wait_for_function("typeof window.__S === 'function'")
    _frames(page, 3)


def _start(page: Page, name: str = "Lotte") -> None:
    """Resume where there is something to resume, else type a name and start.

    Two things the title screen learned make the old one-line click wrong: the
    Continue card's button is primary too, and Start refuses an empty name.
    """
    resume = page.locator("#btn-continue")
    if resume.count() and resume.is_visible():
        resume.click()
    else:
        page.fill("#name", name)
        page.click("#btn-go")
    page.wait_for_selector("#title.off", state="attached")
    page.wait_for_function("window.__debug().started === true")
    _frames(page, 3)


def _px(ndc: float, width: int) -> float:
    """A projected x, from the clip space three.js hands back, to a pixel."""
    return (ndc * 0.5 + 0.5) * width


def _py(ndc: float, height: int) -> float:
    return (0.5 - ndc * 0.5) * height


def _around(x: float, y: float, stage: dict[str, int], side: int = 360) -> dict:
    """A square clip centred on a point, kept inside the stage."""
    return {
        "x": max(0, min(stage["width"] - side, x - side / 2)),
        "y": max(0, min(stage["height"] - side, y - side / 2)),
        "width": side,
        "height": side,
    }


def _frames(page: Page, n: int = 10) -> None:
    """Wait for n more drawn frames: pop-ins and the camera move in the loop."""
    at = int(page.evaluate("window.__debug().frame") or 0)
    page.wait_for_function("n => window.__debug().frame >= n", arg=at + n)


def _settled(page: Page, world: str | None = None) -> None:
    """Wait for the island asked for, for the camera to land and for the zoom.

    A fixed wait after setWorld catches the fly-over: the island is half built
    and the picture is of nothing. These are facts the page produced.
    """
    if world:
        page.wait_for_function("w => window.__debug().world === w", arg=world)
    page.wait_for_function(
        "() => { const g = window.__gfx();"
        " return g.cam.off < 0.5 && Math.abs(g.zoom.level - g.zoom.target) < 2e-3 }"
    )
    _frames(page, 20)


def _calm(page: Page) -> None:
    """No toast on screen: a picture should not catch one halfway through."""
    page.wait_for_function("() => !document.querySelector('#toast .tst')")


def _still(page: Page, expression: str) -> None:
    """Wait until a number the page computes stops changing (the walker)."""
    page.wait_for_function(STILL, arg=expression)


def _walked(page: Page, before: list[float]) -> float:
    """How far the walker has come from a position, on the ground plane."""
    now = page.evaluate("() => window.__debug().pos")
    return math.hypot(now[0] - before[0], now[2] - before[2])


def _tap_towards(
    page: Page, to: tuple[float, float], share: float = 0.8
) -> tuple[float, float]:
    """Tap the ground part of the way to a point, and never anything else.

    Tap to walk is the real control. The ground is a plane, so a point between
    two of its points on screen is between them on the island and the walker
    can never overshoot the target. A point below the stage, or under one of
    the controls drawn over it, is not the ground: tapping there walks nobody,
    so a blocked point is aimed shorter until one of them is the island.
    """
    me = page.evaluate("() => window.__pet().screen")
    hit = "nothing"
    for part in (share, share * 0.7, share * 0.45, share * 0.25):
        at = (me["x"] + (to[0] - me["x"]) * part, me["y"] + (to[1] - me["y"]) * part)
        hit = page.evaluate(
            "([x, y]) => { const el = document.elementFromPoint(x, y);"
            " return el ? el.id || el.tagName.toLowerCase() : 'nothing' }",
            [at[0], at[1]],
        )
        if hit == "c":
            page.mouse.click(*at)
            return at
    raise Cut(f"every tap towards {to[0]:.0f},{to[1]:.0f} lands on {hit}, not ground")


def _signpost(page: Page, label: str) -> tuple[float, float]:
    """The ground under a signpost's pill, in canvas pixels.

    The plot positions live in the game's own scope; what it publishes is the
    plate it drew, which hangs over the same signpost and is only there when a
    player can see it too.
    """
    plate = page.evaluate(
        "t => window.__gfx().plates.list.find(p => p.text === t && p.o > .5) || null",
        label,
    )
    if plate is None:
        raise Cut(f"no {label} signpost is on screen to walk to")
    return plate["x"], plate["y"] + plate["h"]


def _walk_near(page: Page, stage: dict[str, int], gap: float = 6.0) -> None:
    """Walk to the shore beside the first bottle, in steps, never onto it.

    Each tap aims part of the way there, because walking over a bottle reads
    it and takes it off the shore.
    """
    for _ in range(6):
        bottle = page.evaluate("() => window.__bottles().here[0]")
        at = page.evaluate("() => window.__debug().pos")
        if math.hypot(at[0] - bottle["x"], at[2] - bottle["z"]) < gap:
            return
        _tap_towards(
            page,
            (
                _px(bottle["screen"][0], stage["width"]),
                _py(bottle["screen"][1], stage["height"]),
            ),
        )
        page.wait_for_function(
            "p => { const q = window.__debug().pos;"
            " return Math.hypot(q[0] - p[0], q[2] - p[2]) > 1 }",
            arg=at,
        )
        _still(page, "window.__debug().pos[0] + window.__debug().pos[2]")


def _outside(clip: dict[str, int], box: dict[str, float] | None) -> tuple[str, ...]:
    """Which edges of a clip a box crosses. Empty means the subject is whole."""
    if box is None:
        return ("missing",)
    edges = {
        "left": box["x"] < clip["x"] - 0.5,
        "top": box["y"] < clip["y"] - 0.5,
        "right": box["x"] + box["width"] > clip["x"] + clip["width"] + 0.5,
        "bottom": box["y"] + box["height"] > clip["y"] + clip["height"] + 0.5,
    }
    return tuple(name for name, out in edges.items() if out)


def _whole(page: Page, clip: dict[str, int], selector: str, name: str) -> None:
    """Refuse a picture that cuts its own subject.

    The stage and the window are two rectangles of different heights, so a
    clip measured from one and a subject laid out against the other can
    disagree without anything failing: the picture is simply wrong.
    """
    edges = _outside(clip, page.locator(selector).bounding_box())
    if edges:
        raise Cut(f"{name}: {selector} is off the {' and the '.join(edges)} of it")


def _window(page: Page, width: int, height: int) -> dict[str, int]:
    """The whole window as the clip, for a screen laid out against the window.

    The title card, the More sheet and the minimap are positioned against the
    window rather than against the stage, so the window is the picture.
    """
    if page.viewport_size != {"width": width, "height": height}:
        page.set_viewport_size({"width": width, "height": height})
        _frames(page, 10)
    return {"x": 0, "y": 0, "width": width, "height": height}


def _stage(page: Page, width: int) -> dict[str, int]:
    """The stage as this window has it, for a picture of the island itself."""
    tall = page.evaluate(
        "() => document.getElementById('stage').getBoundingClientRect().height"
    )
    return {"x": 0, "y": 0, "width": width, "height": round(tall)}


def _fill_stage(page: Page, width: int, height: int) -> dict[str, int]:
    """Grow the window until the stage itself is the size the picture wants.

    The stage leaves room under it for the controls, so a shot of the whole
    window carries a strip below the island that no player looks at. Only for
    a picture whose subject is on the stage: it makes the window taller than
    the clip, and anything anchored to the window moves down with it.
    """
    for _ in range(4):
        tall = page.evaluate(
            "() => document.getElementById('stage').getBoundingClientRect().height"
        )
        box = page.viewport_size or {"width": width, "height": height}
        if abs(tall - height) < 1:
            break
        page.set_viewport_size(
            {"width": width, "height": int(box["height"] + height - tall)}
        )
        page.wait_for_timeout(400)
    return {"x": 0, "y": 0, "width": width, "height": height}


def _zoom(page: Page, framing: str) -> None:
    """Step the zoom to one of the three framings, then wait for the camera.

    The control is the one a player presses, so the picture can never show a
    level the game cannot reach; the limits come from the game, not from here.
    """
    page.evaluate(
        "key => { const lim = window.__gfx().zoom;"
        " const z = key === 'walker' ? lim.min : key === 'far' ? lim.max : 0;"
        " for (let i = 0; i < 40; i++) { const at = window.__gfx().zoom.target;"
        " if (Math.abs(at - z) < 1e-3) break; zoomStep(at > z ? 1 : -1) } }",
        framing,
    )
    _settled(page)


def _sheet(page: Page, name: str, opener: str, screen: str, after: str) -> Path:
    """One panel, over the dimmed island, the way the HUD button opens it."""
    page.evaluate(opener)
    page.wait_for_selector(f"#{screen}.on", state="attached")
    _frames(page, 20)
    if after:
        page.evaluate(after)
        page.wait_for_timeout(2600)
    target = OUT / name
    page.screenshot(path=str(target), clip=_fill_stage(page, 1280, 900))
    page.evaluate("closeSheet()")
    page.wait_for_selector("#sheet.on", state="detached")
    return target


def screenshots(browser, url: str) -> list[Path]:
    out: list[Path] = []
    OUT.mkdir(parents=True, exist_ok=True)

    # The title screen, at the social-card size and at the size the README
    # shows it. The card is fixed to the window and is as tall as the window
    # lets it be, so the window is the picture in both.
    for name, (wide, tall), scale in (
        ("hero.png", SOCIAL, 2),
        ("onboarding-start.png", DESKTOP, 1),
    ):
        ctx = browser.new_context(
            viewport={"width": wide, "height": tall}, device_scale_factor=scale
        )
        page = ctx.new_page()
        _load(page, url, None)
        # The island orbits behind the title; give it a turn before the shot.
        page.wait_for_timeout(2200)
        clip = _window(page, wide, tall)
        _whole(page, clip, "#title .box", name)
        page.screenshot(path=str(OUT / name), clip=clip)
        out.append(OUT / name)
        ctx.close()

    # Desktop: every world with a played state, then roadmap, vault and tree.
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 760}, device_scale_factor=1
    )
    page = ctx.new_page()
    _load(page, url, PLAYED)
    _start(page)
    island = _fill_stage(page, 1280, 720)
    for world in ("campus", "winter", "desert", "prod"):
        page.evaluate(f"setWorld('{world}')")
        _settled(page, world)
        _calm(page)
        page.screenshot(path=str(OUT / f"island-{world}.png"), clip=island)
        out.append(OUT / f"island-{world}.png")
    # The winter island whole, where its three artifact props are all in frame.
    page.evaluate("setWorld('winter')")
    _settled(page, "winter")
    _zoom(page, "island")
    _calm(page)
    page.screenshot(path=str(OUT / "island-winter-artifacts.png"), clip=island)
    out.append(OUT / "island-winter-artifacts.png")
    # The far framing: the island in the archipelago, with its bridges.
    page.evaluate("setWorld('campus')")
    _settled(page, "campus")
    _zoom(page, "far")
    _calm(page)
    page.screenshot(path=str(OUT / "archipelago.png"), clip=island)
    out.append(OUT / "archipelago.png")
    _zoom(page, "walker")
    page.click("#hud button:has-text('Roadmap')")
    page.wait_for_selector("#s-map.on", state="attached")
    _frames(page, 20)
    page.screenshot(path=str(OUT / "roadmap.png"), clip=island)
    out.append(OUT / "roadmap.png")
    page.evaluate("closeSheet()")
    page.click("#hud button:has-text('Vault')")
    page.wait_for_timeout(2500)
    page.locator("#vault").screenshot(path=str(OUT / "vault.png"))
    out.append(OUT / "vault.png")
    page.click("#vtop button:has-text('Tech tree')")
    page.wait_for_timeout(600)
    page.locator("#vault").screenshot(path=str(OUT / "tree.png"))
    out.append(OUT / "tree.png")
    ctx.close()

    # The panels, on a camp that has played enough for them to hold something.
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 900}, device_scale_factor=1
    )
    page = ctx.new_page()
    _load(page, url, rich())
    _start(page)
    for name, opener, screen, after in PANELS:
        out.append(_sheet(page, name, opener, screen, after))
    stage = _fill_stage(page, 1280, 900)
    # The six companions as the game draws them, picked through the real
    # control in Settings. tests/test_game_pet.py writes these six files as
    # well while issue 148 is open, so this loop is what puts them back.
    pets = OUT / "pets-game"
    pets.mkdir(parents=True, exist_ok=True)
    _zoom(page, "walker")
    for pet in PETS:
        page.evaluate("openSettings()")
        page.wait_for_selector("#set-pet", state="visible")
        page.select_option("#set-pet", pet)
        page.wait_for_function("id => window.__S().pet === id", arg=pet)
        page.evaluate("closeSheet()")
        page.wait_for_selector("#sheet.on", state="detached")
        page.wait_for_function(
            "id => window.__pet().id === id && window.__pet().on", arg=pet
        )
        _frames(page, 20)
        _calm(page)
        seen = page.evaluate("() => window.__pet().screen")
        page.screenshot(
            path=str(pets / f"{pet}.png"),
            clip=_around(seen["x"], seen["y"], stage, side=320),
        )
        out.append(pets / f"{pet}.png")
    # A message in a bottle where it lies. The walker is sent to the shore
    # beside it rather than onto it, because walking over one reads it.
    _zoom(page, "island")
    _calm(page)
    _walk_near(page, stage)
    _zoom(page, "walker")
    _calm(page)
    at = page.evaluate("() => window.__bottles().here[0].screen")
    page.screenshot(
        path=str(OUT / "bottle.png"),
        clip=_around(
            _px(at[0], stage["width"]), _py(at[1], stage["height"]), stage, side=420
        ),
    )
    out.append(OUT / "bottle.png")
    ctx.close()

    # Phone: the HUD as a thumb finds it, and the More menu open over it. The
    # HUD lives on the stage; the More sheet lies on the window's bottom edge,
    # so the two pictures are cut to different rectangles of the same window.
    ctx = browser.new_context(
        viewport={"width": PHONE[0], "height": PHONE[1]},
        device_scale_factor=2,
        is_mobile=True,
        has_touch=True,
    )
    page = ctx.new_page()
    _load(page, url, PLAYED)
    _start(page)
    _settled(page, "campus")
    _calm(page)
    page.screenshot(path=str(OUT / "phone.png"), clip=_stage(page, PHONE[0]))
    out.append(OUT / "phone.png")
    page.tap("#hud-more-btn")
    page.wait_for_selector("#hud-more.open", state="attached")
    _frames(page, 20)
    clip = _window(page, *PHONE)
    _whole(page, clip, "#hud-menu", "phone-more.png")
    page.screenshot(path=str(OUT / "phone-more.png"), clip=clip)
    out.append(OUT / "phone-more.png")
    ctx.close()
    return out


def _workstream(page: Page, n: int):
    """Workstream n's button in the Roadmap panel, past Pre-flight."""
    buttons = page.locator("#plotlist button")
    first = buttons.nth(0).text_content() or ""
    return buttons.nth((1 if "Pre-flight" in first else 0) + n - 1)


def _walk_to(
    page: Page,
    x: float,
    z: float,
    snap,
    *,
    tol: float = 2.2,
    steps: int = 160,
) -> int:
    """Steer with the keyboard until the page reports arrival.

    Returns the number of sampled frames for which the page said the walker
    was on a bridge. Rendering frames are the clock, so a loaded machine takes
    longer without changing where the walk ends.
    """
    keyboard = page.keyboard
    held: set[str] = set()
    deck_frames = 0
    start_world = page.evaluate("window.__S().world")

    def hold(wanted: set[str]) -> None:
        for key in wanted - held:
            keyboard.down(key)
            held.add(key)
        for key in held - wanted:
            keyboard.up(key)
        held.intersection_update(wanted)

    try:
        for step in range(steps):
            debug = page.evaluate("window.__debug()")
            px, _, pz = debug["pos"]
            dx, dz = x - px, z - pz
            if math.hypot(dx, dz) < tol:
                return deck_frames
            wanted: set[str] = set()
            if dx > 0.5:
                wanted.add("ArrowRight")
            elif dx < -0.5:
                wanted.add("ArrowLeft")
            if dz > 0.5:
                wanted.add("ArrowDown")
            elif dz < -0.5:
                wanted.add("ArrowUp")
            hold(wanted)
            _frames(page, 3)
            if page.evaluate("window.__debug().onBridge"):
                deck_frames += 3
            if step % 2 == 0:
                snap()
            if page.evaluate("window.__S().world") != start_world:
                return deck_frames
    finally:
        hold(set())
        _frames(page, 2)
    raise Cut(f"the walker did not reach {x:.1f},{z:.1f} in {steps} steps")


def _bridge_journey(page: Page, snap) -> dict[str, int | str]:
    """Cross campus to winter, then claim winter's first stop."""
    start = page.evaluate("window.__S().world")
    bridge = page.evaluate(
        "() => window.__debug().bridges.find(b => "
        "new Set([b.a,b.b]).has('campus') && "
        "new Set([b.a,b.b]).has('winter'))"
    )
    if not bridge or not bridge["open"] or not bridge["near"]:
        raise Cut(f"the campus to winter bridge is not open and near: {bridge}")

    _zoom(page, "island")
    for _ in range(3):
        snap()
        _frames(page, 3)

    ax, az = bridge["pa"]
    bx, bz = bridge["pb"]
    deck_frames = _walk_to(page, ax, az, snap, steps=180)
    hops = max(2, round(bridge["len"] * 0.62 / 7))
    for index in range(1, hops + 1):
        share = 0.62 * index / hops
        deck_frames += _walk_to(
            page,
            ax + (bx - ax) * share,
            az + (bz - az) * share,
            snap,
            steps=60,
        )
        if page.evaluate("window.__S().world") != start:
            break
    page.wait_for_function("() => window.__S().world === 'winter'")
    _settled(page, "winter")
    snap()

    page.click("#hud button:has-text('Roadmap')")
    page.wait_for_selector("#plotlist button", state="attached")
    _frames(page, 10)
    snap()
    _workstream(page, 1).click()
    page.wait_for_selector("#sheet .screen.on", state="attached")
    _frames(page, 10)
    snap()
    page.click("#sheet .screen.on button:has-text('Mark as done')")
    page.wait_for_function("() => (window.__S().doneW.winter || []).includes(1)")
    for _ in range(6):
        _frames(page, 3)
        snap()
    return {"from": start, "to": "winter", "deck_frames": deck_frames, "claimed": 1}


def gameplay_gif(browser, url: str) -> Path:
    """Walk a real bridge to winter and claim its first stop: one GIF.

    Every step uses the keyboard control and waits on state or rendered frames.
    A GIF of a caption that did not happen is worse than no GIF.
    """
    wide, tall = GIF_WINDOW
    ctx = browser.new_context(
        viewport={"width": wide, "height": tall}, device_scale_factor=1
    )
    page = ctx.new_page()
    _load(
        page,
        url,
        {"name": "Lotte", "done": [1], "doneW": {"campus": [1]}},
    )
    _start(page)
    _settled(page, "campus")
    _calm(page)
    clip = _window(page, wide, tall)
    shots: list[Image.Image] = []

    def snap() -> None:
        shots.append(Image.open(_bytes(page.screenshot(clip=clip))).convert("RGB"))

    result = _bridge_journey(page, snap)
    if result["deck_frames"] <= 0:
        raise Cut("the recorded journey never put the walker on the bridge deck")
    ctx.close()
    target = OUT / "gameplay.gif"
    small = [
        im.resize((480, round(480 * tall / wide)), Image.LANCZOS).quantize(colors=128)
        for im in shots
    ]
    small[0].save(
        target,
        save_all=True,
        append_images=small[1:],
        duration=120,
        loop=0,
        optimize=True,
        comment=GAMEPLAY_MARKER,
    )
    return target


def _bytes(data: bytes):
    import io

    return io.BytesIO(data)


def main() -> None:
    quick = "--quick" in sys.argv
    gif_only = "--gif" in sys.argv
    httpd, url = _serve()
    with sync_playwright() as p:
        browser = p.chromium.launch(args=CHROMIUM_ARGS)
        paths = [] if gif_only else screenshots(browser, url)
        if gif_only or not quick:
            paths.append(gameplay_gif(browser, url))
        browser.close()
    httpd.shutdown()
    for path in paths:
        print(f"{path.relative_to(ROOT)}  {path.stat().st_size // 1024} KB")
    print(json.dumps({"files": len(paths)}))


if __name__ == "__main__":
    main()
