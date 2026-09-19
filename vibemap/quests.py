"""Quests: every workstream has checks that look at what was actually built.

`vibe check 3` runs the checks for workstream 3 of the current world and
awards XP when they pass. Difficulty decides which checks are required:
lenient ones everywhere, strict ones from hard up, extra ones from expert up.
Levels mirror the ages of the tech tree.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import yaml

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


def _shipped(rel: str) -> str | None:
    """The file `vibe new` wrote at this path, or None when it ships none.

    A check has to tell the learner's work from the camp's scaffolding, and
    the template inside the package is the only record of what was scaffolded.
    """
    with project.data_dir("template") as d:
        p = Path(d) / rel
        return p.read_text(encoding="utf-8") if p.is_file() else None


def _is_shipped(p: Path, rel: str) -> bool:
    """True when this file is still byte for byte the one the camp came with."""
    return p.is_file() and p.read_text(encoding="utf-8") == _shipped(rel)


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
    p = ROOT / "workspace" / "game" / "index.html"
    if not p.exists():
        return False, "workspace/game/index.html does not exist"
    text = p.read_text(encoding="utf-8")
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
    if _is_shipped(p, "AGENTS.md"):
        return False, f"AGENTS.md has {n} lines, still the ones `vibe new` wrote"
    return n >= 8, f"AGENTS.md has {n} lines of your own"


def _c2_skill(cfg: Config) -> tuple[bool, str]:
    good = []
    for p in _skills():
        head = p.read_text(encoding="utf-8")
        if not (head.startswith("---") and "name:" in head and "description:" in head):
            continue
        if _is_shipped(p, f"_agents/skills/{p.parent.name}/SKILL.md"):
            continue
        good.append(p.parent.name)
    if not good:
        return False, (
            f"{len(_skills())} skill(s), every one of them a skill the camp "
            "shipped with; write one of your own"
        )
    shown = ", ".join(good[:3]) + (", ..." if len(good) > 3 else "")
    return True, f"{len(good)} skill(s) of your own: {shown}"


def _c2_strict(cfg: Config) -> tuple[bool, str]:
    p = ROOT / "AGENTS.md"
    if not p.exists():
        return False, "AGENTS.md is missing"
    text = p.read_text(encoding="utf-8").lower()
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

    try:
        df = run_sql("top_runs")
    except FileNotFoundError:
        return False, "workspace/sql/top_runs.sql does not exist"
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


def _local_mcp_servers() -> list[str]:
    """Servers added without a scope: ~/.claude.json, under this camp's path.

    `claude mcp add` defaults to the local scope, so the lesson's command
    writes there and never to .mcp.json.
    See https://code.claude.com/docs/en/mcp#find-your-configuration-on-disk
    """
    p = Path.home() / ".claude.json"
    if not p.is_file():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    project_ = data.get("projects", {}).get(str(ROOT), {})
    return list(project_.get("mcpServers", {}))


def _c5_mcp(cfg: Config) -> tuple[bool, str]:
    p = ROOT / ".mcp.json"
    if p.exists():
        servers = json.loads(p.read_text(encoding="utf-8")).get("mcpServers", {})
        if servers:
            return True, f".mcp.json servers: {', '.join(servers)}"
    if _settings().get("mcpServers"):
        return True, "mcpServers in .claude/settings.json"
    local = _local_mcp_servers()
    if local:
        return True, f"local scope servers for this camp: {', '.join(local)}"
    return False, "no MCP server for this camp, in any scope"


def _c6_vault(cfg: Config) -> tuple[bool, str]:
    r = _vault_report(cfg)
    ok = r.own_notes >= 3 and r.own_link_count() >= 6
    return ok, (
        f"{r.own_notes} note(s) you wrote (needs 3) and "
        f"{r.own_link_count()} wikilink(s) of your own (needs 6), "
        f"in a vault of {r.notes} notes"
    )


def _c6_strict(cfg: Config) -> tuple[bool, str]:
    r = _vault_report(cfg)
    return not r.dead_links, f"{len(r.dead_links)} dead links"


def _c7_pages(cfg: Config) -> tuple[bool, str]:
    """A workflow of the learner's own, else the site itself.

    The camp ships `.github/workflows/pages.yml`, so its presence proves
    nothing; either the learner wrote the publishing or the site answers.
    """
    own = [
        p
        for p in (ROOT / ".github" / "workflows").glob("*.yml")
        if "pages" in p.read_text(encoding="utf-8")
        and not _is_shipped(p, f"_github/workflows/{p.name}")
    ]
    if own:
        return True, f"{own[0].name}, a Pages workflow of your own"
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
    plist = _launchd_agent()
    if plist:
        return True, f"a launchd agent runs it: {plist}"
    return (
        False,
        "no schedule found (workflow schedule:, launchd, crontab, "
        "or a print-mode script)",
    )


def _launchd_agent() -> str:
    """A launchd agent that runs an agent: the route stop 8 teaches on macOS."""
    folders = [Path.home() / "Library" / "LaunchAgents", ROOT, ROOT / "scripts"]
    for d in folders:
        for p in sorted(d.glob("*.plist")) if d.is_dir() else []:
            text = p.read_text(encoding="utf-8", errors="ignore")
            if "claude" in text or str(ROOT) in text:
                return p.name
    return ""


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


def _note_check(world: str, n: int, reading_only: bool = False) -> Check:
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
        f"reading only: your note on {ws.name}"
        if reading_only
        else f"vault note for {ws.name}",
        fn,
        f"Write vault/Camp/{safe_title(ws.name)}.md in your own words: a "
        f"## dated section with at least {OWN_WORDS} words on what you did and "
        "learned, and two [[links]] to other notes.",
    )


def _note_strict(world: str, n: int) -> Check:
    ws = campaign.evenings()[world].workstreams[n - 1]

    def fn(cfg: Config) -> tuple[bool, str]:
        note = cfg.vault_dir() / f"{safe_title(ws.name)}.md"
        if not note.exists():
            return False, f"{note.name} does not exist in the vault yet"
        text = note.read_text(encoding="utf-8")
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


def section_words(text: str, heading: str) -> int:
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
        words = section_words(p.read_text(encoding="utf-8"), MENTOR_SECTION)
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


# ---- the deliverable behind each stop -----------------------------------------

# Winter, desert and production stops leave something on the machine, and the
# check looks at it. Every hint names the path exactly: a check the learner
# cannot locate is a puzzle, not a gate.

# Stops whose only deliverable is the note: papers to read, history to follow.
READING_ONLY: frozenset[tuple[str, int]] = frozenset(
    {("winter", 2), ("winter", 4), ("winter", 5), ("winter", 7)}
)

# Terminal agents that read the same AGENTS.md; production stop 7 compares two.
OTHER_AGENTS = ("opencode", "codex", "gemini", "copilot", "cursor", "aider")


def _at(rel: str) -> Path:
    """A workspace path, resolved against this camp."""
    return ROOT / rel


def _body(p: Path) -> list[str]:
    """The non-empty lines of a file; an empty deliverable is not a deliverable."""
    text = p.read_text(encoding="utf-8", errors="ignore")
    return [line for line in text.splitlines() if line.strip()]


def _file_check(
    name: str,
    rel: str,
    hint: str,
    *,
    contains: tuple[str, ...] = (),
    any_of: tuple[str, ...] = (),
    min_lines: int = 1,
) -> Check:
    """One file is the deliverable: it exists, it says these things, it has body."""

    def fn(_: Config) -> tuple[bool, str]:
        p = _at(rel)
        if not p.is_file():
            return False, f"{rel} does not exist"
        lines = _body(p)
        text = "\n".join(lines).lower()
        missing = [w for w in contains if w.lower() not in text]
        if missing:
            return False, f"{rel} does not mention: {', '.join(missing)}"
        if any_of and not any(w.lower() in text for w in any_of):
            return False, f"{rel} mentions none of: {', '.join(any_of)}"
        if len(lines) < min_lines:
            return False, f"{rel} has {len(lines)} lines, needs {min_lines}"
        return True, f"{rel}: {len(lines)} lines"

    return Check(name, fn, hint)


def _dir_check(
    name: str, rel: str, suffixes: tuple[str, ...], hint: str, min_files: int = 1
) -> Check:
    """A folder is the deliverable: it holds files of the kinds the stop asked for."""

    def fn(_: Config) -> tuple[bool, str]:
        d = _at(rel)
        if not d.is_dir():
            return False, f"{rel}/ does not exist"
        found = [p for p in sorted(d.rglob("*")) if p.suffix in suffixes]
        return len(found) >= min_files, (
            f"{len(found)} {' or '.join(suffixes)} file(s) in {rel}/ "
            f"(needs {min_files})"
        )

    return Check(name, fn, hint)


def _w8_makemore(_: Config) -> tuple[bool, str]:
    d = _at("workspace/winter/makemore")
    if not d.is_dir():
        return False, "workspace/winter/makemore/ does not exist"
    code = [p for p in sorted(d.rglob("*")) if p.suffix in (".py", ".ipynb")]
    if not code:
        return False, "no .py or .ipynb in workspace/winter/makemore/"
    samples = d / "samples.txt"
    if not samples.is_file():
        return False, "no workspace/winter/makemore/samples.txt"
    n = len(_body(samples))
    return n >= 10, f"{len(code)} script(s) and {n} sampled names (needs 10)"


def _d1_dial(_: Config) -> tuple[bool, str]:
    p = _at("AGENTS.md")
    if not p.is_file():
        return False, "AGENTS.md is missing"
    text = p.read_text(encoding="utf-8").lower()
    loose = any(w in text for w in ("scratch", "vibe-only", "vibe only"))
    tight = "test" in text
    if loose and tight:
        return True, "AGENTS.md names the loose end and the tested end"
    return False, (
        "AGENTS.md needs both ends of the dial: a vibe-only folder "
        f"({'named' if loose else 'missing'}) and where tests are required "
        f"({'named' if tight else 'missing'})"
    )


def _d2_dotfolders(_: Config) -> tuple[bool, str]:
    p = _at("workspace/desert/dotfiles.md")
    if not p.is_file():
        return False, "workspace/desert/dotfiles.md does not exist"
    entries = set()
    for line in _body(p):
        m = re.search(r"(?<![\w.])\.[a-z][a-z0-9_-]{1,20}", line)
        if not m:
            continue
        rest = (line[: m.start()] + line[m.end() :]).strip(" -*`:|#")
        if len(rest.split()) >= 3:
            entries.add(m.group(0))
    return len(entries) >= 6, (
        f"{len(entries)} dot entries with a line explaining them (needs 6)"
    )


def _d3_tests(_: Config) -> tuple[bool, str]:
    """The learner's own tests, run the way they will run them: pytest, green."""
    found = sorted(_at("workspace").rglob("test_*.py"))
    if not found:
        return False, "no test_*.py under workspace/"
    out = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", *PYTEST_PLAIN, *map(str, found)],
        cwd=ROOT, capture_output=True, text=True, timeout=600,
    )  # fmt: skip
    lines = _plain(out.stdout or out.stderr).splitlines()
    return out.returncode == 0, lines[-1] if lines else "no output"


