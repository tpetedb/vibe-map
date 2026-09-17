# vibe.zsh: the shell half of Vibe Code Camp's terminal setup.
# Adapted from Tom's Toolbox (github.com/tpetedb/toms-toolbox, MIT): the
# palette-coloured syntax highlighting, history suggestions, the live
# completion dropdown, fzf in the house colours, sane history and a few
# aliases. Sourced from ~/.zshrc by `vibe dotfiles install zsh`; remove that
# one line to switch it off. Nothing here needs oh-my-zsh.
#
# Plugins come from Homebrew (brew install zsh-autosuggestions
# zsh-syntax-highlighting zsh-autocomplete fzf); each block below is a no-op
# when its plugin is missing, so the file is safe to source on a bare Mac.

# -- Palette (the five hues, base variants; docs/DESIGN.md) ------------------
export VIBE_RED="#D32F2F" VIBE_ORANGE="#FF8C1A" VIBE_YELLOW="#FFBF00"
export VIBE_GREEN="#00A86B" VIBE_BLUE="#0067A5"

# -- History: big, shared, deduplicated ---------------------------------------
HISTSIZE=50000
SAVEHIST=50000
HISTFILE="$HOME/.zsh_history"
setopt HIST_IGNORE_ALL_DUPS HIST_FIND_NO_DUPS HIST_REDUCE_BLANKS
setopt SHARE_HISTORY APPEND_HISTORY INC_APPEND_HISTORY
setopt AUTO_CD CORRECT NO_BEEP

# -- Completion menu (zsh's own) ---------------------------------------------
autoload -Uz compinit && compinit -u
zstyle ':completion:*' menu select
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}'

# -- fzf: fuzzy history (ctrl-r), files (ctrl-t), directories (alt-c) --------
if command -v fzf >/dev/null 2>&1; then
    export FZF_DEFAULT_OPTS="--height 40% --layout=reverse --border --color=fg:#cccccc,bg:#000000,hl:${VIBE_YELLOW},fg+:#ffffff,bg+:#1a1a1a,hl+:${VIBE_GREEN},info:${VIBE_BLUE},prompt:${VIBE_GREEN},pointer:${VIBE_ORANGE},marker:${VIBE_ORANGE},spinner:${VIBE_YELLOW},header:${VIBE_BLUE}"
    export FZF_CTRL_T_OPTS="--preview 'head -80 {}'"
    # fzf 0.48+ ships its own zsh integration; older builds have the files.
    if fzf --zsh >/dev/null 2>&1; then
        source <(fzf --zsh)
    elif [[ -r "$(brew --prefix 2>/dev/null)/opt/fzf/shell/key-bindings.zsh" ]]; then
        source "$(brew --prefix)/opt/fzf/shell/key-bindings.zsh"
        source "$(brew --prefix)/opt/fzf/shell/completion.zsh"
    fi
fi

# -- The three plugins, if Homebrew installed them ---------------------------
_vibe_brew="$(brew --prefix 2>/dev/null)"
if [[ -n "$_vibe_brew" ]]; then
    # Live dropdown of files, dirs and flags while typing.
    [[ -r "$_vibe_brew/share/zsh-autocomplete/zsh-autocomplete.plugin.zsh" ]] && \
        source "$_vibe_brew/share/zsh-autocomplete/zsh-autocomplete.plugin.zsh"
    zstyle ':autocomplete:*' delay 0.1        # debounce per-keystroke forks
    zstyle ':autocomplete:*' min-input 2      # start after two characters
    # Fish-like grey suggestion from history; right arrow accepts.
    [[ -r "$_vibe_brew/share/zsh-autosuggestions/zsh-autosuggestions.zsh" ]] && \
        source "$_vibe_brew/share/zsh-autosuggestions/zsh-autosuggestions.zsh"
    ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE='fg=244'
    ZSH_AUTOSUGGEST_STRATEGY=(history)
    # Real-time command colouring; must be sourced last.
    [[ -r "$_vibe_brew/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" ]] && \
        source "$_vibe_brew/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"
fi
unset _vibe_brew

# Syntax colours follow the palette: green is a command that exists, red-bright
# one that does not, blue for options and keywords, yellow for strings.
typeset -gA ZSH_HIGHLIGHT_STYLES
ZSH_HIGHLIGHT_STYLES[command]="fg=${VIBE_GREEN}"
ZSH_HIGHLIGHT_STYLES[builtin]="fg=${VIBE_GREEN}"
ZSH_HIGHLIGHT_STYLES[alias]="fg=${VIBE_GREEN}"
ZSH_HIGHLIGHT_STYLES[function]="fg=${VIBE_GREEN}"
ZSH_HIGHLIGHT_STYLES[unknown-token]="fg=#F04923"
ZSH_HIGHLIGHT_STYLES[reserved-word]="fg=${VIBE_BLUE},bold"
ZSH_HIGHLIGHT_STYLES[single-hyphen-option]="fg=${VIBE_BLUE}"
ZSH_HIGHLIGHT_STYLES[double-hyphen-option]="fg=${VIBE_BLUE}"
ZSH_HIGHLIGHT_STYLES[single-quoted-argument]="fg=${VIBE_YELLOW}"
ZSH_HIGHLIGHT_STYLES[double-quoted-argument]="fg=${VIBE_YELLOW}"
ZSH_HIGHLIGHT_STYLES[globbing]="fg=${VIBE_YELLOW},bold"
ZSH_HIGHLIGHT_STYLES[path]="fg=white,underline"

# -- Aliases worth the muscle memory -----------------------------------------
alias ..="cd .."
alias ...="cd ../.."
alias ll="ls -lah"
alias la="ls -A"
alias gs="git status"
alias gd="git diff"
alias gl="git log --oneline --graph --decorate -20"
alias py="python3"
alias dc="docker compose"

# -- tj: pick or create a tmux session with fzf -------------------------------
tj() {
    command -v tmux >/dev/null 2>&1 || { echo "tj: tmux is not installed"; return 1; }
    if ! tmux list-sessions >/dev/null 2>&1; then
        tmux new-session -s main
        return
    fi
    local picked
    picked="$(tmux list-sessions -F '#{session_name}' | fzf --prompt='tmux session > ' --print-query | tail -1)"
    [[ -n "$picked" ]] || return 0
    tmux has-session -t "=$picked" 2>/dev/null || tmux new-session -d -s "$picked"
    if [[ -n "$TMUX" ]]; then tmux switch-client -t "=$picked"; else tmux attach-session -t "=$picked"; fi
}

# -- Prompt: starship when present (the palette lives in ~/.config/starship.toml)
if command -v starship >/dev/null 2>&1 && [[ -z "$VIBE_NO_STARSHIP" ]]; then
    eval "$(starship init zsh)"
fi
