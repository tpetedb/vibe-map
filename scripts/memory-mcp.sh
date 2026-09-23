#!/bin/sh
# The shared memory for every session of both teams: the official MCP memory
# server, pinned, behind tools/board.py, which serializes writes across processes
# and refuses the whole-graph read. The graph lives next to the board room in
# the git common dir, so every worktree shares it and it is never committed.
# Claude starts this from .mcp.json, Codex from .codex/config.toml.
set -eu
PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
export PATH
root="$(cd "$(dirname "$0")/.." && pwd)"
common="$(git -C "$root" rev-parse --path-format=absolute --git-common-dir)" || {
  echo "memory-mcp: $root is not inside a git checkout" >&2
  exit 1
}
export VIBE_MEMORY_FILE="${VIBE_MEMORY_FILE:-$common/board/memory.jsonl}"
exec python3 "$root/tools/board.py" memory-serve -- \
  npx -y @modelcontextprotocol/server-memory@2026.8.31
