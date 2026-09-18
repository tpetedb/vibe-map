---
name: justfile
description: Adds and names recipes in a justfile so a task is one reviewable command for a human, a hook, CI and an agent. Use when the user says "add a just recipe", "put this in the justfile", "what does just --list show", "make this a task", "run it with just", "justfile", "just file", or when the same multi-step shell has been composed twice.
allowed-tools: Read Edit Bash(just --list) Bash(just --summary) Bash(just --fmt --check) Bash(just --dump --dump-format json)
---
# Writing a justfile

A justfile holds the commands of a project as named recipes you run with `just RECIPE`. Manual: https://just.systems/man/en/

## When a recipe earns its place

- You have composed the same multi-step shell twice. The third time is a recipe. Why: the steps stop drifting between your terminal, the hook and CI.
- A task needs an exact order or exact flags. Put them in the recipe, not in a README sentence, so there is one spelling of the command.
- A task is dangerous. A recipe can carry `[confirm]`, which asks in the terminal before it runs (https://just.systems/man/en/requiring-confirmation-for-recipes.html).
- Do not add a recipe that only wraps one short command you already type by hand; `just` is not an alias file.

## Naming

- One word, lowercase, a verb or the thing produced: `build`, `test`, `verify`, `media`. A hyphen when a second word is needed: `test-one`, `build-check`.
- A helper that exists only as a dependency starts with `_`, or carries `[private]`, and is left out of `just --list` (https://just.systems/man/en/private-recipes.html).
- Group related recipes with `[group('check')]`; `just --list` prints them under that heading and `just --groups` lists the groups (https://just.systems/man/en/groups.html).
- The first recipe in the file, or the one with `[default]`, runs when `just` is called with no arguments (https://just.systems/man/en/the-default-recipe.html). Make it the list or the thing people run most.

## Doc comments are the interface

The comment on the line directly above a recipe is what `just --list` prints next to it (https://just.systems/man/en/documentation-comments.html). Every public recipe gets one, lowercase, one line, saying what it does and not how:

```just
# rebuild the game from src/
build:
    uv run python tools/build.py
```

An example line above the comment documents a parameter:

```just
# example: just test-one "tests/test_cli.py -k export"
# run one test file or pattern (quote the whole argument)
test-one args:
    uv run pytest -q --no-header {{args}}
```

Parameters may have defaults (`deploy env='staging':`) and the last one may be variadic with `*` (zero or more) or `+` (one or more) (https://just.systems/man/en/recipe-parameters.html). A recipe named after the colon is a dependency and runs first, once per invocation (https://just.systems/man/en/dependencies.html).

## Never put a secret in a justfile

A justfile is committed and is read by everyone and every agent that opens the repository. Keys, tokens and passwords go in `.env`, which `set dotenv-load` reads into the environment of the recipes, and `.env` stays in `.gitignore` (https://just.systems/man/en/dotenv-settings.html). Read them as `$NAME` in the recipe body; never as a literal and never as a default parameter value.

## The contract with an agent

- `AGENTS.md` lists recipes, not shell incantations. An agent that reads "run `just verify`" cannot get the flags wrong.
- The hook, the CI job and the person all call the same recipe. One definition, so green locally means green in CI.
- In Claude Code, one allow rule covers them: `"Bash(just *)"` in `permissions.allow`. The wildcard goes after the program, so the rule reaches the recipes in this repository and nothing else, which is narrower than allowing arbitrary shell (https://code.claude.com/docs/en/permissions).
- Keep the destructive ones behind `[confirm]` so the rule stays safe to hand out.

## Before you commit

- `just --list` reads the way you want the project explained.
- `just --fmt --check` exits 0, or run `just --fmt` (https://just.systems/man/en/formatting-and-dumping-justfiles.html).
- `just -n RECIPE` prints what it would do without doing it (`just --help`).
