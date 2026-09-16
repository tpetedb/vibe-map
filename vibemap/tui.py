"""`just start`: the onboarding terminal.

Four screens: who you are (name, persona, difficulty, provider, theme),
what the machine has (the toolbelt, with one-key installs and a YOLO button
that installs everything missing), where to go (the game, Claude Code in
this folder, Claude in YOLO mode, Zed with Claude over ACP, the vault in
Obsidian, the tests) and the campaign map (the four-by-eight grid of
workstreams). Anything that needs the real terminal runs after the screen
closes, never inside it.
"""

from __future__ import annotations

import os
import shlex
import subprocess
from pathlib import Path

from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Log,
    Select,
    Static,
)

from vibemap import campaign, pet, project
from vibemap.config import CONFIG_PATH, DIFFICULTIES, Config
from vibemap.palette import BLACK, BLUE, GREEN, MUTED, RED, SURFACE, TEXT, YELLOW
from vibemap.personas import PERSONAS
from vibemap.providers import PROVIDERS
from vibemap.quests import level_for
from vibemap.state import STATE_PATH, State
from vibemap.themes import THEMES
from vibemap.toolbelt import TOOLS, Tool

ROOT = project.root()

BANNER = r"""
 __   _____ ___ ___    ___ ___  ___  ___    ___   _   __  __ ___
 \ \ / /_ _| _ ) __|  / __/ _ \|   \| __|  / __| /_\ |  \/  | _ \
  \ V / | || _ \ _|  | (_| (_) | |) | _|  | (__ / _ \| |\/| |  _/
   \_/ |___|___/___|  \___\___/|___/|___|  \___/_/ \_\_|  |_|_|
"""

ACTIONS: dict[str, tuple[str, str]] = {
    "play": ("Play the game", "open game/vibe-map.html in the browser"),
    "claude": ("Claude Code here", "start claude in this folder"),
    "yolo": ("Claude, YOLO mode", "claude --dangerously-skip-permissions"),
    "zed": ("Zed with Claude over ACP", "zed . then the agent panel, Claude Code"),
    "obsidian": ("Obsidian vault", "open vault/ as a vault"),
    "tests": ("Run the tests", "just test"),
    "map": ("Campaign map", "the four islands and 32 stops, in this screen"),
    "status": ("Campaign status", "uv run vibe status"),
    "quit": ("Quit", ""),
}


class PetWidget(Static):
    """The companion: idles, blinks, strolls the width of its box."""

    def __init__(self, cfg: Config, name: str) -> None:
        super().__init__(markup=False)
        self.pet = pet.resolve(
            name,
            species=cfg.pet.species,
            name=cfg.pet.name,
            eye=cfg.pet.eye,
            hat=cfg.pet.hat,
        )
        self.tick = 0

    def on_mount(self) -> None:
        self.paint()
        self.set_interval(0.5, self.step)

    def step(self) -> None:
        self.tick += 1
        self.paint()

    def paint(self) -> None:
        width = max(pet.WIDTH, self.size.width or 40)
        offset = pet.stroll(self.tick, width)
        self.update(pet.render(self.pet, self.tick, stats=False, offset=offset))


class Welcome(Screen[None]):
    """Who is playing, and how."""

    def __init__(self, cfg: Config, state: State) -> None:
        super().__init__()
        self.cfg = cfg
        self.state = state

    def compose(self) -> ComposeResult:
        lr = self.cfg.learner
        yield Header(show_clock=False)
        with VerticalScroll(id="welcome"):
            yield Static(BANNER, classes="banner")
            yield Static(
                "From intern to expert, one evening at a time. "
                "Pick who you are; every choice lives in vibe.toml "
                "and can change later.",
                classes="lead",
            )
            yield Label("Your name")
            yield Input(value=self.state.name, id="name", placeholder="Lotte")
            yield Label("Your field (persona)")
            yield Select(
                [(f"{p.label}: {p.field}", p.id) for p in PERSONAS.values()],
                value=lr.persona,
                id="persona",
                allow_blank=False,
            )
            yield Label("Difficulty")
            yield Select(
                [(f"{d.label}: {d.blurb}", k) for k, d in DIFFICULTIES.items()],
                value=lr.difficulty,
                id="difficulty",
                allow_blank=False,
            )
            yield Label("Model provider (for explain, council, custom themes)")
            yield Select(
                [
                    (
                        f"{p.label}" + ("" if p.available() else "  (not installed)"),
                        p.id,
                    )
                    for p in PROVIDERS.values()
                ],
                value=lr.provider,
                id="provider",
                allow_blank=False,
            )
            yield Label("Theme")
            yield Select(
                [(t.label, t.id) for t in THEMES.values()],
                value=self.cfg.theme.preset
                if self.cfg.theme.preset in THEMES
                else "wine-night",
                id="theme",
                allow_blank=False,
            )
            with Horizontal(classes="row"):
                yield Button("Continue", id="next", variant="success")
                yield Button("Quit", id="quit", variant="error")
        yield Footer()

    @on(Button.Pressed, "#quit")
    def quit_app(self) -> None:
        self.app.exit("quit")

    @on(Button.Pressed, "#next")
    def save_and_continue(self) -> None:
        data = self.cfg.model_dump()
        data["learner"]["persona"] = self.query_one("#persona", Select).value
        data["learner"]["difficulty"] = self.query_one("#difficulty", Select).value
        data["learner"]["provider"] = self.query_one("#provider", Select).value
        data["theme"]["preset"] = self.query_one("#theme", Select).value
        name = self.query_one("#name", Input).value.strip() or "Lotte"
        data["learner"]["name"] = name
        cfg = Config.model_validate(data)
        app = self.app
        assert isinstance(app, VibeApp)
        cfg.save(app.config_path)
        self.state.name = name
        self.state.save(app.state_path)
        app.push_screen(Checks(cfg, self.state))


