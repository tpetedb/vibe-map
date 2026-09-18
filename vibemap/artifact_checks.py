"""Artifacts are tasks: the checks behind `vibe check --artifact <id>`.

Every artifact in vibemap/data/campaign.json carries a `real` block: a short
walkthrough written from the official documentation of the thing, the commands
that documentation gives, and one `check` spec. The spec names a kind; the kind
is a function here. Nothing in this module reaches the network and nothing
invents a rule: a check either looks at the file the learner wrote or runs it.

A kind has two layers. The floor always runs and is offline: the file exists
and holds what the documentation asks for. The confirmation runs the thing for
real and is skipped, with the install command in the message, when the tool it
needs is not on this machine. The floor alone can pass a check, so a learner is
never blocked by a missing tool; the detail always says which layer answered.

The module is separate from quests.py on purpose: the artifact family grows on
its own and never has to touch the workstream checks.
"""

from __future__ import annotations

import json
import re
import shutil
import sqlite3
import subprocess
import sys
from collections.abc import Callable
from importlib.util import find_spec
from pathlib import Path
from typing import Any

from vibemap import campaign, project
from vibemap.config import Config
from vibemap.quests import Check, Quest, required_levels, section_words

ROOT = project.root()
ARTIFACTS_DIR = ROOT / "workspace" / "artifacts"
ARTIFACT_XP_SHARE = 2  # an artifact built for real is worth half a workstream
ARTIFACT_NOTE = "notes.md"
ARTIFACT_SECTION = "## What I learned"
ARTIFACT_WORDS = 25
RUN_TIMEOUT = 120  # a task is under twenty minutes; its script is under two


def artifact_dir(artifact_id: str) -> Path:
    return ARTIFACTS_DIR / artifact_id


def get_artifact(artifact_id: str) -> dict[str, Any]:
    for a in campaign.artifacts():
        if a["id"] == artifact_id:
            return a
    raise ValueError(
        f"unknown artifact {artifact_id!r}; one of: "
        + ", ".join(a["id"] for a in campaign.artifacts())
    )


def artifact_ids() -> list[str]:
    return [a["id"] for a in campaign.artifacts()]


# ---- shared plumbing ----------------------------------------------------------


def _missing(here: Path, name: str) -> str | None:
    """The message for a file the walkthrough asks for and did not get."""
    return None if (here / name).exists() else f"{name} is not in {_where(here)}"


def _where(here: Path) -> str:
    return f"workspace/artifacts/{here.name}"


def _floor(here: Path, spec: dict[str, Any]) -> tuple[bool, str] | None:
    """The offline layer every kind shares. None means it passed."""
    name = spec.get("file")
    if not name:
        return None
    gone = _missing(here, name)
    if gone:
        return False, gone
    text = (here / name).read_text(encoding="utf-8", errors="replace")
    absent = [s for s in spec.get("contains", ()) if s not in text]
    if absent:
        return False, f"{name} does not use: {', '.join(absent)}"
    return None


