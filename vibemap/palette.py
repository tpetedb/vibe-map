"""Tom's palette mapped to rich and Textual, the same tokens R2-D2 uses.

Red is action and errors, green is success and done, blue is organisation
and paths, yellow is curiosity and warnings, black is the background.
"""

from __future__ import annotations

from rich.theme import Theme

RED = "#D32F2F"
GREEN = "#00A86B"
BLUE = "#0067A5"
YELLOW = "#FFBF00"
ORANGE = "#FF8C1A"
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
