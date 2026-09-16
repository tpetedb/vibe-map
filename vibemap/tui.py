"""`just start`: the onboarding terminal.

Three screens: who you are (name, persona, difficulty, provider, theme),
what the machine has (the toolbelt, with one-key installs and a YOLO button
that installs everything missing), and where to go (the game, Claude Code
in this folder, Claude in YOLO mode, Zed with Claude over ACP, the vault in
Obsidian, the tests). Anything that needs the real terminal runs after the
screen closes, never inside it.
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

from vibemap.config import CONFIG_PATH, DIFFICULTIES, Config
from vibemap.palette import BLACK, BLUE, GREEN, MUTED, RED, SURFACE, TEXT, YELLOW
from vibemap.personas import PERSONAS
from vibemap.providers import PROVIDERS
from vibemap.quests import level_for
from vibemap.state import STATE_PATH, State
from vibemap.themes import THEMES
from vibemap.toolbelt import TOOLS, Tool

ROOT = Path(__file__).resolve().parents[1]

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
    "status": ("Campaign status", "uv run vibe status"),
    "quit": ("Quit", ""),
}


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
        if event.button.id and event.button.id.startswith("act-"):
            self.app.exit(event.button.id[4:])


class VibeApp(App[str]):
    TITLE = "Vibe Code Camp"
    SUB_TITLE = "the onboarding terminal"
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
    #welcome, #checks, #launch {{ padding: 0 1; }}
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
