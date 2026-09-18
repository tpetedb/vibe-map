#!/usr/bin/env bash
# What a product checkout needs inside a Codespace or any dev container.
# scripts/setup.sh is the macOS equivalent and installs through Homebrew; the
# container has no Homebrew, so each tool comes from its own official installer.
#
# This runs as onCreateCommand, not postCreateCommand, because that is the half
# a Codespaces prebuild replays, so everything slow (the Python environment, the
# browsers) would land in one. No prebuild is configured: a prebuild bills the
# repository's owner for Actions minutes and storage.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

BIN="$HOME/.local/bin"
mkdir -p "$BIN"
export PATH="$BIN:$PATH"

have() { command -v "$1" >/dev/null 2>&1; }

have uv || curl -LsSf https://astral.sh/uv/install.sh | \
  env UV_INSTALL_DIR="$BIN" UV_NO_MODIFY_PATH=1 sh
have just || curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | \
  bash -s -- --to "$BIN"
have duckdb || curl -fsSL https://install.duckdb.org | bash
# The duckdb installer puts the binary in ~/.duckdb/cli/latest; link it where
# the rest of the toolbelt lives so a plain `duckdb` works.
if [ -x "$HOME/.duckdb/cli/latest/duckdb" ]; then
  ln -sf "$HOME/.duckdb/cli/latest/duckdb" "$BIN/duckdb"
fi

uv sync --frozen
# Only the product runs the test battery, so only the product needs the
# browsers. --with-deps wants root for apt; the browsers themselves belong to
# the user that runs the tests, so the two halves are separate commands.
sudo env "PATH=$PATH" uv run --no-sync playwright install-deps chromium webkit
uv run --no-sync playwright install chromium webkit

mkdir -p .claude/skills
for d in .agents/skills/*/; do
  n=$(basename "$d")
  [ -e ".claude/skills/$n" ] || ln -s "../../.agents/skills/$n" ".claude/skills/$n"
done

uv run --no-sync vibe init >/dev/null

echo "ready: just start, just verify, or python3 -m http.server 8000 to serve the game"
