"""The terminal companion: state, config, quests, vault, scores, personas, themes."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from grimoire import campaign
from grimoire.cli import cli
from grimoire.config import DIFFICULTIES, Config
from grimoire.personas import PERSONAS, get_persona
from grimoire.quests import LEVELS, level_for, quest_for, required_levels, xp_for
from grimoire.scores import read_scores, run_sql, summary
from grimoire.state import State, decode_code
from grimoire.themes import THEMES, load_theme
from grimoire.toolbelt import TOOLS
from grimoire.vault import Vault, safe_title
from tests.conftest import ROOT

# ---- state ---------------------------------------------------------------------


def test_state_round_trips_through_json(tmp_path: Path) -> None:
    p = tmp_path / "state.json"
    s = State(name="Tom")
    assert s.mark_done("campus", 1, note="shipped", xp=100)
    assert not s.mark_done("campus", 1)
    s.save(p)
    back = State.load(p)
    assert back.name == "Tom" and back.done == [1] and back.xp == 100
    assert back.log[0].note == "shipped"


def test_state_migrates_the_v1_file(tmp_path: Path) -> None:
    p = tmp_path / "state.json"
    p.write_text(
        json.dumps(
            {
                "name": "Lotte",
                "done": [1, 2],
                "doneW": {"campus": [1, 2], "winter": [3]},
                "path": {"cherny": "deep"},
                "log": [{"n": 1, "at": "2026-09-16T18:00", "note": "old"}],
            }
        )
    )
    s = State.load(p)
    assert s.version == 2
    assert s.done == [1, 2] and s.done_w["winter"] == [3]
    assert s.path == {"cherny": "deep"}
    assert s.log[0].n == 1 and s.log[0].world == "campus"


def test_state_refuses_a_newer_version(tmp_path: Path) -> None:
    p = tmp_path / "state.json"
    p.write_text(json.dumps({"version": 99, "name": "x"}))
    with pytest.raises(ValueError, match="version 99"):
        State.load(p)


def test_progress_code_round_trip_and_version_gate() -> None:
    s = State(name="Lotte")
    s.mark_done("campus", 3, xp=100)
    s.path["karpathy"] = "deep"
    code = s.to_code()
    assert "=" not in code
    payload = decode_code(code)
    assert payload["v"] == 2 and payload["done"] == [3]
    other = State()
    other.merge_code(code)
    assert other.done == [3] and other.path["karpathy"] == "deep" and other.xp == 100
    with pytest.raises(ValueError):
        decode_code("definitely not base64 json")
    import base64

    newer = base64.urlsafe_b64encode(json.dumps({"v": 9}).encode()).decode()
    with pytest.raises(ValueError, match="newer"):
        decode_code(newer)


# ---- config --------------------------------------------------------------------


def test_config_defaults_and_round_trip(tmp_path: Path) -> None:
    p = tmp_path / "grimoire.toml"
    cfg = Config()
    cfg.save(p)
    assert Config.load(p) == cfg
    assert cfg.learner.difficulty == "normal" and len(cfg.finale.dates) == 6


def test_config_refuses_unknown_keys(tmp_path: Path) -> None:
    p = tmp_path / "grimoire.toml"
    p.write_text('[learner]\nname = "x"\ndifficulty = "insane"\n[typo]\nx = 1\n')
    with pytest.raises(ValueError) as e:
        Config.load(p)
    assert "difficulty" in str(e.value) and "typo" in str(e.value)


def test_committed_config_is_valid() -> None:
    cfg = Config.load(ROOT / "grimoire.toml")
    assert cfg.learner.persona in PERSONAS
    assert cfg.theme.preset in THEMES


# ---- quests --------------------------------------------------------------------


def test_levels_mirror_the_ages_of_the_tech_tree() -> None:
    ages = [(a[0], a[2]) for a in campaign.ages()]
    assert [(a, lab) for a, lab, _ in LEVELS] == ages


def test_level_for_and_xp_multipliers() -> None:
    assert level_for(0)[:2] == ("dark", "Intern")
    assert level_for(299)[1] == "Intern" and level_for(300)[1] == "Junior"
    assert level_for(5000) == ("future", "Expert", None)
    assert xp_for("normal") == 100 and xp_for("god") == 300
    assert required_levels("beginner") == {"lenient"}
    assert required_levels("hard") == {"lenient", "strict"}
    assert required_levels("god") == {"lenient", "strict", "extra"}


def test_every_workstream_has_a_quest_with_hints() -> None:
    cfg = Config()
    for world in campaign.evenings():
        for n in range(1, 9):
            q = quest_for(world, n, cfg)
            assert q.checks, (world, n)
            assert all(c.hint for c in q.checks)


def test_workstream_two_passes_in_this_repo() -> None:
    q = quest_for("campus", 2, Config())
    results = [c.run(Config()) for c in q.checks]
    assert all(r.ok for r in results), [(r.name, r.detail) for r in results]


# ---- vault ---------------------------------------------------------------------


def test_safe_title_strips_what_obsidian_refuses() -> None:
    assert safe_title("CI/CD and automation") == "CI-CD and automation"
    assert (
        safe_title("TOML in practice: pyproject.toml")
        == "TOML in practice - pyproject.toml"
    )
    assert safe_title('a"b*c?d<e>f\\g') == "abcdefg"


def test_vault_build_is_lint_clean_in_a_fresh_folder(tmp_path: Path) -> None:
    cfg = Config.model_validate({"vault": {"path": str(tmp_path), "folder": "G"}})
    state = State(name="Lotte")
    state.mark_done("campus", 1, note="a game", xp=100)
    state.path["cherny"] = "deep"
    v = Vault(cfg, state)
    paths = v.build(get_persona("data-engineer"))
    assert len(paths) > 60
    report = v.lint()
    assert report.ok, (report.orphans, report.dead_links, report.no_frontmatter)
    tonight = v.path("Tonight").read_text()
    assert "[[Innovation Hub]]" in tonight and "Level Intern" in tonight
    assert v.path("Map").read_text().count("flowchart") == 2
    assert v.path("Cookbook").exists() and v.path("Your field").exists()


def test_vault_build_log_and_upsert(tmp_path: Path) -> None:
    cfg = Config.model_validate({"vault": {"path": str(tmp_path), "folder": "G"}})
    v = Vault(cfg, State())
    v.build(get_persona("chief-of-staff"))
    v.add_build_log("[[Map]] regenerated")
    v.build(get_persona("chief-of-staff"))
    text = v.path("Tonight").read_text()
    assert text.count("[[Map]] regenerated") == 1
    v.upsert_dated("Innovation Hub", summary="s", bullets=["one"], tags=["workstream"])
    v.upsert_dated("Innovation Hub", summary="s", bullets=["two"], tags=["workstream"])
    note = v.path("Innovation Hub").read_text()
    assert note.index("- two") < note.index("- one")


# ---- scores, personas, themes, toolbelt -----------------------------------------


def test_scores_summary_and_sql() -> None:
    data = summary(read_scores())
    assert data["runs"] >= 8 and data["best"] >= data["mean"]
    df = run_sql("top_runs")
    assert list(df.columns) == ["played_at", "player", "score"] and df.height == 5


def test_personas_are_complete() -> None:
    assert len(PERSONAS) == 6
    for p in PERSONAS.values():
        assert len(p.dataset.rows) == 8 and len(p.recipes) == 3
        assert p.dataset.to_csv().splitlines()[0] == ",".join(p.dataset.columns)
        assert all(1 <= r.workstream <= 8 for r in p.recipes)


def test_themes_load_and_serialise(tmp_path: Path) -> None:
    for name in THEMES:
        t = load_theme(name)
        assert t.pairing_kind == "none" or len(t.pairings) == 8
    text = THEMES["seminar"].to_toml()
    assert 'tone = "academic"' in text
    with pytest.raises(ValueError, match="unknown theme"):
        load_theme("no-such-theme")


def test_toolbelt_entries_are_documented() -> None:
    ids = [t.id for t in TOOLS]
    assert len(ids) == len(set(ids))
    for t in TOOLS:
        assert t.install and t.url.startswith("https://")
    assert DIFFICULTIES["god"].xp_multiplier == 3.0


# ---- the command line ------------------------------------------------------------


def test_cli_status_json_and_export() -> None:
    runner = CliRunner()
    r = runner.invoke(cli, ["status", "--json"])
    assert r.exit_code == 0, r.output
    data = json.loads(r.output)
    assert set(data) >= {"name", "xp", "level", "done", "persona", "difficulty"}
    r = runner.invoke(cli, ["export"])
    assert r.exit_code == 0 and decode_code(r.output.strip())["v"] == 2


def test_note_methods_bootstrap_into_a_fresh_vault(tmp_path: Path) -> None:
    from grimoire.methods import METHODS, get_method

    assert len(METHODS) == 8
    cfg = Config.model_validate({"vault": {"path": str(tmp_path), "folder": "G"}})
    v = Vault(cfg, State())
    v.build(get_persona("chief-of-staff"))
    m = get_method("zettelkasten")
    base = v.dir / "Methods" / m.name
    for folder in m.folders:
        (base / folder).mkdir(parents=True)
    v.write(f"Method - {m.name}", m.hub, tags=["tech"])
    v.add_build_log(f"[[Method - {m.name}]] bootstrapped")
    report = v.lint()
    assert report.ok, (report.orphans, report.dead_links)
    assert all(t.filename.endswith(".md") and "{{" in t.body for t in m.templates)
    with pytest.raises(ValueError, match="unknown method"):
        get_method("no-such-method")


def test_cli_lists_personas_and_themes() -> None:
    runner = CliRunner()
    assert "data-engineer" in runner.invoke(cli, ["persona"]).output
    assert "field-guide" in runner.invoke(cli, ["theme"]).output
    assert "god" in runner.invoke(cli, ["difficulty"]).output
    assert runner.invoke(cli, ["check", "42"]).exit_code != 0
