"""Work orders: a task for an agent is data, and its acceptance is a command.

A prompt that says "and run the tests" is a hope. An order says which files the
work may touch, which commands have to pass and which judgements a second agent
has to make, and this tool is the one place all of that is checked: from a
`just` recipe, from a Claude Code hook, and from CI. `work/README.md` is the
short version, `docs/adr/0016-work-orders.md` the reasoning.

    python3 tools/work.py new <id> --team <team> --title "..."
    python3 tools/work.py validate     every order readable, no two active ones overlap
    python3 tools/work.py check <id>   ownership, then every criterion's command
    python3 tools/work.py review <id>  the packet a reviewer reads
    python3 tools/work.py accept <id>  check + review + sign-offs: ready to land
    python3 tools/work.py plan <goal>  launch groups: needs, disjoint files, the budget
    python3 tools/work.py board        every active order in every worktree
    python3 tools/work.py ci --base origin/main
    python3 tools/work.py sweep        at a release: remove the orders that landed
    python3 tools/work.py post <id>    the order's one status comment on its issue
    python3 tools/work.py thread <id>  what the owner and collaborators said there
    python3 tools/work.py say <id> --role <role> "..."
    python3 tools/work.py hook pre-tool|stop   what .claude/settings.json calls

Standard library only, so a hook can run it with a bare python3.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import re
import subprocess
import sys
import time
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sync_main import GENERATED  # noqa: E402  one list of what nobody owns

ROOT = Path(__file__).resolve().parents[1]
VERSION = 1
ID = re.compile(r"^[a-z0-9][a-z0-9-]{2,48}$")
JUDGES = ("reviewer", "manager")
# What any order may touch besides what it owns: outputs that are regenerated,
# and the fragment CI demands for a change to the product.
ANYONE = (*GENERATED, "changelog.d/")
ORDER_LINE = re.compile(r"^\s*order:\s*([a-z0-9-]+)\s*$", re.M)
ROLE_LINE = re.compile(r"^\s*role:\s*([a-z-]+)\s*$", re.M)
# A criterion may take a browser battery; a hung one must still end.
CHECK_TIMEOUT = 1500


class Bad(Exception):
    """A file that does not say what it has to. Always names the file."""


def covers(pattern: str, path: str) -> bool:
    """Whether a path falls under a pattern: `dir/` is a prefix, the rest is a glob."""
    if pattern.endswith("/"):
        return path.startswith(pattern)
    return path == pattern or fnmatch.fnmatchcase(path, pattern)


def overlap(a: str, b: str) -> bool:
    """Whether two owned entries (a file, or a folder ending in /) can collide."""
    return covers(a, b) or covers(b, a)


def git(root: Path, *args: str) -> str:
    out = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True, check=False
    )
    return out.stdout.strip()


# What the tool writes next to an order is a measurement, not part of the work.
NOT_RESULTS = ":(exclude)work/orders/*/result.json"


def dirty(root: Path) -> list[str]:
    """Paths with uncommitted changes, every untracked file by name. The first
    column of a status line is a space for an unstaged change, so the output is
    read unstripped."""
    out = subprocess.run(
        ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"]
        + ["--", ".", NOT_RESULTS],
        capture_output=True,
        text=True,
        check=False,
    )
    lines = [ln for ln in out.stdout.splitlines() if ln.strip()]
    return [ln[3:].split(" -> ")[-1].strip('"') for ln in lines]


def _toml(path: Path) -> dict:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as e:
        raise Bad(f"{path}: not valid TOML: {e}") from e


def _version(data: dict, path: Path) -> None:
    if data.get("v") != VERSION:
        raise Bad(f"{path}: v = {data.get('v')!r}, this tool reads v = {VERSION}")


# ---------------------------------------------------------------- teams


@dataclass(frozen=True, slots=True)
class Team:
    id: str
    title: str
    paths: tuple[str, ...]
    tests: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Teams:
    teams: tuple[Team, ...]
    shared: tuple[str, ...]

    def ids(self) -> set[str]:
        return {t.id for t in self.teams}

    def of(self, path: str) -> str | None:
        """The team a path belongs to: the first one in the file that covers it."""
        if any(covers(s, path) for s in self.shared):
            return "shared"
        for team in self.teams:
            if any(covers(p, path) for p in team.paths):
                return team.id
        return None


def load_teams(root: Path = ROOT) -> Teams:
    path = root / "work" / "teams.toml"
    data = _toml(path)
    _version(data, path)
    teams = []
    for raw in data.get("teams", []):
        if not ID.match(str(raw.get("id", ""))):
            raise Bad(f"{path}: a team needs an id like 'scene', got {raw.get('id')!r}")
        if not raw.get("paths"):
            raise Bad(f"{path}: team {raw['id']} owns no paths")
        teams.append(
            Team(
                raw["id"],
                str(raw.get("title", "")),
                tuple(raw["paths"]),
                tuple(raw.get("tests", [])),
            )
        )
    if len({t.id for t in teams}) != len(teams):
        raise Bad(f"{path}: two teams share an id")
    return Teams(tuple(teams), tuple(data.get("shared", [])))


# ---------------------------------------------------------------- orders


@dataclass(frozen=True, slots=True)
class Criterion:
    id: str
    text: str
    check: str | None
    judge: str | None
    timeout: int


@dataclass(frozen=True, slots=True)
class Order:
    id: str
    root: Path
    title: str
    team: str
    branch: str
    goal: str
    builder: str
    owns: tuple[str, ...]
    cross: tuple[str, ...]
    needs: tuple[str, ...]
    criteria: tuple[Criterion, ...]
    issue: int | None = None
    extra: dict = field(default_factory=dict)

    @property
    def dir(self) -> Path:
        return self.root / "work" / "orders" / self.id

    @property
    def rel(self) -> str:
        return f"work/orders/{self.id}/"

    def may_touch(self, path: str) -> bool:
        return (
            path.startswith(self.rel)
            or any(covers(o, path) for o in self.owns)
            or any(covers(a, path) for a in ANYONE)
        )


def load_order(folder: Path, teams: Teams, root: Path) -> Order:
    path = folder / "order.toml"
    data = _toml(path)
    _version(data, path)
    oid = str(data.get("id", ""))
    if not ID.match(oid) or oid != folder.name:
        raise Bad(f"{path}: id = {oid!r} has to be the folder name, {folder.name!r}")
    for key in ("title", "team", "branch"):
        if not str(data.get(key, "")).strip():
            raise Bad(f"{path}: {key} is missing")
    if data["team"] not in teams.ids():
        raise Bad(f"{path}: team {data['team']!r} is not in work/teams.toml")
    cross = tuple(data.get("cross", []))
    for other in cross:
        if other not in teams.ids() or other == data["team"]:
            raise Bad(f"{path}: cross names {other!r}, which is not another team")
    owns = tuple(data.get("owns", []))
    if not owns:
        raise Bad(f"{path}: owns is empty, so the order may touch nothing")
    for entry in owns:
        if any(ch in entry for ch in "*?["):
            raise Bad(f"{path}: owns {entry!r}: name files or folders/, not globs")
        home = teams.of(entry)
        if home not in (data["team"], "shared", *cross):
            raise Bad(
                f"{path}: owns {entry!r}, which belongs to team {home!r}; "
                f"add it to cross and get that team's sign-off, or leave it"
            )
    criteria = []
    for raw in data.get("criteria", []):
        cid = str(raw.get("id", ""))
        if not cid or not str(raw.get("text", "")).strip():
            raise Bad(f"{path}: a criterion needs an id and a text")
        has_check, has_judge = bool(raw.get("check")), bool(raw.get("judge"))
        if has_check == has_judge:
            raise Bad(f"{path}: criterion {cid} needs exactly one of check or judge")
        if has_judge and raw["judge"] not in JUDGES:
            raise Bad(f"{path}: criterion {cid}: judge is one of {', '.join(JUDGES)}")
        criteria.append(
            Criterion(
                cid,
                raw["text"],
                raw.get("check"),
                raw.get("judge"),
                int(raw.get("timeout", CHECK_TIMEOUT)),
            )
        )
    if len({c.id for c in criteria}) != len(criteria):
        raise Bad(f"{path}: two criteria share an id")
    if not any(c.check for c in criteria):
        raise Bad(f"{path}: no criterion has a check; at least one must be a command")
    return Order(
        oid,
        root,
        data["title"],
        data["team"],
        data["branch"],
        str(data.get("goal", "")),
        str(data.get("builder", "")),
        owns,
        cross,
        tuple(data.get("needs", [])),
        tuple(criteria),
        data.get("issue"),
    )


def orders_in(root: Path, teams: Teams) -> list[Order]:
    base = root / "work" / "orders"
    if not base.is_dir():
        return []
    return [
        load_order(d, teams, root)
        for d in sorted(base.iterdir())
        if (d / "order.toml").is_file()
    ]


def worktrees(root: Path = ROOT) -> list[tuple[Path, str]]:
    """Every checkout of this repository with the branch it is on."""
    out, path = [], None
    for line in git(root, "worktree", "list", "--porcelain").splitlines():
        if line.startswith("worktree "):
            path = Path(line[9:])
        elif line.startswith("branch ") and path:
            out.append((path, line[7:].removeprefix("refs/heads/")))
    return out


def landed(root: Path = ROOT) -> set[str]:
    """Orders whose review is on main: the review travels with the work it accepts."""
    names = git(root, "ls-tree", "-r", "--name-only", "origin/main", "work/orders/")
    return {n.split("/")[2] for n in names.splitlines() if n.endswith("/review.toml")}


def active(root: Path = ROOT) -> list[Order]:
    """Orders being worked on now: their branch is checked out in some worktree."""
    done, found = landed(root), {}
    for path, branch in worktrees(root):
        try:
            teams = load_teams(path)
        except (Bad, FileNotFoundError):
            continue
        for order in orders_in(path, teams):
            if order.branch == branch and order.id not in done:
                found[order.id] = order
    return list(found.values())


def collisions(orders: list[Order]) -> list[str]:
    out = []
    for i, a in enumerate(orders):
        for b in orders[i + 1 :]:
            hit = [(x, y) for x in a.owns for y in b.owns if overlap(x, y)]
            if hit:
                x, y = hit[0]
                out.append(
                    f"{a.id} and {b.id} both own {x if x == y else x + ' / ' + y}"
                )
    return out


def find(oid: str, root: Path = ROOT) -> Order:
    teams = load_teams(root)
    for order in orders_in(root, teams):
        if order.id == oid:
            return order
    raise Bad(f"no order {oid!r} under {root / 'work' / 'orders'}")


# ---------------------------------------------------------------- checks


def changed(root: Path, base: str) -> list[str]:
    """What this branch changes against base, committed or not."""
    names = set(git(root, "diff", "--name-only", f"{base}...HEAD").splitlines())
    return sorted(n for n in names | set(dirty(root)) if n)


def strays(order: Order, base: str) -> list[str]:
    return [p for p in changed(order.root, base) if not order.may_touch(p)]


def tree_key(root: Path) -> str:
    """The exact state of the checkout: a result is only good for the tree it saw."""
    paths = dirty(root)
    parts = [git(root, "rev-parse", "HEAD"), git(root, "diff", "HEAD")]
    for rel in paths:
        file = root / rel
        if file.is_file():
            parts.append(rel + hashlib.sha1(file.read_bytes()).hexdigest())
    return hashlib.sha1("\n".join(parts).encode()).hexdigest()


def run_check(order: Order, base: str, force: bool = False) -> dict:
    out_path = order.dir / "result.json"
    key = tree_key(order.root)
    if not force and out_path.is_file():
        old = json.loads(out_path.read_text(encoding="utf-8"))
        if old.get("tree") == key and old.get("ok"):
            old["cached"] = True
            return old
    result: dict = {"order": order.id, "tree": key, "strays": strays(order, base)}
    rows = []
    for c in order.criteria:
        if not c.check:
            rows.append({"id": c.id, "judge": c.judge, "text": c.text})
            continue
        start = time.monotonic()
        try:
            proc = subprocess.run(
                c.check,
                shell=True,
                cwd=order.root,
                capture_output=True,
                text=True,
                timeout=c.timeout,
                check=False,
            )
            code, tail = proc.returncode, (proc.stdout + proc.stderr)[-1200:]
        except subprocess.TimeoutExpired:
            code, tail = 124, f"timed out after {c.timeout}s"
        rows.append(
            {
                "id": c.id,
                "check": c.check,
                "exit": code,
                "seconds": round(time.monotonic() - start, 1),
                "tail": tail,
                "text": c.text,
            }
        )
    result["criteria"] = rows
    result["ok"] = not result["strays"] and all(r.get("exit", 0) == 0 for r in rows)
    out_path.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
    return result


def show(result: dict) -> str:
    lines = [
        f"order {result['order']}" + ("  (cached)" if result.get("cached") else "")
    ]
    for p in result["strays"]:
        lines.append(f"  STRAY  {p}  is outside what the order owns")
    for r in result["criteria"]:
        if "judge" in r:
            lines.append(f"  judge  {r['id']}  for the {r['judge']}: {r['text']}")
        else:
            mark = "pass " if r["exit"] == 0 else "FAIL "
            lines.append(f"  {mark}  {r['id']}  {r['seconds']}s  {r['check']}")
            if r["exit"] != 0:
                lines += [f"         | {x}" for x in r["tail"].splitlines()[-12:]]
    lines.append("  OK" if result["ok"] else "  NOT OK")
    return "\n".join(lines)


# ---------------------------------------------------------------- review


def _signed(order: Order, path: Path, who: str) -> dict:
    """A review or a sign-off: by someone else, about this order, still current."""
    data = _toml(path)
    _version(data, path)
    if data.get("order") != order.id:
        raise Bad(f"{path}: order = {data.get('order')!r}, expected {order.id!r}")
    by = str(data.get("by", "")).strip()
    if not by:
        raise Bad(f"{path}: by is missing: a {who} has a name")
    if order.builder and by == order.builder:
        raise Bad(f"{path}: by = {by!r} is the builder; nobody accepts their own work")
    if data.get("verdict") not in ("accept", "improve"):
        raise Bad(f"{path}: verdict is accept or improve")
    sha = str(data.get("reviewed", ""))
    contained = sha and subprocess.run(
        ["git", "-C", str(order.root), "merge-base", "--is-ancestor", sha, "HEAD"],
        capture_output=True,
        check=False,
    )
    if not contained or contained.returncode != 0:
        raise Bad(f"{path}: reviewed = {sha!r} is not a commit this branch contains")
    later = git(order.root, "diff", "--name-only", f"{sha}..HEAD").splitlines()
    moved = [
        p
        for p in later
        if any(covers(o, p) for o in order.owns) and not p.startswith(order.rel)
    ]
    if moved:
        raise Bad(
            f"{path}: {', '.join(moved[:3])} changed after the {who} looked; "
            f"review again and update reviewed"
        )
    return data


def load_review(order: Order) -> dict:
    path = order.dir / "review.toml"
    if not path.is_file():
        raise Bad(f"{path}: no review yet")
    data = _signed(order, path, "reviewer")
    ruled = {str(r.get("id")): r for r in data.get("criteria", [])}
    for c in order.criteria:
        row = ruled.get(c.id)
        if not row or row.get("verdict") not in ("pass", "fail"):
            raise Bad(f"{path}: criterion {c.id} has no pass or fail")
        if not str(row.get("evidence", "")).strip():
            raise Bad(f"{path}: criterion {c.id} has a verdict and no evidence")
    return data


def acceptance(order: Order, base: str) -> list[str]:
    """Everything between this order and main, as sentences. Empty means land it."""
    why = []
    result = run_check(order, base)
    if not result["ok"]:
        why.append("the checks do not pass (just work-check)")
    try:
        review = load_review(order)
        if review["verdict"] != "accept":
            why.append("the reviewer asked for improvements")
        failed = [r["id"] for r in review["criteria"] if r["verdict"] == "fail"]
        if failed:
            why.append(f"the reviewer failed {', '.join(failed)}")
    except Bad as e:
        why.append(str(e))
    for team in order.cross:
        path = order.dir / f"signoff-{team}.toml"
        try:
            if not path.is_file():
                raise Bad(f"{path}: team {team} has not signed off on its files")
            if _signed(order, path, f"{team} manager")["verdict"] != "accept":
                why.append(f"team {team} did not accept the change to its files")
        except Bad as e:
            why.append(str(e))
    return why


# ---------------------------------------------------------------- plan


def load_goal(gid: str, root: Path = ROOT) -> dict:
    path = root / "work" / "goals" / f"{gid}.toml"
    data = _toml(path)
    _version(data, path)
    if data.get("id") != gid or not str(data.get("statement", "")).strip():
        raise Bad(f"{path}: a goal needs id = {gid!r} and a statement")
    if not data.get("orders"):
        raise Bad(f"{path}: orders is empty")
    return data


def plan(gid: str, root: Path = ROOT) -> list[list[Order]]:
    """Launch groups: what an order needs has landed or ran in an earlier group,
    no two orders in a group own the same file, and a group fits the budget."""
    goal = load_goal(gid, root)
    budget = int(goal.get("budget", 4))
    by_id = {o.id: o for o in orders_in(root, load_teams(root))}
    missing = [i for i in goal["orders"] if i not in by_id]
    if missing:
        raise Bad(f"goal {gid}: no order file for {', '.join(missing)}")
    done = landed(root)
    todo = [by_id[i] for i in goal["orders"] if i not in done]
    for o in todo:
        unknown = [n for n in o.needs if n not in by_id and n not in done]
        if unknown:
            raise Bad(f"order {o.id}: needs {', '.join(unknown)}, which does not exist")
    groups: list[list[Order]] = []
    settled = set(done)
    while todo:
        group: list[Order] = []
        for o in todo:
            ready = all(n in settled for n in o.needs)
            free = not any(overlap(x, y) for g in group for x in g.owns for y in o.owns)
            if ready and free and len(group) < budget:
                group.append(o)
        if not group:
            raise Bad(f"goal {gid}: {', '.join(o.id for o in todo)} wait on each other")
        groups.append(group)
        settled |= {o.id for o in group}
        todo = [o for o in todo if o not in group]
    return groups


# ---------------------------------------------------------------- the issue
#
# The repository is the record: orders, reviews and sign-offs travel with the
# code. The order's GitHub issue is the conversation. An agent reads it before
# it starts and the tool keeps one status comment there current.

MARK = "<!-- work:{id} -->"
# Anyone can comment on a public issue. What an agent reads as instructions
# comes only from people who can already push here.
TRUSTED = ("OWNER", "MEMBER", "COLLABORATOR")


def status_comment(order: Order, result: dict | None, review: dict | None) -> str:
    """The order as its issue sees it. Same inputs, same text, so it is safe to
    rewrite in place."""
    lines = [
        MARK.format(id=order.id),
        f"**Order `{order.id}`** ({order.team}): {order.title}",
        "",
        f"Branch `{order.branch}`. Owns: {', '.join(f'`{o}`' for o in order.owns)}.",
        "",
        "| criterion | how | state |",
        "|---|---|---|",
    ]
    ran = {r["id"]: r for r in (result or {}).get("criteria", [])}
    ruled = {r["id"]: r for r in (review or {}).get("criteria", [])}
    for c in order.criteria:
        if c.check:
            row = ran.get(c.id)
            state = "not run" if not row else ("pass" if row["exit"] == 0 else "FAIL")
            how = f"`{c.check}`"
        else:
            state, how = "waits for the " + str(c.judge), "judged"
        if c.id in ruled:
            state += f", reviewer: {ruled[c.id]['verdict']}"
        lines.append(f"| {c.id}: {c.text} | {how} | {state} |")
    for p in (result or {}).get("strays", []):
        lines.append(f"\nOutside the order: `{p}`")
    if review:
        lines.append(f"\nReview by {review['by']}: **{review['verdict']}**.")
        for f in review.get("findings", []):
            lines.append(
                f"- {f.get('severity', '')}: `{f.get('file', '')}` {f['text']}"
            )
    lines.append("\nWritten by `tools/work.py post`; edits here are overwritten.")
    return "\n".join(lines) + "\n"


def trusted(comments: list[dict]) -> tuple[list[dict], int]:
    """The comments an agent may read, and how many were held back."""
    keep = [
        c
        for c in comments
        if c.get("author_association") in TRUSTED
        and not str(c.get("body", "")).startswith("<!-- work:")
    ]
    ours = sum(1 for c in comments if str(c.get("body", "")).startswith("<!-- work:"))
    return keep, len(comments) - len(keep) - ours


def _gh(*args: str, body: str | None = None) -> str:
    out = subprocess.run(
        ["gh", "api", *args, *(["-f", f"body={body}"] if body is not None else [])],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if out.returncode != 0:
        raise Bad(f"gh api {args[0]}: {out.stderr.strip()[:300]}")
    return out.stdout


def _comments(issue: int) -> list[dict]:
    raw = _gh(f"repos/{{owner}}/{{repo}}/issues/{issue}/comments", "--paginate")
    return json.loads(raw or "[]")


def _issue_of(order: Order) -> int:
    if not order.issue:
        raise Bad(f"{order.dir / 'order.toml'}: no issue = <number> to talk on")
    return int(order.issue)


# ---------------------------------------------------------------- hooks


def _repo_of(path: Path) -> Path | None:
    for parent in [path, *path.parents]:
        if (parent / ".git").exists():
            return parent
    return None


def hook_pre_tool(event: dict) -> tuple[int, str]:
    """Refuse an edit outside what the order on this branch owns."""
    raw = (event.get("tool_input") or {}).get("file_path")
    if not raw:
        return 0, ""
    target = Path(raw).resolve()
    root = _repo_of(target.parent)
    if not root or not (root / "work" / "teams.toml").is_file():
        return 0, ""
    branch = git(root, "branch", "--show-current")
    try:
        mine = [o for o in orders_in(root, load_teams(root)) if o.branch == branch]
    except Bad as e:
        return 2, f"work order unreadable, fix it first: {e}"
    if len(mine) != 1:
        return 0, ""
    order, rel = mine[0], target.relative_to(root).as_posix()
    if order.may_touch(rel):
        return 0, ""
    home = load_teams(root).of(rel) or "nobody"
    return 2, (
        f"{rel} is outside order {order.id} (team {order.team}); it belongs to "
        f"{home}. Leave it and report it, or have the order's owns and cross "
        f"changed by the manager. This order owns: {', '.join(order.owns)}"
    )


def hook_stop(
    event: dict, base: str = "origin/main", root: Path = ROOT
) -> tuple[int, str]:
    """An agent that reports on an order may only stop when the order holds."""
    if event.get("stop_hook_active"):
        return 0, ""
    text = str(event.get("last_assistant_message", ""))
    found = ORDER_LINE.search(text)
    if not found:
        return 0, ""
    role = ROLE_LINE.search(text)
    here = {o.id: o for o in active(root)}
    order = here.get(found.group(1))
    if not order:
        return 0, ""
    try:
        if role and role.group(1) == "reviewer":
            load_review(order)
            return 0, ""
        result = run_check(order, base)
    except Bad as e:
        return 2, str(e)
    if result["ok"]:
        return 0, ""
    return 2, "The order does not hold yet, so this is not done:\n" + show(result)


# ---------------------------------------------------------------- commands

TEMPLATE = """v = 1
id = "{id}"
title = "{title}"
team = "{team}"
branch = "{branch}"
goal = "{goal}"
builder = ""

