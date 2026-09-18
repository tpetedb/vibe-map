"""Build game/vibe-map.html from src/.

The game ships as one file with three.js embedded and no CDN. src/ holds the
parts in load order: src/config/ first (the source configuration a fork
edits), then the game modules. This script concatenates them and injects the
generated data (campaign JSON, tech notes, tech tree) and the journey values
from config/camp.toml that the game exposes as CONFIG. Concatenation is the
whole build: no bundler, no minifier, so the output stays readable.

Every input is resolved relative to the folder holding tools/build.py, so a
copy of src/ and this file in workspace/forks/ builds on its own (`vibe fork`).

    uv run python tools/build.py             write game/vibe-map.html
    uv run python tools/build.py --check     exit 1 if the file differs
    uv run python tools/build.py --root DIR  build the fork in DIR
"""

from __future__ import annotations

import functools
import importlib.util
import json
import os
import shutil
import sys
import tomllib
from pathlib import Path


def _root(argv: list[str] | None = None) -> Path:
    """Where to build: --root DIR, else the folder holding this file's tools/."""
    args = list(argv if argv is not None else sys.argv[1:])
    if "--root" in args:
        return Path(args[args.index("--root") + 1]).expanduser().resolve()
    return Path(__file__).resolve().parents[1]


ROOT = _root()
SRC = ROOT / "src"
OUT = ROOT / "game" / "vibe-map.html"
GENERATED = ROOT / "tools" / "generated"
CONFIG_DIR = SRC / "config"

# Game modules in load order. The state module must come first (S, save,
# load) and boot last (it reads localStorage and paints the title screen).
GAME_ORDER = [
    "@config",  # CONFIG, NEWS and src/config/*.js
    "00-state.js",
    "05-icons.js",
    "10-scene.js",
    "11-character.js",
    "12-buildings.js",
    "@campaign",
    "16-artifacts.js",
    "17-artifact-props.js",
    "20-worlds.js",
    "21-world-build.js",
    "30-input.js",
    "31-animate.js",
    "40-sheet.js",
    "@notes",
    "51-notes-dynamic.js",
    "@tree",
    "60-vault.js",
    "70-minigames.js",
    "71-finale.js",
    "80-sync.js",
    "85-settings.js",
    "87-onboarding.js",
    "88-chat.js",
    "89-dashboard.js",
    "90-boot.js",
]


def _read(rel: str) -> str:
    return (SRC / rel).read_text(encoding="utf-8")


def _config_modules() -> str:
    """src/config/*.js: the source configuration, in name order, first."""
    return "".join(
        f.read_text(encoding="utf-8") for f in sorted(CONFIG_DIR.glob("*.js"))
    )


def _campaign_js() -> str:
    """The campaign a fork carries, else the one inside the installed package."""
    sys.path.insert(0, str(ROOT))
    local = GENERATED / "campaign.json"
    if local.exists():
        data = json.loads(local.read_text(encoding="utf-8"))
    else:
        from vibemap.project import data_text  # noqa: PLC0415

        data = json.loads(data_text("campaign.json"))
    dump = functools.partial(json.dumps, ensure_ascii=False)
    return (
        "const CAMPAIGN=" + dump(data["evenings"]) + ";\n"
        "const MENTORS=" + dump(data["mentors"]) + ";\n"
        "const ARTIFACTS=" + dump(data.get("artifacts", [])) + ";\n"
    )


def _notes_js() -> str:
    generated = (GENERATED / "notes.js").read_text(encoding="utf-8")
    return "const NOTES={\n" + generated + ",\n" + _read("game/50-notes.js")


def _tree_js() -> str:
    return (GENERATED / "tree.js").read_text(encoding="utf-8").rstrip("\n") + "\n"


def _news_js() -> str:
    """data/news.json, embedded so a file:// game shows it without a fetch."""
    p = ROOT / "data" / "news.json"
    data = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    items = [
        {k: it.get(k, "") for k in ("source", "title", "link", "date")}
        for it in data.get("items", [])[:20]
    ]
    payload = {"fetched_at": data.get("fetched_at", ""), "items": items}
    return "const NEWS=" + json.dumps(payload, ensure_ascii=False) + ";\n"


def _version() -> str:
    """The product version: this checkout's pyproject, else the installed package."""
    pyproject = ROOT / "pyproject.toml"
    if pyproject.exists():
        return tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"][
            "version"
        ]
    from vibemap import __version__  # noqa: PLC0415

    return __version__


