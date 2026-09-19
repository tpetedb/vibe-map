"""Targeted checks for the recurring mistake classes in this repo.

Usage:
    uv run python tools/checks.py style [paths...]   em dashes and emoji
    uv run python tools/checks.py links              every https link answers
    uv run python tools/checks.py sinks [--write]    values the game writes as HTML

Each check prints one line per finding and exits 1 when there is any, so an
agent can run it after every edit instead of rediscovering the failure in
review. Lines longer than MAX_LINE are skipped by the style check: they are
minified vendor code, not prose.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

from rich.console import Console

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {
    ".md", ".py", ".js", ".html", ".css", ".toml", ".yml", ".yaml",
    ".json", ".sh", ".zsh", ".just", ".txt", ".sql", ".env", ".example",
}  # fmt: skip
TEXT_NAMES = {"justfile", "agents.just", ".gitignore", ".env.example"}
MAX_LINE = 1000
EM_DASH = chr(0x2014)
# The house rules are about the copy we write. These two files are other
# people's published words, pulled verbatim by `vibe news`; editing an em dash
# out of a headline would be editing the headline (docs/adr/0010).
QUOTED_VERBATIM = frozenset({"data/news.json", "game/news.json", "vault/Camp/News.md"})


def _emoji_pattern() -> re.Pattern[str]:
    """Emoji code point ranges, built from numbers so this file contains none."""
    ranges = [
        (0x1F300, 0x1FAFF),
        (0x1F1E6, 0x1F1FF),
        (0x2600, 0x27BF),
        (0xFE0F, 0xFE0F),
    ]
    body = "".join(chr(a) if a == b else f"{chr(a)}-{chr(b)}" for a, b in ranges)
    return re.compile(f"[{body}]")


EMOJI = _emoji_pattern()
URL = re.compile(r"https?://[^\s)\]\"'<>`]+")
LINK_SOURCES = (
    "README.md",
    "HANDOVER.md",
    "docs/SYLLABUS.md",
    "docs/RESOURCES.md",
    "docs/ROADMAP.md",
    "docs/AOE-STUDY.md",
    "vibemap/data/topics",
    "vibemap/data/campaign.json",
    "vibemap/data/resources.md",
)
# Sites that answer bots with 403 or 405 are reported, not failed: the link
# still works for a person in a browser.
SOFT_STATUSES = {401, 403, 405, 429, 999}
# Copied in verbatim from elsewhere; their comments are not our prose.
VENDORED = (
    "src/vendor/",
    # A synced mirror of src/ and tools/build.py; checked at the original.
    "vibemap/data/fork_source/",
    "vibemap/data/dotfiles/",
    ".agents/skills/webapp-testing/",
    ".agents/skills/verification-before-completion/",
)

console = Console(highlight=False)
RED, GREEN, YELLOW, BLUE = "#D32F2F", "#00A86B", "#FFBF00", "#0067A5"


def _tracked_text_files() -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout.split("\n")
    files = []
    for rel in filter(None, out):
        # Vendored third-party files keep their upstream prose (docs/SKILLS.md).
        if rel.startswith(VENDORED):
            continue
        p = ROOT / rel
        if p.suffix in TEXT_SUFFIXES or p.name in TEXT_NAMES:
            files.append(p)
    return files


def check_style(paths: list[str]) -> int:
    """Report em dashes and emoji in prose and code.

    Args:
        paths: Files to scan; every tracked text file when empty.

    Returns:
        The number of findings.
    """
    files = [ROOT / p for p in paths] if paths else _tracked_text_files()
    findings = 0
    for path in files:
        if path.name == "checks.py" or not path.is_file():
            continue
        if path.relative_to(ROOT).as_posix() in QUOTED_VERBATIM:
            continue
        try:
            lines = path.read_text(encoding="utf-8").split("\n")
        except UnicodeDecodeError:
            continue
        for no, line in enumerate(lines, 1):
            if len(line) > MAX_LINE:
                continue
            what = []
            if EM_DASH in line:
                what.append("em dash")
            if EMOJI.search(line):
                what.append("emoji")
            if what:
                findings += 1
                rel = path.relative_to(ROOT)
                console.print(
                    f"[{RED}]{rel}:{no}[/] {', '.join(what)}: {line.strip()[:90]}"
                )
    if findings:
        console.print(f"[{RED}]{findings} style finding(s)[/]")
    else:
        console.print(f"[{GREEN}]style OK[/]: no em dashes, no emoji")
    return findings


def _collect_links() -> dict[str, set[str]]:
    links: dict[str, set[str]] = {}
    for rel in LINK_SOURCES:
        p = ROOT / rel
        if not p.exists():
            continue
        # A source may be a folder: the tech tree is one file per topic.
        for f in sorted(p.rglob("*")) if p.is_dir() else [p]:
            if not f.is_file():
                continue
            text = f.read_text(encoding="utf-8")
            if f.suffix == ".json":
                text = json.dumps(json.loads(text))
            for url in URL.findall(text):
                url = url.rstrip(".,;:\\")
                links.setdefault(url, set()).add(rel)
    return links


def _probe(url: str) -> tuple[str, int | str]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (vibe-map link check)", "Accept": "*/*"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return url, r.status
    except urllib.error.HTTPError as e:
        return url, e.code
    except Exception as e:  # reason: any transport failure is one finding
        return url, type(e).__name__


def check_links() -> int:
    """Probe every link in the docs and the tech tree; return the broken count."""
    links = _collect_links()
    console.print(f"[{BLUE}]probing {len(links)} links[/]")
    broken = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        for url, status in pool.map(_probe, sorted(links)):
            where = ", ".join(sorted(links[url]))
            if isinstance(status, int) and status < 400:
                continue
            if status in SOFT_STATUSES:
                console.print(
                    f"[{YELLOW}]{status}[/] {url}  ({where}) "
                    "bot-blocked, verify by hand"
                )
                continue
            broken += 1
            console.print(f"[{RED}]{status}[/] {url}  ({where})")
    if broken:
        console.print(f"[{RED}]{broken} broken link(s)[/]")
    else:
        console.print(f"[{GREEN}]links OK[/]")
    return broken


# ---- sinks: what the game writes into the page as HTML -----------------------
# The page is built from strings, so a value that reaches innerHTML is markup
# unless it went through esc(). docs/SECURITY-MODEL.md is the rule; this is
# the ratchet: every interpolation inside an HTML template that is not wrapped
# in a helper of SAFE_CALLS, and every sink, is counted in a register somebody
# has looked at. A new one fails until it is escaped or added with a reason to
# believe it is build-time data of ours.
GAME_SRC = ROOT / "src" / "game"
SINK_REGISTER = ROOT / "tools" / "reviewed_sinks.json"
SINK = re.compile(r"\.innerHTML\s*\+?=|\.insertAdjacentHTML\s*\(")
FORBIDDEN_SINKS = {
    "eval": re.compile(r"(?<![\w.])eval\s*\("),
    "new Function": re.compile(r"new\s+Function\s*\("),
    "document.write": re.compile(r"document\.write(ln)?\s*\("),
    "outerHTML": re.compile(r"\.outerHTML\s*="),
    "srcdoc": re.compile(r"\.srcdoc\s*="),
    "a timer given a string": re.compile(r"set(Timeout|Interval)\s*\(\s*[\"'`]"),
}
SAFE_CALLS = ("esc", "icon")


def _template(text: str, i: int, found: list[tuple[str, list[str]]]) -> int:
    """Read the template literal that opens at i; record it and what it holds."""
    static: list[str] = []
    holes: list[str] = []
    i += 1
    while i < len(text) and text[i] != "`":
        if text[i] == "\\":
            i += 2
        elif text.startswith("${", i):
            end = _code(text, i + 2, found, until="}")
            holes.append(text[i + 2 : end].strip())
            i = end + 1
        else:
            static.append(text[i])
            i += 1
    found.append(("".join(static), holes))
    return i + 1


def _code(text: str, i: int, found: list[tuple[str, list[str]]], until: str) -> int:
    """Walk JavaScript from i to the closing brace of a hole, or to the end.

    Strings, comments and regular expressions are told apart the way the
    build tells them apart, so a quote inside a regex is not a string.
    """
    sys.path.insert(0, str(ROOT))
    from tools.build import _DIVIDE_AFTER, _regex_end, _string_end  # noqa: PLC0415

    depth, prev = 0, ""
    while i < len(text):
        c = text[i]
        if c.isspace():
            i += 1
            continue
        if c in "\"'":
            i = _string_end(text, i) or len(text)
        elif c == "`":
            i = _template(text, i, found)
        elif text.startswith("//", i):
            i = text.find("\n", i) % (len(text) + 1)
            continue
        elif text.startswith("/*", i):
            i = text.find("*/", i) % (len(text) + 1) + 2
            continue
        elif c == "/" and prev not in _DIVIDE_AFTER and _regex_end(text, i):
            i = _regex_end(text, i) or len(text)
        elif c == "}" and until == "}" and depth == 0:
            return i
        else:
            depth += (c == "{") - (c == "}")
            i += 1
        prev = c if c not in "\"'`/" else ("/" if c == "/" else "x")
    return i


def _wrapped(expr: str) -> bool:
    """True when the whole expression is one call to a helper of SAFE_CALLS."""
    for name in SAFE_CALLS:
        if not expr.startswith(name + "("):
            continue
        depth = 0
        for k, c in enumerate(expr):
            depth += c == "("
            depth -= c == ")"
            if depth == 0 and c == ")":
                return k == len(expr) - 1
    return False


def scan_sinks(src: Path = GAME_SRC) -> dict[str, dict[str, object]]:
    """Per module: the sinks, and the raw interpolations inside HTML templates."""
    out: dict[str, dict[str, object]] = {}
    for path in sorted(src.glob("*.js")):
        text = path.read_text(encoding="utf-8")
        found: list[tuple[str, list[str]]] = []
        _code(text, 0, found, until="")
        raw: dict[str, int] = {}
        for static, holes in found:
            if "<" not in static:
                continue
            for expr in holes:
                if not _wrapped(expr):
                    raw[expr] = raw.get(expr, 0) + 1
        sinks = len(SINK.findall(text))
        if sinks or raw:
            out[path.name] = {"sinks": sinks, "raw": dict(sorted(raw.items()))}
    return out


def check_sinks(write: bool = False, src: Path = GAME_SRC) -> int:
    findings = 0
    for path in [*sorted(src.glob("*.js")), ROOT / "src" / "errors.js"]:
        text = path.read_text(encoding="utf-8")
        for name, rx in FORBIDDEN_SINKS.items():
            if rx.search(text):
                console.print(f"[red]{path.name}[/]: {name} is never used in the game")
                findings += 1
    now = scan_sinks(src)
    if write:
        SINK_REGISTER.write_text(
            json.dumps(now, indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        console.print(f"wrote {SINK_REGISTER.relative_to(ROOT)}")
        return findings
    seen = json.loads(SINK_REGISTER.read_text(encoding="utf-8"))
    for name, entry in now.items():
        old = seen.get(name, {"sinks": 0, "raw": {}})
        if entry["sinks"] > old["sinks"]:
            console.print(
                f"[red]{name}[/]: {entry['sinks']} HTML sinks, the register has"
                f" {old['sinks']}. Prefer textContent; see docs/SECURITY-MODEL.md."
            )
            findings += 1
        for expr, count in entry["raw"].items():  # type: ignore[union-attr]
            if count > old["raw"].get(expr, 0):
                console.print(
                    f"[red]{name}[/]: ${{{expr}}} goes into HTML without esc()."
                    " Wrap it, or if it is build-time data of ours, run"
                    " tools/checks.py sinks --write and say why in the PR."
                )
                findings += 1
    return findings


def main() -> None:
    ap = argparse.ArgumentParser(prog="checks")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("style", help="em dashes and emoji")
    s.add_argument("paths", nargs="*")
    sub.add_parser("links", help="every https link answers")
    k = sub.add_parser("sinks", help="values written into the page as HTML")
    k.add_argument("--write", action="store_true", help="accept what is there now")
    a = ap.parse_args()
    if a.cmd == "style":
        findings = check_style(a.paths)
    elif a.cmd == "sinks":
        findings = check_sinks(a.write)
    else:
        findings = check_links()
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
