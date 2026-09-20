"""Tom's palette mapped to rich and Textual, the same tokens R2-D2 uses.

Red is action and errors, green is success and done, blue is organisation
and paths, yellow is curiosity and warnings, black is the background.
"""

from __future__ import annotations

import re

from rich.theme import Theme

RED = "#D32F2F"
GREEN = "#00A86B"
BLUE = "#0067A5"
YELLOW = "#FFBF00"
ORANGE = "#FF8C1A"
# The fonts a device already has. The game is one file with no CDN and
# every generated page must read the same offline as online, so nothing
# here asks a third party for a typeface.
SYSTEM_SANS = 'system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",sans-serif'
SYSTEM_MONO = 'ui-monospace,"SF Mono",Menlo,Consolas,monospace'
BLACK = "#000000"
SURFACE = "#0A0A0A"
TEXT = "#F1F1F8"
MUTED = "#8B93A7"

# Semantic aliases
PRIMARY = YELLOW
SECONDARY = BLUE
ACCENT = GREEN
ERROR = RED
SUCCESS = GREEN
WARN = YELLOW

RICH_THEME = Theme(
    {
        "ok": f"bold {GREEN}",
        "done": GREEN,
        "todo": MUTED,
        "warn": YELLOW,
        "err": f"bold {RED}",
        "path": BLUE,
        "title": f"bold {YELLOW}",
        "muted": MUTED,
        "xp": f"bold {ORANGE}",
        "accent": GREEN,
    }
)

# One colour per shelf of the tech tree; the game's tree view uses the same map.
CATEGORY_COLOURS = {
    "shell": BLUE,
    "git": ORANGE,
    "formats": YELLOW,
    "code": GREEN,
    "data": "#00D084",
    "net": "#0088CC",
    "ship": "#F04923",
    "agents": RED,
    "docs": "#C29200",
    "knowledge": "#FFA94D",
    "future": "#CCCCCC",
}

# Obsidian graph colour groups want the 24-bit integer of the hex colour.
AGE_COLOURS = {
    "dark": "#94A3B8",
    "feudal": GREEN,
    "castle": ORANGE,
    "imperial": "#C084FC",
    "future": YELLOW,
}


def hex_to_int(hex_colour: str) -> int:
    """Convert '#RRGGBB' to the integer Obsidian stores in graph.json."""
    return int(hex_colour.lstrip("#"), 16)


# The design tokens of docs/DESIGN.md, in the order src/style.css declares
# them. Anything the CLI renders as HTML (the dashboard report) writes this
# block instead of spelling colours again; a test keeps it equal to the game's.
CSS_TOKENS: dict[str, str] = {
    "bg": BLACK,
    "surface-1": SURFACE,
    "surface-2": "#141414",
    "surface-3": "#1A1A1A",
    "hairline": "rgba(255,255,255,.10)",
    "hairline-2": "rgba(255,255,255,.18)",
    "text": TEXT,
    "muted": MUTED,
    "red": RED,
    "red-dim": "#9A2A2A",
    "red-bright": "#F04923",
    "orange": ORANGE,
    "orange-dim": "#C26A14",
    "orange-bright": "#FFA94D",
    "yellow": YELLOW,
    "yellow-dim": "#C29200",
    "yellow-bright": "#FFD500",
    "green": GREEN,
    "green-dim": "#0A7A52",
    "green-bright": "#00D084",
    "blue": BLUE,
    "blue-dim": "#0A4E7A",
    "blue-bright": "#0088CC",
    "radius-s": "8px",
    "radius-m": "12px",
    "radius-l": "16px",
    "radius-pill": "999px",
    "space-1": "4px",
    "space-2": "8px",
    "space-3": "12px",
    "space-4": "16px",
    "space-6": "24px",
    "space-8": "32px",
    "font-display": SYSTEM_SANS,
    "font-body": SYSTEM_SANS,
    "font-mono": SYSTEM_MONO,
}


def css_tokens(indent: str = "  ") -> str:
    """The :root block every generated page starts from."""
    body = "\n".join(f"{indent}--{k}:{v};" for k, v in CSS_TOKENS.items())
    return ":root{\n" + body + "\n}"


# A terminal paints with escape sequences; a table cell, a log line and a check
# detail are text. This is the one place they come off.
_ESCAPE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]|\x1b[@-_~]")


def plain(text: str) -> str:
    """Terminal output as text: no escape sequences, no control characters.

    Newlines survive, because a caller that splits the output into lines
    depends on them; everything else a program writes to move the cursor or
    ring a bell is dropped.
    """
    kept = (c for c in _ESCAPE.sub("", text) if c == "\n" or c.isprintable())
    return "".join(kept).strip()
