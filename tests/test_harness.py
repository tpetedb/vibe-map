"""The harness: one source in .agents/ and config.toml, the client files rendered.

Most tests copy the harness sources into a scratch git repository, because the
generator reads tracked files only and its promises are about what a checkout
holds. The model table, the profiles and the rendered outputs are also read
straight from this repository, since those are what the clients load.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

from tests.conftest import ROOT
from tools import work

spec = importlib.util.spec_from_file_location(
    "harness", ROOT / ".agents" / "utils" / "harness.py"
)
assert spec and spec.loader
harness = importlib.util.module_from_spec(spec)
sys.modules["harness"] = harness
spec.loader.exec_module(harness)

SOURCES = ("config.toml", ".agents/conf", ".agents/context", ".agents/templates")
OUTPUTS = (
    "CLAUDE.md",
    ".claude/settings.json",
    ".claude/agents",
    ".codex/config.toml",
    ".codex/hooks.json",
    ".codex/agents",
    ".agents/generated.lock",
)


def sh(root: Path, *args: str) -> str:
    out = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=True
    )
    return out.stdout.strip()


def copy(rel: str, dest: Path) -> None:
    src = ROOT / rel
    if src.is_dir():
        shutil.copytree(src, dest / rel)
    else:
        (dest / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dest / rel)


def commit(root: Path) -> None:
    sh(root, "add", "-A")
    sh(root, "commit", "-qm", "x")


@pytest.fixture(autouse=True)
def isolated(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """No test reads this machine's Codex home or git identity."""
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "codex-home"))
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", "/dev/null")
    monkeypatch.setenv("GIT_CONFIG_SYSTEM", "/dev/null")
    monkeypatch.setenv("GIT_AUTHOR_NAME", "t")
    monkeypatch.setenv("GIT_AUTHOR_EMAIL", "t@example.org")
    monkeypatch.setenv("GIT_COMMITTER_NAME", "t")
    monkeypatch.setenv("GIT_COMMITTER_EMAIL", "t@example.org")


@pytest.fixture
def tree(tmp_path: Path) -> Path:
    """The harness sources and their committed outputs, two small skills and a
    root AGENTS.md, in a git repository of their own."""
    root = tmp_path / "repo"
    root.mkdir()
    sh(root, "init", "-q", "-b", "main")
    for rel in (*SOURCES, *OUTPUTS, ".agents/utils/harness.py"):
        copy(rel, root)
    for name in ("alpha", "beta"):
        skill = root / ".agents" / "skills" / name
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(f"---\nname: {name}\n---\n")
    (root / "AGENTS.md").write_text("# agents\n")
    (root / ".gitignore").write_text(".claude/skills/\n.agents/config.local.toml\n")
    commit(root)
    return root


def edit(path: Path, old: str, new: str) -> None:
    text = path.read_text()
    assert old in text, f"{old!r} not in {path}"
    path.write_text(text.replace(old, new, 1))


# ------------------------------------------------------------ the root config


def test_the_root_config_carries_every_knob_and_nothing_else() -> None:
    config = harness.load_config(ROOT)
    assert set(config) == {
        "version",
        "profile",
        "safeguards",
        "autonomy",
        "providers",
        "agents",
        "models",
        "usage",
    }
    assert set(config["usage"]) == {"claude", "openai"}


def test_the_three_profiles_are_complete_and_alike() -> None:
    folder = ROOT / ".agents" / "conf" / "profiles"
    assert sorted(p.stem for p in folder.glob("*.toml")) == [
        "balanced",
        "fast",
        "strict",
    ]
    keys = {
        p.stem: set(harness.flat(harness.load_profile(ROOT, p.stem)))
        for p in folder.glob("*.toml")
    }
    assert keys["strict"] == keys["balanced"] == keys["fast"]
    assert keys["strict"] == set(harness.flat(harness.PROFILE))


