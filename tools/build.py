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
import re
import shutil
import sys
import urllib.parse
from pathlib import Path
from string import ascii_letters, digits
from typing import Any


def _root(argv: list[str] | None = None) -> Path:
    """Where to build: --root DIR, else the folder holding this file's tools/."""
    args = list(argv if argv is not None else sys.argv[1:])
    if "--root" in args:
        return Path(args[args.index("--root") + 1]).expanduser().resolve()
    return Path(__file__).resolve().parents[1]


ROOT = _root()
SRC = ROOT / "src"
OUT = ROOT / "game" / "vibe-map.html"
# The runtime feed, published next to the game by the Pages workflow.
NEWS_OUT = ROOT / "game" / "news.json"
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
    "17b-switchboard.js",
    "@items",
    "18-avatar.js",
    "19-items.js",
    "@pets",
    "19b-pet.js",
    "19c-bottles.js",
    "20-worlds.js",
    "21-world-build.js",
    "22-archipelago.js",
    "30-input.js",
    "31-animate.js",
    "32-minimap.js",
    "40-sheet.js",
    "41-search.js",
    "@notes",
    "51-notes-dynamic.js",
    "@tree",
    "60-vault.js",
    "70-minigames.js",
    "71-finale.js",
    "80-sync.js",
    "85-settings.js",
    "86-interests.js",
    "87-onboarding.js",
    "88-chat.js",
    "89-dashboard.js",
    "90-boot.js",
]


def _read(rel: str) -> str:
    return (SRC / rel).read_text(encoding="utf-8")


def _icon_data_uri() -> str:
    """src/icon.svg as an inline data URI: the tab icon costs no request.

    Single quotes inside, so the URI can sit in a double-quoted attribute; the
    hash of every colour has to be escaped or the browser reads it as the
    start of a fragment.
    """
    svg = " ".join(_read("icon.svg").split()).replace('"', "'")
    return "data:image/svg+xml," + urllib.parse.quote(svg, safe="/:=;,' ")


def _head_html() -> str:
    """head.html with its placeholders filled; an unfilled one is a build fault."""
    site = _camp().game.site_url
    text = _read("head.html")
    for key, value in (("{{SITE}}", site), ("{{ICON}}", _icon_data_uri())):
        text = text.replace(key, value)
    left = re.search(r"\{\{[A-Z]+\}\}", text)
    if left:
        raise SystemExit(f"src/head.html has no value for {left.group(0)}")
    return text


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


def _items_js() -> str:
    """Collectibles and seats: a fork's own list, else the package's."""
    sys.path.insert(0, str(ROOT))
    local = GENERATED / "items.json"
    if local.exists():
        data = json.loads(local.read_text(encoding="utf-8"))
    else:
        from vibemap.project import data_text  # noqa: PLC0415

        data = json.loads(data_text("items.json"))
    return "const ITEMS=" + json.dumps(data, ensure_ascii=False) + ";\n"


def _pets_js() -> str:
    """The vendored pixel sets, the same packed frames the terminal paints.

    One source: vibemap/data/pets is read here, so nothing is redrawn for the
    game and a fork built from the installed package gets them too.
    """
    sys.path.insert(0, str(ROOT))
    from vibemap import sprites  # noqa: PLC0415

    data = {
        name: json.loads(
            (sprites.PETS / name / "frames.json").read_text(encoding="utf-8")
        )
        for name in sprites.available()
    }
    return "const PETS=" + json.dumps(data, ensure_ascii=False) + ";\n"


def _notes_js() -> str:
    generated = (GENERATED / "notes.js").read_text(encoding="utf-8")
    return "const NOTES={\n" + generated + ",\n" + _read("game/50-notes.js")


def _tree_js() -> str:
    return (GENERATED / "tree.js").read_text(encoding="utf-8").rstrip("\n") + "\n"


# The feed the game carries. NEWS_FIELDS is the whole contract between
# vibemap/news.py and the News card; a version travels with it so a game built
# by an older release refuses a newer file instead of half reading it.
NEWS_FIELDS = ("id", "source", "name", "kind", "title", "link", "date", "summary")
NEWS_ITEMS = 24


