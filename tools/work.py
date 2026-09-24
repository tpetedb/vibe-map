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
import importlib.util
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # the system python on a Mac is older than 3.11
    if sys.argv[1:2] == ["hook"]:
        print("work hooks are off: python3 is older than 3.11", file=sys.stderr)
        raise SystemExit(0) from None
    raise SystemExit("tools/work.py needs Python 3.11 or newer") from None

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sync_main import GENERATED  # noqa: E402  one list of what nobody owns

ROOT = Path(__file__).resolve().parents[1]
VERSION = 1
ID = re.compile(r"^[a-z0-9][a-z0-9-]{2,48}$")
JUDGES = ("reviewer", "manager")
# What any order may touch besides what it owns: outputs that are regenerated,
# and the fragment CI demands for a change to the product.
ANYONE = (*GENERATED, "changelog.d/")
# A report's first line names its order; "order: x" further down is prose.
ORDER_LINE = re.compile(r"\A\s*order:\s*([a-z0-9-]+)\s*$", re.M)
ROLE_LINE = re.compile(r"^\s*role:\s*([a-z-]+)\s*$", re.M)
# A criterion may take a browser battery; a hung one must still end.
CHECK_TIMEOUT = 1500
# All of an order's criteria together when a stop hook runs them: under the
# hook's own timeout in .claude/settings.json, so the tool ends it, with a reason.
STOP_BUDGET = 1500
# How many agents an order remembers in touched.json, newest edit last. An
# agent drops out once this many others have edited under the order since its
# own last edit; four work at once, so that agent stopped long ago.
TOUCHED_KEEP = 32


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


# Every path handed to git is a file name, never pathspec magic: a file called
# `:(nope)x.js` would stop a diff, and one called `:!src/x.js` would hide x.js.
GIT = ("git", "--literal-pathspecs")