def test_a_profile_cannot_inherit(tree: Path) -> None:
    edit(
        tree / ".agents/conf/profiles/fast.toml",
        "version = 1\n",
        'version = 1\nextends = "balanced"\n',
    )
    with pytest.raises(harness.Bad, match="unknown key extends"):
        harness.load_profile(tree, "fast")


def test_an_unknown_key_in_the_root_config_fails_loudly(tree: Path) -> None:
    edit(tree / "config.toml", "agents = 4", 'agents = 4\ncolour = "red"')
    with pytest.raises(harness.Bad, match="config.toml: unknown key colour"):
        harness.load_config(tree)


def test_an_unknown_profile_fails_loudly(tree: Path) -> None:
    edit(tree / "config.toml", 'profile = "balanced"', 'profile = "turbo"')
    with pytest.raises(harness.Bad, match="no .agents/conf/profiles/turbo.toml"):
        harness.load_config(tree)


def test_an_unknown_version_is_refused(tree: Path) -> None:
    edit(tree / "config.toml", "version = 1", "version = 2")
    with pytest.raises(harness.Bad, match="version = 2"):
        harness.load_config(tree)


# ------------------------------------------------------------ the model table


def test_haiku_takes_no_effort() -> None:
    assert harness.model_effort("claude", "claude-haiku-4-5", "low") is None
    assert harness.model_effort("claude", "claude-sonnet-5", "low") == "low"


@pytest.mark.parametrize(
    ("old", "new", "why"),
    [
        (
            'effort = { claude = "max", openai = "ultra" }',
            'effort = { claude = "max", openai = "max" }',
            "'max' is not a openai level",
        ),
        (
            'effort = { claude = "max", openai = "ultra" }',
            'effort = { claude = "ultra", openai = "ultra" }',
            "'ultra' is not a claude level",
        ),
    ],
)
def test_max_is_claude_only_and_ultra_codex_only(
    tree: Path, old: str, new: str, why: str
) -> None:
    edit(tree / ".agents/conf/models/tom.toml", old, new)
    with pytest.raises(harness.Bad, match=why):
        harness.load_models(tree, "tom")


def test_a_role_naming_an_unknown_alias_is_refused(tree: Path) -> None:
    edit(
        tree / ".agents/conf/models/tom.toml", 'claude = ["opus"]', 'claude = ["opsu"]'
    )
    with pytest.raises(harness.Bad, match="'opsu' is not in ids.claude"):
        harness.load_models(tree, "tom")


def test_an_id_the_client_does_not_list_is_reported() -> None:
    models = harness.load_models(ROOT, "tom")
    listed = {"gpt-6-sol": {"high", "medium"}, "gpt-5.6-terra": {"low"}}
    bad, notes = harness.model_problems(models, {"openai": listed, "claude": None})
    assert any("gpt-6-astra is not in the client's model list" in b for b in bad)
    assert not any("gpt-6-sol is not" in b for b in bad)
    assert any("claude ids: unknown" in n for n in notes)
    assert any("gpt-5.6-terra is listed by the client now" in n for n in notes)


def test_an_effort_the_client_does_not_offer_for_that_model_is_reported() -> None:
    models = harness.load_models(ROOT, "tom")
    listed = {
        mid: {"low", "medium", "high"} for mid in models["ids"]["openai"].values()
    }
    bad, _ = harness.model_problems(models, {"openai": listed})
    assert any("gpt-6-astra offers no effort ultra" in b for b in bad)


def test_tom_s_preferences_are_what_pick_returns() -> None:
    assert harness.pick("builder", "claude", root=ROOT) == ("claude-opus-5-5", "high")
    assert harness.pick("builder", "codex", root=ROOT) == ("gpt-6-sol", "high")
    assert harness.pick("design", "codex", root=ROOT) == ("gpt-6-astra", "high")
    assert harness.pick("coordinate", "claude", root=ROOT)[0] == "claude-fable-5-1"
    assert harness.pick("hard", "claude", root=ROOT) == ("claude-fable-5-1", "max")
    assert harness.pick("hard", "codex", root=ROOT) == ("gpt-6-astra", "ultra")


