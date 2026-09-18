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
    shadow_map: int = 2048
    show_pairings: bool | None = None


VaultMode = Literal["full", "grow"]


class VaultConfig(_Strict):
    path: str = "vault"
    folder: str = "Camp"
    mode: VaultMode = "full"


class NewsConfig(_Strict):
    """Feeds `vibe news` pulls; an empty list means the built-in six."""

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
            f"name = {_q(self.learner.name)}",
            f"persona = {_q(self.learner.persona)}"
            "  # chief-of-staff | cleaning-ceo | university-md | pabo-teacher"
            " | data-engineer | interior-stylist",
            f"difficulty = {_q(self.learner.difficulty)}"
            "  # beginner | easy | normal | hard | expert | god",
            f"mode = {_q(self.learner.mode)}"
            "  # campaign (four evenings) | roadmap (the tech tree as quests)",
            f"provider = {_q(self.learner.provider)}"
            "  # claude | codex | gemini | copilot | opencode",
            "interests = [" + ", ".join(_q(i) for i in self.learner.interests) + "]"
            "  # shelves to offer first; empty = everything (vibe interests)",
            "",
            "[theme]",
            f"preset = {_q(self.theme.preset)}"
            "  # studio | wine-night | boardroom | seminar | field-guide"
            " | a name in themes/",
            "",
            "[finale]",
            "dates = [",
            *[f"  {_q(d)}," for d in self.finale.dates],
            "]",
            "",
            "[game]",
            f"repo_url = {_q(self.game.repo_url)}",
            f"shadow_map = {self.game.shadow_map}  # drop to 1024 if a phone stutters",
            "",
            "[vault]",
            f"path = {_q(self.vault.path)}",
            f"folder = {_q(self.vault.folder)}",
            f"mode = {_q(self.vault.mode)}"
            "  # full (every note from day one) | grow (notes unlock as you play)",
            "",
            "[news]  # feeds for `vibe news`; empty means the built-in six",
            "feeds = [" + ", ".join(_q(f) for f in self.news.feeds) + "]",
            f"per_feed = {self.news.per_feed}",
            "",
            "[pet]  # the terminal companion; empty means what your name rolled",
            f"enabled = {str(self.pet.enabled).lower()}",
            f"species = {_q(self.pet.species)}  # {' | '.join(pet.SPECIES)}",
            f"name = {_q(self.pet.name)}",
            f"eye = {_q(self.pet.eye)}  # one of: · * × ◉ @ °",
            f"hat = {_q(self.pet.hat)}"
            "  # none | crown | tophat | propeller | halo | wizard | beanie | tinyduck",
            f"style = {_q(self.pet.style)}  # auto | pixel | ascii; pixel sprites"
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


def _q(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


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