def _config_js() -> str:
    """The journey values (config/camp.toml) the game exposes as a constant."""
    sys.path.insert(0, str(ROOT))
    from vibemap import project  # noqa: PLC0415
    from vibemap.config import Config  # noqa: PLC0415
    from vibemap.themes import load_theme, theme_for_game  # noqa: PLC0415

    cfg = Config.load(project.nearest_config(ROOT))
    version = _version()
    theme = theme_for_game(
        load_theme(cfg.theme.preset), show_pairings=cfg.game.show_pairings
    )
    data = {
        "version": version,
        "theme": theme,
        "dates": cfg.finale.dates,
        "repo": cfg.game.repo_url,
        "shadowMap": cfg.game.shadow_map,
        "difficulty": cfg.learner.difficulty,
        "persona": cfg.learner.persona,
        "provider": cfg.learner.provider,
        "mode": cfg.learner.mode,
        "vault": {"mode": cfg.vault.mode},
    }
    return "const CONFIG=" + json.dumps(data, ensure_ascii=False) + ";\n"


def _game_script() -> str:
    parts = []
    for name in GAME_ORDER:
        if name == "@config":
            parts.append(_config_js())
            parts.append(_news_js())
            parts.append(_config_modules())
        elif name == "@campaign":
            parts.append(_campaign_js())
        elif name == "@notes":
            parts.append(_notes_js())
        elif name == "@tree":
            parts.append(_tree_js())
        else:
            parts.append(_read("game/" + name))
    return "(function(){\n" + "".join(parts) + "})();\n"


def build() -> str:
    """Return the full HTML document as a string."""
    return (
        _read("head.html")
        + "<style>\n"
        + _read("style.css")
        + "</style>\n</head>\n"
        + _read("body.html")
        + "<script>"
        + _read("errors.js").rstrip("\n")
        + "</script>\n"
        + "<script>\n"
        + _read("vendor/three.min.js")
        + "</script>\n"
        # Motion (MIT, https://motion.dev) is optional: the game checks for
        # window.Motion and degrades to instant transitions without it.
        + "<script>\n"
        + "/* motion 12.43.0, MIT, https://github.com/motiondivision/motion */\n"
        + _read("vendor/motion.min.js").rstrip("\n")
        + "\n</script>\n"
        # d3-force (ISC) runs the vault graph: a simulation that cools
        # and stops, the same physics as Obsidian's graph view.
        + "<script>\n"
        + _read("vendor/d3-force.min.js").rstrip("\n")
        + "\n</script>\n"
        + "<script>\n"
        + _game_script()
        + "</script>\n</body>\n</html>"
    )


# The re-exec below runs this file again; the flag stops a second round.
REEXEC_FLAG = "VIBE_BUILD_REEXEC"


def _vibe_interpreter() -> str | None:
    """The python behind the `vibe` on PATH, from its console script shebang."""
    exe = shutil.which("vibe")
    if not exe:
        return None
    try:
        first = Path(exe).read_text(encoding="utf-8", errors="ignore").splitlines()[0]
    except (OSError, IndexError):
        return None
    py = first[2:].strip().strip('"') if first.startswith("#!") else ""
    if not py:
        py = str(Path(exe).resolve().parent / "python")
    return py if Path(py).exists() else None


def _hand_over_to_vibe() -> None:
    """A fork is built by a plain python3, which has no vibemap; borrow one.

    The build reads the camp's journey configuration through the package, and
    the only copy in a camp lives in the virtualenv of the installed `vibe`.
    A product checkout has a pyproject.toml and never takes this path.
    """
    if (ROOT / "pyproject.toml").exists() or importlib.util.find_spec("vibemap"):
        return
    py = None if os.environ.get(REEXEC_FLAG) else _vibe_interpreter()
    if not py:
        raise SystemExit(
            "this build needs the vibe package. Install it with "
            "`uv tool install vibe-map`, or run it with the python that has it."
        )
    os.environ[REEXEC_FLAG] = "1"
    os.execv(py, [py, str(Path(__file__).resolve()), *sys.argv[1:]])


def main() -> None:
    _hand_over_to_vibe()
    html = build()
    if "--check" in sys.argv:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != html:
            print(
                "game/vibe-map.html differs from a fresh build of src/; run: just build"
            )
            sys.exit(1)
        print("build OK: game/vibe-map.html matches src/")
        return
    OUT.write_text(html, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(html.encode()) // 1024} KB)")


if __name__ == "__main__":
    main()
