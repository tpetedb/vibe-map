# Vibe Code Camp tasks. Run `just` or `just --list` to see them.
# Python work delegates to uv; orchestration lives here. Install just with
# `brew install just`.
#
# THIS file is the human's: starting the evening, playing, building, testing.
# The imported agents.just adds two groups that render below these in
# `just --list`: [check] (one targeted check per known mistake class) and
# [agent] (compact recipes for coding agents that replace hand-composed
# multi-step shell). Humans can use those too.

import 'agents.just'

# show the task list
default:
    @just --list

# the onboarding terminal: checks the machine, offers installs, launches things
start:
    uv run vibe start

# install what the evening needs: Python env, browsers for the tests, skill links, vault
setup *args:
    ./scripts/setup.sh {{args}}

# the long game: the game in the browser, the vault in Obsidian, the status in this terminal (docs/LONG-GAME.md)
camp:
    open game/vibe-map.html
    -open -a Obsidian vault
    uv run vibe status

# open the game in the default browser
game:
    open game/vibe-map.html

# pull the AI feeds into the vault note News and bake them into the game
news:
    uv run vibe news
    uv run python tools/build.py

# rebuild game/vibe-map.html from src/
build:
    uv run python tools/build.py

# regenerate the tech tree outputs from vibemap/tech.py (notes, tree JS, ROADMAP)
tree:
    uv run python tools/regen_tree.py
    uv run python tools/build.py

# where you are in the campaign, with XP and quests
status:
    uv run vibe status

# verify the definition of done for a workstream, award the XP (all if omitted)
check *n:
    uv run vibe check {{n}}

# write workspace/dashboard.html from the state, the vault and the scores, and open it
dashboard:
    uv run vibe dashboard

# rebuild the vault notes and the Mermaid map, then lint for orphans and dead links
vault:
    uv run vibe vault build
    uv run vibe vault lint

# run the whole pytest battery (CLI, build, Playwright in Chromium and WebKit)
test:
    uv run pytest

# the browser smoke tests only, with screenshots in tests/out
smoke:
    uv run pytest tests/test_game_smoke.py

# a camp from nothing with the vibe of this checkout: new, the checks, the code
e2e:
    uv run python tools/fresh_camp.py --vibe="uv run --project {{justfile_directory()}} vibe"

# lint (ruff check + format check)
lint:
    uv run ruff check . && uv run ruff format --check .

# what CI runs: lint + tests + build check
verify: lint test

# render the screenshots and the gameplay GIF in docs/media from the built game
media:
    uv run python tools/media.py

# regenerate docs/COOKBOOK.md from the personas
cookbook:
    uv run python tools/gen_cookbook.py

# fetch the claude-obsidian skill set (MIT) and print how to load it on this vault
obsidian-plugin:
    @test -d ~/.claude/plugins/claude-obsidian || git clone --depth 1 https://github.com/AgriciDaniel/claude-obsidian.git ~/.claude/plugins/claude-obsidian
    @echo 'claude --plugin-dir ~/.claude/plugins/claude-obsidian   # then /claude-obsidian:wiki-lint on vault/'

# terminal setup modules from Tom's toolbox: `just dotfiles` lists, `just dotfiles install zsh` writes
dotfiles *args:
    uv run vibe dotfiles {{args}}

# what is installed and what is missing; `just toolbelt missing` installs everything missing
toolbelt *install:
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -n "{{install}}" ]; then uv run vibe toolbelt --install "{{install}}"; else uv run vibe toolbelt; fi

# ask the provider to explain the last commits in plain words
explain n="3":
    uv run vibe explain -n {{n}}

# example: just council "Should I learn git before Python?"
# convene the mentors on a question; minutes land in the vault
council topic:
    uv run vibe council "{{topic}}"

# example: just break sandbox
# a sandbox branch to break things in: play/<name>, from the current branch
break name:
    git switch -c play/{{name}}
    @echo "You are on play/{{name}}. Break anything. Come back with: just rescue"

# commit whatever is lying around on the play branch and return to main, unhurt
rescue:
    #!/usr/bin/env bash
    set -euo pipefail
    branch=$(git branch --show-current)
    case "$branch" in play/*) ;; *) echo "not on a play branch (on $branch); nothing to rescue"; exit 0;; esac
    git add -A && git commit -qm "Play session on $branch" || true
    git switch main
    echo "Back on main. $branch is kept; delete it with: git branch -D $branch"
    uv run vibe explain -n 1 || true

# remove build caches and test output
clean:
    rm -rf .pytest_cache .ruff_cache tests/out