def _run(here: Path, name: str) -> tuple[bool, str]:
    """Run the learner's script with the interpreter running vibe, offline."""
    try:
        out = subprocess.run(
            [sys.executable, name],
            cwd=here,
            capture_output=True,
            text=True,
            timeout=RUN_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return False, f"{name} did not finish in {RUN_TIMEOUT} seconds"
    if out.returncode != 0:
        tail = [line for line in out.stderr.splitlines() if line.strip()]
        return False, f"{name} failed: {tail[-1] if tail else 'no output'}"
    return True, out.stdout


def _in_order(text: str, wanted: list[str]) -> str | None:
    """The first wanted line that is absent or out of order, else None."""
    at = 0
    for want in wanted:
        found = text.find(want, at)
        if found < 0:
            return want
        at = found + len(want)
    return None


def _tool(name: str) -> bool:
    return shutil.which(name) is not None


# ---- the kinds ----------------------------------------------------------------


def _k_script(here: Path, spec: dict[str, Any]) -> tuple[bool, str]:
    """Run it and read its output: the expected lines, in the expected order."""
    ok, out = _run(here, spec["file"])
    if not ok:
        return False, out
    wanted = list(spec.get("prints", ()))
    astray = _in_order(out, wanted)
    if astray is not None:
        first = " ".join(out.split())[:90]
        return False, f"expected {astray!r} in the output, got: {first!r}"
    return True, f"{spec['file']} printed all {len(wanted)} expected lines"


def _k_dockerfile(here: Path, spec: dict[str, Any]) -> tuple[bool, str]:
    """Parse it always; build it when docker is installed."""
    text = (here / spec["file"]).read_text(encoding="utf-8")
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    if not lines or not lines[0].upper().startswith(("FROM", "ARG", "# syntax")):
        return False, "a Dockerfile starts with FROM (an ARG may come before it)"
    known = {
        "ADD", "ARG", "CMD", "COPY", "ENTRYPOINT", "ENV", "EXPOSE", "FROM",
        "HEALTHCHECK", "LABEL", "ONBUILD", "RUN", "SHELL", "STOPSIGNAL",
        "USER", "VOLUME", "WORKDIR",
    }  # fmt: skip
    joined: list[str] = []
    for line in lines:
        if joined and joined[-1].endswith("\\"):
            joined[-1] = joined[-1][:-1] + " " + line
        else:
            joined.append(line)
    for line in joined:
        word = line.split(maxsplit=1)[0].upper()
        if word not in known:
            return False, f"{word} is not a Dockerfile instruction"
    if not _tool("docker"):
        return True, (
            f"{len(joined)} instructions parse; docker is not installed, so the "
            "image was not built (install Docker Desktop and run the check again)"
        )
    tag = spec.get("tag", f"vibe-{here.name}")
    out = subprocess.run(
        ["docker", "build", "-t", tag, "."],
        cwd=here, capture_output=True, text=True, timeout=600,
    )  # fmt: skip
    if out.returncode != 0:
        tail = [line for line in out.stderr.splitlines() if line.strip()]
        return False, f"docker build failed: {tail[-1] if tail else 'no output'}"
    return True, f"docker built the image {tag}"


def _k_duckdb(here: Path, spec: dict[str, Any]) -> tuple[bool, str]:
    """Run the pipeline, then ask the database the question it was built for."""
    ok, out = _run(here, spec["file"])
    if not ok:
        return False, out
    db = here / spec["db"]
    if not db.exists():
        return False, f"{spec['file']} wrote no {spec['db']}"
    import duckdb  # a dependency of this package, so never missing

    con = duckdb.connect(str(db), read_only=True)
    try:
        rows = con.execute(spec["query"]).fetchall()
    finally:
        con.close()
    if not rows or not rows[0] or not rows[0][0]:
        return False, f"{spec['query']} returned nothing"
    return True, f"{spec['query']} returned {rows[0][0]} in {spec['db']}"


def _k_fastapi(here: Path, spec: dict[str, Any]) -> tuple[bool, str]:
    """Answer the app's own test client, which needs no port and no network."""
    # TestClient is httpx underneath, so both have to be here before it runs.
    absent = [m for m in ("fastapi", "httpx") if find_spec(m) is None]
    if absent:
        return True, (
            f"{spec['file']} holds the app the docs describe; "
            f"{' and '.join(absent)} is not installed here, so it was not called "
            f"(uv add {' '.join(absent)}, then run this again)"
        )
    ok, out = _run(here, spec["file"])
    if not ok:
        return False, out
    astray = _in_order(out, list(spec.get("prints", ())))
    if astray is not None:
        return False, f"expected {astray!r} from the test client, got: {out[:90]!r}"
    return True, "the test client got 200 and the body the docs show"


def _k_workflow(here: Path, spec: dict[str, Any]) -> tuple[bool, str]:
    """A workflow file parses and has the shape GitHub Actions documents."""
    import yaml  # a dependency of this package, so never missing

    text = (here / spec["file"]).read_text(encoding="utf-8")
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        return False, f"{spec['file']} is not valid YAML: {str(e).splitlines()[0]}"
    if not isinstance(data, dict):
        return False, f"{spec['file']} is not a mapping"
    # YAML 1.1 reads a bare `on` as the boolean True; both spellings are the key.
    triggers = data.get("on", data.get(True))
    jobs = data.get("jobs")
    if triggers is None or not isinstance(jobs, dict) or not jobs:
        return False, "a workflow needs an on: trigger and at least one job"
    for name, job in jobs.items():
        if not isinstance(job, dict) or not job.get("runs-on") or not job.get("steps"):
            return False, f"job {name} needs runs-on and steps"
    for want in spec.get("triggers", ()):
        if want not in (triggers if isinstance(triggers, dict) else {triggers: None}):
            return False, f"the workflow has no {want}: trigger"
    return True, f"{len(jobs)} job(s), triggers: {_names(triggers)}"


def _names(triggers: Any) -> str:
    if isinstance(triggers, dict):
        return ", ".join(str(k) for k in triggers)
    if isinstance(triggers, list):
        return ", ".join(str(k) for k in triggers)
    return str(triggers)


def _k_mcp(here: Path, spec: dict[str, Any]) -> tuple[bool, str]:
    """An MCP config lists at least one server with the command that starts it."""
    text = (here / spec["file"]).read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        return False, f"{spec['file']} is not valid JSON: {e.msg} on line {e.lineno}"
    servers = data.get("mcpServers")
    if not isinstance(servers, dict) or not servers:
        return False, "no mcpServers object with a server in it"
    for name, server in servers.items():
        if not isinstance(server, dict) or not server.get("command"):
            return False, f"server {name} has no command"
    return True, f"{len(servers)} server(s): {', '.join(servers)}"


def _k_sqlite(here: Path, spec: dict[str, Any]) -> tuple[bool, str]:
    """Run the script, then open the database file it wrote and count."""
    ok, out = _run(here, spec["file"])
    if not ok:
        return False, out
    db = here / spec["db"]
    if not db.exists():
        return False, f"{spec['file']} wrote no {spec['db']}"
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        table = spec["table"]
        found = con.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
            (table,),
        ).fetchone()
        if not found:
            return False, f"{spec['db']} has no table called {table}"
        rows = con.execute(f"SELECT count(*) FROM {table}").fetchone()[0]  # noqa: S608
        if not rows:
            return False, f"{table} is empty"
        detail = f"{table} holds {rows} rows"
        if spec.get("index"):
            names = [r[1] for r in con.execute(f"PRAGMA index_list({table})")]
            if not names:
                return False, f"{table} has no index on it"
            detail += f", index: {', '.join(names)}"
    finally:
        con.close()
    return True, detail


