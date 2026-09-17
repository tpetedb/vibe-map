"""Terminal setup modules: the configs from Tom's toolbox, installable at will.

Each module is a few files from ``vibemap/data/dotfiles/`` (adapted from
https://github.com/tpetedb/toms-toolbox, MIT) that land in the learner's home
or vault: the zsh snippet with fzf and the three plugins, the tmux bar, the
Ghostty theme, the Starship prompt, the R2-D2 Obsidian theme, AeroSpace.
Installs never destroy anything: an existing target that differs is copied to
``<name>.bak-<stamp>`` first, and the zsh module only appends one ``source``
line to ``~/.zshrc``.
"""

from __future__ import annotations

import filecmp
import os
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from importlib import resources
from pathlib import Path

ZSH_LINE = 'source "$HOME/.config/vibe/vibe.zsh"  # Vibe Code Camp terminal setup'


@dataclass(frozen=True, slots=True)
class Module:
    """One installable configuration.

    Attributes:
        id: Lowercase identifier used on the command line.
        name: Display name.
        what: What it gives you, in one or two sentences.
        files: ``(package path under data/dotfiles, target)`` pairs; targets
            start with ``~`` for the home folder or ``vault:`` for the vault.
        brew: Homebrew formulae and casks the module expects.
        after: What to do once the files are in place.
        docs: The upstream documentation.
        append: ``(target, line)`` appended once, for the shell rc file.
    """

    id: str
    name: str
    what: str
    files: tuple[tuple[str, str], ...]
    brew: tuple[str, ...] = ()
    after: str = ""
    docs: str = ""
    append: tuple[str, str] | None = None
    macos_only: bool = False


MODULES: dict[str, Module] = {
    "zsh": Module(
        "zsh",
        "zsh: completion, fzf, highlighting",
        "A live completion dropdown, grey history suggestions, command colouring in the palette, fzf on ctrl-r and ctrl-t, big shared history, a tmux picker (tj). One source line in ~/.zshrc; nothing needs oh-my-zsh.",
        (("zsh/vibe.zsh", "~/.config/vibe/vibe.zsh"),),
        brew=(
            "fzf",
            "zsh-autosuggestions",
            "zsh-syntax-highlighting",
            "zsh-autocomplete",
        ),
        after="Open a new terminal, type two letters and watch the dropdown; ctrl-r searches history.",
        docs="https://github.com/marlonrichert/zsh-autocomplete",
        append=("~/.zshrc", ZSH_LINE),
    ),
    "tmux": Module(
        "tmux",
        "tmux: the bottom bar and j/k/i/l panes",
        "True colour, the mouse, windows from 1, a status bar in the palette (session, path, clock, host), panes on j/k/i/l like AeroSpace, prefix r to reload. Prefix stays Ctrl-b.",
        (("tmux/tmux.conf", "~/.config/tmux/tmux.conf"),),
        brew=("tmux",),
        after="Run tmux; prefix | splits right, prefix - splits down, prefix j/k/i/l moves.",
        docs="https://github.com/tmux/tmux/wiki",
    ),
    "ghostty": Module(
        "ghostty",
        "Ghostty: the R2-D2 terminal theme",
        "OLED black with the five hues as the ANSI palette, MesloLGS Nerd Font, a blinking block cursor, a little blur and padding. Ghostty reloads the config on save.",
        (
            ("ghostty/config", "~/.config/ghostty/config"),
            (
                "ghostty/themes/r2d2-high-contrast",
                "~/.config/ghostty/themes/r2d2-high-contrast",
            ),
        ),
        brew=("--cask ghostty", "--cask font-meslo-lg-nerd-font"),
        after="Open Ghostty (or cmd-shift-, to reload). Yellow cursor, green commands, black glass.",
        docs="https://ghostty.org/docs/config/reference",
        macos_only=True,
    ),
    "starship": Module(
        "starship",
        "Starship: the prompt",
        "A one-line prompt: (venv), the full path in blue, the branch in yellow, the time on the right in red, a green dollar when the last command passed and a red one when it did not. Colours are ANSI names so they follow the terminal theme.",
        (("starship/starship.toml", "~/.config/starship.toml"),),
        brew=("starship",),
        after='The zsh module starts it; otherwise add eval "$(starship init zsh)" to ~/.zshrc.',
        docs="https://starship.rs/config/",
    ),
    "obsidian-theme": Module(
        "obsidian-theme",
        "Obsidian: the R2-D2 theme",
        "Tom's own Obsidian theme: black canvas, folders orange, code blue, config files yellow, data and media green, heavy documents red, callouts in the same hues. Installed into this vault; pick it under Settings, Appearance, Themes.",
        (
            ("obsidian/R2-D2/theme.css", "vault:.obsidian/themes/R2-D2/theme.css"),
            (
                "obsidian/R2-D2/manifest.json",
                "vault:.obsidian/themes/R2-D2/manifest.json",
            ),
        ),
        after="Settings, Appearance, Themes, pick R2-D2. The file explorer colours by file kind.",
        docs="https://help.obsidian.md/Extending+Obsidian/Themes",
    ),
    "aerospace": Module(
        "aerospace",
        "AeroSpace: tiling windows",
        "Windows tile by themselves; alt-j/k/i/l focuses left, down, up, right, alt-shift moves, alt plus a letter switches workspace. The same directions as the tmux panes.",
        (("aerospace/aerospace.toml", "~/.aerospace.toml"),),
        brew=("--cask nikitabobko/tap/aerospace",),
        after="Start AeroSpace; alt-t is a workspace called T, alt-shift-semicolon then esc reloads.",
        docs="https://nikitabobko.github.io/AeroSpace/guide",
        macos_only=True,
    ),
}


