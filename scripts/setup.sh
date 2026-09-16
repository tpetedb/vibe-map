#!/usr/bin/env bash
# Project Grimoire setup for macOS. Read before running. Each step is optional and idempotent.
set -euo pipefail
cd "$(dirname "$0")/.."

have(){ command -v "$1" >/dev/null 2>&1; }

echo "== Homebrew"
have brew || { echo "Install Homebrew first: https://brew.sh"; exit 1; }

echo "== GitHub CLI, uv (Python), DuckDB"
for f in gh uv duckdb; do have "$f" || brew install "$f"; done

echo "== Obsidian (app)"
[ -d "/Applications/Obsidian.app" ] || brew install --cask obsidian || true

echo "== Claude Code"
if ! have claude; then
  echo "Install Claude Code following https://code.claude.com/docs/en/quickstart then re-run this script."
fi

echo "== Link Agent Skills into .claude/skills (Claude Code reads only that folder)"
mkdir -p .claude/skills
for d in .agents/skills/*/; do
  n=$(basename "$d")
  [ -e ".claude/skills/$n" ] || ln -s "../../.agents/skills/$n" ".claude/skills/$n"
done

echo "== Optional: community skills (uncomment what you want)"
# npx skills add wshobson/agents --skill <name>     # https://github.com/wshobson/agents
# gh skill install wshobson/agents <name>            # GitHub CLI 2.90+

echo "== Python env"
[ -d .venv ] || uv venv >/dev/null
uv pip install --quiet duckdb 2>/dev/null || true

echo "== Vault"
python3 grimoire/cli.py init

echo "== Git"
[ -d .git ] || { git init -q && git add -A && git commit -qm "Grimoire: initial commit from template"; }

echo
echo "Done. Next: 'claude' in this folder, open vault/ in Obsidian, then 'python3 grimoire/cli.py status'."
