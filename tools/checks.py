"""Targeted checks for the recurring mistake classes in this repo.

Usage:
    uv run python tools/checks.py style [paths...]   em dashes and emoji
    uv run python tools/checks.py links              every https link answers

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


def main() -> None:
    ap = argparse.ArgumentParser(prog="checks")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("style", help="em dashes and emoji")
    s.add_argument("paths", nargs="*")
    sub.add_parser("links", help="every https link answers")
    a = ap.parse_args()
    findings = check_style(a.paths) if a.cmd == "style" else check_links()
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
