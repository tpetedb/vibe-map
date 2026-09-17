"""Every stop on winter, desert and production is checked against a deliverable.

A fresh camp is red everywhere. The same camp, with the files each stop asks
for written into it, is green everywhere. The fork challenges of the new
production stop get their own scripted fork, and the game shows that stop on
the production island.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from click.testing import CliRunner

from tests.conftest import encode_progress
from vibemap import campaign, quests
from vibemap.cli import cli
from vibemap.vault import safe_title

ROOT = Path(__file__).resolve().parents[1]
WORLDS = ("winter", "desert", "prod")

OWN_NOTE = """Tonight I did the work myself and wrote it down while it was
still fresh. The agent drafted, I rewrote the half that made no sense, and the
check told me what was still missing before I could claim the stop. What I
learned is that the deliverable is the point: the file on disk is what the
check reads, and the note is what I will read again. See [[Git]] and
[[Docker and containers]] for the parts I had to look up twice.
"""


def _camp(tmp_path: Path) -> Path:
    camp = tmp_path / "camp"
    out = CliRunner().invoke(cli, ["new", str(camp), "--name", "T"])
    assert out.exit_code == 0, out.output
    return camp


def _vibe(camp: Path, *args: str) -> str:
    env = dict(os.environ, VIBE_HOME=str(camp))
    out = subprocess.run(
        [sys.executable, "-m", "vibemap.cli", *args],
        cwd=camp,
        env=env,
        capture_output=True,
        text=True,
    )
    return out.stdout + out.stderr


def _island(camp: Path, world: str) -> str:
    return _vibe(camp, "check", "--all", "--no-claim", "-w", world)


def _git(camp: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=camp, check=True, capture_output=True)


def _write(camp: Path, rel: str, text: str) -> None:
    p = camp / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _write_notes(camp: Path) -> None:
    """The floor under every stop: the learner's own words in every note."""
    for world in WORLDS:
        for ws in campaign.evenings()[world].workstreams:
            note = camp / "vault" / "Camp" / f"{safe_title(ws.name)}.md"
            text = note.read_text(encoding="utf-8")
            assert "not done yet" in text, ws.name
            note.write_text(
                text.replace(
                    "- not done yet; run `vibe check` when it is",
                    "\n".join(f"- {line}" for line in OWN_NOTE.strip().splitlines()),
                ),
                encoding="utf-8",
            )


MERMAID = """# The transformer block
Tokens go in, attention mixes them, the block repeats.

```mermaid
flowchart LR
  A[token] --> B[embedding]
  B --> C[attention]
  C --> D[feed forward]
```

Attention is the part that looks at every other token in the window.
A token is a chunk of text, not a word, which is why counting letters fails.
"""

LOCAL_MODEL = """# A model on my own laptop
I ran ollama run llama3.2 and asked it the three questions I asked Claude.
It was faster to start and much worse at long instructions.
The GPU tab in Activity Monitor lit up while it answered.
Licences: Llama has a community licence, Apache-2.0 has none of that.
Question one: it invented a plausible source.
Question two: it refused for no reason.
Question three: it was fine, and offline, which is the point.
"""

DOTFOLDERS = """# Every dot entry, one line each
- .git: the repository itself, every version of every file.
- .gitignore: the list of paths git is told to leave alone.
- .env: secrets for this folder, never committed.
- .venv: the Python environment uv builds here.
- .claude: Claude Code's settings, hooks and agents for this camp.
- .agents: skills in the Agent Skills standard, read by every agent.
- .github: what GitHub runs for me, workflows and templates.
- .vibe: my progress state, ignored by git.
"""

SPEC = """# Nicknames for players

## Why
Two players share a first name and the leaderboard is confusing.

## What
A player may set a nickname; the leaderboard shows it instead of the name.

## Not this
No profiles, no avatars, no login.
No migration of the rows already in scores.csv.

## Files
workspace/python/scores.py reads it; workspace/sql/top_runs.sql groups on it.

## Done when
The nickname appears in scores.csv and the tests cover an empty one.
A run with no nickname still shows the name, and the test says so.
"""