def test_pick_requires_a_provider() -> None:
    with pytest.raises(SystemExit) as e:
        harness.main(["pick", "builder"])
    assert e.value.code == 2


def test_pick_never_returns_another_providers_model(tree: Path) -> None:
    models = harness.load_models(ROOT, "tom")
    for mrole in models["roles"]:
        for provider, vendor in (("claude", "claude"), ("codex", "openai")):
            if vendor in models["roles"][mrole]:
                model_id, _ = harness.pick(mrole, provider, root=ROOT)
                assert model_id in models["ids"][vendor].values()
    edit(
        tree / ".agents/conf/models/tom.toml",
        "[roles.design]                       # Astra for beautiful design\n"
        'openai = ["astra"]\nclaude = ["opus"]\n'
        'effort = { claude = "high", openai = "high" }',
        '[roles.design]\nopenai = ["astra"]\neffort = { openai = "high" }',
    )
    with pytest.raises(harness.Bad, match="names no claude model"):
        harness.pick("design", "claude", root=tree)


def test_pick_steps_down_at_slow_at_and_pauses_at_stop_at() -> None:
    assert harness.pick("cheap", "claude", 0.1, ROOT) == ("claude-sonnet-5", "low")
    assert harness.pick("cheap", "claude", 0.7, ROOT) == ("claude-haiku-4-5", None)
    with pytest.raises(harness.Paused):
        harness.pick("cheap", "claude", 0.9, ROOT)


# ------------------------------------------------------------ the floor


@pytest.mark.parametrize(
    "overlay",
    [
        'local_checks = "nearest"',
        "loop = { iterations = 50 }",
        "claude = { allowUnsandboxedCommands = true }",
        "mcp_servers = 0\nreview = { independent = 0 }",
    ],
)
def test_a_private_overlay_weaker_than_the_floor_is_refused_before_spawn(
    tree: Path, overlay: str
) -> None:
    (tree / ".agents" / "config.local.toml").write_text(f"version = 1\n{overlay}\n")
    with pytest.raises(harness.Refused, match="weaker than"):
        harness.effective(tree)
    with pytest.raises(harness.Refused):
        harness.pick("builder", "claude", root=tree)


def test_a_host_overlay_can_never_reach_full_access(tree: Path) -> None:
    (tree / ".agents" / "config.local.toml").write_text(
        'version = 1\ncodex = { sandbox_mode = "danger-full-access" }\n'
    )
    with pytest.raises(harness.Bad, match="danger-full-access"):
        harness.effective(tree)


def test_a_stronger_overlay_applies_and_names_itself(tree: Path) -> None:
    (tree / ".agents" / "config.local.toml").write_text(
        'version = 1\nlocal_checks = "affected-plus-security"\n'
        "loop = { iterations = 10 }\n"
    )
    _, values = harness.effective(tree)
    assert values["local_checks"] == harness.Value(
        "affected-plus-security", ".agents/config.local.toml"
    )
    assert values["loop.iterations"].value == 10
    assert values["loop.wall_minutes"].source.endswith("balanced.toml")


def test_the_root_safeguards_knob_cannot_go_below_the_profile(tree: Path) -> None:
    edit(tree / "config.toml", 'safeguards = "profile"', 'safeguards = "light"')
    with pytest.raises(harness.Refused, match="safeguards = 'light'"):
        harness.effective(tree)


def test_ralph_runs_only_in_the_container(tree: Path) -> None:
    edit(tree / "config.toml", 'autonomy = "lead"', 'autonomy = "ralph"')
    with pytest.raises(harness.Refused, match="ralph"):
        harness.effective(tree)


# ------------------------------------------------------------ rendered outputs


