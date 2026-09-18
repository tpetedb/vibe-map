"""The hands-on behind `vibe check --topic <id>`.

A topic may carry a `hands_on` block: a folder in the workspace, a definition
of done, and one check spec. The spec names a kind from
vibemap/artifact_checks.py, so a topic and an artifact are verified by exactly
the same code and a new kind serves both.
"""

from __future__ import annotations

from pathlib import Path

from vibemap import project, topics
from vibemap.artifact_checks import run_spec
from vibemap.config import Config
from vibemap.quests import Check, Quest, required_levels
from vibemap.topics import Topic

ROOT = project.root()


def hands_on_dir(topic: Topic) -> Path:
    """Where the exercise for this topic lives, as an absolute path."""
    if topic.hands_on is None:
        raise ValueError(f"topic {topic.id} has no hands-on")
    return ROOT / topic.hands_on.folder(topic.id)


def _hands_on_check(topic: Topic) -> Check:
    hands_on = topic.hands_on
    assert hands_on is not None
    here = hands_on_dir(topic)
    folder = hands_on.folder(topic.id)

    def fn(_: Config) -> tuple[bool, str]:
        if not here.is_dir():
            return False, f"{folder}/ does not exist yet"
        return run_spec(here, hands_on.check)

    return Check(hands_on.title, fn, f"{folder}/: {hands_on.done}")


def topic_quest(topic_id: str, cfg: Config) -> Quest:
    """The quest for one topic: the smallest real thing it asks you to build."""
    topic = topics.get(topic_id)
    if topic.hands_on is None:
        raise ValueError(
            f"topic {topic.id!r} has no hands-on yet, so there is nothing to check"
        )
    checks = (_hands_on_check(topic),)
    wanted = required_levels(cfg.learner.difficulty)
    return Quest(
        "topic", 0, f"{topic.title}: {topic.hands_on.title}",
        tuple(c for c in checks if c.level in wanted),
    )  # fmt: skip