CI = """name: checks
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pipx run ruff check .
      - run: pipx run pytest -q
"""

COMPARISON = """# Two agents, one task
I asked opencode and codex for the same test on scores.py.
opencode: slower to start, picked up AGENTS.md without being told.
codex: faster, ignored the skill until I named it.
Both wrote a test that passed on the first run.
opencode needed the model set by hand.
codex asked before writing the file.
I would keep opencode for the local model and codex for speed.
"""

INSTALL_SH = """#!/usr/bin/env bash
# Symlink every config back into place.
set -euo pipefail
ln -sf "$PWD/zshrc" "$HOME/.zshrc"
"""


def _write_deliverables(camp: Path) -> None:
    """One deliverable per stop, exactly what the hint asks for."""
    _write(camp, "workspace/winter/backprop/lecun1989.py", "print('one epoch')\n")
    _write(camp, "workspace/winter/transformer.md", MERMAID)
    _write(camp, "workspace/winter/local-model.md", LOCAL_MODEL)
    _write(camp, "workspace/winter/makemore/train.py", "print('makemore')\n")
    _write(
        camp,
        "workspace/winter/makemore/samples.txt",
        "\n".join(f"name{i}" for i in range(12)) + "\n",
    )

    agents = camp / "AGENTS.md"
    agents.write_text(
        agents.read_text(encoding="utf-8")
        + "\n## The dial\n\nscratch/ is vibe-only. workspace/python needs tests "
        "before anything is merged.\n",
        encoding="utf-8",
    )
    _write(camp, "workspace/desert/dotfiles.md", DOTFOLDERS)
    _write(
        camp,
        "workspace/python/test_scores.py",
        "def test_mean_of_one_row():\n    assert sum([3]) / 1 == 3\n",
    )
    _write(camp, "workspace/specs/nickname.md", SPEC)
    _write(camp, ".github/workflows/checks.yml", CI)
    _write(camp, "workspace/jobs/nightly.sh", "#!/usr/bin/env bash\necho nightly\n")
    _write(
        camp,
        "workspace/jobs/log.csv",
        "started,ended,exit\n08:00,08:01,0\n09:00,09:01,0\n",
    )
    _write(
        camp,
        "workspace/evals/cases.csv",
        "prompt,expected\n" + "".join(f"q{i},yes\n" for i in range(6)),
    )
    _write(camp, "workspace/evals/run.py", "print('score: 5/6')\n")

    settings = camp / ".claude" / "settings.json"
    data = json.loads(settings.read_text(encoding="utf-8"))
    data["hooks"]["Stop"] = [
        {"hooks": [{"type": "command", "command": "pytest -q", "timeout": 60}]}
    ]
    data["permissions"] = {
        "allow": ["Bash(pytest*)", "Bash(ruff*)", "Bash(git status*)"]
    }
    settings.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    _write(
        camp,
        "workspace/dotfiles/Brewfile",
        "brew 'starship'\nbrew 'fzf'\nbrew 'ripgrep'\nbrew 'bat'\ncask 'ghostty'\n",
    )
    _write(camp, "workspace/dotfiles/ghostty/config", "font-size = 14\n")
    _write(camp, "workspace/dotfiles/zshrc", 'eval "$(starship init zsh)"\n')
    _write(camp, "workspace/dotfiles/README.md", "# My dotfiles\nRun install.sh.\n")
    _write(camp, "workspace/dotfiles/install.sh", INSTALL_SH)
    _write(camp, "workspace/agents/comparison.md", COMPARISON)

    dots = camp / "workspace" / "dotfiles"
    _git(dots, "init", "-q")
    _commit(dots, "mine")

    # `vibe new` already made the camp a repository; the stop asks for a remote,
    # a second branch and history the learner rewrote.
    _git(camp, "remote", "add", "origin", "https://github.com/learner/my-camp.git")
    _commit(camp, "the deliverables of the evening")
    _git(camp, "switch", "-qc", "feature/nickname")
    _git(camp, "reset", "-q", "--hard", "HEAD")


def _commit(repo: Path, message: str) -> None:
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.email=t@e.st", "-c", "user.name=T", "commit", "-qm", message)