def test_the_codex_project_file_carries_only_what_a_project_may_set() -> None:
    text = (ROOT / ".codex" / "config.toml").read_text()
    config = tomllib.loads(text)
    ignored = (
        "profile",
        "profiles",
        "model_provider",
        "model_providers",
        "openai_base_url",
        "chatgpt_base_url",
        "notify",
        "otel",
    )
    assert not set(ignored) & set(config)
    assert config["sandbox_mode"] == "workspace-write"
    assert "permissions" not in config and "default_permissions" not in config
    # A tracked writable root breaks every shell tool in a linked worktree; the
    # board is added at launch with --add-dir (A2 as amended on the #192 review).
    assert "writable_roots" not in json.dumps(config)


def test_every_agent_renders_for_both_clients_with_its_role_model() -> None:
    models = harness.load_models(ROOT, "tom")
    for role in harness.load_roles(ROOT, models):
        md = (ROOT / ".claude" / "agents" / f"{role['name']}.md").read_text()
        codex = tomllib.loads(
            (ROOT / ".codex" / "agents" / f"{role['name']}.toml").read_text()
        )
        assert codex["developer_instructions"] == role["instructions"]
        if role.get("model_role"):
            claude_id, effort = harness.role_model(models, role["model_role"], "claude")
            assert f"\nmodel: {claude_id}\n" in md and f"\neffort: {effort}\n" in md
            openai_id, _ = harness.role_model(models, role["model_role"], "openai")
            assert codex["model"] == openai_id
        else:
            assert "\nmodel:" not in md and "model" not in codex


def test_the_hooks_are_the_same_set_on_both_clients() -> None:
    claude = json.loads((ROOT / ".claude" / "settings.json").read_text())["hooks"]
    codex = json.loads((ROOT / ".codex" / "hooks.json").read_text())["hooks"]
    assert list(claude) == list(codex)
    for event in ("PreToolUse", "SubagentStop", "Stop"):
        assert claude[event] == codex[event]


def test_the_toml_writer_reads_back_what_it_wrote() -> None:
    doc = {
        "a": 'quote " and \\ back',
        "b": 'multi\nline """ three\n',
        "t": {"x-y": [1, True], ".z": 0.5},
    }
    assert tomllib.loads(harness.dump_toml(doc, "# h")) == doc


# ------------------------------------------------------------ check and sync


def test_check_is_clean_on_a_copy_of_this_tree(tree: Path) -> None:
    assert harness.check(tree) == []


def test_check_names_an_output_edited_by_hand(tree: Path) -> None:
    edit(tree / ".claude/settings.json", '"timeout": 20', '"timeout": 21')
    assert "edited by hand or stale: .claude/settings.json" in harness.check(tree)


def test_check_names_an_input_changed_without_a_sync(tree: Path) -> None:
    edit(tree / ".agents/conf/models/tom.toml", 'openai = ["sol"]', 'openai = ["luna"]')
    drift = harness.check(tree)
    assert "input changed since the last sync: .agents/conf/models/tom.toml" in drift
    assert "differs from a fresh render: .codex/agents/builder.toml" in drift


@pytest.mark.skipif(not shutil.which("uv"), reason="sync renders through uv")
def test_sync_renders_from_tracked_input_only(tree: Path) -> None:
    """The committed outputs come back byte for byte from the sources, and a
    private overlay changes none of them."""
    for rel in OUTPUTS:
        p = tree / rel
        shutil.rmtree(p) if p.is_dir() else p.unlink()
    (tree / ".agents" / "config.local.toml").write_text(
        'version = 1\nlocal_checks = "affected-plus-security"\n'
    )
    out = subprocess.run(
        [sys.executable, ".agents/utils/harness.py", "sync"],
        cwd=tree,
        capture_output=True,
        text=True,
        check=False,
        env={k: v for k, v in os.environ.items() if k != "HARNESS_REEXEC"},
    )
    assert out.returncode == 0, out.stderr
    for rel in OUTPUTS:
        a, b = ROOT / rel, tree / rel
        files = sorted(a.rglob("*")) if a.is_dir() else [a]
        for f in files:
            if f.is_file():
                other = b / f.relative_to(a) if a.is_dir() else b
                if rel == ".agents/generated.lock":
                    continue  # it hashes this repository's harness.py and inputs
                assert other.read_bytes() == f.read_bytes(), f"{f} differs"
    assert harness.check(tree) == []


