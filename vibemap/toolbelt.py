"""The toolbelt: what a good machine has, how to check it, how to install it.

Every install command below was taken from the tool's own documentation on
2026-09-16 (URL in each entry). Nothing is installed unless the user chooses
it, or has chosen YOLO mode, which installs everything missing at once.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from vibemap.palette import plain

Tier = Literal["core", "evening", "toolbelt", "provider"]


@dataclass(frozen=True, slots=True)
class Tool:
    id: str
    label: str
    what: str
    binary: str
    install: str
    url: str
    tier: Tier
    size: str = "MB"
    app: str | None = None
    version_args: tuple[str, ...] = ("--version",)

    def is_installed(self) -> bool:
        if self.app and Path(self.app).exists():
            return True
        return shutil.which(self.binary) is not None

    def version(self) -> str | None:
        exe = shutil.which(self.binary)
        if exe is None:
            return "installed" if self.app and Path(self.app).exists() else None
        try:
            out = subprocess.run(
                [exe, *self.version_args], capture_output=True, text=True, timeout=15
            )
        except (OSError, subprocess.TimeoutExpired):
            return "installed"
        if out.returncode != 0:
            # Some apps ship a CLI without a version flag; the binary is proof.
            return "installed"
        line = plain((out.stdout or out.stderr).split("\n")[0])
        return line.strip()[:60] or "installed"


TOOLS: tuple[Tool, ...] = (
    Tool(
        "brew", "Homebrew", "the package manager every other install uses",
        "brew",
        '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
        "https://brew.sh", "core",
    ),
    Tool(
        "git", "Git", "the save-point system, workstream 4",
        "git", "xcode-select --install", "https://git-scm.com", "core",
    ),
    Tool(
        "gh", "GitHub CLI", "Pages, PRs and the repo from the terminal, workstream 7",
        "gh", "brew install gh", "https://cli.github.com", "core",
    ),
    Tool(
        "uv", "uv", "Python environments and this very CLI",
        "uv", "brew install uv", "https://docs.astral.sh/uv/", "core",
    ),
    Tool(
        "just", "just", "the task runner behind `just start`",
        "just", "brew install just", "https://just.systems", "core",
    ),
    Tool(
        "claude", "Claude Code", "the coding agent, every workstream",
        "claude", "curl -fsSL https://claude.ai/install.sh | bash",
        "https://code.claude.com/docs/en/quickstart", "core",
    ),
    Tool(
        "duckdb", "DuckDB", "SQL over CSV files, workstream 3",
        "duckdb", "brew install duckdb", "https://duckdb.org/docs/", "evening",
    ),
    Tool(
        "jq", "jq", "JSON in the shell; the hook lesson uses it",
        "jq", "brew install jq", "https://jqlang.org", "evening",
    ),
    Tool(
        "obsidian", "Obsidian", "the vault, workstream 6",
        "obsidian", "brew install --cask obsidian", "https://obsidian.md", "evening",
        size="GB", app="/Applications/Obsidian.app", version_args=("version",),
    ),
    Tool(
        "playwright", "Playwright browsers", "Chromium and WebKit for `just test`",
        "playwright", "uv run playwright install chromium webkit",
        "https://playwright.dev/python/", "evening", size="GB",
    ),
    Tool(
        "node", "Node.js", "npm installs for the other provider CLIs",
        "node", "brew install node", "https://nodejs.org", "toolbelt",
    ),
    Tool(
        "bun", "Bun", "a fast JavaScript runtime and package manager",
        "bun", "brew install oven-sh/bun/bun", "https://bun.com/docs/installation",
        "toolbelt",
    ),
    Tool(
        "zed", "Zed", "the editor with Claude Code built in over ACP",
        "zed", "brew install --cask zed", "https://zed.dev", "toolbelt", size="GB",
        app="/Applications/Zed.app",
    ),
    Tool(
        "code", "VS Code", "the other editor, with the Claude Code extension",
        "code", "brew install --cask visual-studio-code", "https://code.visualstudio.com",
        "toolbelt", size="GB", app="/Applications/Visual Studio Code.app",
    ),
    Tool(
        "ghostty", "Ghostty", "a fast terminal with real themes",
        "ghostty", "brew install --cask ghostty", "https://ghostty.org", "toolbelt",
        app="/Applications/Ghostty.app",
    ),
    Tool(
        "tmux", "tmux", "panes and sessions that survive a closed window",
        "tmux", "brew install tmux", "https://github.com/tmux/tmux/wiki", "toolbelt",
        version_args=("-V",),
    ),
    Tool(
        "starship", "Starship", "a prompt that shows git, venv and path",
        "starship", "brew install starship", "https://starship.rs", "toolbelt",
    ),
    Tool(
        "aerospace", "AeroSpace", "a tiling window manager for macOS",
        "aerospace", "brew install --cask nikitabobko/tap/aerospace",
        "https://github.com/nikitabobko/AeroSpace", "toolbelt",
        app="/Applications/AeroSpace.app",
    ),
    Tool(
        "btop", "btop", "a resource monitor that looks like a cockpit",
        "btop", "brew install btop", "https://github.com/aristocratos/btop", "toolbelt",
    ),
    Tool(
        "fzf", "fzf", "fuzzy find anything: files, history, branches",
        "fzf", "brew install fzf", "https://github.com/junegunn/fzf", "toolbelt",
    ),
    Tool(
        "rg", "ripgrep", "grep, but fast and sensible",
        "rg", "brew install ripgrep", "https://github.com/BurntSushi/ripgrep", "toolbelt",
    ),
    Tool(
        "bat", "bat", "cat with syntax highlighting",
        "bat", "brew install bat", "https://github.com/sharkdp/bat", "toolbelt",
    ),
    Tool(
        "eza", "eza", "ls with icons, git status and a tree view",
        "eza", "brew install eza", "https://github.com/eza-community/eza", "toolbelt",
    ),
    Tool(
        "orbstack", "OrbStack", "Docker and Linux machines, light on the Mac",
        "orb", "brew install --cask orbstack", "https://orbstack.dev", "toolbelt",
        size="GB", app="/Applications/OrbStack.app",
    ),
    Tool(
        "codex", "OpenAI Codex CLI", "another coding agent; `codex exec` for scripts",
        "codex", "brew install --cask codex", "https://github.com/openai/codex", "provider",
    ),
    Tool(
        "gemini", "Gemini CLI", "Google's coding agent; `gemini -p` for scripts",
        "gemini", "brew install gemini-cli", "https://github.com/google-gemini/gemini-cli",
        "provider",
    ),
    Tool(
        "copilot", "GitHub Copilot CLI", "GitHub's agent; `copilot -p` for scripts",
        "copilot", "brew install --cask copilot-cli",
        "https://docs.github.com/en/copilot/how-tos/set-up/install-copilot-cli", "provider",
    ),
    Tool(
        "opencode", "OpenCode", "an open-source agent; `opencode run` for scripts",
        "opencode", "brew install anomalyco/tap/opencode", "https://opencode.ai/docs/",
        "provider",
    ),
)  # fmt: skip

TOOLS_BY_ID = {t.id: t for t in TOOLS}


def get_tool(tool_id: str) -> Tool:
    try:
        return TOOLS_BY_ID[tool_id]
    except KeyError:
        raise ValueError(
            f"unknown tool {tool_id!r}; one of: {', '.join(TOOLS_BY_ID)}"
        ) from None


def missing(tier: Tier | None = None) -> list[Tool]:
    return [
        t for t in TOOLS if (tier is None or t.tier == tier) and not t.is_installed()
    ]


def install(tool: Tool, *, dry_run: bool = False) -> int:
    """Run the documented install command; return its exit code."""
    print(f"$ {tool.install}")
    if dry_run:
        return 0
    return subprocess.run(tool.install, shell=True).returncode
