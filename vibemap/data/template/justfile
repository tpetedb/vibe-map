# Your camp's tasks. Run `just` to list them. Everything delegates to the
# `vibe` command (uv tool install git+https://github.com/tpetedb/vibe-map);
# nothing here needs the engine's source, and every recipe also runs as
# `vibe <thing>`. Install just with `brew install just`.

# show the task list
default:
    @just --list

# the onboarding terminal: checks the machine, offers installs, launches things
start:
    vibe start

# first time here: the progress file, the vault, the skills linked for Claude Code
setup:
    vibe init
    mkdir -p .claude/skills
    for d in .agents/skills/*/; do n=$(basename "$d"); [ -e ".claude/skills/$n" ] || ln -s "../../.agents/skills/$n" ".claude/skills/$n"; done
    @echo "ready: just start"

# the long game: the game in the browser, the vault in Obsidian, your status here
camp:
    vibe play
    -open -a Obsidian vault
    vibe status

# open the game (the hosted one, or the cached copy from `vibe play --offline`)
game:
    vibe play

# where you are in the campaign, with XP and quests
status:
    vibe status

# verify the definition of done for workstream n (the next one if omitted; --all for every one), award the XP
check *n:
    vibe check {{n}}

# mark a workstream done with one line on what you built
done n note:
    vibe done {{n}} "{{note}}"

# rebuild the vault notes and the Mermaid map, then lint for orphans and dead links
vault:
    vibe vault build
    vibe vault lint

# pull the AI feeds into the vault note News
news:
    vibe news

# the scores in workspace/data: summary, or `just scores top_runs` for a query in workspace/sql
scores *sql:
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -n "{{sql}}" ]; then vibe scores --sql "{{sql}}"; else vibe scores; fi

# ask the provider to explain the last commits in plain words
explain n="3":
    vibe explain -n {{n}}

# example: just council "Should I learn git before Python?"
# convene the mentors on a question; minutes land in the vault
council topic:
    vibe council "{{topic}}"

# a sandbox branch to break things in: play/<name>
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