# ------------------------------------------------------------ doctor


def test_the_skill_links_are_relative_idempotent_and_repaired(tree: Path) -> None:
    done = harness.link_skills(tree, can_link=True)
    assert done == ["linked .claude/skills/alpha", "linked .claude/skills/beta"]
    link = tree / ".claude" / "skills" / "alpha"
    assert os.readlink(link) == "../../.agents/skills/alpha"
    assert harness.link_skills(tree, can_link=True) == []
    link.unlink()
    link.symlink_to(tree / ".agents" / "skills" / "alpha")  # absolute
    (tree / ".claude" / "skills" / "gone").symlink_to("../../.agents/skills/gone")
    assert harness.link_problems(tree) == [".claude/skills/alpha is an absolute link"]
    assert harness.link_skills(tree, can_link=True) == [
        "linked .claude/skills/alpha",
        "removed .claude/skills/gone",
    ]
    assert os.readlink(link) == "../../.agents/skills/alpha"
    assert harness.link_problems(tree) == []


def test_the_skills_are_copied_when_links_cannot_be_made(tree: Path) -> None:
    done = harness.link_skills(tree, can_link=False)
    assert done == ["copied .claude/skills/alpha", "copied .claude/skills/beta"]
    copied = tree / ".claude" / "skills" / "alpha"
    assert copied.is_dir() and not copied.is_symlink()
    assert harness.link_skills(tree, can_link=False) == []
    (tree / ".agents" / "skills" / "alpha" / "SKILL.md").write_text("changed\n")
    assert harness.link_skills(tree, can_link=False) == ["copied .claude/skills/alpha"]
    assert (copied / "SKILL.md").read_text() == "changed\n"


def test_every_root_to_leaf_chain_of_this_repository_is_measured() -> None:
    chains = harness.agents_chains(ROOT)
    leaves = {leaf for leaf, _, _ in chains}
    files = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "*AGENTS.md"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    dirs = {str(Path(f).parent) for f in files}
    for d in dirs:
        assert d in leaves or any(
            leaf.startswith(f"{d}/") or d == "." for leaf in leaves
        )
    for _, size, chain in chains:
        assert chain[0] == "AGENTS.md" and size <= 24 * 1024


def test_a_chain_over_the_budget_fails_the_doctor(tree: Path) -> None:
    (tree / "AGENTS.md").write_text("r" * 20 * 1024)
    (tree / "deep").mkdir()
    (tree / "deep" / "AGENTS.md").write_text("d" * 5 * 1024)
    commit(tree)
    [(leaf, size, chain)] = harness.agents_chains(tree)
    assert (leaf, chain) == ("deep", ["AGENTS.md", "deep/AGENTS.md"])
    assert size > 24 * 1024
    bad, _ = harness.doctor(tree)
    assert any(b.startswith("chain deep:") for b in bad)


def test_the_doctor_reports_project_trust_and_hook_trust_apart(tree: Path) -> None:
    home = Path(os.environ["CODEX_HOME"])
    home.mkdir()
    assert harness.project_trust(tree)[0] == "missing"
    assert harness.hook_trust(tree, "0.156.1")[0] == "missing"
    assert harness.hook_trust(tree, "9.9.9")[0] == "unknown"
    main = harness.main_checkout(tree)
    hooks = tree / ".codex" / "hooks.json"
    events = json.loads(hooks.read_text())["hooks"]
    snake = {e: re.sub(r"(?<!^)(?=[A-Z])", "_", e).lower() for e in events}
    state = "".join(
        f'[hooks.state."{hooks}:{snake[e]}:0:0"]\ntrusted_hash = "sha256:0"\n'
        for e in events
    )
    (home / "config.toml").write_text(
        f'[projects."{main}"]\ntrust_level = "trusted"\n{state}'
    )
    assert harness.project_trust(tree)[0] == "verified"
    state_now, why = harness.hook_trust(tree, "0.156.1")
    assert state_now == "unknown" and "/hooks" in why
    _, report = harness.doctor(tree)
    lines = [r for r in report if r.startswith("codex ")]
    assert [r.split(":")[0] for r in lines] == [
        "codex project trust",
        "codex hook trust",
    ]