def _scripted_fork(camp: Path) -> None:
    """The four challenges, done: made, configured, extended, broken, repaired."""
    made = _vibe(camp, "fork", "--from", str(ROOT))
    assert "files" in made, made
    fork = camp / quests.FORK_DIR

    cfg_js = fork / "src" / "config" / "00-config.js"
    cfg_js.write_text(
        cfg_js.read_text(encoding="utf-8").replace(
            "const WORLD_SCALE=1.6;", "const WORLD_SCALE=2.4;"
        ),
        encoding="utf-8",
    )

    local = fork / "tools" / "generated" / "campaign.json"
    data = json.loads(local.read_text(encoding="utf-8"))
    data["evenings"]["prod"]["ws"].append(
        {"h": "Stop 9", "n": "Context engineering, my own stop", "d": "from the news"}
    )
    local.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    boot = fork / "src" / "game" / "90-boot.js"
    broken = boot.with_suffix(".js.off")
    boot.rename(broken)
    _record(fork, expect_ok=False)
    broken.rename(boot)
    _record(fork, expect_ok=True)


def _record(fork: Path, *, expect_ok: bool) -> None:
    out = subprocess.run(
        [sys.executable, "tools/record_build.py"],
        cwd=fork,
        capture_output=True,
        text=True,
    )
    assert out.returncode == 0, out.stdout + out.stderr
    said = "build passed" if expect_ok else "build failed"
    assert said in out.stdout, out.stdout


def test_a_fresh_camp_fails_every_stop(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    for world in WORLDS:
        output = _island(camp, world)
        assert "all checks pass" not in output, output
        assert output.count("not yet.") == 8, output


def test_scripted_deliverables_pass_every_stop(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    _write_notes(camp)
    _write_deliverables(camp)
    _scripted_fork(camp)
    for world in WORLDS:
        output = _island(camp, world)
        assert output.count("all checks pass") == 8, output
        assert "not yet." not in output, output


def test_each_fork_challenge_is_checked_on_its_own(tmp_path: Path) -> None:
    camp = _camp(tmp_path)
    for challenge in quests.FORK_CHALLENGES:
        assert "not yet." in _vibe(camp, "check", "--fork", challenge), challenge
    _scripted_fork(camp)
    for challenge in quests.FORK_CHALLENGES:
        output = _vibe(camp, "check", "--fork", challenge)
        assert "your fork builds and is yours" in output, (challenge, output)
    unknown = _vibe(camp, "check", "--fork", "sideways")
    assert "unknown fork challenge" in unknown, unknown


def test_reading_only_stops_say_so_and_still_need_the_note() -> None:
    from vibemap.config import Config

    cfg = Config()
    for world, n in sorted(quests.READING_ONLY):
        quest = quests.quest_for(world, n, cfg)
        assert quest.checks[0].name.startswith("reading only:"), quest.checks[0].name
        assert (world, n) not in quests.STOP_CHECKS
    for world in WORLDS:
        for n in range(1, 9):
            has_deliverable = (world, n) in quests.STOP_CHECKS
            assert has_deliverable is ((world, n) not in quests.READING_ONLY), (
                world,
                n,
            )


def test_the_production_island_shows_the_forking_stop(game) -> None:
    """The prod island still lays out eight plots; the sixth is the fork now."""
    game.goto()
    game.start("Lotte")
    game.import_code(encode_progress(done_w={"campus": [], "prod": [1, 2, 3, 4, 5]}))
    game.page.evaluate("setWorld('prod')")
    game.page.wait_for_function("() => window.__S().world === 'prod'")
    game.open_roadmap()
    buttons = game.workstream_buttons()
    assert len(buttons) == 8
    assert "Fork the game" in (buttons[5].text_content() or "")
    buttons[5].click()
    game.page.wait_for_selector("#sheet .screen.on", state="attached")
    text = game.page.text_content("#sheet .screen.on") or ""
    for word in ("vibe fork", "src/config/00-config.js", "vibe check --fork"):
        assert word in text, word
    game.screenshot("stops_prod_fork", clip_height=860)
    game.assert_clean()
