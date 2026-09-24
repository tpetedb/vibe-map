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
import sys
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

from vibemap import campaign, dotfiles, pet, project
from vibemap.config import CONFIG_PATH, DIFFICULTIES, Config
from vibemap.palette import (
    BLACK,
    BLUE,
    GREEN,
    MUTED,
    ORANGE,
    RED,
    SURFACE,
    TEXT,
    YELLOW,
)
from vibemap.personas import PERSONAS
from vibemap.providers import PROVIDERS
from vibemap.quests import level_for
from vibemap.state import PLACEHOLDER, STATE_PATH, State
from vibemap.themes import THEMES, load_theme
from vibemap.toolbelt import TOOLS, Tool

ROOT = project.root()


def progress_line(state: State) -> str:
    """The one progress sentence both screens show, from state alone."""
    return (
        f"{state.total_done()}/{campaign.total_stops()} stops, "
        f"{len(state.mentors)}/{len(campaign.mentors())} mentors verified, "
        f"{len(state.artifacts_built)}/{len(campaign.artifacts())} "
        "artifacts built for real"
    )


def has_engine() -> bool:
    """True in the product checkout, where the game can be rebuilt."""
    return (ROOT / "tools" / "build.py").exists()


# The stops that teach permissions; YOLO mode skips every prompt they explain.
PERMISSION_STOPS = (("desert", 4), ("prod", 5))


def knows_permissions(state: State) -> bool:
    """True once the learner has done every stop that teaches permissions."""
    return all(state.is_done(world, n) for world, n in PERMISSION_STOPS)


def yolo_locked_hint() -> str:
    """Why YOLO mode is greyed out, naming the lessons that open it."""
    evs = campaign.evenings()
    lessons = " and ".join(
        f"{evs[w].workstreams[n - 1].name} ({evs[w].short}, stop {n})"
        for w, n in PERMISSION_STOPS
    )
    return f"skips every permission prompt; opens once you have done {lessons}"


def launchers(state: State) -> list[tuple[str, str, str, bool]]:
    """(key, title, hint, disabled) for the launch screen, camp or product."""
    engine = has_engine()
    locked = not knows_permissions(state)
    rows = []
    for key, (title, hint) in ACTIONS.items():
        off = key in ENGINE_ONLY and not engine
        if off:
            hint = NO_ENGINE
        if key == "yolo" and locked:
            hint, off = yolo_locked_hint(), True
        rows.append((key, title, hint, off))
    return rows


BANNER = r"""
 __   _____ ___ ___    ___ ___  ___  ___    ___   _   __  __ ___
 \ \ / /_ _| _ ) __|  / __/ _ \|   \| __|  / __| /_\ |  \/  | _ \
  \ V / | || _ \ _|  | (_| (_) | |) | _|  | (__ / _ \| |\/| |  _/
   \_/ |___|___/___|  \___\___/|___/|___|  \___/_/ \_\_|  |_|_|
"""

# Stops that need the engine's own repository; a camp has no tools/build.py.
ENGINE_ONLY = ("tests",)
NO_ENGINE = "the engine lives in the product repository; a camp has no build"

ACTIONS: dict[str, tuple[str, str]] = {
    "play": ("Play the game", "the local build, the cached copy, else the hosted one"),
    "claude": ("Claude Code here", "start claude in this folder"),
    "yolo": ("Claude, YOLO mode", "claude --dangerously-skip-permissions"),
    "zed": ("Zed with Claude over ACP", "zed . then the agent panel, Claude Code"),
    "obsidian": ("Obsidian vault", "open the camp's vault folder as a vault"),
    "tests": ("Run the tests", "just test"),
    "map": ("Campaign map", "the four islands and 32 stops, in this screen"),
    "dotfiles": ("Terminal setup", "zsh, tmux, Ghostty, Starship, the R2-D2 themes"),
    "status": ("Campaign status", "vibe status: stops, XP and what comes next"),
    "news": ("Pull the world feed", "vibe news: the sources into the vault note News"),
    "quit": ("Quit", ""),
}


