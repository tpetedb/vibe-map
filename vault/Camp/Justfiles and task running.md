---
title: "Justfiles and task running"
date: 2026-09-18
tags: [tech, shell]
generated: 0a90d7946d98
---
# Justfiles and task running

A justfile is a file of named commands, called recipes, that you run with `just RECIPE`. It replaces a folder of half-remembered scripts and the README section nobody updates: `just --list` prints every task with the comment above it, so the project explains itself. just is a command runner, not a build system, so it skips make's file-timestamp machinery and its idiosyncrasies (no .PHONY). Recipes take parameters with defaults (`deploy env='staging':`), a last parameter may be variadic with + (one or more) or * (zero or more), and a recipe may depend on others, which run first and only once per invocation. Variables are assigned with `:=`, `export` puts one in the environment, and `set dotenv-load` reads a .env file into the environment of every recipe. A recipe starting with `#!` is a shebang recipe: its body is saved to a file and run, so a task can be Python or Node instead of sh. Attributes annotate a recipe: `[group('check')]` sorts it in the listing, `[private]` hides a helper, `[confirm]` asks before a destructive one, `[no-cd]` keeps the working directory where you invoked from. `import 'agents.just'` pulls another file's recipes in as if they were here; `mod foo` makes a submodule you call as `just foo b`. On the command line: `just --choose` hands the recipes to a chooser (fzf by default), `just --fmt` formats the file, `just --fmt --check` exits 1 with a diff instead, `just --dump --dump-format json` prints the whole file as JSON, `just -n` (--dry-run) prints what it would do, and `just --completions zsh` writes a completion script. And for an agent: a justfile is the narrowest useful contract between a person and a coding agent. Every task is one named, reviewable command instead of hand-composed shell, AGENTS.md lists recipes rather than incantations, the hook and the CI job call the same recipe you do, `[confirm]` guards the dangerous ones, and in Claude Code a single allow rule `Bash(just *)` grants the recipes you wrote and nothing else, which is far narrower than allowing arbitrary shell. This repository is the worked example: `justfile` holds the human tasks and imports `agents.just`, which holds the [check] and [agent] groups.

**History.** just is written in Rust by Casey Rodarmor, with a syntax the manual says is inspired by make. It reached 1.0.0 on 22 February 2022 and has kept one changelog since. Modules (`mod`) arrived in 1.19.0 and were stabilised in 1.31.0, which is why older justfiles use `import` for everything.

**Try in five minutes.** just --list in this repository, then just --dump --dump-format json | head -30 to see your own tasks as data. Add a recipe with a doc comment and a parameter, and run it.

- Docs: [just manual](https://just.systems/man/en/), [just, the repository](https://github.com/casey/just), [Source: just manual, Recipes](https://just.systems/man/en/recipes.html), [Source: just manual, Documentation Comments](https://just.systems/man/en/documentation-comments.html), [Source: just manual, Recipe Parameters](https://just.systems/man/en/recipe-parameters.html), [Source: just manual, Dependencies](https://just.systems/man/en/dependencies.html), [Source: just manual, Dotenv Settings](https://just.systems/man/en/dotenv-settings.html), [Source: just manual, Shebang Recipes](https://just.systems/man/en/shebang-recipes.html), [Source: just manual, Attributes](https://just.systems/man/en/attributes.html), [Source: just manual, Imports](https://just.systems/man/en/imports.html), [Source: just manual, Modules](https://just.systems/man/en/modules.html), [Source: just manual, Listing Available Recipes](https://just.systems/man/en/listing-available-recipes.html), [Source: just manual, Formatting and dumping justfiles](https://just.systems/man/en/formatting-and-dumping-justfiles.html), [Source: just manual, Shell Completion Scripts](https://just.systems/man/en/shell-completion-scripts.html), [Source: just CHANGELOG (1.0.0, 22 February 2022)](https://github.com/casey/just/blob/master/CHANGELOG.md), [Source: Claude Code docs, Configure permissions](https://code.claude.com/docs/en/permissions)
- Unlocks: [[AGENTS.md]], [[CI-CD and automation]], [[Git hooks]]
- Shelf: Terminal and shell · Depth: Working knowledge

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #shell
