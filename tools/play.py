"""Play the game headlessly: every island, every stop, every mentor, the finale.

The driver clicks what a person clicks (roadmap buttons, "Mark as done",
mentor choices, the date and pairing pickers) and ends with the progress
code the game exports, so the CLI can import a fully played campaign.

    uv run python tools/play.py                 play everything, print the code
    uv run python tools/play.py campus 3        play one stop, print the state
    uv run python tools/play.py --json          machine-readable summary
    uv run python tools/play.py --name=Tom      play as Tom (default Lotte)
"""

from __future__ import annotations

import functools
import http.server
import json
import sys
import threading
from dataclasses import dataclass, field
from pathlib import Path

from playwright.sync_api import Browser, Page, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
GAME = "/game/vibe-map.html"
WORLDS = ("campus", "winter", "desert", "prod")
CHROMIUM_ARGS = [
    "--use-angle=swiftshader",
    "--use-gl=angle",
    "--enable-unsafe-swiftshader",
    "--ignore-gpu-blocklist",
    "--enable-webgl",
]


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args: object) -> None:
        pass


def serve() -> tuple[http.server.ThreadingHTTPServer, str]:
    handler = functools.partial(_Quiet, directory=str(ROOT))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    host, port = httpd.server_address[:2]
    return httpd, f"http://{host}:{port}{GAME}"


@dataclass
class Player:
    """Drives one page through the campaign, collecting page errors."""

    page: Page
    errors: list[str] = field(default_factory=list)
    log: list[str] = field(default_factory=list)

    def attach(self) -> None:
        self.page.on("pageerror", lambda e: self.errors.append(f"pageerror: {e}"))
        self.page.on(
            "console",
            lambda m: (
                self.errors.append(f"console.error: {m.text}")
                if m.type == "error" and "favicon" not in m.text
                else None
            ),
        )

    def start(self, url: str, name: str) -> None:
        self.page.goto(url)
        self.page.wait_for_function("typeof window.__S === 'function'")
        self.page.fill("#name", name)
        self.page.click("text=Kick off the engagement")
        self.page.wait_for_selector("#title.off", state="attached")
        self.page.wait_for_timeout(800)
        self.log.append("started")

    def state(self) -> dict:
        return self.page.evaluate("window.__S()")

    def world(self, world: str) -> None:
        while self.state()["world"] != world:
            self.page.click("#hud button:has-text('World')")
            self.page.wait_for_timeout(1000)
        self.log.append(f"world {world}")

    def _workstream_buttons(self):
        buttons = self.page.locator("#plotlist button")
        offset = 1 if "Pre-flight" in (buttons.nth(0).text_content() or "") else 0
        return [buttons.nth(offset + i) for i in range(8)]

    def stop(self, n: int) -> None:
        """Open stop n from the roadmap and mark it done, the way a player does."""
        self.page.click("#hud button:has-text('Roadmap')")
        self.page.wait_for_selector("#plotlist button", state="attached")
        self.page.wait_for_timeout(500)  # the sheet springs in over ~400 ms
        self._workstream_buttons()[n - 1].click()
        self.page.wait_for_selector("#sheet .screen.on", state="attached")
        self.page.wait_for_timeout(150)
        # Exercise the mini-games on the campus while the sheet is open.
        world = self.state()["world"]
        if world == "campus":
            self._minigame(n)
        self.page.click("#sheet .screen.on button:has-text('Mark as done')")
        self.page.wait_for_timeout(300)
        assert n in self.state()["done"], f"{world} stop {n} did not register"
        self.log.append(f"{world} {n} done")

    def artifacts(self) -> int:
        """Open every artifact on this island and press each of its buttons."""
        ids = self.page.evaluate(
            "window.__artifacts()"
            ".filter(a => a.world === window.__S().world).map(a => a.id)"
        )
        for aid in ids:
            self.page.evaluate(f"openArtifact({aid!r})")
            self.page.wait_for_selector("#s-artifact.on", state="attached")
            buttons = self.page.locator("#s-artifact button[data-demo]")
            for i in range(buttons.count()):
                buttons.nth(i).click()
                self.page.wait_for_timeout(120)
            self.page.wait_for_timeout(600)
            assert (self.page.text_content("#art-term") or "").strip(), aid
        self.page.click("#sheet .x")
        self.log.append(f"artifacts {len(ids)}")
        return len(ids)

    def _minigame(self, n: int) -> None:
        p = self.page
        if n == 1:
            p.evaluate("spinUp()")
        elif n == 2:
            p.evaluate("speak(true)")
        elif n == 3:
            p.evaluate("roll(5)")
        elif n == 4:
            p.fill("#release", "A scoring board ranked by coffee")
            p.evaluate("commit()")
            p.evaluate("ruin()")
            p.evaluate("revert(0)")
        elif n == 5:
            p.evaluate("bridge('cal'); bridge('files')")
        elif n == 6:
            p.evaluate("weave()")

    def mentors(self) -> int:
        """Meet every mentor on the current island through the roadmap."""
        world = self.state()["world"]
        ids = [
            m["id"]
            for m in self.page.evaluate("window.__debug().mentors")
            if m["world"] == world
        ]
        for i, mid in enumerate(ids):
            self.page.evaluate(f"openMentor('{mid}')")
            self.page.wait_for_selector("#s-mentor.on", state="attached")
            self.page.click(
                "#s-mentor button:has-text('Tell me more')"
                if i % 3 != 2
                else "#s-mentor button:has-text('Not interested')"
            )
            self.page.wait_for_timeout(150)
        self.log.append(f"{world} mentors {len(ids)}")
        return len(ids)

    def finale(self) -> str:
        self.page.evaluate("openCh(9)")
        self.page.wait_for_selector("#s-9.on", state="attached")
        self.page.click("#dates button >> nth=0")
        self.page.click("#wines button >> nth=0")
        self.page.wait_for_timeout(200)
        msg = self.page.text_content("#msg") or ""
        assert "go-live" in msg, "the finale message did not render"
        self.log.append("finale")
        return msg

    def vault(self) -> tuple[int, int]:
        self.page.click("#hud button:has-text('Vault')")
        self.page.wait_for_selector("#vault.on", state="attached")
        self.page.wait_for_timeout(400)
        text = self.page.text_content("#vcount") or ""
        notes, links = (int(s.split()[0]) for s in text.split("·")[:2])
        self.page.click("#vtop button:has-text('Back to campus')")
        self.log.append(f"vault {notes} notes {links} links")
        return notes, links

    def export(self) -> str:
        self.page.click("#hud button:has-text('Roadmap')")
        self.page.wait_for_selector("#s-map.on", state="attached")
        self.page.click("#s-map button:has-text('Export progress')")
        return self.page.input_value("#impcode")