def _news_payload() -> dict[str, object]:
    """data/news.json, trimmed to what the game reads."""
    p = ROOT / "data" / "news.json"
    data = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    items = [
        {**{k: it.get(k, "") for k in NEWS_FIELDS}, "tags": it.get("tags", [])}
        for it in data.get("items", [])[:NEWS_ITEMS]
    ]
    return {
        "version": data.get("version", 0),
        "fetched_at": data.get("fetched_at", ""),
        "items": items,
    }


def news_json() -> str:
    """The same payload as a file next to the game, for the runtime refresh.

    The hosted game fetches ./news.json from its own origin, so the copy that
    ships beside the page is what a browser with no live update reads.
    """
    return json.dumps(_news_payload(), ensure_ascii=False, indent=1) + "\n"


def _news_js() -> str:
    """The baked copy, so a file:// game shows the feed without a fetch."""
    return "const NEWS=" + json.dumps(_news_payload(), ensure_ascii=False) + ";\n"


def _version() -> str:
    """The product version: this checkout's pyproject, else the installed package."""
    import tomllib  # noqa: PLC0415 (3.11+; a fork may be started by an older python)

    pyproject = ROOT / "pyproject.toml"
    if pyproject.exists():
        return tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"][
            "version"
        ]
    from vibemap import __version__  # noqa: PLC0415

    return __version__


def _persona_interests(persona_id: str) -> list[str]:
    """The shelves this persona leans on; personas.py stays the one source."""
    from vibemap.personas import PERSONAS  # noqa: PLC0415

    p = PERSONAS.get(persona_id)
    return list(p.interests) if p else []


@functools.cache
def _camp() -> Any:
    """This camp's config/camp.toml: the one read, shared by everything here."""
    sys.path.insert(0, str(ROOT))
    from vibemap import project  # noqa: PLC0415
    from vibemap.config import Config  # noqa: PLC0415

    return Config.load(project.nearest_config(ROOT))


def _config_js() -> str:
    """The journey values (config/camp.toml) the game exposes as a constant."""
    sys.path.insert(0, str(ROOT))
    from vibemap.themes import load_theme, theme_for_game  # noqa: PLC0415

    cfg = _camp()
    version = _version()
    theme = theme_for_game(
        load_theme(cfg.theme.preset), show_pairings=cfg.game.show_pairings
    )
    data = {
        "version": version,
        "theme": theme,
        "dates": cfg.finale.dates,
        "repo": cfg.game.repo_url,
        # Where the product is published, so the game can link to a document
        # that lives beside it there from a camp that has no copy of one.
        "site": cfg.game.site_url,
        "shadowMap": cfg.game.shadow_map,
        "difficulty": cfg.learner.difficulty,
        "persona": cfg.learner.persona,
        "provider": cfg.learner.provider,
        "mode": cfg.learner.mode,
        # What the camp chose to learn, and what this persona would choose:
        # the game offers the preset and stores the answer in S.interests.
        "interests": cfg.learner.interests,
        "personaInterests": _persona_interests(cfg.learner.persona),
        # The camp's companion: a published game ships the camp's choice, the
        # way it ships the theme, and the player can change it in Settings.
        "pet": {"species": cfg.pet.species, "enabled": cfg.pet.enabled},
        "vault": {"mode": cfg.vault.mode},
        "news": {"live": cfg.news.live},
    }
    return "const CONFIG=" + json.dumps(data, ensure_ascii=False) + ";\n"


# Every part of the script is a whole unit of JavaScript, so its brackets
# close inside it. A part whose brackets do not close cannot parse, and the
# concatenation would hide the fault in whichever part the browser gives up on.
_CLOSERS = {")": "(", "]": "[", "}": "{"}
# After these, a slash divides; anywhere else it opens a regular expression.
_DIVIDE_AFTER = frozenset("_$)]}") | frozenset(ascii_letters + digits)


