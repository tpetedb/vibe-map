"""Build game/grimoire.html from src/.

The game ships as one file with three.js embedded and no CDN. src/ holds the
parts in load order; this script concatenates them and injects the generated
data (campaign JSON, tech notes, tech tree) and the values from grimoire.toml
that the game exposes as constants. Concatenation is the whole build: no
bundler, no minifier, so the output stays readable and diffable.

    uv run python tools/build.py           write game/grimoire.html
    uv run python tools/build.py --check   exit 1 if the file differs from a fresh build
"""

from __future__ import annotations

import functools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
OUT = ROOT / "game" / "grimoire.html"
GENERATED = ROOT / "tools" / "generated"

# Game modules in load order. The state module must come first (S, save,
# load) and boot last (it reads localStorage and paints the title screen).
GAME_ORDER = [
    "00-state.js",
    "10-scene.js",
    "11-character.js",
    "12-buildings.js",
    "@campaign",
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
    "90-boot.js",
]


def _read(rel: str) -> str:
    return (SRC / rel).read_text(encoding="utf-8")


def _campaign_js() -> str:
    data = json.loads(_read("data/campaign.json"))
    dump = functools.partial(json.dumps, ensure_ascii=False)
    return (
        "const CAMPAIGN=" + dump(data["evenings"]) + ";\n"
        "const MENTORS=" + dump(data["mentors"]) + ";\n"
    )


def _notes_js() -> str:
    generated = (GENERATED / "notes.js").read_text(encoding="utf-8")
    return "const NOTES={\n" + generated + ",\n" + _read("game/50-notes.js")


def _tree_js() -> str:
    return (GENERATED / "tree.js").read_text(encoding="utf-8").rstrip("\n") + "\n"


def _game_script() -> str:
    parts = []
    for name in GAME_ORDER:
        if name == "@campaign":
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
        + "<script>\n"
        + _game_script()
        + "</script>\n</body>\n</html>"
    )


def main() -> None:
    html = build()
    if "--check" in sys.argv:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != html:
            print(
                "game/grimoire.html differs from a fresh build of src/; run: just build"
            )
            sys.exit(1)
        print("build OK: game/grimoire.html matches src/")
        return
    OUT.write_text(html, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(html.encode()) // 1024} KB)")


if __name__ == "__main__":
    main()
