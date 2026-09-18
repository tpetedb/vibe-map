#!/usr/bin/env bash
# Your camp in a container: the same four tools the course asks for on a Mac,
# from their own official installers because there is no Homebrew here.
#
# It runs as onCreateCommand, the half a Codespaces prebuild replays, so a
# prebuild you switch on for your own camp would already have everything. None
# is configured: a prebuild bills the repository's owner for Actions minutes.
# A camp has no test battery, so there are no browsers to download.
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
if [ -x "$HOME/.duckdb/cli/latest/duckdb" ]; then
  ln -sf "$HOME/.duckdb/cli/latest/duckdb" "$BIN/duckdb"
fi

# The engine is not in this folder; the command is installed, as on a Mac.
# Add @vX.Y.Z to pin a release instead of following main.
uv tool install --force git+https://github.com/tpetedb/vibe-map
just setup

echo "ready: just start"
