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
    uv run grimoire start

# install what the evening needs: Python env, browsers for the tests, skill links, vault
setup *args:
    ./scripts/setup.sh {{args}}

# open the game in the default browser
game:
    open game/grimoire.html

# rebuild game/grimoire.html from src/
build:
    uv run python tools/build.py

# regenerate the tech tree outputs from tools/tech.py (notes, tree JS, ROADMAP)
tree:
    uv run python tools/regen_tree.py
    uv run python tools/build.py

# where you are in the campaign, with XP and quests
status:
    uv run grimoire status

# verify the definition of done for a workstream, award the XP (all if omitted)
check *n:
    uv run grimoire check {{n}}

# rebuild the vault notes and the Mermaid map, then lint for orphans and dead links
vault:
    uv run grimoire vault build
    uv run grimoire vault lint

# run the whole pytest battery (CLI, build, Playwright in Chromium and WebKit)
test:
    uv run pytest

# the browser smoke tests only, with screenshots in tests/out
smoke:
    uv run pytest tests/test_game_smoke.py

# lint (ruff check + format check)
lint:
    uv run ruff check . && uv run ruff format --check .

# what CI runs: lint + tests + build check
verify: lint test

# remove build caches and test output
clean:
    rm -rf .pytest_cache .ruff_cache tests/out
