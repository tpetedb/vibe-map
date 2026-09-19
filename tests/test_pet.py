"""The terminal companion: deterministic, twelve columns wide, configurable."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

from tools.script_camp import script_stops
from vibemap import pet, sprites
from vibemap.cli import cli
from vibemap.config import Config


def _camp(tmp_path: Path) -> Path:
    camp = tmp_path / "camp"
    out = CliRunner().invoke(cli, ["new", str(camp), "--name", "T"])
    assert out.exit_code == 0, out.output
    return camp


def _vibe(camp: Path, *args: str, **env: str) -> str:
    """The CLI as a learner runs it, in a camp of its own."""
    out = subprocess.run(
        [sys.executable, "-m", "vibemap.cli", *args],
        cwd=camp,
        env=dict(os.environ, VIBE_HOME=str(camp), NO_COLOR="1", COLUMNS="100", **env),
        capture_output=True,
        text=True,
    )
    return out.stdout + out.stderr


def test_roll_matches_upstream_for_known_names() -> None:
    # Values taken from `npx claude-buddy <name>` (btcromesh/claude-buddy 1.0.0).
    tom = pet.roll("tom")
    assert (tom.species, tom.rarity, tom.name) == ("robot", "common", "Spooky Pebble")
    lotte = pet.roll("Lotte")
    assert (lotte.species, lotte.rarity, lotte.name) == (
        "snail",
        "common",
        "Bouncy Biscuit",
    )
    owl = pet.roll("tpetedb")
    assert (owl.species, owl.rarity, owl.name, owl.hat) == (
        "owl",
        "epic",
        "Fuzzy Wobbles",
        "crown",
    )
    assert pet.roll("tom") == tom


def test_every_frame_is_five_rows_of_twelve_columns() -> None:
    for species in pet.SPECIES:
        p = pet.Pet(species, species, pet.EYES[3], "wizard", "rare", False, {})
        for tick in range(len(pet.IDLE_SEQUENCE)):
            rows = pet.frame(p, tick)
            assert len(rows) == 5, species
            assert all(len(r) == pet.WIDTH for r in rows), (species, tick, rows)
    blink = pet.frame(pet.roll("tom"), pet.IDLE_SEQUENCE.index(-1))
    assert pet.roll("tom").eye not in "".join(blink)


def test_the_hat_stays_on_every_frame() -> None:
    # Row 0 is the hat's row; a fidget there keeps only what the hat misses.
    for species in pet.SPECIES:
        p = pet.Pet(species, species, pet.EYES[0], "crown", "epic", False, {})
        for index in range(len(pet.BODIES[species])):
            rows = pet.sprite(p, index)
            assert "\\^^^/" in rows[0], (species, index, rows[0])
            assert all(len(r) == pet.WIDTH for r in rows), (species, index)
    dragon = pet.Pet("dragon", "d", pet.EYES[0], "crown", "epic", False, {})
    assert pet.sprite(dragon, 2)[0] == "   \\^^^/~   "
    bare = pet.Pet("dragon", "d", pet.EYES[0], "none", "common", False, {})
    assert pet.sprite(bare, 2)[0] == "   ~    ~   "


def test_resolve_applies_overrides_and_refuses_unknown_ones() -> None:
    p = pet.resolve("tom", species="crab", name="Pinch", hat="crown")
    assert (p.species, p.name, p.hat, p.rarity) == ("crab", "Pinch", "crown", "common")
    assert pet.sprite(p, 0)[0].strip() == "\\^^^/"
    with pytest.raises(ValueError, match="species"):
        pet.resolve("tom", species="unicorn")
    with pytest.raises(ValueError, match="hat"):
        pet.resolve("tom", hat="fedora")


def test_stroll_turns_around_inside_the_width() -> None:
    offsets = [pet.stroll(t, 40, period=8) for t in range(16)]
    assert offsets[0] == 0 and max(offsets) == 40 - pet.WIDTH
    assert offsets[8] == 40 - pet.WIDTH and offsets[15] > 0
    assert pet.stroll(5, 10) == 0


def test_config_round_trips_the_pet_table(tmp_path) -> None:
    cfg = Config()
    cfg.pet.species = "crab"
    cfg.pet.name = "Pinch"
    cfg.pet.style = "pixel"
    cfg.save(tmp_path / "vibe.toml")
    back = Config.load(tmp_path / "vibe.toml")
    assert back.pet.species == "crab" and back.pet.name == "Pinch"
    assert back.pet.enabled is True
    assert back.pet.style == "pixel" and Config().pet.style == "auto"
    (tmp_path / "bad.toml").write_text('[pet]\nstyle = "crayon"\n', encoding="utf-8")
    with pytest.raises(ValueError, match="pet.style"):
        Config.load(tmp_path / "bad.toml")


def test_vibe_pet_prints_the_creature_and_the_gallery() -> None:
    runner = CliRunner()
    out = runner.invoke(cli, ["pet", "--all"]).output
    assert out.count("\n\n") >= len(pet.SPECIES) - 1
    assert "crab" in out and "dog" in out
    one = runner.invoke(cli, ["pet"])
    assert one.exit_code == 0, one.output
    assert "face:" in one.output


def test_the_cat_and_the_dog_are_chosen_never_rolled() -> None:
    # The roll indexes into the upstream list, so ours must stay out of it.
    assert "crab" not in pet._ROLLABLE and "dog" not in pet._ROLLABLE
    assert "cat" in pet._ROLLABLE
    assert set(pet.SPECIES) - set(pet._ROLLABLE) == {"crab", "dog"}
    for name in ("cat", "dog"):
        p = pet.resolve("tom", species=name)
        assert p.species == name
        assert pet.columns(p, "pixel") == sprites.sheet(name).width
        assert pet.happy_frames(p, "pixel") > 1
        assert "Shepardskin" in pet.credit(p, "pixel")
        # Pixels where the terminal allows them, the ASCII art everywhere else.
        assert "▀" in pet.render(p, 0, stats=False, style="pixel").plain
        assert "▀" not in pet.render(p, 0, stats=False, style="ascii").plain


def test_vibe_pet_species_writes_the_choice_into_the_camp(tmp_path) -> None:
    camp = _camp(tmp_path)
    out = _vibe(camp, "pet", "--species", "dog")
    assert "camp.toml [pet] updated" in out, out
    assert 'species = "dog"' in (camp / "config" / "camp.toml").read_text()
    assert "dog ·" in _vibe(camp, "pet")
    assert "unknown species" in _vibe(camp, "pet", "--species", "wyvern")


def test_a_colourless_terminal_hears_why_the_pixels_look_flat(tmp_path) -> None:
    camp = _camp(tmp_path)
    forced = _vibe(camp, "pet", "--species", "crab", "--style", "pixel")
    # NO_COLOR paints no truecolor, so the half blocks arrive flat: say so.
    assert "truecolor" in forced and "ascii" in forced, forced
    art = _vibe(camp, "pet", "--style", "ascii", TERM="dumb")
    assert "\u2580" not in art and "truecolor" not in art, art


def test_a_claimed_stop_flashes_the_happy_state(tmp_path) -> None:
    camp = _camp(tmp_path)
    assert "is pleased" in _vibe(camp, "done", "1", "did it", "--force")
    script_stops(camp)
    assert "is pleased" in _vibe(camp, "check", "1", "-w", "winter")
    # Switched off in camp.toml, the claim says nothing about the creature.
    _vibe(camp, "pet", "--off")
    assert "is pleased" not in _vibe(camp, "done", "2", "did it", "--force")