def test_a_linked_worktree_is_trusted_and_hooked_the_way_codex_resolves_it(
    tree: Path,
) -> None:
    """Codex 0.156.1 decides a checkout's trust by its own entry first, then the
    main checkout's, and takes a linked worktree's project hooks from the main
    checkout's .codex/, keyed by that path (openai/codex PR 21969)."""
    home = Path(os.environ["CODEX_HOME"])
    home.mkdir()
    wt = tree.parent / "wt"
    sh(tree, "worktree", "add", "-q", "-b", "wt", str(wt))
    wt = wt.resolve()
    main = harness.main_checkout(wt)
    assert main == tree.resolve()
    config = home / "config.toml"
    config.write_text(f'[projects."{main}"]\ntrust_level = "trusted"\n')
    state, why = harness.project_trust(wt)
    assert state == "verified" and str(main) in why
    config.write_text(
        f'[projects."{main}"]\ntrust_level = "trusted"\n'
        f'[projects."{wt}"]\ntrust_level = "untrusted"\n'
    )
    assert harness.project_trust(wt)[0] == "missing"
    config.write_text(f'[projects."{wt}"]\ntrust_level = "trusted"\n')
    state, why = harness.project_trust(wt)
    assert state == "verified" and str(wt) in why

    events = json.loads((wt / ".codex" / "hooks.json").read_text())["hooks"]
    snake = {e: re.sub(r"(?<!^)(?=[A-Z])", "_", e).lower() for e in events}

    def approved(checkout: Path) -> str:
        path = checkout / ".codex" / "hooks.json"
        return "".join(
            f'[hooks.state."{path}:{snake[e]}:0:0"]\ntrusted_hash = "sha256:0"\n'
            for e in events
        )

    config.write_text(f'[projects."{main}"]\ntrust_level = "trusted"\n{approved(wt)}')
    assert harness.hook_trust(wt, "0.156.1")[0] == "missing"
    config.write_text(f'[projects."{main}"]\ntrust_level = "trusted"\n{approved(main)}')
    assert harness.hook_trust(wt, "0.156.1")[0] == "unknown"


def test_explain_names_the_source_and_the_boundary_of_every_value() -> None:
    rows = harness.explain(ROOT)
    boundaries = set(harness.APPLIES.values())
    keys = {r["key"] for r in rows}
    for key in ("profile", "agents", "usage.claude.slow_at", "codex.sandbox_mode"):
        assert key in keys
    assert "models.build.claude" in keys and "hooks.PreToolUse" in keys
    for r in rows:
        assert (ROOT / r["source"]).is_file(), r
        assert r["applies"] in boundaries, r


# ------------------------------------------------------------ work.py


def test_work_py_takes_lock_listed_outputs_as_regenerable(tree: Path) -> None:
    for rel in ("tools/work.py", "tools/sync_main.py", "work/teams.toml"):
        copy(rel, tree)
    folder = tree / "work" / "orders" / "one"
    folder.mkdir(parents=True)
    (folder / "order.toml").write_text(
        'v = 1\nid = "one"\ntitle = "t"\nteam = "harness"\nbranch = "feat/x"\n'
        'builder = "b"\nowns = ["tools/x.py"]\ncross = []\nneeds = []\n'
        '[[criteria]]\nid = "c1"\ntext = "t"\ncheck = "true"\n'
    )
    order = work.find("one", tree)
    # As a hook or a recipe runs it: a fresh interpreter that never saw harness.py.
    cold = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; sys.path.insert(0, 'tools'); import work;"
            " print(work.find('one', work.Path('.')).may_touch('CLAUDE.md'))",
        ],
        cwd=tree,
        capture_output=True,
        text=True,
        check=False,
    )
    assert cold.stdout.strip() == "True", cold.stderr
    assert order.may_touch(".claude/settings.json")
    assert order.may_touch(".codex/agents/builder.toml")
    assert not order.may_touch("docs/SKILLS.md")
    lock = tree / ".agents" / "generated.lock"
    edit(lock, "[outputs]\n", '[outputs]\n"docs/SKILLS.md" = "sha256:0"\n')
    with pytest.raises(work.Bad, match="docs/SKILLS.md.*does not render"):
        order.may_touch("docs/SKILLS.md")


