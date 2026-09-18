"""The terminal companion: deterministic, twelve columns wide, configurable."""

from __future__ import annotations

import pytest
from click.testing import CliRunner

from vibemap import pet
from vibemap.cli import cli
from vibemap.config import Config


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
    assert "crab" in out
    one = runner.invoke(cli, ["pet"])
    assert one.exit_code == 0, one.output
    assert "face:" in one.output
