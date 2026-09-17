"""Render docs/COOKBOOK.md from vibemap/personas.py and the general recipes.

One source for the recipes: the personas module. This script writes the
Markdown the docs and the vault both point at.

    uv run python tools/gen_cookbook.py           write docs/COOKBOOK.md
    uv run python tools/gen_cookbook.py --check   exit 1 when it is stale
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from vibemap.personas import PERSONAS  # noqa: E402
from vibemap.providers import PROVIDERS  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "COOKBOOK.md"

GENERAL = [
    (
        "Start the evening",
        "Everything installed, the vault open, the game running.",
        [
            "brew install just",
            "just setup",
            "just start",
        ],
        "The onboarding screen shows every core tool green.",
    ),
    (
        "Claim a workstream",
        "Let the CLI check your work and award the XP.",
        [
            "uv run vibe status",
            "uv run vibe check 1",
            'uv run vibe done 1 "a scoring board that ranks the team by coffee"',
        ],
        "The vault has a dated note for the workstream and Tonight lists it as done.",
    ),
    (
        "Break something on purpose, then come back",
        "A branch is a sandbox. Nothing on main can be hurt from a play branch.",
        [
            "just break sandbox",
            "# ask the agent for anything, however wild",
            "uv run vibe explain",
            "just rescue",
        ],
        "You are back on main, the play branch still exists, "
        "and explain told you what happened.",
    ),
    (
        "Ask the council",
        "Four mentors answer, review each other, a chairman decides.",
        [
            'uv run vibe council "Should I learn git before Python?"',
            "open vault/Camp",
        ],
        "A Council note in the vault with a verdict and three steps for tonight.",
    ),
    (
        "Change the voice",
        "Serious, academic, plain, or one the model writes for you.",
        [
            "uv run vibe theme boardroom",
            "just build",
            "uv run vibe theme rainforest --create "
            '--brief "a jungle expedition, plain tone, no drinks"',
        ],
        "The title screen reads in the new voice after a rebuild.",
    ),
]


def render() -> str:
    lines = [
        "# Cookbook",
        "",
        "Recipes are prompts you paste into your provider plus a definition of done. "
        "The general ones work for everyone; the persona ones are tuned to a field of "
        "work. Switch persona with `uv run vibe persona <id>`; the vault note "
        "*Cookbook* mirrors your persona's section.",
        "",
        "## Your provider",
        "",
        "| provider | run a prompt from a script | docs |",
        "|---|---|---|",
    ]
    for p in PROVIDERS.values():
        argv = " ".join(p.argv('"..."'))
        lines.append(f"| {p.label} | `{argv}` | {p.docs} |")
    lines += ["", "## General recipes", ""]
    for title, goal, steps, done in GENERAL:
        lines += [f"### {title}", "", goal, "", "```bash"]
        lines += steps
        lines += ["```", "", f"**Done when:** {done}", ""]
    for p in PERSONAS.values():
        lines += [f"## {p.label}", "", f"*{p.field}.*", ""]
        lines += [f"**Your game (workstream 1).** {p.game_idea}", ""]
        ds = p.dataset
        lines += [
            "**Your dataset (workstream 3).** "
            f"`workspace/data/examples/{ds.filename}`, "
            f"columns `{', '.join(ds.columns)}`. Write it with "
            f"`uv run vibe persona {p.id}`. Question to answer: {ds.question}",
            "",
            f"**Rolinda asks.** {p.rolinda}",
            "",
        ]
        for r in p.recipes:
            lines += [
                f"### {r.title}",
                "",
                f"Workstream {r.workstream}. {r.goal}",
                "",
                "```text",
                r.prompt,
                "```",
                "",
                f"**Done when:** {r.done}",
                "",
            ]
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    text = render()
    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            print("docs/COOKBOOK.md is stale; run: just cookbook")
            sys.exit(1)
        print("cookbook OK")
        return
    OUT.write_text(text, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