def play_everything(browser: Browser, url: str, *, name: str = "Lotte") -> dict:
    ctx = browser.new_context(viewport={"width": 1280, "height": 800})
    page = ctx.new_page()
    player = Player(page)
    player.attach()
    player.start(url, name)
    mentors = 0
    try:
        for world in WORLDS:
            player.world(world)
            for n in range(1, 9):
                player.stop(n)
            mentors += player.mentors()
        player.world("campus")
        artifacts = player.artifacts()
        msg = player.finale()
        notes, links = player.vault()
        code = player.export()
        state = player.state()
    except Exception as e:  # reason: say where the run got to before re-raising
        raise RuntimeError(
            f"play-through failed after: {player.log[-3:]}; errors: {player.errors}"
        ) from e
    finally:
        ctx.close()
    return {
        "code": code,
        "done": state["doneW"],
        "path": state["path"],
        "mentors": mentors,
        "artifacts": artifacts,
        "notes": notes,
        "links": links,
        "finale": msg[:80],
        "errors": player.errors,
        "log": player.log,
    }


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    name = next(
        (a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--name=")), "Lotte"
    )
    httpd, url = serve()
    with sync_playwright() as p:
        browser = p.chromium.launch(args=CHROMIUM_ARGS)
        if len(args) == 2:
            ctx = browser.new_context(viewport={"width": 1280, "height": 800})
            player = Player(ctx.new_page())
            player.attach()
            player.start(url, name)
            player.world(args[0])
            player.stop(int(args[1]))
            result = {"done": player.state()["doneW"], "errors": player.errors}
        else:
            result = play_everything(browser, url, name=name)
        browser.close()
    httpd.shutdown()
    if "--json" in sys.argv:
        print(json.dumps(result, indent=2))
    else:
        for line in result.get("log", []):
            print(line)
        total = sum(len(v) for v in result["done"].values())
        print(f"stops done: {total}/32, errors: {len(result['errors'])}")
        if "code" in result:
            print(result["code"])
    sys.exit(1 if result["errors"] else 0)


if __name__ == "__main__":
    main()
