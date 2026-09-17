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
uv tool install git+https://github.com/tpetedb/vibe-map
vibe new                     # makes ~/vibe-map-<you>-<today>: workspace, vault, config; no engine
cd vibe-map-*
just setup                   # links the skills for Claude Code; the vault was built by vibe new
```

The repository is the install source until the package is published; once it is on PyPI, `uv tool install vibe-map` is the short form of the same thing. `just` is not on a Mac by default: `brew install just` puts it there, and every recipe in a camp also runs as `vibe <thing>`, so `just check 1` and `vibe check 1` are the same command.

The convention is your name, vibe-map, the date you started: `vibe-map-tom-2026-09-17`. It sorts by date, and a progress code or a note always says which camp it came from. The game's own setup guide (title screen, The full experience, or Roadmap, Setup guide) prints these commands with your name filled in.

You should see `ready: just start`, with the skills linked and the vault already built by `vibe new`. A camp has no Python environment of its own and no test browsers: the engine lives inside the installed `vibe` command. (`just setup` in the product repository is a different recipe with the same name; that one makes a `.venv` and installs Playwright.) Then make the terminal yours (optional, recommended):

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
3. Walk into a yellow ring, press **Inspect**, press the buttons, then read the **Do it for real** section on the sheet and build the thing in `workspace/artifacts/<id>/`.
4. Walk up to a mentor, press **Enter**, walk the dialogue one question at a time, and do the exercise they set in `workspace/mentors/<id>/`. It takes under fifteen minutes.
5. Open **Roadmap**, press **Export progress**. The code is now in your clipboard.

### In the terminal

```bash
cd ~/vibe-map-*
vibe import <paste the code>
vibe check 1            # the CLI verifies stop 1 on your machine and awards the XP
vibe check --artifact cafe   # what the artifact asked you to build, or --artifact all
vibe check --mentor cherny   # the exercise the mentor set, or --mentor all
vibe status             # the grid, your level, the pet
vibe vault build        # the vault catches up with the state
```

You should see `imported: N new stops`, green checks per stop, and `vault built`. A verified mentor encounter raises a plaque on their spot the next time you open the game; an artifact you built for real reads "built for real" on its sheet.

### In Obsidian

Press Cmd-R (reload) or just click **Tonight** in the sidebar. The Tonight note lists what you did, the Hot cache shows the last five entries, and in grow mode the graph has new nodes. Press Cmd-G for the graph.

That is the whole loop: game, terminal, vault. Four commands.

## 4. Your own copy of the game (production island, stop 6)

```bash
cd ~/vibe-map-*
vibe fork                       # workspace/forks/vibe-map/, with its own src/config/
cd workspace/forks/vibe-map
just build                      # your own game/vibe-map.html
open game/vibe-map.html
cd ~/vibe-map-*
vibe check --fork               # or one challenge: exists, config, topic, repair
```

Your camp's `config/camp.toml` is your journey: who you are, how hard, which theme. The fork's `src/config/00-config.js` is the game itself: world scale, island radius, palette. Change the first and your game changes; change the second and the game changes. Break the fork on purpose, run `just record`, repair it, run `just record` again: that is the repair challenge, and nothing you do in there touches the course you are playing.

## 5. Once a week (five minutes)

```bash
cd ~/vibe-map-*
vibe news               # pull the AI feeds into the vault note News and the Roadmap card
vibe vault lint         # orphans and dead links, if you wrote notes by hand
vibe vault feature --all   # once: the thirty-five Obsidian feature notes, with a canvas, a base and a deck
git add -A && git commit -m "Week: what I learned" && git push
```

In a camp the feed lands in `.vibe/news.json` and the vault note News, and `vibe play` opens the hosted game, which carries its own news. Baking the news into a game file (`just build`) only exists in the product repository. If you forked the product on GitHub, its `news` action does the first line for you every Monday, and Pages redeploys the hosted game with the fresh News card.

## 6. Keep the three windows side by side

With AeroSpace (`vibe dotfiles install aerospace`): alt-shift-a moves a window to workspace A. Put the browser and Obsidian on A, the terminal on T; alt-a and alt-t switch. Without it: three windows, Cmd-Tab.

`just camp` opens all three at once: the game in the browser, the vault in Obsidian, and the terminal with `vibe status`.

## 7. When you come back after a month

```bash
cd ~/vibe-map-*
git pull --ff-only          # your own commits from another machine
uv tool upgrade vibe-map    # the CLI
vibe status                 # where you were
vibe news                   # what happened meanwhile
```

The game in the browser still has your progress (it lives in the browser's storage); the terminal has the same in `.vibe/state.json`; the vault has it as notes. If they disagree, the progress code wins: export from the game, import in the terminal, rebuild the vault.

## 8. If something breaks

| You see | Do |
|---|---|
| `vibe: command not found` | `uv tool install git+https://github.com/tpetedb/vibe-map`, then open a new terminal |
| `No camp in ...` | `cd ~/vibe-map-*` (or `vibe new` once) |
| the game shows the Roadmap list, no island | WebGL is off; Chrome on a Mac with Apple silicon is the reference; the lessons still work |
| Obsidian shows a note with dashed links | grow mode: those notes are still in `_library`; play on, or `vibe vault unlock "<title>"` |
| `claude -p` complains about a model | run `claude` once interactively to log in; the CLI retries with `--model sonnet` |
| you want to start the game over | Roadmap, Reset progress, click it twice; or open the hosted game with `?reset` at the end of the URL. Stops, artifacts and mentor choices go; your name and settings stay. The terminal's state is separate: `rm .vibe/state.json` starts that over too |
| `just: command not found` | `brew install just`; or skip it, every recipe also runs as `vibe <thing>` |
| `just verify` or `just build` is not a recipe here | they belong to the product repository; a camp checks with `vibe check`, `vibe vault lint` and your own tests in `workspace/` |
| the News card says no news yet | `vibe news`, then reopen the game with `vibe play`; a forked product repo's Monday action refreshes the hosted game |

Nothing you do in the game or the terminal can delete the vault. `git log` shows every change; `just rescue` brings you back to main.