class Checks(Screen[None]):
    """What the machine has; install what it lacks."""

    def __init__(self, cfg: Config, state: State) -> None:
        super().__init__()
        self.cfg = cfg
        self.state = state
        self.busy = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Vertical(id="checks"):
            yield Static(
                "The toolbelt. Green is installed. Pick a row and press Install, "
                "install the core, or go YOLO and install everything missing.",
                classes="lead",
            )
            yield DataTable(id="tools", cursor_type="row", zebra_stripes=True)
            with Horizontal(classes="row"):
                yield Button("Install selected", id="one", variant="primary")
                yield Button("Install core", id="core", variant="warning")
                yield Button("YOLO: install everything", id="yolo", variant="error")
                yield Button("Continue", id="next", variant="success")
            yield Log(id="log", auto_scroll=True, max_lines=400)
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#tools", DataTable)
        table.add_columns("tool", "tier", "status", "what")
        self.refresh_rows()

    def refresh_rows(self) -> None:
        table = self.query_one("#tools", DataTable)
        table.clear()
        for t in TOOLS:
            v = t.version()
            status = f"[{GREEN}]{v}[/]" if v else f"[{RED}]missing[/]"
            table.add_row(t.label, t.tier, status, t.what, key=t.id)

    def _selected_tool(self) -> Tool | None:
        table = self.query_one("#tools", DataTable)
        if table.row_count == 0:
            return None
        key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key.value
        return next((t for t in TOOLS if t.id == key), None)

    @on(Button.Pressed, "#one")
    def install_one(self) -> None:
        t = self._selected_tool()
        if t:
            self.run_installs([t])

    @on(Button.Pressed, "#core")
    def install_core(self) -> None:
        self.run_installs(
            [t for t in TOOLS if t.tier == "core" and not t.is_installed()]
        )

    @on(Button.Pressed, "#yolo")
    def install_all(self) -> None:
        self.run_installs([t for t in TOOLS if not t.is_installed()])

    @on(Button.Pressed, "#next")
    def go_on(self) -> None:
        if not self.busy:
            self.app.push_screen(Launch(self.cfg, self.state))

    @work(thread=True, exclusive=True)
    def run_installs(self, tools: list[Tool]) -> None:
        log = self.query_one("#log", Log)
        if not tools:
            self.app.call_from_thread(log.write_line, "nothing to install")
            return
        self.busy = True
        for t in tools:
            self.app.call_from_thread(log.write_line, f"$ {t.install}")
            proc = subprocess.Popen(
                t.install,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            assert proc.stdout is not None
            for line in proc.stdout:
                self.app.call_from_thread(log.write_line, line.rstrip())
            rc = proc.wait()
            self.app.call_from_thread(
                log.write_line, f"{'ok' if rc == 0 else f'exit {rc}'}: {t.label}"
            )
        self.busy = False
        self.app.call_from_thread(self.refresh_rows)


class Launch(Screen[None]):
    """Where to go now."""

    def __init__(self, cfg: Config, state: State) -> None:
        super().__init__()
        self.cfg = cfg
        self.state = state

    def compose(self) -> ComposeResult:
        age, label, nxt = level_for(self.state.xp)
        yield Header(show_clock=False)
        with Vertical(id="launch"):
            yield Static(
                f"{self.state.name}, {PERSONAS[self.cfg.learner.persona].label}, "
                f"{DIFFICULTIES[self.cfg.learner.difficulty].label}. Level {label} "
                f"({age} age), {self.state.xp} XP, {self.state.total_done()}/32 stops.",
                classes="lead",
            )
            if self.cfg.pet.enabled:
                yield PetWidget(self.cfg, self.state.name)
            for key, (title, hint) in ACTIONS.items():
                with Horizontal(classes="action"):
                    yield Button(
                        title,
                        id=f"act-{key}",
                        variant="primary" if key != "quit" else "error",
                    )
                    yield Static(hint, classes="hint")
        yield Footer()

    @on(Button.Pressed)
    def choose(self, event: Button.Pressed) -> None:
        if event.button.id == "act-map":
            self.app.push_screen(Map(self.state))
        elif event.button.id and event.button.id.startswith("act-"):
            self.app.exit(event.button.id[4:])


class Map(Screen[None]):
    """The campaign grid: four evenings, eight stops each, like `vibe status`."""

    def __init__(self, state: State) -> None:
        super().__init__()
        self.state = state

    def _row(self, world: str, ev: campaign.Evening) -> str:
        nxt = next((i for i in range(1, 9) if not self.state.is_done(world, i)), None)
        cells = []
        for i in range(1, 9):
            if self.state.is_done(world, i):
                cells.append(f"[{GREEN}]x[/]")
            elif i == nxt:
                cells.append(f"[{YELLOW}]>[/]")
            else:
                cells.append(f"[{MUTED}].[/]")
        done = len(self.state.done_w.get(world, []))
        label = f"{ev.short} · {ev.island}"
        return f"[{BLUE}]{label:<34}[/] " + " ".join(cells) + f"  [{MUTED}]{done}/8[/]"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Vertical(id="map"):
            yield Static(
                f"{self.state.total_done()}/32 stops, {self.state.xp} XP. "
                "Each row is an island; each cell is a workstream.",
                classes="lead",
            )
            for world, ev in campaign.evenings().items():
                yield Static(self._row(world, ev), classes="maprow", markup=True)
            yield Static(
                f"[{GREEN}]x[/] done   [{YELLOW}]>[/] next   [{MUTED}].[/] to do",
                classes="legend",
                markup=True,
            )
            with Horizontal(classes="row"):
                yield Button("Back", id="back", variant="primary")
        yield Footer()

    @on(Button.Pressed, "#back")
    def back(self) -> None:
        self.app.pop_screen()


class VibeApp(App[str]):
    TITLE = "Vibe Code Camp: the onboarding terminal"
    SUB_TITLE = ""
    CSS = f"""
    Screen {{ background: {BLACK}; color: {TEXT}; }}
    Header {{ background: {BLACK}; color: {YELLOW}; }}
    Footer {{ background: {SURFACE}; }}
    .banner {{ color: {YELLOW}; text-style: bold; margin: 0 1; }}
    .lead {{ color: {MUTED}; margin: 0 1 1 1; }}
    Label {{ color: {BLUE}; margin: 1 1 0 1; text-style: bold; }}
    Input, Select {{ margin: 0 1; }}
    .row {{ height: auto; margin: 1 1; }}
    .row Button {{ margin: 0 1 0 0; }}
    .action {{ height: 3; margin: 0 1; }}
    .action Button {{ width: 34; margin: 0 2 0 0; }}
    .hint {{ color: {MUTED}; padding: 1 0; }}
    DataTable {{ height: 1fr; margin: 0 1; border: round {GREEN}; }}
    Log {{ height: 10; margin: 0 1; border: round {BLUE}; }}
    #welcome, #checks, #launch, #map {{ padding: 0 1; }}
    .maprow {{ margin: 0 1; }}
    PetWidget {{ height: 8; width: 60; margin: 0 1 1 1; }}
    .legend {{ color: {MUTED}; margin: 1 1 0 1; }}
    """

    def __init__(
        self, *, config_path: Path = CONFIG_PATH, state_path: Path = STATE_PATH
    ) -> None:
        super().__init__()
        self.config_path = config_path
        self.state_path = state_path
        self.cfg = Config.load(config_path)
        self.state = State.load(state_path)

    def on_mount(self) -> None:
        self.push_screen(Welcome(self.cfg, self.state))


def run() -> None:
    """Run the screens, then act on the choice in the real terminal."""
    choice = VibeApp().run() or "quit"
    if choice == "quit":
        return
    if choice == "play":
        subprocess.run(["open", str(ROOT / "game" / "vibe-map.html")])
    elif choice == "claude":
        os.execvp("claude", ["claude"])
    elif choice == "yolo":
        os.execvp("claude", ["claude", "--dangerously-skip-permissions"])
    elif choice == "zed":
        subprocess.run(["zed", str(ROOT)])
        print(
            "Zed is opening. Open the agent panel (cmd-? or the sparkle icon), "
            "pick Claude Code from the plus menu, and sign in with /login."
        )
    elif choice == "obsidian":
        subprocess.run(["open", "-a", "Obsidian", str(ROOT / "vault")])
        print("Obsidian: Manage vaults, Open folder as vault, pick vault/.")
    elif choice == "tests":
        os.execvp("just", ["just", "test"])
    elif choice == "status":
        os.execvp("uv", ["uv", "run", "--no-sync", "vibe", "status"])
    else:
        print(f"unknown choice {shlex.quote(choice)}")


if __name__ == "__main__":
    run()