def _js_fault(text: str) -> str | None:
    """Where this JavaScript stops making sense, or None when it holds up.

    Strings, template literals, comments and regular expressions are skipped,
    so the scan sees code only. It weighs brackets rather than parsing: that
    is what catches the truncated or hand-garbled file a build must refuse.
    """
    stack: list[tuple[str, int]] = []
    modes = ["code"]  # "template" while inside a `...`, back to code in ${...}
    line, i, n, prev = 1, 0, len(text), ""
    while i < n:
        c = text[i]
        if modes[-1] == "template":
            if c == "\n":
                line += 1
            elif c == "\\":
                i += 1
            elif c == "`":
                modes.pop()
            elif c == "$" and text[i : i + 2] == "${":
                stack.append(("${", line))
                modes.append("code")
                i += 1
            i += 1
            continue
        if c == "\n":
            line += 1
            i += 1
            continue
        if c.isspace():
            i += 1
            continue
        if c == "/" and text[i : i + 2] == "//":
            nl = text.find("\n", i)
            i = n if nl < 0 else nl
            continue
        if c == "/" and text[i : i + 2] == "/*":
            end = text.find("*/", i + 2)
            if end < 0:
                return f"line {line}: a block comment is never closed"
            line += text.count("\n", i, end)
            i = end + 2
            continue
        if c == "/" and prev not in _DIVIDE_AFTER:
            end = _regex_end(text, i)
            if end is not None:
                i = end
                prev = "/"
                continue
        if c in "\"'":
            end = _string_end(text, i)
            if end is None:
                return f"line {line}: a string is never closed"
            i = end
            prev = c
            continue
        if c == "`":
            modes.append("template")
            i += 1
            prev = "`"
            continue
        if c in "([{":
            stack.append((c, line))
        elif c in _CLOSERS:
            if not stack:
                return f"line {line}: `{c}` closes nothing"
            opened, at = stack.pop()
            if opened == "${":
                if c != "}":
                    return f"line {line}: `{c}` closes the ${{ of line {at}"
                modes.pop()
            elif opened != _CLOSERS[c]:
                return f"line {line}: `{c}` closes the `{opened}` of line {at}"
        prev = c
        i += 1
    if modes[-1] == "template":
        return "a template literal is never closed"
    if stack:
        opened, at = stack[-1]
        return f"line {at}: `{opened}` is never closed"
    return None


def _string_end(text: str, i: int) -> int | None:
    """The index after the quote that closes the string starting at i."""
    quote, i = text[i], i + 1
    while i < len(text):
        c = text[i]
        if c == "\\":
            i += 2
            continue
        if c == quote:
            return i + 1
        if c == "\n":
            return None
        i += 1
    return None


def _regex_end(text: str, i: int) -> int | None:
    """The index after the slash closing the regex at i, or None if it is not one.

    A regular expression lives on one line, so a slash whose partner is not on
    the same line was a division sign after all.
    """
    i, in_class = i + 1, False
    while i < len(text):
        c = text[i]
        if c == "\\":
            i += 2
            continue
        if c == "\n":
            return None
        if c == "[":
            in_class = True
        elif c == "]":
            in_class = False
        elif c == "/" and not in_class:
            return i + 1
        i += 1
    return None


def _part(name: str, text: str) -> str:
    fault = _js_fault(text)
    if fault:
        raise SystemExit(f"{name} is not JavaScript the browser can read: {fault}")
    return text


def _game_script() -> str:
    parts = []
    for name in GAME_ORDER:
        if name == "@config":
            parts.append(_part("CONFIG", _config_js()))
            parts.append(_part("NEWS", _news_js()))
            for f in sorted(CONFIG_DIR.glob("*.js")):
                parts.append(_part(f"src/config/{f.name}", f.read_text("utf-8")))
        elif name == "@campaign":
            parts.append(_part("the campaign", _campaign_js()))
        elif name == "@pets":
            parts.append(_part("the pixel pets", _pets_js()))
        elif name == "@items":
            parts.append(_part("the items", _items_js()))
        elif name == "@notes":
            parts.append(_part("src/game/50-notes.js", _notes_js()))
        elif name == "@tree":
            parts.append(_part("tools/generated/tree.js", _tree_js()))
        else:
            parts.append(_part("src/game/" + name, _read("game/" + name)))
    return "(function(){\n" + "".join(parts) + "})();\n"


def build() -> str:
    """Return the full HTML document as a string."""
    return (
        _head_html()
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
    feed = news_json()
    if "--check" in sys.argv:
        for path, fresh in ((OUT, html), (NEWS_OUT, feed)):
            current = path.read_text(encoding="utf-8") if path.exists() else ""
            if current != fresh:
                name = path.relative_to(ROOT)
                print(f"{name} differs from a fresh build of src/; run: just build")
                sys.exit(1)
        print("build OK: game/vibe-map.html matches src/")
        return
    OUT.write_text(html, encoding="utf-8")
    NEWS_OUT.write_text(feed, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(html.encode()) // 1024} KB)")


if __name__ == "__main__":
    main()
