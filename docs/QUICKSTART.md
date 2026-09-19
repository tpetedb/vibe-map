# Quickstart

Four ways in, from nothing installed to a full camp. Every step is a command you can paste; every block says what you should see afterwards. Numbers are steps, not minutes.

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

   Prints `vibe, version X.Y.Z`, the number in `pyproject.toml` at the commit you installed. That one file is the only place the version is written; everything else reads it. The repository is the install source until the package is published; once it is on PyPI, `uv tool install vibe-map` is the short form of the same thing.

2. Start a camp.

   ```bash
   vibe new                     # a slim camp (workspace, vault, config; no engine) in vibe-map-<you>-<today>
   cd vibe-map-*
   vibe name "Your Name"
   vibe status
   ```

   The folder name is the convention: your name, vibe-map, the date you started (`vibe new ~/vibe-map-tom-2026-09-17` spells it out; `--name tom` changes the person part). One camp per person and start date sorts by date in a listing and tells you which camp a note or a progress code came from. `vibe status` prints your name, level, XP and the four-by-eight grid of workstreams. Add `--github you/camp` to `vibe new` to push the camp to a new GitHub repository as well (needs `gh auth login`); `--private` with it creates the repository private instead of public, which needs GitHub Pro for the camp's Pages workflow, its protected branches and its CODEOWNERS file. The camp has three zones: `workspace/` (yours), `vault/` (the notes) and the configuration files; the engine stays inside the `vibe` command and the hosted game (`vibe play`).

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
   vibe interests               # the eleven shelves of the tree, and what you chose
   vibe interests set data,shell,agents   # or: vibe interests all
   ```

   Each command rewrites `config/camp.toml`. Delete the file and everything falls back to defaults.

   Interests decide what comes first, never what exists. The tree and the search put your shelves in front and dim the rest, the Roadmap suggests the next topic from them, grow mode opens their basics from the first evening, and `vibe status` prints both. The thirty-two stops are the same course for everyone.

5. Play, then claim.

   ```bash
   vibe play                    # opens the game
   vibe check 1                 # runs the checks for workstream 1, awards the XP when they pass
   vibe done 1 "a scoring board that ranks the team by coffee"
   ```

   `vibe done` writes a dated note into the vault and links it from `vault/Camp/Tonight.md`.

   The islands hold two more kinds of work, and both are checked the same way. An artifact's sheet has a "Do it for real" task written from the official documentation of the thing; you build it in `workspace/artifacts/<id>/`. A mentor sets one exercise of under fifteen minutes; it goes in `workspace/mentors/<id>/` and a verified encounter raises a plaque on their spot.

   ```bash
   vibe artifact cafe           # the walkthrough, the same one the game shows
   vibe artifact cafe --start   # writes workspace/artifacts/cafe/ with honest stubs
   vibe check --artifact cafe   # or --artifact all
   vibe check --mentor cherny   # or --mentor all
   ```

   The artifact checks look at what you built and run it. One that needs a tool you do not have (Docker, for instance) says so with the install command instead of failing.

   `vibe check` exits 0 when every check passed and 1 when one failed, so you can put it in a hook or a workflow. `--no-claim` changes what is recorded, never the exit code.

6. Take the game apart, on the production island.

   ```bash
   vibe fork                     # your own copy in workspace/forks/vibe-map/, no clone needed
   cd workspace/forks/vibe-map
   just build                    # your own game/vibe-map.html
   cd -
   vibe check --fork             # or one challenge: exists, config, topic, repair
   ```

   The fork is yours to break and repair. Its `src/config/00-config.js` is the game's own settings (world scale, island radius, palette); your camp's `config/camp.toml` stays the settings for your journey. [CONFIG.md](CONFIG.md) is the full table of which setting lives where.

7. Prefer to watch it grow? `vibe vault mode grow` starts the vault with its hubs only and unlocks notes as you play; `vibe vault mode full` reverses it. Nothing is deleted: the rest waits in `vault/_library`.

8. Open the vault in Obsidian: **Open folder as vault**, choose `vault/`. Graph colours, the theme and the templates are pre-configured. `vibe vault lint` reports orphans and dead links. `vibe vault feature --all` adds one note per Obsidian feature, with a canvas, a base, a template and a deck to click through.

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

## Path D: in the browser, on GitHub Codespaces

Nothing on your machine: a container in GitHub's cloud with the tools already
in it. Works from a Chromebook, a borrowed laptop or an iPad. A personal
account gets free Codespaces hours every month and GitHub Pro raises the
allowance; you can also open a codespace on a machine type you pay for.

1. Open a codespace. On the repository page: **Code**, **Codespaces**, **Create
   codespace on main**. Or from a terminal with `gh`:

   ```bash
   gh codespace create --repo tpetedb/vibe-map
   gh codespace code                     # or --web for the browser editor
   ```

   This works on a camp made by `vibe new` too: every camp carries its own
   `.devcontainer/`.

2. Wait for the setup to finish. `.devcontainer/setup.sh` installs uv, just,
   duckdb and the GitHub CLI, syncs the Python environment and, in this
   repository only, downloads the Playwright browsers. A camp's container skips
   the browsers, because a camp has no test battery; it installs the `vibe`
   command instead. When the terminal prints `ready:` you are in.

3. Serve the game and click the forwarded port.

   ```bash
   python3 -m http.server 8000           # then open game/vibe-map.html
   ```

   In a camp it is your own game: `python3 -m http.server 8000 --directory workspace/game`.
   Port 8000 is labelled **The game** in the **Ports** panel and opens in a new
   tab. Port 7717 is labelled **Chat bridge** for `vibe chat serve`. A forwarded
   port is private to you until you change its visibility in that panel.

4. Everything else is Path B or Path C, unchanged: `just start`, `vibe status`,
   `just verify`.

The container is `mcr.microsoft.com/devcontainers/python:1-3.12-bookworm` with
the `github-cli` dev container feature. The same file opens in VS Code locally
(**Dev Containers: Reopen in Container**) if you have Docker, and it costs
nothing there.

Who pays: "compute usage is charged to the account that owns the codespace", so
a codespace you create is yours, on your own free monthly hours, whichever
repository you opened it from. Set a spending limit of zero on your account if
you want the hours to be the hard stop. Prebuilds would make a codespace start
faster, and they bill the repository's owner for Actions minutes and storage,
so none are configured here; the slow work sits in `onCreateCommand` anyway,
which is the part a prebuild would cache if you ever enable one on a repository
of your own.

## Playing over weeks

[LONG-GAME.md](LONG-GAME.md): the three windows (terminal, game, Obsidian), the four-command loop, the weekly ritual with `vibe news`, and what to do when you come back after a month.

## Where things end up

| Where | You did | It landed in |
|---|---|---|
| camp | `vibe new`, `vibe init` | `.vibe/state.json`, `vault/` |
| camp | `vibe persona`, `vibe theme`, `vibe provider` | `config/camp.toml` |
| camp | `vibe done N` | `vault/Camp/<workstream>.md`, `vault/Camp/Tonight.md` |
| camp | `vibe artifact <id> --start` | `workspace/artifacts/<id>/` with a stub for the file the task names and `notes.md` |
| camp | `vibe check --artifact <id>` | `workspace/artifacts/<id>/` is read; the XP and the "built for real" line land in `.vibe/state.json` and the Artifacts note |
| camp | `vibe check --mentor <id>` | `workspace/mentors/<id>/` is read; the plaque, the badge and the mentor's vault note follow |
| camp | `vibe fork` | `workspace/forks/vibe-map/` with its own `src/config/`, `justfile` and `fork.json` |
| camp | `vibe council` | `vault/Camp/Council - <topic>.md` |
| camp | `just setup` | `.vibe/state.json`, the vault, `.claude/skills/` symlinks |
| both | the game | `localStorage` in the browser, exported as a progress code |
| product | `just setup` | `.venv/`, `.claude/skills/` symlinks, Playwright browsers |
| product | `just verify` | nothing on disk; a green or red gate |

## When something is off

- `vibe status` says there is no camp: you are outside a folder with a `config/camp.toml`. `cd` into one, run `vibe new`, or set `VIBE_HOME=/path/to/camp`.
- `claude -p` fails with a model catalog error: the CLI retries with `--model sonnet`; run `claude` once interactively to log in.
- The game shows the Roadmap list instead of the island: WebGL is off or blocked. Chrome on a Mac with Apple silicon is the reference; the lessons still work.
- Tests hang on the first run (product repository only): `uv run playwright install chromium webkit` was skipped; `just setup` runs it.
