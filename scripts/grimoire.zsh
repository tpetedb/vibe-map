# Vibe Code Camp shell helpers for zsh.
#
# zsh in practice: a file you `source` from ~/.zshrc adds aliases and
# functions to every new terminal. Add this line to ~/.zshrc, then open a
# new tab:
#
#   source /path/to/vibe-map/scripts/grimoire.zsh
#
# Everything here is a shortcut for a command that also works spelled out.

# The repo this file lives in, so the aliases work from any folder.
export GRIMOIRE_HOME="${0:A:h:h}"

alias g='uv run --project "$GRIMOIRE_HOME" --no-sync grimoire'
alias gs='g status'
alias gc='g check'
alias gv='g vault lint'
alias gx='g explain'

# Jump to the repo and show where you are in the campaign.
camp() {
  cd "$GRIMOIRE_HOME" || return 1
  just status
}

# Open the game, the vault and a Claude session in one go.
evening() {
  cd "$GRIMOIRE_HOME" || return 1
  just game
  open -a Obsidian "$GRIMOIRE_HOME/vault" 2>/dev/null
  claude
}

# A prompt segment for Starship or p10k: the XP and level in one word.
grimoire_prompt_segment() {
  local json
  json=$(uv run --project "$GRIMOIRE_HOME" --no-sync grimoire status --json 2>/dev/null) || return 0
  print -r -- "$(print -r -- "$json" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(f"{d[\"level\"]} {d[\"xp\"]}xp")')"
}