def _k_sklearn(here: Path, spec: dict[str, Any]) -> tuple[bool, str]:
    """Split, fit, score: real scikit-learn, skipped when it is not installed."""
    if find_spec("sklearn") is None:
        return True, (
            f"{spec['file']} does the split the docs describe; scikit-learn is "
            "not installed here, so it was not run (uv add scikit-learn)"
        )
    ok, out = _run(here, spec["file"])
    if not ok:
        return False, out
    astray = _in_order(out, list(spec.get("prints", ())))
    if astray is not None:
        return False, f"expected {astray!r} in the output, got: {out[:90]!r}"
    return True, "it trained, and it reported a train and a test score"


def _k_files(here: Path, spec: dict[str, Any]) -> tuple[bool, str]:
    """The floor on its own: every named file exists and says what it must."""
    for name, wanted in spec["files"].items():
        gone = _missing(here, name)
        if gone:
            return False, gone
        text = (here / name).read_text(encoding="utf-8", errors="replace")
        absent = [s for s in wanted if s not in text]
        if absent:
            return False, f"{name} does not mention: {', '.join(absent)}"
        for s in spec.get("absent", {}).get(name, ()):
            if s in text:
                return False, f"{name} must not contain {s!r}"
    return True, f"{len(spec['files'])} file(s) hold what the docs ask for"


def _k_frontmatter(here: Path, spec: dict[str, Any]) -> tuple[bool, str]:
    """A Markdown file that opens with the YAML frontmatter its docs require."""
    import yaml  # a dependency of this package, so never missing

    text = (here / spec["file"]).read_text(encoding="utf-8")
    parts = text.split("---")
    if not text.startswith("---") or len(parts) < 3:
        return False, f"{spec['file']} does not open with a --- frontmatter block"
    try:
        head = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        return False, f"the frontmatter is not valid YAML: {str(e).splitlines()[0]}"
    if not isinstance(head, dict):
        return False, "the frontmatter is not a mapping of keys to values"
    for key in ("name", "description"):
        if not head.get(key):
            return False, f"the frontmatter has no {key}"
    name = str(head["name"])
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
        return False, f"name {name!r} is not lowercase words joined by hyphens"
    if not parts[2].strip():
        return False, f"{spec['file']} has frontmatter but no brief under it"
    return True, f"{name}: {str(head['description'])[:60]}"


def _just_dump(here: Path, name: str) -> list[dict[str, Any]] | None:
    """The recipes as just itself reads them, or None when just cannot answer."""
    if not _tool("just"):
        return None
    out = subprocess.run(
        ["just", "--justfile", name, "--dump", "--dump-format", "json"],
        cwd=here, capture_output=True, text=True, timeout=RUN_TIMEOUT,
    )  # fmt: skip
    if out.returncode != 0:
        return None
    try:
        data = json.loads(out.stdout)
    except json.JSONDecodeError:
        return None
    recipes = data.get("recipes")
    if not isinstance(recipes, dict):
        return None
    return [
        {
            "name": r.get("name", key),
            "doc": r.get("doc"),
            "parameters": len(r.get("parameters") or ()),
            "dependencies": len(r.get("dependencies") or ()),
            "private": bool(r.get("private")),
        }
        for key, r in recipes.items()
    ]


# A recipe header starts at column 0: a name, optional parameters, a colon that
# is not the `:=` of an assignment, then the dependencies. Settings, imports,
# modules and aliases are the other things that live at column 0.
_JUST_HEADER = re.compile(
    r"^(?P<name>[A-Za-z0-9_-]+)(?P<params>[^:\n]*):(?!=)(?P<deps>.*)$"
)
_JUST_KEYWORDS = ("set", "import", "import?", "mod", "mod?", "alias", "export")


