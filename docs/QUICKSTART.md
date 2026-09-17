# Quickstart

Three ways in, from nothing installed to a full camp. Every step is a command you can paste; every block says what you should see afterwards. Numbers are steps, not minutes.

## Path A: play now, install nothing

1. Get the file.

   ```bash
   curl -fsSL https://raw.githubusercontent.com/tpetedb/vibe-map/main/game/vibe-map.html -o vibe-map.html
   ```

2. Open it.

   ```bash
   open vibe-map.html        # macOS; double-click works too
   ```

   You should see the island turning behind the title panel. One file, three.js embedded, no CDN, works on a phone and offline.

3. Type a name, press **Start**, walk to the 18:00 signpost. The first workstream opens with a full lesson, a definition of done and one question from Rolinda.

Progress lives in the browser. When you later install the CLI, **Roadmap, Export progress** gives a code you paste into `vibe import`.

## Path B: the CLI, installed once

Needs [uv](https://docs.astral.sh/uv/) and git. Homebrew has both: `brew install uv git`.

1. Install the command.

   ```bash
   uv tool install git+https://github.com/tpetedb/vibe-map
   vibe --version
   ```

   Prints the version, for example `vibe, version 0.3.0`. The repository is the install source until the package is published; once it is on PyPI, `uv tool install vibe-map` is the short form of the same thing.

2. Start a camp.

   ```bash
   vibe new                     # a slim camp (workspace, vault, config; no engine) in vibe-map-<you>-<today>
   cd vibe-map-*
   vibe name "Your Name"
   vibe status
   ```

   The folder name is the convention: your name, vibe-map, the date you started (`vibe new ~/vibe-map-tom-2026-09-17` spells it out; `--name tom` changes the person part). One camp per person and start date sorts by date in a listing and tells you which camp a note or a progress code came from. `vibe status` prints your name, level, XP and the four-by-eight grid of workstreams. Add `--github you/camp` to `vibe new` to push the camp to a new GitHub repository as well (needs `gh auth login`). The camp has three zones: `workspace/` (yours), `vault/` (the notes) and the configuration files; the engine stays inside the `vibe` command and the hosted game (`vibe play`).

3. Pick a provider. Everything that talks to a model runs the CLI you already pay for, in print mode.

   ```bash
   vibe provider claude         # Claude Code, works with a Claude Max subscription
   vibe provider codex          # OpenAI Codex CLI, works with a ChatGPT subscription
   ```

   Also `gemini`, `copilot` and `opencode`. The provider is only used by `vibe explain`, `vibe council` and `vibe theme --create`; the game and the quests never call a model.

4. Say who you are.

   ```bash
   vibe persona data-engineer   # or chief-of-staff, cleaning-ceo, university-md, pabo-teacher, interior-stylist
   vibe difficulty normal       # beginner, easy, normal, hard, expert, god
   vibe theme studio            # studio is the default; wine-night is the original
   ```

   Each command rewrites `vibe.toml`. Delete the file and everything falls back to defaults.

5. Play, then claim.

   ```bash
   vibe play                    # opens the game
   vibe check 1                 # runs the checks for workstream 1, awards the XP when they pass
   vibe done 1 "a scoring board that ranks the team by coffee"
   ```

   `vibe done` writes a dated note into the vault and links it from `vault/Camp/Tonight.md`.

6. Prefer to watch it grow? `vibe vault mode grow` starts the vault with its hubs only and unlocks notes as you play; `vibe vault mode full` reverses it. Nothing is deleted: the rest waits in `vault/_library`.

7. Open the vault in Obsidian: **Open folder as vault**, choose `vault/`. Graph colours, the theme and the templates are pre-configured. `vibe vault lint` reports orphans and dead links. `vibe vault feature --all` adds one note per Obsidian feature, with a canvas, a base, a template and a deck to click through.

## Path C: the product repository, for people who want the engine

This path is not a camp. It clones the product: the game's source, the CLI's code and the course's tests. Take it when you want to change the engine itself. `just setup`, `just verify` and the Playwright browsers exist here and nowhere else; a camp from Path B has `vibe` and a much shorter `justfile`.

1. Clone and enter.

   ```bash
   git clone https://github.com/tpetedb/vibe-map.git camp && cd camp
   brew install just
   ```

2. Install what the evening needs.

   ```bash
   just setup                   # uv sync, Playwright browsers, skill links, the vault
   just setup --check           # dry run: only report what is missing
   ```

   You should see a `.venv`, the Playwright browsers downloading and `vault built`. In a camp, `just setup` is a different recipe with the same name: it runs `vibe init` and links the skills, prints `ready: just start`, and has no `--check`.

3. Open the onboarding screen.

   ```bash
   just start
   ```

   A terminal UI: your name, your field, difficulty, provider and theme; a toolbelt check with one-key installs; launchers for the game, the vault, the docs and Claude Code. The YOLO button installs everything at once.

4. Verify like CI does, before you commit anything.

   ```bash
   just verify                  # ruff, pytest with Playwright, build check
   ```

   Product only: a camp has no test battery and no build. There the equivalent gate is `vibe check --all` for the workstreams, `vibe vault lint` for the notes and whatever tests you wrote in `workspace/`.

5. Make the terminal yours, module by module.

   ```bash
   vibe dotfiles                 # what is in place
   vibe dotfiles install zsh --brew
   vibe dotfiles install tmux
   ```

   Each module is a few files from Tom's toolbox; anything that differs is backed up next to itself.

6. Break something on purpose, then come back.

   ```bash
   just break sandbox           # a play/sandbox branch
   vibe explain                 # the provider explains the last commits in plain words
   just rescue                  # back on main, nothing lost
   ```

## Playing over weeks

[LONG-GAME.md](LONG-GAME.md): the three windows (terminal, game, Obsidian), the four-command loop, the weekly ritual with `vibe news`, and what to do when you come back after a month.

## Where things end up

| Where | You did | It landed in |
|---|---|---|
| camp | `vibe new`, `vibe init` | `.vibe/state.json`, `vault/` |
| camp | `vibe persona`, `vibe theme`, `vibe provider` | `vibe.toml` |
| camp | `vibe done N` | `vault/Camp/<workstream>.md`, `vault/Camp/Tonight.md` |
| camp | `vibe council` | `vault/Camp/Council - <topic>.md` |
| camp | `just setup` | `.vibe/state.json`, the vault, `.claude/skills/` symlinks |
| both | the game | `localStorage` in the browser, exported as a progress code |
| product | `just setup` | `.venv/`, `.claude/skills/` symlinks, Playwright browsers |
| product | `just verify` | nothing on disk; a green or red gate |

## When something is off

- `vibe status` says there is no camp: you are outside a folder with a `vibe.toml`. `cd` into one, run `vibe new`, or set `VIBE_HOME=/path/to/camp`.
- `claude -p` fails with a model catalog error: the CLI retries with `--model sonnet`; run `claude` once interactively to log in.
- The game shows the Roadmap list instead of the island: WebGL is off or blocked. Chrome on a Mac with Apple silicon is the reference; the lessons still work.
- Tests hang on the first run (product repository only): `uv run playwright install chromium webkit` was skipped; `just setup` runs it.