def _d4_gate(_: Config) -> tuple[bool, str]:
    """A gate, not a bookkeeping hook: it runs a check, or it stands before one."""
    hooks = _settings().get("hooks", {})
    checkers = ("ruff", "pytest", "lint", "format", "test")
    gates = {k for k in ("PreToolUse", "Stop", "SubagentStop") if hooks.get(k)}
    for event, blocks in hooks.items():
        for b in blocks:
            for h in b.get("hooks", []):
                if any(w in h.get("command", "") for w in checkers):
                    gates.add(event)
    if gates:
        return True, f"gates: {', '.join(sorted(gates))}"
    return False, f"hooks configured ({', '.join(hooks) or 'none'}) but none is a gate"


def _d5_spec(_: Config) -> tuple[bool, str]:
    d = _at("workspace/specs")
    if not d.is_dir():
        return False, "workspace/specs/ does not exist"
    good = [
        p
        for p in sorted(d.glob("*.md"))
        if len(_body(p)) >= 12 and any(ln.startswith("## ") for ln in _body(p))
    ]
    return bool(good), (
        f"{good[0].name}: a spec with sections"
        if good
        else f"{len(list(d.glob('*.md')))} file(s), none with sections and 12 lines"
    )


def _d6_ci(_: Config) -> tuple[bool, str]:
    d = _at(".github/workflows")
    files = sorted(d.glob("*.yml")) + sorted(d.glob("*.yaml"))
    if not files:
        return False, "no workflow under .github/workflows/"
    for p in files:
        try:
            wf = yaml.safe_load(p.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            return False, f"{p.name} is not valid YAML: {_plain(str(e))[:80]}"
        if not isinstance(wf, dict):
            continue
        for job_id, job in (wf.get("jobs") or {}).items():
            if not isinstance(job, dict):
                continue
            for step in job.get("steps") or []:
                run = str(step.get("run", "")) if isinstance(step, dict) else ""
                found = next((w for w in ("pytest", "ruff") if w in run), "")
                if found:
                    return True, f"{p.name}: job {job_id} runs {found}"
    return False, (
        f"{len(files)} workflow(s) parse, no step of any job runs pytest or ruff"
    )


def _d7_job(_: Config) -> tuple[bool, str]:
    d = _at("workspace/jobs")
    found = [p for p in sorted(d.glob("*")) if p.suffix in (".sh", ".py")]
    scripts = [p for p in found if len(_body(p)) >= 2]
    if not scripts:
        return False, (
            f"{len(found)} script(s) in workspace/jobs/, none with a job in it"
            if found
            else "no .sh or .py in workspace/jobs/"
        )
    log = d / "log.csv"
    if not log.is_file():
        return False, "no workspace/jobs/log.csv; the job records every run"
    runs = max(len(_body(log)) - 1, 0)
    return runs >= 2, f"{scripts[0].name} and {runs} recorded run(s) (needs 2)"


def _d8_evals(_: Config) -> tuple[bool, str]:
    cases, runner = _at("workspace/evals/cases.csv"), _at("workspace/evals/run.py")
    if not cases.is_file():
        return False, "no workspace/evals/cases.csv"
    if not runner.is_file():
        return False, "no workspace/evals/run.py"
    rows = max(len(_body(cases)) - 1, 0)
    return rows >= 5, f"{rows} eval case(s) (needs 5)"


def _p1_brewfile(_: Config) -> tuple[bool, str]:
    p = _at("workspace/dotfiles/Brewfile")
    if not p.is_file():
        return False, "no workspace/dotfiles/Brewfile"
    entries = [ln for ln in _body(p) if ln.split(" ")[0] in ("brew", "cask", "tap")]
    return len(entries) >= 5, f"{len(entries)} Brewfile entries (needs 5)"


def _p2_terminal(_: Config) -> tuple[bool, str]:
    want = ("workspace/dotfiles/ghostty/config", "workspace/dotfiles/zshrc")
    missing = [rel for rel in want if not _at(rel).is_file() or not _body(_at(rel))]
    return not missing, (
        "your ghostty config and your zshrc, both written"
        if not missing
        else f"missing or empty: {', '.join(missing)}"
    )


def _p3_github(_: Config) -> tuple[bool, str]:
    url = _git("remote", "get-url", "origin")
    if "github.com" not in url:
        return False, "no origin remote on github.com"
    names = [b for b in _git("branch", "--format=%(refname:short)").splitlines() if b]
    return len(names) >= 2, (
        f"{url} with {len(names)} branch(es): {', '.join(names[:4]) or 'none'} "
        "(needs a second branch)"
    )


def _p4_history(_: Config) -> tuple[bool, str]:
    log = _git("reflog", "-n", "300")
    found = sorted(w for w in ("rebase", "revert", "cherry-pick", "reset") if w in log)
    return bool(found), (
        f"the reflog remembers: {', '.join(found)}"
        if found
        else "no rebase, revert, cherry-pick or reset in the reflog"
    )


def _p5_permissions(_: Config) -> tuple[bool, str]:
    allow = _settings().get("permissions", {}).get("allow", [])
    return len(allow) >= 3, f"{len(allow)} allowed tool pattern(s) (needs 3)"


def _p7_other_agents(_: Config) -> tuple[bool, str]:
    p = _at("workspace/agents/comparison.md")
    if not p.is_file():
        return False, "no workspace/agents/comparison.md"
    text = p.read_text(encoding="utf-8").lower()
    named = [a for a in OTHER_AGENTS if a in text]
    if len(named) < 2:
        return False, f"names {len(named)} agent(s); compare two, side by side"
    n = len(_body(p))
    return n >= 8, f"{', '.join(named)} over {n} lines (needs 8)"


def _p8_dotfiles_repo(_: Config) -> tuple[bool, str]:
    d = _at("workspace/dotfiles")
    if not (d / ".git").exists():
        return False, "workspace/dotfiles is not a git repository"
    install = d / "install.sh"
    if not install.is_file():
        return False, "no workspace/dotfiles/install.sh"
    if "ln -s" not in install.read_text(encoding="utf-8"):
        return False, "install.sh does not symlink anything (ln -s)"
    if not (d / "README.md").is_file():
        return False, "no workspace/dotfiles/README.md"
    return True, "a git repo with install.sh and a README"


# ---- the fork -----------------------------------------------------------------

FORK_DIR = Path("workspace") / "forks" / "vibe-map"
FORK_MANIFEST = "fork.json"
FORK_VERSION = 1
# The production stop the fork challenges belong to; `vibe check --fork` prints
# under its heading and claims it like any other stop.
FORK_STOP = 6


def fork_dir(base: Path | None = None) -> Path:
    return (base or ROOT) / FORK_DIR


def config_fingerprint(config_dir: Path) -> str:
    """One hash over src/config/*.js: what "changed the configuration" means."""
    h = hashlib.sha256()
    for f in sorted(config_dir.glob("*.js")):
        h.update(f.name.encode())
        h.update(f.read_bytes())
    return h.hexdigest()


def read_manifest(base: Path | None = None) -> dict:
    """The fork's fork.json. An unknown version is refused, not patched around."""
    p = fork_dir(base) / FORK_MANIFEST
    data = json.loads(p.read_text(encoding="utf-8"))
    if data.get("version") != FORK_VERSION:
        raise ValueError(
            f"{FORK_MANIFEST} version {data.get('version')} is not {FORK_VERSION}; "
            "run vibe fork --force to make a fresh fork"
        )
    return data


def _fork_exists(_: Config) -> tuple[bool, str]:
    d = fork_dir()
    if not (d / "src" / "config").is_dir():
        return False, f"no {FORK_DIR.as_posix()}/src/config"
    if not (d / FORK_MANIFEST).exists():
        return False, f"no {FORK_MANIFEST}; this fork was not made by vibe fork"
    read_manifest()
    return True, f"{FORK_DIR.as_posix()} with its own src/config"


def _fork_changed(_: Config) -> tuple[bool, str]:
    d = fork_dir()
    if not (d / FORK_MANIFEST).exists():
        return False, "no fork yet"
    now = config_fingerprint(d / "src" / "config")
    if now == read_manifest()["config_sha256"]:
        return False, "src/config is still the product's"
    return True, "src/config differs from the product build"


def _fork_builds(_: Config) -> tuple[bool, str]:
    d = fork_dir()
    if not (d / "tools" / "build.py").exists():
        return False, "no fork yet"
    out = d / "game" / "vibe-map.html"
    before = out.stat().st_mtime if out.exists() else 0.0
    r = subprocess.run(
        [sys.executable, "tools/build.py"],
        cwd=d,
        capture_output=True,
        text=True,
        timeout=180,
    )
    if r.returncode != 0:
        return False, _plain(r.stderr or r.stdout)[-160:]
    if not out.exists() or out.stat().st_mtime == before:
        return False, "the build wrote no game/vibe-map.html"
    return True, f"{out.stat().st_size // 1024} KB from your own src/"


FORK_REPAIR = "repair.json"
FORK_REPAIR_VERSION = 1
# Commit messages that count as the two halves of a repair, when the fork is a
# git repository and the marker file was never written.
BROKE = ("break", "broke", "broken")
FIXED = ("repair", "fix", "fixed", "green")


def _fork_topic(_: Config) -> tuple[bool, str]:
    """A topic of the learner's own: a stop or a tree node the product lacks."""
    d = fork_dir()
    generated = d / "tools" / "generated"
    if not generated.is_dir():
        return False, "no fork yet"
    mine: set[str] = set()
    theirs = {ws.name for ev in campaign.evenings().values() for ws in ev.workstreams}
    local = generated / "campaign.json"
    if local.is_file():
        data = json.loads(local.read_text(encoding="utf-8"))
        mine |= {
            x["n"] for ev in data.get("evenings", {}).values() for x in ev.get("ws", [])
        }
    tree = generated / "tree.js"
    if tree.is_file():
        mine |= set(re.findall(r'"id":\s*"([^"]+)"', tree.read_text(encoding="utf-8")))
        theirs |= {t.id for t in campaign.tech_nodes()}
    new = sorted(mine - theirs)
    return bool(new), (
        f"your own topic: {', '.join(new[:3])}"
        if new
        else "the fork's campaign and tree still hold only the product's topics"
    )


def _fork_repaired(_: Config) -> tuple[bool, str]:
    """Evidence of a build that failed and then passed: the marker, else git."""
    d = fork_dir()
    marker = d / FORK_REPAIR
    if marker.is_file():
        data = json.loads(marker.read_text(encoding="utf-8"))
        if data.get("version") != FORK_REPAIR_VERSION:
            raise ValueError(
                f"{FORK_REPAIR} version {data.get('version')} is not "
                f"{FORK_REPAIR_VERSION}; delete it and record the runs again"
            )
        runs = data.get("runs", [])
        broke = next((i for i, r in enumerate(runs) if not r.get("ok")), None)
        if broke is not None and any(r.get("ok") for r in runs[broke + 1 :]):
            return True, f"{FORK_REPAIR}: a broken build, then a green one"
        return False, (
            f"{len(runs)} recorded run(s); needs a broken one, then a green one"
        )
    inside = subprocess.run(
        ["git", "-C", str(d), "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, timeout=20,
    )  # fmt: skip
    if inside.returncode != 0:
        return False, f"no {FORK_DIR.as_posix()}/{FORK_REPAIR} and no git history"
    log = subprocess.run(
        ["git", "log", "--format=%s", "-n", "50"],
        cwd=d, capture_output=True, text=True, timeout=20,
    ).stdout.lower()  # fmt: skip
    subjects = list(reversed(log.splitlines()))
    broke = next(
        (i for i, s in enumerate(subjects) if any(w in s for w in BROKE)), None
    )
    later = subjects[broke + 1 :] if broke is not None else []
    if any(any(w in s for w in FIXED) for s in later):
        return True, "the fork's git history breaks the build and then repairs it"
    return False, "the fork's history shows no break followed by a repair"


# The four challenges of the forking stop, in the order they are meant to be
# done. `vibe check --fork <challenge>` runs one of them.
FORK_CHALLENGES: dict[str, tuple[Check, ...]] = {
    "exists": (
        Check(
            "fork exists",
            _fork_exists,
            f"fork tpetedb/vibe-map on GitHub, then: vibe fork "
            f"(writes {FORK_DIR.as_posix()})",
        ),
    ),
    "config": (
        Check(
            "your configuration",
            _fork_changed,
            "edit workspace/forks/vibe-map/src/config/00-config.js, "
            "the world scale or a palette colour",
        ),
        Check(
            "it builds",
            _fork_builds,
            "in the fork: just build (or python tools/build.py) and read the error",
        ),
    ),
    "topic": (
        Check(
            "a topic of your own",
            _fork_topic,
            "pick one from vibe news or an article you read, then ask your agent "
            "to add it to workspace/forks/vibe-map/tools/generated/campaign.json "
            "(a ws entry) or tree.js (a node id), and rebuild",
        ),
    ),
    "repair": (
        Check(
            "broken and repaired",
            _fork_repaired,
            "in the fork: break the build on purpose, run just record, fix it, "
            f"run just record again (it writes {FORK_REPAIR})",
        ),
    ),
}

FORK_CHECKS: tuple[Check, ...] = tuple(
    c for checks in FORK_CHALLENGES.values() for c in checks
)


def fork_quest(cfg: Config, challenge: str = "all") -> Quest:
    """The checks behind `vibe check --fork`, all of them or one challenge."""
    if challenge != "all" and challenge not in FORK_CHALLENGES:
        raise ValueError(
            f"unknown fork challenge {challenge!r}; one of: all, "
            + ", ".join(FORK_CHALLENGES)
        )
    checks = FORK_CHECKS if challenge == "all" else FORK_CHALLENGES[challenge]
    wanted = required_levels(cfg.learner.difficulty)
    ws = campaign.evenings()["prod"].workstreams[FORK_STOP - 1]
    return Quest(
        "prod", FORK_STOP, ws.name,
        tuple(c for c in checks if c.level in wanted),
    )  # fmt: skip


# The deliverable of every stop that has one. The note check is the floor
# underneath all of them; the fork challenges are the production forking stop.
STOP_CHECKS: dict[tuple[str, int], tuple[Check, ...]] = {
    ("winter", 1): (
        _dir_check(
            "a backprop reproduction",
            "workspace/winter/backprop",
            (".py", ".ipynb"),
            "workspace/winter/backprop/: the notebook or script the agent wrote "
            "with you, following karpathy/lecun1989-repro.",
        ),
    ),
    ("winter", 3): (
        _file_check(
            "your transformer diagram",
            "workspace/winter/transformer.md",
            "workspace/winter/transformer.md: a ```mermaid block of the "
            "transformer block, and your own lines on tokens and attention.",
            contains=("```mermaid", "token", "attention"),
            min_lines=8,
        ),
    ),
    ("winter", 6): (
        _file_check(
            "a local model run recorded",
            "workspace/winter/local-model.md",
            "workspace/winter/local-model.md: the model you pulled with ollama, "
            "the three questions you asked it, and how the answers differed.",
            contains=("ollama",),
            any_of=("llama", "qwen", "mistral", "gemma", "phi"),
            min_lines=8,
        ),
    ),
    ("winter", 8): (
        Check(
            "a tiny model of your own",
            _w8_makemore,
            "workspace/winter/makemore/: the notebook or script, and "
            "samples.txt with the ten names it invented.",
        ),
    ),
    ("desert", 1): (
        Check(
            "the dial is written down",
            _d1_dial,
            "AGENTS.md: name the vibe-only folder (scratch/) and the folders "
            "that need tests before a merge.",
        ),
    ),
    ("desert", 2): (
        Check(
            "every dot entry explained",
            _d2_dotfolders,
            "workspace/desert/dotfiles.md: one line each for at least six dot "
            "entries you found with ls -la (.git, .gitignore, .env, .venv, "
            ".claude, .agents, .github).",
        ),
    ),
    ("desert", 3): (
        Check(
            "your tests run green",
            _d3_tests,
            "workspace/: a test_*.py next to the code it tests, and pytest green.",
        ),
    ),
    ("desert", 4): (
        Check(
            "a hook that gates",
            _d4_gate,
            ".claude/settings.json: a PostToolUse hook that runs ruff or a Stop "
            "hook that runs pytest, not only a bookkeeping hook.",
        ),
    ),
    ("desert", 5): (
        Check(
            "a spec you wrote first",
            _d5_spec,
            "workspace/specs/<feature>.md: twelve lines with ## sections, "
            "written before the code.",
        ),
    ),
    ("desert", 6): (
        Check(
            "CI runs your checks",
            _d6_ci,
            ".github/workflows/<name>.yml: valid YAML that runs ruff and pytest "
            "on push and pull request.",
        ),
    ),
    ("desert", 7): (
        Check(
            "a job that ran twice",
            _d7_job,
            "workspace/jobs/: the script, and log.csv with a row per run "
            "(start, end, exit code). Run it twice.",
        ),
    ),
    ("desert", 8): (
        Check(
            "an eval with cases",
            _d8_evals,
            "workspace/evals/cases.csv with five cases and "
            "workspace/evals/run.py that scores them.",
        ),
    ),
    ("prod", 1): (
        Check(
            "a Brewfile",
            _p1_brewfile,
            "workspace/dotfiles/Brewfile: brew bundle dump --file=- writes it; "
            "five entries at least.",
        ),
    ),
    ("prod", 2): (
        Check(
            "your terminal, configured",
            _p2_terminal,
            "workspace/dotfiles/ghostty/config and workspace/dotfiles/zshrc: "
            "your own, line by line.",
        ),
    ),
    ("prod", 3): (
        Check(
            "a GitHub remote and a branch",
            _p3_github,
            "gh repo create, git remote add origin, then git switch -c "
            "feature/<something> and push it.",
        ),
    ),
    ("prod", 4): (
        Check(
            "history you rewrote",
            _p4_history,
            "on a throwaway branch: git rebase -i HEAD~3, or git revert <hash>. "
            "git reflog is the evidence.",
        ),
    ),
    ("prod", 5): (
        Check(
            "permissions set once",
            _p5_permissions,
            '.claude/settings.json: "permissions": {"allow": [...]} with at '
            "least three patterns, for example Bash(pytest*).",
        ),
    ),
    ("prod", 7): (
        Check(
            "two agents compared",
            _p7_other_agents,
            "workspace/agents/comparison.md: the same task in two agents "
            "(opencode, codex, gemini), eight lines on what differed.",
        ),
    ),
    ("prod", 8): (
        Check(
            "a dotfiles repository",
            _p8_dotfiles_repo,
            "workspace/dotfiles/: git init, install.sh that symlinks with ln -s, "
            "and a README.md.",
        ),
    ),
}
STOP_CHECKS[("prod", FORK_STOP)] = FORK_CHECKS


def quest_for(world: str, n: int, cfg: Config) -> Quest:
    """The quest for one workstream, with the checks this difficulty requires."""
    ws = campaign.evenings()[world].workstreams[n - 1]
    if world == "campus":
        checks = list(CAMPUS_CHECKS[n])
    else:
        checks = [
            _note_check(world, n, (world, n) in READING_ONLY),
            *STOP_CHECKS.get((world, n), ()),
            _note_strict(world, n),
        ]
    checks += list(EXTRA)
    if cfg.learner.difficulty == "god":
        checks += list(GOD)
    wanted = required_levels(cfg.learner.difficulty)
    return Quest(world, n, ws.name, tuple(c for c in checks if c.level in wanted))


def run_quest(quest: Quest, cfg: Config) -> list[CheckResult]:
    return [c.run(cfg) for c in quest.checks]


# ---- badges -------------------------------------------------------------------

# Twenty links the learner wrote themselves, not the ones vibe generates.
OWN_LINKS_BADGE = 20

BADGES: dict[str, str] = {
    "first-light": "First light: the first workstream done",
    "full-evening": "Full evening: eight of eight on one island",
    "campaign": "Campaign: all thirty-two stops",
    "streak-3": "Streak: three stops in one day",
    "linked": "Linked: twenty wikilinks of your own in the vault",
    "shipped": "Shipped: GitHub Pages is live",
    "collector": "Collector: found every artifact on the island",
    "builder": "Builder: every artifact built for real, not just inspected",
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
        # The generated vault is full of links from day one; the badge is for
        # the learner's own linking, so only their lines count.
        if _vault_report(cfg).own_link_count() >= OWN_LINKS_BADGE:
            earned.append("linked")
    except OSError:
        pass
    rec = state.checks.get("campus:7")
    if rec and rec.ok and any("live" in p for p in rec.passed):
        earned.append("shipped")
    if state.artifacts and len(state.artifacts) >= len(campaign.artifacts()):
        earned.append("collector")
    if len(state.artifacts_built) >= len(campaign.artifacts()):
        earned.append("builder")
    if len(state.mentors) >= len(campaign.mentors()):
        earned.append("mentored")
    fresh = [b for b in earned if b not in state.badges]
    state.badges.extend(fresh)
    return fresh


def stamp() -> str:
    return dt.datetime.now().isoformat(timespec="minutes")
