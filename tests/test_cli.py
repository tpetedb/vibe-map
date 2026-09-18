"""The terminal companion: state, config, quests, vault, scores, personas, themes."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest
from click.testing import CliRunner

from tests.conftest import ROOT, encode_progress
from vibemap import campaign, project
from vibemap.cli import cli
from vibemap.config import DIFFICULTIES, Config
from vibemap.personas import PERSONAS, get_persona
from vibemap.quests import (
    LEVELS,
    level_for,
    mentor_quest,
    quest_for,
    required_levels,
    xp_for,
)
from vibemap.scores import read_scores, run_sql, summary
from vibemap.state import State, decode_code
from vibemap.themes import THEMES, load_theme
from vibemap.toolbelt import TOOLS
from vibemap.vault import Vault, safe_title

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
    p = tmp_path / "config" / "camp.toml"
    cfg = Config()
    cfg.save(p)
    assert Config.load(p) == cfg
    assert cfg.learner.difficulty == "normal" and len(cfg.finale.dates) == 6


def test_config_refuses_unknown_keys(tmp_path: Path) -> None:
    p = tmp_path / "camp.toml"
    p.write_text('[learner]\nname = "x"\ndifficulty = "insane"\n[typo]\nx = 1\n')
    with pytest.raises(ValueError) as e:
        Config.load(p)
    assert "difficulty" in str(e.value) and "typo" in str(e.value)


def test_committed_config_is_valid() -> None:
    cfg = Config.load(project.config_path(ROOT))
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


def test_vault_rewrite_keeps_the_original_date(tmp_path: Path) -> None:
    cfg = Config.model_validate({"vault": {"path": str(tmp_path), "folder": "G"}})
    v = Vault(cfg, State())
    p = v.write("Stable", "first", tags=["concept"])
    text = p.read_text().replace("date: 20", "date: 19")
    p.write_text(text)
    v.write("Stable", "second", tags=["concept"])
    again = p.read_text()
    assert "date: 19" in again and "second" in again


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
    # One heading per day: the second entry joins the first instead of racing it.
    assert note.count(f"## {date.today().isoformat()}") == 1
    assert note.index("- one") < note.index("- two")


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
    from vibemap.methods import METHODS, get_method

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


# ---- a camp on the command line ---------------------------------------------


def _camp(tmp_path: Path) -> Path:
    camp = tmp_path / "camp"
    out = CliRunner().invoke(cli, ["new", str(camp), "--name", "Tom"])
    assert out.exit_code == 0, out.output
    return camp


def _run(camp: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "vibemap.cli", *args],
        cwd=camp,
        env=dict(os.environ, VIBE_HOME=str(camp), COLUMNS="200"),
        capture_output=True,
        text=True,
    )


def test_a_camp_without_scores_says_so_instead_of_crashing(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    for args in (("scores",), ("scores", "--sql", "top_runs")):
        out = _run(camp, *args)
        assert out.returncode == 1, out.stdout
        assert "no scores yet" in out.stdout
        assert "Traceback" not in out.stderr


def test_the_name_from_camp_toml_reaches_the_state_and_the_vault(
    tmp_path: Path,
) -> None:
    camp = _camp(tmp_path)
    assert 'name = "Tom"' in (camp / "config" / "camp.toml").read_text()
    out = _run(camp, "status", "--json")
    assert json.loads(out.stdout)["name"] == "Tom", out.stdout
    out = _run(camp, "name", "Lotte")
    assert out.returncode == 0, out.stdout + out.stderr
    assert "vault rebuilt" in out.stdout
    assert "Lotte" in (camp / "vault" / "Camp" / "Tonight.md").read_text()
    assert json.loads(_run(camp, "status", "--json").stdout)["name"] == "Lotte"


def test_status_congratulates_a_finished_campaign(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    state = json.loads((camp / ".vibe" / "state.json").read_text())
    state["doneW"] = {w: list(range(1, 9)) for w in ("campus", "winter")}
    (camp / ".vibe" / "state.json").write_text(json.dumps(state))
    assert "Next island" in _run(camp, "status").stdout
    state["doneW"] = {
        w: list(range(1, 9)) for w in ("campus", "winter", "desert", "prod")
    }
    (camp / ".vibe" / "state.json").write_text(json.dumps(state))
    out = _run(camp, "status").stdout
    assert "All 32 stops done" in out and "winter 1" not in out


def test_undo_gives_the_stop_and_the_xp_back(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    assert _run(camp, "done", "1", "I built it", "--force").returncode == 0
    before = json.loads(_run(camp, "status", "--json").stdout)
    assert before["done"]["campus"] == [1] and before["xp"] > 0
    # Forcing a stop that is already done changes nothing.
    again = _run(camp, "done", "1", "--force")
    assert "already done" in again.stdout
    assert json.loads(_run(camp, "status", "--json").stdout)["xp"] == before["xp"]
    out = _run(camp, "undo", "1")
    assert "is open again" in out.stdout, out.stdout + out.stderr
    after = json.loads(_run(camp, "status", "--json").stdout)
    assert after["done"]["campus"] == [] and after["xp"] == 0
    assert "not done" in _run(camp, "undo", "1").stdout + _run(camp, "undo", "1").stderr


def test_vault_build_counts_the_folder_and_theme_knows_it_is_a_camp(
    tmp_path: Path,
) -> None:
    camp = _camp(tmp_path)
    out = _run(camp, "vault", "build").stdout
    count = int(out.split(":")[1].strip().split(" ")[0])
    on_disk = len(list((camp / "vault" / "Camp").rglob("*.md")))
    assert count == on_disk
    theme = _run(camp, "theme", "seminar").stdout
    assert "just build" not in theme and "product repository" in theme


def test_news_help_names_both_files() -> None:
    out = CliRunner().invoke(cli, ["news", "--help"]).output
    assert "data/news.json" in out and ".vibe/news.json" in out


def test_skills_are_counted_once() -> None:
    from vibemap.quests import _c2_skill, _skills

    paths = _skills()
    assert len(paths) == len({p.resolve() for p in paths})
    ok, detail = _c2_skill(Config())
    assert ok and detail.startswith(f"{len(paths)} skill")


def test_a_tool_without_a_version_flag_still_reads_as_installed() -> None:
    from vibemap.quests import _plain
    from vibemap.toolbelt import TOOLS_BY_ID, Tool

    assert TOOLS_BY_ID["obsidian"].version_args == ("version",)
    # `false` exists and exits 1: the binary is the proof, not its output.
    assert Tool("f", "f", "w", "false", "i", "https://x.test", "core").version() == (
        "installed"
    )
    assert _plain("\x1b[31m3 passed\x1b[0m\n") == "3 passed"
    assert "just verify" in DIFFICULTIES["god"].blurb
    assert "camp" in DIFFICULTIES["god"].blurb


# ---- mentor encounters ---------------------------------------------------------


def test_every_mentor_has_a_sourced_encounter_with_a_small_exercise() -> None:
    for m in campaign.mentors():
        enc = m["encounter"]
        assert 3 <= len(enc["dialogue"]) <= 4, m["id"]
        for line in enc["dialogue"]:
            assert line["you"] and line["m"]
            # Every mentor line is a paraphrase with the source it came from.
            assert m["src"][line["src"]][1].startswith("https://"), m["id"]
        ex = enc["exercise"]
        assert ex["dir"] == f"workspace/mentors/{m['id']}"
        assert ex["minutes"] <= 15 and ex["steps"] and ex["done"]
        assert ex.get("run") or ex.get("sections") or ex.get("contains"), m["id"]
        assert enc["plaque"]


def test_every_mentor_quest_has_checks_with_hints() -> None:
    cfg = Config.model_validate({"learner": {"difficulty": "god"}})
    for m in campaign.mentors():
        q = mentor_quest(m["id"], cfg)
        assert len(q.checks) == 2 and all(c.hint for c in q.checks)


def test_a_mentor_exercise_is_checked_in_the_workspace(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    out = _run(camp, "check", "--mentor", "torvalds")
    assert out.returncode == 1, out.stdout + out.stderr
    assert "does not exist" in out.stdout
    here = camp / "workspace" / "mentors" / "torvalds"
    here.mkdir(parents=True)
    (here / "hash.py").write_text(
        "import hashlib\n"
        "body = b'what is up, doc?'\n"
        "store = b'blob ' + str(len(body)).encode() + b'\\x00' + body\n"
        "print(hashlib.sha1(store).hexdigest())\n"
    )
    (here / "notes.md").write_text(
        "## What I learned\nA commit is named by the hash of its content, "
        "so the name and the bytes can never drift apart, which is why git "
        "can tell in one command whether anything changed at all.\n"
    )
    out = _run(camp, "check", "--mentor", "torvalds")
    assert out.returncode == 0, out.stdout + out.stderr
    assert "pass" in out.stdout and "+" in out.stdout
    state = json.loads((camp / ".vibe" / "state.json").read_text())
    assert state["mentors"] == ["torvalds"] and state["xp"] > 0
    note = (camp / "vault" / "Camp" / "Linus Torvalds.md").read_text()
    assert "Status: done" in note


def test_a_wrong_exercise_fails_with_the_expected_line(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    here = camp / "workspace" / "mentors" / "karpathy"
    here.mkdir(parents=True)
    (here / "bigram.py").write_text("print('after a: q')\n")
    out = _run(camp, "check", "--mentor", "karpathy")
    assert "fail" in out.stdout and "after a: t" in out.stdout
    assert json.loads((camp / ".vibe" / "state.json").read_text())["mentors"] == []


def test_the_progress_code_carries_verified_mentors() -> None:
    s = State(name="Lotte")
    s.mentors.append("torvalds")
    payload = decode_code(s.to_code())
    assert payload["v"] == 2 and payload["mentors"] == ["torvalds"]
    back = State()
    back.merge_code(s.to_code())
    assert back.mentors == ["torvalds"]
    # A code from before the encounters is still a valid version 2 code.
    old = State(name="Lotte")
    assert old.merge_code(encode_progress(done_w={"campus": [1]})) and old.mentors == []


def test_an_unknown_mentor_id_is_refused(tmp_path: Path) -> None:
    out = _run(_camp(tmp_path), "check", "--mentor", "nobody")
    assert out.returncode == 1 and "unknown mentor" in out.stdout


def test_mentor_start_scaffolds_the_folder_without_passing_the_check(
    tmp_path: Path,
) -> None:
    camp = _camp(tmp_path)
    out = _run(camp, "mentor", "hashimoto", "--start")
    assert out.returncode == 0, out.stdout + out.stderr
    here = camp / "workspace" / "mentors" / "hashimoto"
    assert (here / "config.ghostty").exists() and (here / "notes.md").exists()
    assert "One readable config file" in out.stdout and "10 minutes" in out.stdout
    assert "vibe check --mentor hashimoto" in out.stdout
    # A scaffold is a starting point: the check stays red and says what is missing.
    out = _run(camp, "check", "--mentor", "hashimoto")
    assert "fail" in out.stdout and "config.ghostty" in out.stdout
    assert json.loads((camp / ".vibe" / "state.json").read_text())["mentors"] == []
    # Work already in the folder is never overwritten.
    (here / "notes.md").write_text("## What I learned\nMine.\n")
    out = _run(camp, "mentor", "hashimoto", "--start")
    assert "kept your" in out.stdout
    assert "Mine." in (here / "notes.md").read_text()


def test_every_scaffolded_exercise_starts_red(tmp_path: Path, monkeypatch) -> None:
    from vibemap import quests as quests_module
    from vibemap.cli import _scaffold_mentor
    from vibemap.quests import run_quest

    monkeypatch.setattr(quests_module, "MENTORS_DIR", tmp_path)
    cfg = Config.model_validate({"learner": {"difficulty": "god"}})
    for m in campaign.mentors():
        _scaffold_mentor(m)
        results = run_quest(mentor_quest(m["id"], cfg), cfg)
        assert not all(r.ok for r in results), m["id"]


def test_mentor_lists_the_twelve_and_refuses_an_unknown_id(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    out = _run(camp, "mentor")
    assert out.returncode == 0, out.stdout + out.stderr
    for m in campaign.mentors():
        assert m["id"] in out.stdout
    assert "Innovation Campus" in out.stdout and "not yet" in out.stdout
    out = _run(camp, "mentor", "nobody")
    assert out.returncode == 1 and "unknown mentor" in out.stdout


def test_status_counts_encounters_and_artifacts(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    state_path = camp / ".vibe" / "state.json"
    state = json.loads(state_path.read_text())
    state["mentors"] = ["torvalds"]
    state["artifacts"] = ["dock"]
    state["artifactsBuilt"] = ["dock"]
    state_path.write_text(json.dumps(state))
    out = _run(camp, "status")
    assert "1/12 mentors met" in out.stdout, out.stdout
    assert "1/20 artifacts (1 built for real)" in out.stdout
    data = json.loads(_run(camp, "status", "--json").stdout)
    assert data["mentors"] == ["torvalds"] and data["artifacts"] == ["dock"]
    assert data["artifacts_built"] == ["dock"]
    # The keys the regeneration scripts already read are still there.
    assert set(data) >= {"name", "xp", "level", "done", "persona", "difficulty"}


# ---- exit codes, crashes and imported progress (the X0 hunt) --------------------


def test_vibe_check_exits_1_when_a_check_fails_and_0_when_they_pass(
    tmp_path: Path,
) -> None:
    """A course that teaches CI lets its own checks be a step in a pipeline."""
    camp = _camp(tmp_path)
    red = _run(camp, "check", "-w", "campus", "1")
    assert red.returncode == 1, red.stdout
    # --no-claim changes what is recorded, never the code.
    assert _run(camp, "check", "-w", "campus", "1", "--no-claim").returncode == 1

    (camp / "workspace" / "game").mkdir(parents=True, exist_ok=True)
    (camp / "workspace" / "game" / "index.html").write_text(
        "<canvas></canvas><script>let score=0</script>" + "x" * 900, encoding="utf-8"
    )
    green = _run(camp, "check", "-w", "campus", "1", "--no-claim")
    assert green.returncode == 0, green.stdout


def test_a_strict_check_on_an_empty_camp_never_prints_a_traceback(
    tmp_path: Path,
) -> None:
    camp = _camp(tmp_path)
    assert _run(camp, "difficulty", "god").returncode == 0
    for args in (("check", "-w", "campus", "1"), ("check", "-w", "campus", "3")):
        out = _run(camp, *args)
        assert "check crashed" not in out.stdout, out.stdout
        assert "Error" not in out.stdout, out.stdout
    first = _run(camp, "check", "-w", "campus", "1").stdout
    assert "workspace/game/index.html does not exist" in first, first


def test_imported_progress_is_half_and_a_passing_check_pays_the_rest(
    tmp_path: Path,
) -> None:
    camp = _camp(tmp_path)
    code = encode_progress(name="Tom", done_w={"campus": [1]})
    out = _run(camp, "import", code)
    assert out.returncode == 0, out.stdout + out.stderr
    assert "imported, not verified" in out.stdout, out.stdout
    assert "vibe check 1" in out.stdout
    state = json.loads((camp / ".vibe" / "state.json").read_text())
    full = xp_for(Config().learner.difficulty)
    assert state["xp"] == full // 2

    # The status grid says which stops are claims and which are verified.
    assert "claimed in the game, not verified here" in _run(camp, "status").stdout

    (camp / "workspace" / "game").mkdir(parents=True, exist_ok=True)
    (camp / "workspace" / "game" / "index.html").write_text(
        "<canvas></canvas><script>let score=0</script>" + "x" * 900, encoding="utf-8"
    )
    paid = _run(camp, "check", "-w", "campus", "1")
    assert paid.returncode == 0, paid.stdout
    assert "verified" in paid.stdout, paid.stdout
    state = json.loads((camp / ".vibe" / "state.json").read_text())
    assert state["xp"] == full
    # Verified now, so the check does not pay twice.
    assert _run(camp, "check", "-w", "campus", "1").returncode == 0
    assert json.loads((camp / ".vibe" / "state.json").read_text())["xp"] == full
