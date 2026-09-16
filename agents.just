# Agent-facing recipes: compact, deterministic output for coding agents.
#
# An agent that composes raw bash for these workflows generates (and reads
# back) hundreds of tokens per step; a recipe costs one short line and returns
# only what matters. When you catch yourself composing the same multi-step
# shell twice, add it here instead of generating it a third time.
# Human-facing tasks stay in the root justfile; this file is imported by it.

# --- targeted checks: one cheap command per recurring mistake class -----------

# auto-fix what the style gate rejects: ruff --fix plus ruff format
[group('check')]
fmt:
    uv run ruff check --fix . && uv run ruff format .

# example: just style-check docs/SYLLABUS.md
# scan for em dashes and emoji, the house style's most common violations (default: tracked text files)
[group('check')]
style-check *paths:
    @uv run python tools/checks.py style {{paths}}

# every http(s) link in docs/ and the tech tree answers with 2xx or 3xx
[group('check')]
links-check:
    @uv run python tools/checks.py links

# the built game equals a fresh build of src/ (catches hand edits to game/vibe-map.html)
[group('check')]
build-check:
    @uv run python tools/build.py --check

# the tech tree outputs are in sync with tools/tech.py
[group('check')]
tree-check:
    @uv run python tools/regen_tree.py --check

# --- agent workflows -----------------------------------------------------------

# full gate with failures-only output; prints one OK line when green
[group('agent')]
verify-quiet:
    #!/usr/bin/env bash
    set -uo pipefail
    ok=1
    out=$(uv run ruff check . 2>&1) || { echo "$out"; ok=0; }
    out=$(uv run ruff format --check . 2>&1) || { echo "$out"; ok=0; }
    tests=$(uv run pytest -q --no-header 2>&1) || { echo "$tests" | tail -40; ok=0; }
    if [ "$ok" -eq 1 ]; then
        echo "verify OK: lint clean, $(echo "$tests" | tail -1)"
    else
        echo "verify FAILED"
        exit 1
    fi

# example: just test-one "tests/test_cli.py -k export"
# run one test file or pattern (quote the whole argument), quiet output
[group('agent')]
test-one args:
    uv run pytest -q --no-header {{args}}

# working tree changes vs main: porcelain status plus a three-line diffstat
[group('agent')]
changed:
    #!/usr/bin/env bash
    set -uo pipefail
    git status --porcelain
    base=$(git merge-base HEAD main 2>/dev/null) || exit 0
    git diff --stat "$base" | tail -3

# example: just play campus 3
# play one workstream headlessly and report the state afterwards (world, n)
[group('agent')]
play world n:
    uv run python tools/play.py {{world}} {{n}}