def theme_options(preset: str) -> list[tuple[str, str]]:
    """The presets, and the camp's own theme when it named one of its own.

    A name that is not a preset is a themes/<name>.toml file, or a typo; either
    way the select offers it, so pressing Continue cannot quietly replace it.
    """
    options = [(t.label, t.id) for t in THEMES.values()]
    if preset not in THEMES:
        try:
            options.append((f"{load_theme(preset).label} (your own)", preset))
        except ValueError:
            options.append((f"{preset} (not a preset, not in themes/)", preset))
    return options


# Ticks the pet spends being pleased to see you before it settles.
GREETING = 8


class PetWidget(Static):
    """The companion: greets, idles, blinks, strolls the width of its box."""

    def __init__(self, cfg: Config, name: str) -> None:
        super().__init__(markup=False)
        self.pet = pet.resolve(
            name,
            species=cfg.pet.species,
            name=cfg.pet.name,
            eye=cfg.pet.eye,
            hat=cfg.pet.hat,
        )
        # Textual renders truecolor itself, so the config decides and `auto`
        # means pixels wherever the species has them.
        self.pet_style = "pixel" if cfg.pet.style == "auto" else cfg.pet.style
        self.pet_width = pet.columns(self.pet, self.pet_style)
        self.tick = 0

    def on_mount(self) -> None:
        self.paint()
        # Eight frames a second for the sprites, half a second for the art.
        self.set_interval(0.125 if self.pet_width > pet.WIDTH else 0.5, self.step)

    def step(self) -> None:
        self.tick += 1
        self.paint()

    def state_now(self, width: int) -> str:
        """A hello when the screen opens, then walking or idling."""
        if self.tick < GREETING:
            return "happy"
        return pet.gait(self.tick, width, sprite_width=self.pet_width)

    def paint(self) -> None:
        width = max(self.pet_width, self.size.width or 40)
        offset = pet.stroll(self.tick, width, sprite_width=self.pet_width)
        self.update(
            pet.render(
                self.pet,
                self.tick,
                stats=False,
                offset=offset,
                style=self.pet_style,
                state=self.state_now(width),
            )
        )


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
                "Pick who you are; every choice lives in config/camp.toml "
                "and can change later.",
                classes="lead",
            )
            yield Label("Your name (type it plainly, no angle brackets)")
            yield Input(
                value="" if self.state.name == PLACEHOLDER else self.state.name,
                id="name",
                placeholder=PLACEHOLDER,
            )
            yield Static("", id="nameproblem", classes="problem")
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
            yield Label("Vault")
            yield Select(
                [
                    ("Full from day one: every note in the graph", "full"),
                    ("Grows as you play: notes unlock stop by stop", "grow"),
                ],
                value=self.cfg.vault.mode,
                id="vaultmode",
                allow_blank=False,
            )
            yield Label("Theme")
            yield Select(
                theme_options(self.cfg.theme.preset),
                value=self.cfg.theme.preset,
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

    @on(Input.Submitted, "#name")
    def submit_name(self) -> None:
        """Enter in the last field is Continue, as in any other form."""
        self.save_and_continue()

    @on(Button.Pressed, "#next")
    def save_and_continue(self) -> None:
        name = self.query_one("#name", Input).value.strip()
        if not name:
            # The placeholder is the state's word for "nobody has said yet";
            # storing it would greet the learner by it on the next screen.
            problem = self.query_one("#nameproblem", Static)
            problem.update(
                "Type your name first. It goes in camp.toml and can change "
                "later with vibe name."
            )
            problem.display = True
            self.set_focus(self.query_one("#name", Input))
            return
        data = self.cfg.model_dump()
        data["learner"]["persona"] = self.query_one("#persona", Select).value
        data["learner"]["difficulty"] = self.query_one("#difficulty", Select).value
        data["learner"]["provider"] = self.query_one("#provider", Select).value
        data["theme"]["preset"] = self.query_one("#theme", Select).value
        data["vault"]["mode"] = self.query_one("#vaultmode", Select).value
        data["learner"]["name"] = name
        cfg = Config.model_validate(data)
        app = self.app
        assert isinstance(app, VibeApp)
        cfg.save(app.config_path)
        # The app carries the config the learner just saved; the launchers
        # read it after the screens close.
        app.cfg = cfg
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
        with VerticalScroll(id="launch"):
            yield Static(
                f"{self.state.name}, {PERSONAS[self.cfg.learner.persona].label}, "
                f"{DIFFICULTIES[self.cfg.learner.difficulty].label}. Level {label} "
                f"({age} age), {self.state.xp} XP, {progress_line(self.state)}.",
                classes="lead",
            )
            if self.cfg.pet.enabled:
                yield PetWidget(self.cfg, self.state.name)
            for key, title, hint, disabled in launchers(self.state):
                with Horizontal(classes="action"):
                    yield Button(
                        title,
                        id=f"act-{key}",
                        disabled=disabled,
                        variant="primary" if key != "quit" else "error",
                    )
                    yield Static(hint, classes="hint")
        yield Footer()

    @on(Button.Pressed)
    def choose(self, event: Button.Pressed) -> None:
        if event.button.id == "act-map":
            self.app.push_screen(Map(self.state))
        elif event.button.id == "act-dotfiles":
            self.app.push_screen(Dotfiles(self.cfg))
        elif event.button.id and event.button.id.startswith("act-"):
            self.app.exit(event.button.id[4:])


# The grid's four marks in the app's colours; the marks live in campaign.MARKS.
MARK_COLOURS = {"done": GREEN, "claimed": ORANGE, "next": YELLOW, "todo": MUTED}


class Map(Screen[None]):
    """The campaign grid: four evenings, eight stops each, like `vibe status`."""

    def __init__(self, state: State) -> None:
        super().__init__()
        self.state = state

    def _cell(self, mark: str) -> str:
        """One square, in the same language as the grid of `vibe status`."""
        glyph, _ = campaign.MARKS[mark]
        return f"[{MARK_COLOURS[mark]}]{glyph}[/]"

    def _row(self, world: str, ev: campaign.Evening) -> str:
        cells = [self._cell(m) for m in campaign.stop_marks(self.state, world)]
        done = len(self.state.done_w.get(world, []))
        label = f"{ev.short} · {ev.island}"
        return (
            f"[{BLUE}]{label:<34}[/] "
            + " ".join(cells)
            + f"  [{MUTED}]{done}/{campaign.stop_count(world)}[/]"
        )

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Vertical(id="map"):
            yield Static(
                f"{progress_line(self.state)}, {self.state.xp} XP. "
                "Each row is an island; each cell is a workstream.",
                classes="lead",
            )
            for world, ev in campaign.evenings().items():
                yield Static(self._row(world, ev), classes="maprow", markup=True)
            yield Static(
                "   ".join(
                    f"{self._cell(m)} {meaning}"
                    for m, (_, meaning) in campaign.MARKS.items()
                ),
                classes="legend",
                markup=True,
            )
            with Horizontal(classes="row"):
                yield Button("Back", id="back", variant="primary")
        yield Footer()

    @on(Button.Pressed, "#back")
    def back(self) -> None:
        self.app.pop_screen()


class Dotfiles(Screen[None]):
    """Tom's terminal setup, one Install button per module."""

    def __init__(self, cfg: Config) -> None:
        super().__init__()
        self.cfg = cfg
        self.home = dotfiles.default_home()
        self.vault = ROOT / cfg.vault.path

    def _state(self, m: dotfiles.Module) -> str:
        return (
            "installed"
            if dotfiles.is_installed(m, home=self.home, vault=self.vault)
            else "not yet"
        )

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with VerticalScroll(id="dotfiles"):
            yield Static(
                "Configs adapted from Tom's toolbox (MIT). Install writes the files "
                "with a backup of anything that differs; the zsh module adds one "
                "source line to ~/.zshrc. Homebrew deps are printed, not run.",
                classes="lead",
            )
            for m in dotfiles.MODULES.values():
                with Horizontal(classes="action"):
                    yield Button(
                        f"Install {m.id}",
                        id=f"dot-{m.id}",
                        variant="success"
                        if self._state(m) == "installed"
                        else "primary",
                    )
                    yield Static(
                        f"{m.name}: {self._state(m)}",
                        id=f"dothint-{m.id}",
                        classes="hint",
                    )
            yield Log(id="dotlog")
            with Horizontal(classes="row"):
                yield Button("Back", id="back", variant="primary")
        yield Footer()

    @on(Button.Pressed)
    def act(self, event: Button.Pressed) -> None:
        bid = event.button.id or ""
        if bid == "back":
            self.app.pop_screen()
            return
        if not bid.startswith("dot-"):
            return
        m = dotfiles.get_module(bid[4:])
        log = self.query_one("#dotlog", Log)
        if m.macos_only and os.uname().sysname != "Darwin":
            log.write_line(f"{m.id}: macOS only, skipped")
            return
        plan = dotfiles.install(m, home=self.home, vault=self.vault)
        for target, backup in plan.writes:
            log.write_line(f"wrote {target}" + ("  (backup kept)" if backup else ""))
        for rc in plan.appends:
            log.write_line(f"appended one line to {rc}")
        if not plan.writes and not plan.appends:
            log.write_line(f"{m.id}: already in place")
        if m.brew:
            log.write_line(f"deps: {dotfiles.brew_command(m)}")
        log.write_line(m.after)
        self.refresh_rows()

    def refresh_rows(self) -> None:
        """Every row says what the disk says, after an install as before it."""
        for m in dotfiles.MODULES.values():
            installed = self._state(m) == "installed"
            self.query_one(f"#dothint-{m.id}", Static).update(
                f"{m.name}: {self._state(m)}"
            )
            self.query_one(f"#dot-{m.id}", Button).variant = (
                "success" if installed else "primary"
            )


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
    .action {{ height: auto; margin: 0 1; }}
    .action Button {{ width: 34; margin: 0 2 0 0; }}
    .hint {{ color: {MUTED}; width: 1fr; padding: 1 0; }}
    .problem {{ color: {RED}; margin: 0 1; display: none; }}
    DataTable {{ height: 1fr; min-height: 10; margin: 0 1; border: round {GREEN}; }}
    Log {{ height: 6; margin: 0 1; border: round {BLUE}; }}
    #welcome, #checks, #launch, #map, #dotfiles {{ padding: 0 1; }}
    #dotfiles .action Button {{ width: 26; }}
    #dotlog {{ height: 8; }}
    .maprow {{ margin: 0 1; }}
    PetWidget {{ height: auto; width: 60; margin: 0 1 1 1; }}
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
    app = VibeApp()
    choice = app.run() or "quit"
    if choice == "quit":
        return
    if choice == "play":
        from vibemap.cli import open_game  # local: the CLI owns how to open it

        open_game()
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
        vault = app.cfg.vault.path
        subprocess.run(["open", "-a", "Obsidian", str(ROOT / vault)])
        print(f"Obsidian: Manage vaults, Open folder as vault, pick {vault}/.")
    elif choice == "tests":
        os.execvp("just", ["just", "test"])
    elif choice == "status":
        # This interpreter already has the CLI; `uv run` in a camp without a
        # project only earns a warning.
        os.execvp(sys.executable, [sys.executable, "-m", "vibemap.cli", "status"])
    elif choice == "news":
        os.execvp(sys.executable, [sys.executable, "-m", "vibemap.cli", "news"])
    else:
        print(f"unknown choice {shlex.quote(choice)}")


if __name__ == "__main__":
    run()
