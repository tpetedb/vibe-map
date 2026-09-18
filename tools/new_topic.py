"""Scaffold a topic file, or a whole pack, under vibemap/data/topics/.

A topic is data (ADR 0013), so it starts from the same skeleton every time:
the right keys in the right order, today as the date of check, and TODO
markers where the author has to read the official documentation and write.
The schema test refuses a file that still carries one.

    uv run python tools/new_topic.py topic core rsync --title "rsync"
    uv run python tools/new_topic.py pack cloud --title "The cloud pack"

After writing the words: `just tree`, then `uv run pytest tests/test_topics.py`.
"""

from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOPICS = ROOT / "vibemap" / "data" / "topics"
TODO = "TODO"

TOPIC_TEMPLATE = '''# {title}. Written from the official docs, nothing from memory.
id = "{topic_id}"
title = "{title}"
age = "{age}"
shelf = "{shelf}"
depth = {depth}
# The day every source below was read. Move it when you check them again.
checked = {checked}
minutes = {minutes}

summary = """{todo} what this is, and when you would reach for it."""
history = """{todo} the mental model in five sentences, each one from a source."""
try_it = """{todo} the smallest real thing, under twenty minutes, no cloud account."""

unlocks = []
prerequisites = []

[[sources]]
label = "{todo} the official page this topic is written from"
url = "https://{todo}.invalid"

[[sources]]
label = "{todo} the second source"
url = "https://{todo}.invalid"

[[sources]]
label = "{todo} the third source"
url = "https://{todo}.invalid"

# The hands-on: a folder in the workspace and one offline check. The kinds are
# in vibemap/artifact_checks.py; delete this block if the topic has no exercise.
[hands_on]
title = "{todo} what the learner builds"
minutes = 20
done = "{todo} how the learner knows it worked"
check = {{ kind = "files", files = {{ "notes.md" = ["{todo} a line it reads"] }} }}
'''

PACK_TEMPLATE = '''# {title}
id = "{pack_id}"
title = "{title}"
blurb = """{todo} what this pack covers and who it is for."""
shelf = "{shelf}"
order = {order}
maintainer = """{todo} how this pack is reviewed and what it never does."""

# Reading order, which is also the order of the roadmap and the notes.
topics = [
]
'''


def _write(path: pathlib.Path, text: str) -> None:
    if path.exists():
        raise SystemExit(f"{path.relative_to(ROOT)} already exists; nothing written")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)}")


def _add_to_pack(manifest: pathlib.Path, topic_id: str) -> None:
    """Put the new id last in the pack's reading order, where it belongs."""
    lines = manifest.read_text(encoding="utf-8").splitlines()
    entry = f'  "{topic_id}",'
    if entry in lines:
        return
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == "]":
            lines.insert(i, entry)
            break
    else:
        raise SystemExit(f"{manifest.name} has no topics list to add to")
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"added {topic_id} to {manifest.relative_to(ROOT)}")


def new_topic(args: argparse.Namespace) -> None:
    folder = TOPICS / args.pack
    if not (folder / "pack.toml").exists():
        raise SystemExit(
            f"no pack {args.pack!r}; make one first: "
            f"uv run python tools/new_topic.py pack {args.pack} --title ..."
        )
    _write(
        folder / f"{args.topic}.toml",
        TOPIC_TEMPLATE.format(
            topic_id=args.topic,
            title=args.title or args.topic,
            age=args.age,
            shelf=args.shelf,
            depth=args.depth,
            minutes=args.minutes,
            checked=dt.date.today().isoformat(),
            todo=TODO,
        ),
    )
    _add_to_pack(folder / "pack.toml", args.topic)
    print("now write the words from the official docs, then run: just tree")


def new_pack(args: argparse.Namespace) -> None:
    _write(
        TOPICS / args.pack / "pack.toml",
        PACK_TEMPLATE.format(
            pack_id=args.pack,
            title=args.title or args.pack,
            shelf=args.shelf,
            order=args.order,
            todo=TODO,
        ),
    )
    print(f"now add topics: uv run python tools/new_topic.py topic {args.pack} <id>")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="new_topic")
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("topic", help="a topic file inside a pack")
    t.add_argument("pack")
    t.add_argument("topic")
    t.add_argument("--title", default="")
    t.add_argument("--shelf", default="agents")
    t.add_argument("--age", default="imperial")
    t.add_argument("--depth", type=int, default=2, choices=(1, 2, 3))
    t.add_argument("--minutes", type=int, default=20)
    t.set_defaults(fn=new_topic)
    p = sub.add_parser("pack", help="a new pack folder")
    p.add_argument("pack")
    p.add_argument("--title", default="")
    p.add_argument("--shelf", default="agents")
    p.add_argument("--order", type=int, default=100)
    p.set_defaults(fn=new_pack)
    args = ap.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main(sys.argv[1:])
