"""vibe.toml: every knob has a default, so the file is optional.

Unknown keys are refused (pydantic ``extra="forbid"``): a typo in the config
must fail loudly instead of silently doing nothing. Difficulty presets live
here too because they are configuration, not game logic.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from vibemap import project

ROOT = project.root()
CONFIG_PATH = ROOT / "vibe.toml"

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
    name: str = "Lotte"
    persona: str = "chief-of-staff"
    difficulty: Difficulty = "normal"
    mode: Mode = "campaign"
    provider: Provider = "claude"


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


class PetConfig(_Strict):
    """The terminal companion. Empty strings mean: keep what the name rolled."""

    enabled: bool = True
    species: str = ""
    name: str = ""
    eye: str = ""
    hat: str = ""


class Config(_Strict):
    """The whole of vibe.toml with defaults for every table."""

    learner: Learner = Field(default_factory=Learner)
    theme: ThemeConfig = Field(default_factory=ThemeConfig)
    finale: Finale = Field(default_factory=Finale)
    game: GameConfig = Field(default_factory=GameConfig)
    vault: VaultConfig = Field(default_factory=VaultConfig)
    pet: PetConfig = Field(default_factory=PetConfig)

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
            "# Vibe Code Camp configuration. Every key has a default; delete the",
            "# file and `just start` still works. Unknown keys are refused.",
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
            "[pet]  # the terminal companion; empty means what your name rolled",
            f"enabled = {str(self.pet.enabled).lower()}",
            f"species = {_q(self.pet.species)}"
            "  # duck | goose | blob | cat | dragon | octopus | owl | penguin"
            " | turtle | snail | ghost | axolotl | capybara | cactus | robot"
            " | rabbit | mushroom | chonk | crab",
            f"name = {_q(self.pet.name)}",
            f"eye = {_q(self.pet.eye)}  # one of: · * × ◉ @ °",
            f"hat = {_q(self.pet.hat)}"
            "  # none | crown | tophat | propeller | halo | wizard | beanie | tinyduck",
            "",
        ]
        if self.game.show_pairings is not None:
            lines.insert(
                lines.index("[vault]") - 1,
                f"show_pairings = {str(self.game.show_pairings).lower()}",
            )
        return "\n".join(lines)

    def save(self, path: Path = CONFIG_PATH) -> None:
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
        "No hints, every check strict, and `just verify` must be green to claim.",
    ),
}  # fmt: skip