def git(root: Path, *args: str, must: bool = False) -> str:
    """One git call. `must` is for an answer the verdict depends on: an empty
    string from a failed diff would read as "nothing changed"."""
    out = subprocess.run(
        [*GIT, "-c", "core.quotepath=false", "-C", str(root), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if must and out.returncode != 0:
        raise Bad(f"git {' '.join(args)}: {out.stderr.strip()[:300]}")
    return out.stdout.strip()


def names(root: Path, *args: str, must: bool = False) -> list[str]:
    """Paths from a git command that was asked for them with -z. Splitting on
    newlines hands back a quoted name for anything with a quote, a backslash or
    a newline in it, and a quoted name matches no file."""
    out = subprocess.run(
        [*GIT, "-C", str(root), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if must and out.returncode != 0:
        raise Bad(f"git {' '.join(args)}: {out.stderr.strip()[:300]}")
    return [n for n in out.stdout.split("\0") if n]


def measured(path: str) -> bool:
    """What the tool writes next to an order: a measurement, not part of the work."""
    return fnmatch.fnmatchcase(path, "work/orders/*/result.json") or (
        fnmatch.fnmatchcase(path, "work/orders/*/touched.json")
    )


def dirty(root: Path) -> list[str]:
    """Paths with uncommitted changes, every untracked file by name. The first
    column of a status line is a space for an unstaged change, so the entries
    are read unstripped."""
    fields = names(root, "status", "--porcelain", "-z", "--untracked-files=all")
    out = []
    while fields:
        entry = fields.pop(0)
        out.append(entry[3:])
        # A rename is two paths, and the one that went away matters as much.
        if entry[0] in "RC" and fields:
            out.append(fields.pop(0))
    return [p for p in out if not measured(p)]


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

    def owns_path(self, path: str) -> bool:
        """Its own: the order's folder, owns, and what anyone may change."""
        return (
            path.startswith(self.rel)
            or any(covers(o, path) for o in self.owns)
            or any(covers(a, path) for a in ANYONE)
        )

    def may_touch(self, path: str) -> bool:
        """What it may change: its own, and what harness.py renders, which
        strays() accepts only while `harness.py check` reproduces it."""
        return self.owns_path(path) or path in regenerable(self.root)


# The harness generator and its lock: what it renders is regenerated by any
# order, like GENERATED, and `harness.py check` guards those files instead:
# strays() runs it whenever an order changed one it does not own.
HARNESS = ".agents/utils/harness.py"
HARNESS_LOCK = ".agents/generated.lock"
_regenerable: dict[tuple, frozenset[str]] = {}


def _harness(root: Path):
    """The generator of this checkout, loaded from its file; a broken one is Bad."""
    if not (root / HARNESS).is_file():
        raise Bad(f"{root / HARNESS_LOCK}: lists outputs, and there is no {HARNESS}")
    name = f"work_harness_{hashlib.sha256(str(root).encode()).hexdigest()[:8]}"
    spec = importlib.util.spec_from_file_location(name, root / HARNESS)
    if not spec or not spec.loader:
        raise Bad(f"{root / HARNESS}: cannot be loaded")
    harness = importlib.util.module_from_spec(spec)
    # A dataclass looks its module up by name while the class is built.
    sys.modules[name] = harness
    try:
        spec.loader.exec_module(harness)
    except Exception as e:
        raise Bad(f"{root / HARNESS}: {e}") from None
    return harness


def harness_drift(root: Path) -> list[str]:
    """What `harness.py check` finds in this checkout: a rendered output that
    no sync of the tracked sources reproduces, such as a hand edit."""
    try:
        return list(_harness(root).check(root))
    except Bad:
        raise
    except Exception as e:  # a check that cannot run vouches for nothing
        return [f"harness.py check could not run: {e}"]


def regenerable(root: Path) -> frozenset[str]:
    """The outputs .agents/generated.lock lists, when the generator renders
    every one of them. A path it does not render, such as a hand-maintained
    doc, is refused: listing a file in the lock must not free it from owns."""
    lock = root / HARNESS_LOCK
    if not lock.is_file():
        return frozenset()
    stamp = tuple(
        (p.stat().st_mtime_ns, p.stat().st_size) if p.is_file() else None
        for p in (lock, root / HARNESS, root / "config.toml")
    )
    key = (str(root), stamp)
    if key not in _regenerable:
        listed = set(_toml(lock).get("outputs", {}))
        harness = _harness(root)
        try:
            rendered = set(harness.rendered_paths(root))
        except Exception as e:  # a broken generator frees nothing
            raise Bad(f"{root / HARNESS}: {e}") from None
        stray = sorted(listed - rendered)
        if stray:
            raise Bad(
                f"{lock}: lists {', '.join(stray)}, which {HARNESS} does not "
                f"render; a hand-maintained file stays in an order's owns"
            )
        _regenerable[key] = frozenset(listed)
    return _regenerable[key]


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
        inside = (
            names(root, "ls-files", "-z", "--", entry) if entry.endswith("/") else []
        )
        for name in (entry, *inside):
            home = teams.of(name)
            if home is None:
                raise Bad(
                    f"{path}: owns {name!r}, which no team in work/teams.toml covers"
                )
            if home not in (data["team"], "shared", *cross):
                raise Bad(
                    f"{path}: owns {entry!r}, but {name!r} belongs to team {home!r}; "
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


def readable(root: Path, teams: Teams) -> tuple[list[Order], list[str]]:
    """The orders that load, and one sentence for each that does not. Reading
    across worktrees has to survive a draft somebody else has just started."""
    base, good, drafts = root / "work" / "orders", [], []
    for d in sorted(base.iterdir()) if base.is_dir() else []:
        if (d / "order.toml").is_file():
            try:
                good.append(load_order(d, teams, root))
            except Bad as e:
                drafts.append(str(e))
    return good, drafts


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
    """Orders whose accepting review is on main: it travels with the work."""
    on_main = names(
        root, "ls-tree", "-r", "--name-only", "-z", "origin/main", "work/orders/"
    )
    done = set()
    for name in on_main:
        if name.endswith("/review.toml"):
            try:
                ruling = tomllib.loads(git(root, "show", f"origin/main:{name}"))
            except tomllib.TOMLDecodeError:
                continue
            if ruling.get("verdict") == "accept":
                done.add(name.split("/")[2])
    return done


def active(root: Path = ROOT, drafts: list[str] | None = None) -> list[Order]:
    """Orders being worked on now: their branch is checked out in some worktree.
    Unreadable ones are skipped, and named in `drafts` when the caller asks."""
    done, found = landed(root), {}
    for path, branch in worktrees(root):
        try:
            orders, bad = readable(path, load_teams(path))
        except (Bad, FileNotFoundError):
            continue
        if drafts is not None:
            drafts += bad
        for order in orders:
            if order.branch == branch and order.id not in done:
                found[order.id] = order
    return list(found.values())


def collisions(orders: list[Order], involving: set[str] | None = None) -> list[str]:
    """Two orders that cannot both be built as written: they own the same file,
    or they share a branch, where each would count the other's files as strays.
    A shared file is no clash when one order lists the other in `needs`: they
    run one after the other, as `plan` puts them, and the later one builds on
    the earlier one's branch. With `involving`, only the pairs one of those
    orders is part of."""
    out = []
    for i, a in enumerate(orders):
        for b in orders[i + 1 :]:
            if involving is not None and not {a.id, b.id} & involving:
                continue
            if a.branch == b.branch:
                out.append(f"{a.id} and {b.id} share the branch {a.branch}")
            if a.id in b.needs or b.id in a.needs:
                continue
            hit = [(x, y) for x in a.owns for y in b.owns if overlap(x, y)]
            if hit:
                x, y = hit[0]
                out.append(
                    f"{a.id} and {b.id} both own {x if x == y else x + ' / ' + y}"
                )
    return out


# A test marked integration may fetch the internet, and a publisher's outage is
# no reason for an order to fail: a criterion's command runs offline.
INTEGRATION = re.compile(
    r"^\s*(@pytest\.mark\.integration|pytestmark\b.*\bmark\.integration)\b", re.M
)


def online(order: Order) -> list[str]:
    """Each criterion that runs pytest over a file with integration tests and
    does not deselect them, as a sentence. A warning: the marker may be off."""
    out = []
    for c in order.criteria:
        for part in re.split(r"&&|\|\||[;|]", c.check or ""):
            try:
                words = shlex.split(part)
            except ValueError:
                words = part.split()
            if "pytest" not in words:
                continue
            args = words[words.index("pytest") + 1 :]
            if any("not integration" in w for w in args):
                continue
            # A path, not the value of -m or -k; a file not written yet is none.
            given = [
                w.split("::")[0]
                for w in args
                if w[:1] != "-" and ("/" in w or w.split("::")[0].endswith(".py"))
            ]
            # With no path pytest runs its testpaths, which here is tests/.
            paths = [order.root / g for g in given or ["tests"]]
            files = sorted(
                f
                for g in paths
                for f in ([g] if g.is_file() else g.rglob("*.py") if g.is_dir() else [])
            )
            hits = [
                f.relative_to(order.root).as_posix()
                for f in files
                if INTEGRATION.search(f.read_text(encoding="utf-8", errors="replace"))
            ]
            if hits:
                out.append(
                    f"{order.id} {c.id} runs pytest on {', '.join(hits)}, which has "
                    f"integration tests, without -m 'not integration'"
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
    mine = set(diff_names(root, base))
    loose = dirty(root)
    if loose:
        # An uncommitted file is this branch's work only if it differs from
        # base: in the middle of a merge, everything arriving from main is
        # uncommitted too, and none of it is ours. The index is asked as well as
        # the working tree, or a change that is only staged reads as no change.
        differs: set[str] = set()
        for where in ((), ("--cached",)):  # the working tree, then the index
            args = ("diff", *where, "--name-only", "--no-renames", "-z", base, "--")
            differs |= set(names(root, *args, *loose, must=True))
        new = set(
            names(root, "ls-files", "--others", "--exclude-standard", "-z", must=True)
        )
        mine |= {n for n in loose if n in differs or n in new}
    return sorted(n for n in mine if n)


def diff_names(root: Path, base: str, rev: str = "HEAD") -> list[str]:
    """Paths that differ between the merge base and rev. A shallow clone may
    lack the merge base, so deepen once; after that, not knowing is an error."""
    args = ("diff", "--name-only", "--no-renames", "-z", f"{base}...{rev}")
    try:
        return names(root, *args, must=True)
    except Bad:
        git(root, "fetch", "--no-tags", "--deepen=500", "origin")
        return names(root, *args, must=True)


def strays(
    order: Order, base: str, files: list[str] | None = None, rev: str | None = None
) -> list[str]:
    """What the order changed and may not touch: `files` as its branch changed
    them (the checkout's changes by default), read at rev (the working tree when
    None)."""
    files = changed(order.root, base) if files is None else files
    out = [p for p in files if not order.may_touch(p)]
    carried = inherited(order, base, out, rev) if out else set()
    out = [p for p in out if p not in carried]
    # A rendered output it does not own is its change only as a regeneration.
    freed = [p for p in files if p in regenerable(order.root)]
    freed = [p for p in freed if not order.owns_path(p)]
    drift = harness_drift(order.root) if freed else []
    if drift:
        why = "; ".join(drift[:3])
        out += [f"{p} (rendered, and harness.py check finds: {why})" for p in freed]
    return out


def inherited(order: Order, base: str, paths: list[str], rev: str | None) -> set[str]:
    """Of these paths, those an order this one needs changed on its branch and
    this one carries exactly as that branch left them. The later order builds
    on the earlier one's branch before it lands (see collisions), so that work
    is the earlier order's, answered for there. A needed order whose branch
    cannot be found vouches for nothing."""
    by_id = {o.id: o for o in orders_in(order.root, load_teams(order.root))}
    at = (rev,) if rev else ()
    new = set()
    if not rev:
        args = ("ls-files", "--others", "--exclude-standard", "-z")
        new = set(names(order.root, *args, must=True))
    out: set[str] = set()
    for nid in order.needs:
        need = by_id.get(nid)
        if need is None:
            continue
        try:
            theirs = tip(order.root, need.branch)
        except Bad:
            continue
        # Once both branches merged main there are several merge bases, and
        # git names main's when asked for one; the needed work is at another.
        points = git(order.root, "merge-base", "--all", rev or "HEAD", theirs)
        for point in points.split():
            built = set(diff_names(order.root, base, point)) & set(paths)
            if not built:
                continue
            # Differs from what the needed branch built: in the tree, or staged.
            moved: set[str] = set()
            for where in ((), ("--cached",)) if not rev else ((),):
                args = ("diff", *where, "--name-only", "--no-renames", "-z")
                args += (point, *at, "--", *built)
                moved |= set(names(order.root, *args, must=True))
            out |= built - moved - new
    return out


def tip(root: Path, branch: str) -> str:
    """The newest commit of a branch: in this clone, else on origin. A pull
    request's runner has only the commit it tests, so origin is asked once."""
    refs = (f"refs/heads/{branch}", f"refs/remotes/origin/{branch}")
    for ref in refs:
        if sha := git(root, "rev-parse", "--verify", "-q", ref + "^{commit}"):
            return sha
    if git(root, "check-ref-format", "--normalize", refs[0]) == refs[0]:
        git(root, "fetch", "-q", "--no-tags", "origin", f"+{refs[0]}:{refs[1]}")
        if sha := git(root, "rev-parse", "--verify", "-q", refs[1] + "^{commit}"):
            return sha
    raise Bad(
        f"branch {branch} is neither in this clone nor on origin, so what it "
        f"changed cannot be told apart from the rest of this pull request"
    )


def own_files(order: Order, base: str, head: str) -> tuple[list[str], str | None]:
    """What the order's own branch changed, as this checkout carries it, and the
    commit to read it at: all of it on that branch (the working tree), and in a
    train car the part of the branch the car merged, so a loose change riding
    in the same car is nobody's stray."""
    if order.branch == head:
        return changed(order.root, base), None
    merged = git(order.root, "merge-base", "HEAD", tip(order.root, order.branch))
    if not merged:
        raise Bad(f"branch {order.branch} and this pull request share no commit")
    return diff_names(order.root, base, merged), merged


def tree_key(root: Path) -> str:
    """The exact state of the checkout: a result is only good for the tree it saw."""
    paths = dirty(root)
    parts = [git(root, "rev-parse", "HEAD"), git(root, "diff", "HEAD")]
    for rel in paths:
        file = root / rel
        if file.is_file():
            parts.append(rel + hashlib.sha1(file.read_bytes()).hexdigest())
    return hashlib.sha1("\n".join(parts).encode()).hexdigest()


def last_result(order: Order) -> dict | None:
    path = order.dir / "result.json"
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None
    except json.JSONDecodeError:
        return None


def _run(cmd: str, cwd: Path, timeout: int) -> tuple[int, str]:
    """A criterion's command in its own process group, so that a timeout ends
    the browsers and servers it started and not only the shell."""
    proc = subprocess.Popen(
        cmd,
        shell=True,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )
    try:
        out, _ = proc.communicate(timeout=timeout)
        return proc.returncode, out[-1200:]
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.communicate()
        return 124, f"timed out after {timeout}s"


def run_check(
    order: Order, base: str, force: bool = False, budget: int | None = None
) -> dict:
    """Ownership, then every command. The cache is the builder's convenience:
    it is a file the builder can write, so acceptance always passes force."""
    out_path = order.dir / "result.json"
    key = tree_key(order.root)
    old = None if force else last_result(order)
    if old and old.get("tree") == key and old.get("ok"):
        old["cached"] = True
        return old
    result: dict = {"order": order.id, "tree": key, "strays": strays(order, base)}
    rows, began = [], time.monotonic()
    for c in order.criteria:
        if not c.check:
            rows.append({"id": c.id, "judge": c.judge, "text": c.text})
            continue
        start = time.monotonic()
        spent = int(start - began)
        allowed = (
            c.timeout if budget is None else max(1, min(c.timeout, budget - spent))
        )
        code, tail = _run(c.check, order.root, allowed)
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
    if budget is None:
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


SHA = re.compile(r"^[0-9a-f]{40}$")


def contribution(order: Order, base: str, rev: str) -> str:
    """What the branch adds to the files the order owns, and to the order itself,
    as a patch id: the same after a clean merge of main, different after any
    edit, whitespace included."""
    span = f"{base}...{rev}"
    touched = names(
        order.root,
        *("diff", "--name-only", "--no-renames", "-z", span, "--"),
        *order.owns,
        order.rel + "order.toml",
        must=True,
    )
    # The rulings are about the contribution, not part of it: an order that owns
    # work/ would otherwise end its own review by committing it.
    rulings = (order.rel + "review.toml", order.rel + "signoff-*.toml")
    paths = [p for p in touched if not any(fnmatch.fnmatchcase(p, r) for r in rulings)]
    if not paths:
        return ""
    diff = subprocess.run(
        [*GIT, "-C", str(order.root), "diff", "--no-renames", span, "--", *paths],
        capture_output=True,
        check=False,
    )
    if diff.returncode != 0:
        raise Bad(
            f"git diff {base}...{rev}: {diff.stderr.decode(errors='replace')[:300]}"
        )
    # Bytes in and out: an owned file does not have to be UTF-8. Verbatim,
    # because indentation is meaning in Python and in YAML.
    ident = subprocess.run(
        ["git", "patch-id", "--verbatim"],
        input=diff.stdout,
        capture_output=True,
        check=False,
    )
    return ident.stdout.split(b" ")[0].strip().decode()


def _signed(order: Order, path: Path, who: str, base: str) -> dict:
    """A review or a sign-off: by someone else, about this order, still current."""
    data = _toml(path)
    _version(data, path)
    if data.get("order") != order.id:
        raise Bad(f"{path}: order = {data.get('order')!r}, expected {order.id!r}")
    by = str(data.get("by", "")).strip()
    if not by:
        raise Bad(f"{path}: by is missing: a {who} has a name")
    if not order.builder:
        raise Bad(
            f"{order.dir / 'order.toml'}: builder is empty, so nobody can tell "
            f"whether {by!r} is someone else"
        )
    if by == order.builder:
        raise Bad(f"{path}: by = {by!r} is the builder; nobody accepts their own work")
    if data.get("verdict") not in ("accept", "improve"):
        raise Bad(f"{path}: verdict is accept or improve")
    sha = str(data.get("reviewed", ""))
    if not SHA.match(sha):
        raise Bad(f"{path}: reviewed = {sha!r}: the full commit id, not a name for it")
    contained = subprocess.run(
        [*GIT, "-C", str(order.root), "merge-base", "--is-ancestor", sha, "HEAD"],
        capture_output=True,
        check=False,
    )
    if contained.returncode != 0:
        raise Bad(f"{path}: reviewed = {sha!r} is not a commit this branch contains")
    if contribution(order, base, sha) != contribution(order, base, "HEAD"):
        raise Bad(
            f"{path}: the order or a file it owns changed after the {who} looked; "
            f"review again and update reviewed"
        )
    return data


def load_review(order: Order, base: str = "origin/main") -> dict:
    path = order.dir / "review.toml"
    if not path.is_file():
        raise Bad(f"{path}: no review yet")
    data = _signed(order, path, "reviewer", base)
    ruled = {str(r.get("id")): r for r in data.get("criteria", [])}
    for c in order.criteria:
        row = ruled.get(c.id)
        if not row or row.get("verdict") not in ("pass", "fail"):
            raise Bad(f"{path}: criterion {c.id} has no pass or fail")
        if not str(row.get("evidence", "")).strip():
            raise Bad(f"{path}: criterion {c.id} has a verdict and no evidence")
    return data


def acceptance(order: Order, base: str, run: bool = True) -> list[str]:
    """Everything between this order and main, as sentences. Empty means land it.
    With `run` the commands are measured afresh; CI passes False because the
    battery next to it runs the same tests."""
    why, reviewer = [], ""
    if run and not run_check(order, base, force=True)["ok"]:
        why.append("the checks do not pass (just work-check)")
    try:
        review = load_review(order, base)
        reviewer = str(review["by"]).strip()
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
            signed = _signed(order, path, f"{team} manager", base)
            if signed.get("team") != team:
                raise Bad(f"{path}: team = {signed.get('team')!r}, expected {team!r}")
            if str(signed["by"]).strip() == reviewer:
                raise Bad(
                    f"{path}: by = {reviewer!r} also wrote the review; a team's "
                    f"manager speaks for the team, not for the review"
                )
            if signed["verdict"] != "accept":
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


def plan(gid: str, root: Path = ROOT) -> tuple[list[list[Order]], dict[str, list[str]]]:
    """Launch groups: what an order needs has landed or ran in an earlier group,
    no two orders in a group own the same file, and a group fits the budget.
    Next to them, what cannot start yet and which orders it waits for: an order
    of another goal that has not landed, or one here that waits itself. Only
    orders that wait on each other are a mistake in the plan."""
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
    ours = {o.id for o in todo}
    blocked: dict[str, list[str]] = {}
    grew = True
    while grew:
        grew = False
        for o in todo:
            waits = [
                n for n in o.needs if n not in done and (n not in ours or n in blocked)
            ]
            if waits and o.id not in blocked:
                blocked[o.id], grew = waits, True
    todo = [o for o in todo if o.id not in blocked]
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
            raise Bad(
                f"goal {gid}: {', '.join(o.id for o in todo)} wait on each other, "
                f"a cycle in needs"
            )
        groups.append(group)
        settled |= {o.id for o in group}
        todo = [o for o in todo if o not in group]
    return groups, blocked


# ---------------------------------------------------------------- the issue
#
# The repository is the record: orders, reviews and sign-offs travel with the
# code. The order's GitHub issue is the conversation. An agent reads it before
# it starts and the tool keeps one status comment there current.

MARK = "<!-- work:{id} -->"
# Anyone can comment on a public issue. What an agent reads as instructions
# comes only from people who can already push here.
TRUSTED = ("OWNER", "COLLABORATOR")


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


def is_status(comment: dict, oid: str = "") -> bool:
    """A status comment of this tool: the marker, from someone who can push. A
    stranger who pastes the marker has written an ordinary untrusted comment."""
    body = str(comment.get("body", ""))
    mark = MARK.format(id=oid) if oid else "<!-- work:"
    return body.startswith(mark) and comment.get("author_association") in TRUSTED


def trusted(comments: list[dict]) -> tuple[list[dict], int]:
    """The comments an agent may read, and how many were held back."""
    keep = [
        c
        for c in comments
        if c.get("author_association") in TRUSTED and not is_status(c)
    ]
    ours = sum(1 for c in comments if is_status(c))
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


def _who(event: dict) -> str:
    """The subagent behind a hook event, or nothing for a session: a session is
    held by what its report says, so nothing would ever read its id."""
    return str(event.get("agent_id") or "")


def _touched(order: Order) -> dict:
    path = order.dir / "touched.json"
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    except json.JSONDecodeError:
        return {}


def _remember(order: Order, who: str, rel: str) -> None:
    """Note which agent worked on which order, so that stopping can be judged by
    what an agent did and not by how it words its report. Someone who only ever
    wrote into the order's folder is reviewing, not building.

    The rule that keeps the file from growing without end: agents are kept in
    the order of their last edit and only the TOUCHED_KEEP most recent stay. An
    agent that is already the most recent with the same role costs no write,
    which is the common case of one builder editing file after file. If one
    ever did go missing it would cost that agent a reminder, never a check:
    what decides is work-check, work-accept and CI."""
    if not who:
        return
    seen = _touched(order)
    role = "builder" if not rel.startswith(order.rel) else seen.get(who, "reviewer")
    if list(seen.items())[-1:] == [(who, role)]:
        return
    seen.pop(who, None)
    seen[who] = role
    kept = dict(list(seen.items())[-TOUCHED_KEEP:])
    (order.dir / "touched.json").write_text(json.dumps(kept), encoding="utf-8")


def hook_pre_tool(event: dict) -> tuple[int, str]:
    """Refuse an edit outside what the orders on this branch own. Anything this
    cannot read lets the edit through: a broken order has to stay repairable,
    and `check` refuses it later anyway."""
    given = event.get("tool_input") or {}
    raw = given.get("file_path") or given.get("notebook_path")
    if not raw or not isinstance(raw, str):
        return 0, ""
    target = Path(raw).resolve()
    root = _repo_of(target.parent)
    if not root or not (root / "work" / "teams.toml").is_file():
        return 0, ""
    try:
        teams = load_teams(root)
        orders, _ = readable(root, teams)
        rel = target.relative_to(root.resolve()).as_posix()
    except (Bad, ValueError):
        return 0, ""
    branch = git(root, "branch", "--show-current")
    mine = [o for o in orders if o.branch == branch]
    if not mine:
        return 0, ""
    if rel.startswith("work/orders/") and rel.endswith(
        ("/result.json", "/touched.json")
    ):
        return (
            2,
            f"{rel} is a measurement tools/work.py writes, not yours to edit",
        )
    for order in mine:
        if order.owns_path(rel):
            _remember(order, _who(event), rel)
            return 0, ""
    try:
        rendered = any(o.may_touch(rel) for o in mine)
    except Bad:
        return 0, ""
    if rendered:
        return 2, (
            f"{rel} is rendered by {HARNESS}: edit its source under .agents/ or "
            f"config.toml and run `uv run python {HARNESS} sync`, never the file"
        )
    home = teams.of(rel) or "nobody"
    ids = ", ".join(o.id for o in mine)
    owns = ", ".join(x for o in mine for x in o.owns)
    return 2, (
        f"{rel} is outside order {ids}; it belongs to team {home}. Leave it and "
        f"report it, or have the manager change owns and cross. Owned here: {owns}"
    )


def hook_stop(
    event: dict, base: str = "origin/main", root: Path = ROOT
) -> tuple[int, str]:
    """Send an agent back once when the order it worked on does not hold. A
    subagent is known by the edits the other hook saw; a session only by a
    report whose first line names the order, because Stop fires at the end of
    every turn and a check can take minutes. This is a reminder for a
    cooperative agent, not the gate: edits made through a shell are never seen
    here. What decides is check, accept and CI."""
    if event.get("stop_hook_active"):
        return 0, ""
    orders = {o.id: o for o in active(root)}
    who, text = _who(event), str(event.get("last_assistant_message", ""))
    roles = {o.id: _touched(o)[who] for o in orders.values() if who in _touched(o)}
    named = ORDER_LINE.search(text)
    if named and named.group(1) in orders and named.group(1) not in roles:
        said = ROLE_LINE.search(text)
        roles[named.group(1)] = said.group(1) if said else "builder"
    for oid, role in roles.items():
        order = orders[oid]
        try:
            if role == "reviewer":
                load_review(order, base)
                continue
            result = run_check(order, base, budget=STOP_BUDGET)
        except Bad as e:
            return 2, str(e)
        if not result["ok"]:
            return 2, "The order does not hold yet, so this is not done:\n" + show(
                result
            )
    return 0, ""


# ---------------------------------------------------------------- commands

TEMPLATE = """v = 1
id = {id}
title = {title}
team = {team}
branch = {branch}
goal = {goal}
# Whoever builds this writes their name here; a review by the same name does not count.
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


def _q(text: str) -> str:
    """A TOML basic string: JSON's escapes are a subset of TOML's."""
    return json.dumps(text, ensure_ascii=False)


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
            id=_q(a.id),
            title=_q(a.title),
            team=_q(a.team),
            branch=_q(branch),
            goal=_q(a.goal or ""),
        ),
        encoding="utf-8",
    )
    print(
        f"wrote {folder.relative_to(ROOT)}/order.toml, a draft: it loads once owns, "
        f"builder and a criterion are filled in, and guards nothing until then"
    )
    return 0


def cmd_validate(_: argparse.Namespace) -> int:
    orders = orders_in(ROOT, load_teams())
    drafts: list[str] = []
    live = active(ROOT, drafts)
    # A builder's check judges its own order: a clash between two orders in
    # other worktrees is theirs to settle. A checkout building none sees all.
    here = git(ROOT, "branch", "--show-current")
    mine = {o.id for o in orders if o.branch == here} or None
    clash = collisions(live, mine)
    for line in clash:
        print("collision:", line)
    for line in collisions(live):
        if line not in clash:
            print("collision elsewhere, not this branch's:", line)
    for line in drafts:
        print("draft elsewhere, not judged:", line)
    for order in orders:
        for line in online(order):
            print("warning:", line)
    print(
        f"{len(orders)} orders read, {len(clash)} collisions this checkout answers for"
    )
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
    groups, blocked = plan(a.goal)
    for n, group in enumerate(groups, 1):
        print(f"group {n}")
        for o in group:
            print(f"  {o.id:<28} {o.team:<9} {', '.join(o.owns)}")
    if blocked:
        print("blocked, until what they need has landed")
        for oid, waits in blocked.items():
            print(f"  {oid} blocked by {', '.join(waits)}")
    return 0


def cmd_board(_: argparse.Namespace) -> int:
    done = landed()
    rows = []
    for order in active():
        ok = (last_result(order) or {}).get("ok")
        checks = {True: "pass", False: "FAIL", None: "not run"}[ok]
        review = "yes" if (order.dir / "review.toml").is_file() else "no"
        rows.append((order.id, order.team, order.branch, checks, review))
    print(f"{'order':<28} {'team':<9} {'branch':<34} {'checks':<8} review")
    for r in rows:
        print(f"{r[0]:<28} {r[1]:<9} {r[2]:<34} {r[3]:<8} {r[4]}")
    print(f"{len(rows)} active, {len(done)} landed")
    return 0


def cmd_ci(a: argparse.Namespace) -> int:
    """On a pull request. The orders it carries are those whose folder it touches
    and those written for its branch, so leaving the folder alone hides nothing.
    Each has to be readable. Each order is judged by itself, so a train car can
    carry several: one that is built ships its accepted review and every
    sign-off, and stays inside its files, measured on what its own branch
    changed. An order is built when the pull request touches a file it owns, or
    when it names a builder and the pull request ships code; one with no builder
    and none of its files touched is a plan, and a plan needs no review. A pull
    request that carries no order is left alone."""
    files = diff_names(ROOT, a.base)
    orders = {o.id: o for o in orders_in(ROOT, load_teams())}
    carried = {n.split("/")[2] for n in files if n.startswith("work/orders/")}
    head = (
        a.head
        or os.environ.get("GITHUB_HEAD_REF")
        or git(ROOT, "branch", "--show-current")
    )
    done = landed()
    carried |= {
        o.id for o in orders.values() if head and o.branch == head and o.id not in done
    }
    carried &= set(orders)
    ships_code = any(not n.startswith("work/") for n in files)
    bad = []
    for oid in sorted(carried):
        order = orders[oid]
        touches = any(covers(o, n) for n in files for o in order.owns)
        built = touches or (bool(order.builder) and ships_code)
        if built:
            bad += [f"{oid}: {w}" for w in acceptance(order, a.base, run=False)]
        if not built and order.branch != head:
            continue
        try:
            own, at = own_files(order, a.base, head)
            bad += [
                f"{oid}: {s} is outside what it owns"
                for s in strays(order, a.base, own, at)
            ]
        except Bad as e:
            bad.append(f"{oid}: {e}")
    for line in bad:
        print("work:", line)
    print(f"work: {len(carried)} orders in this pull request, {len(bad)} problems")
    return 1 if bad else 0


def cmd_sweep(_: argparse.Namespace) -> int:
    """Remove the orders that have landed: main has their review, git has the rest."""
    gone = []
    for oid in sorted(landed()):
        folder = ROOT / "work" / "orders" / oid
        if folder.is_dir():
            shutil.rmtree(folder)
            gone.append(oid)
    print(f"swept {len(gone)} landed orders: {', '.join(gone) or 'none'}")
    return 0


def cmd_post(a: argparse.Namespace) -> int:
    order = find(a.id)
    issue = _issue_of(order)
    try:
        review = load_review(order)
    except Bad:
        review = None
    body = status_comment(order, last_result(order), review)
    mine = [c for c in _comments(issue) if is_status(c, order.id)]
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
    number = _issue_of(order)
    issue = json.loads(_gh(f"repos/{{owner}}/{{repo}}/issues/{number}"))
    if issue.get("author_association") in TRUSTED:
        print(
            f"=== #{number} {issue.get('title', '')}\n"
            + str(issue.get("body") or "").strip()
        )
    keep, held = trusted(_comments(number))
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


def cmd_hook(a: argparse.Namespace) -> int:
    """Whatever arrives, a hook answers 0 or 2. A traceback would read as a
    broken harness to every agent in the session."""
    try:
        event = json.loads(sys.stdin.read() or "{}")
        if not isinstance(event, dict):
            return 0
        if not isinstance(event.get("tool_input") or {}, dict):
            return 0
        code, why = (hook_pre_tool if a.which == "pre-tool" else hook_stop)(event)
    except Exception as e:  # noqa: BLE001  a hook must not fall over
        print(f"work hook let go: {type(e).__name__}: {e}", file=sys.stderr)
        return 0
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
    ci = sub.add_parser("ci")
    ci.add_argument("--base", default="origin/main")
    ci.add_argument("--head", default="", help="the pull request's branch")
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