def get_module(module_id: str) -> Module:
    try:
        return MODULES[module_id]
    except KeyError:
        raise ValueError(
            f"unknown module {module_id!r}; one of: {', '.join(MODULES)}"
        ) from None


def source_text(rel: str) -> str:
    return (
        resources.files("vibemap")
        .joinpath("data", "dotfiles", *rel.split("/"))
        .read_text(encoding="utf-8")
    )


def resolve(target: str, *, home: Path, vault: Path) -> Path:
    if target.startswith("vault:"):
        return vault / target[6:]
    if target.startswith("~/"):
        return home / target[2:]
    return Path(target)


def is_installed(m: Module, *, home: Path, vault: Path) -> bool:
    """True when every file is in place and identical, and the rc line exists."""
    for rel, target in m.files:
        p = resolve(target, home=home, vault=vault)
        if not p.exists() or p.read_text(encoding="utf-8") != source_text(rel):
            return False
    if m.append:
        rc = resolve(m.append[0], home=home, vault=vault)
        if not rc.exists() or m.append[1] not in rc.read_text(encoding="utf-8"):
            return False
    return True


@dataclass(slots=True)
class Plan:
    """What an install would do, so `--dry-run` can print it."""

    writes: list[tuple[Path, bool]] = field(default_factory=list)  # (path, backup)
    appends: list[Path] = field(default_factory=list)
    skipped: list[Path] = field(default_factory=list)


def plan(m: Module, *, home: Path, vault: Path, force: bool = False) -> Plan:
    out = Plan()
    for rel, target in m.files:
        p = resolve(target, home=home, vault=vault)
        if p.exists():
            if p.read_text(encoding="utf-8") == source_text(rel):
                out.skipped.append(p)
                continue
            out.writes.append((p, True))
        else:
            out.writes.append((p, False))
    if m.append:
        rc = resolve(m.append[0], home=home, vault=vault)
        if not rc.exists() or m.append[1] not in rc.read_text(encoding="utf-8"):
            out.appends.append(rc)
    return out


def install(m: Module, *, home: Path, vault: Path, dry_run: bool = False) -> Plan:
    """Write the module's files with backups; append the rc line once."""
    p = plan(m, home=home, vault=vault)
    if dry_run:
        return p
    stamp = datetime.now().strftime("%Y%m%d%H%M")
    for target, backup in p.writes:
        target.parent.mkdir(parents=True, exist_ok=True)
        if backup:
            shutil.copy2(target, target.with_name(f"{target.name}.bak-{stamp}"))
        rel = next(
            r for r, t in m.files if resolve(t, home=home, vault=vault) == target
        )
        target.write_text(source_text(rel), encoding="utf-8")
    for rc in p.appends:
        rc.parent.mkdir(parents=True, exist_ok=True)
        existing = rc.read_text(encoding="utf-8") if rc.exists() else ""
        sep = "" if not existing or existing.endswith("\n") else "\n"
        rc.write_text(existing + sep + m.append[1] + "\n", encoding="utf-8")  # type: ignore[index]
    return p


def brew_command(m: Module) -> str:
    return "brew install " + " ".join(m.brew) if m.brew else ""


def same(a: Path, b: Path) -> bool:
    return a.exists() and b.exists() and filecmp.cmp(a, b, shallow=False)


def default_home() -> Path:
    return Path(os.environ.get("VIBE_HOME_DIR", str(Path.home())))
