"""The council of mentors: the llm-council pattern with the twelve mentors.

Three stages, the way karpathy/llm-council does it with several models:
each mentor answers the question in character, grounded in the ideas and
sources recorded for them in campaign.json; each mentor then reviews the
other answers anonymised; a chairman synthesises the ranking into minutes.
Every stage is one call to the configured provider CLI in print mode, so it
works with any of them and costs a handful of calls.
"""

from __future__ import annotations

import datetime as dt
import re
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING

from vibemap import campaign
from vibemap.providers import ask
from vibemap.themes import THEMES, THEMES_DIR, Theme, load_theme
from vibemap.vault import safe_title

if TYPE_CHECKING:
    from vibemap.cli import Ctx
    from vibemap.state import State

MAX_MENTORS = 4
GROUNDING = (
    "Answer only with positions you can attribute to this person's recorded ideas "
    "and sources below. If the sources do not cover the question, say so in their "
    "voice instead of inventing a view. Never invent quotes or numbers. Plain "
    "language, at most 180 words, no bullet lists."
)


def _mentor_prompt(m: dict, topic: str) -> str:
    ideas = "\n".join(f"- {i}" for i in m["ideas"])
    sources = "\n".join(f"- {t}: {u}" for t, u in m["src"])
    return (
        f"You are {m['name']}, {m['role']}. {GROUNDING}\n\n"
        f"Recorded ideas:\n{ideas}\n\nGoing deeper: {m['deep']}\n\n"
        f"Sources:\n{sources}\n\n"
        f"Question from a learner: {topic}\n\nYour answer, in character:"
    )


def _review_prompt(m: dict, topic: str, answers: dict[str, str]) -> str:
    block = "\n\n".join(f"Answer {k}:\n{v}" for k, v in answers.items())
    return (
        f"You are {m['name']}, {m['role']}. Below are anonymised answers from other "
        f"people to the question: {topic}\n\n{block}\n\n"
        "Rank them from most to least useful for a beginner, with one sentence per "
        "answer saying why. Format: a line per answer, 'A: reason'. "
        "Be honest, not polite."
    )


def _chair_prompt(
    topic: str, answers: dict[str, str], reviews: dict[str, str], key: dict[str, str]
) -> str:
    block = "\n\n".join(f"Answer {k} (by {key[k]}):\n{v}" for k, v in answers.items())
    rev = "\n\n".join(f"Review by {who}:\n{r}" for who, r in reviews.items())
    return (
        "You are the chairman of a council. Synthesise the answers and the peer "
        f"reviews on this question: {topic}\n\n{block}\n\n{rev}\n\n"
        "Write minutes in Markdown with exactly these headings: ## Verdict (three "
        "sentences), ## Where they agree, ## Where they disagree, ## What to do "
        "tonight (three concrete steps), ## Ranking (the answers in the order the "
        "reviews put them, naming the person). No em dashes, no emoji."
    )


def seated(state: State, mentor_ids: list[str]) -> tuple[list[dict], list[str]]:
    """Who sits at the table, and the names that did not fit on it.

    With no ids the island the learner is on picks the mentors, the same
    island `vibe status` calls next; the table seats MAX_MENTORS.

    Raises:
        ValueError: when an id names nobody.
    """
    mentors = campaign.mentors()
    if mentor_ids:
        chosen = [campaign.mentor(i) for i in mentor_ids]
    else:
        here = campaign.current_world(state)
        chosen = [m for m in mentors if m["world"] == here] or mentors
    return chosen[:MAX_MENTORS], [m["name"] for m in chosen[MAX_MENTORS:]]


def convene(
    ctx: Ctx, topic: str, *, mentors: list[dict], dry_run: bool = False
) -> Path | None:
    """Run the three stages and write the minutes to the vault.

    Returns:
        The path of the minutes note, or None on a dry run.

    Raises:
        ValueError: on an empty topic or an empty council.
    """
    if not topic.strip():
        raise ValueError("the council needs a question")
    chosen = mentors
    if not chosen:
        raise ValueError("no mentors selected")
    provider = ctx.cfg.learner.provider
    labels = [chr(ord("A") + i) for i in range(len(chosen))]
    key = {lab: m["name"] for lab, m in zip(labels, chosen, strict=True)}

    if dry_run:
        for m in chosen:
            print(f"--- {m['name']} ---\n{_mentor_prompt(m, topic)}\n")
        return None

    answers = {
        lab: ask(provider, _mentor_prompt(m, topic))
        for lab, m in zip(labels, chosen, strict=True)
    }
    reviews = {}
    for lab, m in zip(labels, chosen, strict=True):
        others = {k: v for k, v in answers.items() if k != lab}
        reviews[m["name"]] = ask(provider, _review_prompt(m, topic, others))
    minutes = ask(provider, _chair_prompt(topic, answers, reviews, key))

    title = "Council: " + re.sub(r"[^\w\s-]", "", topic).strip()[:60]
    body = [
        f"Convened {dt.date.today().isoformat()} with "
        + ", ".join(f"[[{m['name']}]]" for m in chosen)
        + f" through {provider}.",
        "",
        minutes.strip(),
        "",
        "## The answers",
    ]
    for lab, m in zip(labels, chosen, strict=True):
        body += [f"### {m['name']} (answer {lab})", answers[lab].strip(), ""]
    body += ["Back to [[Tonight]] · [[Your path]]", "", "#council #decision"]
    path = ctx.vault.write(title, "\n".join(body), tags=["council", "decision"])
    ctx.vault.add_build_log(f"[[{safe_title(title)}]] convened on: {topic}")
    return path


def create_theme(provider: str, name: str, brief: str) -> Path:
    """Ask the provider for a themes/<name>.toml and validate it."""
    if not re.fullmatch(r"[a-z0-9-]{2,32}", name):
        raise ValueError("theme name: lowercase letters, digits and dashes only")
    example = THEMES["boardroom"].to_toml()
    prompt = (
        "Write a TOML file for a theme of an evening course on building software "
        "with AI coding agents. Keep exactly the keys of the example, change every "
        f"value to fit this brief: {brief or name}. The intro is one paragraph of at "
        "most 90 words addressed to the learner; pairings is a list of exactly eight "
        "short strings (drinks or snacks or nothing-themed items), pairing_kind is one "
        "of wine, coffee, tea, none; tone is one of jargon, plain, academic. No em "
        "dashes, no emoji. Output only the TOML, no fences.\n\nExample:\n" + example
    )
    text = ask(provider, prompt)
    text = re.sub(r"^```[a-z]*\n|```$", "", text.strip(), flags=re.M)
    data = tomllib.loads(text)
    data["id"] = name
    data["pairings"] = tuple(data.get("pairings", ()))
    theme = Theme(**data)
    THEMES_DIR.mkdir(exist_ok=True)
    path = THEMES_DIR / f"{name}.toml"
    path.write_text(theme.to_toml(), encoding="utf-8")
    load_theme(name)
    return path