@pytest.mark.skipif(not shutil.which("uv"), reason="sync renders through uv")
def test_a_hand_edit_to_a_lock_listed_output_is_refused(tree: Path) -> None:
    """Lock-listed outputs leave owns only while harness.py check reproduces
    them: a regeneration passes, a hand edit to the rendered deny floor by an
    order that does not own it fails the edit hook, work-check and CI."""
    for rel in ("tools/work.py", "tools/sync_main.py", "work/teams.toml"):
        copy(rel, tree)
    folder = tree / "work" / "orders" / "one"
    folder.mkdir(parents=True)
    (folder / "order.toml").write_text(
        'v = 1\nid = "one"\ntitle = "t"\nteam = "harness"\nbranch = "feat/x"\n'
        'builder = "b"\nowns = ["config.toml", ".agents/generated.lock"]\n'
        "cross = []\nneeds = []\n"
        '[[criteria]]\nid = "c1"\ntext = "t"\ncheck = "true"\n'
    )
    with (tree / ".gitignore").open("a") as f:
        f.write("__pycache__/\n")
    commit(tree)
    sh(tree, "checkout", "-qb", "feat/x")
    order = work.find("one", tree)
    edit(tree / "config.toml", 'profile = "balanced"', 'profile = "strict"')
    subprocess.run(
        [sys.executable, ".agents/utils/harness.py", "sync"],
        cwd=tree,
        capture_output=True,
        check=True,
    )
    moved = set(work.changed(tree, "main"))
    assert moved & work.regenerable(tree) - {".agents/generated.lock"}
    assert work.strays(order, "main") == []
    commit(tree)
    assert work.strays(order, "main", work.diff_names(tree, "main"), "HEAD") == []

    settings = tree / ".claude" / "settings.json"
    code, why = work.hook_pre_tool({"tool_input": {"file_path": str(settings)}})
    assert code == 2 and "harness.py sync" in why
    settings.write_text(settings.read_text().replace("{", "{ ", 1))
    out = work.strays(order, "main")
    assert [s for s in out if s.startswith(".claude/settings.json")], out
    commit(tree)
    out = work.strays(order, "main", work.diff_names(tree, "main"), "HEAD")
    assert [s for s in out if s.startswith(".claude/settings.json")], out


# ------------------------------------------------------------ the docs


FENCE = re.compile(r"^```toml[^\n]*\n(.*?)^```", re.S | re.M)


def toml_blocks() -> list[tuple[str, int, str]]:
    files = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "docs", ".agents/README.md"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    paths = [ROOT / f for f in files if f.endswith(".md")]
    common = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "--path-format=absolute"]
        + ["--git-common-dir"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    decision = Path(common) / "board" / "harness" / "DECISION-final.md"
    if decision.is_file():  # the runtime store: on a person's clone, not in CI
        paths.append(decision)
    return [
        (str(p), i, m.group(1))
        for p in paths
        for i, m in enumerate(FENCE.finditer(p.read_text(encoding="utf-8")))
    ]


def test_the_readme_points_at_the_decision_copy() -> None:
    readme = (ROOT / ".agents" / "README.md").read_text()
    assert "board/harness/DECISION-final.md" in readme


@pytest.mark.parametrize(("path", "index", "block"), toml_blocks())
def test_every_fenced_toml_block_parses(path: str, index: int, block: str) -> None:
    try:
        tomllib.loads(block)
    except tomllib.TOMLDecodeError as e:
        pytest.fail(f"{path}, toml block {index + 1}: {e}")
