"""config/camp.toml: every knob has a default, so the file is optional.

Unknown keys are refused (pydantic ``extra="forbid"``): a typo in the config
must fail loudly instead of silently doing nothing. Difficulty presets live
here too because they are configuration, not game logic.

This is the journey level of the three configuration levels (see
`docs/CONFIG.md`): who you are, how hard, which theme, where the vault is.
The retired `vibe.toml` at the camp root is still read for one release;
`deprecation_note()` says so, and writes go back to the file that was read.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from vibemap import pet, project, sprites

ROOT = project.root()
CONFIG_PATH = project.config_path(ROOT)


def deprecation_note() -> str | None:
    """One line when a camp is still on vibe.toml, else nothing."""
    legacy = project.legacy_config_in_use(ROOT)
    if legacy is None:
        return None
    return (
        f"{legacy.name} is read for one more release; "
        f"move it to {project.CAMP_CONFIG.as_posix()}"
    )


Difficulty = Literal["beginner", "easy", "normal", "hard", "expert", "god"]
Mode = Literal["campaign", "roadmap"]
Provider = Literal["claude", "codex", "gemini", "copilot", "opencode"]

DEFAULT_DATES = [
    "Friday 25 September",
    "Saturday 3 October",
    "Friday 9 October",
    "Saturday 17 October",
    "Friday 23 October",
    "Another slot, I will circle back with Tom",
]


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Learner(_Strict):
    name: str = "<your_name>"  # a placeholder until vibe name or just start sets it
    persona: str = "chief-of-staff"
    difficulty: Difficulty = "normal"
    mode: Mode = "campaign"
    provider: Provider = "claude"
    # Shelves of the tech tree to be offered first; empty means everything.
    # Nothing is hidden by a choice, so an empty list is a complete course.
    interests: list[str] = Field(default_factory=list)

    @field_validator("interests")
    @classmethod
    def _known_shelves(cls, value: list[str]) -> list[str]:
        from vibemap.interests import normalise  # noqa: PLC0415

        return normalise(value)


class ThemeConfig(_Strict):
    preset: str = "studio"


class Finale(_Strict):
    dates: list[str] = Field(default_factory=lambda: list(DEFAULT_DATES))


class GameConfig(_Strict):
    repo_url: str = "https://github.com/tpetedb/vibe-map"
    # Where the product is published. The game links to documents that live
    # beside it there (the syllabus), and a camp keeps this pointing at the
    # product so its own copy of the game never links into a folder it has
    # not got.
    site_url: str = "https://tpetedb.github.io/vibe-map/"
    shadow_map: int = 2048
    show_pairings: bool | None = None


VaultMode = Literal["full", "grow"]


class VaultConfig(_Strict):
    path: str = "vault"
    folder: str = "Camp"
    mode: VaultMode = "full"


class NewsConfig(_Strict):
    """The live world feed: what `vibe news` pulls and whether the game shows it.

    An empty feed list means the registry in `vibemap/data/sources.json`.
    `live = false` is the off switch: nothing from the feed appears anywhere
    in the game and the hosted game does not refresh at runtime.
    """

    live: bool = True
    feeds: list[str] = Field(default_factory=list)
    per_feed: int = 8


class PetConfig(_Strict):
    """The terminal companion. Empty strings mean: keep what the name rolled."""

    enabled: bool = True
    species: str = ""
    name: str = ""
    eye: str = ""
    hat: str = ""
    # auto: pixels where a species has them and the terminal has truecolor.
    style: Literal["auto", "pixel", "ascii"] = "auto"


class Config(_Strict):
    """The whole of camp.toml with defaults for every table."""

    learner: Learner = Field(default_factory=Learner)
    theme: ThemeConfig = Field(default_factory=ThemeConfig)
    finale: Finale = Field(default_factory=Finale)
    game: GameConfig = Field(default_factory=GameConfig)
    vault: VaultConfig = Field(default_factory=VaultConfig)
    pet: PetConfig = Field(default_factory=PetConfig)
    news: NewsConfig = Field(default_factory=NewsConfig)

    @classmethod
    def load(cls, path: Path = CONFIG_PATH) -> Config:
        """Read the TOML file if it exists; refuse unknown keys.

        Raises:
            ValueError: with the offending key when the file has a typo.
        """
        if not path.exists():
            return cls()
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        try:
            return cls.model_validate(data)
        except ValidationError as e:
            problems = "; ".join(
                f"{'.'.join(str(p) for p in err['loc'])}: {err['msg']}"
                for err in e.errors()
            )
            raise ValueError(f"{path.name}: {problems}") from None

    def vault_dir(self) -> Path:
        return ROOT / self.vault.path / self.vault.folder

    def dump(self) -> str:
        """Render the config as TOML with the explanatory header."""
        lines = [
            "# Vibe Code Camp, journey configuration: who you are, how hard, the",
            "# theme, the vault. Every key has a default; delete the file and",
            "# `just start` still works. Unknown keys are refused. The game's own",
            "# configuration is src/config/, see docs/CONFIG.md.",
            "",
            "[learner]",
            f"name = {toml_str(self.learner.name)}",
            f"persona = {toml_str(self.learner.persona)}"
            "  # chief-of-staff | cleaning-ceo | university-md | pabo-teacher"
            " | data-engineer | interior-stylist",
            f"difficulty = {toml_str(self.learner.difficulty)}"
            "  # beginner | easy | normal | hard | expert | god",
            f"mode = {toml_str(self.learner.mode)}"
            "  # campaign (four evenings) | roadmap (the tech tree as quests)",
            f"provider = {toml_str(self.learner.provider)}"
            "  # claude | codex | gemini | copilot | opencode",
            "interests = ["
            + ", ".join(toml_str(i) for i in self.learner.interests)
            + "]"
            "  # shelves to offer first; empty = everything (vibe interests)",
            "",
            "[theme]",
            f"preset = {toml_str(self.theme.preset)}"
            "  # studio | wine-night | boardroom | seminar | field-guide"
            " | a name in themes/",
            "",
            "[finale]",
            "dates = [",
            *[f"  {toml_str(d)}," for d in self.finale.dates],
            "]",
            "",
            "[game]",
            f"repo_url = {toml_str(self.game.repo_url)}",
            f"site_url = {toml_str(self.game.site_url)}  # where the product is published",
            f"shadow_map = {self.game.shadow_map}  # drop to 1024 if a phone stutters",
            "",
            "[vault]",
            f"path = {toml_str(self.vault.path)}",
            f"folder = {toml_str(self.vault.folder)}",
            f"mode = {toml_str(self.vault.mode)}"
            "  # full (every note from day one) | grow (notes unlock as you play)",
            "",
            "[news]  # the live world feed; empty feeds means the source registry",
            f"live = {str(self.news.live).lower()}"
            "  # false hides every feed-driven element in the game",
            "feeds = [" + ", ".join(toml_str(f) for f in self.news.feeds) + "]",
            f"per_feed = {self.news.per_feed}",
            "",
            "[pet]  # the terminal companion; empty means what your name rolled",
            f"enabled = {str(self.pet.enabled).lower()}",
            f"species = {toml_str(self.pet.species)}  # {' | '.join(pet.SPECIES)}",
            f"name = {toml_str(self.pet.name)}",
            f"eye = {toml_str(self.pet.eye)}  # one of: · * × ◉ @ °",
            f"hat = {toml_str(self.pet.hat)}"
            "  # none | crown | tophat | propeller | halo | wizard | beanie | tinyduck",
            f"style = {toml_str(self.pet.style)}  # auto | pixel | ascii; pixel sprites"
            f" for {', '.join(sprites.available())}",
            "",
        ]
        if self.game.show_pairings is not None:
            lines.insert(
                lines.index("[vault]") - 1,
                f"show_pairings = {str(self.game.show_pairings).lower()}",
            )
        return "\n".join(lines)

    def save(self, path: Path = CONFIG_PATH) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.dump(), encoding="utf-8")


# tomllib only reads, so every write goes through this one serialiser. A name
# with a quote, a backslash or a newline must come back out of the file
# unchanged; TOML 1.0 basic strings escape those and every control character.
_TOML_ESCAPES = {
    "\\": "\\\\",
    '"': '\\"',
    "\b": "\\b",
    "\t": "\\t",
    "\n": "\\n",
    "\f": "\\f",
    "\r": "\\r",
}


def toml_str(value: str) -> str:
    """VALUE as a TOML basic string, ready to be written into camp.toml."""
    out = []
    for c in value:
        escaped = _TOML_ESCAPES.get(c)
        if escaped is None and (c < " " or c == "\x7f"):
            escaped = f"\\u{ord(c):04X}"
        out.append(escaped or c)
    return '"' + "".join(out) + '"'


def config_label(path: Path = CONFIG_PATH) -> str:
    """How the configuration file is named in output: one spelling everywhere."""
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.name


@dataclass(frozen=True, slots=True)
class DifficultyPreset:
    """What a difficulty changes: hints, strictness, XP."""

    label: str
    xp_multiplier: float
    hints: Literal["full", "short", "none"]
    strict: bool
    extra_checks: bool
    blurb: str


DIFFICULTIES: dict[str, DifficultyPreset] = {
    "beginner": DifficultyPreset(
        "Beginner", 0.8, "full", False, False,
        "Every command is spelled out and copy-pastable. Checks are lenient.",
    ),
    "easy": DifficultyPreset(
        "Easy", 0.9, "full", False, False,
        "Full hints, lenient checks, a little less hand-holding in the copy.",
    ),
    "normal": DifficultyPreset(
        "Normal", 1.0, "short", False, False,
        "Short hints. The checks look at what you actually built.",
    ),
    "hard": DifficultyPreset(
        "Hard", 1.5, "short", True, False,
        "Strict checks: more commits, real links, no placeholder files.",
    ),
    "expert": DifficultyPreset(
        "Expert", 2.0, "none", True, True,
        "No hints. Extra checks: tests exist and pass, the vault is lint-clean.",
    ),
    "god": DifficultyPreset(
        "God", 3.0, "none", True, True,
        "No hints, every check strict, and the whole gate green: `just verify` "
        "in the product, the vault lint and your tests in a camp.",
    ),
}  # fmt: skip