def _just_parse(text: str) -> list[dict[str, Any]]:
    """The tolerant reader for a machine with no just on PATH."""
    out: list[dict[str, Any]] = []
    doc: str | None = None
    for line in text.splitlines():
        if not line.strip():
            doc = None
            continue
        if line[0].isspace():  # a recipe body or a continuation
            continue
        if line.startswith("#"):
            doc = line.lstrip("#").strip() or None
            continue
        if line.startswith("["):  # an attribute keeps the doc comment above it
            continue
        m = _JUST_HEADER.match(line)
        if not m or m.group("name") in _JUST_KEYWORDS:
            doc = None
            continue
        out.append(
            {
                "name": m.group("name"),
                "doc": doc,
                "parameters": len(m.group("params").split()),
                "dependencies": len(m.group("deps").split()),
                "private": m.group("name").startswith("_"),
            }
        )
        doc = None
    return out


def _k_justfile(here: Path, spec: dict[str, Any]) -> tuple[bool, str]:
    """Read the tasks as data: just itself when it is installed, else by line."""
    name = spec["file"]
    text = (here / name).read_text(encoding="utf-8", errors="replace")
    recipes = _just_dump(here, name)
    how = "just read it as JSON"
    if recipes is None:
        if _tool("just"):
            return False, (
                f"just could not parse {name}; run: just --justfile {name} --list"
            )
        recipes = _just_parse(text)
        how = (
            "just is not installed, so the file was read line by line "
            "(brew install just, then run this again)"
        )
    public = [r for r in recipes if not r["private"]]
    wanted = int(spec.get("recipes", 3))
    if len(public) < wanted:
        return False, f"{len(public)} recipe(s) in {name}, the task asks for {wanted}"
    bare = [r["name"] for r in public if not r["doc"]]
    if bare:
        return False, f"no comment above: {', '.join(sorted(bare))}"
    if spec.get("parameter") and not any(r["parameters"] for r in public):
        return False, "no recipe takes a parameter"
    if spec.get("dependency") and not any(r["dependencies"] for r in public):
        return False, "no recipe depends on another"
    return True, f"{len(public)} documented recipes; {how}"


KINDS: dict[str, Callable[[Path, dict[str, Any]], tuple[bool, str]]] = {
    "script": _k_script,
    "justfile": _k_justfile,
    "dockerfile": _k_dockerfile,
    "duckdb": _k_duckdb,
    "fastapi": _k_fastapi,
    "workflow": _k_workflow,
    "mcp": _k_mcp,
    "sqlite": _k_sqlite,
    "sklearn": _k_sklearn,
    "frontmatter": _k_frontmatter,
    "files": _k_files,
}


# ---- the quest ----------------------------------------------------------------


def _built_check(a: dict[str, Any]) -> Check:
    real = a["real"]
    spec = real["check"]
    here = artifact_dir(a["id"])
    run = KINDS[spec["kind"]]

    def fn(_: Config) -> tuple[bool, str]:
        if not here.is_dir():
            return False, f"{real['dir']}/ does not exist yet"
        floor = _floor(here, spec)
        if floor is not None:
            return floor
        return run(here, spec)

    return Check(real["title"], fn, f"{real['dir']}/: {real['done']}")


def _note_check(a: dict[str, Any]) -> Check:
    here = artifact_dir(a["id"])

    def fn(_: Config) -> tuple[bool, str]:
        p = here / ARTIFACT_NOTE
        if not p.exists():
            return False, f"no {ARTIFACT_NOTE} in {a['real']['dir']}"
        words = section_words(p.read_text(encoding="utf-8"), ARTIFACT_SECTION)
        return words >= ARTIFACT_WORDS, (
            f"{words} of your own words under {ARTIFACT_SECTION} "
            f"(needs {ARTIFACT_WORDS})"
        )

    return Check(
        f"your note on {a['name']}",
        fn,
        f"Write {a['real']['dir']}/{ARTIFACT_NOTE} with a {ARTIFACT_SECTION} "
        f"section of at least {ARTIFACT_WORDS} words.",
        "strict",
    )


def artifact_quest(artifact_id: str, cfg: Config) -> Quest:
    """The quest for one artifact: you built the thing, then you wrote it down."""
    a = get_artifact(artifact_id)
    checks = (_built_check(a), _note_check(a))
    wanted = required_levels(cfg.learner.difficulty)
    return Quest(
        "artifact", 0, f"{a['name']}: {a['real']['title']}",
        tuple(c for c in checks if c.level in wanted),
    )  # fmt: skip
