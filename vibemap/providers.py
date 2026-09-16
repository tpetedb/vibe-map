"""Model providers: the coding agent CLIs, driven in print mode.

The course is Claude Code first, but `explain`, `council` and `theme create`
work with whichever CLI the learner has. Every invocation form here comes from
the vendor's documentation (URL per entry, checked 2026-09-16).
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from collections.abc import Callable
from dataclasses import dataclass


class ProviderMissing(RuntimeError):
    """The chosen provider CLI is not on PATH."""


@dataclass(frozen=True, slots=True)
class Provider:
    id: str
    label: str
    binary: str
    argv: Callable[[str], list[str]]
    docs: str
    install: str

    def available(self) -> bool:
        return shutil.which(self.binary) is not None


PROVIDERS: dict[str, Provider] = {
    "claude": Provider(
        "claude", "Claude Code", "claude",
        lambda p: ["claude", "-p", p],
        "https://code.claude.com/docs/en/quickstart",
        "curl -fsSL https://claude.ai/install.sh | bash",
    ),
    "codex": Provider(
        "codex", "OpenAI Codex CLI", "codex",
        lambda p: ["codex", "exec", p],
        "https://learn.chatgpt.com/docs/non-interactive-mode",
        "brew install --cask codex",
    ),
    "gemini": Provider(
        "gemini", "Gemini CLI", "gemini",
        lambda p: ["gemini", "-p", p],
        "https://github.com/google-gemini/gemini-cli",
        "brew install gemini-cli",
    ),
    "copilot": Provider(
        "copilot", "GitHub Copilot CLI", "copilot",
        lambda p: ["copilot", "-p", p],
        "https://docs.github.com/en/copilot/how-tos/use-copilot-agents/use-copilot-cli",
        "brew install --cask copilot-cli",
    ),
    "opencode": Provider(
        "opencode", "OpenCode", "opencode",
        lambda p: ["opencode", "run", p],
        "https://opencode.ai/docs/cli/",
        "brew install anomalyco/tap/opencode",
    ),
}  # fmt: skip


def get_provider(provider_id: str) -> Provider:
    try:
        return PROVIDERS[provider_id]
    except KeyError:
        raise ValueError(
            f"unknown provider {provider_id!r}; one of: {', '.join(PROVIDERS)}"
        ) from None


def ask(provider_id: str, prompt: str, *, timeout: int = 600) -> str:
    """Run the provider once in print mode and return its answer.

    Raises:
        ProviderMissing: when the CLI is not installed.
        RuntimeError: when the CLI exits non-zero.
    """
    provider = get_provider(provider_id)
    if not provider.available():
        raise ProviderMissing(
            f"{provider.label} is not installed. Install: {provider.install} "
            f"(docs: {provider.docs})"
        )
    argv = provider.argv(prompt)
    result = subprocess.run(
        argv, capture_output=True, text=True, timeout=timeout, env=_clean_env()
    )
    if result.returncode != 0 and provider.id == "claude":
        # A pinned model this Claude Code build does not know (a preview
        # alias in ~/.claude/settings.json): retry on the documented alias.
        if "model catalog" in result.stderr:
            result = subprocess.run(
                [*argv, "--model", "sonnet"],
                capture_output=True,
                text=True,
                timeout=timeout,
                env=_clean_env(),
            )
    if result.returncode != 0:
        raise RuntimeError(
            f"{provider.label} exited {result.returncode}: "
            f"{_strip_ansi(result.stderr).strip()[:500]}"
        )
    return result.stdout.strip()


def _clean_env() -> dict[str, str]:
    """The environment minus the variables a parent Claude Code session exports."""
    return {
        k: v
        for k, v in os.environ.items()
        if not (k.startswith("CLAUDE_CODE_") or k in {"CLAUDECODE", "CLAUDE_PID"})
    }


def _strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)
