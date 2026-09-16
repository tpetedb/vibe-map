"""Themes: the same course in a different voice.

The wine-night preset is the original: corporate jargon on top of real
content, Rolinda speaking plainly. The serious presets keep the content and
change the framing, the pairing and the hosts. A custom theme is a TOML file
in themes/ with the same fields; `vibe theme create` asks the provider to
write one.
"""

from __future__ import annotations

import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

ROOT = Path(__file__).resolve().parents[1]
THEMES_DIR = ROOT / "themes"

PairingKind = Literal["wine", "coffee", "tea", "none"]
Tone = Literal["jargon", "plain", "academic"]


@dataclass(frozen=True, slots=True)
class Theme:
    id: str
    label: str
    tone: Tone
    host_role: str
    guide_role: str
    pairing_kind: PairingKind
    intro: str
    pairings: tuple[str, ...]
    sign_off: str

    def to_toml(self) -> str:
        d = asdict(self)
        lines = [
            f"# Theme {self.id}: edit freely, then set [theme] preset in vibe.toml"
        ]
        for k, v in d.items():
            if isinstance(v, (tuple, list)):
                lines.append(f"{k} = [")
                lines += [f"  {_q(x)}," for x in v]
                lines.append("]")
            else:
                lines.append(f"{k} = {_q(str(v))}")
        return "\n".join(lines) + "\n"


def _q(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


THEMES: dict[str, Theme] = {
    "studio": Theme(
        id="studio",
        label="Studio (professional, playful, the default)",
        tone="plain",
        host_role="Site Reliability Engineer",
        guide_role="Head of Operations",
        pairing_kind="coffee",
        intro=(
            "Welcome to the campus. Over one evening you build one small piece "
            "of software with an AI coding agent, keep it under version control, "
            "connect it to real data and one tool, publish it, and schedule an "
            "agent to run without you. Eight stops, each with a definition of "
            "done and one plain question at the end. Tom keeps the systems up; "
            "Rolinda asks the questions everyone else is too polite to ask."
        ),
        pairings=(
            "Espresso, to start",
            "Filter, slow",
            "Flat white",
            "Cortado",
            "Cold brew",
            "Decaf, sensibly",
            "Sparkling water",
            "Still water",
        ),
        sign_off="Done is a green check and one sentence you can explain to Rolinda.",
    ),
    "wine-night": Theme(
        id="wine-night",
        label="Wine night (the original)",
        tone="jargon",
        host_role="Site Reliability Engineer, Executive Sponsor",
        guide_role="Head of Hospitality Operations (Beverages)",
        pairing_kind="wine",
        intro=(
            "Dear Chief of Staff. Welcome to your greenfield, cloud-agnostic, "
            "future-proof Innovation Campus. Over one evening of high-bandwidth "
            "synchronous co-creation, one workstream per hour, we will stand up "
            "eight strategic capabilities and, on the final slide, align on a "
            "go-live date. The evening is paired accordingly, beginning with a "
            "Chardonnay from Bourgogne that Rolinda describes as arrogant on the "
            "cheek."
        ),
        pairings=(
            "Bourgogne Chardonnay, the arrogant one",
            "Sancerre, chalky, unresolved finish",
            "Barolo, decanted during the retro",
            "Riesling Kabinett, precise, versioned",
            "Rioja Reserva, integrated",
            "Champagne, for the go-live",
            "Port, for the postmortem",
            "Water, for the drive home",
        ),
        sign_off="Per the RACI, Rolinda has the last word.",
    ),
    "boardroom": Theme(
        id="boardroom",
        label="Boardroom (serious, coffee)",
        tone="plain",
        host_role="Engineering lead",
        guide_role="Operations lead",
        pairing_kind="coffee",
        intro=(
            "Welcome. In one evening you will build a small piece of software "
            "with an AI coding agent, keep it under version control, connect it "
            "to real data and one external tool, publish it, and schedule an "
            "agent to run without you. Eight steps, each with a definition of "
            "done and a plain question at the end."
        ),
        pairings=(
            "Espresso, short",
            "Filter, Ethiopian, slow",
            "Flat white",
            "Cortado",
            "Cold brew",
            "Decaf, sensibly",
            "Sparkling water",
            "Still water",
        ),
        sign_off="Decisions are written down before anyone leaves.",
    ),
    "seminar": Theme(
        id="seminar",
        label="Seminar (academic, tea)",
        tone="academic",
        host_role="Course convener",
        guide_role="Teaching assistant",
        pairing_kind="tea",
        intro=(
            "This seminar treats AI coding agents as a subject of study and a "
            "tool at once. Each of the eight sessions introduces one concept, "
            "its history, a hands-on exercise with a verifiable outcome, and "
            "the primary source to read afterwards. Bring questions; the "
            "exercises are the argument."
        ),
        pairings=(
            "Sencha",
            "Earl Grey",
            "Oolong",
            "Genmaicha",
            "Rooibos",
            "Chamomile",
            "Mint",
            "Water",
        ),
        sign_off="Reading for next week is in the vault.",
    ),
    "field-guide": Theme(
        id="field-guide",
        label="Field guide (plain, no pairing)",
        tone="plain",
        host_role="Guide",
        guide_role="Guide",
        pairing_kind="none",
        intro=(
            "This is a field guide. Eight stops, each one thing you build and "
            "can show. No jargon, no ceremony. When you finish a stop, run the "
            "check, read what it says, and move on."
        ),
        pairings=(),
        sign_off="Done is when the check is green.",
    ),
}

DEFAULT_THEME = "studio"


def load_theme(name: str) -> Theme:
    """A preset by id, or themes/<name>.toml; raise ValueError otherwise."""
    if name in THEMES:
        return THEMES[name]
    path = THEMES_DIR / f"{name}.toml"
    if not path.exists():
        raise ValueError(
            f"unknown theme {name!r}; presets: {', '.join(THEMES)}; "
            f"custom themes live in themes/<name>.toml"
        )
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    data["pairings"] = tuple(data.get("pairings", ()))
    missing = {f for f in Theme.__dataclass_fields__} - set(data)
    if missing:
        raise ValueError(f"{path.name} is missing: {', '.join(sorted(missing))}")
    return Theme(**data)


def theme_for_game(theme: Theme, *, show_pairings: bool | None) -> dict[str, object]:
    """The subset the game embeds as `const THEME`."""
    return {
        "id": theme.id,
        "tone": theme.tone,
        "hostRole": theme.host_role,
        "guideRole": theme.guide_role,
        "pairing": theme.pairing_kind,
        "showPairings": (
            theme.pairing_kind != "none" if show_pairings is None else show_pairings
        ),
        "intro": theme.intro,
        "pairings": list(theme.pairings),
        "signOff": theme.sign_off,
    }