# Files, or folders ending in /. No globs: two orders may never own the same file.
owns = []
# Other teams whose files this order has to touch; each one signs off.
cross = []
# Orders that have to land before this one starts.
needs = []

# At least one criterion is a command. Exit 0 is pass; anything else is not.
[[criteria]]
id = "c1"
text = ""
check = ""

# What a command cannot decide goes to a person in a role, who rules on it
# in review.toml with evidence.
# [[criteria]]
# id = "c2"
# text = ""
# judge = "reviewer"
"""


def cmd_new(a: argparse.Namespace) -> int:
    if not ID.match(a.id):
        raise Bad(f"{a.id!r}: an id is lowercase letters, digits and dashes")
    if a.team not in load_teams().ids():
        raise Bad(f"{a.team!r} is not a team in work/teams.toml")
    folder = ROOT / "work" / "orders" / a.id
    if folder.exists():
        raise Bad(f"{folder} exists")
    folder.mkdir(parents=True)
    branch = a.branch or git(ROOT, "branch", "--show-current")
    (folder / "order.toml").write_text(
        TEMPLATE.format(
            id=a.id, title=a.title, team=a.team, branch=branch, goal=a.goal or ""
        ),
        encoding="utf-8",
    )
    print(f"wrote {folder.relative_to(ROOT)}/order.toml: fill in owns and criteria")
    return 0


def cmd_validate(_: argparse.Namespace) -> int:
    orders = orders_in(ROOT, load_teams())
    clash = collisions(active())
    for line in clash:
        print("collision:", line)
    print(f"{len(orders)} orders read, {len(clash)} collisions among the active ones")
    return 1 if clash else 0


def cmd_check(a: argparse.Namespace) -> int:
    result = run_check(find(a.id), a.base, force=a.force)
    print(show(result))
    return 0 if result["ok"] else 1


def cmd_review(a: argparse.Namespace) -> int:
    order = find(a.id)
    print(show(run_check(order, a.base)))
    print("\nwhat changed:")
    print(git(order.root, "diff", "--stat", f"{a.base}...HEAD"))
    print(f'\nreviewed = "{git(order.root, "rev-parse", "HEAD")}"')
    print(f"write your ruling to {order.rel}review.toml (work/templates/review.toml)")
    return 0


def cmd_accept(a: argparse.Namespace) -> int:
    why = acceptance(find(a.id), a.base)
    for line in why:
        print("not yet:", line)
    if not why:
        print(f"{a.id}: checked, reviewed, signed off. Ready to land.")
    return 1 if why else 0


def cmd_plan(a: argparse.Namespace) -> int:
    for n, group in enumerate(plan(a.goal), 1):
        print(f"group {n}")
        for o in group:
            print(f"  {o.id:<28} {o.team:<9} {', '.join(o.owns)}")
    return 0


def cmd_board(_: argparse.Namespace) -> int:
    done = landed()
    rows = []
    for order in active():
        result = order.dir / "result.json"
        ok = json.loads(result.read_text())["ok"] if result.is_file() else None
        checks = {True: "pass", False: "FAIL", None: "not run"}[ok]
        review = "yes" if (order.dir / "review.toml").is_file() else "no"
        rows.append((order.id, order.team, order.branch, checks, review))
    print(f"{'order':<28} {'team':<9} {'branch':<34} {'checks':<8} review")
    for r in rows:
        print(f"{r[0]:<28} {r[1]:<9} {r[2]:<34} {r[3]:<8} {r[4]}")
    print(f"{len(rows)} active, {len(done)} landed")
    return 0


def cmd_ci(a: argparse.Namespace) -> int:
    """On a pull request: every order it carries is readable, and one that ships
    code ships its accepted review with it. A pull request without an order is
    left alone, and so is the ownership of a train car, which carries several:
    each of those was checked where it was built."""
    names = git(ROOT, "diff", "--name-only", f"{a.base}...HEAD").splitlines()
    touched = sorted({n.split("/")[2] for n in names if n.startswith("work/orders/")})
    code = [n for n in names if not n.startswith("work/")]
    bad = []
    for oid in touched:
        if not (ROOT / "work" / "orders" / oid / "order.toml").is_file():
            continue
        order = find(oid)
        if not code:
            continue
        try:
            review = load_review(order)
            if review["verdict"] != "accept":
                bad.append(f"{oid}: reviewed, not accepted")
        except Bad as e:
            bad.append(str(e))
        if len(touched) == 1:
            bad += [
                f"{oid}: {p} is outside what it owns" for p in strays(order, a.base)
            ]
    for line in bad:
        print("work:", line)
    print(f"work: {len(touched)} orders in this pull request, {len(bad)} problems")
    return 1 if bad else 0


def cmd_post(a: argparse.Namespace) -> int:
    order = find(a.id)
    issue = _issue_of(order)
    result_path = order.dir / "result.json"
    result = json.loads(result_path.read_text()) if result_path.is_file() else None
    try:
        review = load_review(order)
    except Bad:
        review = None
    body = status_comment(order, result, review)
    mark = MARK.format(id=order.id)
    mine = [c for c in _comments(issue) if str(c.get("body", "")).startswith(mark)]
    if mine and mine[0]["body"].strip() == body.strip():
        print(f"#{issue}: status of {order.id} is current")
    elif mine:
        _gh(
            f"repos/{{owner}}/{{repo}}/issues/comments/{mine[0]['id']}",
            "-X",
            "PATCH",
            body=body,
        )
        print(f"#{issue}: status of {order.id} updated")
    else:
        _gh(f"repos/{{owner}}/{{repo}}/issues/{issue}/comments", body=body)
        print(f"#{issue}: status of {order.id} posted")
    return 0


def cmd_thread(a: argparse.Namespace) -> int:
    order = find(a.id)
    keep, held = trusted(_comments(_issue_of(order)))
    for c in keep:
        print(f"--- {c['user']['login']} at {c['created_at']}")
        print(c["body"].strip())
    print(
        f"--- {len(keep)} comments; {held} from people who cannot push here, not shown"
    )
    return 0


def cmd_say(a: argparse.Namespace) -> int:
    order = find(a.id)
    body = f"**{a.role}** on order `{order.id}`:\n\n{a.text.strip()}\n"
    _gh(f"repos/{{owner}}/{{repo}}/issues/{_issue_of(order)}/comments", body=body)
    print(f"#{order.issue}: said as {a.role}")
    return 0


def cmd_sweep(_: argparse.Namespace) -> int:
    """Remove the orders that have landed: main has their review, git has the rest."""
    gone = []
    for oid in sorted(landed()):
        folder = ROOT / "work" / "orders" / oid
        if folder.is_dir():
            for f in sorted(folder.iterdir()):
                f.unlink()
            folder.rmdir()
            gone.append(oid)
    print(f"swept {len(gone)} landed orders: {', '.join(gone) or 'none'}")
    return 0


def cmd_hook(a: argparse.Namespace) -> int:
    try:
        event = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return 0
    code, why = (hook_pre_tool if a.which == "pre-tool" else hook_stop)(event)
    if why:
        print(why, file=sys.stderr)
    return code


def main() -> int:
    p = argparse.ArgumentParser(prog="work", description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new")
    n.add_argument("id")
    n.add_argument("--team", required=True)
    n.add_argument("--title", required=True)
    n.add_argument("--goal")
    n.add_argument("--branch")
    sub.add_parser("validate")
    for name in ("check", "review", "accept"):
        c = sub.add_parser(name)
        c.add_argument("id")
        c.add_argument("--base", default="origin/main")
        c.add_argument("--force", action="store_true")
    sub.add_parser("plan").add_argument("goal")
    sub.add_parser("board")
    sub.add_parser("sweep")
    sub.add_parser("ci").add_argument("--base", default="origin/main")
    for name in ("post", "thread"):
        sub.add_parser(name).add_argument("id")
    say = sub.add_parser("say")
    say.add_argument("id")
    say.add_argument("--role", required=True)
    say.add_argument("text")
    sub.add_parser("hook").add_argument("which", choices=("pre-tool", "stop"))
    a = p.parse_args()
    try:
        return globals()[f"cmd_{a.cmd}"](a)
    except Bad as e:
        print(f"work: {e}", file=sys.stderr)
        return 2
    except FileNotFoundError as e:
        print(f"work: {e.filename}: not found", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
