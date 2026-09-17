"""Quests: every workstream has checks that look at what was actually built.

`vibe check 3` runs the checks for workstream 3 of the current world and
awards XP when they pass. Difficulty decides which checks are required:
lenient ones everywhere, strict ones from hard up, extra ones from expert up.
Levels mirror the ages of the tech tree.
"""

from __future__ import annotations

import datetime as dt
import json
import re
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from vibemap import campaign, project
from vibemap.config import DIFFICULTIES, Config
from vibemap.state import State
from vibemap.vault import learner_sections, safe_title

ROOT = project.root()
XP_BASE = 100
Level = Literal["lenient", "strict", "extra"]

# (age id, level label, xp needed). The names are the ages of vibemap/tech.py;
# tests assert the two lists agree.
LEVELS: tuple[tuple[str, str, int], ...] = (
    ("dark", "Intern", 0),
    ("feudal", "Junior", 300),
    ("castle", "Medior", 800),
    ("imperial", "Senior", 1500),
    ("future", "Expert", 2400),
)


def level_for(xp: int) -> tuple[str, str, int | None]:
    """Return (age id, label, xp for the next level or None at the top)."""
    current = LEVELS[0]
    nxt: int | None = None
    for i, (age, label, need) in enumerate(LEVELS):
        if xp >= need:
            current = (age, label, need)
            nxt = LEVELS[i + 1][2] if i + 1 < len(LEVELS) else None
    return current[0], current[1], nxt


@dataclass(frozen=True, slots=True)
class CheckResult:
    name: str
    ok: bool
    detail: str
    hint: str
    level: Level


@dataclass(frozen=True, slots=True)
class Check:
    name: str
    fn: Callable[[Config], tuple[bool, str]]
    hint: str
    level: Level = "lenient"

    def run(self, cfg: Config) -> CheckResult:
        try:
            ok, detail = self.fn(cfg)
        except Exception as e:  # reason: a check must never crash the CLI
            ok, detail = False, f"check crashed: {type(e).__name__}: {e}"
        return CheckResult(self.name, ok, detail, self.hint, self.level)


@dataclass(frozen=True, slots=True)
class Quest:
    world: str
    n: int
    title: str
    checks: tuple[Check, ...]


def required_levels(difficulty: str) -> set[Level]:
    preset = DIFFICULTIES[difficulty]
    levels: set[Level] = {"lenient"}
    if preset.strict:
        levels.add("strict")
    if preset.extra_checks:
        levels.add("extra")
    return levels


def xp_for(difficulty: str) -> int:
    return round(XP_BASE * DIFFICULTIES[difficulty].xp_multiplier)


# ---- helpers ------------------------------------------------------------------


# A check detail goes into a table, so the runner must not colour or wrap it.
PYTEST_PLAIN = ("--color=no", "-p", "no:cacheprovider")
ANSI = re.compile(r"\x1b\[[0-9;]*m")


def _plain(text: str) -> str:
    """Terminal output without escape codes, fit for one table cell."""
    return ANSI.sub("", text).strip()


