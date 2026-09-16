#!/usr/bin/env bash
# Vibe Code Camp setup for macOS. Idempotent: run it again any time.
#
#   scripts/setup.sh            install the core, link skills, build the vault
#   scripts/setup.sh --check    report only, install nothing
#   scripts/setup.sh --yolo     also install every toolbelt and provider tool
#   scripts/setup.sh --help
#
# Bash 3.2 compatible (the one macOS ships). Colours follow the house palette.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

RED=$'\033[38;2;211;47;47m'; GREEN=$'\033[38;2;0;168;107m'
BLUE=$'\033[38;2;0;103;165m'; YELLOW=$'\033[38;2;255;191;0m'; RESET=$'\033[0m'
info() { printf '%s..%s %s\n' "$BLUE" "$RESET" "$*"; }
ok()   { printf '%sok%s %s\n' "$GREEN" "$RESET" "$*"; }
warn() { printf '%s!!%s %s\n' "$YELLOW" "$RESET" "$*"; }
fail() { printf '%sxx%s %s\n' "$RED" "$RESET" "$*" >&2; }
die()  { fail "$*"; exit 1; }
step() { printf '\n%s== %s%s\n' "$YELLOW" "$*" "$RESET"; }

CHECK=0; YOLO=0
for arg in "$@"; do
  case "$arg" in
    --check) CHECK=1 ;;
    --yolo) YOLO=1 ;;
    --help|-h) sed -n '2,9p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) die "unknown flag: $arg (try --help)" ;;
  esac
done

have() { command -v "$1" >/dev/null 2>&1; }

need_or_install() {
  # usage: need_or_install <binary> <label> <install command...>
  local bin="$1" label="$2"; shift 2
  if have "$bin"; then ok "$label ($(command -v "$bin"))"; return 0; fi
  if [ "$CHECK" = 1 ]; then warn "$label missing; would run: $*"; return 0; fi
  info "installing $label: $*"
  "$@" || die "$label did not install"
  have "$bin" || die "$label still missing after install; open a new terminal and re-run"
  ok "$label"
}

main() {
  step "Core tools"
  if ! have brew; then
    if [ "$CHECK" = 1 ]; then warn "Homebrew missing: https://brew.sh"; else
      die "Install Homebrew first: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    fi
  else ok "Homebrew"; fi
  need_or_install git "Git" xcode-select --install
  need_or_install gh "GitHub CLI" brew install gh
  need_or_install uv "uv" brew install uv
  need_or_install just "just" brew install just
  need_or_install duckdb "DuckDB" brew install duckdb
  need_or_install jq "jq" brew install jq
  if have claude; then ok "Claude Code ($(claude --version 2>/dev/null | head -1))"; else
    if [ "$CHECK" = 1 ]; then warn "Claude Code missing: curl -fsSL https://claude.ai/install.sh | bash"; else
      info "installing Claude Code"; curl -fsSL https://claude.ai/install.sh | bash
    fi
  fi
  if [ -d /Applications/Obsidian.app ]; then ok "Obsidian"; else
    if [ "$CHECK" = 1 ]; then warn "Obsidian missing: brew install --cask obsidian"; else
      brew install --cask obsidian || warn "Obsidian did not install; download it from https://obsidian.md"
    fi
  fi

  step "Python environment"
  if [ "$CHECK" = 1 ]; then
    if [ -d .venv ]; then ok ".venv exists"; else warn "no .venv yet; uv sync would create it"; fi
  else
    uv sync --frozen >/dev/null && ok "uv sync (see pyproject.toml)"
    if uv run --no-sync playwright install chromium webkit >/dev/null 2>&1; then
      ok "Playwright browsers"
    else
      warn "Playwright browsers did not install; just test needs them"
    fi
  fi

  step "Skills for Claude Code"
  mkdir -p .claude/skills
  for d in .agents/skills/*/; do
    n=$(basename "$d")
    [ -e ".claude/skills/$n" ] || { [ "$CHECK" = 1 ] || ln -s "../../.agents/skills/$n" ".claude/skills/$n"; }
  done
  ok "$(find .agents/skills -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ') skills linked into .claude/skills"

  step "Vault and state"
  if [ "$CHECK" = 1 ]; then
    if [ -f .grimoire/state.json ]; then ok "state.json exists"; else warn "no state yet; grimoire init would create it"; fi
  else
    uv run --no-sync grimoire init >/dev/null && ok "vault built (uv run grimoire vault lint to check it)"
  fi

  if [ "$YOLO" = 1 ] && [ "$CHECK" = 0 ]; then
    step "YOLO: everything missing from the toolbelt"
    uv run --no-sync grimoire toolbelt --install missing
  fi

  step "Done"
  if [ "$CHECK" = 1 ]; then info "check only; nothing was installed"; fi
  printf 'Next: %sjust start%s (the onboarding screen), or %sclaude%s in this folder.\n' "$GREEN" "$RESET" "$GREEN" "$RESET"
}

main "$@"
