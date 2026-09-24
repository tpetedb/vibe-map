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

# example: just sinks-check
# every value the game writes into the page as HTML is escaped or registered (docs/SECURITY-MODEL.md)
[group('check')]
sinks-check:
    @uv run python tools/checks.py sinks

# every http(s) link in docs/ and the tech tree answers with 2xx or 3xx
[group('check')]
links-check:
    @uv run python tools/checks.py links

# the built game equals a fresh build of src/ (catches hand edits to game/vibe-map.html)
[group('check')]
build-check:
    @uv run python tools/build.py --check

# the tech tree outputs are in sync with vibemap/tech.py
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

# ---- work orders: a task is data and its acceptance is a command (work/README.md)

# scaffold an order on this branch: just work-new hunt-s-ask panels "Ask panel and chat bridge"
work-new id team title:
    python3 tools/work.py new "{{id}}" --team "{{team}}" --title "{{title}}"

# every order here is readable, and no two active orders own the same file
work-validate:
    python3 tools/work.py validate

# ownership, then every criterion's command; the result is cached for this exact tree
work-check id:
    python3 tools/work.py check "{{id}}"

# what a reviewer reads, and the commit to put in review.toml
work-review id:
    python3 tools/work.py review "{{id}}"

# checks, review and sign-offs together: is it ready to land
work-accept id:
    python3 tools/work.py accept "{{id}}"

# a goal as launch groups: needs first, disjoint files, the agent budget
work-plan goal:
    python3 tools/work.py plan "{{goal}}"

# every active order in every worktree
work-board:
    python3 tools/work.py board

# write or refresh the order's one status comment on its issue
work-post id:
    python3 tools/work.py post "{{id}}"

# read the order's issue: owner and collaborators only, status comments left out
work-thread id:
    python3 tools/work.py thread "{{id}}"

# say something on the order's issue in a role: just work-say hunt-s manager:panels "..."
work-say id role text:
    python3 tools/work.py say "{{id}}" --role "{{role}}" "{{text}}"

# ---- the harness: .agents/ and config.toml are the source (.agents/README.md)

# render .claude, .codex and CLAUDE.md from .agents, link the skills, write the lock
harness-sync:
    uv run python .agents/utils/harness.py sync

# exit 1 when an output was edited by hand or an input was not synced
harness-check:
    python3 .agents/utils/harness.py check

# offline health: schemas, lock, skill links, instruction chains, models, Codex trust
harness-doctor:
    python3 .agents/utils/harness.py doctor

# every effective value, the file it comes from and when a change applies
harness-explain:
    python3 .agents/utils/harness.py explain

# example: just harness-pick builder codex
# the model and effort a role is spawned with on one provider
harness-pick role provider:
    python3 .agents/utils/harness.py pick "{{role}}" --provider "{{provider}}"