def _git(*args: str) -> str:
    try:
        return subprocess.run(
            ["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=20
        ).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return ""


def _count_lines(p: Path) -> int:
    return sum(1 for line in p.read_text(encoding="utf-8").splitlines() if line.strip())


def _skills() -> list[Path]:
    """Every skill once: .claude/skills usually symlinks the .agents ones."""
    seen: set[Path] = set()
    out: list[Path] = []
    for p in sorted(ROOT.glob(".agents/skills/*/SKILL.md")) + sorted(
        ROOT.glob(".claude/skills/*/SKILL.md")
    ):
        key = p.resolve()
        if key not in seen:
            seen.add(key)
            out.append(p)
    return out


def _settings() -> dict:
    p = ROOT / ".claude" / "settings.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def _vault_report(cfg: Config):
    from vibemap.vault import Vault  # local: vault imports quests

    return Vault(cfg, State()).lint()


# ---- campus checks (the original eight workstreams) ---------------------------


def _c1_game(cfg: Config) -> tuple[bool, str]:
    p = ROOT / "workspace" / "game" / "index.html"
    if not p.exists():
        return False, "workspace/game/index.html does not exist"
    text = p.read_text(encoding="utf-8")
    if "Workstream 1 starts here" in text:
        return False, "workspace/game/index.html is still the placeholder"
    return len(text) > 800, f"workspace/game/index.html has {len(text)} bytes"


def _c1_game_strict(cfg: Config) -> tuple[bool, str]:
    text = (ROOT / "workspace" / "game" / "index.html").read_text(encoding="utf-8")
    has = "<script" in text and ("score" in text.lower() or "<canvas" in text)
    return (
        has,
        "a script and a score or a canvas"
        if has
        else "no script, score or canvas found",
    )


def _c2_agents_md(cfg: Config) -> tuple[bool, str]:
    p = ROOT / "AGENTS.md"
    if not p.exists():
        return False, "AGENTS.md is missing"
    n = _count_lines(p)
    return n >= 8, f"AGENTS.md has {n} lines"


def _c2_skill(cfg: Config) -> tuple[bool, str]:
    good = []
    for p in _skills():
        head = p.read_text(encoding="utf-8")
        if head.startswith("---") and "name:" in head and "description:" in head:
            good.append(p.parent.name)
    if not good:
        return False, "no skill with name and description in its frontmatter"
    shown = ", ".join(good[:3]) + (", ..." if len(good) > 3 else "")
    return True, f"{len(good)} skill(s) with valid frontmatter: {shown}"


def _c2_strict(cfg: Config) -> tuple[bool, str]:
    text = (ROOT / "AGENTS.md").read_text(encoding="utf-8").lower()
    ok = "## commands" in text and "test" in text
    return (
        ok,
        "AGENTS.md names commands and tests"
        if ok
        else "no Commands section with tests",
    )


def _c3_csv(cfg: Config) -> tuple[bool, str]:
    p = ROOT / "workspace" / "data" / "scores.csv"
    if not p.exists():
        return False, "workspace/data/scores.csv is missing"
    lines = p.read_text(encoding="utf-8").splitlines()
    ok = lines and lines[0] == "played_at,player,score,duration_s" and len(lines) >= 4
    return bool(ok), f"{max(len(lines) - 1, 0)} score rows"


def _c3_sql_py(cfg: Config) -> tuple[bool, str]:
    sqls = list((ROOT / "workspace" / "sql").glob("*.sql"))
    pys = list((ROOT / "workspace" / "python").glob("*.py"))
    return bool(sqls and pys), f"{len(sqls)} sql, {len(pys)} python files"


def _c3_strict(cfg: Config) -> tuple[bool, str]:
    from vibemap.scores import run_sql

    df = run_sql("top_runs")
    return df.height > 0, f"top_runs.sql returns {df.height} rows through DuckDB"


def _c4_commits(cfg: Config) -> tuple[bool, str]:
    n = int(_git("rev-list", "--count", "HEAD") or 0)
    return n >= 3, f"{n} commits"


def _c4_hook(cfg: Config) -> tuple[bool, str]:
    hooks = _settings().get("hooks", {})
    return bool(hooks), f"hooks configured: {', '.join(hooks) or 'none'}"


def _c4_strict(cfg: Config) -> tuple[bool, str]:
    n = int(_git("rev-list", "--count", "HEAD") or 0)
    return n >= 8, f"{n} commits (8 needed on strict)"


def _c5_mcp(cfg: Config) -> tuple[bool, str]:
    p = ROOT / ".mcp.json"
    if p.exists():
        servers = json.loads(p.read_text(encoding="utf-8")).get("mcpServers", {})
        if servers:
            return True, f".mcp.json servers: {', '.join(servers)}"
    if _settings().get("mcpServers"):
        return True, "mcpServers in .claude/settings.json"
    return False, "no .mcp.json with servers"


def _c6_vault(cfg: Config) -> tuple[bool, str]:
    r = _vault_report(cfg)
    ok = r.notes >= 6 and r.link_count() >= 12
    return ok, f"{r.notes} notes, {r.link_count()} wikilinks"


def _c6_strict(cfg: Config) -> tuple[bool, str]:
    r = _vault_report(cfg)
    return not r.dead_links, f"{len(r.dead_links)} dead links"


def _c7_pages(cfg: Config) -> tuple[bool, str]:
    wf = list((ROOT / ".github" / "workflows").glob("*.yml"))
    if any("pages" in p.read_text(encoding="utf-8") for p in wf):
        return True, "a Pages workflow exists"
    return _c7_strict(cfg)


def _c7_strict(cfg: Config) -> tuple[bool, str]:
    url = _git("remote", "get-url", "origin")
    m = re.search(r"github\.com[:/]([^/]+/[^/.]+)", url)
    if not m:
        return False, "no GitHub remote"
    try:
        out = subprocess.run(
            ["gh", "api", f"repos/{m.group(1)}/pages", "--jq", ".html_url"],
            capture_output=True, text=True, timeout=20,
        )  # fmt: skip
    except (OSError, subprocess.TimeoutExpired):
        return False, "gh not available"
    if out.returncode == 0 and out.stdout.strip():
        return True, f"Pages live at {out.stdout.strip()}"
    return False, "GitHub Pages is not enabled for the remote"


def _c8_subagent(cfg: Config) -> tuple[bool, str]:
    agents = list((ROOT / ".claude" / "agents").glob("*.md"))
    return bool(agents), f"subagents: {', '.join(p.stem for p in agents) or 'none'}"


def _c8_schedule(cfg: Config) -> tuple[bool, str]:
    wf = " ".join(
        p.read_text(encoding="utf-8")
        for p in (ROOT / ".github" / "workflows").glob("*.yml")
    )
    if "schedule:" in wf:
        return True, "a scheduled GitHub Actions workflow"
    scripts = " ".join(
        p.read_text(encoding="utf-8", errors="ignore")
        for p in (ROOT / "scripts").glob("*")
    )
    if re.search(r"claude\s+-p|codex exec|gemini -p|copilot -p|opencode run", scripts):
        return True, "a script runs an agent in print mode"
    try:
        cron = subprocess.run(
            ["crontab", "-l"], capture_output=True, text=True, timeout=10
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        cron = ""
    if "claude" in cron:
        return True, "crontab runs claude"
    return (
        False,
        "no schedule found (workflow schedule:, crontab, or a print-mode script)",
    )


def _is_product() -> bool:
    """The product checkout has the engine's tests; a camp has only its workspace."""
    return (ROOT / "tests" / "test_repo.py").exists()


def _extra_tests(cfg: Config) -> tuple[bool, str]:
    """Expert: tests exist and pass. The product runs its own gates; a camp runs
    whatever pytest finds under workspace/ (the learner's tests for their work)."""
    if _is_product():
        cmd = [
            "uv", "run", "--no-sync", "pytest", "-q", *PYTEST_PLAIN,
            "tests/test_repo.py", "tests/test_build.py",
        ]  # fmt: skip
    else:
        found = sorted((ROOT / "workspace").rglob("test_*.py"))
        if not found:
            return False, "no test_*.py under workspace/ (write one for your game)"
        cmd = ["python3", "-m", "pytest", "-q", *PYTEST_PLAIN, *[str(p) for p in found]]
    out = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=600)
    lines = _plain(out.stdout or out.stderr).splitlines()
    return out.returncode == 0, lines[-1] if lines else "no output"


def _extra_verify(cfg: Config) -> tuple[bool, str]:
    """God: the whole gate is green. The product runs just verify; a camp runs the
    vault lint and its workspace tests."""
    if _is_product():
        out = subprocess.run(
            ["just", "verify-quiet"],
            cwd=ROOT, capture_output=True, text=True, timeout=1200,
        )  # fmt: skip
        lines = _plain(out.stdout or out.stderr).splitlines()
        return out.returncode == 0, lines[-1] if lines else "no output"
    from vibemap.vault import Vault

    report = Vault(cfg, State.load()).lint()
    if not report.ok:
        return False, (
            f"vault lint: {len(report.orphans)} orphans, "
            f"{len(report.dead_links)} dead links"
        )
    ok, msg = _extra_tests(cfg)
    return ok, f"vault OK; {msg}"


# Links every generated note already carries; they prove nothing about a note.
def _generic_links() -> set[str]:
    return {"Tonight", "Map"} | {ev.short for ev in campaign.evenings().values()}


OWN_WORDS = 40  # the learner's own words a note needs before a stop counts


def _own_content(text: str, ws: campaign.Workstream) -> tuple[int, set[str], bool]:
    """(words, links, a dated entry of their own) for the learner's part of a note."""
    sections = learner_sections(text, tuple(u for _, u in ws.sources))
    own = [line for _, lines in sections for line in lines]
    words = sum(len(line.split()) for line in own)
    links = {m.strip() for line in own for m in re.findall(r"\[\[([^\]|#]+)", line)}
    dated = any(
        re.fullmatch(r"\d{4}-\d{2}-\d{2}", head) and lines for head, lines in sections
    )
    return words, links - _generic_links(), dated


def _note_check(world: str, n: int) -> Check:
    """The stop is done when the note holds the learner's own account of it.

    Everything vibe writes into the note itself (the stub, the claim bullets,
    the campaign sources) is ignored, so an untouched note never passes.
    """
    ws = campaign.evenings()[world].workstreams[n - 1]

    def fn(cfg: Config) -> tuple[bool, str]:
        p = cfg.vault_dir() / f"{safe_title(ws.name)}.md"
        if not p.exists():
            return False, f"no vault note called {safe_title(ws.name)}"
        words, links, dated = _own_content(p.read_text(encoding="utf-8"), ws)
        ok = dated and words >= OWN_WORDS and len(links) >= 2
        return ok, (
            f"{words} of your own words (needs {OWN_WORDS}), {len(links)} links "
            f"beyond the generated ones, dated entry: {'yes' if dated else 'no'}"
        )

    return Check(
        f"vault note for {ws.name}",
        fn,
        f"Write vault/Camp/{safe_title(ws.name)}.md in your own words: a "
        f"## dated section with at least {OWN_WORDS} words on what you did and "
        "learned, and two [[links]] to other notes.",
    )


def _note_strict(world: str, n: int) -> Check:
    ws = campaign.evenings()[world].workstreams[n - 1]

    def fn(cfg: Config) -> tuple[bool, str]:
        text = (cfg.vault_dir() / f"{safe_title(ws.name)}.md").read_text(
            encoding="utf-8"
        )
        sections = learner_sections(text, tuple(u for _, u in ws.sources))
        own_sources = [
            line
            for head, lines in sections
            if head == "Sources"
            for line in lines
            if "http" in line
        ]
        _, links, _ = _own_content(text, ws)
        ok = bool(own_sources) and len(links) >= 3
        return ok, (
            f"{len(own_sources)} source(s) you added, {len(links)} links"
            if ok
            else "needs a Sources line you added and three links of your own"
        )

    return Check(
        f"sources for {ws.name}",
        fn,
        "Add a line under ## Sources with something you actually read, and a "
        "third [[link]].",
        "strict",
    )


# ---- mentor encounters --------------------------------------------------------

# The exercise a mentor sets is small and offline: a file with a marker, a
# script that prints one expected line, or a note with a required section.
MENTORS_DIR = ROOT / "workspace" / "mentors"
MENTOR_XP_SHARE = 2  # a mentor exercise is worth half a workstream
MENTOR_NOTE = "notes.md"
MENTOR_SECTION = "## What I learned"
MENTOR_WORDS = 25


def mentor_dir(mentor_id: str) -> Path:
    return MENTORS_DIR / mentor_id


def _section_words(text: str, heading: str) -> int:
    """Words under `heading`, up to the next heading of the same or higher level."""
    lines = text.splitlines()
    level = len(heading) - len(heading.lstrip("#"))
    words = 0
    inside = False
    for line in lines:
        if line.strip().startswith("#"):
            here = len(line) - len(line.lstrip("#"))
            if line.strip().lower() == heading.lower():
                inside = True
                continue
            if inside and here <= level:
                break
            continue
        if inside:
            words += len(line.split())
    return words


def _run_exercise(path: Path) -> tuple[bool, str]:
    """Run the learner's script with the interpreter running vibe. Offline by
    design: nothing in an exercise needs the network."""
    try:
        out = subprocess.run(
            [sys.executable, path.name],
            cwd=path.parent,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        return False, f"{path.name} did not finish in 60 seconds"
    if out.returncode != 0:
        first = _plain(out.stderr).splitlines()
        return False, f"{path.name} failed: {first[-1] if first else 'no output'}"
    return True, _plain(out.stdout)


def _exercise_check(m: dict) -> Check:
    ex = m["encounter"]["exercise"]
    here = mentor_dir(m["id"])

    def fn(cfg: Config) -> tuple[bool, str]:
        p = here / ex["file"]
        if not p.exists():
            return False, f"{ex['dir']}/{ex['file']} does not exist"
        text = p.read_text(encoding="utf-8")
        missing = [s for s in ex.get("sections", ()) if s.lower() not in text.lower()]
        missing += [s for s in ex.get("contains", ()) if s not in text]
        if missing:
            return False, f"{ex['file']} is missing: {', '.join(missing)}"
        lines = [line for line in text.splitlines() if line.strip()]
        if len(lines) < ex.get("min_lines", 1):
            return (
                False,
                f"{ex['file']} has {len(lines)} lines, needs {ex['min_lines']}",
            )
        if not ex.get("run"):
            return True, f"{ex['file']} holds what the exercise asks for"
        ok, detail = _run_exercise(p)
        if not ok:
            return False, detail
        want = ex["prints"]
        return want in detail, (
            f"it printed {want!r}"
            if want in detail
            else f"expected {want!r}, got: {detail[:80]!r}"
        )

    return Check(
        ex["title"],
        fn,
        f"{ex['dir']}/: {ex['done']}. Steps: " + " ".join(ex["steps"]),
    )


def _mentor_note_check(m: dict) -> Check:
    here = mentor_dir(m["id"])

    def fn(cfg: Config) -> tuple[bool, str]:
        p = here / MENTOR_NOTE
        if not p.exists():
            return False, f"no {MENTOR_NOTE} in {m['encounter']['exercise']['dir']}"
        words = _section_words(p.read_text(encoding="utf-8"), MENTOR_SECTION)
        return words >= MENTOR_WORDS, (
            f"{words} of your own words under {MENTOR_SECTION} (needs {MENTOR_WORDS})"
        )

    return Check(
        f"your note on {m['name']}",
        fn,
        f"Write {m['encounter']['exercise']['dir']}/{MENTOR_NOTE} with a "
        f"{MENTOR_SECTION} section of at least {MENTOR_WORDS} words.",
        "strict",
    )


def mentor_quest(mentor_id: str, cfg: Config) -> Quest:
    """The quest for one mentor encounter: the exercise, then your own note."""
    m = campaign.mentor(mentor_id)
    checks = [_exercise_check(m), _mentor_note_check(m)]
    wanted = required_levels(cfg.learner.difficulty)
    return Quest(
        "mentor",
        0,
        f"{m['name']}: {m['encounter']['exercise']['title']}",
        tuple(c for c in checks if c.level in wanted),
    )


CAMPUS_CHECKS: dict[int, tuple[Check, ...]] = {
    1: (
        Check(
            "your game exists",
            _c1_game,
            "Ask the agent for one file, workspace/game/index.html, no libraries.",
        ),
        Check(
            "it is a game",
            _c1_game_strict,
            "It needs a script and a score or a canvas.",
            "strict",
        ),
    ),
    2: (
        Check(
            "AGENTS.md has rules",
            _c2_agents_md,
            "Write eight lines the agent must follow.",
        ),
        Check(
            "one skill exists",
            _c2_skill,
            "Add .agents/skills/<name>/SKILL.md with name and description.",
        ),
        Check(
            "commands and tests named",
            _c2_strict,
            "Add a Commands section that mentions tests.",
            "strict",
        ),
    ),
    3: (
        Check(
            "scores.csv has rows", _c3_csv, "Play three rounds and append the scores."
        ),
        Check(
            "sql and python exist",
            _c3_sql_py,
            "One query in workspace/sql/, one script in workspace/python/.",
        ),
        Check(
            "DuckDB runs top_runs.sql",
            _c3_strict,
            "brew install duckdb, then the query must run.",
            "strict",
        ),
    ),
    4: (
        Check(
            "three commits", _c4_commits, "git add -A && git commit -m 'what and why'"
        ),
        Check("a hook", _c4_hook, "Add a hooks block to .claude/settings.json."),
        Check(
            "eight commits",
            _c4_strict,
            "Commit after every change you would be sad to lose.",
            "strict",
        ),
    ),
    5: (Check("an MCP server", _c5_mcp, "claude mcp add <name> ... writes .mcp.json"),),
    6: (
        Check(
            "a linked vault",
            _c6_vault,
            "Six notes and twelve wikilinks; run vibe vault build.",
        ),
        Check("no dead links", _c6_strict, "vibe vault lint lists them.", "strict"),
    ),
    7: (
        Check("published", _c7_pages, "A Pages workflow, or gh api .../pages answers."),
        Check(
            "Pages is live", _c7_strict, "Settings, Pages, deploy from main.", "strict"
        ),
    ),
    8: (
        Check("a subagent", _c8_subagent, "Add .claude/agents/<name>.md."),
        Check(
            "a schedule",
            _c8_schedule,
            "A workflow with schedule:, a crontab line, or a print-mode script.",
        ),
    ),
}

EXTRA: tuple[Check, ...] = (
    Check(
        "repo tests pass",
        _extra_tests,
        "tests that pass (the product's, or yours under workspace/)",
        "extra",
    ),
)
GOD: tuple[Check, ...] = (
    Check(
        "the whole gate is green",
        _extra_verify,
        "just verify (product) or vault lint plus your tests (camp)",
        "extra",
    ),
)


def quest_for(world: str, n: int, cfg: Config) -> Quest:
    """The quest for one workstream, with the checks this difficulty requires."""
    ws = campaign.evenings()[world].workstreams[n - 1]
    if world == "campus":
        checks = list(CAMPUS_CHECKS[n])
    else:
        checks = [_note_check(world, n), _note_strict(world, n)]
    checks += list(EXTRA)
    if cfg.learner.difficulty == "god":
        checks += list(GOD)
    wanted = required_levels(cfg.learner.difficulty)
    return Quest(world, n, ws.name, tuple(c for c in checks if c.level in wanted))


def run_quest(quest: Quest, cfg: Config) -> list[CheckResult]:
    return [c.run(cfg) for c in quest.checks]


# ---- badges -------------------------------------------------------------------

BADGES: dict[str, str] = {
    "first-light": "First light: the first workstream done",
    "full-evening": "Full evening: eight of eight on one island",
    "campaign": "Campaign: all thirty-two stops",
    "streak-3": "Streak: three stops in one day",
    "linked": "Linked: twenty wikilinks in the vault",
    "shipped": "Shipped: GitHub Pages is live",
    "collector": "Collector: found every artifact on the island",
    "mentored": "Mentored: every mentor's exercise done for real",
}


def new_badges(state: State, cfg: Config) -> list[str]:
    earned = []
    if state.total_done() >= 1:
        earned.append("first-light")
    if any(len(v) >= 8 for v in state.done_w.values()):
        earned.append("full-evening")
    if state.total_done() >= 32:
        earned.append("campaign")
    if state.today_count() >= 3:
        earned.append("streak-3")
    try:
        if _vault_report(cfg).link_count() >= 20:
            earned.append("linked")
    except OSError:
        pass
    rec = state.checks.get("campus:7")
    if rec and rec.ok and any("live" in p for p in rec.passed):
        earned.append("shipped")
    if state.artifacts and len(state.artifacts) >= len(campaign.artifacts()):
        earned.append("collector")
    if len(state.mentors) >= len(campaign.mentors()):
        earned.append("mentored")
    fresh = [b for b in earned if b not in state.badges]
    state.badges.extend(fresh)
    return fresh


def stamp() -> str:
    return dt.datetime.now().isoformat(timespec="minutes")
