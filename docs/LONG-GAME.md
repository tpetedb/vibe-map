# The long game: terminal, game and vault, one machine, one loop

This is the setup for playing over weeks, not one evening. Three windows, one loop, every command spelled out. Nothing here assumes you know what a terminal is; if a line says "you should see", check it before the next line.

## 0. What the three windows do

| Window | What it is for | How you get there |
|---|---|---|
| Terminal | commands: install, check your work, pull news, build the vault | Ghostty (or Terminal.app): Cmd-Space, type Terminal, Enter |
| Game | the island: walk, inspect artifacts, open a stop, read the lesson | a browser tab on `game/vibe-map.html` (or the hosted URL) |
| Obsidian | the vault: everything you learned, linked, growing | the Obsidian app with `vault/` opened as a vault |

They share one thing: the progress code. The game writes it, the terminal reads it, the vault is built from it.

## 1. One-time setup (twenty minutes)

Open the terminal. Paste one line at a time.

```bash
xcode-select --install 2>/dev/null; true     # macOS command line tools; a dialog may appear, accept it
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install git uv just gh
brew install --cask obsidian ghostty
```

You should see `brew` finishing without red lines. Then the camp:

```bash
uv tool install vibe-map
vibe new ~/camp
cd ~/camp
just setup
```

You should see: a `.venv` created, Playwright browsers installed, skills linked, `vault built`. Then make the terminal yours (optional, recommended):

```bash
vibe dotfiles install zsh --brew
vibe dotfiles install tmux
vibe dotfiles install starship
exec zsh
```

You should see a prompt with the path in blue and a green dollar sign.

## 2. Tell it who you are (two minutes)

```bash
just start
```

A screen opens in the terminal. Pick your name, your field, a difficulty, your model provider (Claude Code with a Claude Max subscription, or Codex), the vault mode (**Grows as you play** if you want to watch the graph grow) and a theme. Continue, look at the toolbelt (green means installed), Continue again, then pick **Play the game**.

## 3. The loop (every session)

### In the game

1. Walk to a signpost, press **Enter**, read the lesson, do the thing it asks for on your machine.
2. Press **Mark as done** when the definition of done is met.
3. Walk into a yellow ring, press **Inspect**, press the buttons.
4. Open **Roadmap**, press **Export progress**. The code is now in your clipboard.

### In the terminal

```bash
cd ~/camp
vibe import <paste the code>
vibe check 1            # the CLI verifies stop 1 on your machine and awards the XP
vibe status             # the grid, your level, the pet
vibe vault build        # the vault catches up with the state
```

You should see `imported: N new stops`, green checks per stop, and `vault built`.

### In Obsidian

Press Cmd-R (reload) or just click **Tonight** in the sidebar. The Tonight note lists what you did, the Hot cache shows the last five entries, and in grow mode the graph has new nodes. Press Cmd-G for the graph.

That is the whole loop: game, terminal, vault. Four commands.

## 4. Once a week (five minutes)

```bash
cd ~/camp
vibe news && just build # pull the AI feeds into the vault note News and bake them into the game
vibe vault lint         # orphans and dead links, if you wrote notes by hand
vibe vault feature --all   # once: the thirty-five Obsidian feature notes, with a canvas, a base and a deck
git add -A && git commit -m "Week: what I learned" && git push
```

If you forked the template on GitHub, the `news` action does the first line for you every Monday, and Pages redeploys the hosted game with the fresh News card.

## 5. Keep the three windows side by side

With AeroSpace (`vibe dotfiles install aerospace`): alt-shift-a moves a window to workspace A. Put the browser and Obsidian on A, the terminal on T; alt-a and alt-t switch. Without it: three windows, Cmd-Tab.

`just camp` opens all three at once: the game in the browser, the vault in Obsidian, and the terminal with `vibe status`.

## 6. When you come back after a month

```bash
cd ~/camp
git pull --ff-only          # your own commits from another machine
uv tool upgrade vibe-map    # the CLI
vibe status                 # where you were
vibe news                   # what happened meanwhile
```

The game in the browser still has your progress (it lives in the browser's storage); the terminal has the same in `.vibe/state.json`; the vault has it as notes. If they disagree, the progress code wins: export from the game, import in the terminal, rebuild the vault.

## 7. If something breaks

| You see | Do |
|---|---|
| `vibe: command not found` | `uv tool install vibe-map`, then open a new terminal |
| `No camp in ...` | `cd ~/camp` (or `vibe new ~/camp` once) |
| the game shows the Roadmap list, no island | WebGL is off; Chrome on a Mac with Apple silicon is the reference; the lessons still work |
| Obsidian shows a note with dashed links | grow mode: those notes are still in `_library`; play on, or `vibe vault unlock "<title>"` |
| `claude -p` complains about a model | run `claude` once interactively to log in; the CLI retries with `--model sonnet` |
| the News card says no news yet | `vibe news`, then `just build` (the news is baked into the game); a forked repo's Monday action does both |

Nothing you do in the game or the terminal can delete the vault. `git log` shows every change; `just rescue` brings you back to main.
