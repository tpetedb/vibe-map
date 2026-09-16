---
title: "Files, folders and paths"
date: 2026-09-16
tags: [tech, dark]
---
# Files, folders and paths

A project is a folder. A path is an address inside it: absolute (/Users/lotte/vibe-map) or relative (./data/scores.csv). Agents work inside one folder at a time and see the world as files, which is why structure matters more than in a GUI.

**History.** The hierarchical file system with directories comes from Multics (Daley and Neumann, 1965) via Unix. Hidden dotfiles are, according to Rob Pike, the result of an early Unix shortcut: ls skipped every name starting with a dot to hide . and .., and people started using it on purpose.

**Try in five minutes.** In the template: find . -type f -not -path './.venv/*' | head -30 and read what each path is for.

- Docs: [Unix filesystem basics](https://missing.csail.mit.edu/2020/course-shell/), [Source: Daley and Neumann, A General-Purpose File System for Secondary Storage (FJCC 1965)](https://multicians.org/fjcc4.html), [Source: Rob Pike, A lesson in shortcuts (2012, archived copy)](https://www.moldvan.com/hidden-dot-files-linux-came-rob-pike-g/)
- Unlocks: [[Dotfiles]], [[Config formats - JSON, YAML, TOML, Markdown]], [[Git]]
- Age: Dark Age · Level: Intern

<!-- generated from vibemap/tech.py; edit there -->

Back to [[Tech tree]]

#tech #dark
